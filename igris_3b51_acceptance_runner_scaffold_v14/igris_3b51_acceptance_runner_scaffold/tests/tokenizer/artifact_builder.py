"""Write IGRIS metadata and SHA-256 manifest for a validated trained artifact."""
from __future__ import annotations

import json
from pathlib import Path

from .acceptance_config import PROJECT_VERSION
from .artifact_contract import BACKEND_FILES, ARTIFACT_SCHEMA_VERSION, sha256_file
from .metadata_contract import build_metadata, save_metadata


def finalize_artifact(candidate: str, artifact_dir: str | Path) -> tuple[Path, Path]:
    if candidate not in BACKEND_FILES:
        raise ValueError("candidate must be 'A' or 'B'")
    root = Path(artifact_dir).expanduser().resolve()
    backend = root / BACKEND_FILES[candidate]
    if not backend.is_file() or backend.stat().st_size == 0:
        raise FileNotFoundError(f"trained backend artifact missing or empty: {backend}")

    # Re-open the real backend and verify the exact vocabulary and structural IDs.
    if candidate == "A":
        from tokenizers import Tokenizer
        model = Tokenizer.from_file(str(backend))
        actual_size = model.get_vocab_size(with_added_tokens=True)
        id_lookup = model.token_to_id
    else:
        import sentencepiece as spm
        model = spm.SentencePieceProcessor(model_file=str(backend))
        actual_size = model.get_piece_size()
        id_lookup = model.piece_to_id

    from .acceptance_config import STRUCTURAL_TOKENS, VOCAB_SIZE
    if actual_size != VOCAB_SIZE:
        raise ValueError(f"vocabulary size {actual_size} != {VOCAB_SIZE}")
    for expected_id, token in enumerate(STRUCTURAL_TOKENS):
        actual_id = id_lookup(token)
        if actual_id != expected_id:
            raise ValueError(f"structural token {token!r}: expected {expected_id}, got {actual_id}")

    metadata_path = root / "metadata.json"
    manifest_path = root / "artifact_manifest.json"
    save_metadata(metadata_path, build_metadata(candidate, extra={
        "backend_file": BACKEND_FILES[candidate],
        "training_artifact_status": "trained_and_backend_verified",
    }))
    manifest = {
        "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
        "project": "IGRIS",
        "project_version": PROJECT_VERSION,
        "candidate": candidate,
        "backend_file": BACKEND_FILES[candidate],
        "metadata_file": "metadata.json",
        "sha256": {
            BACKEND_FILES[candidate]: sha256_file(backend),
            "metadata.json": sha256_file(metadata_path),
        },
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\\n",
        encoding="utf-8",
    )
    return metadata_path, manifest_path
