"""Candidate adapter boundary.

This module intentionally does not train tokenizers or guess artifact paths.
Actual artifact loading remains blocked until trained artifacts and the final
loader contract are available.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class AdapterResult:
    candidate: str
    backend: Optional[Any]
    status: str
    reason: str


class CandidateAdapter:
    def __init__(self, candidate: str, artifact_path: Optional[str] = None):
        if candidate not in ("A", "B"):
            raise ValueError("candidate must be 'A' or 'B'")
        self.candidate = candidate
        self.artifact_path = Path(artifact_path) if artifact_path else None

    def load(self) -> AdapterResult:
        if self.artifact_path is None:
            return AdapterResult(
                self.candidate, None, "BLOCKED",
                "No trained tokenizer artifact path was supplied."
            )
        if not self.artifact_path.is_file():
            return AdapterResult(
                self.candidate, None, "BLOCKED",
                f"Artifact does not exist: {self.artifact_path}"
            )
        return AdapterResult(
            self.candidate, None, "BLOCKED",
            "Artifact exists, but production loader integration is not "
            "implemented in this acceptance-runner scaffold. No assumptions "
            "are made about loader arguments or artifact metadata."
        )
