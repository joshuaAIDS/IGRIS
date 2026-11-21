"""
IGRIS Phase 24 / Phase 25 / Phase 26 Configurable Quality Filter v2
===================================================================
Detects empty, short, long, spammy, URL-heavy, malformed, and low-info records.
Every rejection carries a machine-readable reason code.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class QualityConfigV2:
    min_length_chars: int = 10
    max_length_chars: int = 100000
    min_words: int = 2
    max_repeated_char_run: int = 5
    max_url_ratio: float = 0.30
    max_punct_ratio: float = 0.40
    max_digit_ratio: float = 0.50
    boilerplate_keywords: Set[str] = field(default_factory=lambda: {
        "cookie policy", "terms of service", "privacy policy", "click here",
        "subscribe now", "advertisement", "404 not found", "page not found",
    })


@dataclass
class QualityVerdict:
    passed: bool
    rejection_reasons: List[str]   # Machine-readable reason codes
    char_count: int
    word_count: int
    url_ratio: float
    punct_ratio: float
    repeated_char_max_run: int
    has_malformed_unicode: bool


class QualityFilterV2:
    """Configurable text quality filter producing machine-readable rejection reasons."""

    def __init__(self, config: Optional[QualityConfigV2] = None):
        self.config = config or QualityConfigV2()

    def evaluate(self, text: str) -> QualityVerdict:
        reasons: List[str] = []
        if not text or not text.strip():
            return QualityVerdict(False, ["EMPTY_RECORD"], 0, 0, 0.0, 0.0, 0, False)

        stripped = text.strip()
        char_count = len(stripped)
        words = re.findall(r'\b\w+\b', stripped, re.UNICODE)
        word_count = len(words)

        # Length checks
        if char_count < self.config.min_length_chars:
            reasons.append("TOO_SHORT")
        if char_count > self.config.max_length_chars:
            reasons.append("TOO_LONG")
        if word_count < self.config.min_words:
            reasons.append("TOO_FEW_WORDS")

        # Repeated character spam
        max_run = 0
        cur_run = 1
        for i in range(1, len(stripped)):
            if stripped[i] == stripped[i - 1]:
                cur_run += 1
                max_run = max(max_run, cur_run)
            else:
                cur_run = 1
        max_run = max(max_run, cur_run) if stripped else 0
        if max_run > self.config.max_repeated_char_run:
            reasons.append("REPEATED_CHAR_SPAM")

        # URL density
        urls = re.findall(r'https?://\S+', stripped)
        url_chars = sum(len(u) for u in urls)
        url_ratio = url_chars / char_count if char_count > 0 else 0
        if url_ratio > self.config.max_url_ratio:
            reasons.append("URL_HEAVY")

        # Punctuation density
        punct_count = sum(1 for ch in stripped if unicodedata.category(ch).startswith('P'))
        punct_ratio = punct_count / char_count if char_count > 0 else 0
        if punct_ratio > self.config.max_punct_ratio:
            reasons.append("EXCESSIVE_PUNCTUATION")

        # Malformed Unicode:
        # 1. Contains U+FFFD replacement char
        # 2. Contains double viramas (U+0BCD U+0BCD)
        # 3. Contains lone combining vowel sign at position 0
        has_malformed = '\uFFFD' in stripped or '\u0BCD\u0BCD' in stripped
        if not has_malformed and stripped:
            first_cp = ord(stripped[0])
            if 0x0BBE <= first_cp <= 0x0BCD:  # Lone Tamil vowel sign or virama at start of text
                has_malformed = True

        if has_malformed:
            reasons.append("MALFORMED_UNICODE")

        # Boilerplate
        lower_text = stripped.lower()
        for kw in self.config.boilerplate_keywords:
            if kw in lower_text:
                reasons.append("BOILERPLATE_DETECTED")
                break

        # Language uncertainty (detect purely symbolic / numeric text)
        alpha_count = sum(1 for ch in stripped if ch.isalpha())
        if alpha_count == 0:
            reasons.append("NO_ALPHABETIC_CHARS")

        return QualityVerdict(
            passed=len(reasons) == 0,
            rejection_reasons=reasons,
            char_count=char_count,
            word_count=word_count,
            url_ratio=round(url_ratio, 4),
            punct_ratio=round(punct_ratio, 4),
            repeated_char_max_run=max_run,
            has_malformed_unicode=has_malformed,
        )
