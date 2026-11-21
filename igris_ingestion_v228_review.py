"""
IGRIS v2.2.28 reference module: strict shared ingestion and raw-byte codec.
Review copy only; this does not modify the user's repository.
"""
from dataclasses import dataclass
from typing import Iterable, Literal, Protocol, Sequence

try:
    import unicodedata2 as unicode_data
except ImportError as exc:
    raise RuntimeError("Requires unicodedata2==15.1.0") from exc
if unicode_data.unidata_version != "15.1.0":
    raise RuntimeError(f"Requires Unicode 15.1.0; found {unicode_data.unidata_version}")

Mode = Literal["text_mode", "exact_unicode_mode", "raw_binary_mode"]
PAD_ID, BOS_ID, EOS_ID = 0, 1, 2
STRUCTURAL_TOKENS = {
    0: "<|pad|>", 1: "<|begin_of_text|>", 2: "<|end_of_text|>",
    3: "<think>", 4: "</think>", 5: "<action>", 6: "</action>",
    7: "<action_result>", 8: "</action_result>",
    9: "<|system|>", 10: "<|user|>", 11: "<|assistant|>",
}
STRUCTURAL_ID_LIMIT = 12


class ContentTokenizer(Protocol):
    def encode_content(self, text: str) -> list[int]: ...
    def decode_content(self, ids: Sequence[int]) -> str: ...
    def get_vocab_size(self) -> int: ...


