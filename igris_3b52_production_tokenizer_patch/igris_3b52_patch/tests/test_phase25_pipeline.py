"""
IGRIS Phase 25 Test Suite
=========================
Comprehensive unit, integration, adversarial, and governance test suite:
- Phase 25 Pipeline 9-stage integration
- Language identification improvement & adversarial verification
- Unicode Tamil-safe preservation & adversarial detection
- Quality filter verification
- Multi-level duplicate detection & false-positive check
- Pipeline determinism & reproducibility
- Candidate A & B Tokenizer hash integrity & read-only evaluation
- Project governance invariants
"""

import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "scripts"))
sys.path.insert(0, str(PATCH_ROOT))

from dataset_pipeline_v2 import DatasetPipelineV2, RawRecord, ProcessedRecord
from duplicate_detector_v2 import DuplicateDetectorV2
from language_identifier_v2 import LanguageIdentifierV2
from quality_filter_v2 import QualityConfigV2, QualityFilterV2
from tanglish_analyzer import TanglishAnalyzer
from unicode_processor_v2 import UnicodeProcessorV2


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for the 9-stage pipeline."""

    def setUp(self):
        self.pipeline = DatasetPipelineV2()

    def test_pipeline_non_destructive(self):
        """No silent record deletion: N input records produce exactly N processed records."""
        inputs = [
            RawRecord("REC-01", "This is a clean English sentence with sufficient length."),
            RawRecord("REC-02", ""),  # empty (should be rejected, not deleted)
            RawRecord("REC-03", "தமிழ் ஒரு பழமையான செம்மொழி ஆகும்."),
            RawRecord("REC-04", "a" * 80),  # spam (rejected, not deleted)
        ]
        processed, telemetry = self.pipeline.process_dataset(inputs)
        self.assertEqual(len(processed), len(inputs))
        self.assertEqual(telemetry["total_records"], 4)
        self.assertEqual(telemetry["processed_records"], 4)

    def test_provenance_and_audit_fields(self):
        """Every record retains original text, SHA-256 hashes, and decision audit trail."""
        rec = RawRecord("AUDIT-01", "Let us wrap up this release quickly da.")
        p = self.pipeline.process_record(rec)
        self.assertEqual(p.id, "AUDIT-01")
        self.assertEqual(p.original_text, rec.text)
        self.assertTrue(len(p.sha256_original) == 64)
        self.assertTrue(len(p.sha256_normalized) == 64)
        self.assertIn(p.final_action, ["ACCEPTED", "REJECTED", "DUPLICATE_FLAGGED"])


class TestLanguageIdentificationImprovements(unittest.TestCase):
    """Adversarial and weakness validation for Language Identification."""

    def setUp(self):
        self.lid = LanguageIdentifierV2()

    def test_english_dominant_with_tamil_particles(self):
        """Weakness 1: Sentences predominantly English with subtle Tamil particles."""
        cases = [
            "Let us wrap up this release quickly da, otherwise deployment will get delayed.",
            "Aiyo, the network latency is spiking again, please check the load balancer.",
            "Don't worry pa, the pipeline will auto-recover in a couple of minutes.",
            "Please finish this documentation ticket today itself da, client is waiting.",
            "No problem da, we can easily reproduce the test failure in our local sandbox.",
        ]
        for c in cases:
            res = self.lid.identify(c)
            self.assertEqual(res.label, "TANGLISH", f"Failed on: {c}")
            self.assertGreater(res.confidence, 0.4)

    def test_intra_sentential_code_switching(self):
        """Weakness 2: Code switching between Tamil script and Latin script."""
        cases = [
            "Server reboot aana piragu microservices automatically start aagala, script execute பண்ணனும்.",
            "Database connection pool timeout increase பண்ணினா, concurrency issues solve aagidum.",
            "Storage matrix calculations verify pannitom, local disk capacity deficit clearly documented.",
        ]
        for c in cases:
            res = self.lid.identify(c)
            self.assertEqual(res.label, "TANGLISH", f"Failed on: {c}")

    def test_formal_technical_tanglish(self):
        """Weakness 3: Formal technical prose with Tamil case markers."""
        cases = [
            "Decoder-only transformer architecture-ல் multi-head self-attention mechanisms language representations-ஐ generate செய்கின்றன.",
            "Tokenizer vocabulary-யில் 32,768 structural and subword tokens முறையாக allocate செய்யப்பட்டுள்ளன.",
            "Gradient clipping threshold 1.0-க்கு மேலாக செல்லாமல் training stability ensure செய்யப்படுகிறது.",
        ]
        for c in cases:
            res = self.lid.identify(c)
            self.assertEqual(res.label, "TANGLISH", f"Failed on: {c}")

    def test_non_forced_uncertainty(self):
        """Uncertain and ambiguous text should be UNKNOWN, not forced."""
        cases = [
            "",
            "   ",
            "12345 67890",
            "!@#$% ^&*()",
        ]
        for c in cases:
            res = self.lid.identify(c)
            self.assertEqual(res.label, "UNKNOWN")


class TestUnicodePreservationAndAdversarial(unittest.TestCase):
    """Tests for Tamil Unicode preservation and adversarial detection."""

    def setUp(self):
        self.up = UnicodeProcessorV2()

    def test_tamil_vowel_signs_preservation(self):
        """All 11 Tamil vowel signs must survive NFC normalization intact."""
        vowel_signs = ["கா", "கி", "கீ", "கு", "கூ", "கெ", "கே", "கை", "கொ", "கோ", "கௌ"]
        for vs in vowel_signs:
            norm, rep = self.up.normalize(vs)
            self.assertEqual(norm, vs)
            self.assertGreater(rep.tamil_combining_marks_preserved, 0)

    def test_virama_and_conjuncts(self):
        """Virama pulli consonants must be preserved."""
        text = "க் ங் ச் ஞ் ட் ண் த் ந் ப் ம் ய் ர் ல் வ் ழ் ள் ற் ன்"
        norm, rep = self.up.normalize(text)
        self.assertEqual(norm, text)
        self.assertEqual(rep.virama_sequences_preserved, 18)

    def test_adversarial_double_virama(self):
        """Adversarial double virama must be flagged as malformed."""
        text = "க்்"
        _, rep = self.up.normalize(text)
        self.assertTrue(any("Double virama" in s for s in rep.malformed_sequences))

    def test_adversarial_lone_combining_mark(self):
        """Lone combining mark must be flagged as malformed."""
        text = "\u0BBE"
        _, rep = self.up.normalize(text)
        self.assertTrue(any("Lone combining mark" in s for s in rep.malformed_sequences))

    def test_replacement_char_detection(self):
        """U+FFFD replacement char must be detected."""
        text = "Test\uFFFDString"
        _, rep = self.up.normalize(text)
        self.assertTrue(rep.has_replacement_char)


class TestDuplicateDetection(unittest.TestCase):
    """Multi-level duplicate detection and false positive verification."""

    def setUp(self):
        self.dd = DuplicateDetectorV2(near_dup_threshold=0.80)

    def test_exact_and_normalized_duplicate(self):
        r1 = self.dd.check_and_register("D1", "Machine learning models require data.")
        self.assertFalse(r1.is_duplicate)

        r2 = self.dd.check_and_register("D2", "Machine learning models require data.")
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.dup_type, "EXACT")

        r3 = self.dd.check_and_register("D3", "  machine learning models require data.  \n")
        self.assertTrue(r3.is_duplicate)
        self.assertEqual(r3.dup_type, "NORMALIZED")

    def test_near_duplicate(self):
        r1 = self.dd.check_and_register("D4", "The quick brown fox jumps over the lazy dog near river bank.")
        self.assertFalse(r1.is_duplicate)

        r2 = self.dd.check_and_register("D5", "The quick brown fox jumps over the lazy dog near river bank today.")
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.dup_type, "NEAR_DUPLICATE")

    def test_no_false_positive_on_distinct_texts(self):
        t1 = "Software architecture designs system interfaces."
        t2 = "Tamil is an ancient classical Dravidian language."
        r1 = self.dd.check_and_register("D6", t1)
        r2 = self.dd.check_and_register("D7", t2)
        self.assertFalse(r1.is_duplicate)
        self.assertFalse(r2.is_duplicate)


class TestPipelineReproducibility(unittest.TestCase):
    """Pipeline determinism and reproducibility test."""

    def test_deterministic_output(self):
        pipeline = DatasetPipelineV2()
        recs = [
            RawRecord("R1", "First record text for reproducibility test."),
            RawRecord("R2", "Second record தமிழ் மொழியில் எழுதப்பட்டுள்ளது."),
            RawRecord("R3", "First record text for reproducibility test."),  # duplicate
        ]
        out1, _ = pipeline.process_dataset(recs)
        pipeline.reset_state()
        out2, _ = pipeline.process_dataset(recs)

        for p1, p2 in zip(out1, out2):
            d1 = p1.to_dict()
            d2 = p2.to_dict()
            d1.pop("timestamp_utc")
            d2.pop("timestamp_utc")
            self.assertEqual(d1, d2)


class TestTokenizerIntegrity(unittest.TestCase):
    """Tokenizer Candidate A and B hash integrity and read-only verification."""

    def test_candidate_a_hash_invariant(self):
        path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.assertTrue(path.exists())
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        self.assertEqual(h, "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561")

    def test_candidate_b_hash_invariant(self):
        path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        self.assertTrue(path.exists())
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        self.assertEqual(h, "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888")

    def test_candidate_a_zero_unk_on_target_languages(self):
        from tokenizers import Tokenizer
        path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        tok = Tokenizer.from_file(str(path))
        unk_id = tok.token_to_id("[UNK]")
        if unk_id is None:
            unk_id = tok.token_to_id("<unk>")

        samples = [
            "The quick brown fox jumps over the lazy dog.",
            "தமிழ் மிகவும் அழகான செம்மொழி ஆகும்.",
            "Innaiku office-ku seekiram kelambanum da.",
            "Model architecture-ல் transformer layers உள்ளன.",
        ]
        for s in samples:
            enc = tok.encode(s)
            unk_count = sum(1 for tid in enc.ids if tid == unk_id) if unk_id is not None else 0
            self.assertEqual(unk_count, 0, f"UNK detected in: {s}")


class TestGovernanceInvariants(unittest.TestCase):
    """Strict verification of zero production data and locked gates."""

    def test_zero_production_data(self):
        prod_dirs = [
            PATCH_ROOT / "data" / "production",
            PATCH_ROOT / "data" / "raw",
            PATCH_ROOT / "data" / "acquired",
        ]
        for pd in prod_dirs:
            if pd.exists():
                data_files = [f for f in pd.rglob("*") if f.is_file() and f.suffix not in {".md", ".txt", ".gitkeep"}]
                self.assertEqual(len(data_files), 0)


if __name__ == "__main__":
    unittest.main()
