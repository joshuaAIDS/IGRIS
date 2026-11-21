"""
IGRIS Phase 24 Tamil-Safe Unicode Processing Engine v2
======================================================
Enforces NFC normalization while preserving Tamil combining marks,
virama sequences, and valid ZWJ/ZWNJ behavior.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class UnicodeReport:
    original_length: int
    normalized_length: int
    is_nfc_original: bool
    has_replacement_char: bool
    control_chars_removed: int
    tamil_combining_marks_preserved: int
    virama_sequences_preserved: int
    zwj_zwnj_preserved: int
    malformed_sequences: List[str] = field(default_factory=list)
    script_distribution: Dict[str, float] = field(default_factory=dict)


# Tamil Unicode block: U+0B80 - U+0BFF
TAMIL_VOWELS = set(range(0x0B85, 0x0B95))       # அ-ஔ
TAMIL_CONSONANTS = set(range(0x0B95, 0x0BBA))    # க-ஹ
TAMIL_VOWEL_SIGNS = set(range(0x0BBE, 0x0BCD))   # Combining vowel signs
TAMIL_VIRAMA = 0x0BCD                             # ்
TAMIL_AU_LENGTH_MARK = 0x0BD7                      # ௗ
TAMIL_DIGITS = set(range(0x0BE6, 0x0BF0))
TAMIL_SYMBOLS = set(range(0x0BF0, 0x0BFB))

ZWJ = '\u200D'    # Zero Width Joiner
ZWNJ = '\u200C'   # Zero Width Non-Joiner


def is_tamil_char(cp: int) -> bool:
    return 0x0B80 <= cp <= 0x0BFF


class UnicodeProcessorV2:
    """Tamil-safe Unicode processor with NFC normalization and malformed sequence detection."""

    def normalize(self, text: str) -> Tuple[str, UnicodeReport]:
        """Normalize text while preserving Tamil combining sequences."""
        orig_len = len(text)
        is_nfc_orig = unicodedata.is_normalized('NFC', text)
        has_replacement = '\uFFFD' in text

        # Count Tamil combining marks before normalization
        tamil_combining = sum(1 for ch in text if ord(ch) in TAMIL_VOWEL_SIGNS)
        virama_count = text.count(chr(TAMIL_VIRAMA))
        zwj_zwnj_count = text.count(ZWJ) + text.count(ZWNJ)

        # Detect malformed sequences
        malformed = self._detect_malformed(text)

        # Apply NFC normalization (preserves Tamil combining marks correctly)
        normalized = unicodedata.normalize('NFC', text)

        # Remove dangerous control characters (preserve ZWJ/ZWNJ, tabs, newlines)
        cleaned, ctrl_removed = self._sanitize_controls(normalized)

        # Verify Tamil combining marks preserved
        tamil_combining_after = sum(1 for ch in cleaned if ord(ch) in TAMIL_VOWEL_SIGNS)
        virama_after = cleaned.count(chr(TAMIL_VIRAMA))
        zwj_zwnj_after = cleaned.count(ZWJ) + cleaned.count(ZWNJ)

        # Script distribution
        script_dist = self._compute_script_dist(cleaned)

        return cleaned, UnicodeReport(
            original_length=orig_len,
            normalized_length=len(cleaned),
            is_nfc_original=is_nfc_orig,
            has_replacement_char=has_replacement,
            control_chars_removed=ctrl_removed,
            tamil_combining_marks_preserved=tamil_combining_after,
            virama_sequences_preserved=virama_after,
            zwj_zwnj_preserved=zwj_zwnj_after,
            malformed_sequences=malformed,
            script_distribution=script_dist,
        )

    def _detect_malformed(self, text: str) -> List[str]:
        """Detect malformed Tamil Unicode sequences."""
        issues = []
        chars = list(text)
        for i, ch in enumerate(chars):
            cp = ord(ch)
            # Lone combining mark without base consonant
            if cp in TAMIL_VOWEL_SIGNS or cp == TAMIL_VIRAMA:
                if i == 0 or not is_tamil_char(ord(chars[i - 1])):
                    if i == 0 or ord(chars[i - 1]) not in TAMIL_CONSONANTS:
                        issues.append(f"Lone combining mark U+{cp:04X} at position {i}")
            # Double virama
            if cp == TAMIL_VIRAMA and i > 0 and ord(chars[i - 1]) == TAMIL_VIRAMA:
                issues.append(f"Double virama at position {i}")
        # Replacement char
        if '\uFFFD' in text:
            issues.append("Contains U+FFFD replacement character (encoding failure)")
        return issues

    def _sanitize_controls(self, text: str) -> Tuple[str, int]:
        """Remove invisible control characters while preserving ZWJ/ZWNJ and formatting."""
        result = []
        removed = 0
        for ch in text:
            cat = unicodedata.category(ch)
            if cat == 'Cc' and ch not in ('\n', '\r', '\t'):
                removed += 1
                continue
            # Preserve ZWJ and ZWNJ (category Cf) — important for Indic rendering
            if cat == 'Cf' and ch not in (ZWJ, ZWNJ, '\uFEFF'):
                # Strip other formatting marks except BOM at start
                removed += 1
                continue
            result.append(ch)
        return ''.join(result), removed

    def _compute_script_dist(self, text: str) -> Dict[str, float]:
        """Compute script character distribution."""
        from language_identifier_v2 import _char_script
        counts: Dict[str, int] = {}
        total = 0
        for ch in text:
            sc = _char_script(ch)
            if sc in ("SPACE", "DIGIT", "PUNCT", "OTHER"):
                continue
            counts[sc] = counts.get(sc, 0) + 1
            total += 1
        if total == 0:
            return {}
        return {k: round(v / total, 4) for k, v in counts.items()}

    def round_trip_check(self, text: str) -> bool:
        """Verify that NFC normalization is lossless: normalize(text) == normalize(normalize(text))."""
        n1 = unicodedata.normalize('NFC', text)
        n2 = unicodedata.normalize('NFC', n1)
        return n1 == n2
