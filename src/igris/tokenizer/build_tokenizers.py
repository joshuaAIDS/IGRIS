"""IGRIS shared tokenizer build interface.

Provides a unified entry point to:
  - Build Candidate A (ByteLevel BPE via Hugging Face Tokenizers).
  - Build Candidate B (Unigram via SentencePiece).
  - Validate both artifacts.
  - Save build metadata.
  - Reload and smoke-test artifacts.

Output directory structure:
  artifacts/tokenizer/candidate_a/
    tokenizer.json
    build_metadata.json
  artifacts/tokenizer/candidate_b/
    tokenizer.model
    build_metadata.json

IMPORTANT: Actual corpus training requires explicit user authorization.
This module provides the builder orchestration only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from .strict import (
    STRUCTURAL_TOKENS,
    STRUCTURAL_COUNT,
    VOCAB_SIZE,
    StrictTokenizer,
    RawBinaryCodec,
)
from .candidate_a_builder import (
    build_candidate_a,
    load_and_validate_candidate_a,
)
from .candidate_b_builder import (
    build_candidate_b,
    load_and_validate_candidate_b,
)


# ---------------------------------------------------------------------------
# Default output paths
# ---------------------------------------------------------------------------

DEFAULT_ARTIFACTS_ROOT = Path("artifacts") / "tokenizer"
CANDIDATE_A_DIR = "candidate_a"
CANDIDATE_B_DIR = "candidate_b"


# ---------------------------------------------------------------------------
# Build result
# ---------------------------------------------------------------------------

@dataclass
class BuildResult:
    """Result of a single candidate build."""
    candidate: str
    artifact_path: Path
    metadata_path: Path
    validation_passed: bool
    validation_errors: list[str] = field(default_factory=list)
    smoke_test_passed: bool = False
    smoke_test_errors: list[str] = field(default_factory=list)


@dataclass
class BuildReport:
    """Combined build report for both candidates."""
    candidate_a: BuildResult | None = None
    candidate_b: BuildResult | None = None

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        result: dict = {}
        for name, build in [("candidate_a", self.candidate_a), ("candidate_b", self.candidate_b)]:
            if build is not None:
                result[name] = {
                    "candidate": build.candidate,
                    "artifact_path": str(build.artifact_path),
                    "metadata_path": str(build.metadata_path),
                    "validation_passed": build.validation_passed,
                    "validation_errors": build.validation_errors,
                    "smoke_test_passed": build.smoke_test_passed,
                    "smoke_test_errors": build.smoke_test_errors,
                }
        return result


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

_SMOKE_TEXTS = [
    "",
    "Hello world",
    "தமிழ்",
    "Tanglish vanakkam நன்றி",
    "हिन्दी",
    "emoji 🎉🌍",
    "e\u0301",  # combining acute accent → NFC: é
    "a  b\t\n",  # whitespace
    "<|pad|> literal structural token spelling",
]


def _smoke_test(tokenizer: StrictTokenizer) -> list[str]:
    """Run smoke tests on a loaded tokenizer. Return list of error strings (empty = pass)."""
    errors: list[str] = []

    # Text round-trip tests.
    for text in _SMOKE_TEXTS:
        try:
            ids = tokenizer.encode_content(text)
            decoded = tokenizer.decode_content(ids)
            # NFC normalization means e\u0301 → é
            import unicodedata2
            expected = unicodedata2.normalize("NFC", text)
            if decoded != expected:
                errors.append(
                    f"Text round-trip failed for {text!r}: "
                    f"got {decoded!r}, expected {expected!r}"
                )
        except Exception as exc:
            errors.append(f"Text encode/decode raised for {text!r}: {exc}")

    # Batch test.
    try:
        batch_result = tokenizer.decode_batch(
            tokenizer.encode_batch(["", "test", "தமிழ்"])
        )
        if batch_result != ["", "test", "தமிழ்"]:
            errors.append(f"Batch round-trip mismatch: {batch_result!r}")
    except Exception as exc:
        errors.append(f"Batch test raised: {exc}")

    # Raw binary round-trip test.
    try:
        codec = tokenizer.raw_binary_codec()
        payload = bytes(range(256))
        encoded = codec.encode_bytes(payload)
        decoded_bytes = codec.decode_bytes(encoded)
        if decoded_bytes != payload:
            errors.append("Raw binary round-trip failed for 0x00–0xFF")
    except Exception as exc:
        errors.append(f"Raw binary test raised: {exc}")

    # Structural token ID verification.
    for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
        try:
            # Verify that encoding text containing the literal spelling
            # escapes it and round-trips correctly.
            test_text = f"before{spelling}after"
            ids = tokenizer.encode_content(test_text)
            decoded = tokenizer.decode_content(ids)
            if decoded != test_text:
                errors.append(
                    f"Structural escape round-trip failed for {spelling!r}: "
                    f"got {decoded!r}"
                )
        except Exception as exc:
            errors.append(f"Structural escape test raised for {spelling!r}: {exc}")

    return errors


# ---------------------------------------------------------------------------
# Build orchestration
# ---------------------------------------------------------------------------

def build_all(
    corpus_iterator_a: Iterator[str],
    corpus_iterator_b: Iterator[str],
    *,
    artifacts_root: str | Path = DEFAULT_ARTIFACTS_ROOT,
    min_frequency_a: int = 2,
    character_coverage_b: float = 0.9995,
) -> BuildReport:
    """Build both Candidate A and Candidate B tokenizers.

    Args:
        corpus_iterator_a: Text iterator for Candidate A training.
        corpus_iterator_b: Text iterator for Candidate B training.
        artifacts_root: Root directory for artifacts.
        min_frequency_a: BPE min frequency for Candidate A.
        character_coverage_b: Character coverage for Candidate B.

    Returns:
        A ``BuildReport`` with results for both candidates.
    """
    root = Path(artifacts_root)
    report = BuildReport()

    report.candidate_a = build_single(
        "A", corpus_iterator_a, root / CANDIDATE_A_DIR,
        min_frequency_a=min_frequency_a,
    )
    report.candidate_b = build_single(
        "B", corpus_iterator_b, root / CANDIDATE_B_DIR,
        character_coverage_b=character_coverage_b,
    )

    return report


def build_single(
    candidate: str,
    corpus_iterator: Iterator[str],
    output_dir: str | Path,
    *,
    min_frequency_a: int = 2,
    character_coverage_b: float = 0.9995,
) -> BuildResult:
    """Build a single candidate tokenizer.

    Args:
        candidate: ``'A'`` or ``'B'``.
        corpus_iterator: Text iterator for training.
        output_dir: Output directory for the artifact.
        min_frequency_a: BPE min frequency (Candidate A only).
        character_coverage_b: Character coverage (Candidate B only).

    Returns:
        A ``BuildResult`` with validation and smoke-test results.
    """
    output_path = Path(output_dir)

    if candidate == "A":
        artifact_path = build_candidate_a(
            corpus_iterator, output_path, min_frequency=min_frequency_a,
        )
        metadata_path = output_path / "build_metadata.json"

        # Validate by reloading.
        validation_errors: list[str] = []
        try:
            tokenizer = load_and_validate_candidate_a(artifact_path)
            validation_passed = True
        except Exception as exc:
            validation_errors.append(str(exc))
            validation_passed = False
            tokenizer = None

        # Smoke test.
        smoke_errors: list[str] = []
        if tokenizer is not None:
            smoke_errors = _smoke_test(tokenizer)

        return BuildResult(
            candidate="A",
            artifact_path=artifact_path,
            metadata_path=metadata_path,
            validation_passed=validation_passed,
            validation_errors=validation_errors,
            smoke_test_passed=len(smoke_errors) == 0,
            smoke_test_errors=smoke_errors,
        )

    elif candidate == "B":
        artifact_path = build_candidate_b(
            corpus_iterator, output_path, character_coverage=character_coverage_b,
        )
        metadata_path = output_path / "build_metadata.json"

        # Validate by reloading.
        validation_errors = []
        try:
            tokenizer = load_and_validate_candidate_b(artifact_path)
            validation_passed = True
        except Exception as exc:
            validation_errors.append(str(exc))
            validation_passed = False
            tokenizer = None

        # Smoke test.
        smoke_errors = []
        if tokenizer is not None:
            smoke_errors = _smoke_test(tokenizer)

        return BuildResult(
            candidate="B",
            artifact_path=artifact_path,
            metadata_path=metadata_path,
            validation_passed=validation_passed,
            validation_errors=validation_errors,
            smoke_test_passed=len(smoke_errors) == 0,
            smoke_test_errors=smoke_errors,
        )

    else:
        raise ValueError(f"Unknown candidate: {candidate!r}; must be 'A' or 'B'")
