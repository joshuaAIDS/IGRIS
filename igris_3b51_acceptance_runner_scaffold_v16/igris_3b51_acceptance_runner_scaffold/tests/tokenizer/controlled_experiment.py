"""Plan and audit controlled IGRIS tokenizer repeatability experiments.

This module NEVER trains tokenizers. It validates corpus parity, emits a
repeat-run plan, and compares hashes from artifacts produced separately after
explicit training authorization.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable, Mapping, Any

from .training_config import corpus_fingerprints, CANDIDATE_A_CONFIG, CANDIDATE_B_CONFIG
from .reproducibility import sha256_file


@dataclass(frozen=True)
class ExperimentPlan:
    schema_version: str
    project: str
    corpus: tuple[tuple[str, str, int], ...]
    candidates: Mapping[str, Mapping[str, Any]]
    training_execution: str


def _config_payload(config) -> dict[str, Any]:
    return {
        "candidate": config.candidate,
        "algorithm": config.algorithm,
        "vocab_size": config.vocab_size,
        "structural_tokens": list(config.structural_tokens),
        "normalization": config.normalization,
        "byte_fallback": config.byte_fallback,
        "deterministic_settings": [list(x) for x in config.deterministic_settings],
        "backend_filename": config.backend_filename,
    }


def build_experiment_plan(corpus_files: Iterable[str | Path], output_root: str | Path) -> ExperimentPlan:
    """Create an in-memory plan for two runs per candidate; reads corpus only."""
    fingerprints = corpus_fingerprints(corpus_files)
    root = Path(output_root).expanduser().resolve()
    candidates: dict[str, dict[str, Any]] = {}
    for key, config in (("A", CANDIDATE_A_CONFIG), ("B", CANDIDATE_B_CONFIG)):
        payload = _config_payload(config)
        config_hash = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()
        candidates[key] = {
            "config": payload,
            "config_sha256": config_hash,
            "runs": [
                {"run": 1, "output_dir": str(root / f"candidate_{key}" / "run_1"), "status": "PLANNED"},
                {"run": 2, "output_dir": str(root / f"candidate_{key}" / "run_2"), "status": "PLANNED"},
            ],
        }
    return ExperimentPlan("1.0", "IGRIS v2.2.28", fingerprints, candidates,
                          "NOT_EXECUTED; this scaffold only plans and audits")


def plan_to_dict(plan: ExperimentPlan) -> dict[str, Any]:
    return {
        "schema_version": plan.schema_version,
        "project": plan.project,
        "corpus": [list(row) for row in plan.corpus],
        "candidates": dict(plan.candidates),
        "training_execution": plan.training_execution,
    }


def write_plan(plan: ExperimentPlan, destination: str | Path) -> Path:
    """Write plan JSON only when caller explicitly invokes this function."""
    target = Path(destination).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(plan_to_dict(plan), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    target.write_text(payload, encoding="utf-8", newline="\n")
    return target


def compare_artifact_pair(first: str | Path, second: str | Path) -> dict[str, Any]:
    """Compare two already-existing backend files; never loads/trains them."""
    p1, p2 = Path(first).expanduser().resolve(), Path(second).expanduser().resolve()
    h1, h2 = sha256_file(p1), sha256_file(p2)
    return {
        "first": str(p1), "second": str(p2),
        "first_sha256": h1, "second_sha256": h2,
        "identical_bytes": h1 == h2,
        "conclusion": "BYTE_IDENTICAL" if h1 == h2 else "NOT_BYTE_IDENTICAL",
        "caveat": "Hash equality is byte-level evidence only; semantic equivalence requires backend-level tests.",
    }
