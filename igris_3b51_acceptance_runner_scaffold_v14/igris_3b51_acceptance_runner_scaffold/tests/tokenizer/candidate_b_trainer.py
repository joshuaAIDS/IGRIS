"""Explicit, local-only trainer for IGRIS Candidate B (SentencePiece Unigram).

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
        if "," in str(path):
            raise ValueError(
                "SentencePiece input paths cannot contain commas because its trainer "
                "accepts a comma-separated input list."
            )
        if not path.is_file():
            raise FileNotFoundError(f"corpus file does not exist: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"corpus file is empty: {path}")
        with path.open("r", encoding="utf-8", errors="strict", newline="") as stream:
            for _ in stream:
                pass
    return paths


def train_candidate_b(
    corpus_files: Iterable[str | Path],
    output_dir: str | Path,
    *,
    vocab_size: int = VOCAB_SIZE,
) -> Path:
    """Train Candidate B and return its tokenizer.model path."""
    if type(vocab_size) is not int or vocab_size != VOCAB_SIZE:
        raise ValueError(f"IGRIS requires vocab_size={VOCAB_SIZE}")
    paths = _validate_corpus_files(corpus_files)

    try:
        import sentencepiece as spm
    except ImportError as exc:
        raise RuntimeError(
            "Candidate B requires the already-approved sentencepiece==0.2.3; "
            "this trainer will not install it."
        ) from exc

    output = Path(output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    prefix = output / "tokenizer"

    # SentencePiece places PAD at 0. With UNK/BOS/EOS disabled, the ordered
    # user-defined symbols occupy IDs 1..11, as required by the contract.
    spm.SentencePieceTrainer.train(
        input=",".join(str(p) for p in paths),
        model_prefix=str(prefix),
        model_type="unigram",
        vocab_size=VOCAB_SIZE,
        hard_vocab_limit=True,
        character_coverage=1.0,
        input_sentence_size=0,
        shuffle_input_sentence=False,
        num_threads=1,
        max_sentence_length=16384,
        normalization_rule_name="identity",
        add_dummy_prefix=False,
        remove_extra_whitespaces=False,
        escape_whitespaces=True,
        byte_fallback=True,
        unk_id=-1,
        bos_id=-1,
        eos_id=-1,
        pad_id=0,
        pad_piece=STRUCTURAL_TOKENS[0],
        user_defined_symbols=list(STRUCTURAL_TOKENS[1:]),
    )

    backend_path = prefix.with_suffix(".model")
    if not backend_path.is_file() or backend_path.stat().st_size == 0:
        raise RuntimeError("SentencePiece did not produce a non-empty tokenizer.model")

    processor = spm.SentencePieceProcessor(model_file=str(backend_path))
    actual_size = processor.get_piece_size()
    if actual_size != VOCAB_SIZE:
        raise RuntimeError(
            f"Candidate B trained vocabulary is {actual_size}, expected exactly {VOCAB_SIZE}. "
            "Use a sufficiently representative approved corpus; do not weaken the limit."
        )
    for expected_id, token in enumerate(STRUCTURAL_TOKENS):
        actual_id = processor.piece_to_id(token)
        actual_piece = processor.id_to_piece(expected_id)
        if actual_id != expected_id or actual_piece != token:
            raise RuntimeError(
                f"Candidate B structural ID mismatch for {token!r}: "
                f"expected {expected_id}, piece_to_id={actual_id}, id_to_piece={actual_piece!r}"
            )
    return backend_path
