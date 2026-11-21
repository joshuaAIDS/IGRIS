"""Strict, backend-independent validation primitives for IGRIS tokenizers."""

from collections.abc import Sequence
from typing import Any

from .acceptance_config import (
    CONTENT_ID_MAX_EXCLUSIVE,
    CONTENT_ID_MIN,
    VOCAB_SIZE,
)


def require_text(value: Any, name: str = "text") -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be str, got {type(value).__name__}")
    # Reject lone UTF-16 surrogate code points; Unicode scalar values only.
    for index, char in enumerate(value):
        if 0xD800 <= ord(char) <= 0xDFFF:
            raise ValueError(f"{name} contains a lone surrogate at index {index}")
    return value


def require_bytes(value: Any, name: str = "payload") -> bytes:
    if not isinstance(value, bytes):
        raise TypeError(f"{name} must be bytes, got {type(value).__name__}")
    return value


def require_token_id(value: Any, *, content_only: bool = True,
                     vocab_size: int = VOCAB_SIZE) -> int:
    # type(...) is int intentionally rejects bool, which subclasses int.
    if type(value) is not int:
        raise TypeError(f"token ID must be int, got {type(value).__name__}")
    if value < 0 or value >= vocab_size:
        raise ValueError(f"token ID {value} outside [0, {vocab_size})")
    if content_only and not (CONTENT_ID_MIN <= value < CONTENT_ID_MAX_EXCLUSIVE):
        raise ValueError(f"structural/reserved token ID {value} is not valid content")
    return value


def require_id_sequence(values: Any, *, content_only: bool = True,
                        vocab_size: int = VOCAB_SIZE,
                        name: str = "ids") -> list[int]:
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of token IDs")
    # Validate the complete sequence before returning a normalized copy.
    result = []
    for index, value in enumerate(values):
        try:
            result.append(require_token_id(
                value, content_only=content_only, vocab_size=vocab_size
            ))
        except (TypeError, ValueError) as exc:
            raise type(exc)(f"{name}[{index}]: {exc}") from exc
    return result


def require_text_batch(values: Any, name: str = "texts") -> list[str]:
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of strings")
    # Full validation happens before a caller invokes a tokenizer backend.
    return [require_text(value, f"{name}[{i}]") for i, value in enumerate(values)]


def require_id_batch(values: Any, *, content_only: bool = True,
                     vocab_size: int = VOCAB_SIZE,
                     name: str = "batch_ids") -> list[list[int]]:
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise TypeError(f"{name} must be a sequence of ID sequences")
    validated = []
    for index, row in enumerate(values):
        validated.append(require_id_sequence(
            row, content_only=content_only, vocab_size=vocab_size,
            name=f"{name}[{index}]"
        ))
    return validated
