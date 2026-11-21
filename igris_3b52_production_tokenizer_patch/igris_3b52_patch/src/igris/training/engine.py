"""IGRIS Training Engine — Controlled Pretraining, Mixed Precision, and Hardware Telemetry.

Coordinates model training, gradient accumulation, learning rate scheduling,
real-time hardware profiling (VRAM, host RAM, tokens/sec), periodic validation, and checkpoints.
"""
from __future__ import annotations

import datetime
import json
import math
import os
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import psutil
import torch
import torch.nn as nn
from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_production_config,
)
from igris.training.checkpoint import (
    CAND_A_HASH,
    CheckpointMetadata,
    IgrisCheckpointManager,
    compute_config_fingerprint,
)
from igris.training.evaluator import EvaluationMetrics, IgrisEvaluator


@dataclass
class TrainingConfig:
    training_run_id: str = "run_dev_synthetic_01"
    model_name: str = "igris-prod-16l"
    max_seq_len: int = 512
    micro_batch_size: int = 2
    gradient_accumulation_steps: int = 2
    learning_rate: float = 1e-4
    weight_decay: float = 0.1
    betas: Tuple[float, float] = (0.9, 0.95)
    eps: float = 1e-8
    warmup_steps: int = 2
    max_steps: int = 10
    min_lr_ratio: float = 0.1
    gradient_clipping: float = 1.0
    precision: str = "bf16"
    activation_checkpointing: bool = True
    eval_interval: int = 5
    checkpoint_interval: int = 5
    random_seed: int = 42
    output_dir: str = ""
    candidate_a_hash: str = CAND_A_HASH

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CosineWarmupScheduler:
    """Cosine learning rate schedule with linear warmup."""

    def __init__(
        self,
        optimizer: torch.optim.Optimizer,
        warmup_steps: int,
        max_steps: int,
        min_lr_ratio: float = 0.1,
    ):
        self.optimizer = optimizer
        self.warmup_steps = max(1, warmup_steps)
        self.max_steps = max(self.warmup_steps + 1, max_steps)
        self.min_lr_ratio = min_lr_ratio
        self.base_lrs = [group["lr"] for group in optimizer.param_groups]
        self.current_step = 0

    def step(self) -> float:
        self.current_step += 1
        factor = self._get_lr_factor(self.current_step)
        for base_lr, group in zip(self.base_lrs, self.optimizer.param_groups):
            group["lr"] = base_lr * factor
        return self.optimizer.param_groups[0]["lr"]

    def _get_lr_factor(self, step: int) -> float:
        if step < self.warmup_steps:
            return float(step) / float(self.warmup_steps)
        progress = float(step - self.warmup_steps) / float(self.max_steps - self.warmup_steps)
        progress = min(max(progress, 0.0), 1.0)
        cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
        return self.min_lr_ratio + (1.0 - self.min_lr_ratio) * cosine_decay

    def state_dict(self) -> Dict[str, Any]:
        return {"current_step": self.current_step, "base_lrs": self.base_lrs}

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        self.current_step = state_dict.get("current_step", 0)
        self.base_lrs = state_dict.get("base_lrs", self.base_lrs)


