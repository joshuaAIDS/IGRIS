"""
IGRIS v2.2.28 — Candidate B configuration review scaffold
Status: REVIEW ONLY / NOT PRODUCTION INTEGRATED

This file records the approved SentencePiece Unigram configuration.
It does not read a corpus, train a tokenizer, download data, install packages,
or modify the IGRIS repository.
"""

from dataclasses import dataclass
from typing import Final

EXPECTED_SENTENCEPIECE_VERSION: Final[str] = "0.2.3"
VOCAB_SIZE: Final[int] = 32_768

STRUCTURAL_TOKENS: Final[tuple[str, ...]] = (
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

STRUCTURAL_TOKEN_IDS: Final[dict[str, int]] = {
    token: token_id for token_id, token in enumerate(STRUCTURAL_TOKENS)
}

# SentencePiece special-token IDs:
PAD_ID: Final[int] = 0
UNK_ID: Final[int] = -1
BOS_ID: Final[int] = -1
EOS_ID: Final[int] = -1

# SentencePiece training options. NFC and literal structural-token escaping
# are handled by the shared ingestion wrapper, not by SentencePiece.
SENTENCEPIECE_TRAINING_OPTIONS: Final[dict[str, object]] = {
    "model_type": "unigram",
    "vocab_size": VOCAB_SIZE,
    "character_coverage": 1.0,
    "byte_fallback": True,
    "normalization_rule_name": "identity",
    "add_dummy_prefix": False,
    "remove_extra_whitespaces": False,
    "escape_whitespaces": True,
    "pad_id": PAD_ID,
    "unk_id": UNK_ID,
    "bos_id": BOS_ID,
    "eos_id": EOS_ID,
    "pad_piece": "<|pad|>",
    "user_defined_symbols": list(STRUCTURAL_TOKENS[1:]),
}


@dataclass(frozen=True)
class CandidateBReview:
    """Declarative review record; not a trainer or production tokenizer."""

    candidate: str = "B"
    algorithm: str = "SentencePiece Unigram"
    sentencepiece_version: str = EXPECTED_SENTENCEPIECE_VERSION
    vocab_size: int = VOCAB_SIZE
    byte_fallback: bool = True
    structural_token_count: int = len(STRUCTURAL_TOKENS)
    structural_ids_fixed: bool = True
    corpus_training_authorized: bool = False
    production_integration_complete: bool = False


def validate_static_contract() -> None:
    """Validate only static configuration invariants."""
    assert len(STRUCTURAL_TOKENS) == 12
    assert len(set(STRUCTURAL_TOKENS)) == 12
    assert STRUCTURAL_TOKEN_IDS["<|pad|>"] == 0
    assert tuple(STRUCTURAL_TOKEN_IDS.values()) == tuple(range(12))
    assert SENTENCEPIECE_TRAINING_OPTIONS["model_type"] == "unigram"
    assert SENTENCEPIECE_TRAINING_OPTIONS["vocab_size"] == 32_768
    assert SENTENCEPIECE_TRAINING_OPTIONS["byte_fallback"] is True
    assert SENTENCEPIECE_TRAINING_OPTIONS["normalization_rule_name"] == "identity"
    assert SENTENCEPIECE_TRAINING_OPTIONS["add_dummy_prefix"] is False
    assert SENTENCEPIECE_TRAINING_OPTIONS["remove_extra_whitespaces"] is False
    assert SENTENCEPIECE_TRAINING_OPTIONS["escape_whitespaces"] is True
    assert SENTENCEPIECE_TRAINING_OPTIONS["pad_id"] == 0
    assert SENTENCEPIECE_TRAINING_OPTIONS["unk_id"] == -1
    assert SENTENCEPIECE_TRAINING_OPTIONS["bos_id"] == -1
    assert SENTENCEPIECE_TRAINING_OPTIONS["eos_id"] == -1


if __name__ == "__main__":
    validate_static_contract()
    print("Candidate B static configuration: PASS")
    print("Training: NOT RUN")
    print("Production integration: NOT COMPLETE")
