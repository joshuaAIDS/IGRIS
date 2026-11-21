"""IGRIS Phase 18 — Distributed Training Architecture & Scalability Validation Engine.

Implements and validates:
1. Distributed Data Parallel (DDP) engine with process group lifecycle, DistributedSampler,
   gradient all-reduce synchronization, and no_sync() gradient accumulation.
2. Mixed-Precision Engine supporting FP32, FP16 (with GradScaler), and native BF16 (Ampere).
3. Activation Checkpointing integration for IgrisTransformerBlock with numerical gradient invariance.
4. Fully Sharded Data Parallel (FSDP) module wrap policies, sharding configurations, and
   multi-node cluster memory scaling models.
5. Distributed Checkpoint Manager with atomic writes (.tmp -> .pt), SHA-256 sidecar verification,
   rank-0 coordination, and simulated worker crash recovery.
6. Strict governance enforcement under SOLO_DEVELOPER_OWNER_REVIEW (Default-Deny production ingress).
"""
from __future__ import annotations

import copy
import dataclasses
import datetime
import hashlib
import json
import math
import os
import random
import sys
import tempfile
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

import torch
import torch.distributed as dist
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP

# Setup pathing
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    IgrisTransformerBlock,
    get_baseline_50m_config,
    get_production_config,
    get_test_tiny_config,
)
from checkpoint_integrity import (
    CAND_A_HASH,
    CAND_B_HASH,
)


