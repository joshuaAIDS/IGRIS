"""
verify_candidate_a_corpus_accounting.py

Automated Verification Suite for Candidate A Corpus Accounting Audit:
1. Verifies all 5 accounting audit deliverables exist and are non-empty.
2. Reconciles raw harvest count to exactly 1,084.
3. Verifies mathematical balance: 399 approved + 283 duplicates + 402 exclusions = 1,084 raw.
4. Verifies CANDIDATE_A_EXCLUSION_AUDIT.csv has exactly 402 rows.
5. Verifies CANDIDATE_A_PROVENANCE_AUDIT.csv has exactly 399 rows, 100% code-free.
6. Verifies split manifest has 320 Train, 40 Val, 39 Test.
7. Verifies cryptographic hashes for Candidate A, B, and Experimental Tokenizer.
8. Runs regression test suites.
"""

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

EXPECTED_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
EXPECTED_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"

ACCOUNTING_DELIVERABLES = [
    "CANDIDATE_A_CORPUS_ACCOUNTING_CORRECTION.md",
    "CANDIDATE_A_SOURCE_COUNT_RECONCILIATION.csv",
    "CANDIDATE_A_EXCLUSION_AUDIT.csv",
    "CANDIDATE_A_PROVENANCE_AUDIT.csv",
    "verify_candidate_a_corpus_accounting.py",
]

class TestCandidateACorpusAccounting(unittest.TestCase):

    def test_01_accounting_deliverables_exist_and_non_empty(self):
        for fname in ACCOUNTING_DELIVERABLES:
            p = PATCH_ROOT / fname
            self.assertTrue(p.exists(), f"Deliverable missing: {fname}")
            self.assertGreater(p.stat().st_size, 0, f"Deliverable empty: {fname}")

    def test_02_raw_reconciliation_balance(self):
        p = PATCH_ROOT / "CANDIDATE_A_SOURCE_COUNT_RECONCILIATION.csv"
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        file_rows = [r for r in rows if r["source_file"] != "TOTAL_RECONCILED"]
        self.assertEqual(len(file_rows), 8)
        
        tot_raw = sum(int(r["actual_raw_harvest"]) for r in file_rows)
        tot_approved = sum(int(r["final_unique_approved"]) for r in file_rows)
        tot_exact_dup = sum(int(r["exact_duplicates_removed"]) for r in file_rows)
        tot_norm_dup = sum(int(r["normalized_duplicates_removed"]) for r in file_rows)
        tot_near_dup = sum(int(r["near_duplicates_removed"]) for r in file_rows)
        tot_non_target = sum(int(r["non_target_script_excluded"]) for r in file_rows)
        tot_malformed = sum(int(r["malformed_excluded"]) for r in file_rows)
        tot_noise = sum(int(r["unclassifiable_noise_excluded"]) for r in file_rows)
        
        tot_dup = tot_exact_dup + tot_norm_dup + tot_near_dup
        tot_excluded = tot_non_target + tot_malformed + tot_noise
        
        self.assertEqual(tot_raw, 1084)
        self.assertEqual(tot_approved, 399)
        self.assertEqual(tot_dup, 283)
        self.assertEqual(tot_excluded, 402)
        self.assertEqual(tot_approved + tot_dup + tot_excluded, 1084)

    def test_03_exclusion_audit_rows_count(self):
        p = PATCH_ROOT / "CANDIDATE_A_EXCLUSION_AUDIT.csv"
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 402)
        
        # Verify non-target scripts
        scripts = set(r["specific_reason"] for r in rows if r["exclusion_category"] == "NON_TARGET_SCRIPT")
        self.assertIn("Devanagari", scripts)
        self.assertIn("Telugu", scripts)
        self.assertIn("Kannada", scripts)
        self.assertIn("Malayalam", scripts)
        self.assertIn("Bengali", scripts)
        self.assertIn("Gujarati", scripts)

    def test_04_provenance_audit_rows_and_code_free(self):
        p = PATCH_ROOT / "CANDIDATE_A_PROVENANCE_AUDIT.csv"
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 399)
        
        # Verify language classification
        for r in rows:
            self.assertIn(r["language_classification"], ["TAMIL", "ENGLISH", "TANGLISH"])
            self.assertEqual(r["is_code_free"], "YES")
            self.assertEqual(r["is_intended_synthetic_text"], "YES")

    def test_05_split_manifest_distribution(self):
        p = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 399)
        
        from collections import Counter
        counts = Counter(r["split"] for r in rows)
        self.assertEqual(counts["TRAIN"], 320)
        self.assertEqual(counts["VALIDATION"], 40)
        self.assertEqual(counts["TEST"], 39)

    def test_06_cryptographic_hash_invariants(self):
        h_a = hashlib.sha256((PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json").read_bytes()).hexdigest()
        h_b = hashlib.sha256((PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model").read_bytes()).hexdigest()
        h_exp = hashlib.sha256((PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json").read_bytes()).hexdigest()
        
        self.assertEqual(h_a, EXPECTED_CAND_A_HASH)
        self.assertEqual(h_b, EXPECTED_CAND_B_HASH)
        self.assertEqual(h_exp, EXPECTED_EXP_HASH)

    def test_07_regression_phase26(self):
        res = subprocess.run([sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase26_benchmark.py"), "-q"],
                             cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 26 regression failed: {res.stdout}\n{res.stderr}")

    def test_08_regression_phase31a(self):
        res = subprocess.run([sys.executable, str(PATCH_ROOT / "verify_phase31a.py")],
                             cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 31A verification failed: {res.stdout}\n{res.stderr}")

    def test_09_zero_production_data(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = list(target_dir.glob("**/*"))
                files = [f for f in files if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
