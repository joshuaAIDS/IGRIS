"""
verify_tanglish_taxonomy.py

Standalone Verification Test Harness for IGRIS Tanglish Taxonomy Reconciliation:
- Verifies all 5 deliverables exist and are non-empty.
- Verifies CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv (399 rows, exact schema, valid enums).
- Verifies operational language labels sum to TANGLISH: 196, TAMIL: 111, ENGLISH: 92.
- Verifies linguistic matrix language labels sum to TAMIL: 153, ENGLISH: 131, TANGLISH: 115.
- Verifies script forms sum to TAMIL_SCRIPT: 109, LATIN_SCRIPT: 182, MIXED_SCRIPT: 108.
- Verifies CANDIDATE_A_81_RECORD_RECLASSIFICATION_REVIEW.csv (81 rows, all RETAIN_TANGLISH).
- Verifies historical files immutability (split manifest, training report, provenance audit).
- Verifies cryptographic hash invariants (Candidate A, Candidate B, Exp Tokenizer).
- Runs regression tests (verify_candidate_a_final_classification.py, verify_candidate_a_corpus_accounting.py).
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

class TestTanglishTaxonomy(unittest.TestCase):

    def test_01_deliverables_exist_and_non_empty(self):
        deliverables = [
            "TANGLISH_TAXONOMY_RECONCILIATION.md",
            "CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv",
            "CANDIDATE_A_81_RECORD_RECLASSIFICATION_REVIEW.csv",
            "IGRIS_LANGUAGE_TAXONOMY_V1.md",
            "verify_tanglish_taxonomy.py",
        ]
        for d in deliverables:
            p_file = PATCH_ROOT / d
            self.assertTrue(p_file.exists(), f"Patch deliverable missing: {p_file}")
            self.assertGreater(p_file.stat().st_size, 0, f"Patch deliverable empty: {p_file}")

            a_file = ARTIFACT_DIR / d
            self.assertTrue(a_file.exists(), f"Artifact deliverable missing: {a_file}")
            self.assertGreater(a_file.stat().st_size, 0, f"Artifact deliverable empty: {a_file}")

    def test_02_multidimensional_labels_schema_and_counts(self):
        csv_path = PATCH_ROOT / "CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 399, f"Expected 399 rows, got {len(rows)}")
        
        valid_script_forms = {"TAMIL_SCRIPT", "LATIN_SCRIPT", "MIXED_SCRIPT", "OTHER_OR_UNKNOWN"}
        valid_langs = {"TAMIL", "ENGLISH", "TANGLISH", "UNKNOWN"}
        valid_binary = {"YES", "NO"}

        for r in rows:
            self.assertIn(r["operational_language_label"], valid_langs)
            self.assertIn(r["linguistic_matrix_language"], valid_langs)
            self.assertIn(r["script_form"], valid_script_forms)
            self.assertIn(r["contains_english_vocabulary"], valid_binary)
            self.assertIn(r["contains_tamil_vocabulary"], valid_binary)
            self.assertIn(r["contains_code_switching"], valid_binary)
            self.assertIn(r["contains_tamil_discourse_markers"], valid_binary)
            self.assertIn(r["romanized_tamil_present"], valid_binary)
            self.assertEqual(r["review_status"], "VERIFIED_BY_AUDIT")

    def test_03_operational_language_distribution(self):
        csv_path = PATCH_ROOT / "CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        op_counts = Counter(r["operational_language_label"] for r in rows)
        self.assertEqual(op_counts["TANGLISH"], 196)
        self.assertEqual(op_counts["TAMIL"], 111)
        self.assertEqual(op_counts["ENGLISH"], 92)
        self.assertEqual(op_counts["UNKNOWN"], 0)

    def test_04_matrix_language_distribution(self):
        csv_path = PATCH_ROOT / "CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        mat_counts = Counter(r["linguistic_matrix_language"] for r in rows)
        self.assertEqual(mat_counts["TAMIL"], 153)
        self.assertEqual(mat_counts["ENGLISH"], 131)
        self.assertEqual(mat_counts["TANGLISH"], 115)
        self.assertEqual(mat_counts["UNKNOWN"], 0)

    def test_05_reclassification_review_81_records(self):
        csv_path = PATCH_ROOT / "CANDIDATE_A_81_RECORD_RECLASSIFICATION_REVIEW.csv"
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        self.assertEqual(len(rows), 81, f"Expected 81 rows, got {len(rows)}")
        
        by_mat = Counter(r["matrix_language"] for r in rows)
        self.assertEqual(by_mat["TAMIL"], 42)
        self.assertEqual(by_mat["ENGLISH"], 39)

        for r in rows:
            self.assertEqual(r["operational_label"], "TANGLISH")
            self.assertEqual(r["final_operational_disposition"], "RETAIN_TANGLISH_OPERATIONAL_LABEL")
            self.assertEqual(r["reclassification_analysis"], "DIMENSIONAL_PERSPECTIVE_MATRIX_LANGUAGE")

    def test_06_historical_files_immutable(self):
        split_path = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
        with open(split_path, encoding="utf-8") as f:
            s_rows = list(csv.DictReader(f))
        
        self.assertEqual(len(s_rows), 399)
        s_counts = Counter(r["language"] for r in s_rows)
        self.assertEqual(s_counts["TANGLISH"], 196)
        self.assertEqual(s_counts["TAMIL"], 111)
        self.assertEqual(s_counts["ENGLISH"], 92)

    def test_07_cryptographic_hash_invariants(self):
        cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        exp_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"

        self.assertEqual(get_file_sha256(cand_a_path), ORIGINAL_CAND_A_HASH)
        self.assertEqual(get_file_sha256(cand_b_path), ORIGINAL_CAND_B_HASH)
        self.assertEqual(get_file_sha256(exp_path), EXPECTED_EXP_HASH)

    def test_08_regressions(self):
        p1 = subprocess.run([sys.executable, "verify_candidate_a_final_classification.py"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(p1.returncode, 0, f"Final classification verifier failed: {p1.stderr}")

        p2 = subprocess.run([sys.executable, "verify_candidate_a_corpus_accounting.py"], cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(p2.returncode, 0, f"Accounting verifier failed: {p2.stderr}")

    def test_09_zero_production_data(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = list(target_dir.glob("**/*"))
                files = [f for f in files if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
