"""
verify_owner_review_package.py

Automated verification suite for the 30-Example Owner-Review Package.
"""

import csv
import hashlib
import unittest
from pathlib import Path
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CAND_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"
CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

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

class TestOwnerReviewPackage(unittest.TestCase):

    def test_01_cryptographic_hashes(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        cand_b_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        
        self.assertEqual(get_sha256(cand_a_p), CAND_A_HASH, "Candidate A hash corrupted!")
        self.assertEqual(get_sha256(exp_a_p), CAND_EXP_HASH, "Experimental Candidate A hash corrupted!")
        self.assertEqual(get_sha256(cand_b_p), CAND_B_HASH, "Candidate B hash corrupted!")

    def test_02_structural_tokens(self):
        cand_a_p = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        exp_a_p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok_a = Tokenizer.from_file(str(cand_a_p))
        tok_exp = Tokenizer.from_file(str(exp_a_p))
        for tid, tstr in STRUCTURAL_TOKENS:
            self.assertEqual(tok_a.id_to_token(tid), tstr)
            self.assertEqual(tok_exp.id_to_token(tid), tstr)

    def test_03_deliverables_presence_across_all_locations(self):
        deliverables = [
            "TOKENIZER_OWNER_REVIEW_30.csv",
            "TOKENIZER_OWNER_REVIEW_GUIDE.md",
            "TOKENIZER_UNICODE_DIAGNOSTICS.md",
            "TOKENIZER_OWNER_REVIEW_SUMMARY.md"
        ]
        for loc in [WORKSPACE_ROOT, PATCH_ROOT, ARTIFACT_DIR]:
            for d in deliverables:
                p = loc / d
                self.assertTrue(p.exists(), f"Missing deliverable: {p}")
                self.assertGreater(p.stat().st_size, 0, f"Empty deliverable: {p}")

    def test_04_owner_review_30_csv_structure_and_governance(self):
        csv_path = WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_30.csv"
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        
        self.assertEqual(len(reader), 30, f"Expected exactly 30 rows, got {len(reader)}")
        
        ta_count = sum(1 for r in reader if r["language"] == "TAMIL")
        en_count = sum(1 for r in reader if r["language"] == "ENGLISH")
        tg_count = sum(1 for r in reader if r["language"] == "TANGLISH")
        self.assertEqual(ta_count, 10, f"Expected 10 Tamil, got {ta_count}")
        self.assertEqual(en_count, 10, f"Expected 10 English, got {en_count}")
        self.assertEqual(tg_count, 10, f"Expected 10 Tanglish, got {tg_count}")

        # Strict governance checks
        for r in reader:
            self.assertEqual(r["human_review_decision"], "NOT_REVIEWED", f"Row {r['review_id']} not NOT_REVIEWED!")
            self.assertEqual(r["reviewer_rationale"], "", f"Row {r['review_id']} rationale not empty!")
            self.assertTrue(len(r["suggested_decision_options"]) > 0, f"Row {r['review_id']} missing options!")
            self.assertTrue(len(r["unicode_codepoints"]) > 0, f"Row {r['review_id']} missing codepoints!")
            self.assertTrue(len(r["grapheme_clusters"]) > 0, f"Row {r['review_id']} missing grapheme clusters!")

    def test_05_human_review_sample_300_governance(self):
        csv_path = WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv"
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 300)
        for r in reader:
            self.assertEqual(r["human_review_decision"], "NOT_REVIEWED")
            self.assertEqual(r["reviewer_rationale"], "")

    def test_06_guide_covers_all_30_ids(self):
        guide_text = (WORKSPACE_ROOT / "TOKENIZER_OWNER_REVIEW_GUIDE.md").read_text(encoding="utf-8")
        for i in range(1, 31):
            rev_id = f"OWN-REV-{i:02d}"
            self.assertIn(rev_id, guide_text, f"Missing {rev_id} in review guide!")

    def test_07_unicode_diagnostics_content(self):
        diag_text = (WORKSPACE_ROOT / "TOKENIZER_UNICODE_DIAGNOSTICS.md").read_text(encoding="utf-8")
        self.assertIn("bytes_to_unicode", diag_text)
        self.assertIn("à®¤", diag_text)
        self.assertIn("à¯į", diag_text)
        self.assertIn("Ġ", diag_text)
        self.assertIn("100.0%", diag_text)
        self.assertIn("NFC", diag_text)
        self.assertIn("NFD", diag_text)

    def test_08_production_data_and_pretraining_locked(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = [f for f in target_dir.glob("**/*") if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
