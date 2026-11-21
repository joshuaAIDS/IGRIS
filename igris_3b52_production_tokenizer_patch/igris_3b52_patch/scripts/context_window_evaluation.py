"""IGRIS Milestone 3B.59 — Context Window Evaluation and Management Engine.

Evaluates and manages token sequences against the fixed IGRIS context length:
  - Context length: exactly 2,048 tokens
  - Vocabulary: exactly 32,768 tokens
  - Structural tokens: exactly 12 (IDs 0–11)

Provides:
  1. Sequence classification (SHORT: 1–64, MEDIUM: 65–1024, LONG: 1025–2048, OVERFLOW: >2048)
  2. Exact truncation policy (prefix truncation to 2048 with telemetry)
  3. Sliding-window chunking (configurable chunk_size, stride, overlap)
  4. Framing-aware budget allocation (reserving space for structural turn markers)
  5. Boundary preservation and reconstruction fidelity
  6. Strict no-automatic-BOS/EOS guarantee
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from igris.tokenizer.strict import (
    STRUCTURAL_COUNT,
    STRUCTURAL_TOKENS,
    StrictTokenizer,
)

MAX_CONTEXT_LENGTH = 2048


class SequenceTier(str, Enum):
    EMPTY = "EMPTY"
    SHORT = "SHORT"          # 1 - 64 tokens
    MEDIUM = "MEDIUM"        # 65 - 1024 tokens
    LONG = "LONG"            # 1025 - 2048 tokens
    OVERFLOW = "OVERFLOW"    # > 2048 tokens


def classify_sequence_tier(token_count: int) -> SequenceTier:
    """Classify token sequence into context window tiers."""
    if token_count <= 0:
        return SequenceTier.EMPTY
    elif token_count <= 64:
        return SequenceTier.SHORT
    elif token_count <= 1024:
        return SequenceTier.MEDIUM
    elif token_count <= MAX_CONTEXT_LENGTH:
        return SequenceTier.LONG
    else:
        return SequenceTier.OVERFLOW


@dataclass
class TruncationResult:
    original_length: int
    truncated_length: int
    was_truncated: bool
    tokens: list[int]
    tier: SequenceTier


def truncate_to_context(
    tokens: Sequence[int],
    max_length: int = MAX_CONTEXT_LENGTH,
) -> TruncationResult:
    """Apply strict prefix truncation to fit within the context length."""
    orig_len = len(tokens)
    tier = classify_sequence_tier(orig_len)

    if orig_len <= max_length:
        return TruncationResult(
            original_length=orig_len,
            truncated_length=orig_len,
            was_truncated=False,
            tokens=list(tokens),
            tier=tier,
        )

    truncated = list(tokens[:max_length])
    return TruncationResult(
        original_length=orig_len,
        truncated_length=len(truncated),
        was_truncated=True,
        tokens=truncated,
        tier=tier,
    )


@dataclass
class TokenChunk:
    chunk_index: int
    start_offset: int
    end_offset: int
    tokens: list[int]
    is_last: bool


def chunk_sequence(
    tokens: Sequence[int],
    chunk_size: int = MAX_CONTEXT_LENGTH,
    stride: int = 1536,
) -> list[TokenChunk]:
    """Split an arbitrary length token sequence into sliding window chunks.

    Args:
        tokens: Full sequence of token IDs.
        chunk_size: Maximum tokens per chunk (default: 2048).
        stride: Step size between consecutive chunks (default: 1536, overlap = 512).

    Returns:
        List of TokenChunk instances, each with len(tokens) <= chunk_size.
    """
    if not tokens:
        return []

    if len(tokens) <= chunk_size:
        return [
            TokenChunk(
                chunk_index=0,
                start_offset=0,
                end_offset=len(tokens),
                tokens=list(tokens),
                is_last=True,
            )
        ]

    chunks: list[TokenChunk] = []
    chunk_idx = 0
    start = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = list(tokens[start:end])
        is_last = (end >= len(tokens))

        chunks.append(
            TokenChunk(
                chunk_index=chunk_idx,
                start_offset=start,
                end_offset=end,
                tokens=chunk_tokens,
                is_last=is_last,
            )
        )

        if is_last:
            break

        start += stride
        chunk_idx += 1

    return chunks


@dataclass
class FramedSequenceResult:
    total_tokens: int
    content_tokens: int
    framing_tokens: list[int]
    sequence_ids: list[int]
    exceeded_budget: bool


def frame_with_structural_budget(
    content_tokens: Sequence[int],
    prefix_structural_ids: Sequence[int],
    suffix_structural_ids: Sequence[int],
    max_context: int = MAX_CONTEXT_LENGTH,
) -> FramedSequenceResult:
    """Frame content tokens with structural tokens while strictly enforcing context budget."""
    for sid in list(prefix_structural_ids) + list(suffix_structural_ids):
        if not (0 <= sid < STRUCTURAL_COUNT):
            raise ValueError(f"Framing token ID {sid} is not a valid structural token (0–11)")

    overhead = len(prefix_structural_ids) + len(suffix_structural_ids)
    if overhead >= max_context:
        raise ValueError(f"Structural framing overhead ({overhead}) exceeds total context ({max_context})")

    available_content_budget = max_context - overhead
    was_truncated = len(content_tokens) > available_content_budget

    final_content = list(content_tokens[:available_content_budget])
    sequence = list(prefix_structural_ids) + final_content + list(suffix_structural_ids)

    return FramedSequenceResult(
        total_tokens=len(sequence),
        content_tokens=len(final_content),
        framing_tokens=list(prefix_structural_ids) + list(suffix_structural_ids),
        sequence_ids=sequence,
        exceeded_budget=was_truncated,
    )


def verify_no_automatic_bos_eos(
    tokenizer: StrictTokenizer,
    sample_text: str = "Test sequence for framing check.",
) -> bool:
    """Verify that encode_content strictly does NOT insert automatic BOS (1) or EOS (2)."""
    enc = tokenizer.encode_content(sample_text)
    if not enc:
        return True
    first_token = enc[0]
    last_token = enc[-1]
    # Structural IDs 1 (<|begin_of_text|>) and 2 (<|end_of_text|>)
    has_auto_bos = (first_token == 1)
    has_auto_eos = (last_token == 2)
    return not (has_auto_bos or has_auto_eos)
