"""
IGRIS v2.2.28 reference module: shared ingestion and strict raw-byte codec.
No tokenizer training, downloads, or repository modifications are performed.
"""
from dataclasses import dataclass
from typing import Iterable, Literal, Protocol, Sequence
import unicodedata

Mode = Literal["text_mode", "exact_unicode_mode", "raw_binary_mode"]
PAD_ID, BOS_ID, EOS_ID = 0, 1, 2


class ContentTokenizer(Protocol):
    def encode_content(self, text: str) -> list[int]: ...
    def decode_content(self, ids: Sequence[int]) -> str: ...


@dataclass(frozen=True)
class SequencePolicy:
    add_bos: bool = True
    add_eos: bool = True
    bos_id: int = BOS_ID
    eos_id: int = EOS_ID


@dataclass(frozen=True)
class EncodedInput:
    mode: Mode
    content_ids: tuple[int, ...]
    sequence_ids: tuple[int, ...]
    normalized_text: str | None


def _validate_unicode_scalars(text: str) -> None:
    for i, ch in enumerate(text):
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise ValueError(f"Lone surrogate U+{cp:04X} at character index {i}")


def normalize_text(text: str, mode: Literal["text_mode", "exact_unicode_mode"]) -> str:
    if not isinstance(text, str):
        raise TypeError("Expected str input")
    _validate_unicode_scalars(text)
    if mode == "text_mode":
        return unicodedata.normalize("NFC", text)
    if mode == "exact_unicode_mode":
        return text
    raise ValueError(f"Unsupported text mode: {mode}")


def apply_framing(content_ids: Sequence[int], policy: SequencePolicy) -> list[int]:
    ids = [int(x) for x in content_ids]
    if policy.bos_id in ids or policy.eos_id in ids:
        raise ValueError("Content encoder emitted a reserved BOS/EOS ID")
    if policy.add_bos:
        ids.insert(0, policy.bos_id)
    if policy.add_eos:
        ids.append(policy.eos_id)
    return ids


def encode_text(tokenizer: ContentTokenizer, text: str, *,
                mode: Literal["text_mode", "exact_unicode_mode"] = "text_mode",
                framing: SequencePolicy = SequencePolicy()) -> EncodedInput:
    normalized = normalize_text(text, mode)
    content = tokenizer.encode_content(normalized)
    if any(not isinstance(x, int) or x < 0 for x in content):
        raise TypeError("Tokenizer must return non-negative integer IDs")
    return EncodedInput(mode, tuple(content), tuple(apply_framing(content, framing)), normalized)


def strip_framing(sequence_ids: Sequence[int], policy: SequencePolicy) -> list[int]:
    ids = list(sequence_ids)
    if policy.add_bos:
        if not ids or ids[0] != policy.bos_id:
            raise ValueError("Missing or misplaced BOS")
        ids = ids[1:]
    if policy.add_eos:
        if not ids or ids[-1] != policy.eos_id:
            raise ValueError("Missing or misplaced EOS")
        ids = ids[:-1]
    if policy.bos_id in ids or policy.eos_id in ids:
        raise ValueError("Unexpected framing token inside content")
    return ids


@dataclass(frozen=True)
class ByteTokenCodec:
    """Exact one-to-one mapping of byte values 0..255 to tokenizer IDs."""
    byte_to_id: dict[int, int]

    def __post_init__(self):
        mapping = dict(self.byte_to_id)
        if set(mapping) != set(range(256)):
            raise ValueError("byte_to_id must contain exactly keys 0..255")
        values = list(mapping.values())
        if any(not isinstance(x, int) or x < 0 for x in values):
            raise ValueError("Byte token IDs must be non-negative integers")
        if len(set(values)) != 256:
            raise ValueError("Every byte must map to a unique token ID")
        object.__setattr__(self, "byte_to_id", mapping)

    @property
    def id_to_byte(self) -> dict[int, int]:
        return {token_id: byte for byte, token_id in self.byte_to_id.items()}

    def encode(self, payload: bytes) -> list[int]:
        if not isinstance(payload, bytes):
            raise TypeError("raw_binary_mode requires bytes")
        return [self.byte_to_id[b] for b in payload]

    def decode(self, token_ids: Iterable[int]) -> bytes:
        reverse = self.id_to_byte
        result = bytearray()
        for index, token_id in enumerate(token_ids):
            if not isinstance(token_id, int) or token_id not in reverse:
                raise ValueError(f"Invalid byte token ID at index {index}: {token_id!r}")
            result.append(reverse[token_id])
        return bytes(result)


def encode_raw_binary(payload: bytes, codec: ByteTokenCodec, *,
                      framing: SequencePolicy = SequencePolicy()) -> EncodedInput:
    content = codec.encode(payload)
    return EncodedInput("raw_binary_mode", tuple(content),
                        tuple(apply_framing(content, framing)), None)


def decode_raw_binary(content_ids: Sequence[int], codec: ByteTokenCodec) -> bytes:
    return codec.decode(content_ids)


def self_test() -> dict[str, str]:
    class Echo:
        def encode_content(self, text: str) -> list[int]:
            return list(text.encode("utf-8"))
        def decode_content(self, ids: Sequence[int]) -> str:
            return bytes(ids).decode("utf-8", errors="strict")

    echo = Echo()
    nfc = encode_text(echo, "e\u0301", mode="text_mode")
    exact = encode_text(echo, "e\u0301", mode="exact_unicode_mode")
    assert nfc.normalized_text == "\u00e9"
    assert exact.normalized_text == "e\u0301"
    assert nfc.content_ids != exact.content_ids

    codec = ByteTokenCodec({b: 1000 + b for b in range(256)})
    payload = bytes(range(256))
    assert codec.decode(codec.encode(payload)) == payload

    binary = b"\xff\xfe\x80\x00IGRIS"
    framed = encode_raw_binary(binary, codec)
    body = strip_framing(framed.sequence_ids, SequencePolicy())
    assert decode_raw_binary(body, codec) == binary

    try:
        codec.decode([999999])
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid byte token ID was not rejected")

    class Bad:
        def encode_content(self, text: str) -> list[int]:
            return [BOS_ID, 99]
        def decode_content(self, ids: Sequence[int]) -> str:
            return ""

    try:
        encode_text(Bad(), "x")
    except ValueError:
        pass
    else:
        raise AssertionError("Backend framing token was not rejected")

    return {
        "NFC normalization": "PASS",
        "exact Unicode preservation": "PASS",
        "all 256 byte values roundtrip": "PASS",
        "arbitrary binary roundtrip": "PASS",
        "invalid byte ID rejection": "PASS",
        "single-owner framing": "PASS",
    }


if __name__ == "__main__":
    results = self_test()
    for name, status in results.items():
        print(f"{name}: {status}")
    print(f"TOTAL: {len(results)} self-tests passed")
