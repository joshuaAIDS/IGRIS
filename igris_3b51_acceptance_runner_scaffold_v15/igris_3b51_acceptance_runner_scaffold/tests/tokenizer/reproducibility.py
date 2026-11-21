"""Reproducibility audit helpers. These functions never train tokenizers."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import platform
from pathlib import Path
from typing import Any, Mapping

CANDIDATE_REPRODUCIBILITY = {
    "A": {"level": "EMPIRICAL_ONLY", "seed_control": False,
          "reason": "Reviewed Tokenizers BpeTrainer interface exposes no explicit seed parameter.",
          "controls": {"ordered_inputs": True, "min_frequency": 2,
                       "initial_alphabet": "ByteLevel.alphabet()",
                       "parallelism_environment": "TOKENIZERS_PARALLELISM=false (not a seed)"}},
    "B": {"level": "CONTROLLED_BUT_EMPIRICAL_REQUIRED", "seed_control": False,
          "reason": "Single-threaded, unshuffled settings reduce variability; no seed guarantee is asserted.",
          "controls": {"ordered_inputs": True, "shuffle_input_sentence": False,
                       "num_threads": 1, "input_sentence_size": 0, "hard_vocab_limit": True}},
}

def sha256_file(path: str | Path) -> str:
    p = Path(path)
    if not p.is_file(): raise FileNotFoundError(str(p))
    h = sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def environment_fingerprint(*, tokenizers_version=None, sentencepiece_version=None):
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "platform": platform.platform(), "tokenizers": tokenizers_version,
            "sentencepiece": sentencepiece_version}

@dataclass(frozen=True)
class RunRecord:
    candidate: str
    corpus_sha256: str
    config_sha256: str
    environment: Mapping[str, Any]
    artifact_sha256: str

def _canonical_hash(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return sha256(payload).hexdigest()

def compare_runs(first: RunRecord, second: RunRecord) -> tuple[bool, str]:
    if first.candidate not in ("A", "B") or second.candidate != first.candidate:
        return False, "candidate identity mismatch"
    for field in ("corpus_sha256", "config_sha256", "environment"):
        if getattr(first, field) != getattr(second, field):
            return False, f"{field} differs between runs"
    if first.artifact_sha256 != second.artifact_sha256:
        return False, "artifact hashes differ; deterministic output not demonstrated"
    return True, "identical corpus, config, environment, and artifact hash"

def build_run_record(candidate: str, corpus_sha256: str, config: Mapping[str, Any],
                     environment: Mapping[str, Any], artifact_path: str | Path) -> RunRecord:
    if candidate not in ("A", "B"): raise ValueError("candidate must be 'A' or 'B'")
    if not isinstance(corpus_sha256, str) or len(corpus_sha256) != 64:
        raise ValueError("corpus_sha256 must be a 64-character SHA-256 hex digest")
    try: int(corpus_sha256, 16)
    except ValueError as exc: raise ValueError("corpus_sha256 must be hexadecimal") from exc
    if not isinstance(config, Mapping) or not isinstance(environment, Mapping):
        raise TypeError("config and environment must be mappings")
    return RunRecord(candidate, corpus_sha256.lower(), _canonical_hash(config),
                     dict(environment), sha256_file(artifact_path))

def reproducibility_policy(candidate: str) -> dict[str, Any]:
    if candidate not in CANDIDATE_REPRODUCIBILITY: raise ValueError("candidate must be 'A' or 'B'")
    return json.loads(json.dumps(CANDIDATE_REPRODUCIBILITY[candidate]))
