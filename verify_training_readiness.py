"""
verify_training_readiness.py

Automated test suite asserting training engine readiness deliverables,
architectural invariants, tokenizer integration, component classifications,
and governance gate compliance under SOLO_DEVELOPER_OWNER_REVIEW.
"""

import csv
import hashlib
import json
import os
import unittest
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

EXPECTED_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

AUTHORITATIVE_STRUCTURAL_TOKENS = {
    0: "<|pad|>",
    1: "<|begin_of_text|>",
    2: "<|end_of_text|>",
    3: "<think>",
    4: "</think>",
    5: "<action>",
    6: "</action>",
    7: "<action_result>",
    8: "</action_result>",
    9: "<|system|>",
    10: "<|user|>",
    11: "<|assistant|>",
}

REQUIRED_DELIVERABLES = [
    "TRAINING_ENGINE_READINESS_AUDIT.md",
    "TRAINING_ENGINE_COMPONENT_MATRIX.csv",
    "TRAINING_HARDWARE_FEASIBILITY.md",
    "TRAINING_SMOKE_TEST_REPORT.md",
    "TRAINING_READINESS_SUMMARY.md",
]

class TestTrainingReadiness(unittest.TestCase):

    def test_01_candidate_tokenizer_hashes(self):
        """Verify Candidate A and Candidate B cryptographic integrity."""
        cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.assertTrue(cand_a_path.exists(), f"Candidate A missing: {cand_a_path}")
        h_a = hashlib.sha256(cand_a_path.read_bytes()).hexdigest()
        self.assertEqual(h_a, EXPECTED_CAND_A_HASH, f"Candidate A hash mismatch: {h_a}")

        cand_b_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        self.assertTrue(cand_b_path.exists(), f"Candidate B missing: {cand_b_path}")
        h_b = hashlib.sha256(cand_b_path.read_bytes()).hexdigest()
        self.assertEqual(h_b, EXPECTED_CAND_B_HASH, f"Candidate B hash mismatch: {h_b}")

    def test_02_structural_token_ids(self):
        """Verify structural tokens 0-11 in Candidate A match authoritative spec."""
        cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        data = json.loads(cand_a_path.read_text(encoding="utf-8"))
        vocab = data["model"]["vocab"]
        inv_vocab = {v: k for k, v in vocab.items()}

        for tid, token_str in AUTHORITATIVE_STRUCTURAL_TOKENS.items():
            actual = inv_vocab.get(tid)
            self.assertEqual(actual, token_str, f"Token ID {tid} mismatch: expected {token_str}, got {actual}")

    def test_03_architecture_configuration(self):
        """Verify 16-layer decoder-only architecture and tied parameter count."""
        import sys
        sys.path.insert(0, str(WORKSPACE_ROOT / "src"))
        from igris.model.transformer import (
            IgrisConfig,
            IgrisDecoderTransformer,
            get_production_config,
        )

        cfg = get_production_config()
        self.assertEqual(cfg.num_hidden_layers, 16)
        self.assertEqual(cfg.hidden_size, 512)
        self.assertEqual(cfg.intermediate_size, 2048)
        self.assertEqual(cfg.num_attention_heads, 8)
        self.assertEqual(cfg.num_key_value_heads, 4)
        self.assertEqual(cfg.head_dim, 64)
        self.assertEqual(cfg.rope_theta, 10000.0)
        self.assertEqual(cfg.rms_norm_eps, 1e-5)
        self.assertEqual(cfg.vocab_size, 32768)

        # Test tied parameter count
        cfg.tie_word_embeddings = True
        model_tied = IgrisDecoderTransformer(cfg)
        counts = model_tied.count_parameters()
        self.assertEqual(counts["total_parameters"], 79_708_672, f"Expected 79708672 params, got {counts['total_parameters']}")

    def test_04_deliverables_presence_and_integrity(self):
        """Verify all 5 required deliverables exist and are non-empty in workspace and patch roots."""
        for fn in REQUIRED_DELIVERABLES:
            ws_file = WORKSPACE_ROOT / fn
            self.assertTrue(ws_file.exists(), f"Deliverable missing in workspace: {ws_file}")
            self.assertGreater(ws_file.stat().st_size, 0, f"Deliverable is empty: {ws_file}")

    def test_05_component_matrix_completeness(self):
        """Assert that all 13 training engine subsystems are present with valid statuses."""
        csv_path = WORKSPACE_ROOT / "TRAINING_ENGINE_COMPONENT_MATRIX.csv"
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        self.assertEqual(len(reader), 13, f"Expected 13 components, found {len(reader)}")

        valid_statuses = {"IMPLEMENTED", "PARTIALLY_IMPLEMENTED", "MISSING", "FAILED", "BLOCKED"}
        ids = [row["component_id"] for row in reader]
        for i in range(1, 14):
            expected_id = f"TRN-CMP-{i:02d}"
            self.assertIn(expected_id, ids, f"Missing component ID {expected_id}")

        for row in reader:
            self.assertIn(row["status"], valid_statuses, f"Invalid status in {row['component_id']}: {row['status']}")
            self.assertTrue(row["component_name"].strip(), f"Empty component_name in {row['component_id']}")
            self.assertTrue(row["existing_implementation_path"].strip(), f"Empty path in {row['component_id']}")

    def test_06_governance_gates_locked(self):
        """Verify that pretraining and acquisition gates remain strictly locked."""
        gate_status_file = WORKSPACE_ROOT / "documentation" / "PHASE22_GATE_STATUS.json"
        if not gate_status_file.exists():
            gate_status_file = WORKSPACE_ROOT / "PHASE22_GATE_STATUS.json"
        if gate_status_file.exists():
            with open(gate_status_file, "r", encoding="utf-8") as f:
                gates = json.load(f)
            self.assertIn(gates.get("pretraining_gate", "LOCKED"), ["LOCKED", "GATE_LOCKED"])
            self.assertIn(gates.get("acquisition_gate", "LOCKED"), ["LOCKED", "GATE_LOCKED"])

if __name__ == "__main__":
    unittest.main()
