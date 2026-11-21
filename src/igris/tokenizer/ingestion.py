"""Shared ingestion API. Framing is explicit and opt-in, never automatic."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Sequence
from .strict import StrictTokenizer, RawBinaryCodec, validate_ids, VOCAB_SIZE

Mode = Literal["text_mode", "exact_unicode_mode", "raw_binary_mode"]
PAD_ID, BOS_ID, EOS_ID = 0, 1, 2

@dataclass(frozen=True)
class SequencePolicy:
    add_bos: bool = False
    add_eos: bool = False
    bos_id: int = BOS_ID
    eos_id: int = EOS_ID

@dataclass(frozen=True)
class EncodedInput:
    mode: Mode
    content_ids: tuple[int, ...]
    sequence_ids: tuple[int, ...]
    normalized_text: str | None

def apply_framing(content_ids: Sequence[int], policy: SequencePolicy = SequencePolicy(), vocab_size: int = VOCAB_SIZE) -> list[int]:
    ids = validate_ids(content_ids, vocab_size)
    for name, token_id in (("bos_id", policy.bos_id), ("eos_id", policy.eos_id)):
        if isinstance(token_id, bool) or not isinstance(token_id, int) or token_id < 0 or token_id >= vocab_size:
            raise ValueError(f"Invalid {name}")
    if policy.add_bos and policy.bos_id in ids: raise ValueError("Content already contains BOS ID")
    if policy.add_eos and policy.eos_id in ids: raise ValueError("Content already contains EOS ID")
    if policy.add_bos: ids.insert(0, policy.bos_id)
    if policy.add_eos: ids.append(policy.eos_id)
    return ids

def strip_framing(sequence_ids: Sequence[int], policy: SequencePolicy = SequencePolicy(), vocab_size: int = VOCAB_SIZE) -> list[int]:
    seq = sequence_ids
    if isinstance(seq, (str, bytes, bytearray)) or not isinstance(seq, (list, tuple)):
        raise TypeError("sequence_ids must be list or tuple")
    ids = []
    for i, x in enumerate(seq):
        if isinstance(x, bool) or not isinstance(x, int): raise TypeError(f"sequence_ids[{i}] must be int")
        if x < 0 or x >= vocab_size: raise ValueError(f"sequence_ids[{i}] out of range")
        ids.append(x)
    if policy.add_bos:
        if not ids or ids[0] != policy.bos_id: raise ValueError("Missing or misplaced BOS")
        ids = ids[1:]
    if policy.add_eos:
        if not ids or ids[-1] != policy.eos_id: raise ValueError("Missing or misplaced EOS")
        ids = ids[:-1]
    return validate_ids(ids, vocab_size)

def encode_text(tokenizer: StrictTokenizer, text: str, *, mode: Literal["text_mode", "exact_unicode_mode"] = "text_mode", framing: SequencePolicy = SequencePolicy()) -> EncodedInput:
    if mode not in ("text_mode", "exact_unicode_mode"): raise ValueError("Unsupported text mode")
    ids = tokenizer.encode_content(text) if mode == "text_mode" else StrictTokenizer(tokenizer.backend, "exact").encode_content(text)
    return EncodedInput(mode, tuple(ids), tuple(apply_framing(ids, framing, tokenizer.vocab_size)), text if mode == "exact_unicode_mode" else __import__("unicodedata2").normalize("NFC", text))

def encode_raw_binary(payload: bytes, codec: RawBinaryCodec, *, framing: SequencePolicy = SequencePolicy()) -> EncodedInput:
    ids = codec.encode_bytes(payload)
    return EncodedInput("raw_binary_mode", tuple(ids), tuple(apply_framing(ids, framing, codec.vocab_size)), None)

def decode_raw_binary(content_ids: Sequence[int], codec: RawBinaryCodec) -> bytes:
    return codec.decode_bytes(content_ids)

def decode_text(tokenizer: StrictTokenizer, content_ids: Sequence[int]) -> str:
    return tokenizer.decode_content(content_ids)
