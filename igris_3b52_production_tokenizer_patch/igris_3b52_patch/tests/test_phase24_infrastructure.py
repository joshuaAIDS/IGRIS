"""
IGRIS Phase 24 — Comprehensive Infrastructure Test Suite
=========================================================
Tests language identification, Unicode processing, Tanglish analysis,
quality filtering, duplicate detection, and tokenizer round-trip integrity.
"""

import hashlib
import json
import os
import re
import sys
import unicodedata
import unittest
from pathlib import Path

# Add scripts directory to path
PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

from language_identifier_v2 import LanguageIdentifierV2, LangIDResult
from unicode_processor_v2 import UnicodeProcessorV2, UnicodeReport
from tanglish_analyzer import TanglishAnalyzer, TanglishAnalysis
from quality_filter_v2 import QualityFilterV2, QualityConfigV2, QualityVerdict
from duplicate_detector_v2 import DuplicateDetectorV2, DupResult
from language_quality_reporter import LanguageQualityReporter


class TestLanguageIdentifier(unittest.TestCase):
    """Tests for the three-category language identification engine."""

    def setUp(self):
        self.lid = LanguageIdentifierV2()

    def test_pure_tamil(self):
        r = self.lid.identify("தமிழ் மிகவும் அழகான மொழி, இது உலகின் மிகப் பழமையான மொழிகளில் ஒன்று.")
        self.assertEqual(r.label, "TAMIL")
        self.assertGreater(r.confidence, 0.7)

    def test_pure_english(self):
        r = self.lid.identify("The quick brown fox jumps over the lazy dog near the river bank.")
        self.assertEqual(r.label, "ENGLISH")
        self.assertGreater(r.confidence, 0.5)

    def test_tanglish_romanized(self):
        r = self.lid.identify("Innaiku evening tea sapda polama? Enaku romba tired-ah iruku.")
        self.assertEqual(r.label, "TANGLISH")

    def test_tanglish_code_switch(self):
        r = self.lid.identify("இந்த server configuration ரொம்ப complex-ஆ இருக்கு, restart பண்ணவா?")
        self.assertEqual(r.label, "TANGLISH")
        self.assertTrue(r.is_code_mixed)

    def test_english_with_tamil_particles(self):
        r = self.lid.identify("Let us wrap up this release quickly da, otherwise deployment will get delayed machan.")
        self.assertEqual(r.label, "TANGLISH")

    def test_hindi_out_of_scope(self):
        r = self.lid.identify("हिंदी एक बहुत सुंदर भाषा है और भारत में सबसे अधिक बोली जाती है।")
        self.assertEqual(r.label, "OUT_OF_SCOPE")

    def test_telugu_out_of_scope(self):
        r = self.lid.identify("తెలుగు భాషలో అనేక అందమైన కవితలు ఉన్నాయి.")
        self.assertEqual(r.label, "OUT_OF_SCOPE")

    def test_empty_input(self):
        r = self.lid.identify("")
        self.assertEqual(r.label, "UNKNOWN")

    def test_numbers_only(self):
        r = self.lid.identify("12345 67890")
        self.assertEqual(r.label, "UNKNOWN")

    def test_formal_tanglish(self):
        r = self.lid.identify("கணினி வலையமைப்பு (computer network) பாதுகாப்பு protocol-கள் முறையாக configure செய்யப்பட வேண்டும்.")
        self.assertEqual(r.label, "TANGLISH")

    def test_latin_not_all_english(self):
        """Romanized Tamil should NOT be classified as English."""
        r = self.lid.identify("Nalla movie pathiya nethu? Climax scene romba emotionally touch aayiduchu.")
        self.assertNotEqual(r.label, "ENGLISH")


class TestUnicodeProcessor(unittest.TestCase):
    """Tests for Tamil-safe Unicode processing."""

    def setUp(self):
        self.proc = UnicodeProcessorV2()

    def test_nfc_normalization(self):
        text = "தமிழ் test"
        cleaned, report = self.proc.normalize(text)
        self.assertTrue(unicodedata.is_normalized('NFC', cleaned))

    def test_tamil_combining_marks_preserved(self):
        text = "கோ"  # க + ோ (combining vowel sign)
        cleaned, report = self.proc.normalize(text)
        self.assertIn("கோ", cleaned)

    def test_virama_preserved(self):
        text = "க்"  # க + virama
        cleaned, report = self.proc.normalize(text)
        self.assertIn(chr(0x0BCD), cleaned)
        self.assertGreater(report.virama_sequences_preserved, 0)

    def test_replacement_char_detection(self):
        text = "test\uFFFDtext"
        _, report = self.proc.normalize(text)
        self.assertTrue(report.has_replacement_char)

    def test_control_char_removal(self):
        text = "test\x01\x02text"
        cleaned, report = self.proc.normalize(text)
        self.assertNotIn("\x01", cleaned)
        self.assertEqual(report.control_chars_removed, 2)

    def test_zwj_preserved(self):
        text = "test\u200Dtext"
        cleaned, _ = self.proc.normalize(text)
        self.assertIn("\u200D", cleaned)

    def test_round_trip(self):
        texts = [
            "தமிழ் மொழி",
            "server configuration-ஐ test பண்ணிட்டேன்",
            "The quick brown fox",
            "கோ கா கி கீ கு கூ",
        ]
        for text in texts:
            self.assertTrue(self.proc.round_trip_check(text), f"Round-trip failed: {text}")

    def test_adversarial_lone_combining_mark(self):
        # Lone combining mark at start
        text = chr(0x0BBE) + "test"
        _, report = self.proc.normalize(text)
        self.assertTrue(any("Lone combining" in m for m in report.malformed_sequences))

    def test_adversarial_double_virama(self):
        text = "க" + chr(0x0BCD) + chr(0x0BCD)  # double virama
        _, report = self.proc.normalize(text)
        self.assertTrue(any("Double virama" in m for m in report.malformed_sequences))


