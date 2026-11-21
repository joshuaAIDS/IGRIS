"""IGRIS Phase 16 — Controlled Model Training Pipeline and Engine.

Provides an isolated, auditable model training pipeline for IGRIS transformer architectures.
Enforces default-deny governance gates, strict isolation of synthetic fixtures,
deterministic random seeding, gradient clipping, atomic checkpointing, and cryptographic audit trails.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import math
import os
import random
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

# Setup patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

import torch
import torch.nn as nn
from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_production_config,
    get_test_tiny_config,
)
from checkpoint_integrity import (
    CAND_A_HASH,
    CAND_B_HASH,
    CheckpointManager,
    CheckpointMetadata,
    compute_config_fingerprint,
)

TRAINING_SCHEMA_PATH = _PATCH_ROOT / "MODEL_TRAINING_CONFIG_SCHEMA.json"


class GovernanceGateError(PermissionError):
    """Raised when a production boundary or unauthorized training operation is attempted."""


class ConfigurationValidationError(ValueError):
    """Raised when training configuration fails schema or invariant validation."""


@dataclass
class ModelTrainingConfig:
    training_version: str = "v1.0.0-synthetic"
    model_config: dict[str, Any] = field(default_factory=dict)
    target_environment: str = "synthetic_test"
    random_seed: int = 42
    batch_size: int = 4
    gradient_accumulation_steps: int = 1
    max_steps: int = 10
    eval_interval: int = 5
    checkpoint_interval: int = 5
    gradient_clipping: float = 1.0
    optimizer: dict[str, Any] = field(
        default_factory=lambda: {
            "name": "AdamW",
            "lr": 1e-4,
            "weight_decay": 0.1,
            "betas": [0.9, 0.95],
            "eps": 1e-8,
        }
    )
    scheduler: dict[str, Any] = field(
        default_factory=lambda: {
            "name": "cosine",
            "warmup_steps": 2,
            "min_lr_ratio": 0.1,
        }
    )
    mixed_precision: str = "no"
    max_seq_len: int = 128
    save_top_k: int = 3
    owner_authorization_reference: str = "AUTH-SOLO-OWNER-PHASE16-SYNTHETIC-VALIDATION"
    output_checkpoint_dir: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelTrainingConfig:
        return cls(**data)


class TrainingConfigValidator:
    """Validates training configuration against MODEL_TRAINING_CONFIG_SCHEMA.json invariants."""

    def __init__(self, schema_path: Path | str | None = None):
        self.schema_path = Path(schema_path or TRAINING_SCHEMA_PATH)
        if self.schema_path.exists():
            self.schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        else:
            self.schema = {}

    def validate(
        self,
        config: ModelTrainingConfig,
        candidate_a_hash: str = CAND_A_HASH,
        candidate_b_hash: str = CAND_B_HASH,
    ) -> list[str]:
        errors: list[str] = []

        # 1. Version pattern validation
        if not re.match(r"^v[0-9]+\.[0-9]+.*$", config.training_version):
            errors.append(f"training_version '{config.training_version}' must match pattern '^v[0-9]+\\.[0-9]+.*$'")

        # 2. Target environment gate
        if config.target_environment not in ["synthetic_test", "isolated_test", "production"]:
            errors.append(f"Invalid target_environment: '{config.target_environment}'")
        elif config.target_environment == "production":
            raise GovernanceGateError(
                "CRITICAL GOVERNANCE GATE: Production model training is strictly LOCKED in Phase 16. "
                "No production model pretraining is authorized. Target environment 'production' is denied."
            )

        # 3. Owner authorization verification
        if not config.owner_authorization_reference:
            raise GovernanceGateError("Owner authorization reference is missing.")
        if "UNAUTHORIZED" in config.owner_authorization_reference.upper():
            raise GovernanceGateError("Owner authorization reference marks execution as UNAUTHORIZED.")
        if not config.owner_authorization_reference.startswith("AUTH-SOLO-OWNER-"):
            raise GovernanceGateError(
                f"Invalid owner authorization reference format: '{config.owner_authorization_reference}'. "
                "Must begin with 'AUTH-SOLO-OWNER-'."
            )

        # 4. Tokenizer Invariants Verification
        if candidate_a_hash != CAND_A_HASH:
            errors.append(f"Candidate A tokenizer hash mismatch! Expected {CAND_A_HASH}, got {candidate_a_hash}")
        if candidate_b_hash != CAND_B_HASH:
            errors.append(f"Candidate B tokenizer hash mismatch! Expected {CAND_B_HASH}, got {candidate_b_hash}")

        # 5. Hyperparameter boundaries
        if config.batch_size < 1:
            errors.append("batch_size must be >= 1")
        if config.max_steps < 1:
            errors.append("max_steps must be >= 1")
        if config.gradient_clipping < 0:
            errors.append("gradient_clipping must be >= 0.0")

        opt = config.optimizer
        if not isinstance(opt, dict) or "lr" not in opt or opt["lr"] <= 0:
            errors.append("optimizer must specify a positive 'lr'")
        if opt.get("name") not in ["AdamW", "adamw"]:
            errors.append(f"optimizer name '{opt.get('name')}' must be AdamW")

        if not config.output_checkpoint_dir:
            errors.append("output_checkpoint_dir must be specified")

        return errors


class TrainingAuditLogger:
    """Appends immutable structured JSONL audit events for model training operations."""

    def __init__(self, log_path: Path | str):
        self.log_path = Path(log_path).resolve()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        event: str,
        step: int = 0,
        loss: Optional[float] = None,
        lr: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        record = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event": event,
            "step": step,
            "loss": round(loss, 6) if loss is not None else None,
            "learning_rate": lr,
            "details": details or {},
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


class IgrisCosineWarmupScheduler:
    """Cosine learning rate scheduler with linear warmup."""

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


class IgrisTrainingPipeline:
    """Reproducible, controlled model training pipeline for IGRIS transformer architectures."""

    def __init__(
        self,
        config: ModelTrainingConfig,
        custom_audit_log: Optional[Path | str] = None,
    ):
        self.config = config
        self.validator = TrainingConfigValidator()
        self.checkpoint_manager = CheckpointManager()

        # Validate configuration and governance gates
        errors = self.validator.validate(config)
        if errors:
            raise ConfigurationValidationError(f"Training configuration validation failed: {'; '.join(errors)}")

        self.checkpoint_dir = Path(config.output_checkpoint_dir).resolve()
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        log_file = custom_audit_log or (self.checkpoint_dir / "model_training_audit.jsonl")
        self.audit_logger = TrainingAuditLogger(log_file)

        # Set reproducible seeds
        self._set_deterministic_seeds(config.random_seed)

        # Initialize model
        if config.model_config:
            self.model_config = IgrisConfig(**config.model_config)
        else:
            self.model_config = get_test_tiny_config()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = IgrisDecoderTransformer(self.model_config).to(self.device)

        # Initialize optimizer
        opt_cfg = config.optimizer
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=opt_cfg.get("lr", 1e-4),
            weight_decay=opt_cfg.get("weight_decay", 0.1),
            betas=tuple(opt_cfg.get("betas", [0.9, 0.95])),
            eps=opt_cfg.get("eps", 1e-8),
        )

        # Initialize scheduler
        sched_cfg = config.scheduler
        self.scheduler = IgrisCosineWarmupScheduler(
            self.optimizer,
            warmup_steps=sched_cfg.get("warmup_steps", 2),
            max_steps=config.max_steps,
            min_lr_ratio=sched_cfg.get("min_lr_ratio", 0.1),
        )

        self.current_step = 0
        self.step_history: list[dict[str, Any]] = []

        self.audit_logger.log(
            event="PIPELINE_INITIALIZED",
            step=0,
            details={
                "training_version": config.training_version,
                "target_environment": config.target_environment,
                "device": str(self.device),
                "model_parameters": self.model.count_parameters(),
                "config_fingerprint": compute_config_fingerprint(self.model_config),
            },
        )

    def _set_deterministic_seeds(self, seed: int) -> None:
        random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def train_step(self, batch: dict[str, torch.Tensor], step: int) -> dict[str, float]:
        """Execute a single forward, backward, clipping, and optimizer step."""
        self.model.train()
        self.optimizer.zero_grad()

        input_ids = batch["input_ids"].to(self.device)
        attention_mask = batch.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)
        labels = batch.get("labels", input_ids).to(self.device)

        # Forward pass
        out = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
        )
        logits = out["logits"]
        loss = out["loss"]

        if loss is None or torch.isnan(loss) or torch.isinf(loss):
            raise ValueError(f"Step {step}: Loss is non-finite (loss={loss})")

        # Backward pass
        loss.backward()

        # Check gradients finiteness
        for name, param in self.model.named_parameters():
            if param.grad is not None:
                if torch.isnan(param.grad).any() or torch.isinf(param.grad).any():
                    raise ValueError(f"Step {step}: Non-finite gradient in {name}")

        # Gradient clipping
        grad_norm = torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            max_norm=self.config.gradient_clipping,
        )

        # Optimizer step
        self.optimizer.step()

        # Scheduler step
        current_lr = self.scheduler.step()

        step_info = {
            "step": step,
            "loss": float(loss.item()),
            "grad_norm": float(grad_norm.item() if isinstance(grad_norm, torch.Tensor) else grad_norm),
            "learning_rate": current_lr,
        }
        self.step_history.append(step_info)

        self.audit_logger.log(
            event="STEP_COMPLETED",
            step=step,
            loss=step_info["loss"],
            lr=step_info["learning_rate"],
            details={"grad_norm": step_info["grad_norm"]},
        )

        return step_info

    def evaluate(self, eval_batches: list[dict[str, torch.Tensor]]) -> float:
        """Evaluate model loss on synthetic validation batches."""
        self.model.eval()
        total_loss = 0.0
        total_batches = len(eval_batches)
        if total_batches == 0:
            return 0.0

        with torch.no_grad():
            for batch in eval_batches:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch.get("attention_mask")
                if attention_mask is not None:
                    attention_mask = attention_mask.to(self.device)
                labels = batch.get("labels", input_ids).to(self.device)

                out = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
                loss = out["loss"]
                total_loss += float(loss.item())

        avg_loss = total_loss / total_batches
        self.audit_logger.log(
            event="EVALUATION_COMPLETED",
            step=self.current_step,
            loss=avg_loss,
            details={"eval_batches": total_batches},
        )
        return avg_loss

    def save_step_checkpoint(self, step: int, loss: float) -> Path:
        """Save an atomic checkpoint with metadata sidecar and integrity hash."""
        chk_id = f"chk_step_{step:06d}"
        chk_filename = f"{chk_id}.pt"
        chk_path = self.checkpoint_dir / chk_filename

        fp = compute_config_fingerprint(self.model_config)
        meta = CheckpointMetadata(
            checkpoint_id=chk_id,
            step=step,
            loss=loss,
            random_seed=self.config.random_seed,
            model_config_fingerprint=fp,
            model_config=self.model_config.to_dict(),
            candidate_a_sha256=CAND_A_HASH,
            candidate_b_sha256=CAND_B_HASH,
            is_synthetic_test=(self.config.target_environment != "production"),
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        saved_path = self.checkpoint_manager.save_checkpoint(
            model=self.model,
            optimizer=self.optimizer,
            metadata=meta,
            output_filepath=chk_path,
        )

        self.audit_logger.log(
            event="CHECKPOINT_SAVED",
            step=step,
            loss=loss,
            details={"checkpoint_path": str(saved_path), "checkpoint_id": chk_id},
        )
        return saved_path

    def resume_from_checkpoint(self, checkpoint_path: Path | str) -> int:
        """Load and restore model and optimizer state from checkpoint."""
        payload, metadata = self.checkpoint_manager.load_checkpoint(
            filepath=checkpoint_path,
            model=self.model,
            optimizer=self.optimizer,
            expected_config=self.model_config,
        )
        self.current_step = metadata.step
        self.audit_logger.log(
            event="CHECKPOINT_RESTORED",
            step=self.current_step,
            loss=metadata.loss,
            details={"checkpoint_id": metadata.checkpoint_id},
        )
        return self.current_step

    def run_synthetic_training(
        self,
        synthetic_batches: list[dict[str, torch.Tensor]],
        eval_batches: Optional[list[dict[str, torch.Tensor]]] = None,
    ) -> dict[str, Any]:
        """Run controlled synthetic training experiment."""
        start_time = datetime.datetime.now(datetime.timezone.utc)
        saved_checkpoints: list[str] = []

        initial_loss: Optional[float] = None
        final_loss: Optional[float] = None

        batch_idx = 0
        total_batches = len(synthetic_batches)

        for step in range(1, self.config.max_steps + 1):
            self.current_step = step
            batch = synthetic_batches[batch_idx % total_batches]
            batch_idx += 1

            step_info = self.train_step(batch, step)
            if step == 1:
                initial_loss = step_info["loss"]
            final_loss = step_info["loss"]

            # Save checkpoint at interval or last step
            if (
                step % self.config.checkpoint_interval == 0
                or step == self.config.max_steps
            ):
                saved_chk = self.save_step_checkpoint(step, step_info["loss"])
                saved_checkpoints.append(str(saved_chk))

            # Run evaluation at interval
            if eval_batches and step % self.config.eval_interval == 0:
                self.evaluate(eval_batches)

        end_time = datetime.datetime.now(datetime.timezone.utc)
        elapsed_sec = (end_time - start_time).total_seconds()

        summary = {
            "status": "COMPLETED",
            "training_version": self.config.training_version,
            "target_environment": self.config.target_environment,
            "max_steps": self.config.max_steps,
            "initial_loss": initial_loss,
            "final_loss": final_loss,
            "loss_reduced": (final_loss < initial_loss) if (initial_loss and final_loss) else False,
            "saved_checkpoints": saved_checkpoints,
            "elapsed_seconds": round(elapsed_sec, 3),
            "step_history": self.step_history,
        }

        self.audit_logger.log(
            event="TRAINING_COMPLETED",
            step=self.current_step,
            loss=final_loss,
            details={
                "initial_loss": initial_loss,
                "final_loss": final_loss,
                "saved_checkpoints_count": len(saved_checkpoints),
                "elapsed_seconds": round(elapsed_sec, 3),
            },
        )

        return summary