def compute_file_sha256(path: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_config_fingerprint(config_dict: dict[str, Any]) -> str:
    """Generate deterministic SHA-256 fingerprint for model configuration."""
    canonical_json = json.dumps(config_dict, sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:16]

# Reference constants
SYNTHETIC_DATA_PATH = _PATCH_ROOT / "data" / "synthetic_pretraining_fixtures" / "igris_phase17_synthetic_multilingual.json"
EXPECTED_SYNTHETIC_DATA_HASH = "2d26efe369c9984f0f68bed828a48f5d0b4c13c75bc2c4c49b0c331779b8d8f7"


class PrecisionMode(str, Enum):
    FP32 = "fp32"
    FP16 = "fp16"
    BF16 = "bf16"


# -----------------------------------------------------------------------------
# 1. Governance & Security Invariants
# -----------------------------------------------------------------------------

def verify_governance_invariants() -> dict[str, Any]:
    """Verify all Phase 18 governance invariants before executing distributed routines."""
    # Check Candidate tokenizers
    cand_a_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    
    if not cand_a_path.exists():
        raise RuntimeError(f"Candidate A tokenizer missing at {cand_a_path}")
    if not cand_b_path.exists():
        raise RuntimeError(f"Candidate B tokenizer missing at {cand_b_path}")
    
    hash_a = compute_file_sha256(cand_a_path)
    hash_b = compute_file_sha256(cand_b_path)
    
    if hash_a != CAND_A_HASH:
        raise RuntimeError(f"Candidate A hash mismatch: expected {CAND_A_HASH}, got {hash_a}")
    if hash_b != CAND_B_HASH:
        raise RuntimeError(f"Candidate B hash mismatch: expected {CAND_B_HASH}, got {hash_b}")
    
    # Check synthetic dataset fixture
    if not SYNTHETIC_DATA_PATH.exists():
        raise RuntimeError(f"Synthetic training fixture missing at {SYNTHETIC_DATA_PATH}")
    synth_hash = compute_file_sha256(SYNTHETIC_DATA_PATH)
    if synth_hash != EXPECTED_SYNTHETIC_DATA_HASH:
        raise RuntimeError(f"Synthetic fixture hash mismatch: expected {EXPECTED_SYNTHETIC_DATA_HASH}, got {synth_hash}")
    
    return {
        "status": "PASS",
        "production_ingress": "LOCKED",
        "operating_model": "SOLO_DEVELOPER_OWNER_REVIEW",
        "candidate_a_hash": hash_a,
        "candidate_b_hash": hash_b,
        "synthetic_data_hash": synth_hash,
    }


# -----------------------------------------------------------------------------
# 2. Distributed Process Group Lifecycle
# -----------------------------------------------------------------------------

def init_distributed_environment(
    rank: int,
    world_size: int,
    backend: str = "gloo",
    master_addr: str = "127.0.0.1",
    master_port: int = 29520,
) -> None:
    """Initialize PyTorch distributed process group cleanly."""
    if dist.is_initialized():
        return
    
    init_method = f"tcp://{master_addr}:{master_port}"
    dist.init_process_group(
        backend=backend,
        init_method=init_method,
        rank=rank,
        world_size=world_size,
        timeout=datetime.timedelta(seconds=60),
    )


def cleanup_distributed_environment() -> None:
    """Cleanly destroy the distributed process group."""
    if dist.is_initialized():
        dist.destroy_process_group()


# -----------------------------------------------------------------------------
# 3. Distributed Sampler
# -----------------------------------------------------------------------------

class IgrisDistributedSampler:
    """Deterministic, disjoint dataset partitioner for distributed data parallel training."""

    def __init__(
        self,
        dataset_size: int,
        num_replicas: int,
        rank: int,
        shuffle: bool = True,
        seed: int = 42,
        drop_last: bool = False,
    ):
        if rank < 0 or rank >= num_replicas:
            raise ValueError(f"Invalid rank {rank} for world_size {num_replicas}")
        
        self.dataset_size = dataset_size
        self.num_replicas = num_replicas
        self.rank = rank
        self.shuffle = shuffle
        self.seed = seed
        self.drop_last = drop_last
        self.epoch = 0

        if self.drop_last and self.dataset_size % self.num_replicas != 0:
            self.num_samples = math.ceil((self.dataset_size - self.num_replicas) / self.num_replicas)
        else:
            self.num_samples = math.ceil(self.dataset_size / self.num_replicas)
        self.total_size = self.num_samples * self.num_replicas

    def set_epoch(self, epoch: int) -> None:
        """Set epoch for deterministic seed permutation."""
        self.epoch = epoch

    def __iter__(self) -> Iterator[int]:
        if self.shuffle:
            g = random.Random(self.seed + self.epoch)
            indices = list(range(self.dataset_size))
            g.shuffle(indices)
        else:
            indices = list(range(self.dataset_size))

        if not self.drop_last:
            # Pad indices to make it evenly divisible
            padding_size = self.total_size - len(indices)
            if padding_size <= len(indices):
                indices += indices[:padding_size]
            else:
                indices += (indices * math.ceil(padding_size / len(indices)))[:padding_size]
        else:
            indices = indices[: self.total_size]

        assert len(indices) == self.total_size

        # Subsample for this rank
        indices = indices[self.rank : self.total_size : self.num_replicas]
        assert len(indices) == self.num_samples

        return iter(indices)

    def __len__(self) -> int:
        return self.num_samples


# -----------------------------------------------------------------------------
# 4. Mixed-Precision Module
# -----------------------------------------------------------------------------

class MixedPrecisionHandler:
    """Manages mixed-precision contexts (FP32, FP16 with GradScaler, BF16 native)."""

    def __init__(
        self,
        precision: Union[str, PrecisionMode],
        device: torch.device,
        initial_scale: float = 65536.0,
    ):
        self.precision = PrecisionMode(precision)
        self.device = device
        self.is_cuda = (device.type == "cuda")
        
        # Verify BF16 support if requested
        if self.precision == PrecisionMode.BF16:
            if self.is_cuda and not torch.cuda.is_bf16_supported():
                raise RuntimeError("BF16 requested but current CUDA device does not support native BF16!")
        
        # Determine autocast dtype and enabled flag
        if self.precision == PrecisionMode.FP16:
            self.autocast_enabled = self.is_cuda
            self.autocast_dtype = torch.float16
            self.scaler: Optional[torch.amp.GradScaler] = (
                torch.amp.GradScaler("cuda", init_scale=initial_scale) if self.is_cuda else None
            )
        elif self.precision == PrecisionMode.BF16:
            self.autocast_enabled = True
            self.autocast_dtype = torch.bfloat16
            self.scaler = None
        else:
            self.autocast_enabled = False
            self.autocast_dtype = torch.float32
            self.scaler = None

    def autocast(self):
        """Return autocast context for the forward pass."""
        device_type = "cuda" if self.is_cuda else "cpu"
        return torch.amp.autocast(
            device_type=device_type,
            dtype=self.autocast_dtype,
            enabled=self.autocast_enabled,
        )

    def backward(self, loss: torch.Tensor) -> None:
        """Execute backward pass with optional gradient scaling."""
        if self.scaler is not None:
            self.scaler.scale(loss).backward()
        else:
            loss.backward()

    def step(
        self,
        optimizer: torch.optim.Optimizer,
        model: nn.Module,
        max_grad_norm: float = 1.0,
    ) -> Tuple[float, bool]:
        """Perform optimizer step with unscaling, gradient clipping, and scale updates.
        
        Returns:
            Tuple of (grad_norm, step_successful).
        """
        if self.scaler is not None:
            self.scaler.unscale_(optimizer)
            grad_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm))
            old_scale = self.scaler.get_scale()
            self.scaler.step(optimizer)
            self.scaler.update()
            new_scale = self.scaler.get_scale()
            # If scale decreased, step was skipped due to inf/nan
            step_successful = (new_scale >= old_scale)
            return grad_norm, step_successful
        else:
            grad_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm))
            optimizer.step()
            return grad_norm, True