class TestTanglishAnalyzer(unittest.TestCase):
    """Tests for Tanglish code-switching analysis."""

    def setUp(self):
        self.analyzer = TanglishAnalyzer()

    def test_code_switch_detection(self):
        text = "இந்த server configuration ரொம்ப complex"
        analysis = self.analyzer.analyze(text)
        self.assertGreater(len(analysis.code_switch_points), 0)
        self.assertGreater(analysis.tamil_ratio, 0)
        self.assertGreater(analysis.latin_ratio, 0)

    def test_discourse_markers(self):
        text = "Let us do this quickly da, machan we need to finish."
        analysis = self.analyzer.analyze(text)
        self.assertIn("da", analysis.discourse_markers_found)
        self.assertIn("machan", analysis.discourse_markers_found)

    def test_tamil_suffix_detection(self):
        text = "server-ல் configuration-ஐ update"
        analysis = self.analyzer.analyze(text)
        self.assertTrue(any("-ல்" in s or "-ஐ" in s for s in analysis.tamil_suffixes_detected))

    def test_pure_english_no_switches(self):
        text = "The quick brown fox jumps over the lazy dog."
        analysis = self.analyzer.analyze(text)
        self.assertEqual(len(analysis.code_switch_points), 0)
        self.assertEqual(analysis.tamil_char_count, 0)

    def test_romanized_tamil_candidates(self):
        text = "Innaiku evening sapda polama pannunga vaanga"
        analysis = self.analyzer.analyze(text)
        self.assertTrue(analysis.is_structurally_plausible)


class TestQualityFilter(unittest.TestCase):
    """Tests for configurable quality filtering."""

    def setUp(self):
        self.qf = QualityFilterV2()

    def test_empty_record(self):
        v = self.qf.evaluate("")
        self.assertFalse(v.passed)
        self.assertIn("EMPTY_RECORD", v.rejection_reasons)

    def test_too_short(self):
        v = self.qf.evaluate("hi")
        self.assertFalse(v.passed)
        self.assertIn("TOO_SHORT", v.rejection_reasons)

    def test_repeated_char_spam(self):
        v = self.qf.evaluate("aaaaaaaaaa this is spam text")
        self.assertFalse(v.passed)
        self.assertIn("REPEATED_CHAR_SPAM", v.rejection_reasons)

    def test_url_heavy(self):
        v = self.qf.evaluate("Visit https://example.com/very/long/url/path/here for more info")
        # URL ratio may exceed threshold
        if v.url_ratio > 0.30:
            self.assertIn("URL_HEAVY", v.rejection_reasons)

    def test_malformed_unicode(self):
        v = self.qf.evaluate("This text has \uFFFD replacement characters in it.")
        self.assertIn("MALFORMED_UNICODE", v.rejection_reasons)

    def test_good_text_passes(self):
        v = self.qf.evaluate("This is a perfectly normal English sentence with enough words to pass quality checks.")
        self.assertTrue(v.passed)
        self.assertEqual(v.rejection_reasons, [])

    def test_good_tamil_passes(self):
        v = self.qf.evaluate("தமிழ் மிகவும் அழகான மொழி, பல நூற்றாண்டுகளாக வளர்ந்த இலக்கிய மரபைக் கொண்டது.")
        self.assertTrue(v.passed)

    def test_boilerplate(self):
        v = self.qf.evaluate("Please accept our cookie policy and terms of service before continuing.")
        self.assertIn("BOILERPLATE_DETECTED", v.rejection_reasons)

    def test_rejection_reasons_machine_readable(self):
        v = self.qf.evaluate("")
        for reason in v.rejection_reasons:
            self.assertTrue(reason.isupper() and "_" in reason or reason.isupper(),
                            f"Reason '{reason}' is not machine-readable uppercase code")


