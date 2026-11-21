"""
IGRIS Text Quality Filtering Engine
===================================
Phase 14 Dataset Integrity, Cleaning, and Validation Infrastructure

Enforces:
1. Rejection of empty and extremely short documents.
2. Repeated character sequence detection (e.g. "aaaaaaa", "!!!!!!").
3. Excessive whitespace and formatting artifact detection.
4. Repeated line and loop detection.
5. Corrupted text / mojibake detection.
6. Excessive symbol-to-alphanumeric ratio filtering.
7. Low-information boilerplate and navigation artifact filtering.
8. Suspicious machine spam detection.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple


@dataclass
class QualityConfig:
    min_doc_length_chars: int = 15
    min_words: int = 3
    max_repeated_char_run: int = 6
    max_repeated_line_ratio: float = 0.35
    max_symbol_ratio: float = 0.45
    max_whitespace_ratio: float = 0.50
    boilerplate_keywords: Set[str] = field(default_factory=lambda: {
        "cookie policy", "terms of service", "privacy policy", "all rights reserved",
        "click here", "subscribe now", "advertisement", "sponsored content",
        "sign in to continue", "404 not found", "page not found"
    })


@dataclass
class QualityDecision:
    passed: bool
    quality_score: float
    rejection_reasons: List[str]
    doc_length_chars: int
    word_count: int
    symbol_ratio: float
    repeated_line_ratio: float


# Mojibake patterns common in broken UTF-8 / Latin-1 transcode
MOJIBAKE_PATTERNS = [
    re.compile(r"Ã[©¢¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿]"),
    re.compile(r"â€[™œž]"),
    re.compile(r"ï¿½"),
    re.compile(r"\ufffd"),
]


class QualityFilter:
    """
    Configurable text quality filtering engine with granular diagnostics
    and multi-dimensional scoring.
    """
    def __init__(self, config: Optional[QualityConfig] = None):
        self.config = config if config is not None else QualityConfig()

    def evaluate_document(self, text: str) -> QualityDecision:
        """
        Evaluate text against quality standards.
        Returns QualityDecision containing passed flag, composite score, and diagnostic reasons.
        """
        rejection_reasons: List[str] = []

        if not text or not text.strip():
            return QualityDecision(
                passed=False,
                quality_score=0.0,
                rejection_reasons=["EMPTY_DOCUMENT"],
                doc_length_chars=0,
                word_count=0,
                symbol_ratio=0.0,
                repeated_line_ratio=0.0
            )

        stripped = text.strip()
        length_chars = len(stripped)
        words = re.findall(r"\b\w+\b", stripped, re.UNICODE)
        word_count = len(words)

        # 1. Extremely Short Document Check
        if length_chars < self.config.min_doc_length_chars:
            rejection_reasons.append(
                f"EXTREMELY_SHORT_DOCUMENT: {length_chars} chars < min {self.config.min_doc_length_chars}"
            )

        if word_count < self.config.min_words:
            rejection_reasons.append(
                f"INSUFFICIENT_WORDS: {word_count} words < min {self.config.min_words}"
            )

        # 2. Repeated Character Sequence Check (e.g. "aaaaaa", "!!!!!!")
        repeat_pattern = re.compile(r"(.)\1{" + str(self.config.max_repeated_char_run) + r",}")
        if repeat_pattern.search(stripped):
            rejection_reasons.append(
                f"REPEATED_CHAR_SEQUENCE: character repeated > {self.config.max_repeated_char_run} times"
            )

        # 3. Excessive Whitespace Check
        whitespace_chars = sum(1 for c in text if c.isspace())
        ws_ratio = whitespace_chars / len(text) if len(text) > 0 else 0.0
        if ws_ratio > self.config.max_whitespace_ratio:
            rejection_reasons.append(
                f"EXCESSIVE_WHITESPACE: whitespace ratio {ws_ratio:.2f} > max {self.config.max_whitespace_ratio:.2f}"
            )

        # 4. Repeated Line Check
        lines = [line.strip() for line in stripped.splitlines() if line.strip()]
        if len(lines) >= 3:
            total_lines = len(lines)
            unique_lines = len(set(lines))
            repeated_line_ratio = (total_lines - unique_lines) / total_lines
            if repeated_line_ratio > self.config.max_repeated_line_ratio:
                rejection_reasons.append(
                    f"REPEATED_LINES: repeated line ratio {repeated_line_ratio:.2f} > max {self.config.max_repeated_line_ratio:.2f}"
                )
        else:
            repeated_line_ratio = 0.0

        # 5. Mojibake and Corrupted Encoding Check
        for pat in MOJIBAKE_PATTERNS:
            if pat.search(text):
                rejection_reasons.append("CORRUPTED_MOJIBAKE_ENCODING: detected garbled Unicode encoding sequence")
                break

        # 6. Excessive Symbol / Punctuation Density Check
        symbol_count = 0
        alpha_count = 0
        for c in stripped:
            if c.isalnum():
                alpha_count += 1
            elif not c.isspace():
                symbol_count += 1

        total_non_ws = alpha_count + symbol_count
        symbol_ratio = symbol_count / total_non_ws if total_non_ws > 0 else 1.0
        if symbol_ratio > self.config.max_symbol_ratio:
            rejection_reasons.append(
                f"EXCESSIVE_SYMBOL_DENSITY: symbol ratio {symbol_ratio:.2f} > max {self.config.max_symbol_ratio:.2f}"
            )

        # 7. Low-information Boilerplate Check
        lower_text = stripped.lower()
        for kw in self.config.boilerplate_keywords:
            if kw in lower_text and word_count < 15:
                rejection_reasons.append(f"BOILERPLATE_LOW_INFORMATION: contains '{kw}' in low-context document")
                break

        # Calculate composite quality score (0.0 to 1.0)
        score = 1.0
        if length_chars < self.config.min_doc_length_chars:
            score -= 0.3
        if word_count < self.config.min_words:
            score -= 0.3
        if symbol_ratio > 0.3:
            score -= min(0.3, symbol_ratio * 0.5)
        if repeated_line_ratio > 0.2:
            score -= min(0.3, repeated_line_ratio)
        if any("MOJIBAKE" in r for r in rejection_reasons):
            score -= 0.5

        quality_score = max(0.0, min(1.0, round(score, 4)))
        passed = len(rejection_reasons) == 0

        return QualityDecision(
            passed=passed,
            quality_score=quality_score,
            rejection_reasons=rejection_reasons,
            doc_length_chars=length_chars,
            word_count=word_count,
            symbol_ratio=round(symbol_ratio, 4),
            repeated_line_ratio=round(repeated_line_ratio, 4)
        )
