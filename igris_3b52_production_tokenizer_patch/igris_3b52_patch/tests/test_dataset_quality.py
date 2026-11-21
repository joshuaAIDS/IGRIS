"""IGRIS Milestone 3B.59 — Unit tests for Dataset Quality and Governance engine."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add patch src and scripts
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

import unicodedata2

from dataset_quality_checks import (
    MinHashNearDuplicateDetector,
    audit_sample_quality,
    compute_non_linguistic_ratio,
    detect_train_eval_leakage,
    identify_script_distribution,
    screen_pii_and_sensitive_data,
    verify_encoding_and_normalization,
)


class TestDatasetQuality(unittest.TestCase):
    def test_utf8_and_nfc_validation(self) -> None:
        """Valid NFC text passes encoding and normalization checks."""
        text = "தமிழ் மொழி மற்றும் English clean text."
        is_utf8, is_nfc, has_surr, issues = verify_encoding_and_normalization(text)
        self.assertTrue(is_utf8)
        self.assertTrue(is_nfc)
        self.assertFalse(has_surr)
        self.assertEqual(len(issues), 0)

    def test_decomposed_nfd_detected(self) -> None:
        """Decomposed NFD text is flagged as non-canonical."""
        nfd_text = unicodedata2.normalize("NFD", "é")  # Decomposes to 'e' + U+0301
        is_utf8, is_nfc, has_surr, issues = verify_encoding_and_normalization(nfd_text)
        self.assertTrue(is_utf8)
        self.assertFalse(is_nfc)
        self.assertTrue(any("NFC" in issue for issue in issues))

    def test_lone_surrogates_flagged(self) -> None:
        """Lone surrogate codepoints are flagged immediately."""
        bad_text = "test\ud800text"
        is_utf8, is_nfc, has_surr, issues = verify_encoding_and_normalization(bad_text)
        self.assertTrue(has_surr)
        self.assertTrue(any("surrogate" in issue for issue in issues))

    def test_script_distribution(self) -> None:
        """Identifies primary scripts and block distributions accurately."""
        tamil_text = "தமிழ் ஒரு தொன்மையான மொழி."
        script, dist = identify_script_distribution(tamil_text)
        self.assertEqual(script, "Tamil")
        self.assertGreater(dist["Tamil"], 0.70)

        hindi_text = "नमस्ते दुनिया, यह हिन्दी वाक्य है।"
        script_h, dist_h = identify_script_distribution(hindi_text)
        self.assertEqual(script_h, "Devanagari")
        self.assertGreater(dist_h["Devanagari"], 0.60)

        english_text = "Standard English prose without non-Latin characters."
        script_e, dist_e = identify_script_distribution(english_text)
        self.assertEqual(script_e, "Latin")
        self.assertGreater(dist_e["Latin"], 0.80)

    def test_pii_screening(self) -> None:
        """Detects emails, phone numbers, IP addresses, and API keys."""
        text = (
            "Contact user@example.com or support@igris.org. "
            "Phone: +1-800-555-0199 or 9876543210. "
            "Server at 192.168.1.100. "
            "Secret: api_key='sk_live_1234567890abcdef123456'."
        )
        pii = screen_pii_and_sensitive_data(text)
        self.assertIn("email", pii)
        self.assertEqual(len(pii["email"]), 2)
        self.assertIn("phone", pii)
        self.assertIn("ip_address", pii)
        self.assertIn("api_key", pii)

    def test_clean_text_has_no_pii(self) -> None:
        """Clean sample produces empty PII matches."""
        text = "This is a completely clean sentence discussing multilingual tokenization algorithms."
        pii = screen_pii_and_sensitive_data(text)
        self.assertEqual(len(pii), 0)

    def test_non_linguistic_ratio(self) -> None:
        """Calculates ratio of non-linguistic characters."""
        normal_text = "Hello world! How are you?"
        noise_normal = compute_non_linguistic_ratio(normal_text)
        self.assertLess(noise_normal, 0.10)

        symbol_dense = "### $$$ %%% &&& *** +++ === ~~~ @@@ !!!"
        noise_dense = compute_non_linguistic_ratio(symbol_dense)
        self.assertGreater(noise_dense, 0.50)

    def test_minhash_near_duplicate_detection(self) -> None:
        """MinHash correctly detects near-duplicates and separates distinct texts."""
        detector = MinHashNearDuplicateDetector(threshold=0.85)
        text_a = "The decoder-only autoregressive transformer architecture relies heavily on causal attention."
        text_b = "The decoder-only autoregressive transformer architecture relies heavily on causal attention!"  # punctuation diff
        text_c = "Shakespeare wrote many plays and sonnets in Elizabethan England during the sixteenth century."

        sig_a = detector.compute_signature(text_a)
        sig_b = detector.compute_signature(text_b)
        sig_c = detector.compute_signature(text_c)

        sim_ab = detector.estimate_similarity(sig_a, sig_b)
        sim_ac = detector.estimate_similarity(sig_a, sig_c)

        self.assertGreaterEqual(sim_ab, 0.85)
        self.assertTrue(detector.is_near_duplicate(sig_a, sig_b))
        self.assertLess(sim_ac, 0.30)
        self.assertFalse(detector.is_near_duplicate(sig_a, sig_c))

    def test_train_eval_leakage_detector(self) -> None:
        """Flags exact hash collisions between training inventory and evaluation set."""
        import hashlib
        train_hashes = {
            hashlib.sha256("Training sample 1".encode("utf-8")).hexdigest(),
            hashlib.sha256("Training sample 2".encode("utf-8")).hexdigest(),
        }

        clean_eval = ["Evaluation sample A", "Evaluation sample B"]
        no_leak, leakages = detect_train_eval_leakage(clean_eval, train_hashes)
        self.assertTrue(no_leak)
        self.assertEqual(len(leakages), 0)

        contaminated_eval = ["Evaluation sample A", "Training sample 1"]
        is_clean, leaks = detect_train_eval_leakage(contaminated_eval, train_hashes)
        self.assertFalse(is_clean)
        self.assertEqual(len(leaks), 1)


if __name__ == "__main__":
    unittest.main()
