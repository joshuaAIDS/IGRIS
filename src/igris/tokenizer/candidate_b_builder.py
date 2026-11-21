"""IGRIS Candidate B tokenizer builder — Unigram via SentencePiece.

Builds a Unigram tokenizer with:
  - Byte fallback enabled (256 <0xXX> pieces)
  - Identity normalization (no NFKC, no dummy prefix, no extra-whitespace removal)
  - escape_whitespaces = true
  - 12 structural tokens at IDs 0–11
  - PAD ID = 0, BOS/EOS/UNK = -1  (disabled)
  - Vocabulary size exactly 32,768

IMPORTANT: SentencePiece's trainer does NOT guarantee that user-defined pieces
land at specific IDs.  The trainer inserts <unk>, byte-fallback pieces, and
user-defined pieces in its own ordering.  This builder works around that
limitation by:

  1. Training with the correct configuration.
  2. Inspecting the resulting model protobuf.
  3. Rearranging pieces in the serialized proto so that IDs 0–11 exactly
     match the IGRIS structural token specification.
  4. Re-serializing the corrected proto and saving it.

This post-training rearrangement is safe because Unigram models store
per-piece log-probabilities and the piece↔score mapping is preserved.
The model is functionally identical; only the ID assignment changes.

Backend limitations:
  - SentencePiece Unigram training is not fully deterministic across
    platforms when the corpus has frequency ties.  The structural-token
    placement IS deterministic because it is enforced by proto rewriting.
  - The ``sentencepiece_model_pb2`` protobuf module is required for
    post-training inspection and rearrangement.

Actual training on a production corpus requires explicit authorization.
Synthetic-corpus training is provided for testing only.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Sequence

import sentencepiece as spm

from .strict import (
    STRUCTURAL_TOKENS,
    STRUCTURAL_COUNT,
    VOCAB_SIZE,
    load_candidate_b,
    StrictTokenizer,
)
from .artifact_validation import validate_candidate_b_config


# ---------------------------------------------------------------------------
# Proto manipulation helpers
# ---------------------------------------------------------------------------

def _load_proto(model_path: str | Path):
    """Load a SentencePiece model file and parse the protobuf."""
    from sentencepiece import sentencepiece_model_pb2
    proto = sentencepiece_model_pb2.ModelProto()
    proto.ParseFromString(Path(model_path).read_bytes())
    return proto


def _rearrange_pieces(proto) -> None:
    """Rearrange pieces in the proto so IDs 0–11 match IGRIS structural tokens.

    Strategy:
      1. Build a map of current piece spellings → (piece_obj, current_index).
      2. Identify which pieces currently sit at IDs 0–11.
      3. Build the target ordering:
         - IDs 0–11: structural tokens (with correct type flags).
         - IDs 12+:  everything else in their original relative order,
                     excluding the structural tokens (which were moved).
      4. Replace proto.pieces with the new ordering.

    This also sets the correct SentencePiece type for each structural token:
      - ID 0 (<|pad|>): PAD type (value 6)
      - IDs 1–11: CONTROL type (value 3)

    And removes any <unk> piece that the trainer may have inserted (since
    we set unk_id = -1, there should be no UNK, but the trainer sometimes
    adds one anyway).
    """
    from sentencepiece import sentencepiece_model_pb2
    SP = sentencepiece_model_pb2.ModelProto.SentencePiece

    # Index all current pieces.
    spelling_to_piece: dict[str, Any] = {}
    ordered_non_structural: list = []
    structural_set = set(STRUCTURAL_TOKENS)

    for piece in proto.pieces:
        if piece.piece in structural_set:
            spelling_to_piece[piece.piece] = piece
        else:
            ordered_non_structural.append(piece)

    # Remove any leftover <unk> pieces since unk_id = -1.
    ordered_non_structural = [
        p for p in ordered_non_structural
        if not (p.piece == "<unk>" and p.type == SP.UNKNOWN)
    ]

    # Build the new piece list.
    new_pieces = []

    # IDs 0–11: structural tokens in exact order.
    for idx, spelling in enumerate(STRUCTURAL_TOKENS):
        if spelling in spelling_to_piece:
            piece = spelling_to_piece[spelling]
        else:
            # Create a new piece entry if the trainer didn't produce one.
            piece = SP()
            piece.piece = spelling
            piece.score = 0.0

        # Set the correct type.
        if idx == 0:
            piece.type = getattr(SP, "PAD", SP.CONTROL)  # <|pad|> → PAD or CONTROL type
        else:
            piece.type = SP.CONTROL   # Remaining structural → CONTROL type

        new_pieces.append(piece)

    # IDs 12+: remaining pieces in original order.
    new_pieces.extend(ordered_non_structural)

    # Pad to VOCAB_SIZE if the trainer produced fewer pieces than needed
    # (happens with small corpora where hard_vocab_limit=False).
    # Use UNUSED type for padding pieces so that SentencePiece never emits them
    # during normal text encoding.
    if len(new_pieces) < VOCAB_SIZE:
        for i in range(VOCAB_SIZE - len(new_pieces)):
            pad_piece = SP()
            pad_piece.piece = f"<|reserved_{i:05d}|>"
            pad_piece.score = 0.0
            pad_piece.type = SP.UNUSED
            new_pieces.append(pad_piece)

    # Verify total count.
    if len(new_pieces) != VOCAB_SIZE:
        raise ValueError(
            f"After rearrangement, piece count is {len(new_pieces)}; "
            f"expected {VOCAB_SIZE}"
        )

    # Verify no duplicate pieces exist in the rearranged model.
    seen_pieces: set[str] = set()
    for idx, p in enumerate(new_pieces):
        if p.piece in seen_pieces:
            raise ValueError(
                f"Candidate B proto has duplicate piece {p.piece!r} at index {idx}"
            )
        seen_pieces.add(p.piece)

    # Replace proto pieces.
    del proto.pieces[:]
    proto.pieces.extend(new_pieces)


def _fix_trainer_spec(proto) -> None:
    """Ensure the trainer_spec fields match IGRIS requirements.

    This corrects any values the SentencePiece trainer may have overridden.
    """
    spec = proto.trainer_spec
    spec.pad_id = 0
    spec.pad_piece = STRUCTURAL_TOKENS[0]
    spec.bos_id = -1
    spec.eos_id = -1
    spec.unk_id = -1
    spec.vocab_size = VOCAB_SIZE
    # Clear ephemeral host temp paths so artifact serializations are deterministic
    # and contain no host-specific leakage.
    del spec.input[:]
    spec.model_prefix = ""


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def build_candidate_b(
    corpus_iterator: Iterator[str],
    output_dir: str | Path,
    *,
    vocab_size: int = VOCAB_SIZE,
    character_coverage: float = 0.9995,
    num_threads: int = 1,
    seed_sentencepiece_size: int = 1_000_000,
    save_raw_model: bool = False,
) -> Path:
    """Train a Candidate B Unigram tokenizer and save the artifact.

    Args:
        corpus_iterator: An iterator yielding text strings for training.
            For synthetic testing, pass a small list.  For production,
            pass a streaming iterator over the authorized corpus.
        output_dir: Directory where ``tokenizer.model`` and
            ``build_metadata.json`` will be written.
        vocab_size: Target vocabulary size (must be ``VOCAB_SIZE``).
        character_coverage: Character coverage for the Unigram trainer.
        num_threads: Number of training threads (1 for determinism).
        seed_sentencepiece_size: Seed sentence piece size for the trainer.

    Returns:
        Path to the saved ``tokenizer.model``.

    Raises:
        ValueError: If vocab_size does not match the IGRIS specification.
    """
    if vocab_size != VOCAB_SIZE:
        raise ValueError(
            f"Candidate B vocab_size must be {VOCAB_SIZE}; got {vocab_size}"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Write corpus to a temporary file (SentencePiece requires a file path).
    corpus_lines = list(corpus_iterator)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", encoding="utf-8", delete=False
    ) as tmp:
        tmp_path = tmp.name
        for line in corpus_lines:
            tmp.write(line)
            if not line.endswith("\n"):
                tmp.write("\n")

    try:
        # Train with SentencePiece.
        # We use a temporary prefix, then post-process the proto.
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_prefix = os.path.join(tmp_dir, "igris_b_raw")

            # Build the user_defined_symbols list (structural tokens).
            user_defined = list(STRUCTURAL_TOKENS)

            # SentencePiece requires unk_id during training and it must
            # not collide with pad_id.  Strategy:
            #   - Train with unk_id at a default position (let the trainer
            #     pick it, we pass no explicit unk_id so it defaults to 0).
            #   - Set pad_id=-1 during training (the trainer doesn't
            #     support pad_id=0 when unk_id=0).
            #   - Fix pad_id, unk_id, and piece ordering in the proto
            #     after training.
            #
            # We request vocab_size+1 to account for the <unk> piece that
            # the trainer inserts, which we will remove in post-processing.
            #
            # hard_vocab_limit=False allows the trainer to produce fewer
            # pieces than vocab_size when the corpus is too small (e.g.
            # synthetic test corpus).  Missing pieces are padded with
            # reserved entries in _pad_to_vocab_size().
            spm.SentencePieceTrainer.train(
                input=tmp_path,
                model_prefix=model_prefix,
                model_type="unigram",
                vocab_size=vocab_size + 1,  # +1 for <unk> we'll remove
                character_coverage=character_coverage,
                byte_fallback=True,
                normalization_rule_name="identity",
                add_dummy_prefix=False,
                remove_extra_whitespaces=False,
                # pad_id=-1 during training; we set it to 0 in the proto.
                pad_id=-1,
                bos_id=-1,
                eos_id=-1,
                # unk_id defaults to 0 (required by the trainer).
                user_defined_symbols=user_defined,  # All 12 structural tokens.
                num_threads=num_threads,
                seed_sentencepiece_size=seed_sentencepiece_size,
                hard_vocab_limit=False,
            )

            raw_model_path = model_prefix + ".model"

            # Optionally preserve raw unrearranged model for equivalence verification.
            if save_raw_model:
                raw_artifact_path = output_path / "tokenizer_raw.model"
                raw_artifact_path.write_bytes(Path(raw_model_path).read_bytes())

            # Load, inspect and rearrange the proto.
            proto = _load_proto(raw_model_path)

            # Ensure normalizer_spec is correct.
            norm = proto.normalizer_spec
            norm.name = "identity"
            norm.add_dummy_prefix = False
            norm.remove_extra_whitespaces = False
            norm.escape_whitespaces = True

            # Fix trainer_spec IDs.
            _fix_trainer_spec(proto)

            # Rearrange pieces to enforce IGRIS structural token ordering.
            _rearrange_pieces(proto)

            # Save the corrected model.
            artifact_path = output_path / "tokenizer.model"
            artifact_path.write_bytes(proto.SerializeToString())

    finally:
        # Clean up temporary corpus file.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # Validate by loading with the existing loader pipeline.
    processor = spm.SentencePieceProcessor(model_file=str(artifact_path))

    # Compute SHA-256.
    sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

    # Run the existing artifact validator.
    validation_result = validate_candidate_b_config(processor)

    # Write build metadata.
    metadata = {
        "candidate": "B",
        "backend": "sentencepiece",
        "backend_version": _get_sentencepiece_version(),
        "model_type": "UNIGRAM",
        "byte_fallback": True,
        "normalizer": "identity",
        "vocab_size": VOCAB_SIZE,
        "structural_tokens": {
            spelling: idx for idx, spelling in enumerate(STRUCTURAL_TOKENS)
        },
        "unicode_version": "15.1.0",
        "training_config": {
            "character_coverage": character_coverage,
            "num_threads": num_threads,
            "seed_sentencepiece_size": seed_sentencepiece_size,
            "add_dummy_prefix": False,
            "remove_extra_whitespaces": False,
            "escape_whitespaces": True,
        },
        "artifact_sha256": sha256,
        "artifact_filename": "tokenizer.model",
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "validation": validation_result,
    }

    metadata_path = output_path / "build_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    return artifact_path


def load_and_validate_candidate_b(
    artifact_path: str | Path,
    normalization: str = "NFC",
) -> StrictTokenizer:
    """Load a Candidate B artifact, run all validators, and return a StrictTokenizer.

    This is a convenience wrapper around ``load_candidate_b`` that also
    verifies the byte-fallback mapping is complete.

    Args:
        artifact_path: Path to ``tokenizer.model``.
        normalization: ``'NFC'`` or ``'exact'``.

    Returns:
        A validated ``StrictTokenizer`` ready for use.
    """
    return load_candidate_b(str(artifact_path), normalization)


def _get_sentencepiece_version() -> str:
    """Return the installed sentencepiece library version."""
    try:
        return spm.__version__
    except AttributeError:
        return "unknown"
