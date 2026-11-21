"""Expected on-disk artifact layout contract; validates files, not model loading."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .acceptance_config import PROJECT_VERSION
from .metadata_contract import validate_metadata

MANIFEST_NAME = "artifact_manifest.json"
METADATA_NAME = "metadata.json"
BACKEND_FILES = {"A": "tokenizer.json", "B": "tokenizer.model"}
ARTIFACT_SCHEMA_VERSION = "1.0"


class ArtifactContractError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_artifact_directory(candidate: str, artifact_dir: str | Path) -> dict[str, Any]:
    if candidate not in BACKEND_FILES:
        raise ArtifactContractError("candidate must be 'A' or 'B'")
    root = Path(artifact_dir)
    if not root.exists():
        raise ArtifactContractError(f"artifact directory does not exist: {root}")
    if not root.is_dir():
        raise ArtifactContractError("artifact path must be a directory")

    manifest_path = root / MANIFEST_NAME
    metadata_path = root / METADATA_NAME
    backend_path = root / BACKEND_FILES[candidate]

    for required in (manifest_path, metadata_path, backend_path):
        if not required.is_file():
            raise ArtifactContractError(f"required artifact file missing: {required.name}")
        if required.stat().st_size == 0:
            raise ArtifactContractError(f"required artifact file is empty: {required.name}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ArtifactContractError(f"invalid artifact manifest JSON: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ArtifactContractError("artifact manifest must be a JSON object")
    expected = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "project": "IGRIS",
        "project_version": PROJECT_VERSION,
        "candidate": candidate,
        "backend_file": BACKEND_FILES[candidate],
        "metadata_file": METADATA_NAME,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ArtifactContractError(f"manifest {key} mismatch")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    try:
        validate_metadata(metadata)
    except (TypeError, ValueError) as exc:
        raise ArtifactContractError(f"metadata contract failed: {exc}") from exc
    if metadata.get("candidate") != candidate:
        raise ArtifactContractError("metadata candidate identity mismatch")

    hashes = manifest.get("sha256")
    if not isinstance(hashes, dict):
        raise ArtifactContractError("manifest sha256 field must be an object")
    for filename, path in ((BACKEND_FILES[candidate], backend_path),
                           (METADATA_NAME, metadata_path)):
        expected_hash = hashes.get(filename)
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            raise ArtifactContractError(f"missing/invalid SHA-256 for {filename}")
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash.lower():
            raise ArtifactContractError(f"SHA-256 mismatch for {filename}")

    return {
        "candidate": candidate,
        "artifact_dir": str(root),
        "backend_file": BACKEND_FILES[candidate],
        "metadata_file": METADATA_NAME,
        "backend_sha256": hashes[BACKEND_FILES[candidate]],
        "metadata_sha256": hashes[METADATA_NAME],
        "layout_valid": True,
        "model_loaded": False,
    }


def create_artifact_manifest(candidate: str, artifact_dir: str | Path) -> dict[str, Any]:
    """Utility for tests/docs only; never writes or downloads a real model."""
    if candidate not in BACKEND_FILES:
        raise ArtifactContractError("candidate must be 'A' or 'B'")
    root = Path(artifact_dir)
    backend = root / BACKEND_FILES[candidate]
    metadata = root / METADATA_NAME
    return {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "project": "IGRIS",
        "project_version": PROJECT_VERSION,
        "candidate": candidate,
        "backend_file": BACKEND_FILES[candidate],
        "metadata_file": METADATA_NAME,
        "sha256": {
            BACKEND_FILES[candidate]: sha256_file(backend),
            METADATA_NAME: sha256_file(metadata),
        },
    }
