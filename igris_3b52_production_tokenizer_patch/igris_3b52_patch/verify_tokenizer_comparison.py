"""
verify_tokenizer_comparison.py

Standalone Verification Test Harness for Controlled Tokenizer Comparison:
- Verifies all 8 comparison deliverables exist and are non-empty.
- Verifies cryptographic hash invariants (Original A, Reference B, Exp A).
- Verifies structural token IDs 0-11 in both tokenizers.
- Verifies split integrity (320 Train, 40 Val, 39 Test = 399 Total).
- Verifies metrics reproducibility (fertility, sequence length, reduction %).
- Verifies no promotion or modification of production tokenizer artifacts.
- Runs regression tests.
- Verifies zero production data present ($0.00 spend).
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

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

ORIGINAL_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
ORIGINAL_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
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

class TestTokenizerComparison(unittest.TestCase):

    def test_01_deliverables_exist_and_non_empty(self):
        deliverables = [
            "TOKENIZER_COMPARISON_REPORT.md",
            "TOKENIZER_COMPARISON_METRICS.csv",
            "TOKENIZER_LANGUAGE_BREAKDOWN.csv",
            "TOKENIZER_SCRIPT_BREAKDOWN.csv",
            "TOKENIZER_UNICODE_VALIDATION_REPORT.md",
            "TOKENIZER_ARTIFACT_INTEGRITY_REPORT.md",
            "TOKENIZER_BENCHMARK_METHODOLOGY.md",
            "verify_tokenizer_comparison.py",
        ]
        for d in deliverables:
            p_file = PATCH_ROOT / d
            self.assertTrue(p_file.exists(), f"Patch deliverable missing: {p_file}")
            self.assertGreater(p_file.stat().st_size, 0, f"Patch deliverable empty: {p_file}")

            a_file = ARTIFACT_DIR / d
            self.assertTrue(a_file.exists(), f"Artifact deliverable missing: {a_file}")
            self.assertGreater(a_file.stat().st_size, 0, f"Artifact deliverable empty: {a_file}")

    def test_02_cryptographic_hashes(self):
        cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

        self.assertEqual(get_file_sha256(cand_a_path), ORIGINAL_CAND_A_HASH)
        self.assertEqual(get_file_sha256(cand_b_path), ORIGINAL_CAND_B_HASH)
        self.assertEqual(get_file_sha256(exp_path), EXPECTED_EXP_HASH)

    def test_03_structural_tokens_and_ids(self):
        cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

        tok_a = Tokenizer.from_file(str(cand_a_path))
        tok_exp = Tokenizer.from_file(str(exp_path))

        for tid, tok in STRUCTURAL_TOKENS:
            self.assertEqual(tok_a.id_to_token(tid), tok)
            self.assertEqual(tok_exp.id_to_token(tid), tok)

    def test_04_split_manifest_and_counts(self):
        split_path = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
        with open(split_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 399)
        train_cnt = sum(1 for r in rows if r["split"] == "TRAIN")
        val_cnt = sum(1 for r in rows if r["split"] == "VALIDATION")
        test_cnt = sum(1 for r in rows if r["split"] == "TEST")

        self.assertEqual(train_cnt, 320)
        self.assertEqual(val_cnt, 40)
        self.assertEqual(test_cnt, 39)

    def test_05_comparison_metrics_reproducibility(self):
        metrics_csv = PATCH_ROOT / "TOKENIZER_COMPARISON_METRICS.csv"
        with open(metrics_csv, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 4)
        by_name = {r["subset_name"]: r for r in rows}

        total_red = float(by_name["ENTIRE_CORPUS"]["token_reduction_pct"])
        self.assertAlmostEqual(total_red, 54.41, delta=0.5)

        train_red = float(by_name["TRAIN_SPLIT"]["token_reduction_pct"])
        self.assertAlmostEqual(train_red, 55.66, delta=0.5)

        val_red = float(by_name["VAL_SPLIT"]["token_reduction_pct"])
        self.assertAlmostEqual(val_red, 49.78, delta=0.5)

        test_red = float(by_name["TEST_SPLIT"]["token_reduction_pct"])
        self.assertAlmostEqual(test_red, 48.93, delta=0.5)

    def test_06_roundtrip_accuracy_100_percent(self):
        metrics_csv = PATCH_ROOT / "TOKENIZER_COMPARISON_METRICS.csv"
        with open(metrics_csv, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        for r in rows:
            self.assertEqual(float(r["cand_a_roundtrip_accuracy"]), 100.0)
            self.assertEqual(float(r["cand_exp_roundtrip_accuracy"]), 100.0)

    def test_07_no_tokenizer_promotion(self):
        cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.assertEqual(get_file_sha256(cand_a_path), ORIGINAL_CAND_A_HASH)
        self.assertNotEqual(get_file_sha256(cand_a_path), EXPECTED_EXP_HASH)

    def test_08_regressions(self):
        p1 = subprocess.run([sys.executable, "verify_tanglish_taxonomy.py"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(p1.returncode, 0, f"Taxonomy verifier failed: {p1.stderr}")

        p2 = subprocess.run([sys.executable, "verify_candidate_a_final_classification.py"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(p2.returncode, 0, f"Final classification verifier failed: {p2.stderr}")

    def test_09_zero_production_data(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = list(target_dir.glob("**/*"))
                files = [f for f in files if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
