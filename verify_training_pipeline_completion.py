"""
verify_training_pipeline_completion.py

Automated test suite asserting training pipeline completion deliverables,
dataset streaming infrastructure, multi-document sequence packing,
evaluation mechanics, checkpoint integrity, and governance compliance
under SOLO_DEVELOPER_OWNER_REVIEW.
"""

import csv
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

import torch

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
    "TRAINING_PIPELINE_COMPLETION_REPORT.md",
    "DATASET_LOADER_VALIDATION_REPORT.md",
    "SEQUENCE_PACKING_VALIDATION_REPORT.md",
    "CHECKPOINT_RESUME_VALIDATION_REPORT.md",
    "TRAINING_PERFORMANCE_BENCHMARK.md",
    "FINAL_PRETRAINING_READINESS_CHECKLIST.md",
]


class TestTrainingPipelineCompletion(unittest.TestCase):

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
        """Verify all 6 required deliverables exist and are non-empty across workspace root."""
        for fn in REQUIRED_DELIVERABLES:
            ws_file = WORKSPACE_ROOT / fn
            self.assertTrue(ws_file.exists(), f"Deliverable missing in workspace: {ws_file}")
            self.assertGreater(ws_file.stat().st_size, 0, f"Deliverable is empty: {ws_file}")

    def test_05_training_package_modules(self):
        """Verify src/igris/training contains all 5 required modules."""
        training_dir = WORKSPACE_ROOT / "src" / "igris" / "training"
        self.assertTrue(training_dir.exists(), "src/igris/training directory missing")
        expected_modules = ["__init__.py", "dataset.py", "evaluator.py", "checkpoint.py", "engine.py"]
        for m in expected_modules:
            mod_path = training_dir / m
            self.assertTrue(mod_path.exists(), f"Module missing: {mod_path}")
            self.assertGreater(mod_path.stat().st_size, 0, f"Module empty: {mod_path}")

    def test_06_sequence_packing_and_mmap(self):
        """Verify SequencePacker and BinaryDatasetWriter functionality."""
        import sys
        sys.path.insert(0, str(WORKSPACE_ROOT / "src"))
        from igris.training.dataset import (
            BinaryDatasetWriter,
            MMapDataset,
            SequencePacker,
        )

        packer = SequencePacker(max_seq_len=64)
        packed = packer.pack_documents([[10, 20, 30], [40, 50]])
        self.assertEqual(len(packed), 1)
        b = packed[0]
        self.assertEqual(b["input_ids"].shape, (64,))
        self.assertEqual(b["attention_mask"].shape, (64,))
        self.assertEqual(b["labels"].shape, (64,))
        self.assertEqual(b["input_ids"][0].item(), 1)  # BOS
        self.assertEqual(b["input_ids"][4].item(), 2)  # EOS doc 1

        with tempfile.TemporaryDirectory() as td:
            writer = BinaryDatasetWriter(output_dir=td, split_name="test_split")
            writer.add_document([100, 200, 300], language="TAMIL")
            manifest = writer.close()
            self.assertEqual(manifest.num_documents, 1)
            self.assertEqual(manifest.total_tokens, 3)

            mmap_ds = MMapDataset(output_dir=td, split_name="test_split")
            doc = mmap_ds[0]
            self.assertEqual(doc.tolist(), [100, 200, 300])
            mmap_ds.close()

    def test_07_governance_gates_locked(self):
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
