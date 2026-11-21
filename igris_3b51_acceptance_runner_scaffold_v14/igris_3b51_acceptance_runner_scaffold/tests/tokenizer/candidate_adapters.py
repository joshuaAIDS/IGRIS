"""Real Candidate A/B artifact loading with strict contract verification.

This module loads existing trained artifacts only. It never trains, downloads,
or modifies tokenizer artifacts.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .artifact_contract import (
    ArtifactContractError,
    validate_artifact_directory,
    BACKEND_FILES,
)
from .acceptance_config import VOCAB_SIZE, STRUCTURAL_TOKENS, STRUCTURAL_TOKEN_IDS


@dataclass
class AdapterResult:
    candidate: str
    backend: Optional[Any]
    status: str
    reason: str
    artifact_info: Optional[dict] = None


class CandidateAdapter:
    def __init__(self, candidate: str, artifact_path: Optional[str] = None):
        if candidate not in ("A", "B"):
            raise ValueError("candidate must be 'A' or 'B'")
        self.candidate = candidate
        self.artifact_path = Path(artifact_path) if artifact_path else None

    def _validate_candidate_a(self, backend: Any) -> None:
        actual_size = backend.get_vocab_size(with_added_tokens=True)
        if actual_size != VOCAB_SIZE:
            raise ValueError(
                f"Candidate A vocabulary size mismatch: expected {VOCAB_SIZE}, got {actual_size}"
            )
        for token, expected_id in STRUCTURAL_TOKEN_IDS.items():
            actual_id = backend.token_to_id(token)
            if actual_id != expected_id:
                raise ValueError(
                    f"Candidate A structural ID mismatch for {token!r}: "
                    f"expected {expected_id}, got {actual_id}"
                )

    def _validate_candidate_b(self, backend: Any) -> None:
        actual_size = backend.get_piece_size()
        if actual_size != VOCAB_SIZE:
            raise ValueError(
                f"Candidate B vocabulary size mismatch: expected {VOCAB_SIZE}, got {actual_size}"
            )
        for token, expected_id in STRUCTURAL_TOKEN_IDS.items():
            actual_id = backend.piece_to_id(token)
            if actual_id != expected_id or backend.id_to_piece(expected_id) != token:
                raise ValueError(
                    f"Candidate B structural ID mismatch for {token!r}: "
                    f"expected {expected_id}, got {actual_id}"
                )

    def load(self) -> AdapterResult:
        if self.artifact_path is None:
            return AdapterResult(
                self.candidate, None, "BLOCKED",
                "No trained tokenizer artifact directory was supplied."
            )
        try:
            artifact_info = validate_artifact_directory(
                self.candidate, self.artifact_path
            )
        except ArtifactContractError as exc:
            return AdapterResult(
                self.candidate, None, "FAIL",
                f"Artifact contract validation failed: {exc}"
            )

        backend_path = self.artifact_path / BACKEND_FILES[self.candidate]
        try:
            if self.candidate == "A":
                try:
                    from tokenizers import Tokenizer
                except ImportError as exc:
                    raise RuntimeError(
                        "Candidate A requires tokenizers==0.23.3 in the active environment."
                    ) from exc
                backend = Tokenizer.from_file(str(backend_path))
                self._validate_candidate_a(backend)
            else:
                try:
                    import sentencepiece as spm
                except ImportError as exc:
                    raise RuntimeError(
                        "Candidate B requires sentencepiece==0.2.3 in the active environment."
                    ) from exc
                backend = spm.SentencePieceProcessor(model_file=str(backend_path))
                self._validate_candidate_b(backend)

        except Exception as exc:
            return AdapterResult(
                self.candidate, None, "FAIL",
                f"Backend loading/validation failed: {type(exc).__name__}: {exc}",
                artifact_info,
            )

        return AdapterResult(
            self.candidate, backend, "PASS",
            "Backend loaded and vocabulary/structural IDs verified.",
            artifact_info,
        )
