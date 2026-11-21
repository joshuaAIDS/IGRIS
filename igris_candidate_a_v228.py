"""
IGRIS v2.2.28 — Candidate A configuration scaffold.

This file configures Hugging Face Tokenizers ByteLevel BPE but DOES NOT:
- train a tokenizer,
- download or read a corpus,
- install or upgrade packages,
- save or modify project files automatically.

Run:
    python igris_candidate_a_v228.py

The checks validate configuration/API availability only. Exact vocabulary size,
token IDs, learned merges, literal-special-token behavior, save/reload fidelity,
and determinism require a trained artifact and remain unverified.
"""

from __future__ import annotations

from dataclasses import dataclass
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders
from tokenizers import AddedToken


STRUCTURAL_TOKENS = (
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

EXPECTED_STRUCTURAL_IDS = {
    token: index for index, token in enumerate(STRUCTURAL_TOKENS)
}

VOCAB_SIZE = 32_768


@dataclass(frozen=True)
class CandidateAConfig:
    vocab_size: int = VOCAB_SIZE
    min_frequency: int = 2
    show_progress: bool = False


def build_candidate_a_config(
    config: CandidateAConfig = CandidateAConfig(),
) -> tuple[Tokenizer, trainers.BpeTrainer]:
    """
    Return an untrained ByteLevel BPE tokenizer and its trainer configuration.

    The trainer's ordered special_tokens list reserves the intended structural
    token order during training. IDs are NOT claimed until a trained artifact
    is inspected.
    """
    if config.vocab_size <= len(STRUCTURAL_TOKENS):
        raise ValueError("Vocabulary size must exceed the structural token count")

    tokenizer = Tokenizer(models.BPE(unk_token=None))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(
        add_prefix_space=False,
        use_regex=True,
    )
    tokenizer.decoder = decoders.ByteLevel()

    special_tokens = [
        AddedToken(
            token,
            single_word=False,
            lstrip=False,
            rstrip=False,
            normalized=False,
            special=True,
        )
        for token in STRUCTURAL_TOKENS
    ]

    trainer = trainers.BpeTrainer(
        vocab_size=config.vocab_size,
        min_frequency=config.min_frequency,
        show_progress=config.show_progress,
        special_tokens=special_tokens,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
    )
    return tokenizer, trainer


def run_configuration_checks() -> dict[str, str]:
    tokenizer, trainer = build_candidate_a_config()

    assert isinstance(tokenizer.model, models.BPE)
    assert isinstance(tokenizer.pre_tokenizer, pre_tokenizers.ByteLevel)
    assert isinstance(tokenizer.decoder, decoders.ByteLevel)
    assert trainer.vocab_size == VOCAB_SIZE
    assert len(trainer.special_tokens) == len(STRUCTURAL_TOKENS)
    assert len(pre_tokenizers.ByteLevel.alphabet()) == 256

    # Confirm the exact declared order in the trainer configuration.
    configured_contents = [item.content for item in trainer.special_tokens]
    assert tuple(configured_contents) == STRUCTURAL_TOKENS

    # Confirm the tokenizer is still untrained: no learned vocabulary/merges
    # have been created by this configuration-only diagnostic.
    assert tokenizer.get_vocab_size() == 0

    return {
        "BPE model construction": "PASS",
        "ByteLevel pre-tokenizer": "PASS",
        "ByteLevel decoder": "PASS",
        "32,768 target configured": "PASS",
        "12 structural tokens ordered": "PASS",
        "256-byte initial alphabet configured": "PASS",
        "training not started": "PASS",
    }


if __name__ == "__main__":
    checks = run_configuration_checks()
    for label, status in checks.items():
        print(f"{label}: {status}")
    print(f"TOTAL: {len(checks)} configuration checks passed")
    print("NOTE: Candidate A is configured, not trained or accepted.")
