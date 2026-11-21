"""Pure validation of the frozen IGRIS Candidate A/B training configuration.

This module does not train tokenizers, read corpora, create output directories,
download data, or install dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Mapping, Any

from .acceptance_config import VOCAB_SIZE, STRUCTURAL_TOKENS, UNICODE_VERSION


@dataclass(frozen=True)
class TrainingConfig:
    candidate: str
    algorithm: str
    vocab_size: int
    structural_tokens: tuple[str, ...]
    normalization: str
    byte_fallback: bool | None
    deterministic_settings: tuple[tuple[str, Any], ...]
    backend_filename: str


CANDIDATE_A_CONFIG = TrainingConfig(
    candidate="A",
    algorithm="ByteLevel BPE",
    vocab_size=VOCAB_SIZE,
    structural_tokens=STRUCTURAL_TOKENS,
    normalization=f"NFC before sentinel escaping; Unicode {UNICODE_VERSION}",
    byte_fallback=None,  # ByteLevel initial alphabet supplies all 256 byte symbols.
    deterministic_settings=(
        ("input_file_order", "preserved"),
        ("trainer_min_frequency", 2),
        ("show_progress", False),
        ("initial_alphabet", "ByteLevel.alphabet()"),
        ("seed_control", "not exposed by the current trainer API"),
    ),
    backend_filename="tokenizer.json",
)

CANDIDATE_B_CONFIG = TrainingConfig(
    candidate="B",
    algorithm="SentencePiece Unigram",
    vocab_size=VOCAB_SIZE,
    structural_tokens=STRUCTURAL_TOKENS,
    normalization="identity (corpus must already follow approved NFC preparation)",
    byte_fallback=True,
    deterministic_settings=(
        ("input_file_order", "preserved"),
        ("shuffle_input_sentence", False),
        ("num_threads", 1),
        ("input_sentence_size", 0),
        ("hard_vocab_limit", True),
    ),
    backend_filename="tokenizer.model",
)


def validate_training_config(config: TrainingConfig, candidate: str) -> list[str]:
    """Return a list of validation errors; empty means config contract passes."""
    errors: list[str] = []
    if candidate not in ("A", "B"):
        return ["candidate must be 'A' or 'B'"]
    expected = CANDIDATE_A_CONFIG if candidate == "A" else CANDIDATE_B_CONFIG
    if not isinstance(config, TrainingConfig):
        return ["config must be a TrainingConfig"]
    if config.candidate != expected.candidate:
        errors.append("candidate identity mismatch")
    if config.algorithm != expected.algorithm:
        errors.append("algorithm mismatch")
    if type(config.vocab_size) is not int or config.vocab_size != VOCAB_SIZE:
        errors.append(f"vocab_size must be exactly {VOCAB_SIZE}")
    if config.structural_tokens != STRUCTURAL_TOKENS:
        errors.append("structural token sequence/order mismatch")
    if config.backend_filename != expected.backend_filename:
        errors.append("backend filename mismatch")
    if config.normalization != expected.normalization:
        errors.append("normalization contract mismatch")
    if config.byte_fallback is not expected.byte_fallback:
        errors.append("byte fallback setting mismatch")
    if config.deterministic_settings != expected.deterministic_settings:
        errors.append("determinism settings differ from reviewed baseline")
    return errors


def corpus_fingerprints(paths: Iterable[str | Path]) -> tuple[tuple[str, str, int], ...]:
    """Hash the same ordered corpus inputs for fair A/B comparison.

    Returns (absolute_path, sha256_hex, byte_count) tuples. Reads only.
    """
    resolved = [Path(p).expanduser().resolve() for p in paths]
    if not resolved:
        raise ValueError("at least one corpus file is required")
    if len(set(resolved)) != len(resolved):
        raise ValueError("duplicate corpus path supplied")
    records = []
    for path in resolved:
        if not path.is_file():
            raise FileNotFoundError(str(path))
        digest = sha256()
        size = 0
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        if size == 0:
            raise ValueError(f"empty corpus file: {path}")
        records.append((str(path), digest.hexdigest(), size))
    return tuple(records)


def validate_fair_comparison(
    candidate_a_inputs: Iterable[str | Path],
    candidate_b_inputs: Iterable[str | Path],
) -> tuple[bool, str]:
    """Require identical ordered files and content hashes for A and B."""
    a = corpus_fingerprints(candidate_a_inputs)
    b = corpus_fingerprints(candidate_b_inputs)
    if a != b:
        return False, "Candidate A/B corpus paths, order, sizes, or SHA-256 hashes differ"
    return True, "Both candidates use identical ordered corpus files and content"
