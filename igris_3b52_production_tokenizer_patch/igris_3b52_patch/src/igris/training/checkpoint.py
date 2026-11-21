"""IGRIS Checkpoint Management Engine — Atomic Persistence, Integrity, and Recovery.

Provides atomic checkpoint creation (.tmp -> .pt), model-only export for inference,
full training checkpointing, RNG restoration, tokenizer binding checks, and crash recovery.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import torch
import torch.nn as nn
from igris.model.transformer import IgrisConfig, IgrisDecoderTransformer

CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"


class CheckpointError(Exception):
    """Base exception for checkpoint operations."""


class CheckpointCorruptionError(CheckpointError):
    """Raised when checkpoint binary fails SHA-256 integrity checks."""


class IncompatibleArchitectureError(CheckpointError):
    """Raised when checkpoint architecture fingerprint fails to match expected model."""


class IncompatibleTokenizerError(CheckpointError):
    """Raised when checkpoint tokenizer hash does not match Candidate A specification."""


@dataclass
class CheckpointMetadata:
    checkpoint_id: str
    step: int
    epoch: int
    train_loss: float
    val_loss: Optional[float]
    val_perplexity: Optional[float]
    per_language_metrics: Dict[str, Any]
    model_config_fingerprint: str
    model_config: Dict[str, Any]
    candidate_a_sha256: str
    dataset_manifest_sha256: str
    precision: str
    payload_sha256: str
    created_at: str
    is_synthetic_test: bool = True
    governance_tag: str = "SYNTHETIC_DEVELOPMENT"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CheckpointMetadata:
        return cls(**data)


def compute_config_fingerprint(config: IgrisConfig) -> str:
    """Generate deterministic SHA-256 fingerprint for model configuration."""
    canonical_json = json.dumps(config.to_dict(), sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:16]


def compute_file_sha256(filepath: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class IgrisCheckpointManager:
    """Manages atomic checkpoint saving, model-only export, verification, and recovery."""

    def __init__(
        self,
        checkpoint_dir: Union[str, Path],
        candidate_a_hash: str = CAND_A_HASH,
    ):
        self.checkpoint_dir = Path(checkpoint_dir).resolve()
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.candidate_a_hash = candidate_a_hash

    def save_full_checkpoint(
        self,
        step: int,
        epoch: int,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        scheduler: Optional[Any],
        config: IgrisConfig,
        train_loss: float,
        val_loss: Optional[float] = None,
        val_perplexity: Optional[float] = None,
        per_language_metrics: Optional[Dict[str, Any]] = None,
        scaler: Optional[torch.amp.GradScaler] = None,
        dataset_manifest_sha256: str = "",
        precision: str = "bf16",
    ) -> Path:
        """Atomically saves full training checkpoint (.tmp -> .pt) with sidecar metadata JSON."""
        chk_id = f"chk_step_{step:06d}"
        target_pt = self.checkpoint_dir / f"{chk_id}.pt"
        target_json = self.checkpoint_dir / f"{chk_id}_metadata.json"
        tmp_pt = self.checkpoint_dir / f".{chk_id}.tmp"

        # Capture complete RNG states
        rng_states = {
            "python_random": random.getstate(),
            "torch_cpu_rng": torch.get_rng_state(),
            "torch_cuda_rng": torch.cuda.get_rng_state() if torch.cuda.is_available() else None,
        }

        fp = compute_config_fingerprint(config)
        meta = CheckpointMetadata(
            checkpoint_id=chk_id,
            step=step,
            epoch=epoch,
            train_loss=round(train_loss, 6),
            val_loss=round(val_loss, 6) if val_loss is not None else None,
            val_perplexity=round(val_perplexity, 2) if val_perplexity is not None else None,
            per_language_metrics=per_language_metrics or {},
            model_config_fingerprint=fp,
            model_config=config.to_dict(),
            candidate_a_sha256=self.candidate_a_hash,
            dataset_manifest_sha256=dataset_manifest_sha256,
            precision=precision,
            payload_sha256="",
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

        payload = {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict() if hasattr(scheduler, "state_dict") else None,
            "scaler_state_dict": scaler.state_dict() if scaler is not None else None,
            "rng_states": rng_states,
            "metadata": meta.to_dict(),
        }

        # 1. Write payload to temporary file
        torch.save(payload, tmp_pt)

        # 2. Compute SHA-256 of binary payload
        payload_hash = compute_file_sha256(tmp_pt)
        meta.payload_sha256 = payload_hash
        payload["metadata"]["payload_sha256"] = payload_hash

        # Re-save with recorded payload hash, then atomically rename
        torch.save(payload, tmp_pt)
        final_hash = compute_file_sha256(tmp_pt)
        meta.payload_sha256 = final_hash
        tmp_pt.replace(target_pt)

        # 3. Write sidecar metadata JSON
        target_json.write_text(json.dumps(meta.to_dict(), indent=2), encoding="utf-8")
        return target_pt

    def export_model_only_checkpoint(
        self,
        model: nn.Module,
        config: IgrisConfig,
        output_filepath: Union[str, Path],
        step: int = 0,
    ) -> Path:
        """Export lightweight inference-only model weights and configuration."""
        out_path = Path(output_filepath).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = out_path.with_suffix(".export.tmp")

        export_payload = {
            "model_state_dict": model.state_dict(),
            "config": config.to_dict(),
            "export_step": step,
            "candidate_a_sha256": self.candidate_a_hash,
            "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        torch.save(export_payload, tmp_path)
        tmp_path.replace(out_path)

        meta_path = out_path.with_name(f"{out_path.stem}_export_metadata.json")
        meta = {
            "file": out_path.name,
            "file_sha256": compute_file_sha256(out_path),
            "config_fingerprint": compute_config_fingerprint(config),
            "candidate_a_sha256": self.candidate_a_hash,
            "exported_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return out_path

    def load_checkpoint(
        self,
        filepath: Union[str, Path],
        model: Optional[nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        scheduler: Optional[Any] = None,
        scaler: Optional[torch.amp.GradScaler] = None,
        expected_config: Optional[IgrisConfig] = None,
        restore_rng: bool = True,
        device: torch.device = torch.device("cpu"),
    ) -> Tuple[Dict[str, Any], CheckpointMetadata]:
        """Loads and verifies checkpoint integrity, restoring model, optimizer, and RNG states."""
        path = Path(filepath).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {path}")

        meta_json_path = path.with_name(f"{path.stem}_metadata.json")
        if not meta_json_path.exists():
            raise CheckpointCorruptionError(f"Missing sidecar metadata JSON: {meta_json_path}")

        sidecar_meta = json.loads(meta_json_path.read_text(encoding="utf-8"))
        expected_hash = sidecar_meta.get("payload_sha256", "")

        # 1. Verify binary hash against sidecar
        actual_hash = compute_file_sha256(path)
        if expected_hash and actual_hash != expected_hash:
            raise CheckpointCorruptionError(
                f"Binary corruption detected in {path}! Expected {expected_hash}, got {actual_hash}"
            )

        # 2. Load payload
        try:
            payload = torch.load(path, map_location=device, weights_only=False)
        except Exception as e:
            raise CheckpointCorruptionError(f"Failed to unpickle checkpoint {path}: {e}") from e

        metadata = CheckpointMetadata.from_dict(payload.get("metadata", sidecar_meta))

        # 3. Verify Tokenizer Invariant Binding
        if metadata.candidate_a_sha256 != self.candidate_a_hash:
            raise IncompatibleTokenizerError(
                f"Checkpoint tokenizer hash mismatch! Checkpoint was created with {metadata.candidate_a_sha256}, "
                f"expected Candidate A {self.candidate_a_hash}"
            )

        # 4. Verify Architecture Configuration Fingerprint
        if expected_config is not None:
            expected_fp = compute_config_fingerprint(expected_config)
            if metadata.model_config_fingerprint != expected_fp:
                raise IncompatibleArchitectureError(
                    f"Architecture mismatch! Expected fingerprint {expected_fp}, "
                    f"checkpoint was trained with {metadata.model_config_fingerprint}"
                )

        # 5. Restore weights
        if model is not None:
            model.load_state_dict(payload["model_state_dict"])

        # 6. Restore optimizer
        if optimizer is not None and payload.get("optimizer_state_dict") is not None:
            optimizer.load_state_dict(payload["optimizer_state_dict"])

        # 7. Restore scheduler
        if scheduler is not None and payload.get("scheduler_state_dict") is not None:
            if hasattr(scheduler, "load_state_dict"):
                scheduler.load_state_dict(payload["scheduler_state_dict"])

        # 8. Restore scaler
        if scaler is not None and payload.get("scaler_state_dict") is not None:
            scaler.load_state_dict(payload["scaler_state_dict"])

        # 9. Restore RNG states
        if restore_rng and "rng_states" in payload:
            rng_s = payload["rng_states"]
            if "python_random" in rng_s:
                random.setstate(rng_s["python_random"])
            if "torch_cpu_rng" in rng_s and rng_s["torch_cpu_rng"] is not None:
                torch.set_rng_state(rng_s["torch_cpu_rng"].cpu())
            if "torch_cuda_rng" in rng_s and rng_s["torch_cuda_rng"] is not None and torch.cuda.is_available():
                torch.cuda.set_rng_state(rng_s["torch_cuda_rng"].cpu())

        return payload, metadata
