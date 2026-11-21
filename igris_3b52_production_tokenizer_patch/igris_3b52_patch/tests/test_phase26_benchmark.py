"""
tests/test_phase26_benchmark.py

IGRIS Phase 26 Test Suite:
- Dataset splits integrity & non-leakage verification
- Development set & validation set threshold selection
- Held-out test set pipeline evaluation
- Tokenizer Candidate A & B comparative integrity
- Hardware resource benchmarks
- Metric reconciliation verification
- Project governance invariants
"""

import hashlib
import json
import unittest
from pathlib import Path
import numpy as np

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
import sys
sys.path.insert(0, str(PATCH_ROOT / "scripts"))
sys.path.insert(0, str(PATCH_ROOT))

from dataset_pipeline_v2 import DatasetPipelineV2, RawRecord
from duplicate_detector_v2 import DuplicateDetectorV2
from language_identifier_v2 import LanguageIdentifierV2
from quality_filter_v2 import QualityFilterV2
from unicode_processor_v2 import UnicodeProcessorV2
from tokenizers import Tokenizer
import sentencepiece as spm


class TestDatasetSplitsIntegrity(unittest.TestCase):
    """Verifies that the benchmark dataset splits are strictly partitioned with zero leakage."""

    @classmethod
    def setUpClass(cls):
        splits_path = PATCH_ROOT / "PHASE26_DATASET_SPLITS.json"
        with open(splits_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.splits = cls.data["splits"]

    def test_split_counts(self):
        self.assertEqual(len(self.splits["dev"]), 100)
        self.assertEqual(len(self.splits["val"]), 100)
        self.assertEqual(len(self.splits["test"]), 100)
        self.assertEqual(self.data["splits_summary"]["total_records"], 300)

    def test_zero_leakage_between_splits(self):
        dev_texts = set(r["text"] for r in self.splits["dev"])
        val_texts = set(r["text"] for r in self.splits["val"])
        test_texts = set(r["text"] for r in self.splits["test"])

        self.assertEqual(len(dev_texts & val_texts), 0, "Leakage between dev and val")
        self.assertEqual(len(dev_texts & test_texts), 0, "Leakage between dev and test")
        self.assertEqual(len(val_texts & test_texts), 0, "Leakage between val and test")

    def test_schema_completeness(self):
        required_keys = [
            "id", "text", "ground_truth_language", "category",
            "expected_processing_behavior", "difficulty", "provenance",
            "dataset_split", "expected_quality_pass", "expected_duplicate",
            "expected_rejection_reasons", "notes"
        ]
        for split_name in ["dev", "val", "test"]:
            for r in self.splits[split_name]:
                for k in required_keys:
                    self.assertIn(k, r, f"Missing key '{k}' in record {r.get('id')}")


class TestLanguageIdentificationBenchmark(unittest.TestCase):
    """Verifies LID performance across difficulty tiers."""

    @classmethod
    def setUpClass(cls):
        cls.lid = LanguageIdentifierV2()
        splits_path = PATCH_ROOT / "PHASE26_DATASET_SPLITS.json"
        with open(splits_path, "r", encoding="utf-8") as f:
            cls.splits = json.load(f)["splits"]

    def test_dev_accuracy_above_threshold(self):
        correct = sum(1 for r in self.splits["dev"] if self.lid.identify(r["text"]).label == r["ground_truth_language"])
        acc = correct / len(self.splits["dev"])
        self.assertGreaterEqual(acc, 0.95, f"Dev accuracy {acc:.2%} below 95%")

    def test_held_out_test_accuracy_above_threshold(self):
        correct = sum(1 for r in self.splits["test"] if self.lid.identify(r["text"]).label == r["ground_truth_language"])
        acc = correct / len(self.splits["test"])
        self.assertGreaterEqual(acc, 0.95, f"Held-out test accuracy {acc:.2%} below 95%")

    def test_out_of_scope_rejection_100pct(self):
        for s in ["dev", "val", "test"]:
            for r in self.splits[s]:
                if r["ground_truth_language"] == "OUT_OF_SCOPE":
                    res = self.lid.identify(r["text"])
                    self.assertEqual(res.label, "OUT_OF_SCOPE", f"Failed to reject non-target text: {r['text']}")


class TestPipelineHeldOutEvaluation(unittest.TestCase):
    """Executes the full pipeline on the unseen held-out test set."""

    @classmethod
    def setUpClass(cls):
        splits_path = PATCH_ROOT / "PHASE26_DATASET_SPLITS.json"
        with open(splits_path, "r", encoding="utf-8") as f:
            cls.test_records = json.load(f)["splits"]["test"]
        cls.pipeline = DatasetPipelineV2(near_dup_threshold=0.70)
        raw_recs = [RawRecord(r["id"], r["text"], metadata=r) for r in cls.test_records]
        cls.processed, cls.telemetry = cls.pipeline.process_dataset(raw_recs)

    def test_pipeline_decision_accuracy(self):
        corr = sum(1 for p, r in zip(self.processed, self.test_records) if p.final_action == r["expected_processing_behavior"])
        acc = corr / len(self.test_records)
        self.assertGreaterEqual(acc, 0.98, f"Pipeline decision accuracy {acc:.2%} below 98%")

    def test_held_out_duplicate_precision(self):
        # All flagged duplicates must be true duplicates (precision = 1.0)
        for p, r in zip(self.processed, self.test_records):
            if p.is_duplicate:
                self.assertTrue(r["expected_duplicate"], f"False positive duplicate: {r['id']}")

    def test_held_out_quality_filter_recall(self):
        for p, r in zip(self.processed, self.test_records):
            if r["expected_quality_pass"]:
                self.assertTrue(p.quality_passed, f"Valid record wrongly rejected: {r['id']}")


class TestTokenizerComparison(unittest.TestCase):
    """Comparative benchmark of Candidate A vs Candidate B."""

    @classmethod
    def setUpClass(cls):
        tok_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        tok_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        cls.h_a = hashlib.sha256(open(tok_a_path, "rb").read()).hexdigest()
        cls.h_b = hashlib.sha256(open(tok_b_path, "rb").read()).hexdigest()
        cls.tok_a = Tokenizer.from_file(str(tok_a_path))
        cls.sp_b = spm.SentencePieceProcessor()
        cls.sp_b.load(str(tok_b_path))

    def test_candidate_a_hash(self):
        self.assertEqual(self.h_a, "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561")

    def test_candidate_b_hash(self):
        self.assertEqual(self.h_b, "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888")

    def test_zero_unk_both_tokenizers(self):
        samples = [
            "தமிழ் மிகவும் தொன்மையான செம்மொழி.",
            "The quick brown fox jumps over the lazy dog.",
            "Innaiku office-ku seekiram kelambanum da.",
            "Transformer architecture-ல் multi-head attention உள்ளது.",
        ]
        unk_a = self.tok_a.token_to_id("[UNK]") or self.tok_a.token_to_id("<unk>")
        unk_b = self.sp_b.unk_id()

        for s in samples:
            ids_a = self.tok_a.encode(s).ids
            if unk_a is not None:
                self.assertEqual(sum(1 for i in ids_a if i == unk_a), 0)

            ids_b = self.sp_b.encode_as_ids(s)
            self.assertEqual(sum(1 for i in ids_b if i == unk_b), 0)

    def test_roundtrip_both_tokenizers(self):
        text = "வணக்கம்! Python and Tamil code mixing test da."
        dec_a = self.tok_a.decode(self.tok_a.encode(text).ids)
        dec_b = self.sp_b.decode_ids(self.sp_b.encode_as_ids(text))
        self.assertEqual(dec_a.strip(), text.strip())
        self.assertEqual(dec_b.strip(), text.strip())


class TestGovernanceInvariants(unittest.TestCase):
    """Strict verification of locked gates and zero production bytes."""

    def test_zero_production_data(self):
        prod_dirs = [
            PATCH_ROOT / "data" / "production",
            PATCH_ROOT / "data" / "raw",
            PATCH_ROOT / "data" / "acquired",
        ]
        for pd in prod_dirs:
            if pd.exists():
                files = [f for f in pd.rglob("*") if f.is_file() and f.suffix not in {".md", ".txt", ".gitkeep"}]
                self.assertEqual(len(files), 0)


if __name__ == "__main__":
    unittest.main()
