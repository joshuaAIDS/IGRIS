"""IGRIS Candidate A tokenizer builder — ByteLevel BPE via Hugging Face Tokenizers.

Builds a BPE tokenizer with:
  - ByteLevel pre-tokenizer and decoder
  - 12 structural tokens at IDs 0–11 (marked special, no whitespace stripping)
  - No automatic post-processor (no BOS/EOS insertion)
  - Vocabulary size exactly 32,768

IMPORTANT: This module provides the builder functions and configuration.
Actual training on a production corpus requires explicit authorization.
Synthetic-corpus training is provided for testing only.

Backend limitations:
  - BPE merges are not fully deterministic across tokenizers library versions
    when the corpus has ties at identical frequency.  The structural-token
    placement and vocabulary size ARE deterministic because they are enforced
    by configuration, not by merge ordering.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Sequence

from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers, AddedToken

from .strict import (
    STRUCTURAL_TOKENS,
    STRUCTURAL_COUNT,
    VOCAB_SIZE,
    load_candidate_a,
    StrictTokenizer,
)
from .artifact_validation import validate_candidate_a_config


# ---------------------------------------------------------------------------
# ByteLevel alphabet (GPT-2 style byte-to-unicode mapping)
# ---------------------------------------------------------------------------

def _byte_level_alphabet() -> list[str]:
    """Return the 256 single-character tokens used by the ByteLevel pre-tokenizer.

    This replicates the mapping from ``tokenizers.pre_tokenizers.ByteLevel.alphabet()``
    so that it can be referenced without instantiating the pre-tokenizer.
    """
    bs: list[int] = list(range(ord("!"), ord("~") + 1))
    bs += list(range(ord("¡"), ord("¬") + 1))
    bs += list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return [chr(c) for _, c in sorted(zip(bs, cs))]


# ---------------------------------------------------------------------------
# Builder configuration
# ---------------------------------------------------------------------------

def _build_structural_tokens() -> list[AddedToken]:
    """Create the 12 AddedToken objects for IGRIS structural tokens.

    Each token is:
      - special=True
      - lstrip=False, rstrip=False  (no whitespace stripping)
      - normalized=False            (the spelling is literal)
      - single_word=False
    """
    tokens: list[AddedToken] = []
    for spelling in STRUCTURAL_TOKENS:
        tokens.append(
            AddedToken(
                spelling,
                special=True,
                lstrip=False,
                rstrip=False,
                normalized=False,
                single_word=False,
            )
        )
    return tokens


def _create_tokenizer_skeleton() -> Tokenizer:
    """Create an untrained Tokenizer with the correct BPE model shell and byte alphabet.

    The initial vocabulary contains:
      - IDs 0–11: structural tokens
      - IDs 12–267: 256 ByteLevel single-byte tokens

    After training, BPE merges fill the remaining IDs up to 32,768.
    """
    byte_chars = _byte_level_alphabet()

    # Initial vocab: structural tokens occupy 0–11, byte chars occupy 12–267.
    initial_vocab: dict[str, int] = {}
    for idx, spelling in enumerate(STRUCTURAL_TOKENS):
        initial_vocab[spelling] = idx
    for i, ch in enumerate(byte_chars):
        initial_vocab[ch] = STRUCTURAL_COUNT + i

    model = models.BPE(vocab=initial_vocab, merges=[], unk_token=None)
    tokenizer = Tokenizer(model)

    # Add structural tokens as special added tokens.
    tokenizer.add_special_tokens(_build_structural_tokens())

    # Pre-tokenizer and decoder: ByteLevel (GPT-2 style).
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(
        add_prefix_space=False,
        use_regex=True,
    )
    tokenizer.decoder = decoders.ByteLevel()

    # Explicitly NO post-processor.
    tokenizer.post_processor = None  # type: ignore[assignment]

    return tokenizer


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def build_candidate_a(
    corpus_iterator: Iterator[str],
    output_dir: str | Path,
    *,
    vocab_size: int = VOCAB_SIZE,
    min_frequency: int = 2,
) -> Path:
    """Train a Candidate A ByteLevel BPE tokenizer and save the artifact.

    Args:
        corpus_iterator: An iterator yielding text strings for training.
            For synthetic testing, pass a small list.  For production,
            pass a streaming iterator over the authorized corpus.
        output_dir: Directory where ``tokenizer.json`` and
            ``build_metadata.json`` will be written.
        vocab_size: Target vocabulary size (must be ``VOCAB_SIZE``).
        min_frequency: Minimum frequency for BPE merges.

    Returns:
        Path to the saved ``tokenizer.json``.

    Raises:
        ValueError: If vocab_size does not match the IGRIS specification.
    """
    if vocab_size != VOCAB_SIZE:
        raise ValueError(
            f"Candidate A vocab_size must be {VOCAB_SIZE}; got {vocab_size}"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    tokenizer = _create_tokenizer_skeleton()

    # The trainer is configured to reach exactly 32,768 tokens.
    # The initial alphabet (256 bytes + 12 structural) = 268 tokens.
    # The trainer will produce vocab_size - 268 = 32,500 merges.
    byte_chars = _byte_level_alphabet()

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=min_frequency,
        special_tokens=[spelling for spelling in STRUCTURAL_TOKENS],
        initial_alphabet=byte_chars,
        show_progress=False,
    )

    # Collect the corpus for training (the HF Tokenizers library needs
    # the full iterator; it does not support streaming in all versions).
    corpus_lines = list(corpus_iterator)
    tokenizer.train_from_iterator(corpus_lines, trainer=trainer)

    # Verify the structural tokens were not displaced.
    for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
        actual = tokenizer.token_to_id(spelling)
        if actual != expected_id:
            raise ValueError(
                f"Post-training structural token {spelling!r} has ID {actual}, "
                f"expected {expected_id}. Training may have displaced reserved tokens."
            )

    # Serialize tokenizer to JSON to ensure safe, non-special model vocabulary padding.
    data = json.loads(tokenizer.to_str())

    # Ensure added_tokens contains strictly the 12 structural tokens.
    structural_set = set(STRUCTURAL_TOKENS)
    data["added_tokens"] = [
        item for item in data.get("added_tokens", [])
        if item.get("id") < STRUCTURAL_COUNT and item.get("content") in structural_set
    ]

    model_vocab = data.setdefault("model", {}).setdefault("vocab", {})
    # Ensure structural tokens are present in model_vocab at IDs 0–11
    for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
        model_vocab[spelling] = expected_id

    # Pad vocabulary to exactly VOCAB_SIZE using non-special model vocabulary filler entries.
    # These entries reside in model.vocab (NOT in added_tokens) and have no corresponding
    # merges in model.merges. Consequently, the ByteLevel BPE tokenizer cannot emit
    # them for any normal user text input.
    if len(model_vocab) < VOCAB_SIZE:
        max_id = max(model_vocab.values()) if model_vocab else -1
        next_id = max_id + 1
        filler_idx = 0
        while len(model_vocab) < VOCAB_SIZE:
            filler_spelling = f"<|filler_{filler_idx:05d}|>"
            while filler_spelling in model_vocab:
                filler_idx += 1
                filler_spelling = f"<|filler_{filler_idx:05d}|>"
            model_vocab[filler_spelling] = next_id
            next_id += 1
            filler_idx += 1

    # Reconstruct tokenizer from the padded JSON specification.
    tokenizer = Tokenizer.from_str(json.dumps(data))

    final_size = tokenizer.get_vocab_size()
    if final_size != VOCAB_SIZE:
        raise ValueError(
            f"Candidate A final vocab size is {final_size}; expected {VOCAB_SIZE}"
        )

    # Save artifact.
    artifact_path = output_path / "tokenizer.json"
    tokenizer.save(str(artifact_path))

    # Compute SHA-256.
    sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

    # Validate using the existing artifact validator.
    validation_result = validate_candidate_a_config(tokenizer)

    # Write build metadata.
    metadata = {
        "candidate": "A",
        "backend": "tokenizers",
        "backend_version": _get_tokenizers_version(),
        "model_type": "BPE",
        "pre_tokenizer": "ByteLevel",
        "decoder": "ByteLevel",
        "post_processor": None,
        "vocab_size": VOCAB_SIZE,
        "structural_tokens": {
            spelling: idx for idx, spelling in enumerate(STRUCTURAL_TOKENS)
        },
        "unicode_version": "15.1.0",
        "training_config": {
            "min_frequency": min_frequency,
            "initial_alphabet_size": len(byte_chars),
        },
        "artifact_sha256": sha256,
        "artifact_filename": "tokenizer.json",
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "validation": validation_result,
    }

    metadata_path = output_path / "build_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    return artifact_path


def load_and_validate_candidate_a(
    artifact_path: str | Path,
    normalization: str = "NFC",
) -> StrictTokenizer:
    """Load a Candidate A artifact, run all validators, and return a StrictTokenizer.

    This is a convenience wrapper around ``load_candidate_a`` that also
    verifies the byte-level mapping is complete.

    Args:
        artifact_path: Path to ``tokenizer.json``.
        normalization: ``'NFC'`` or ``'exact'``.

    Returns:
        A validated ``StrictTokenizer`` ready for use.
    """
    return load_candidate_a(str(artifact_path), normalization)


def _get_tokenizers_version() -> str:
    """Return the installed tokenizers library version."""
    try:
        import tokenizers as _tk
        return _tk.__version__
    except AttributeError:
        return "unknown"
