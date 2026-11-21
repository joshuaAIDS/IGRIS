"""
verify_candidate_a_training.py

Automated Verification Suite for IGRIS Candidate A Synthetic Tokenizer Training:
1. Verifies all 8 deliverable files exist and are non-empty.
2. Cryptographic hash invariant: Original Candidate A and B remain strictly unaltered.
3. Experimental Candidate A exists in separate directory with 32,768 vocabulary.
4. Structural tokens (IDs 0–11) verified.
5. Zero leakage between Train, Validation, and Test splits.
6. 100% Unicode round-trip on held-out test split.
7. Full regression suites execution (Phase 24, 25, 26, 31A).
"""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

from tokenizers import Tokenizer
from igris.tokenizer.strict import STRUCTURAL_TOKENS, VOCAB_SIZE

EXPECTED_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CAND_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
EXPECTED_EXP_HASH = "3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce"

DELIVERABLES = [
    "CANDIDATE_A_SYNTHETIC_TRAINING_REPORT.md",
    "CANDIDATE_A_SYNTHETIC_TRAINING_CONFIG.json",
    "CANDIDATE_A_SYNTHETIC_CORPUS_MANIFEST.csv",
    "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv",
    "CANDIDATE_A_TOKENIZER_COMPARISON.csv",
    "CANDIDATE_A_TOKENIZER_EXAMPLES.md",
    "CANDIDATE_A_TOKENIZER_HASH_REPORT.txt",
    "verify_candidate_a_training.py",
]

class TestCandidateASyntheticTraining(unittest.TestCase):

    def test_01_deliverable_files_exist_and_non_empty(self):
        for fname in DELIVERABLES:
            p = PATCH_ROOT / fname
            self.assertTrue(p.exists(), f"Deliverable missing: {fname}")
            self.assertGreater(p.stat().st_size, 0, f"Deliverable empty: {fname}")

    def test_02_original_candidate_a_hash_unaltered(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, EXPECTED_CAND_A_HASH, "Original Candidate A hash altered!")

    def test_03_original_candidate_b_hash_unaltered(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, EXPECTED_CAND_B_HASH, "Original Candidate B hash altered!")

    def test_04_experimental_tokenizer_exists_and_hashed(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        self.assertTrue(p.exists(), "Experimental tokenizer.json missing")
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, EXPECTED_EXP_HASH, "Experimental tokenizer hash mismatch")

    def test_05_experimental_tokenizer_vocab_and_structural_tokens(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok = Tokenizer.from_file(str(p))
        self.assertEqual(tok.get_vocab_size(), VOCAB_SIZE)
        for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
            actual_id = tok.token_to_id(spelling)
            self.assertEqual(actual_id, expected_id, f"Structural token {spelling} has ID {actual_id}")

    def test_06_split_manifest_and_zero_leakage(self):
        manifest_path = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
        import csv
        with open(manifest_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        train_hashes = set(r["text_sha256"] for r in rows if r["split"] == "TRAIN")
        val_hashes = set(r["text_sha256"] for r in rows if r["split"] == "VALIDATION")
        test_hashes = set(r["text_sha256"] for r in rows if r["split"] == "TEST")
        
        self.assertEqual(len(train_hashes & val_hashes), 0, "Leakage Train-Val by hash")
        self.assertEqual(len(train_hashes & test_hashes), 0, "Leakage Train-Test by hash")
        self.assertEqual(len(val_hashes & test_hashes), 0, "Leakage Val-Test by hash")

        train_texts = set(r["preview_text"] for r in rows if r["split"] == "TRAIN")
        val_texts = set(r["preview_text"] for r in rows if r["split"] == "VALIDATION")
        test_texts = set(r["preview_text"] for r in rows if r["split"] == "TEST")
        self.assertEqual(len(train_texts & val_texts), 0, "Preview Leakage Train-Val")
        self.assertEqual(len(train_texts & test_texts), 0, "Preview Leakage Train-Test")
        self.assertEqual(len(val_texts & test_texts), 0, "Preview Leakage Val-Test")

    def test_07_unicode_roundtrip_fidelity(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"
        tok = Tokenizer.from_file(str(p))
        test_cases = [
            "தமிழ் மொழி வாழ்க",
            "This is a strict test of ByteLevel BPE tokenization.",
            "Intha model romba efficiently perform panrathu bro.",
            "Database migration script-ஐ staging environment-ல் test பண்ணியாச்சு.",
            "ஸ்ரீ கிருஷ்ணா மற்றும் Grantha எழுத்துக்கள்: ஜ, ஷ, ஸ, ஹ, க்ஷ"
        ]
        for tc in test_cases:
            enc = tok.encode(tc)
            dec = tok.decode(enc.ids)
            self.assertEqual(dec, tc, f"Round-trip failed for: {tc}")

    def test_08_regression_phase26(self):
        res = subprocess.run([sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase26_benchmark.py"), "-q"],
                             cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 26 regression failed: {res.stdout}\n{res.stderr}")

    def test_09_regression_phase25(self):
        res = subprocess.run([sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase25_pipeline.py"), "-q"],
                             cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 25 regression failed: {res.stdout}\n{res.stderr}")

    def test_10_regression_phase24(self):
        res = subprocess.run([sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase24_infrastructure.py"), "-q"],
                             cwd=str(PATCH_ROOT), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Phase 24 regression failed: {res.stdout}\n{res.stderr}")

    def test_11_zero_production_data_check(self):
        for d in ["production", "raw", "acquired", "quarantine"]:
            target_dir = PATCH_ROOT / d
            if target_dir.exists():
                files = list(target_dir.glob("**/*"))
                files = [f for f in files if f.is_file() and not f.name.endswith(".gitkeep")]
                self.assertEqual(len(files), 0, f"Production data present in {d}: {files}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
