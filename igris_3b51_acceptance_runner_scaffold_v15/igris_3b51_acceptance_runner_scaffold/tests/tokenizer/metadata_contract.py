"""Backend-independent tokenizer metadata contract and JSON persistence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .acceptance_config import (
    PROJECT_VERSION, ACCEPTANCE_SPEC_VERSION, INTEGRATION_CONTRACT_VERSION,
    VOCAB_SIZE, UNICODE_VERSION, STRUCTURAL_TOKENS, STRUCTURAL_TOKEN_IDS,
)

CANDIDATE_ALGORITHMS = {
    "A": "bytelevel_bpe",
    "B": "sentencepiece_unigram",
}

REQUIRED_FIELDS = (
    "metadata_schema_version",
    "project",
    "project_version",
    "acceptance_spec_version",
    "integration_contract_version",
    "candidate",
    "algorithm",
    "vocab_size",
    "unicode_version",
    "structural_tokens",
    "structural_token_ids",
)


def build_metadata(candidate: str, *, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    if candidate not in CANDIDATE_ALGORITHMS:
        raise ValueError("candidate must be 'A' or 'B'")
    metadata = {
        "metadata_schema_version": "1.0",
        "project": "IGRIS",
        "project_version": PROJECT_VERSION,
        "acceptance_spec_version": ACCEPTANCE_SPEC_VERSION,
        "integration_contract_version": INTEGRATION_CONTRACT_VERSION,
        "candidate": candidate,
        "algorithm": CANDIDATE_ALGORITHMS[candidate],
        "vocab_size": VOCAB_SIZE,
        "unicode_version": UNICODE_VERSION,
        "structural_tokens": list(STRUCTURAL_TOKENS),
        "structural_token_ids": dict(STRUCTURAL_TOKEN_IDS),
    }
    if extra is not None:
        if not isinstance(extra, dict):
            raise TypeError("extra metadata must be a dict")
        overlap = set(extra).intersection(metadata)
        if overlap:
            raise ValueError(f"extra metadata cannot override required fields: {sorted(overlap)}")
        metadata.update(extra)
    validate_metadata(metadata)
    return metadata


def validate_metadata(metadata: Any) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise TypeError("metadata must be a JSON object/dict")
    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        raise ValueError(f"missing required metadata fields: {missing}")

    if metadata["metadata_schema_version"] != "1.0":
        raise ValueError("unsupported metadata schema version")
    if metadata["project"] != "IGRIS":
        raise ValueError("project identity mismatch")
    if metadata["project_version"] != PROJECT_VERSION:
        raise ValueError("project version mismatch")
    if metadata["acceptance_spec_version"] != ACCEPTANCE_SPEC_VERSION:
        raise ValueError("acceptance spec version mismatch")
    if metadata["integration_contract_version"] != INTEGRATION_CONTRACT_VERSION:
        raise ValueError("integration contract version mismatch")

    candidate = metadata["candidate"]
    if candidate not in CANDIDATE_ALGORITHMS:
        raise ValueError("unknown candidate identity")
    if metadata["algorithm"] != CANDIDATE_ALGORITHMS[candidate]:
        raise ValueError("candidate algorithm mismatch")
    if type(metadata["vocab_size"]) is not int or metadata["vocab_size"] != VOCAB_SIZE:
        raise ValueError("vocabulary size mismatch")
    if metadata["unicode_version"] != UNICODE_VERSION:
        raise ValueError("Unicode version mismatch")
    if metadata["structural_tokens"] != list(STRUCTURAL_TOKENS):
        raise ValueError("structural token order/content mismatch")
    if metadata["structural_token_ids"] != STRUCTURAL_TOKEN_IDS:
        raise ValueError("structural token ID mapping mismatch")
    return metadata


def serialize_metadata(metadata: dict[str, Any]) -> str:
    validate_metadata(metadata)
    return json.dumps(metadata, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def save_metadata(path: str | Path, metadata: dict[str, Any]) -> None:
    serialized = serialize_metadata(metadata)
    Path(path).write_text(serialized + "\n", encoding="utf-8")


def load_metadata(path: str | Path) -> dict[str, Any]:
    try:
        raw = Path(path).read_text(encoding="utf-8")
        parsed = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load valid metadata JSON: {exc}") from exc
    return validate_metadata(parsed)
