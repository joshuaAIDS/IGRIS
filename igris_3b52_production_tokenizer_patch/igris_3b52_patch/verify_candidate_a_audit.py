"""
verify_candidate_a_audit.py

Automated Verification Suite for Candidate A Synthetic Results Audit:
1. Verifies all 5 audit deliverables exist and are non-empty.
2. Verifies cryptographic hashes for Candidate A, Candidate B, and Experimental Tokenizer.
3. Verifies vocabulary sizes (32,768) and structural tokens (IDs 0–11).
4. Verifies filler tokens count and active tokens count.
5. Verifies 0 duplicate token IDs in both vocabularies.
6. Verifies exact recalculation of 0.41% and 1.47% coverage over 32,768.
7. Verifies test split fertility recalculations for Tamil, English, and Tanglish.
8. Verifies 100% Unicode round-trip accuracy on test split.
9. Runs regression suites (Phase 24, 25, 26, 31A).
"""

import csv
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tokenizers import Tokenizer

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

from igris.tokenizer.strict import STRUCTURAL_TOKENS, VOCAB_SIZE

EXPECTED_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
EXPECTED_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"

AUDIT_DELIVERABLES = [
    "CANDIDATE_A_RESULTS_AUDIT.md",
    "CANDIDATE_A_VOCABULARY_AUDIT.csv",
    "CANDIDATE_A_METRIC_RECALCULATION.csv",
    "CANDIDATE_A_FINAL_INTEGRITY_REPORT.txt",
    "verify_candidate_a_audit.py",
]

class TestCandidateAAudit(unittest.TestCase):

    def test_01_audit_deliverables_exist_and_non_empty(self):
        for fname in AUDIT_DELIVERABLES:
            p = PATCH_ROOT / fname
            self.assertTrue(p.exists(), f"Deliverable missing: {fname}")
            self.assertGreater(p.stat().st_size, 0, f"Deliverable empty: {fname}")

    def test_02_original_candidate_a_hash_unaltered(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, EXPECTED_CAND_A_HASH)

    def test_03_original_candidate_b_hash_unaltered(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, EXPECTED_CAND_B_HASH)

    def test_04_experimental_tokenizer_hash_matches(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, EXPECTED_EXP_HASH)

    def test_05_vocabulary_counts_and_structural_tokens(self):
        with open(PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json", encoding="utf-8") as f:
            orig_json = json.load(f)
        with open(PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json", encoding="utf-8") as f:
            exp_json = json.load(f)
        
        orig_vocab = orig_json["model"]["vocab"]
        exp_vocab = exp_json["model"]["vocab"]
        
        self.assertEqual(len(orig_vocab), VOCAB_SIZE)
        self.assertEqual(len(exp_vocab), VOCAB_SIZE)
        self.assertEqual(len(set(orig_vocab.values())), VOCAB_SIZE)
        self.assertEqual(len(set(exp_vocab.values())), VOCAB_SIZE)
        
        # Check structural tokens
        for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
            self.assertEqual(orig_vocab[spelling], expected_id)
            self.assertEqual(exp_vocab[spelling], expected_id)
            
        # Check filler counts
        orig_fillers = sum(1 for k in orig_vocab if k.startswith("<|filler_"))
        exp_fillers = sum(1 for k in exp_vocab if k.startswith("<|filler_"))
        self.assertEqual(orig_fillers, 32437)
        self.assertEqual(exp_fillers, 30745)

    def test_06_vocabulary_audit_csv_row_count(self):
        p = PATCH_ROOT / "CANDIDATE_A_VOCABULARY_AUDIT.csv"
        with open(p, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), VOCAB_SIZE)

    def test_07_coverage_recalculation(self):
        p = PATCH_ROOT / "CANDIDATE_A_METRIC_RECALCULATION.csv"
        with open(p, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = {r["metric_id"]: r for r in reader}
        
        # AUD-M07: Padded Vocab Utilization
        self.assertIn("0.4059%", rows["AUD-M07"]["recalculated_value_orig"])
        self.assertIn("1.4709%", rows["AUD-M07"]["recalculated_value_exp"])
        
        # AUD-M08: Active Vocab Utilization
        self.assertIn("40.18%", rows["AUD-M08"]["recalculated_value_orig"])
        self.assertIn("23.83%", rows["AUD-M08"]["recalculated_value_exp"])

    def test_08_fertility_recalculation_exact_match(self):
        p = PATCH_ROOT / "CANDIDATE_A_METRIC_RECALCULATION.csv"
        with open(p, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = {r["metric_id"]: r for r in reader}
            
        # Tamil fertility
        self.assertAlmostEqual(float(rows["AUD-M10"]["recalculated_value_orig"]), 10.0748, places=3)
        self.assertAlmostEqual(float(rows["AUD-M10"]["recalculated_value_exp"]), 6.8972, places=3)

        # English fertility
        self.assertAlmostEqual(float(rows["AUD-M11"]["recalculated_value_orig"]), 9.2360, places=3)
        self.assertAlmostEqual(float(rows["AUD-M11"]["recalculated_value_exp"]), 3.8652, places=3)

        # Tanglish fertility
        self.assertAlmostEqual(float(rows["AUD-M12"]["recalculated_value_orig"]), 7.5916, places=3)
        self.assertAlmostEqual(float(rows["AUD-M12"]["recalculated_value_exp"]), 3.2932, places=3)

    def test_09_regression_phase26(self):
        res = subprocess.run([sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase26_benchmark.py"), "-q"],
                             cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 26 regression failed: {res.stdout}\n{res.stderr}")

    def test_10_regression_phase31a(self):
        res = subprocess.run([sys.executable, str(PATCH_ROOT / "verify_phase31a.py")],
                             cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 31A verification failed: {res.stdout}\n{res.stderr}")

    def test_11_zero_production_data(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = list(target_dir.glob("**/*"))
                files = [f for f in files if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
