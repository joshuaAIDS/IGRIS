"""IGRIS Phase 16 — Comprehensive Model Architecture & Training Pipeline Test Suite.

Verifies:
1. Architectural invariants, parameter counts, and config validation.
2. Causal attention masking, future-token leakage prevention, and autoregressive equivalence.
3. Multilingual token compatibility across Indic scripts.
4. Forward/backward stability, finite gradients, gradient clipping, and parameter updates.
5. Checkpoint integrity: atomic persistence, SHA-256 verification, and corruption detection.
6. Default-deny governance gates: strictly blocking production training.
7. Tokenizer artifact SHA-256 immutability.
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

import pytest
import torch
import torch.nn as nn

# Setup patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_baseline_50m_config,
    get_production_config,
    get_test_tiny_config,
)
from model_config_validator import ModelConfigValidator
from causal_attention_tests import CausalAttentionVerifier
from checkpoint_integrity import (
    CAND_A_HASH,
    CAND_B_HASH,
    CheckpointCorruptionError,
    CheckpointManager,
    CheckpointMetadata,
    IncompatibleArchitectureError,
    IncompatibleTokenizerError,
    compute_config_fingerprint,
)
from model_training_pipeline import (
    GovernanceGateError,
    IgrisTrainingPipeline,
    ModelTrainingConfig,
)
from model_resource_estimator import detect_hardware, estimate_model_resources


class TestModelArchitectureAndInvariants:
    """Validate architectural invariants and parameter counts."""

    def test_production_and_baseline_invariants(self):
        prod_cfg = get_production_config()
        base_cfg = get_baseline_50m_config()

        # Invariant checks
        for cfg in [prod_cfg, base_cfg]:
            assert cfg.vocab_size == 32768
            assert cfg.hidden_size == 512
            assert cfg.num_attention_heads == 8
            assert cfg.num_key_value_heads == 4
            assert cfg.rope_theta == 10000.0
            assert cfg.pad_token_id == 0
            assert cfg.bos_token_id == 1
            assert cfg.eos_token_id == 2
            assert cfg.rms_norm_eps == 1e-5

        assert prod_cfg.num_hidden_layers == 16
        assert prod_cfg.intermediate_size == 2048

        assert base_cfg.num_hidden_layers == 12
        assert base_cfg.intermediate_size == 1376

    def test_config_validator_catches_invalid_configs(self):
        validator = ModelConfigValidator()
        valid_res = validator.validate_config(get_production_config())
        assert valid_res.is_valid is True
        assert len(valid_res.errors) == 0

        # Invalid vocab size
        bad_vocab = get_production_config()
        bad_vocab.vocab_size = 50000
        bad_res = validator.validate_config(bad_vocab)
        assert bad_res.is_valid is False
        assert any("vocab_size" in err for err in bad_res.errors)

        # Invalid attention heads (not divisible)
        bad_heads = get_production_config()
        bad_heads.num_attention_heads = 7
        bad_res2 = validator.validate_config(bad_heads)
        assert bad_res2.is_valid is False

    def test_exact_parameter_counts(self):
        prod_cfg = get_production_config()
        base_cfg = get_baseline_50m_config()
        tiny_cfg = get_test_tiny_config()

        prod_model = IgrisDecoderTransformer(prod_cfg)
        base_model = IgrisDecoderTransformer(base_cfg)
        tiny_model = IgrisDecoderTransformer(tiny_cfg)

        prod_counts = prod_model.count_parameters()
        base_counts = base_model.count_parameters()
        tiny_counts = tiny_model.count_parameters()

        # Production 16L: exactly 96,485,888 params untied
        assert prod_counts["total_parameters"] == 96_485_888
        # Baseline 12L: exactly 68,366,848 params untied
        assert base_counts["total_parameters"] == 68_366_848
        # Tiny: exactly 8,684,160 params
        assert tiny_counts["total_parameters"] == 8_684_160


class TestCausalAttentionAndMasking:
    """Verify mathematical proof of zero future-token information leakage."""

    def test_zero_future_leakage(self):
        tiny_cfg = get_test_tiny_config()
        model = IgrisDecoderTransformer(tiny_cfg)
        model.eval()

        torch.manual_seed(42)
        # Sequence 1: [1, 10, 20, 30]
        # Sequence 2: [1, 10, 20, 999] (identical prefix, different future token)
        seq1 = torch.tensor([[1, 10, 20, 30]])
        seq2 = torch.tensor([[1, 10, 20, 999]])

        with torch.no_grad():
            out1 = model(input_ids=seq1)["logits"]
            out2 = model(input_ids=seq2)["logits"]

        # Check logits for prefix tokens (positions 0, 1, 2)
        prefix_diff = (out1[:, :3, :] - out2[:, :3, :]).abs().max().item()
        assert prefix_diff == 0.0, f"Future token leakage detected! Difference: {prefix_diff}"

        # Position 3 should differ
        pos3_diff = (out1[:, 3, :] - out2[:, 3, :]).abs().max().item()
        assert pos3_diff > 0.01, "Different future token did not change position 3 output!"

    def test_autoregressive_step_equivalence(self):
        tiny_cfg = get_test_tiny_config()
        model = IgrisDecoderTransformer(tiny_cfg)
        model.eval()

        prompt = torch.tensor([[1, 45, 98, 120, 350]])
        seq_len = prompt.shape[1]

        # Batched causal pass
        with torch.no_grad():
            batched_logits = model(input_ids=prompt)["logits"]

        # Step-by-step incremental pass
        step_logits = []
        with torch.no_grad():
            for t in range(1, seq_len + 1):
                sub_prompt = prompt[:, :t]
                out_t = model(input_ids=sub_prompt)["logits"]
                step_logits.append(out_t[:, -1:, :])

        step_stacked = torch.cat(step_logits, dim=1)
        max_diff = (batched_logits - step_stacked).abs().max().item()
        assert max_diff < 1e-5, f"Autoregressive equivalence failed! Difference: {max_diff}"

    def test_causal_masking_proof_suite(self):
        rep = CausalAttentionVerifier().run_all_causal_tests()
        assert rep.future_leakage_prevented is True
        assert rep.max_prefix_absolute_diff == 0.0
        assert rep.autoregressive_step_match is True
        assert rep.max_step_absolute_diff < 1e-5
        assert rep.padding_mask_isolated is True


class TestMultilingualIngestionAndLoss:
    """Verify model forward, backward, and loss across Indic scripts."""

    def test_multilingual_token_ranges(self):
        tiny_cfg = get_test_tiny_config()
        model = IgrisDecoderTransformer(tiny_cfg)
        model.train()

        # Representing Latin, Devanagari, Tamil, Bengali, Telugu tokens
        sample_tokens = torch.tensor([
            [1, 500, 2500, 3500, 0],       # Latin
            [1, 5000, 8000, 11000, 0],     # Devanagari
            [1, 14000, 16000, 19000, 0],   # Tamil/Dravidian
            [1, 22000, 25000, 31000, 0],   # Bengali/Gujarati
        ], dtype=torch.long)

        attn_mask = torch.tensor([
            [1, 1, 1, 1, 0],
            [1, 1, 1, 1, 0],
            [1, 1, 1, 1, 0],
            [1, 1, 1, 1, 0],
        ], dtype=torch.long)

        labels = sample_tokens.clone()
        labels[sample_tokens == 0] = -100

        out = model(input_ids=sample_tokens, attention_mask=attn_mask, labels=labels)
        loss = out["loss"]
        logits = out["logits"]

        assert logits.shape == (4, 5, tiny_cfg.vocab_size)
        assert loss is not None
        assert not torch.isnan(loss)
        assert not torch.isinf(loss)
        assert loss.item() > 0.0

        # Verify backward pass
        loss.backward()
        for name, param in model.named_parameters():
            assert param.grad is not None, f"Missing gradient in {name}"
            assert not torch.isnan(param.grad).any(), f"NaN gradient in {name}"
            assert not torch.isinf(param.grad).any(), f"Inf gradient in {name}"


class TestCheckpointIntegrityAndResumption:
    """Verify atomic checkpoint persistence, corruption detection, and resumption."""

    def test_checkpoint_save_and_exact_load(self, tmp_path):
        tiny_cfg = get_test_tiny_config()
        model = IgrisDecoderTransformer(tiny_cfg)
        opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
        manager = CheckpointManager()

        meta = CheckpointMetadata(
            checkpoint_id="chk_unit_test",
            step=42,
            loss=2.718,
            random_seed=42,
            model_config_fingerprint=compute_config_fingerprint(tiny_cfg),
            model_config=tiny_cfg.to_dict(),
            candidate_a_sha256=CAND_A_HASH,
            candidate_b_sha256=CAND_B_HASH,
            is_synthetic_test=True,
        )

        chk_path = tmp_path / "model_chk.pt"
        manager.save_checkpoint(model, opt, meta, chk_path)

        assert chk_path.exists()
        sidecar_path = tmp_path / "model_chk_metadata.json"
        assert sidecar_path.exists()

        # Restore into fresh model
        fresh_model = IgrisDecoderTransformer(tiny_cfg)
        fresh_opt = torch.optim.AdamW(fresh_model.parameters(), lr=1e-3)

        payload, restored_meta = manager.load_checkpoint(
            filepath=chk_path,
            model=fresh_model,
            optimizer=fresh_opt,
            expected_config=tiny_cfg,
        )

        assert restored_meta.step == 42
        assert abs(restored_meta.loss - 2.718) < 1e-5

        # Check weights identical
        test_in = torch.tensor([[1, 20, 30]])
        model.eval()
        fresh_model.eval()
        with torch.no_grad():
            out1 = model(input_ids=test_in)["logits"]
            out2 = fresh_model(input_ids=test_in)["logits"]

        assert (out1 - out2).abs().max().item() == 0.0

    def test_corruption_detection(self, tmp_path):
        tiny_cfg = get_test_tiny_config()
        model = IgrisDecoderTransformer(tiny_cfg)
        manager = CheckpointManager()

        meta = CheckpointMetadata(
            checkpoint_id="chk_corrupt_test",
            step=1,
            loss=3.0,
            random_seed=42,
            model_config_fingerprint=compute_config_fingerprint(tiny_cfg),
            model_config=tiny_cfg.to_dict(),
            candidate_a_sha256=CAND_A_HASH,
            candidate_b_sha256=CAND_B_HASH,
            is_synthetic_test=True,
        )

        chk_path = tmp_path / "corrupt_chk.pt"
        manager.save_checkpoint(model, None, meta, chk_path)

        # Corrupt 1 byte in checkpoint file
        raw = bytearray(chk_path.read_bytes())
        raw[len(raw) // 2] ^= 0xFF
        chk_path.write_bytes(bytes(raw))

        with pytest.raises(CheckpointCorruptionError):
            manager.load_checkpoint(chk_path)

    def test_incompatible_tokenizer_rejected(self, tmp_path):
        tiny_cfg = get_test_tiny_config()
        model = IgrisDecoderTransformer(tiny_cfg)
        manager = CheckpointManager()

        # Incompatible tokenizer hash
        meta = CheckpointMetadata(
            checkpoint_id="chk_bad_tok",
            step=1,
            loss=3.0,
            random_seed=42,
            model_config_fingerprint=compute_config_fingerprint(tiny_cfg),
            model_config=tiny_cfg.to_dict(),
            candidate_a_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            candidate_b_sha256=CAND_B_HASH,
            is_synthetic_test=True,
        )

        chk_path = tmp_path / "bad_tok_chk.pt"
        manager.save_checkpoint(model, None, meta, chk_path)

        with pytest.raises(IncompatibleTokenizerError):
            manager.load_checkpoint(chk_path)


class TestGovernanceGatesAndTrainingPipeline:
    """Verify default-deny gates and controlled synthetic training loop."""

    def test_default_deny_production_target(self, tmp_path):
        cfg = ModelTrainingConfig(
            training_version="v1.0.0-prod",
            target_environment="production",  # FORBIDDEN
            owner_authorization_reference="AUTH-SOLO-OWNER-PHASE16-SYNTHETIC-VALIDATION",
            output_checkpoint_dir=str(tmp_path),
        )
        with pytest.raises(GovernanceGateError) as exc_info:
            IgrisTrainingPipeline(cfg)
        assert "Production model training is strictly LOCKED in Phase 16" in str(exc_info.value)

    def test_missing_or_unauthorized_reference(self, tmp_path):
        cfg = ModelTrainingConfig(
            training_version="v1.0.0-synthetic",
            target_environment="synthetic_test",
            owner_authorization_reference="UNAUTHORIZED_RUN",
            output_checkpoint_dir=str(tmp_path),
        )
        with pytest.raises(GovernanceGateError):
            IgrisTrainingPipeline(cfg)

    def test_controlled_synthetic_optimization(self, tmp_path):
        tiny_cfg = get_test_tiny_config()
        cfg = ModelTrainingConfig(
            training_version="v1.0.0-synthetic",
            model_config=tiny_cfg.to_dict(),
            target_environment="synthetic_test",
            random_seed=42,
            batch_size=2,
            max_steps=5,
            eval_interval=2,
            checkpoint_interval=5,
            gradient_clipping=1.0,
            optimizer={
                "name": "AdamW",
                "lr": 1e-2,
                "weight_decay": 0.01,
                "betas": [0.9, 0.95],
                "eps": 1e-8,
            },
            owner_authorization_reference="AUTH-SOLO-OWNER-PHASE16-SYNTHETIC-VALIDATION",
            output_checkpoint_dir=str(tmp_path),
        )

        pipeline = IgrisTrainingPipeline(cfg)

        tokens = torch.tensor([[1, 25, 60, 100], [1, 200, 500, 900]], dtype=torch.long)
        batch = {"input_ids": tokens, "labels": tokens}

        summary = pipeline.run_synthetic_training([batch])
        assert summary["status"] == "COMPLETED"
        assert summary["max_steps"] == 5
        assert summary["final_loss"] < summary["initial_loss"]

        # Verify audit log exists
        audit_file = tmp_path / "model_training_audit.jsonl"
        assert audit_file.exists()
        lines = [json.loads(l) for l in audit_file.read_text(encoding="utf-8").strip().split("\n")]
        assert len(lines) >= 6


class TestTokenizerInvariancePhase16:
    """Verify Candidate A and Candidate B SHA-256 hashes are strictly invariant."""

    def test_candidate_tokenizer_hashes_invariant(self):
        cand_a_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        cand_b_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

        assert cand_a_path.exists(), f"Candidate A tokenizer missing at {cand_a_path}"
        assert cand_b_path.exists(), f"Candidate B tokenizer missing at {cand_b_path}"

        import hashlib
        cand_a_actual = hashlib.sha256(cand_a_path.read_bytes()).hexdigest()
        cand_b_actual = hashlib.sha256(cand_b_path.read_bytes()).hexdigest()

        assert cand_a_actual == CAND_A_HASH, f"Candidate A corrupted! Expected {CAND_A_HASH}, got {cand_a_actual}"
        assert cand_b_actual == CAND_B_HASH, f"Candidate B corrupted! Expected {CAND_B_HASH}, got {cand_b_actual}"
