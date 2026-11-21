"""Backend-independent tests for the local corpus preparation pipeline."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from .corpus_preparation import prepare_corpus
from .acceptance_config import STRUCTURAL_TOKENS
from .unicode_security import SENTINEL


class CorpusPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name: str, data: bytes) -> Path:
        path = self.root / name
        path.write_bytes(data)
        return path

    def test_exact_mode_preserves_decomposed_codepoints(self):
        source = self.write("in.txt", "e\u0301\nதமிழ்\n".encode("utf-8"))
        corpus, report, data = prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")
        text = corpus.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("e\u0301\n"))
        self.assertEqual(data["input_record_count"], 2)
        self.assertTrue(report.is_file())

    def test_structural_spellings_are_escaped_as_literal_text(self):
        source = self.write("in.txt", (STRUCTURAL_TOKENS[0] + " literal\n").encode())
        corpus, _, _ = prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")
        prepared = corpus.read_text(encoding="utf-8")
        self.assertNotIn(STRUCTURAL_TOKENS[0], prepared)
        self.assertIn(SENTINEL + "S00;", prepared)

    def test_duplicates_reported_but_preserved_by_default(self):
        source = self.write("in.txt", b"same\nsame\nother\n")
        corpus, _, data = prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")
        self.assertEqual(corpus.read_text(encoding="utf-8"), "same\nsame\nother\n")
        self.assertEqual(data["duplicate_record_count"], 1)
        self.assertEqual(data["records_removed_as_duplicates"], 0)

    def test_explicit_deduplication_preserves_first_occurrence(self):
        source = self.write("in.txt", b"same\nsame\nother\n")
        corpus, _, data = prepare_corpus([source], self.root / "out", mode="exact_unicode_mode", deduplicate=True)
        self.assertEqual(corpus.read_text(encoding="utf-8"), "same\nother\n")
        self.assertEqual(data["records_removed_as_duplicates"], 1)

    def test_blank_records_and_whitespace_preserved(self):
        source = self.write("in.txt", b"\n  keep spaces  \n")
        corpus, _, data = prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")
        self.assertEqual(corpus.read_text(encoding="utf-8"), "\n  keep spaces  \n")
        self.assertEqual(data["blank_record_count"], 1)

    def test_invalid_utf8_rejected(self):
        source = self.write("in.txt", b"valid\n\xff\n")
        with self.assertRaises(UnicodeDecodeError):
            prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")
        self.assertFalse((self.root / "out").exists())

    def test_nul_rejected(self):
        source = self.write("in.txt", b"abc\x00def\n")
        with self.assertRaises(ValueError):
            prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")

    def test_existing_output_not_overwritten(self):
        source = self.write("in.txt", b"hello\n")
        output = self.root / "out"
        output.mkdir()
        marker = output / "keep.txt"
        marker.write_text("untouched")
        with self.assertRaises(FileExistsError):
            prepare_corpus([source], output, mode="exact_unicode_mode")
        self.assertEqual(marker.read_text(), "untouched")

    def test_source_file_is_unchanged_and_report_hashes(self):
        source = self.write("in.txt", b"alpha\n")
        original = source.read_bytes()
        _, report_path, data = prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(report["output_sha256"], data["output_sha256"])

    def test_empty_input_file_rejected(self):
        source = self.write("empty.txt", b"")
        with self.assertRaises(ValueError):
            prepare_corpus([source], self.root / "out", mode="exact_unicode_mode")

    def test_invalid_mode_rejected(self):
        source = self.write("in.txt", b"hello\n")
        with self.assertRaises(ValueError):
            prepare_corpus([source], self.root / "out", mode="wrong")


if __name__ == "__main__":
    unittest.main()
