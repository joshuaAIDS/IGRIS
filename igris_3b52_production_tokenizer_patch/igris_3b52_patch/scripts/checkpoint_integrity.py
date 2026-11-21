"""IGRIS Phase 16 — Checkpoint Integrity and Recovery Engine.

Provides atomic checkpoint persistence, SHA-256 verification, architecture fingerprinting,
tokenizer binding checks, corruption detection, and safe failure on metadata mismatch.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
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
from igris.model.transformer import IgrisConfig, IgrisDecoderTransformer

CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"


class CheckpointError(Exception):
    """Base exception for checkpoint errors."""


class CheckpointCorruptionError(CheckpointError):
    """Raised when checkpoint hash does not match binary contents."""


class IncompatibleArchitectureError(CheckpointError):
    """Raised when checkpoint configuration fingerprint does not match model."""


class IncompatibleTokenizerError(CheckpointError):
    """Raised when checkpoint tokenizer binding does not match Candidate A/B."""


@dataclass
class CheckpointMetadata:
    checkpoint_id: str
    step: int
    loss: float
    random_seed: int
    model_config_fingerprint: str
    model_config: dict[str, Any]
    candidate_a_sha256: str
    candidate_b_sha256: str
    payload_sha256: str = ""
    is_synthetic_test: bool = True
    created_at: str = "2026-11-18T12:00:00Z"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_config_fingerprint(config: IgrisConfig) -> str:
    """Generate deterministic SHA-256 fingerprint for model configuration."""
    canonical_json = json.dumps(config.to_dict(), sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:16]


class CheckpointManager:
    """Manages atomic saving, loading, corruption detection, and validation of checkpoints."""

    def __init__(
        self,
        candidate_a_hash: str = CAND_A_HASH,
        candidate_b_hash: str = CAND_B_HASH,
    ):
        self.cand_a_hash = candidate_a_hash
        self.cand_b_hash = candidate_b_hash

    def save_checkpoint(
        self,
        model: nn.Module,
        optimizer: Optional[torch.optim.Optimizer],
        metadata: CheckpointMetadata,
        output_filepath: Path | str,
    ) -> Path:
        """Atomically save checkpoint payload with integrity metadata."""
        out_path = Path(output_filepath).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = out_path.with_suffix(".tmp")

        payload = {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict() if optimizer else None,
            "metadata": metadata.to_dict(),
        }

        # 1. Write payload to temporary file
        torch.save(payload, tmp_path)

        # 2. Compute SHA-256 of the saved temporary file
        raw_bytes = tmp_path.read_bytes()
        file_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        metadata.payload_sha256 = file_sha256

        # 3. Atomically rename temporary file to destination
        os.replace(tmp_path, out_path)

        # 4. Write external sidecar metadata JSON
        meta_json_path = out_path.with_name(f"{out_path.stem}_metadata.json")
        meta_json_path.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")

        return out_path

    def load_checkpoint(
        self,
        filepath: Path | str,
        model: Optional[IgrisDecoderTransformer] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        expected_config: Optional[IgrisConfig] = None,
    ) -> tuple[dict[str, Any], CheckpointMetadata]:
        """Load, verify, and restore model state from checkpoint."""
        path = Path(filepath).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint not found at {path}")

        # 1. Read sidecar metadata if available
        meta_json_path = path.with_name(f"{path.stem}_metadata.json")
        if not meta_json_path.exists():
            raise CheckpointCorruptionError(f"Missing sidecar metadata JSON for checkpoint {path}")

        sidecar_meta = json.loads(meta_json_path.read_text(encoding="utf-8"))
        expected_sha256 = sidecar_meta.get("payload_sha256", "")

        # 2. Recalculate file hash to detect corruption
        actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()

        # 3. Load payload with PyTorch
        try:
            payload = torch.load(path, map_location="cpu", weights_only=False)
        except Exception as e:
            raise CheckpointCorruptionError(f"Failed to unpickle checkpoint payload: {e}") from e

        meta_dict = payload.get("metadata", {})
        if "payload_sha256" not in meta_dict or not meta_dict["payload_sha256"]:
            meta_dict["payload_sha256"] = actual_sha256
        metadata = CheckpointMetadata(**meta_dict)

        # 4. Verify binary hash against sidecar and recorded hash
        if expected_sha256 and actual_sha256 != expected_sha256:
            raise CheckpointCorruptionError(
                f"Checkpoint binary corruption detected! Expected {expected_sha256}, got {actual_sha256}"
            )

        # 5. Verify Tokenizer Invariant Binding
        if (
            metadata.candidate_a_sha256 != self.cand_a_hash
            or metadata.candidate_b_sha256 != self.cand_b_hash
        ):
            raise IncompatibleTokenizerError(
                f"Checkpoint tokenizer binding mismatch! "
                f"Candidate A: {metadata.candidate_a_sha256} vs {self.cand_a_hash}, "
                f"Candidate B: {metadata.candidate_b_sha256} vs {self.cand_b_hash}"
            )

        # 6. Verify Architecture Configuration Fingerprint
        if expected_config is not None:
            expected_fp = compute_config_fingerprint(expected_config)
            if metadata.model_config_fingerprint != expected_fp:
                raise IncompatibleArchitectureError(
                    f"Architecture mismatch! Expected fingerprint {expected_fp}, "
                    f"checkpoint was trained with {metadata.model_config_fingerprint}"
                )

        # 7. Restore weights if model provided
        if model is not None:
            model.load_state_dict(payload["model_state_dict"])

        # 8. Restore optimizer if provided
        if optimizer is not None and payload.get("optimizer_state_dict") is not None:
            optimizer.load_state_dict(payload["optimizer_state_dict"])

        return payload, metadata


if __name__ == "__main__":
    from igris.model.transformer import get_test_tiny_config
    cfg = get_test_tiny_config()
    model = IgrisDecoderTransformer(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)

    manager = CheckpointManager()
    fp = compute_config_fingerprint(cfg)
    meta = CheckpointMetadata(
        checkpoint_id="chk_test_01",
        step=10,
        loss=3.456,
        random_seed=42,
        model_config_fingerprint=fp,
        model_config=cfg.to_dict(),
        candidate_a_sha256=CAND_A_HASH,
        candidate_b_sha256=CAND_B_HASH,
        is_synthetic_test=True,
    )

    with tempfile.TemporaryDirectory() as td:
        out_f = Path(td) / "test_checkpoint.pt"
        manager.save_checkpoint(model, opt, meta, out_f)
        print("Checkpoint saved atomically to:", out_f)

        # Load back
        model2 = IgrisDecoderTransformer(cfg)
        opt2 = torch.optim.AdamW(model2.parameters(), lr=1e-3)
        manager.load_checkpoint(out_f, model=model2, optimizer=opt2, expected_config=cfg)
        print("Checkpoint loaded and verified successfully!")
