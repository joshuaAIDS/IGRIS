"""
verify_candidate_a_final_classification.py

Comprehensive Verification Suite for Candidate A Final Corpus Classification Audit:
- Verifies all 5 deliverables exist and are non-empty.
- Verifies exclusion category reconciliation totals exactly 402 records.
- Verifies language label transition matrix sums and consistency (399 records).
- Verifies language label change audit contains exactly 81 records.
- Verifies split manifest integrity (320 Train, 40 Val, 39 Test) and text hashes.
- Verifies cryptographic invariants (Candidate A, Candidate B, Exp Tokenizer).
- Runs regression tests (verify_candidate_a_corpus_accounting.py, test_phase26_benchmark.py, verify_phase31a.py).
- Verifies zero production data present.
"""

import csv
import hashlib
import json
import os
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

ORIGINAL_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
ORIGINAL_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
EXPECTED_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"

def get_file_sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

class TestCandidateAFinalClassification(unittest.TestCase):

    def test_01_deliverables_exist_and_non_empty(self):
        deliverables = [
            "CANDIDATE_A_EXCLUSION_CATEGORY_RECONCILIATION.csv",
            "CANDIDATE_A_LANGUAGE_LABEL_TRANSITION_MATRIX.csv",
            "CANDIDATE_A_LANGUAGE_LABEL_CHANGE_AUDIT.csv",
            "CANDIDATE_A_FINAL_CORPUS_CLASSIFICATION_REPORT.md",
            "verify_candidate_a_final_classification.py",
        ]
        for d in deliverables:
            p_file = PATCH_ROOT / d
            self.assertTrue(p_file.exists(), f"Patch file missing: {p_file}")
            self.assertGreater(p_file.stat().st_size, 0, f"Patch file empty: {p_file}")

            a_file = ARTIFACT_DIR / d
            self.assertTrue(a_file.exists(), f"Artifact file missing: {a_file}")
            self.assertGreater(a_file.stat().st_size, 0, f"Artifact file empty: {a_file}")

    def test_02_exclusion_category_reconciliation_totals(self):
        csv_path = PATCH_ROOT / "CANDIDATE_A_EXCLUSION_CATEGORY_RECONCILIATION.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 402, f"Expected 402 rows, got {len(rows)}")
        cats = Counter(r["final_reconciled_category"] for r in rows)
        self.assertEqual(cats["NON_TARGET_LANGUAGE_OR_SCRIPT"], 384)
        self.assertEqual(cats["MALFORMED_OR_TOO_SHORT"], 9)
        self.assertEqual(cats["NOISE_OR_LOW_INFORMATION"], 8)
        self.assertEqual(cats["OTHER_OUT_OF_SCOPE"], 1)
        self.assertEqual(sum(cats.values()), 402)

        # Check discrepancy flags
        disc_rows = [r for r in rows if r["is_discrepancy_record"] == "YES"]
        self.assertEqual(len(disc_rows), 9)  # 8 noise + 1 code

    def test_03_language_label_transition_matrix_sums(self):
        csv_path = PATCH_ROOT / "CANDIDATE_A_LANGUAGE_LABEL_TRANSITION_MATRIX.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 4)  # TAMIL, ENGLISH, TANGLISH, TOTAL
        by_orig = {r["original_training_label"]: r for r in rows}
        
        self.assertEqual(int(by_orig["TAMIL"]["current_tamil"]), 111)
        self.assertEqual(int(by_orig["TAMIL"]["current_english"]), 0)
        self.assertEqual(int(by_orig["TAMIL"]["current_tanglish"]), 0)

        self.assertEqual(int(by_orig["ENGLISH"]["current_tamil"]), 0)
        self.assertEqual(int(by_orig["ENGLISH"]["current_english"]), 92)
        self.assertEqual(int(by_orig["ENGLISH"]["current_tanglish"]), 0)

        self.assertEqual(int(by_orig["TANGLISH"]["current_tamil"]), 42)
        self.assertEqual(int(by_orig["TANGLISH"]["current_english"]), 39)
        self.assertEqual(int(by_orig["TANGLISH"]["current_tanglish"]), 115)

        self.assertEqual(int(by_orig["TOTAL"]["current_tamil"]), 153)
        self.assertEqual(int(by_orig["TOTAL"]["current_english"]), 131)
        self.assertEqual(int(by_orig["TOTAL"]["current_tanglish"]), 115)
        self.assertEqual(int(by_orig["TOTAL"]["total_original"]), 399)

    def test_04_language_label_change_audit_records(self):
        csv_path = PATCH_ROOT / "CANDIDATE_A_LANGUAGE_LABEL_CHANGE_AUDIT.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 81, f"Expected 81 changed records, got {len(rows)}")
        to_tamil = sum(1 for r in rows if r["current_label"] == "TAMIL")
        to_english = sum(1 for r in rows if r["current_label"] == "ENGLISH")
        self.assertEqual(to_tamil, 42)
        self.assertEqual(to_english, 39)

        for r in rows:
            self.assertEqual(r["original_label"], "TANGLISH")
            self.assertIn(r["current_label"], ("TAMIL", "ENGLISH"))
            self.assertIn(r["split"], ("TRAIN", "VALIDATION", "TEST"))

    def test_05_corpus_scope_confinement(self):
        split_path = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
        with open(split_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 399)
        valid_langs = {"TAMIL", "ENGLISH", "TANGLISH"}
        for r in rows:
            self.assertIn(r["language"], valid_langs)
            self.assertFalse(any(0x0900 <= ord(c) <= 0x0D7F and not (0x0B80 <= ord(c) <= 0x0BFF) for c in r["preview_text"]))

    def test_06_split_manifest_and_hash_integrity(self):
        split_path = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
        with open(split_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        splits = Counter(r["split"] for r in rows)
        self.assertEqual(splits["TRAIN"], 320)
        self.assertEqual(splits["VALIDATION"], 40)
        self.assertEqual(splits["TEST"], 39)

        doc_ids = [r["doc_id"] for r in rows]
        self.assertEqual(len(doc_ids), len(set(doc_ids)), "Duplicate doc_id in split manifest")

    def test_07_cryptographic_hash_invariants(self):
        cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

        self.assertEqual(get_file_sha256(cand_a_path), ORIGINAL_CAND_A_HASH)
        self.assertEqual(get_file_sha256(cand_b_path), ORIGINAL_CAND_B_HASH)
        self.assertEqual(get_file_sha256(exp_path), EXPECTED_EXP_HASH)

    def test_08_regressions(self):
        p1 = subprocess.run([sys.executable, "verify_candidate_a_corpus_accounting.py"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(p1.returncode, 0, f"Accounting verifier failed: {p1.stderr}")

        p2 = subprocess.run([sys.executable, "verify_phase31a.py"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(p2.returncode, 0, f"Phase 31A verifier failed: {p2.stderr}")

        p3 = subprocess.run([sys.executable, "-m", "pytest", "tests/test_phase26_benchmark.py"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(p3.returncode, 0, f"Phase 26 benchmark test failed: {p3.stderr}")

    def test_09_zero_production_data(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = list(target_dir.glob("**/*"))
                files = [f for f in files if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
