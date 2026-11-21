"""Artifact-level configuration validators for IGRIS tokenizer candidates."""
from __future__ import annotations

import json
from typing import Any

STRUCTURAL_TOKENS = (
    "<|pad|>", "<|begin_of_text|>", "<|end_of_text|>", "<think>",
    "</think>", "<action>", "</action>", "<action_result>",
    "</action_result>", "<|system|>", "<|user|>", "<|assistant|>",
)
VOCAB_SIZE = 32768


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _node_type(node: Any) -> str | None:
    if node is None:
        return None
    if isinstance(node, dict):
        return node.get("type")
    return type(node).__name__


def validate_candidate_a_config(tokenizer: Any) -> dict:
    """Validate serialized Tokenizers JSON for the approved ByteLevel BPE setup."""
    try:
        data = json.loads(tokenizer.to_str())
    except Exception as exc:
        raise ValueError("Candidate A tokenizer serialization is not valid JSON") from exc

    model = data.get("model") or {}
    _require(model.get("type") == "BPE",
             f"Candidate A model must be BPE, got {model.get('type')!r}")

    pre = data.get("pre_tokenizer")
    dec = data.get("decoder")
    _require(_node_type(pre) == "ByteLevel",
             "Candidate A pre-tokenizer must be ByteLevel")
    _require(_node_type(dec) == "ByteLevel",
             "Candidate A decoder must be ByteLevel")
    _require(data.get("post_processor") is None,
             "Candidate A post_processor must be null; automatic framing is forbidden")

    vocab = tokenizer.get_vocab(with_added_tokens=True)
    _require(len(vocab) == VOCAB_SIZE,
             f"Candidate A full vocabulary must contain {VOCAB_SIZE} entries; got {len(vocab)}")

    added_list = data.get("added_tokens", [])
    _require(len(added_list) == len(STRUCTURAL_TOKENS),
             f"Candidate A must have exactly {len(STRUCTURAL_TOKENS)} added tokens (structural only); got {len(added_list)}")

    added = {
        item.get("content"): item
        for item in added_list
    }
    for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
        actual_id = tokenizer.token_to_id(spelling)
        _require(actual_id == expected_id,
                 f"Candidate A {spelling!r}: expected ID {expected_id}, got {actual_id!r}")
        item = added.get(spelling)
        _require(item is not None,
                 f"Candidate A structural token {spelling!r} must be an added token")
        _require(item.get("id") == expected_id,
                 f"Candidate A added token {spelling!r} has wrong ID")
        _require(item.get("special") is True,
                 f"Candidate A structural token {spelling!r} must be marked special")
        _require(item.get("lstrip") is False and item.get("rstrip") is False,
                 f"Candidate A structural token {spelling!r} must not strip whitespace")

    return {
        "candidate": "A",
        "model_type": model.get("type"),
        "pre_tokenizer": _node_type(pre),
        "decoder": _node_type(dec),
        "post_processor": None,
        "vocab_size": len(vocab),
        "structural_tokens": len(STRUCTURAL_TOKENS),
    }


def validate_candidate_b_config(processor: Any) -> dict:
    """Validate SentencePiece model proto for the approved Unigram setup."""
    try:
        from sentencepiece import sentencepiece_model_pb2
    except Exception as exc:
        raise RuntimeError(
            "sentencepiece_model_pb2 is required to validate Candidate B metadata"
        ) from exc

    proto = sentencepiece_model_pb2.ModelProto()
    proto.ParseFromString(processor.serialized_model_proto())
    spec = proto.trainer_spec
    norm = proto.normalizer_spec
    sp = sentencepiece_model_pb2.ModelProto.SentencePiece

    _require(processor.get_piece_size() == VOCAB_SIZE,
             f"Candidate B vocabulary must be {VOCAB_SIZE}; got {processor.get_piece_size()}")
    _require(spec.model_type == sentencepiece_model_pb2.TrainerSpec.UNIGRAM,
             f"Candidate B model must be Unigram; got model_type={spec.model_type}")
    _require(spec.vocab_size == VOCAB_SIZE,
             f"Candidate B trainer vocab_size must be {VOCAB_SIZE}; got {spec.vocab_size}")
    _require(bool(spec.byte_fallback),
             "Candidate B byte_fallback must be enabled")
    _require(spec.pad_id == 0, f"Candidate B PAD ID must be 0; got {spec.pad_id}")
    _require(spec.bos_id == -1, f"Candidate B BOS ID must be -1; got {spec.bos_id}")
    _require(spec.eos_id == -1, f"Candidate B EOS ID must be -1; got {spec.eos_id}")
    _require(spec.unk_id == -1, f"Candidate B UNK ID must be -1; got {spec.unk_id}")

    _require(norm.name == "identity",
             f"Candidate B normalizer must be identity; got {norm.name!r}")
    _require(norm.add_dummy_prefix is False,
             "Candidate B add_dummy_prefix must be false")
    _require(norm.remove_extra_whitespaces is False,
             "Candidate B remove_extra_whitespaces must be false")
    _require(norm.escape_whitespaces is True,
             "Candidate B escape_whitespaces must be true")

    pieces = proto.pieces
    _require(len(pieces) == VOCAB_SIZE,
             f"Candidate B model proto must contain {VOCAB_SIZE} pieces; got {len(pieces)}")

    unique_pieces = {p.piece for p in pieces}
    _require(len(unique_pieces) == VOCAB_SIZE,
             f"Candidate B model proto contains duplicate pieces ({len(unique_pieces)} unique vs {VOCAB_SIZE} total)")

    _require(pieces[0].piece == STRUCTURAL_TOKENS[0],
             "Candidate B piece 0 must be <|pad|>")
    pad_types = {getattr(sp, "PAD", sp.CONTROL), sp.CONTROL, sp.USER_DEFINED}
    _require(pieces[0].type in pad_types,
             "Candidate B piece 0 must have SentencePiece PAD or CONTROL type")

    allowed_types = {sp.CONTROL, sp.USER_DEFINED}
    for expected_id, spelling in enumerate(STRUCTURAL_TOKENS[1:], start=1):
        piece = pieces[expected_id]
        _require(piece.piece == spelling,
                 f"Candidate B piece {expected_id} must be {spelling!r}, got {piece.piece!r}")
        _require(piece.type in allowed_types,
                 f"Candidate B structural piece {spelling!r} must be CONTROL or USER_DEFINED")

    _require(processor.pad_id() == 0,
             f"Candidate B processor PAD must be 0; got {processor.pad_id()}")
    _require(processor.bos_id() == -1,
             f"Candidate B processor BOS must be disabled; got {processor.bos_id()}")
    _require(processor.eos_id() == -1,
             f"Candidate B processor EOS must be disabled; got {processor.eos_id()}")
    _require(processor.unk_id() == -1,
             f"Candidate B processor UNK must be disabled; got {processor.unk_id()}")

    # Verify all 256 byte fallback pieces exist in processor
    for b in range(256):
        byte_piece = f"<0x{b:02X}>"
        pid = processor.piece_to_id(byte_piece)
        _require(pid >= 0,
                 f"Candidate B missing byte fallback piece {byte_piece}")

    return {
        "candidate": "B",
        "model_type": "UNIGRAM",
        "byte_fallback": True,
        "normalizer": norm.name,
        "vocab_size": len(pieces),
        "structural_tokens": len(STRUCTURAL_TOKENS),
        "pad_id": spec.pad_id,
        "bos_id": spec.bos_id,
        "eos_id": spec.eos_id,
        "unk_id": spec.unk_id,
    }
