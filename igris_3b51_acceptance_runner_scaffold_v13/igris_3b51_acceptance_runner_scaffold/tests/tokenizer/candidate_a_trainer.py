"""Explicit, local-only trainer for IGRIS Candidate A (ByteLevel BPE).

This module never downloads data or installs dependencies. The caller must supply
UTF-8 corpus files that have already been prepared according to the approved
IGRIS text-normalization and sentinel-escaping pipeline.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .acceptance_config import STRUCTURAL_TOKENS, VOCAB_SIZE


def _validate_corpus_files(corpus_files: Iterable[str | Path]) -> list[Path]:
    paths = [Path(p).expanduser().resolve() for p in corpus_files]
    if not paths:
        raise ValueError("at least one explicit corpus file is required")
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"corpus file does not exist: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"corpus file is empty: {path}")
        # Validate UTF-8 without modifying or rewriting the user's corpus.
        with path.open("r", encoding="utf-8", errors="strict", newline="") as stream:
            for _ in stream:
                pass
    return paths


def train_candidate_a(
    corpus_files: Iterable[str | Path],
    output_dir: str | Path,
    *,
    vocab_size: int = VOCAB_SIZE,
) -> Path:
    """Train Candidate A and return its tokenizer.json path.

    No output is written until the corpus paths and dependency are validated.
    Existing output directories are not deleted; tokenizer.json is overwritten
    only if the caller explicitly targets an existing output directory.
    """
    if type(vocab_size) is not int or vocab_size != VOCAB_SIZE:
        raise ValueError(f"IGRIS requires vocab_size={VOCAB_SIZE}")
    paths = _validate_corpus_files(corpus_files)

    try:
        from tokenizers import AddedToken, Tokenizer, decoders, models, pre_tokenizers, trainers
    except ImportError as exc:
        raise RuntimeError(
            "Candidate A requires the already-approved tokenizers==0.23.3; "
            "this trainer will not install it."
        ) from exc

    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    backend_path = output / "tokenizer.json"

    tokenizer = Tokenizer(models.BPE(unk_token=None))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(
        add_prefix_space=False, use_regex=True
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
        vocab_size=VOCAB_SIZE,
        min_frequency=2,
        show_progress=False,
        special_tokens=special_tokens,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
    )
    tokenizer.train([str(p) for p in paths], trainer)
    actual_size = tokenizer.get_vocab_size(with_added_tokens=True)
    if actual_size != VOCAB_SIZE:
        raise RuntimeError(
            f"Candidate A trained vocabulary is {actual_size}, expected exactly {VOCAB_SIZE}. "
            "Use a sufficiently representative approved corpus; do not weaken the limit."
        )
    for expected_id, token in enumerate(STRUCTURAL_TOKENS):
        actual_id = tokenizer.token_to_id(token)
        if actual_id != expected_id:
            raise RuntimeError(
                f"Candidate A structural ID mismatch for {token!r}: "
                f"expected {expected_id}, got {actual_id}"
            )
    tokenizer.save(str(backend_path))
    return backend_path
