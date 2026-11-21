"""IGRIS Phase 15 — Tokenizer Metrics and Evaluation Statistics Engine.

Computes exact statistical, linguistic, and operational metrics for tokenizer candidates
across multilingual corpora without modifying underlying artifacts.
"""
from __future__ import annotations

import math
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any, Sequence

# Indic Unicode Ranges for script-aware metrics
INDIC_RANGES = {
    "Devanagari": (0x0900, 0x097F),
    "Bengali": (0x0980, 0x09FF),
    "Gurmukhi": (0x0A00, 0x0A7F),
    "Gujarati": (0x0A80, 0x0AFF),
    "Oriya": (0x0B00, 0x0B7F),
    "Tamil": (0x0B80, 0x0BFF),
    "Telugu": (0x0C00, 0x0C7F),
    "Kannada": (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
}


def is_indic_codepoint(cp: int) -> bool:
    """Return True if codepoint falls within any major Indic script block."""
    return any(start <= cp <= end for start, end in INDIC_RANGES.values())


@dataclass
class SampleTokenizationMetrics:
    """Exact metrics computed for a single text sample."""
    sample_id: str
    category: str
    text: str
    char_count: int
    word_count: int
    byte_count: int
    token_count: int
    token_ids: list[int]
    # Core quality metrics
    tokens_per_word: float  # Fertility
    tokens_per_char: float
    chars_per_token: float  # Compression (chars)
    bytes_per_token: float  # Compression (bytes)
    # Coverage & Special tokens
    unknown_token_count: int
    unknown_token_rate: float
    byte_fallback_count: int
    byte_fallback_rate: float
    character_coverage: float
    # Character class counts
    punctuation_count: int
    whitespace_count: int
    digit_count: int
    indic_char_count: int
    latin_char_count: int
    # Round-trip fidelity
    round_trip_exact: bool
    round_trip_nfc: bool
    decoded_text: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Omit raw text in large summaries if desired, or keep as dict
        return d


@dataclass
class AggregateCategoryMetrics:
    """Aggregated metrics across a category or language."""
    category: str
    sample_count: int
    total_chars: int
    total_words: int
    total_bytes: int
    total_tokens: int
    avg_tokens_per_word: float  # Aggregate Fertility
    avg_tokens_per_char: float
    avg_chars_per_token: float  # Aggregate Compression (chars)
    avg_bytes_per_token: float  # Aggregate Compression (bytes)
    total_unknown_tokens: int
    unknown_token_rate: float
    total_byte_fallbacks: int
    byte_fallback_rate: float
    character_coverage: float
    round_trip_exact_pct: float
    round_trip_nfc_pct: float
    min_tokens: int
    max_tokens: int


def compute_sample_metrics(
    sample_id: str,
    category: str,
    text: str,
    token_ids: list[int],
    decoded_text: str,
    byte_fallback_ids: set[int] | None = None,
    unk_ids: set[int] | None = None,
) -> SampleTokenizationMetrics:
    """Compute all required tokenization metrics for a single sample."""
    byte_fallback_ids = byte_fallback_ids or set()
    unk_ids = unk_ids or set()

    char_count = len(text)
    words = text.split()
    word_count = len(words)
    byte_count = len(text.encode("utf-8"))
    token_count = len(token_ids)

    # Ratios
    safe_words = max(word_count, 1)
    safe_chars = max(char_count, 1)
    safe_tokens = max(token_count, 1)

    tokens_per_word = token_count / safe_words
    tokens_per_char = token_count / safe_chars
    chars_per_token = char_count / safe_tokens
    bytes_per_token = byte_count / safe_tokens

    # Fallbacks and Unknowns
    unk_count = sum(1 for tid in token_ids if tid in unk_ids)
    unk_rate = unk_count / safe_tokens

    fallback_count = sum(1 for tid in token_ids if tid in byte_fallback_ids)
    fallback_rate = fallback_count / safe_tokens

    # Character coverage: proportion of characters decoded without UNK
    # In byte-fallback tokenizers, full coverage is 1.0 if round-trip succeeds
    char_coverage = 1.0 if unk_count == 0 else max(0.0, 1.0 - unk_rate)

    # Character composition
    punct_count = 0
    ws_count = 0
    digit_count = 0
    indic_count = 0
    latin_count = 0

    for ch in text:
        cp = ord(ch)
        cat = unicodedata.category(ch)
        if cat.startswith("P"):
            punct_count += 1
        elif cat.startswith("Z") or ch in "\t\n\r":
            ws_count += 1
        elif cat.startswith("N"):
            digit_count += 1

        if is_indic_codepoint(cp):
            indic_count += 1
        elif ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
            latin_count += 1

    # Round-trip verification
    rt_exact = (decoded_text == text)
    rt_nfc = (unicodedata.normalize("NFC", decoded_text) == unicodedata.normalize("NFC", text))

    return SampleTokenizationMetrics(
        sample_id=sample_id,
        category=category,
        text=text,
        char_count=char_count,
        word_count=word_count,
        byte_count=byte_count,
        token_count=token_count,
        token_ids=token_ids,
        tokens_per_word=tokens_per_word,
        tokens_per_char=tokens_per_char,
        chars_per_token=chars_per_token,
        bytes_per_token=bytes_per_token,
        unknown_token_count=unk_count,
        unknown_token_rate=unk_rate,
        byte_fallback_count=fallback_count,
        byte_fallback_rate=fallback_rate,
        character_coverage=char_coverage,
        punctuation_count=punct_count,
        whitespace_count=ws_count,
        digit_count=digit_count,
        indic_char_count=indic_count,
        latin_char_count=latin_count,
        round_trip_exact=rt_exact,
        round_trip_nfc=rt_nfc,
        decoded_text=decoded_text,
    )


def aggregate_sample_metrics(
    category: str,
    samples: Sequence[SampleTokenizationMetrics],
) -> AggregateCategoryMetrics:
    """Aggregate a sequence of sample metrics into category-level statistics."""
    if not samples:
        return AggregateCategoryMetrics(
            category=category,
            sample_count=0,
            total_chars=0,
            total_words=0,
            total_bytes=0,
            total_tokens=0,
            avg_tokens_per_word=0.0,
            avg_tokens_per_char=0.0,
            avg_chars_per_token=0.0,
            avg_bytes_per_token=0.0,
            total_unknown_tokens=0,
            unknown_token_rate=0.0,
            total_byte_fallbacks=0,
            byte_fallback_rate=0.0,
            character_coverage=1.0,
            round_trip_exact_pct=100.0,
            round_trip_nfc_pct=100.0,
            min_tokens=0,
            max_tokens=0,
        )

    sample_count = len(samples)
    total_chars = sum(s.char_count for s in samples)
    total_words = sum(s.word_count for s in samples)
    total_bytes = sum(s.byte_count for s in samples)
    total_tokens = sum(s.token_count for s in samples)

    safe_words = max(total_words, 1)
    safe_chars = max(total_chars, 1)
    safe_tokens = max(total_tokens, 1)

    avg_tokens_per_word = total_tokens / safe_words
    avg_tokens_per_char = total_tokens / safe_chars
    avg_chars_per_token = total_chars / safe_tokens
    avg_bytes_per_token = total_bytes / safe_tokens

    total_unks = sum(s.unknown_token_count for s in samples)
    unk_rate = total_unks / safe_tokens

    total_fallbacks = sum(s.byte_fallback_count for s in samples)
    fallback_rate = total_fallbacks / safe_tokens

    avg_coverage = sum(s.character_coverage for s in samples) / sample_count
    exact_pct = (sum(1 for s in samples if s.round_trip_exact) / sample_count) * 100.0
    nfc_pct = (sum(1 for s in samples if s.round_trip_nfc) / sample_count) * 100.0

    min_toks = min(s.token_count for s in samples)
    max_toks = max(s.token_count for s in samples)

    return AggregateCategoryMetrics(
        category=category,
        sample_count=sample_count,
        total_chars=total_chars,
        total_words=total_words,
        total_bytes=total_bytes,
        total_tokens=total_tokens,
        avg_tokens_per_word=round(avg_tokens_per_word, 4),
        avg_tokens_per_char=round(avg_tokens_per_char, 4),
        avg_chars_per_token=round(avg_chars_per_token, 4),
        avg_bytes_per_token=round(avg_bytes_per_token, 4),
        total_unknown_tokens=total_unks,
        unknown_token_rate=round(unk_rate, 6),
        total_byte_fallbacks=total_fallbacks,
        byte_fallback_rate=round(fallback_rate, 6),
        character_coverage=round(avg_coverage, 4),
        round_trip_exact_pct=round(exact_pct, 2),
        round_trip_nfc_pct=round(nfc_pct, 2),
        min_tokens=min_toks,
        max_tokens=max_toks,
    )
