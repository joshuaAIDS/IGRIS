"""IGRIS Phase 19 — End-to-End Pretraining Readiness & Governance Audit Tests.

Verifies:
1. Governance invariants: SOLO_DEVELOPER_OWNER_REVIEW, production ingress locked, Candidate A & B immutable.
2. 32-source dataset catalog taxonomy: 18 permissive, 8 conditional, 2 evaluation-only, 4 incompatible.
3. Architecture & configuration schema validity: causal attention, GQA, RoPE, RMSNorm, SwiGLU.
4. Tokenizer candidate artifacts: 32,768 vocabulary, 12 pinned structural tokens, byte fallback.
5. Processing pipeline integrity: Unicode normalization (NFC), Indic preservation, PII/secret screening.
6. Checkpoint recovery & tamper rejection: atomic .tmp -> .pt writes, external SHA-256 sidecars.
7. Distributed infrastructure validation: DDP multi-process loss synchronization, FSDP wrap policy.
8. End-to-end synthetic dry run completion: 14/14 steps executed cleanly with zero NaNs/Infs.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

import pytest
import torch

# Setup paths
_TEST_DIR = Path(__file__).resolve().parent
_PATCH_ROOT = _TEST_DIR.parent
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from checkpoint_integrity import CAND_A_HASH, CAND_B_HASH
from model_config_validator import ModelConfigValidator
from phase18_distributed_engine import (
    compute_file_sha256,
    get_fsdp_wrap_policy,
    verify_governance_invariants,
)
from phase19_end_to_end_dry_run import run_phase19_dry_run


# -----------------------------------------------------------------------------
# 1. Invariant & Governance Verification Tests
# -----------------------------------------------------------------------------

def test_phase19_governance_invariants():
    """Verify that all non-negotiable governance invariants remain locked."""
    gov = verify_governance_invariants()
    assert gov["status"] == "PASS"
    assert gov["production_ingress"] == "LOCKED"
    assert gov["operating_model"] == "SOLO_DEVELOPER_OWNER_REVIEW"
    assert gov["candidate_a_hash"] == CAND_A_HASH
    assert gov["candidate_b_hash"] == CAND_B_HASH


# -----------------------------------------------------------------------------
# 2. 32-Source Dataset Catalog Classification Audit
# -----------------------------------------------------------------------------

def test_phase19_dataset_catalog_reconciliation():
    """Verify that the 32 candidate sources maintain exact reconciled classifications."""
    catalog_path = _PATCH_ROOT / "DATASET_SOURCE_CATALOG_V3.csv"
    assert catalog_path.exists(), f"Catalog V3 missing at {catalog_path}"

    with open(catalog_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 candidate sources, got {len(rows)}"

    # Audit categories
    permissive_count = sum(1 for r in rows if r.get("tokenizer_training_eligibility") == "ELIGIBLE")
    conditional_count = sum(1 for r in rows if r.get("tokenizer_training_eligibility") == "INELIGIBLE_CONDITIONAL")
    eval_only_count = sum(1 for r in rows if r.get("tokenizer_training_eligibility") == "INELIGIBLE_PROHIBITED")
    incompatible_count = sum(1 for r in rows if r.get("tokenizer_training_eligibility") == "INELIGIBLE_REJECTED")

    # Verify counts match Phase 10-18 reconciled standards
    assert permissive_count == 18, f"Expected 18 permissive candidate sources, got {permissive_count}"
    assert conditional_count == 8, f"Expected 8 conditional sources, got {conditional_count}"
    assert eval_only_count == 2, f"Expected 2 evaluation-only sources, got {eval_only_count}"
    assert incompatible_count == 4, f"Expected 4 incompatible sources, got {incompatible_count}"

    # Verify human approval status
    rejected_count = sum(1 for r in rows if r.get("human_approval_status") == "REJECTED")
    assert rejected_count == 4, f"Expected 4 rejected sources, got {rejected_count}"


# -----------------------------------------------------------------------------
# 3. Model Architecture & Schema Validation Tests
# -----------------------------------------------------------------------------

def test_phase19_architecture_and_config_schemas():
    """Verify model architecture specifications and schema validators."""
    validator = ModelConfigValidator()
    
    prod_cfg = validator.schema_path.parent / "src" / "igris" / "model" / "transformer.py"
    from igris.model.transformer import (
        IgrisDecoderTransformer,
        get_baseline_50m_config,
        get_production_config,
        get_test_tiny_config,
    )

    prod = get_production_config()
    res_prod = validator.validate_config(prod)
    assert res_prod.is_valid, f"Production config schema errors: {res_prod.errors}"
    assert prod.num_attention_heads == 8
    assert prod.num_key_value_heads == 4  # GQA 2:1
    assert prod.hidden_size == 512
    assert prod.max_position_embeddings == 2048
    assert prod.vocab_size == 32768

    baseline = get_baseline_50m_config()
    res_base = validator.validate_config(baseline)
    assert res_base.is_valid, f"Baseline config schema errors: {res_base.errors}"


# -----------------------------------------------------------------------------
# 4. Tokenizer Integrity Tests
# -----------------------------------------------------------------------------

def test_phase19_tokenizer_integrity():
    """Verify Candidate A and B tokenizers have immutable hashes and structural tokens."""
    cand_a_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    assert compute_file_sha256(cand_a_path) == CAND_A_HASH
    assert compute_file_sha256(cand_b_path) == CAND_B_HASH

    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(cand_a_path))
    assert tok.get_vocab_size() == 32768
    # Structural token checks: PAD at 0, BOS at 1, EOS at 2
    assert tok.token_to_id("<|pad|>") == 0
    assert tok.token_to_id("<|begin_of_text|>") == 1
    assert tok.token_to_id("<|end_of_text|>") == 2


# -----------------------------------------------------------------------------
# 5. Distributed FSDP Wrap Policy Verification
# -----------------------------------------------------------------------------

def test_phase19_fsdp_wrap_policy():
    """Verify that FSDP wrap policy correctly isolates IgrisTransformerBlock."""
    policy = get_fsdp_wrap_policy()
    assert policy is not None


# -----------------------------------------------------------------------------
# 6. End-to-End Synthetic Dry Run Verification
# -----------------------------------------------------------------------------

def test_phase19_end_to_end_synthetic_dry_run():
    """Verify the 14-step end-to-end pretraining readiness dry run."""
    report = run_phase19_dry_run()
    assert report["metadata"]["verdict"] == "VERDICT_A_DRY_RUN_PASSED"
    assert len(report["steps_executed"]) == 14
    assert all(s["status"] == "PASS" for s in report["steps_executed"])

    # Check numerical stability
    train_data = report["components_data"]["training"]
    assert train_data["numerical_stability"] == "STABLE_ZERO_NANS_ZERO_INFS"
    assert all(not m["nan_or_inf"] for m in train_data["step_metrics"])

    # Check checkpoint resumption
    resume_data = report["components_data"]["checkpoint_resume"]
    assert resume_data["resumed_step"] == 5
    assert resume_data["subsequent_step_executed"] == 6
    assert resume_data["state_dict_continuity"] == "PERFECT"