# -----------------------------------------------------------------------------
# 5. Distributed Checkpoint Management
# -----------------------------------------------------------------------------

@dataclasses.dataclass
class DistributedCheckpointMetadata:
    step: int
    epoch: int
    global_world_size: int
    loss: float
    precision: str
    gradient_checkpointing: bool
    config_fingerprint: str
    timestamp: str
    file_sha256: str
    governance_tag: str = "SYNTHETIC_TEST_ONLY"

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class DistributedCheckpointManager:
    """Coordinates atomic, rank-0 synchronized checkpoint saving and validation."""

    def __init__(self, checkpoint_dir: Union[str, Path]):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        step: int,
        epoch: int,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        loss: float,
        precision: str,
        config: IgrisConfig,
        scaler: Optional[torch.amp.GradScaler] = None,
        rank: int = 0,
        world_size: int = 1,
    ) -> Optional[Path]:
        """Atomically save checkpoint on Rank 0 with sidecar JSON and synchronize all ranks."""
        # Synchronize all workers before writing
        if dist.is_initialized() and world_size > 1:
            dist.barrier()

        saved_path: Optional[Path] = None

        if rank == 0:
            target_pt = self.checkpoint_dir / f"chk_distributed_step_{step}.pt"
            target_json = self.checkpoint_dir / f"chk_distributed_step_{step}.json"
            tmp_pt = self.checkpoint_dir / f".chk_distributed_step_{step}.tmp"

            # Unwrap DDP if wrapped
            raw_model = model.module if isinstance(model, DDP) else model

            payload = {
                "step": step,
                "epoch": epoch,
                "model_state_dict": raw_model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "scaler_state_dict": scaler.state_dict() if scaler is not None else None,
                "loss": loss,
                "config": dataclasses.asdict(config),
                "governance_tag": "SYNTHETIC_TEST_ONLY",
            }

            # Atomic save to temporary file
            torch.save(payload, tmp_pt)
            file_hash = compute_file_sha256(tmp_pt)
            tmp_pt.replace(target_pt)

            meta = DistributedCheckpointMetadata(
                step=step,
                epoch=epoch,
                global_world_size=world_size,
                loss=loss,
                precision=precision,
                gradient_checkpointing=config.gradient_checkpointing,
                config_fingerprint=compute_config_fingerprint(dataclasses.asdict(config)),
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                file_sha256=file_hash,
                governance_tag="SYNTHETIC_TEST_ONLY",
            )
            target_json.write_text(json.dumps(meta.to_dict(), indent=2), encoding="utf-8")
            saved_path = target_pt

        # Synchronize all workers after writing
        if dist.is_initialized() and world_size > 1:
            dist.barrier()

        return saved_path

    def load_latest_valid_checkpoint(
        self,
        model: nn.Module,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scaler: Optional[torch.amp.GradScaler] = None,
        device: torch.device = torch.device("cpu"),
    ) -> Tuple[int, int, float]:
        """Find and load the latest validated checkpoint, ignoring incomplete .tmp files.
        
        Returns:
            Tuple of (step, epoch, loss).
        """
        json_files = sorted(self.checkpoint_dir.glob("chk_distributed_step_*.json"))
        if not json_files:
            raise FileNotFoundError(f"No valid checkpoint JSON found in {self.checkpoint_dir}")

        for json_path in reversed(json_files):
            step_str = json_path.stem.replace("chk_distributed_step_", "")
            pt_path = self.checkpoint_dir / f"chk_distributed_step_{step_str}.pt"
            
            if not pt_path.exists():
                continue

            # Validate SHA-256 against metadata
            meta = json.loads(json_path.read_text(encoding="utf-8"))
            expected_hash = meta.get("file_sha256", "")
            actual_hash = compute_file_sha256(pt_path)

            if actual_hash != expected_hash:
                continue  # Corrupted, try earlier checkpoint

            # Load weights
            payload = torch.load(pt_path, map_location=device, weights_only=False)
            raw_model = model.module if isinstance(model, DDP) else model
            raw_model.load_state_dict(payload["model_state_dict"])

            if optimizer is not None and "optimizer_state_dict" in payload:
                optimizer.load_state_dict(payload["optimizer_state_dict"])

            if scaler is not None and payload.get("scaler_state_dict") is not None:
                scaler.load_state_dict(payload["scaler_state_dict"])

            return payload["step"], payload["epoch"], payload["loss"]

        raise RuntimeError("No uncorrupted checkpoints found in directory!")


