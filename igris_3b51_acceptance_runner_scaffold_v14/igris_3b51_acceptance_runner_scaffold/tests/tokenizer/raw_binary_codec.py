"""Reference raw-binary codec contract, independent of trained artifacts."""
from __future__ import annotations

from collections.abc import Sequence
from .acceptance_config import VOCAB_SIZE
from .validation import require_bytes, require_id_sequence, require_token_id


class RawBinaryCodec:
    """Map each byte to one distinct content token ID and back.

    Candidate A must supply IDs corresponding to its ByteLevel byte-to-Unicode
    alphabet mapping. Candidate B must supply IDs corresponding to its
    SentencePiece <0xXX> BYTE pieces. This helper validates the mapping shape;
    it does not inspect or build either candidate artifact.
    """

    def __init__(self, byte_to_token_id: Sequence[int]):
        if isinstance(byte_to_token_id, (str, bytes, bytearray)) or not isinstance(
            byte_to_token_id, Sequence
        ):
            raise TypeError("byte_to_token_id must be a sequence of 256 token IDs")
        if len(byte_to_token_id) != 256:
            raise ValueError("byte_to_token_id must contain exactly 256 entries")

        mapping = []
        for byte_value, token_id in enumerate(byte_to_token_id):
            try:
                mapping.append(require_token_id(token_id, content_only=True,
                                                vocab_size=VOCAB_SIZE))
            except (TypeError, ValueError) as exc:
                raise type(exc)(f"mapping for byte 0x{byte_value:02X}: {exc}") from exc

        if len(set(mapping)) != 256:
            raise ValueError("each byte must map to a unique content token ID")

        self._byte_to_id = tuple(mapping)
        self._id_to_byte = {token_id: byte_value
                            for byte_value, token_id in enumerate(mapping)}

    def encode(self, payload: bytes) -> list[int]:
        raw = require_bytes(payload, "payload")
        return [self._byte_to_id[value] for value in raw]

    def decode(self, token_ids: Sequence[int]) -> bytes:
        validated = require_id_sequence(token_ids, content_only=True,
                                         vocab_size=VOCAB_SIZE)
        output = bytearray()
        for index, token_id in enumerate(validated):
            if token_id not in self._id_to_byte:
                raise ValueError(
                    f"token_ids[{index}]={token_id} is not a raw-binary byte token"
                )
            output.append(self._id_to_byte[token_id])
        return bytes(output)
