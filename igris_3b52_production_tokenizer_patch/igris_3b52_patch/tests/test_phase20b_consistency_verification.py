"""
IGRIS Phase 20B - Automated Consistency Verification Test Suite
Operating Model: SOLO_DEVELOPER_OWNER_REVIEW

Verifies:
1. Physical tokenizer hashes match authoritative baselines.
2. Model parameter exact arithmetic and component breakdowns.
3. Dataset ledger integrity across all 32 sources.
4. Governance invariants (locked gates, 0 authorized sources, 0 acquired bytes).
"""

import csv
import hashlib
import os
import sys
import pytest
import torch

# Paths
PATCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PATCH_ROOT)
sys.path.insert(0, os.path.join(PATCH_ROOT, "src"))
sys.path.insert(0, os.path.join(PATCH_ROOT, "scripts"))

from igris.model.transformer import IgrisDecoderTransformer, get_production_config
from secure_acquisition_engine import SecureAcquisitionEngine, AcquisitionGateLockedError


def hash_file(path: str) -> str:
    """Calculate SHA-256 of physical file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestPhase20BConsistency:
    """Rigorous verification of Phase 20B evidence reconciliations."""

    def test_01_tokenizer_physical_hashes(self):
        """Verify physical tokenizer files match authoritative baselines."""
        cand_a_path = os.path.join(PATCH_ROOT, "artifacts", "tokenizer", "candidate_a", "tokenizer.json")
        cand_b_path = os.path.join(PATCH_ROOT, "artifacts", "tokenizer", "candidate_b", "tokenizer.model")

        assert os.path.isfile(cand_a_path), f"Candidate A missing at {cand_a_path}"
        assert os.path.isfile(cand_b_path), f"Candidate B missing at {cand_b_path}"

        expected_hash_a = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
        expected_hash_b = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

        actual_hash_a = hash_file(cand_a_path)
        actual_hash_b = hash_file(cand_b_path)

        assert actual_hash_a == expected_hash_a, f"Candidate A hash mismatch: {actual_hash_a} != {expected_hash_a}"
        assert actual_hash_b == expected_hash_b, f"Candidate B hash mismatch: {actual_hash_b} != {expected_hash_b}"

    def test_02_model_parameter_arithmetic(self):
        """Instantiate IgrisDecoderTransformer and verify parameter counts and exact arithmetic reconciliation."""
        config = get_production_config()
        model = IgrisDecoderTransformer(config)

        # 1. Total registered parameters
        total_registered = sum(p.numel() for p in model.parameters())
        assert total_registered == 96_485_888, f"Unexpected total registered: {total_registered}"

        # 2. Tied unique parameter count
        unique_param_ptrs = set()
        total_unique = 0
        for p in model.parameters():
            if p.data_ptr() not in unique_param_ptrs:
                unique_param_ptrs.add(p.data_ptr())
                total_unique += p.numel()
        # In untied default:
        assert total_unique == 96_485_888

        # When tied:
        config_tied = get_production_config()
        config_tied.tie_word_embeddings = True
        model_tied = IgrisDecoderTransformer(config_tied)
        tied_unique = sum(p.numel() for p in dict((p.data_ptr(), p) for p in model_tied.parameters()).values())
        assert tied_unique == 79_708_672, f"Unexpected tied unique: {tied_unique}"

        # 3. Component counts
        tok_embed = model.embed_tokens.weight.numel()
        lm_head = model.lm_head.weight.numel()
        assert tok_embed == 16_777_216  # 32,768 * 512
        assert lm_head == 16_777_216    # 32,768 * 512

        # 4. Attention counts across 16 layers
        attn_count = 0
        for i in range(config.num_hidden_layers):
            layer = model.layers[i].self_attn
            q = layer.q_proj.weight.numel()
            k = layer.k_proj.weight.numel()
            v = layer.v_proj.weight.numel()
            o = layer.o_proj.weight.numel()
            assert q == 262_144
            assert k == 131_072
            assert v == 131_072
            assert o == 262_144
            attn_count += (q + k + v + o)
        assert attn_count == 12_582_912  # 16 * 786,432

        # 5. SwiGLU counts across 16 layers
        swiglu_count = 0
        for i in range(config.num_hidden_layers):
            mlp = model.layers[i].mlp
            g = mlp.gate_proj.weight.numel()
            u = mlp.up_proj.weight.numel()
            d = mlp.down_proj.weight.numel()
            assert g == 1_048_576
            assert u == 1_048_576
            assert d == 1_048_576
            swiglu_count += (g + u + d)
        assert swiglu_count == 50_331_648  # 16 * 3,145,728

        # 6. Normalization parameters
        norm_count = 0
        for i in range(config.num_hidden_layers):
            norm_count += model.layers[i].input_layernorm.weight.numel()
            norm_count += model.layers[i].post_attention_layernorm.weight.numel()
        norm_count += model.norm.weight.numel()
        assert norm_count == 16_896  # 16 * 1024 + 512

        # 7. Non-embedding parameters
        non_embedding_total = total_registered - tok_embed - lm_head
        assert non_embedding_total == 62_931_456

        # 8. Exact reconciliation arithmetic:
        # Non-embedding = SwiGLU + GQA + RMSNorm
        assert non_embedding_total == (swiglu_count + attn_count + norm_count)
        # Difference = 16,896 exactly
        assert (non_embedding_total - (swiglu_count + attn_count)) == norm_count
        assert norm_count == 16_896

    def test_03_dataset_ledger_integrity(self):
        """Verify all 32 sources in PHASE20A_DATASET_CLASSIFICATION_RECONCILIATION.csv."""
        p20a_file = os.path.join(PATCH_ROOT, "PHASE20A_DATASET_CLASSIFICATION_RECONCILIATION.csv")
        assert os.path.isfile(p20a_file), f"Missing {p20a_file}"

        with open(p20a_file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 32, f"Expected 32 sources, got {len(rows)}"

        # Check classification distributions
        eligible = [r for r in rows if r["current_classification"] == "ELIGIBLE"]
        conditional = [r for r in rows if r["current_classification"] == "INELIGIBLE_CONDITIONAL"]
        prohibited = [r for r in rows if r["current_classification"] == "INELIGIBLE_PROHIBITED"]
        rejected = [r for r in rows if r["current_classification"] == "INELIGIBLE_REJECTED"]

        assert len(eligible) == 18, f"Expected 18 ELIGIBLE, got {len(eligible)}"
        assert len(conditional) == 8, f"Expected 8 INELIGIBLE_CONDITIONAL, got {len(conditional)}"
        assert len(prohibited) == 2, f"Expected 2 INELIGIBLE_PROHIBITED, got {len(prohibited)}"
        assert len(rejected) == 4, f"Expected 4 INELIGIBLE_REJECTED, got {len(rejected)}"

        # Verify specific evaluation-only sources
        prohibited_ids = {r["source_id"] for r in prohibited}
        assert prohibited_ids == {"SRC-CD-02", "SRC-CV-04"}, f"Unexpected prohibited IDs: {prohibited_ids}"

        # Verify Flores-200 is conditional
        flores = next(r for r in rows if r["source_id"] == "SRC-ML-01")
        assert flores["current_classification"] == "INELIGIBLE_CONDITIONAL"

        # Verify IndicGLUE Tanglish is eligible
        indicglue = next(r for r in rows if r["source_id"] == "SRC-TG-02")
        assert indicglue["current_classification"] == "ELIGIBLE"

        # Verify no source has authorization granted in reconciliation
        for r in rows:
            assert "AUTHORIZED" not in r["final_reconciled_status"] or "PENDING" in r["final_reconciled_status"]

    def test_04_governance_invariants(self):
        """Verify production ingress locked, 0 acquired bytes, quarantine isolation."""
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmpdir:
            isolated_audit = Path(tmpdir) / "acquisition_audit.jsonl"
            isolated_dest = Path(tmpdir) / "tmp_test.bin"
            engine = SecureAcquisitionEngine(audit_log_path=isolated_audit)
            assert not engine.is_gate_unlocked(), "Acquisition gate must be locked"

            with pytest.raises(AcquisitionGateLockedError):
                engine.download_source(
                    source_id="SRC-TM-01",
                    url="https://example.com/data.tar.gz",
                    destination_path=isolated_dest,
                    max_size_bytes=1024 * 1024,
                )

        # Quarantine filename isolation
        for root, dirs, files in os.walk(PATCH_ROOT):
            for f in files:
                if not f.endswith(".md"):
                    assert "quarantine" not in f.lower(), f"Isolation violation: {os.path.join(root, f)}"