# -----------------------------------------------------------------------------
# 6. FSDP Compatibility & Scaling Projections
# -----------------------------------------------------------------------------

def get_fsdp_wrap_policy() -> Any:
    """Generate FSDP auto-wrap policy targeting IgrisTransformerBlock."""
    from torch.distributed.fsdp.wrap import ModuleWrapPolicy
    return ModuleWrapPolicy({IgrisTransformerBlock})


def calculate_cluster_memory_projections(
    model_params_count: int,
    vocab_size: int,
    hidden_dim: int,
    num_layers: int,
    seq_len: int,
    batch_size_per_gpu: int,
    world_sizes: list[int] = [1, 2, 4, 8, 16, 32, 64],
) -> list[dict[str, Any]]:
    """Calculate theoretical memory consumption per GPU across FSDP sharding regimes.
    
    In FSDP FULL_SHARD (ZeRO-3):
    - Parameters: sharded across N GPUs (2 bytes per param in FP16/BF16) -> (2 * P) / N
    - Gradients: sharded across N GPUs (2 bytes per param in FP16/BF16) -> (2 * P) / N
    - Optimizer States (AdamW): FP32 master weights (4B) + momentum (4B) + variance (4B) -> 12 * P / N
    - Activations (with activation checkpointing):
      Linear in sequence length and batch size per GPU:
      ~ num_layers * (seq_len * hidden_dim * 2 bytes)
    """
    projections = []
    param_bytes = model_params_count * 2  # FP16/BF16
    grad_bytes = model_params_count * 2
    opt_bytes = model_params_count * 12  # FP32 states

    # Activation memory per GPU (with activation checkpointing enabled)
    # Storing only input activations per transformer block
    act_bytes = num_layers * (batch_size_per_gpu * seq_len * hidden_dim * 2)

    for n in world_sizes:
        sharded_params_mb = (param_bytes / n) / (1024**2)
        sharded_grads_mb = (grad_bytes / n) / (1024**2)
        sharded_opt_mb = (opt_bytes / n) / (1024**2)
        act_mb = act_bytes / (1024**2)

        # Working buffer for all-gather forward/backward (one transformer layer params)
        layer_params = model_params_count / num_layers
        buffer_mb = (layer_params * 2) / (1024**2)

        total_vram_mb = sharded_params_mb + sharded_grads_mb + sharded_opt_mb + act_mb + buffer_mb

        projections.append({
            "world_size": n,
            "sharding_strategy": "FULL_SHARD (ZeRO-3)",
            "params_per_gpu_mb": round(sharded_params_mb, 2),
            "grads_per_gpu_mb": round(sharded_grads_mb, 2),
            "optimizer_per_gpu_mb": round(sharded_opt_mb, 2),
            "activation_per_gpu_mb": round(act_mb, 2),
            "working_buffer_mb": round(buffer_mb, 2),
            "total_estimated_vram_mb": round(total_vram_mb, 2),
            "fits_in_80gb_h100": (total_vram_mb <= 80 * 1024),
            "fits_in_24gb_rtx4090": (total_vram_mb <= 24 * 1024),
            "fits_in_6gb_rtx3050": (total_vram_mb <= 5.9 * 1024),
        })

    return projections


# -----------------------------------------------------------------------------
# 7. Multi-Process DDP Execution Routine
# -----------------------------------------------------------------------------

