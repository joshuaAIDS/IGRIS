"""Trusted sequence rendering reference helper for TS-REN tests."""
from __future__ import annotations

from typing import Callable, Sequence
from .acceptance_config import STRUCTURAL_TOKENS, VOCAB_SIZE
from .validation import require_id_sequence, require_token_id


def decode_content_ids(ids: Sequence[int], decode_content: Callable[[list[int]], str]) -> str:
    """Decode a content-only span; structural IDs are never accepted here."""
    validated = require_id_sequence(ids, content_only=True, vocab_size=VOCAB_SIZE)
    result = decode_content(validated)
    if not isinstance(result, str):
        raise TypeError("decode_content callback must return str")
    return result


def render_sequence(ids: Sequence[int], decode_content: Callable[[list[int]], str]) -> str:
    """Render trusted structural IDs and decode each maximal content span.

    Structural IDs are rendered using their fixed spellings. Adjacent content
    IDs are decoded together; each structural ID closes the current span.
    No trimming, normalization, or automatic framing is performed here.
    """
    validated = require_id_sequence(ids, content_only=False, vocab_size=VOCAB_SIZE)
    pieces: list[str] = []
    content_span: list[int] = []

    def flush() -> None:
        if not content_span:
            return
        decoded = decode_content_ids(content_span, decode_content)
        pieces.append(decoded)
        content_span.clear()

    for token_id in validated:
        if token_id < len(STRUCTURAL_TOKENS):
            flush()
            pieces.append(STRUCTURAL_TOKENS[token_id])
        else:
            content_span.append(token_id)
    flush()
    return "".join(pieces)
