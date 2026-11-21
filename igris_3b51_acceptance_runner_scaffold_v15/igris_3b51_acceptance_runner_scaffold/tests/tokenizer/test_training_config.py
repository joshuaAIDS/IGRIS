"""3B.51.14 training configuration validation tests (no training performed)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from dataclasses import replace

from .training_config import (
    CANDIDATE_A_CONFIG, CANDIDATE_B_CONFIG,
    validate_training_config, validate_fair_comparison, corpus_fingerprints,
)


class TrainingConfigTests(unittest.TestCase):
    def test_01_candidate_a_baseline_valid(self):
        self.assertEqual(validate_training_config(CANDIDATE_A_CONFIG, "A"), [])

    def test_02_candidate_b_baseline_valid(self):
        self.assertEqual(validate_training_config(CANDIDATE_B_CONFIG, "B"), [])

    def test_03_reject_wrong_candidate(self):
        self.assertTrue(validate_training_config(CANDIDATE_A_CONFIG, "X"))

    def test_04_reject_wrong_vocab_size(self):
        self.assertTrue(validate_training_config(replace(CANDIDATE_A_CONFIG, vocab_size=32000), "A"))

    def test_05_reject_bool_vocab_size(self):
        self.assertTrue(validate_training_config(replace(CANDIDATE_B_CONFIG, vocab_size=True), "B"))

    def test_06_reject_reordered_structural_tokens(self):
        changed = replace(CANDIDATE_A_CONFIG, structural_tokens=tuple(reversed(CANDIDATE_A_CONFIG.structural_tokens)))
        self.assertTrue(validate_training_config(changed, "A"))

    def test_07_reject_candidate_b_without_byte_fallback(self):
        self.assertTrue(validate_training_config(replace(CANDIDATE_B_CONFIG, byte_fallback=False), "B"))

    def test_08_reject_candidate_a_backend_filename_mismatch(self):
        self.assertTrue(validate_training_config(replace(CANDIDATE_A_CONFIG, backend_filename="tokenizer.model"), "A"))

    def test_09_reject_normalization_mismatch(self):
        self.assertTrue(validate_training_config(replace(CANDIDATE_B_CONFIG, normalization="NFKC"), "B"))

    def test_10_reject_determinism_setting_drift(self):
        self.assertTrue(validate_training_config(replace(CANDIDATE_B_CONFIG, deterministic_settings=()), "B"))

    def test_11_same_ordered_corpus_is_fair(self):
        with tempfile.TemporaryDirectory() as td:
            p1 = Path(td) / "one.txt"
            p2 = Path(td) / "two.txt"
            p1.write_text("தமிழ்\nEnglish\n", encoding="utf-8")
            p2.write_text("Tanglish sample\n", encoding="utf-8")
            self.assertEqual(validate_fair_comparison([p1, p2], [p1, p2])[0], True)

    def test_12_different_content_is_not_fair(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.txt"; b = Path(td) / "b.txt"
            a.write_text("same input\n", encoding="utf-8")
            b.write_text("different input\n", encoding="utf-8")
            self.assertFalse(validate_fair_comparison([a], [b])[0])

    def test_13_different_file_order_is_not_fair(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.txt"; b = Path(td) / "b.txt"
            a.write_text("A\n", encoding="utf-8"); b.write_text("B\n", encoding="utf-8")
            self.assertFalse(validate_fair_comparison([a, b], [b, a])[0])

    def test_14_reject_duplicate_paths(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.txt"; p.write_text("data\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                corpus_fingerprints([p, p])

    def test_15_reject_empty_corpus_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "empty.txt"; p.write_bytes(b"")
            with self.assertRaises(ValueError):
                corpus_fingerprints([p])

    def test_16_fingerprint_records_sha256_and_size(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.txt"; p.write_bytes(b"abc")
            record = corpus_fingerprints([p])[0]
            self.assertEqual(record[1], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
            self.assertEqual(record[2], 3)


if __name__ == "__main__":
    unittest.main()