def _plain_int(value: object, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer; bool is not accepted")
    return value


def _vocab_size(value: object) -> int:
    size = _plain_int(value, "vocab_size")
    if size <= STRUCTURAL_ID_LIMIT:
        raise ValueError("vocab_size must be greater than 12")
    return size


def _content_ids(ids: Sequence[int], size: int, label: str = "content IDs") -> list[int]:
    if isinstance(ids, (str, bytes, bytearray)):
        raise TypeError(f"{label} must be a sequence of integer IDs")
    try:
        result = list(ids)
    except TypeError as exc:
        raise TypeError(f"{label} must be iterable") from exc
    for i, token_id in enumerate(result):
        if type(token_id) is not int:
            raise TypeError(f"{label}[{i}] must be an integer")
        if token_id < STRUCTURAL_ID_LIMIT:
            raise ValueError(f"{label}[{i}]={token_id} is a structural ID")
        if token_id >= size:
            raise ValueError(f"{label}[{i}]={token_id} outside vocabulary size {size}")
    return result


def _sequence_ids(ids: Sequence[int], size: int) -> list[int]:
    if isinstance(ids, (str, bytes, bytearray)):
        raise TypeError("sequence_ids must be a sequence of integer IDs")
    try:
        result = list(ids)
    except TypeError as exc:
        raise TypeError("sequence_ids must be iterable") from exc
    for i, token_id in enumerate(result):
        if type(token_id) is not int:
            raise TypeError(f"sequence_ids[{i}] must be an integer")
        if not 0 <= token_id < size:
            raise ValueError(f"sequence_ids[{i}]={token_id} outside vocabulary range")
    return result


def _size(tokenizer: ContentTokenizer) -> int:
    getter = getattr(tokenizer, "get_vocab_size", None)
    if not callable(getter):
        raise TypeError("Tokenizer must implement get_vocab_size()")
    return _vocab_size(getter())


def _validate_scalars(text: str) -> None:
    for i, char in enumerate(text):
        cp = ord(char)
        if 0xD800 <= cp <= 0xDFFF:
            raise ValueError(f"Lone surrogate U+{cp:04X} at character index {i}")


@dataclass(frozen=True)
class SequencePolicy:
    # Public encode APIs add no framing unless explicitly requested.
    add_bos: bool = False
    add_eos: bool = False
    bos_id: int = BOS_ID
    eos_id: int = EOS_ID

    def __post_init__(self):
        if type(self.add_bos) is not bool or type(self.add_eos) is not bool:
            raise TypeError("add_bos and add_eos must be bool")
        if _plain_int(self.bos_id, "bos_id") != BOS_ID:
            raise ValueError("BOS ID is fixed at 1")
        if _plain_int(self.eos_id, "eos_id") != EOS_ID:
            raise ValueError("EOS ID is fixed at 2")


@dataclass(frozen=True)
class EncodedInput:
    mode: Mode
    content_ids: tuple[int, ...]
    sequence_ids: tuple[int, ...]
    normalized_text: str | None


def normalize_text(text: str, mode: Literal["text_mode", "exact_unicode_mode"]) -> str:
    if not isinstance(text, str):
        raise TypeError("Expected str input")
    _validate_scalars(text)
    if mode == "text_mode":
        return unicode_data.normalize("NFC", text)
    if mode == "exact_unicode_mode":
        return text
    raise ValueError(f"Unsupported text mode: {mode}")


def apply_framing(content_ids: Sequence[int], policy: SequencePolicy, *,
                  vocab_size: int) -> list[int]:
    if not isinstance(policy, SequencePolicy):
        raise TypeError("policy must be SequencePolicy")
    ids = _content_ids(content_ids, _vocab_size(vocab_size))
    if policy.add_bos:
        ids.insert(0, policy.bos_id)
    if policy.add_eos:
        ids.append(policy.eos_id)
    return ids


def encode_text(tokenizer: ContentTokenizer, text: str, *,
                mode: Literal["text_mode", "exact_unicode_mode"] = "text_mode",
                framing: SequencePolicy = SequencePolicy()) -> EncodedInput:
    size = _size(tokenizer)
    normalized = normalize_text(text, mode)
    content = _content_ids(tokenizer.encode_content(normalized), size, "encoder output")
    sequence = apply_framing(content, framing, vocab_size=size)
    return EncodedInput(mode, tuple(content), tuple(sequence), normalized)


def decode_text(tokenizer: ContentTokenizer, content_ids: Sequence[int]) -> str:
    """Content-only decoding; rejects every structural token ID."""
    ids = _content_ids(content_ids, _size(tokenizer))
    text = tokenizer.decode_content(ids)
    if not isinstance(text, str):
        raise TypeError("decode_content() must return str")
    _validate_scalars(text)
    return text


def strip_framing(sequence_ids: Sequence[int], policy: SequencePolicy, *,
                  vocab_size: int) -> list[int]:
    if not isinstance(policy, SequencePolicy):
        raise TypeError("policy must be SequencePolicy")
    ids = _sequence_ids(sequence_ids, _vocab_size(vocab_size))
    if policy.add_bos:
        if not ids or ids[0] != policy.bos_id:
            raise ValueError("Missing or misplaced BOS")
        ids = ids[1:]
    if policy.add_eos:
        if not ids or ids[-1] != policy.eos_id:
            raise ValueError("Missing or misplaced EOS")
        ids = ids[:-1]
    return _content_ids(ids, _vocab_size(vocab_size), "unframed content IDs")


def render_sequence(tokenizer: ContentTokenizer, sequence_ids: Sequence[int]) -> str:
    """Render structural spellings; decode each maximal content span independently."""
    ids = _sequence_ids(sequence_ids, _size(tokenizer))
    output: list[str] = []
    span: list[int] = []

    def flush():
        if span:
            text = tokenizer.decode_content(span)
            if not isinstance(text, str):
                raise TypeError("decode_content() must return str")
            _validate_scalars(text)
            output.append(text)
            span.clear()

    for token_id in ids:
        if token_id in STRUCTURAL_TOKENS:
            flush()
            output.append(STRUCTURAL_TOKENS[token_id])
        else:
            span.append(token_id)
    flush()
    return "".join(output)


@dataclass(frozen=True)
class ByteTokenCodec:
    byte_to_id: dict[int, int]
    vocab_size: int | None = None

    def __post_init__(self):
        if not isinstance(self.byte_to_id, dict):
            raise TypeError("byte_to_id must be a dict")
        mapping = dict(self.byte_to_id)
        if any(type(k) is not int for k in mapping):
            raise TypeError("Byte mapping keys must be plain integers")
        if set(mapping) != set(range(256)):
            raise ValueError("byte_to_id must contain exactly keys 0..255")
        values = list(mapping.values())
        if any(type(v) is not int for v in values):
            raise TypeError("Byte token IDs must be plain integers")
        if any(v < STRUCTURAL_ID_LIMIT for v in values):
            raise ValueError("Byte token IDs must not be structural IDs")
        if len(set(values)) != 256:
            raise ValueError("Every byte must map to a unique token ID")
        if self.vocab_size is not None:
            size = _vocab_size(self.vocab_size)
            if any(v >= size for v in values):
                raise ValueError("Byte token ID outside vocabulary range")
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
        for i, token_id in enumerate(token_ids):
            if type(token_id) is not int or token_id not in reverse:
                raise ValueError(f"Invalid byte token ID at index {i}: {token_id!r}")
            result.append(reverse[token_id])
        return bytes(result)


def encode_raw_binary(payload: bytes, codec: ByteTokenCodec, *,
                      framing: SequencePolicy = SequencePolicy()) -> EncodedInput:
    if not isinstance(framing, SequencePolicy):
        raise TypeError("framing must be SequencePolicy")
    content = codec.encode(payload)
    if codec.vocab_size is not None:
        sequence = apply_framing(content, framing, vocab_size=codec.vocab_size)
    else:
        sequence = list(content)
        if framing.add_bos:
            sequence.insert(0, BOS_ID)
        if framing.add_eos:
            sequence.append(EOS_ID)
    return EncodedInput("raw_binary_mode", tuple(content), tuple(sequence), None)


def decode_raw_binary(content_ids: Sequence[int], codec: ByteTokenCodec) -> bytes:
    return codec.decode(content_ids)


def self_test() -> dict[str, str]:
    class Echo:
        def get_vocab_size(self): return 4096
        def encode_content(self, text): return [12 + b for b in text.encode("utf-8")]
        def decode_content(self, ids):
            return bytes(i - 12 for i in ids).decode("utf-8", errors="strict")

    tokenizer = Echo()
    nfc = encode_text(tokenizer, "e\u0301")
    exact = encode_text(tokenizer, "e\u0301", mode="exact_unicode_mode")
    assert nfc.normalized_text == "\u00e9"
    assert exact.normalized_text == "e\u0301"
    assert nfc.content_ids != exact.content_ids
    assert decode_text(tokenizer, nfc.content_ids) == "\u00e9"

    codec = ByteTokenCodec({b: 1000 + b for b in range(256)}, vocab_size=4096)
    payload = bytes(range(256))
    assert codec.decode(codec.encode(payload)) == payload
    binary = b"\xff\xfe\x80\x00IGRIS"
    policy = SequencePolicy(True, True)
    framed = encode_raw_binary(binary, codec, framing=policy)
    body = strip_framing(framed.sequence_ids, policy, vocab_size=4096)
    assert decode_raw_binary(body, codec) == binary

    rendered = render_sequence(tokenizer, [1, 77, 9, 78, 2])
    assert rendered == "<|begin_of_text|>A<|system|>B<|end_of_text|>"

    invalid = [([True], TypeError), ([12.0], TypeError), (["12"], TypeError),
               ([-1], ValueError), ([0], ValueError), ([4096], ValueError)]
    for ids, error in invalid:
        try:
            apply_framing(ids, SequencePolicy(), vocab_size=4096)
        except error:
            pass
        else:
            raise AssertionError(f"Invalid IDs accepted: {ids!r}")
    try:
        decode_text(tokenizer, [1])
    except ValueError:
        pass
    else:
        raise AssertionError("Structural ID accepted by content decoder")
    try:
        codec.decode([True])
    except ValueError:
        pass
    else:
        raise AssertionError("Boolean byte token ID accepted")

    return {name: "PASS" for name in (
        "Unicode 15.1 NFC", "exact Unicode preservation",
        "content-only decoding", "all 256 byte values roundtrip",
        "arbitrary binary roundtrip", "explicit BOS/EOS framing",
        "trusted sequence rendering", "strict ID validation",
        "structural ID isolation",
    )}


if __name__ == "__main__":
    results = self_test()
    for name, status in results.items():
        print(f"{name}: {status}")
    print(f"TOTAL: {len(results)} self-tests passed")
