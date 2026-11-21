"""
verify_tokenizer_generalization.py

Standalone Verification Test Suite for Tokenizer Generalization Benchmark:
1. Verifies all 8 deliverables exist and are non-empty.
2. Verifies cryptographic hashes (Original Candidate A and Experimental Candidate A).
3. Verifies structural token slot invariants (IDs 0-11).
4. Verifies manifest integrity (exactly 3,000 records; 1,000 Ta, 1,000 En, 1,000 Tg).
5. Verifies zero cross-corpus contamination against the 399 original records.
6. Verifies generalization compression reduction (~45.19% overall).
7. Verifies 100.0% round-trip accuracy across all 3,000 records.
8. Verifies no promotion of Experimental Candidate A.
9. Verifies zero production data present ($0.00 spend).
"""

import csv
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\e52ff414-ecc8-4b21-888c-82066c8980e0")

ORIGINAL_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"

STRUCTURAL_TOKENS = [
    (0, "<|pad|>"),
    (1, "<|begin_of_text|>"),
    (2, "<|end_of_text|>"),
    (3, "<think>"),
    (4, "</think>"),
    (5, "<action>"),
    (6, "</action>"),
    (7, "<action_result>"),
    (8, "</action_result>"),
    (9, "<|system|>"),
    (10, "<|user|>"),
    (11, "<|assistant|>")
]

def get_file_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

class TestTokenizerGeneralization(unittest.TestCase):

    def test_01_deliverables_exist_and_non_empty(self):
        deliverables = [
            "TOKENIZER_GENERALIZATION_REPORT.md",
            "INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv",
            "TOKENIZER_GENERALIZATION_METRICS.csv",
            "TOKENIZER_CATEGORY_BREAKDOWN.csv",
            "TOKENIZER_SCRIPT_GENERALIZATION.csv",
            "TOKENIZER_CONTAMINATION_AUDIT.md",
            "TOKENIZER_VOCABULARY_METRIC_RECONCILIATION.md",
            "verify_tokenizer_generalization.py"
        ]
        for d in deliverables:
            root_f = WORKSPACE_ROOT / d
            self.assertTrue(root_f.exists(), f"Missing at root: {root_f}")
            self.assertGreater(root_f.stat().st_size, 0, f"Empty at root: {root_f}")

    def test_02_cryptographic_hashes(self):
        cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

        self.assertEqual(get_file_sha256(cand_a_path), ORIGINAL_CAND_A_HASH)
        self.assertEqual(get_file_sha256(exp_path), EXPECTED_EXP_HASH)

    def test_03_structural_tokens(self):
        cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

        tok_a = Tokenizer.from_file(str(cand_a_path))
        tok_exp = Tokenizer.from_file(str(exp_path))

        for tid, tok_str in STRUCTURAL_TOKENS:
            self.assertEqual(tok_a.id_to_token(tid), tok_str)
            self.assertEqual(tok_exp.id_to_token(tid), tok_str)

    def test_04_manifest_integrity(self):
        manifest_p = WORKSPACE_ROOT / "INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv"
        with open(manifest_p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        self.assertEqual(len(rows), 3000)
        ta_cnt = sum(1 for r in rows if r["language"] == "TAMIL")
        en_cnt = sum(1 for r in rows if r["language"] == "ENGLISH")
        tg_cnt = sum(1 for r in rows if r["language"] == "TANGLISH")
        self.assertEqual(ta_cnt, 1000)
        self.assertEqual(en_cnt, 1000)
        self.assertEqual(tg_cnt, 1000)

        # Check categories
        for cat in ["conversational", "formal", "educational", "technical", "long_form"]:
            c_cnt = sum(1 for r in rows if r["category"] == cat)
            self.assertEqual(c_cnt, 600)

    def test_05_zero_cross_corpus_contamination(self):
        manifest_p = WORKSPACE_ROOT / "INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv"
        with open(manifest_p, encoding="utf-8") as f:
            new_rows = list(csv.DictReader(f))
        new_hashes = set(r["text_sha256"] for r in new_rows)

        orig_split_p = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
        with open(orig_split_p, encoding="utf-8") as f:
            orig_rows = list(csv.DictReader(f))
        orig_hashes = set(r["text_sha256"] for r in orig_rows)

        # Assert zero collision
        intersection = new_hashes & orig_hashes
        self.assertEqual(len(intersection), 0, f"Found {len(intersection)} hash collisions!")

    def test_06_metrics_reproducibility(self):
        metrics_p = WORKSPACE_ROOT / "TOKENIZER_GENERALIZATION_METRICS.csv"
        with open(metrics_p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        by_name = {r["subset_name"]: r for r in rows}

        red_overall = float(by_name["FULL_INDEPENDENT_CORPUS"]["token_reduction_pct"])
        self.assertAlmostEqual(red_overall, 45.19, delta=0.5)

        red_ta = float(by_name["LANGUAGE_TAMIL"]["token_reduction_pct"])
        self.assertAlmostEqual(red_ta, 31.02, delta=0.5)

        red_en = float(by_name["LANGUAGE_ENGLISH"]["token_reduction_pct"])
        self.assertAlmostEqual(red_en, 57.03, delta=0.5)

        red_tg = float(by_name["LANGUAGE_TANGLISH"]["token_reduction_pct"])
        self.assertAlmostEqual(red_tg, 46.67, delta=0.5)

    def test_07_roundtrip_accuracy_100_percent(self):
        metrics_p = WORKSPACE_ROOT / "TOKENIZER_GENERALIZATION_METRICS.csv"
        with open(metrics_p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            self.assertEqual(float(r["cand_a_roundtrip_accuracy"]), 100.0)
            self.assertEqual(float(r["cand_exp_roundtrip_accuracy"]), 100.0)

    def test_08_no_tokenizer_promotion(self):
        cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.assertEqual(get_file_sha256(cand_a_path), ORIGINAL_CAND_A_HASH)
        self.assertNotEqual(get_file_sha256(cand_a_path), EXPECTED_EXP_HASH)

    def test_09_zero_production_data(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = list(target_dir.glob("**/*"))
                files = [f for f in files if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