def run_ddp_training_worker(
    rank: int,
    world_size: int,
    steps: int,
    batch_size: int,
    seq_len: int,
    precision: str,
    gradient_checkpointing: bool,
    gradient_accumulation_steps: int,
    master_port: int,
    results_dict: dict[str, Any],
    checkpoint_dir: Optional[str] = None,
) -> None:
    """Worker process for multi-process DDP execution."""
    init_distributed_environment(
        rank=rank,
        world_size=world_size,
        backend="gloo",
        master_port=master_port,
    )

    try:
        device = torch.device("cpu")  # Gloo multi-process on CPU ensures clean cross-process test
        cfg = get_test_tiny_config()
        cfg.gradient_checkpointing = gradient_checkpointing

        model = IgrisDecoderTransformer(cfg).to(device)
        ddp_model = DDP(model)
        optimizer = torch.optim.AdamW(ddp_model.parameters(), lr=1e-4)

        mp_handler = MixedPrecisionHandler(precision, device)
        chk_mgr = DistributedCheckpointManager(checkpoint_dir) if checkpoint_dir else None

        records = json.loads(SYNTHETIC_DATA_PATH.read_text(encoding="utf-8"))["records"]
        sampler = IgrisDistributedSampler(
            dataset_size=len(records),
            num_replicas=world_size,
            rank=rank,
            shuffle=True,
            seed=42,
        )

        step_losses = []
        optimizer.zero_grad()

        for step in range(steps):
            accum_losses = []
            
            for micro_step in range(gradient_accumulation_steps):
                is_accum_boundary = (micro_step == gradient_accumulation_steps - 1)
                
                # Sample batch
                input_ids = torch.randint(0, cfg.vocab_size, (batch_size, seq_len), device=device)
                labels = input_ids.clone()

                # Use no_sync on micro-steps prior to boundary
                sync_context = ddp_model.no_sync() if not is_accum_boundary else contextlib_nullcontext()

                with sync_context:
                    with mp_handler.autocast():
                        out = ddp_model(input_ids)
                        logits = out["logits"]
                        loss = nn.functional.cross_entropy(
                            logits.view(-1, cfg.vocab_size),
                            labels.view(-1),
                        )
                        scaled_loss = loss / gradient_accumulation_steps

                    mp_handler.backward(scaled_loss)
                    accum_losses.append(loss.item())

            # Perform optimizer step
            grad_norm, ok = mp_handler.step(optimizer, ddp_model, max_grad_norm=1.0)
            optimizer.zero_grad()

            # Synchronize loss across ranks for logging
            avg_loss = sum(accum_losses) / len(accum_losses)
            loss_tensor = torch.tensor([avg_loss], device=device)
            dist.all_reduce(loss_tensor, op=dist.ReduceOp.AVG)
            step_losses.append(loss_tensor.item())

            if chk_mgr and (step + 1 == steps):
                chk_mgr.save_checkpoint(
                    step=step + 1,
                    epoch=0,
                    model=ddp_model,
                    optimizer=optimizer,
                    loss=loss_tensor.item(),
                    precision=precision,
                    config=cfg,
                    rank=rank,
                    world_size=world_size,
                )

        results_dict[f"rank_{rank}_losses"] = step_losses
        results_dict[f"rank_{rank}_completed"] = True

    finally:
        cleanup_distributed_environment()


class contextlib_nullcontext:
    """Helper null context for PyTorch synchronization."""
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def run_multiprocess_ddp(
    world_size: int = 2,
    steps: int = 5,
    batch_size: int = 2,
    seq_len: int = 32,
    precision: str = "fp32",
    gradient_checkpointing: bool = False,
    gradient_accumulation_steps: int = 1,
    master_port: int = 29530,
    checkpoint_dir: Optional[str] = None,
) -> dict[str, Any]:
    """Execute multi-process DDP training using torch.multiprocessing.spawn."""
    import torch.multiprocessing as mp
    manager = mp.Manager()
    results_dict = manager.dict()

    mp.spawn(
        run_ddp_training_worker,
        args=(
            world_size,
            steps,
            batch_size,
            seq_len,
            precision,
            gradient_checkpointing,
            gradient_accumulation_steps,
            master_port,
            results_dict,
            checkpoint_dir,
        ),
        nprocs=world_size,
        join=True,
    )

    return dict(results_dict)