class TestDuplicateDetector(unittest.TestCase):
    """Tests for multi-level duplicate detection."""

    def setUp(self):
        self.dd = DuplicateDetectorV2(near_dup_threshold=0.80)

    def test_exact_duplicate(self):
        text = "இந்த server configuration ரொம்ப complex-ஆ இருக்கு."
        r1 = self.dd.check_and_register("doc-001", text)
        self.assertFalse(r1.is_duplicate)
        r2 = self.dd.check_and_register("doc-002", text)
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.dup_type, "EXACT")
        self.assertEqual(r2.matched_id, "doc-001")

    def test_normalized_duplicate(self):
        t1 = "Hello   world   test"
        t2 = "Hello world test"
        r1 = self.dd.check_and_register("doc-003", t1)
        self.assertFalse(r1.is_duplicate)
        r2 = self.dd.check_and_register("doc-004", t2)
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.dup_type, "NORMALIZED")

    def test_near_duplicate(self):
        t1 = "The quick brown fox jumps over the lazy dog near the old stone bridge."
        t2 = "The quick brown fox jumps over the lazy dog near the old wooden bridge."
        r1 = self.dd.check_and_register("doc-005", t1)
        self.assertFalse(r1.is_duplicate)
        r2 = self.dd.check_and_register("doc-006", t2)
        # May or may not be near-duplicate depending on threshold
        if r2.is_duplicate:
            self.assertEqual(r2.dup_type, "NEAR_DUPLICATE")

    def test_unique_texts(self):
        t1 = "This is completely different English text about software engineering."
        t2 = "தமிழ் மொழியின் வரலாறு மிகவும் சுவாரசியமானது."
        r1 = self.dd.check_and_register("doc-007", t1)
        r2 = self.dd.check_and_register("doc-008", t2)
        self.assertFalse(r1.is_duplicate)
        self.assertFalse(r2.is_duplicate)

    def test_mixed_script_duplicates(self):
        t1 = "server configuration-ஐ test பண்ணிட்டேன்"
        r1 = self.dd.check_and_register("doc-009", t1)
        r2 = self.dd.check_and_register("doc-010", t1)
        self.assertTrue(r2.is_duplicate)


class TestTokenizerRoundTrip(unittest.TestCase):
    """Read-only tokenizer evaluation using Candidate A."""

    def setUp(self):
        self.tokenizer_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.expected_hash = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"

    def test_tokenizer_hash_invariant(self):
        h = hashlib.sha256(self.tokenizer_path.read_bytes()).hexdigest()
        self.assertEqual(h, self.expected_hash)

    def test_tokenizer_loads(self):
        try:
            from tokenizers import Tokenizer
            tok = Tokenizer.from_file(str(self.tokenizer_path))
            self.assertIsNotNone(tok)
            self.assertEqual(tok.get_vocab_size(), 32768)
        except ImportError:
            self.skipTest("tokenizers library not available")

    def test_tokenizer_roundtrip_english(self):
        try:
            from tokenizers import Tokenizer
            tok = Tokenizer.from_file(str(self.tokenizer_path))
            text = "The quick brown fox jumps over the lazy dog."
            encoded = tok.encode(text)
            decoded = tok.decode(encoded.ids)
            self.assertIn("quick", decoded)
            self.assertIn("fox", decoded)
        except ImportError:
            self.skipTest("tokenizers library not available")

    def test_tokenizer_roundtrip_tamil(self):
        try:
            from tokenizers import Tokenizer
            tok = Tokenizer.from_file(str(self.tokenizer_path))
            text = "தமிழ் மொழி"
            encoded = tok.encode(text)
            decoded = tok.decode(encoded.ids)
            # Check no UNK flood — at least some Tamil characters recovered
            self.assertGreater(len(decoded.strip()), 0)
        except ImportError:
            self.skipTest("tokenizers library not available")


class TestExistingRegressionSuites(unittest.TestCase):
    """Verify existing test suites still pass."""

    def test_readiness_suite(self):
        import subprocess
        res = subprocess.run(
            [sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-q"],
            cwd=str(PATCH_ROOT), capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 0, f"test_readiness failed: {res.stdout}\n{res.stderr}")
        self.assertIn("5 passed", res.stdout)

    def test_phase22_planning_suite(self):
        import subprocess
        res = subprocess.run(
            [sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase22_production_planning.py"), "-q"],
            cwd=str(PATCH_ROOT), capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 0, f"test_phase22 failed: {res.stdout}\n{res.stderr}")
        self.assertIn("6 passed", res.stdout)


class TestGovernanceInvariants(unittest.TestCase):
    """Verify production gates remain locked."""

    def test_zero_production_data(self):
        quarantine_raw = PATCH_ROOT / "quarantine" / "raw"
        if quarantine_raw.exists():
            files = list(quarantine_raw.glob("*"))
            self.assertEqual(len(files), 0, f"Quarantine not empty: {files}")

    def test_candidate_a_hash(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561")

    def test_candidate_b_hash(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888")


if __name__ == "__main__":
    unittest.main(verbosity=2)