class IgrisTrainer:
    """Production training engine with mixed-precision, telemetry, and checkpointing."""

    def __init__(
        self,
        config: TrainingConfig,
        model_config: Optional[IgrisConfig] = None,
        custom_checkpoint_dir: Optional[Union[str, Path]] = None,
    ):
        self.config = config
        self.output_dir = Path(custom_checkpoint_dir or config.output_dir or "./checkpoints").resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._set_deterministic_seeds(config.random_seed)

        # Model configuration
        if model_config is not None:
            self.model_config = model_config
        else:
            self.model_config = get_production_config()
            self.model_config.tie_word_embeddings = True  # Authoritative tied specification
            self.model_config.max_position_embeddings = max(config.max_seq_len, 2048)

        self.model_config.gradient_checkpointing = config.activation_checkpointing

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.is_cuda = (self.device.type == "cuda")

        # Initialize model
        self.model = IgrisDecoderTransformer(self.model_config).to(self.device)

        # Setup precision and GradScaler
        self.precision = config.precision.lower()
        if self.precision == "bf16" and self.is_cuda and not torch.cuda.is_bf16_supported():
            print("Notice: Native BF16 not supported on this CUDA device, falling back to FP16.")
            self.precision = "fp16"

        self.use_autocast = self.precision in ["bf16", "fp16"]
        self.autocast_dtype = torch.bfloat16 if self.precision == "bf16" else torch.float16
        self.scaler = torch.amp.GradScaler("cuda") if (self.is_cuda and self.precision == "fp16") else None

        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
            betas=config.betas,
            eps=config.eps,
        )

        # Scheduler
        self.scheduler = CosineWarmupScheduler(
            self.optimizer,
            warmup_steps=config.warmup_steps,
            max_steps=config.max_steps,
            min_lr_ratio=config.min_lr_ratio,
        )

        self.checkpoint_manager = IgrisCheckpointManager(
            checkpoint_dir=self.output_dir,
            candidate_a_hash=config.candidate_a_hash,
        )
        self.evaluator = IgrisEvaluator(self.model, self.device)

        self.current_step = 0
        self.step_telemetry: List[Dict[str, Any]] = []

    def _set_deterministic_seeds(self, seed: int) -> None:
        random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def train_step(
        self,
        micro_batches: List[Dict[str, torch.Tensor]],
        step: int,
    ) -> Dict[str, Any]:
        """Execute one complete optimizer step across gradient accumulation micro-batches."""
        self.model.train()
        self.optimizer.zero_grad()

        start_time = time.perf_counter()
        accum_steps = len(micro_batches)
        total_step_loss = 0.0
        total_step_tokens = 0

        # Reset peak VRAM statistics for this step
        if self.is_cuda:
            torch.cuda.reset_peak_memory_stats()

        for micro_idx, batch in enumerate(micro_batches):
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch.get("attention_mask")
            if attention_mask is not None:
                attention_mask = attention_mask.to(self.device)
            labels = batch.get("labels", input_ids).to(self.device)

            batch_tokens = int((labels != -100).sum().item())
            total_step_tokens += batch_tokens

            # Autocast context
            device_type = "cuda" if self.is_cuda else "cpu"
            with torch.amp.autocast(device_type=device_type, dtype=self.autocast_dtype, enabled=self.use_autocast):
                out = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = out["loss"]
                scaled_loss = loss / accum_steps

            if self.scaler is not None:
                self.scaler.scale(scaled_loss).backward()
            else:
                scaled_loss.backward()

            total_step_loss += float(loss.item())

        # Optimizer step with unscaling & clipping
        if self.scaler is not None:
            self.scaler.unscale_(self.optimizer)
            grad_norm = float(torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clipping))
            self.scaler.step(self.optimizer)
            self.scaler.update()
        else:
            grad_norm = float(torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clipping))
            self.optimizer.step()

        self.optimizer.zero_grad()
        current_lr = self.scheduler.step()
        step_duration = time.perf_counter() - start_time

        # Hardware measurements
        tokens_per_sec = total_step_tokens / max(step_duration, 1e-6)
        steps_per_sec = 1.0 / max(step_duration, 1e-6)

        allocated_vram_mb = (torch.cuda.max_memory_allocated() / (1024**2)) if self.is_cuda else 0.0
        reserved_vram_mb = (torch.cuda.max_memory_reserved() / (1024**2)) if self.is_cuda else 0.0
        host_ram_mb = psutil.Process().memory_info().rss / (1024**2)

        telemetry = {
            "step": step,
            "train_loss": round(total_step_loss / accum_steps, 6),
            "grad_norm": round(grad_norm, 6),
            "learning_rate": round(current_lr, 8),
            "step_duration_sec": round(step_duration, 4),
            "steps_per_sec": round(steps_per_sec, 2),
            "tokens_per_sec": round(tokens_per_sec, 1),
            "total_tokens": total_step_tokens,
            "allocated_vram_mb": round(allocated_vram_mb, 2),
            "reserved_vram_mb": round(reserved_vram_mb, 2),
            "host_ram_mb": round(host_ram_mb, 2),
        }
        self.step_telemetry.append(telemetry)
        return telemetry

    def train(
        self,
        train_batches: List[Dict[str, torch.Tensor]],
        val_batches: Optional[List[Dict[str, torch.Tensor]]] = None,
        per_language_val_batches: Optional[Dict[str, List[Dict[str, torch.Tensor]]]] = None,
        dataset_manifest_sha256: str = "",
    ) -> Dict[str, Any]:
        """Execute complete bounded training run with validation and checkpoints."""
        start_time = datetime.datetime.now(datetime.timezone.utc)
        saved_checkpoints: List[str] = []
        val_history: List[Dict[str, Any]] = []

        batch_idx = 0
        total_batches = len(train_batches)
        accum_steps = self.config.gradient_accumulation_steps

        for step in range(1, self.config.max_steps + 1):
            self.current_step = step

            # Slice micro-batches for this accumulation step
            micro_chunk = []
            for _ in range(accum_steps):
                micro_chunk.append(train_batches[batch_idx % total_batches])
                batch_idx += 1

            telem = self.train_step(micro_chunk, step)

            # Validation interval
            latest_val_loss = None
            latest_val_ppl = None
            latest_per_lang = None
            if val_batches and (step % self.config.eval_interval == 0 or step == self.config.max_steps):
                eval_metrics = self.evaluator.evaluate(
                    eval_batches=val_batches,
                    split_name="validation",
                    per_language_batches=per_language_val_batches,
                )
                latest_val_loss = eval_metrics.overall_loss
                latest_val_ppl = eval_metrics.overall_perplexity
                latest_per_lang = eval_metrics.per_language
                val_history.append({
                    "step": step,
                    "metrics": eval_metrics.to_dict(),
                })

            # Checkpoint interval
            if step % self.config.checkpoint_interval == 0 or step == self.config.max_steps:
                chk_path = self.checkpoint_manager.save_full_checkpoint(
                    step=step,
                    epoch=1,
                    model=self.model,
                    optimizer=self.optimizer,
                    scheduler=self.scheduler,
                    config=self.model_config,
                    train_loss=telem["train_loss"],
                    val_loss=latest_val_loss,
                    val_perplexity=latest_val_ppl,
                    per_language_metrics=latest_per_lang,
                    scaler=self.scaler,
                    dataset_manifest_sha256=dataset_manifest_sha256,
                    precision=self.precision,
                )
                saved_checkpoints.append(str(chk_path))

        end_time = datetime.datetime.now(datetime.timezone.utc)
        elapsed_sec = (end_time - start_time).total_seconds()

        return {
            "status": "COMPLETED",
            "run_id": self.config.training_run_id,
            "max_steps": self.config.max_steps,
            "elapsed_seconds": round(elapsed_sec, 3),
            "step_telemetry": self.step_telemetry,
            "validation_history": val_history,
            "saved_checkpoints": saved_checkpoints,
        }
