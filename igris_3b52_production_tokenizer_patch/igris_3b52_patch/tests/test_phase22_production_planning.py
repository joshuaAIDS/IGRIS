"""
tests/test_phase22_production_planning.py

Pytest suite for IGRIS Phase 22 Production Dataset Authorization Decision & Resource Readiness.
Verifies all 8 Phase 22 deliverables, governance invariants, 32-source decision register,
hardware capacity deficit documentation, and tokenizer/model configuration freeze.
"""

import os
import sys
import csv
import json
import hashlib
import tempfile
from pathlib import Path
import pytest
import torch

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PATCH_ROOT = Path(os.path.dirname(CURRENT_DIR))
SCRIPTS_DIR = str(PATCH_ROOT / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if str(PATCH_ROOT) not in sys.path:
    sys.path.insert(0, str(PATCH_ROOT))

from model_training_pipeline import IgrisConfig, IgrisDecoderTransformer
from secure_acquisition_engine import SecureAcquisitionEngine, AcquisitionGateLockedError

EXPECTED_DELIVERABLES = [
    "PHASE22_GOVERNANCE_RECONCILIATION.md",
    "PHASE22_INDICORP_LEGAL_REVIEW_PACKAGE.md",
    "PHASE22_HARDWARE_CAPACITY_ASSESSMENT.md",
    "PHASE22_STORAGE_REQUIREMENTS.csv",
    "PHASE22_ACQUISITION_EXECUTION_PLAN.md",
    "PHASE22_TOKENIZER_MODEL_CONFIGURATION_FREEZE.md",
    "PHASE22_SOURCE_OWNER_DECISION_REGISTER.csv",
    "PHASE22_COMPLETION_REPORT.md",
]

EXPECTED_CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class TestPhase22ProductionPlanning:
    """Verification suite for Phase 22 deliverables and invariants."""

    def test_01_all_deliverables_exist_and_non_empty(self):
        """Verify all 8 Phase 22 deliverables exist and are non-empty."""
        for filename in EXPECTED_DELIVERABLES:
            file_path = PATCH_ROOT / filename
            assert file_path.exists(), f"Deliverable missing: {file_path}"
            assert file_path.stat().st_size > 0, f"Deliverable is empty: {file_path}"

    def test_02_tokenizer_candidate_hashes_and_structural_tokens(self):
        """Verify Candidate A and B bitwise SHA-256 hashes and structural tokens 0-11."""
        cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        
        assert cand_a_path.exists(), f"Candidate A missing: {cand_a_path}"
        assert cand_b_path.exists(), f"Candidate B missing: {cand_b_path}"
        
        hash_a = compute_sha256(cand_a_path)
        hash_b = compute_sha256(cand_b_path)
        
        assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: got {hash_a}"
        assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: got {hash_b}"

        # Verify Candidate A special tokens structure
        with open(cand_a_path, "r", encoding="utf-8") as f:
            tok_data = json.load(f)
            
        vocab = tok_data.get("model", {}).get("vocab", {})
        assert len(vocab) == 32768, f"Expected vocab size 32768, got {len(vocab)}"
        
        expected_pinned = {
            "<|pad|>": 0,
            "<|begin_of_text|>": 1,
            "<|end_of_text|>": 2,
            "<think>": 3,
            "</think>": 4,
            "<action>": 5,
            "</action>": 6,
            "<action_result>": 7,
            "</action_result>": 8,
            "<|system|>": 9,
            "<|user|>": 10,
            "<|assistant|>": 11,
        }
        for token, expected_id in expected_pinned.items():
            assert token in vocab, f"Token {token} missing from vocab"
            assert vocab[token] == expected_id, f"Token {token} mapped to {vocab[token]}, expected {expected_id}"

    def test_03_model_architecture_parameter_reconciliation(self):
        """Verify IGRIS 3B52 parameter counts (96,485,888 untied / 79,708,672 tied)."""
        cfg = IgrisConfig(
            vocab_size=32768,
            max_position_embeddings=2048,
            hidden_size=512,
            num_hidden_layers=16,
            num_attention_heads=8,
            num_key_value_heads=4,
            intermediate_size=2048
        )
        model = IgrisDecoderTransformer(cfg)
        counts = model.count_parameters()
        
        assert counts["total_parameters"] == 96485888
        assert counts["embedding_parameters"] == 16777216
        assert counts["lm_head_parameters"] == 16777216
        assert counts["layers_parameters"] == 62930944
        assert counts["final_norm_parameters"] == 512
        
        unique_tied = counts["total_parameters"] - counts["lm_head_parameters"]
        assert unique_tied == 79708672

    def test_04_source_decision_register_invariants(self):
        """Verify 32 sources in decision register, zero approved for acquisition, zero approved for training."""
        register_path = PATCH_ROOT / "PHASE22_SOURCE_OWNER_DECISION_REGISTER.csv"
        with open(register_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        assert len(rows) == 32, f"Expected exactly 32 candidate sources, got {len(rows)}"
        
        # Check that NO source is approved for acquisition or training
        for r in rows:
            assert r["owner_acquisition_status"] != "APPROVED_FOR_ACQUISITION", (
                f"Source {r['source_id']} prematurely approved for acquisition!"
            )
            assert r["owner_training_status"] != "APPROVED_FOR_TRAINING", (
                f"Source {r['source_id']} prematurely approved for training!"
            )
            assert r["owner_training_status"] == "NOT_APPROVED", (
                f"Source {r['source_id']} owner_training_status must be NOT_APPROVED, got {r['owner_training_status']}"
            )

        # Check IndicCorp v2 language sources have PENDING_LEGAL_REVIEW
        indiccorp_ids = {"SRC-TM-01", "SRC-HI-01", "SRC-OI-01", "SRC-OI-02", "SRC-OI-03", "SRC-OI-04", "SRC-OI-05"}
        for r in rows:
            if r["source_id"] in indiccorp_ids:
                assert r["legal_review_status"] == "PENDING_LEGAL_REVIEW", (
                    f"IndicCorp source {r['source_id']} legal status must be PENDING_LEGAL_REVIEW"
                )

        # Check 4 incompatible sources are rejected
        incompatible_ids = {"SRC-TG-03", "SRC-HI-03", "SRC-CV-01", "SRC-CV-02"}
        for r in rows:
            if r["source_id"] in incompatible_ids:
                assert r["owner_acquisition_status"] == "REJECTED"
                assert r["initial_eligibility_class"] == "INELIGIBLE_REJECTED"

    def test_05_storage_requirements_and_local_deficit(self):
        """Verify storage requirements CSV contains all stages and documents local deficit."""
        storage_path = PATCH_ROOT / "PHASE22_STORAGE_REQUIREMENTS.csv"
        with open(storage_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            
        stage_names = {r["pipeline_stage"] for r in rows}
        expected_stages = {
            "STAGE_01_INGRESS", "STAGE_02_QUARANTINE_EXPANSION", "STAGE_03_CLEANED_CORPUS",
            "STAGE_04_TOKENIZED_SHARDS", "STAGE_05_CHECKPOINTS", "STAGE_06_SCRATCH_BUFFER",
            "STAGE_PEAK_CONCURRENT", "STAGE_SEQUENTIAL_PURGE", "MEASURED_LOCAL_CAPACITY"
        }
        assert expected_stages.issubset(stage_names), f"Missing stages: {expected_stages - stage_names}"
        
        # Verify measured local capacity row
        for r in rows:
            if r["pipeline_stage"] == "MEASURED_LOCAL_CAPACITY":
                assert float(r["size_estimate_binary_gib"]) > 0
            if r["pipeline_stage"] == "STAGE_PEAK_CONCURRENT":
                assert float(r["size_estimate_decimal_gb"]) == 532.40

    def test_06_secure_acquisition_engine_gate_locked_and_isolation(self):
        """Verify SecureAcquisitionEngine defaults to LOCKED and test isolation is maintained."""
        with tempfile.TemporaryDirectory() as tmpdir:
            isolated_audit = Path(tmpdir) / "test_audit.jsonl"
            engine = SecureAcquisitionEngine(audit_log_path=isolated_audit)
            assert not engine.is_gate_unlocked(), "Acquisition gate must default to LOCKED"
            
            isolated_dest = Path(tmpdir) / "test.bin"
            with pytest.raises(AcquisitionGateLockedError):
                engine.download_source(
                    source_id="SRC-TM-01",
                    url="https://example.com/ta.txt",
                    destination_path=isolated_dest,
                    max_size_bytes=1024
                )

        # Confirm zero quarantine directories or files in PATCH_ROOT
        for root, dirs, files in os.walk(str(PATCH_ROOT)):
            for d in dirs:
                assert "quarantine" not in d.lower(), f"Unexpected quarantine dir: {os.path.join(root, d)}"
            for f in files:
                if not f.endswith(".md"):
                    assert "quarantine" not in f.lower(), f"Isolation violation: {os.path.join(root, f)}"
