"""IGRIS strict tokenizer adapters (Candidate A/B)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence
import unicodedata2

from .artifact_validation import (
    validate_candidate_a_config,
    validate_candidate_b_config,
)

STRUCTURAL_TOKENS = (
    "<|pad|>", "<|begin_of_text|>", "<|end_of_text|>", "<think>",
    "</think>", "<action>", "</action>", "<action_result>",
    "</action_result>", "<|system|>", "<|user|>", "<|assistant|>",
)
STRUCTURAL_TO_ID = {s: i for i, s in enumerate(STRUCTURAL_TOKENS)}
ID_TO_STRUCTURAL = dict(enumerate(STRUCTURAL_TOKENS))
STRUCTURAL_COUNT = 12
VOCAB_SIZE = 32768
ESCAPE_SENTINEL = "\U000f0000"
WHITESPACE_MARKER = "\u2581"


def _text(value: Any, label: str = "text") -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be str")
    for i, ch in enumerate(value):
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise ValueError(f"{label} contains lone surrogate U+{cp:04X} at index {i}")
    return value


def _sequence(value: Any, label: str) -> Sequence:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, (list, tuple)):
        raise TypeError(f"{label} must be a list or tuple")
    return value


def validate_ids(ids: Any, vocab_size: int, *, allow_structural: bool = False) -> list[int]:
    seq = _sequence(ids, "ids")
    out: list[int] = []
    for i, token_id in enumerate(seq):
        if isinstance(token_id, bool) or not isinstance(token_id, int):
            raise TypeError(f"ids[{i}] must be an integer; bool is not accepted")
        if token_id < 0 or token_id >= vocab_size:
            raise ValueError(f"ids[{i}]={token_id} is outside [0, {vocab_size})")
        if not allow_structural and token_id < STRUCTURAL_COUNT:
            raise ValueError(f"ids[{i}] is reserved structural ID {token_id}")
        out.append(token_id)
    return out


def escape_text(value: str, normalization: str = "NFC") -> str:
    value = _text(value)
    if normalization == "NFC":
        value = unicodedata2.normalize("NFC", value)
    elif normalization != "exact":
        raise ValueError("normalization must be 'NFC' or 'exact'")

    out: list[str] = []
    spellings = sorted(STRUCTURAL_TOKENS, key=len, reverse=True)
    i = 0
    while i < len(value):
        if value.startswith(ESCAPE_SENTINEL, i):
            out.append(ESCAPE_SENTINEL * 2)
            i += 1
            continue
        if value.startswith(WHITESPACE_MARKER, i):
            out.append(ESCAPE_SENTINEL + "W;")
            i += 1
            continue
        match = next((s for s in spellings if value.startswith(s, i)), None)
        if match is not None:
            out.append(f"{ESCAPE_SENTINEL}S{STRUCTURAL_TO_ID[match]:02d};")
            i += len(match)
            continue
        out.append(value[i])
        i += 1
    return "".join(out)


def unescape_text(value: str) -> str:
    value = _text(value, "decoded text")
    out: list[str] = []
    i = 0
    while i < len(value):
        if value[i] != ESCAPE_SENTINEL:
            out.append(value[i])
            i += 1
            continue
        i += 1
        if i >= len(value):
            raise ValueError("truncated escape sentinel")
        if value[i] == ESCAPE_SENTINEL:
            out.append(ESCAPE_SENTINEL)
            i += 1
            continue
        if value.startswith("W;", i):
            out.append(WHITESPACE_MARKER)
            i += 2
            continue
        if (
            i + 4 <= len(value)
            and value[i] == "S"
            and value[i + 1] in "0123456789"
            and value[i + 2] in "0123456789"
            and value[i + 3] == ";"
        ):
            token_id = int(value[i + 1:i + 3])
            if token_id in ID_TO_STRUCTURAL:
                out.append(STRUCTURAL_TOKENS[token_id])
                i += 4
                continue
        raise ValueError("malformed, unknown, or noncanonical escape sequence")
    return "".join(out)


class _Backend:
    name = "abstract"

    def __init__(self, vocab_size: int):
        self.vocab_size = vocab_size

    def encode_raw_text(self, text: str) -> list[int]:
        raise NotImplementedError

    def decode_raw_text(self, ids: list[int]) -> str:
        raise NotImplementedError

    def byte_id_map(self) -> list[int]:
        raise NotImplementedError


class _TokenizersBackend(_Backend):
    name = "candidate_a_bytelevel_bpe"

    def __init__(self, tokenizer: Any):
        self.tokenizer = tokenizer
        super().__init__(int(tokenizer.get_vocab_size()))

    def encode_raw_text(self, text: str) -> list[int]:
        return list(self.tokenizer.encode(text).ids)

    def decode_raw_text(self, ids: list[int]) -> str:
        return self.tokenizer.decode(ids, skip_special_tokens=False)

    def byte_id_map(self) -> list[int]:
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
        result = []
        for b in range(256):
            token_id = self.tokenizer.token_to_id(byte_encoder[b])
            if token_id is None:
                raise ValueError(f"Candidate A missing ByteLevel byte token 0x{b:02X}")
            result.append(int(token_id))
        return result


class _SentencePieceBackend(_Backend):
    name = "candidate_b_sentencepiece_unigram"

    def __init__(self, processor: Any):
        self.processor = processor
        super().__init__(int(processor.get_piece_size()))

    def encode_raw_text(self, text: str) -> list[int]:
        return list(self.processor.encode(text, out_type=int))

    def decode_raw_text(self, ids: list[int]) -> str:
        return self.processor.decode(ids)

    def byte_id_map(self) -> list[int]:
        result = []
        for b in range(256):
            piece = f"<0x{b:02X}>"
            token_id = int(self.processor.piece_to_id(piece))
            if token_id < 0 or self.processor.id_to_piece(token_id) != piece:
                raise ValueError(f"Candidate B missing byte-fallback piece {piece}")
            result.append(token_id)
        return result


def _validate_artifact(backend: _Backend) -> None:
    if backend.vocab_size != VOCAB_SIZE:
        raise ValueError(
            f"Expected vocabulary size {VOCAB_SIZE}, got {backend.vocab_size}"
        )

    if isinstance(backend, _TokenizersBackend):
        for expected, spelling in enumerate(STRUCTURAL_TOKENS):
            actual = backend.tokenizer.token_to_id(spelling)
            if actual != expected:
                raise ValueError(
                    f"Candidate A token {spelling!r}: expected ID {expected}, got {actual}"
                )

    elif isinstance(backend, _SentencePieceBackend):
        for expected, spelling in enumerate(STRUCTURAL_TOKENS):
            actual = backend.processor.id_to_piece(expected)
            if actual != spelling:
                raise ValueError(
                    f"Candidate B ID {expected}: expected {spelling!r}, got {actual!r}"
                )


@dataclass
class StrictTokenizer:
    backend: _Backend
    normalization: str = "NFC"

    def __post_init__(self) -> None:
        if self.normalization not in ("NFC", "exact"):
            raise ValueError("normalization must be 'NFC' or 'exact'")

    @property
    def vocab_size(self) -> int:
        return self.backend.vocab_size

    @property
    def candidate(self) -> str:
        return self.backend.name

    def encode_content(self, text: str) -> list[int]:
        escaped = escape_text(_text(text), self.normalization)
        return validate_ids(self.backend.encode_raw_text(escaped), self.vocab_size)

    def decode_content(self, ids: Sequence[int]) -> str:
        return unescape_text(
            self.backend.decode_raw_text(validate_ids(ids, self.vocab_size))
        )

    def encode_batch(self, texts: Sequence[str]) -> list[list[int]]:
        seq = _sequence(texts, "texts")
        for i, value in enumerate(seq):
            _text(value, f"texts[{i}]")
        return [self.encode_content(value) for value in seq]

    def decode_batch(self, batch_ids: Sequence[Sequence[int]]) -> list[str]:
        seq = _sequence(batch_ids, "batch_ids")
        rows = []
        for i, row in enumerate(seq):
            if not isinstance(row, (list, tuple)):
                raise TypeError(f"batch_ids[{i}] must be list or tuple")
            rows.append(validate_ids(row, self.vocab_size))
        return [
            unescape_text(self.backend.decode_raw_text(row))
            for row in rows
        ]

    def render_sequence(self, ids: Sequence[int]) -> str:
        validated = validate_ids(
            ids, self.vocab_size, allow_structural=True
        )
        pieces: list[str] = []
        span: list[int] = []

        def flush() -> None:
            if span:
                pieces.append(
                    unescape_text(self.backend.decode_raw_text(span[:]))
                )
                span.clear()

        for token_id in validated:
            if token_id in ID_TO_STRUCTURAL:
                flush()
                pieces.append(ID_TO_STRUCTURAL[token_id])
            else:
                span.append(token_id)
        flush()
        return "".join(pieces)

    def raw_binary_codec(self) -> "RawBinaryCodec":
        return RawBinaryCodec(self.backend.byte_id_map(), self.vocab_size)


class RawBinaryCodec:
    def __init__(self, byte_to_id: Sequence[int], vocab_size: int):
        if len(byte_to_id) != 256:
            raise ValueError("byte mapping must contain exactly 256 IDs")
        ids = validate_ids(list(byte_to_id), vocab_size)
        if len(set(ids)) != 256:
            raise ValueError("byte mapping must be one-to-one")
        self.byte_to_id = tuple(ids)
        self.id_to_byte = {
            token_id: b for b, token_id in enumerate(ids)
        }
        self.vocab_size = vocab_size

    def encode_bytes(self, data: bytes) -> list[int]:
        if not isinstance(data, bytes):
            raise TypeError("raw binary input must be bytes")
        return [self.byte_to_id[b] for b in data]

    def decode_bytes(self, ids: Sequence[int]) -> bytes:
        values = validate_ids(ids, self.vocab_size)
        out = bytearray()
        for i, token_id in enumerate(values):
            if token_id not in self.id_to_byte:
                raise ValueError(f"ids[{i}] is not a raw-byte token")
            out.append(self.id_to_byte[token_id])
        return bytes(out)


def load_candidate_a(path: str, normalization: str = "NFC") -> StrictTokenizer:
    from tokenizers import Tokenizer

    backend = _TokenizersBackend(Tokenizer.from_file(path))
    validate_candidate_a_config(backend.tokenizer)
    _validate_artifact(backend)
    wrapper = StrictTokenizer(backend, normalization)
    RawBinaryCodec(backend.byte_id_map(), backend.vocab_size)
    return wrapper


def load_candidate_b(path: str, normalization: str = "NFC") -> StrictTokenizer:
    import sentencepiece as spm

    processor = spm.SentencePieceProcessor(model_file=path)
    backend = _SentencePieceBackend(processor)
    validate_candidate_b_config(processor)
    _validate_artifact(backend)
    wrapper = StrictTokenizer(backend, normalization)
    RawBinaryCodec(backend.byte_id_map(), backend.vocab_size)
    return wrapper


def unicode_runtime_version() -> str:
    return unicodedata2.unidata_version
