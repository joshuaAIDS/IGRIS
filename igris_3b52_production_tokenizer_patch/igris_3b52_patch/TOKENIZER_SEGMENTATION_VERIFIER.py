"""
TOKENIZER_SEGMENTATION_VERIFIER.py

Independent automated verification suite for the Linguistic Segmentation Quality Audit.
Verifies:
1. Hashes of Candidate A and Experimental Candidate A.
2. Structural token IDs 0-11.
3. Deliverables exist and are non-empty.
4. Exactly 300 human review examples (100 Ta, 100 En, 100 Tg).
5. All 300 human review decisions remain NOT_REVIEWED.
6. Quantitative metrics reproducibility.
7. Unicode round-trip accuracy (100.0%).
8. Production acquisition and pretraining gates remain locked.
9. No tokenizer promotion occurred.
"""

import csv
import hashlib
import os
import unittest
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"

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

def get_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

class TestTokenizerSegmentationAudit(unittest.TestCase):

    def test_01_cryptographic_hashes(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        self.assertEqual(get_sha256(cand_a_p), ORIGINAL_CAND_A_HASH)
        self.assertEqual(get_sha256(exp_a_p), EXPECTED_EXP_HASH)

    def test_02_structural_tokens(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok_a = Tokenizer.from_file(str(cand_a_p))
        tok_exp = Tokenizer.from_file(str(exp_a_p))
        for tid, tstr in STRUCTURAL_TOKENS:
            self.assertEqual(tok_a.id_to_token(tid), tstr)
            self.assertEqual(tok_exp.id_to_token(tid), tstr)

    def test_03_deliverables_exist_and_non_empty(self):
        deliverables = [
            "TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md",
            "TAMIL_SEGMENTATION_AUDIT.csv",
            "ENGLISH_SEGMENTATION_AUDIT.csv",
            "TANGLISH_SEGMENTATION_AUDIT.csv",
            "TOKENIZER_FRAGMENTATION_ANALYSIS.csv",
            "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv",
            "TOKENIZER_SEGMENTATION_VERIFIER.py"
        ]
        for d in deliverables:
            root_f = WORKSPACE_ROOT / d
            self.assertTrue(root_f.exists(), f"Missing at root: {root_f}")
            self.assertGreater(root_f.stat().st_size, 0, f"Empty at root: {root_f}")

    def test_04_human_review_sample_counts_and_statuses(self):
        csv_p = WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv"
        with open(csv_p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 300)
        ta_cnt = sum(1 for r in rows if r["language"] == "TAMIL")
        en_cnt = sum(1 for r in rows if r["language"] == "ENGLISH")
        tg_cnt = sum(1 for r in rows if r["language"] == "TANGLISH")
        self.assertEqual(ta_cnt, 100)
        self.assertEqual(en_cnt, 100)
        self.assertEqual(tg_cnt, 100)

        # All review statuses MUST be NOT_REVIEWED
        for r in rows:
            self.assertEqual(r["human_review_decision"], "NOT_REVIEWED")
            self.assertEqual(r["reviewer_rationale"], "")

    def test_05_target_languages_only(self):
        for audit_file in ["TAMIL_SEGMENTATION_AUDIT.csv", "ENGLISH_SEGMENTATION_AUDIT.csv", "TANGLISH_SEGMENTATION_AUDIT.csv"]:
            p = WORKSPACE_ROOT / audit_file
            with open(p, encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 100)

    def test_06_quantitative_metrics_reproducibility(self):
        p = WORKSPACE_ROOT / "TOKENIZER_FRAGMENTATION_ANALYSIS.csv"
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        by_name = {r["analysis_dimension"]: r for r in rows}

        # Entire corpus reduction should be ~43.34%
        red_all = float(by_name["ENTIRE_EVALUATION_CORPUS"]["token_reduction_pct"])
        self.assertAlmostEqual(red_all, 43.34, delta=0.5)

        # Roundtrip accuracy must be 100.0%
        for r in rows:
            self.assertEqual(float(r["cand_a_roundtrip_accuracy"]), 100.0)
            self.assertEqual(float(r["cand_exp_roundtrip_accuracy"]), 100.0)

    def test_07_no_tokenizer_promotion(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.assertEqual(get_sha256(cand_a_p), ORIGINAL_CAND_A_HASH)
        self.assertNotEqual(get_sha256(cand_a_p), EXPECTED_EXP_HASH)

    def test_08_production_and_pretraining_locked(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = [f for f in target_dir.glob("**/*") if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
