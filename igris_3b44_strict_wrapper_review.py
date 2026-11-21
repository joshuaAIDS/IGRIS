"""
IGRIS v2.2.28 — Strict Tokenizer Wrapper Review Module
Milestone: 3B.44
Status: Temporary review implementation; NOT production-integrated.

This module does not modify repository files. Load a tokenizer artifact and wrap it
with a consistent strict public API.

Required packages:
    tokenizers==0.23.3
    sentencepiece==0.2.3
    unicodedata2==15.1.0

Structural token IDs are fixed at 0..11. The backend artifacts are expected to
have those exact IDs. Raw binary uses a separate candidate-specific mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Sequence, Tuple, Union

import unicodedata2

STRUCTURAL_TOKENS: Tuple[str, ...] = (
    "<|pad|>",
    "<|begin_of_text|>",
    "<|end_of_text|>",
    "<think>",
    "</think>",
    "<action>",
    "</action>",
    "<action_result>",
    "</action_result>",
    "<|system|>",
    "<|user|>",
    "<|assistant|>",
)
STRUCTURAL_TO_ID = {token: i for i, token in enumerate(STRUCTURAL_TOKENS)}
ID_TO_STRUCTURAL = {i: token for i, token in enumerate(STRUCTURAL_TOKENS)}
STRUCTURAL_COUNT = len(STRUCTURAL_TOKENS)

ESCAPE_SENTINEL = "\U000f0000"
WHITESPACE_MARKER = "\u2581"


def _require_text(value: Any, name: str = "text") -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be str")
    # Python strings can contain lone UTF-16 surrogate code points.
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        raise ValueError(f"{name} contains a lone surrogate code point")
    return value


def _require_sequence(value: Any, name: str) -> Sequence:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, (list, tuple)):
        raise TypeError(f"{name} must be a list or tuple")
    return value


def _validate_ids(ids: Any, vocab_size: int, *, allow_structural: bool) -> List[int]:
    seq = _require_sequence(ids, "ids")
    validated: List[int] = []
    for index, token_id in enumerate(seq):
        # bool is a subclass of int, so reject it explicitly.
        if isinstance(token_id, bool) or not isinstance(token_id, int):
            raise TypeError(f"ids[{index}] must be an integer (bool is not allowed)")
        if token_id < 0:
            raise ValueError(f"ids[{index}] is negative")
        if token_id >= vocab_size:
            raise ValueError(f"ids[{index}] is outside vocabulary range")
        if not allow_structural and token_id < STRUCTURAL_COUNT:
            raise ValueError(f"ids[{index}] is a structural token ID")
        validated.append(token_id)
    return validated


def escape_text(text: str, normalization: str = "NFC") -> str:
    """
    Escape literal reserved spellings before backend encoding.

    NFC mode normalizes first. Exact mode preserves the original code-point
    sequence. The escape grammar is:
      literal sentinel -> sentinel + sentinel
      literal U+2581    -> sentinel + 'W;'
      structural token  -> sentinel + 'Snn;'
    """
    text = _require_text(text)
    if normalization == "NFC":
        text = unicodedata2.normalize("NFC", text)
    elif normalization != "exact":
        raise ValueError("normalization must be 'NFC' or 'exact'")

    out: List[str] = []
    i = 0
    # Match structural spellings longest-first to avoid prefix ambiguity.
    spellings = sorted(STRUCTURAL_TOKENS, key=len, reverse=True)
    while i < len(text):
        if text.startswith(ESCAPE_SENTINEL, i):
            out.append(ESCAPE_SENTINEL + ESCAPE_SENTINEL)
            i += len(ESCAPE_SENTINEL)
            continue
        if text.startswith(WHITESPACE_MARKER, i):
            out.append(ESCAPE_SENTINEL + "W;")
            i += len(WHITESPACE_MARKER)
            continue
        matched = None
        for spelling in spellings:
            if text.startswith(spelling, i):
                matched = spelling
                break
        if matched is not None:
            token_id = STRUCTURAL_TO_ID[matched]
            out.append(f"{ESCAPE_SENTINEL}S{token_id:02d};")
            i += len(matched)
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def unescape_text(text: str) -> str:
    """Strict inverse of escape_text; rejects malformed/noncanonical escapes."""
    text = _require_text(text, "decoded text")
    out: List[str] = []
    i = 0
    while i < len(text):
        if text[i] != ESCAPE_SENTINEL:
            out.append(text[i])
            i += 1
            continue

        i += 1
        if i >= len(text):
            raise ValueError("truncated escape sentinel")

        if text[i] == ESCAPE_SENTINEL:
            out.append(ESCAPE_SENTINEL)
            i += 1
            continue

        if text.startswith("W;", i):
            out.append(WHITESPACE_MARKER)
            i += 2
            continue

        if text.startswith("S", i) and i + 4 <= len(text) and text[i + 3:i + 4] == ";":
            digits = text[i + 1:i + 3]
            if len(digits) == 2 and digits.isdigit():
                token_id = int(digits)
                if token_id in ID_TO_STRUCTURAL:
                    out.append(STRUCTURAL_TOKENS[token_id])
                    i += 4
                    continue

        raise ValueError("malformed, unknown, or noncanonical escape sequence")
    return "".join(out)


class _Backend:
    """Small internal adapter interface."""

    name = "abstract"

    def __init__(self, vocab_size: int):
        self.vocab_size = int(vocab_size)

    def encode_raw_text(self, text: str) -> List[int]:
        raise NotImplementedError

    def decode_raw_text(self, ids: List[int]) -> str:
        raise NotImplementedError

    def byte_id_map(self) -> List[int]:
        raise NotImplementedError


class _TokenizersBackend(_Backend):
    name = "tokenizers-bytelevel-bpe"

    def __init__(self, tokenizer: Any):
        self.tokenizer = tokenizer
        super().__init__(tokenizer.get_vocab_size())

    def encode_raw_text(self, text: str) -> List[int]:
        return list(self.tokenizer.encode(text).ids)

    def decode_raw_text(self, ids: List[int]) -> str:
        return self.tokenizer.decode(ids, skip_special_tokens=False)

    def byte_id_map(self) -> List[int]:
        # GPT-2 / ByteLevel byte-to-Unicode bijection.
        bs = list(range(ord("!"), ord("~") + 1))
        bs += list(range(ord("¡"), ord("¬") + 1))
        bs += list(range(ord("®"), ord("ÿ") + 1))
        cs = bs[:]
        n = 0
        for b in range(256):
            if b not in bs:
                bs.append(b)
                cs.append(256 + n)
                n += 1
        byte_encoder = {b: chr(c) for b, c in zip(bs, cs)}
        mapping = []
        for b in range(256):
            token_id = self.tokenizer.token_to_id(byte_encoder[b])
            if token_id is None:
                raise ValueError(f"Candidate A is missing ByteLevel byte mapping for 0x{b:02X}")
            mapping.append(int(token_id))
        return mapping


class _SentencePieceBackend(_Backend):
    name = "sentencepiece-unigram"

    def __init__(self, processor: Any):
        self.processor = processor
        super().__init__(processor.get_piece_size())

    def encode_raw_text(self, text: str) -> List[int]:
        return list(self.processor.encode(text, out_type=int))

    def decode_raw_text(self, ids: List[int]) -> str:
        return self.processor.decode(ids)

    def byte_id_map(self) -> List[int]:
        mapping = []
        for b in range(256):
            piece = f"<0x{b:02X}>"
            token_id = int(self.processor.piece_to_id(piece))
            if token_id < 0 or self.processor.id_to_piece(token_id) != piece:
                raise ValueError(f"Candidate B is missing byte-fallback piece {piece}")
            mapping.append(token_id)
        return mapping


@dataclass
class StrictTokenizer:
    """Strict text and batch API over either supported tokenizer backend."""

    backend: _Backend
    normalization: str = "NFC"

    @property
    def vocab_size(self) -> int:
        return self.backend.vocab_size

    @property
    def candidate(self) -> str:
        return self.backend.name

    def encode_content(self, text: str) -> List[int]:
        text = _require_text(text)
        escaped = escape_text(text, self.normalization)
        ids = self.backend.encode_raw_text(escaped)
        ids = _validate_ids(ids, self.vocab_size, allow_structural=False)
        return ids

    def decode_content(self, ids: Sequence[int]) -> str:
        validated = _validate_ids(ids, self.vocab_size, allow_structural=False)
        decoded = self.backend.decode_raw_text(validated)
        return unescape_text(decoded)

    def encode_batch(self, texts: Sequence[str]) -> List[List[int]]:
        seq = _require_sequence(texts, "texts")
        # Validate the entire input before doing any backend work.
        for i, text in enumerate(seq):
            _require_text(text, f"texts[{i}]")
        return [self.encode_content(text) for text in seq]

    def decode_batch(self, batch_ids: Sequence[Sequence[int]]) -> List[str]:
        seq = _require_sequence(batch_ids, "batch_ids")
        # Validate all rows before decoding any row.
        validated_rows = []
        for row_index, row in enumerate(seq):
            if not isinstance(row, (list, tuple)):
                raise TypeError(f"batch_ids[{row_index}] must be a list or tuple")
            validated_rows.append(
                _validate_ids(row, self.vocab_size, allow_structural=False)
            )
        return [unescape_text(self.backend.decode_raw_text(row)) for row in validated_rows]

    def render_sequence(self, ids: Sequence[int]) -> str:
        validated = _validate_ids(ids, self.vocab_size, allow_structural=True)
        parts: List[str] = []
        content_span: List[int] = []

        def flush() -> None:
            if content_span:
                decoded = self.backend.decode_raw_text(content_span)
                parts.append(unescape_text(decoded))
                content_span.clear()

        for token_id in validated:
            if token_id in ID_TO_STRUCTURAL:
                flush()
                parts.append(ID_TO_STRUCTURAL[token_id])
            else:
                content_span.append(token_id)
        flush()
        return "".join(parts)

    def raw_binary_codec(self) -> "RawBinaryCodec":
        return RawBinaryCodec(self.backend.byte_id_map(), self.vocab_size)


class RawBinaryCodec:
    """Independent direct-byte codec; never performs text normalization/escaping."""

    def __init__(self, byte_to_id: Sequence[int], vocab_size: int):
        if len(byte_to_id) != 256:
            raise ValueError("byte_to_id must contain exactly 256 IDs")
        ids = _validate_ids(list(byte_to_id), vocab_size, allow_structural=False)
        if len(set(ids)) != 256:
            raise ValueError("byte mapping must be one-to-one")
        self.byte_to_id = tuple(ids)
        self.id_to_byte = {token_id: byte for byte, token_id in enumerate(ids)}
        self.vocab_size = vocab_size

    def encode_bytes(self, data: bytes) -> List[int]:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        return [self.byte_to_id[b] for b in data]

    def decode_bytes(self, ids: Sequence[int]) -> bytes:
        validated = _validate_ids(ids, self.vocab_size, allow_structural=False)
        result = bytearray()
        for i, token_id in enumerate(validated):
            if token_id not in self.id_to_byte:
                raise ValueError(f"ids[{i}] is not a raw-byte token ID")
            result.append(self.id_to_byte[token_id])
        return bytes(result)


def load_candidate_a(model_path: str, normalization: str = "NFC") -> StrictTokenizer:
    from tokenizers import Tokenizer
    tokenizer = Tokenizer.from_file(model_path)
    backend = _TokenizersBackend(tokenizer)
    _validate_artifact_structure(backend)
    return StrictTokenizer(backend, normalization)


def load_candidate_b(model_path: str, normalization: str = "NFC") -> StrictTokenizer:
    import sentencepiece as spm
    processor = spm.SentencePieceProcessor(model_file=model_path)
    backend = _SentencePieceBackend(processor)
    _validate_artifact_structure(backend)
    return StrictTokenizer(backend, normalization)


def _validate_artifact_structure(backend: _Backend) -> None:
    if backend.vocab_size <= STRUCTURAL_COUNT:
        raise ValueError("Vocabulary is too small for the structural token contract")

    if isinstance(backend, _TokenizersBackend):
        for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
            actual_id = backend.tokenizer.token_to_id(spelling)
            if actual_id != expected_id:
                raise ValueError(
                    f"Candidate A structural token mismatch: {spelling} expected "
                    f"ID {expected_id}, got {actual_id}"
                )
    elif isinstance(backend, _SentencePieceBackend):
        for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
            actual_piece = backend.processor.id_to_piece(expected_id)
            if actual_piece != spelling:
                raise ValueError(
                    f"Candidate B structural token mismatch at ID {expected_id}: "
                    f"expected {spelling}, got {actual_piece}"
                )


__all__ = [
    "STRUCTURAL_TOKENS",
    "ESCAPE_SENTINEL",
    "StrictTokenizer",
    "RawBinaryCodec",
    "escape_text",
    "unescape_text",
    "load_candidate_a",
    "load_candidate_b",
]
