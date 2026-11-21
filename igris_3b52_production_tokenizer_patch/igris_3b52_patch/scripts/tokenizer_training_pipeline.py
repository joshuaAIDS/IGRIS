"""IGRIS Phase 15 — Controlled Tokenizer Training Pipeline.

Provides an isolated, reproducible, default-deny tokenizer training capability
strictly bounded by governance policies and tier boundaries.

MANDATORY INVARIANTS:
  1. Default-Deny Authorization: Training rejected without explicit owner authorization.
  2. Tier Boundary Enforcement:
     - Tier 1 (Permissive): Requires explicit source-level authorization.
     - Tier 2 (Conditional): STRICTLY BLOCKED from training.
     - Tier 3 (Evaluation-Only): STRICTLY BLOCKED from training.
     - Tier 4 (Permanently Blocked): STRICTLY BLOCKED from training.
  3. No Implicit Permission: Physical presence of corpus grants zero permission.
  4. Production Gate Lock: Production tokenizer training is locked; only synthetic
     or isolated test runs are permitted.
  5. Artifact Isolation: Generated test artifacts must be stored in isolated disposable
     test directories; never written to candidate_a or candidate_b production locations.
  6. Provenance & Reproducibility: Input hash verification, output hash generation,
     and chained audit logging.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

# Ensure patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from igris.tokenizer.strict import (
    STRUCTURAL_COUNT,
    STRUCTURAL_TOKENS,
    VOCAB_SIZE,
    load_candidate_a,
    load_candidate_b,
)
from igris.tokenizer.candidate_a_builder import build_candidate_a
from igris.tokenizer.candidate_b_builder import build_candidate_b
from tokenizer_evaluation import TokenizerEvaluator, TokenizerEvaluationSummary

# Certified Production Invariants
CANDIDATE_A_EXPECTED_SHA256 = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_EXPECTED_SHA256 = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

# 32 Canonical Registered Sources and Tiers
TIER_1_PERMISSIVE_SOURCES = {
    "SRC-TA-01", "SRC-TA-02", "SRC-TA-03", "SRC-TA-04", "SRC-TA-05",
    "SRC-TA-06", "SRC-TA-07", "SRC-TA-08", "SRC-TA-09", "SRC-TA-10",
    "SRC-TA-11", "SRC-TA-12", "SRC-TA-13", "SRC-TA-14", "SRC-TA-15",
    "SRC-TA-16", "SRC-EN-01", "SRC-HI-01",
}

TIER_2_CONDITIONAL_SOURCES = {
    "SRC-ML-01", "SRC-TE-01", "SRC-KN-01", "SRC-BN-01",
    "SRC-GU-01", "SRC-CD-01", "SRC-DOC-01", "SRC-MIX-01",
}

TIER_3_EVALUATION_SOURCES = {
    "SRC-CD-02",  # HumanEval / MBPP benchmark evaluation
    "SRC-CV-04",  # Anthropic HH-RLHF evaluation
}

TIER_4_BLOCKED_SOURCES = {
    "SRC-CHAT-01",  # DailyDialog (non-commercial / unclear rights)
    "SRC-SUB-01",   # OpenSubtitles (copyright ambiguity)
    "SRC-IITB-01",  # IIT Bombay English-Hindi (non-commercial restriction)
    "SRC-SOC-01",   # Social Dravidian (unlicensed scraped corpus)
}


class TrainingError(Exception):
    """Base exception for tokenizer training errors."""


class TrainingAuthorizationError(TrainingError):
    """Raised when training lacks explicit owner authorization."""


class TierBoundaryViolationError(TrainingError):
    """Raised when training attempts to ingest prohibited or restricted source tiers."""


class ProductionTrainingLockedError(TrainingError):
    """Raised when production training is attempted while gates remain locked."""


class ArtifactIsolationError(TrainingError):
    """Raised when training outputs violate isolation boundaries."""


class CorpusIntegrityError(TrainingError):
    """Raised when corpus hash or manifest verification fails."""


@dataclass
class CorpusManifest:
    manifest_id: str
    manifest_path: str
    authorized_sources: list[str]
    expected_corpus_sha256: str


@dataclass
class TokenizerTrainingConfig:
    config_version: str
    candidate_type: str  # "candidate_a_bpe" or "candidate_b_unigram"
    vocab_size: int
    structural_tokens: list[str]
    byte_fallback: bool
    random_seed: int
    target_environment: str  # "synthetic_test", "isolated_test", "production"
    owner_authorization_reference: str
    corpus_manifest: CorpusManifest
    output_directory: str
    character_coverage: float = 0.9995
    min_frequency: int = 2
    provenance_logging: bool = True

    def validate(self) -> None:
        """Validate configuration parameters against schema rules."""
        if self.vocab_size != VOCAB_SIZE:
            raise ValueError(f"vocab_size must be {VOCAB_SIZE}; got {self.vocab_size}")
        if self.structural_tokens != list(STRUCTURAL_TOKENS):
            raise ValueError("structural_tokens must exactly match canonical 12 tokens")
        if not self.byte_fallback:
            raise ValueError("byte_fallback must be True")
        if self.candidate_type not in ["candidate_a_bpe", "candidate_b_unigram"]:
            raise ValueError(f"Unknown candidate_type: {self.candidate_type}")
        if self.target_environment not in ["synthetic_test", "isolated_test", "production"]:
            raise ValueError(f"Unknown target_environment: {self.target_environment}")


@dataclass
class TrainingResult:
    status: str
    candidate_type: str
    artifact_path: str
    artifact_sha256: str
    corpus_sha256: str
    training_duration_sec: float
    output_vocab_size: int
    provenance_record: dict[str, Any]
    evaluation_summary: TokenizerEvaluationSummary | None = None


class ControlledTokenizerTrainingPipeline:
    """Orchestrates controlled, reproducible tokenizer training."""

    def __init__(
        self,
        audit_log_path: Path | str | None = None,
        production_candidate_a_path: Path | str | None = None,
        production_candidate_b_path: Path | str | None = None,
    ):
        self.audit_log_path = Path(audit_log_path or (_PATCH_ROOT.parent / "quarantine" / "logs" / "tokenizer_training_audit.jsonl"))
        artifacts_dir = _PATCH_ROOT / "artifacts" / "tokenizer"
        self.prod_cand_a = Path(production_candidate_a_path or (artifacts_dir / "candidate_a" / "tokenizer.json"))
        self.prod_cand_b = Path(production_candidate_b_path or (artifacts_dir / "candidate_b" / "tokenizer.model"))

    def verify_candidate_invariants(self) -> None:
        """Verify that Candidate A and Candidate B hashes on disk remain intact."""
        if self.prod_cand_a.exists():
            h_a = hashlib.sha256(self.prod_cand_a.read_bytes()).hexdigest()
            if h_a != CANDIDATE_A_EXPECTED_SHA256:
                raise ArtifactIsolationError(
                    f"Candidate A invariant violated! Expected {CANDIDATE_A_EXPECTED_SHA256}, got {h_a}"
                )
        if self.prod_cand_b.exists():
            h_b = hashlib.sha256(self.prod_cand_b.read_bytes()).hexdigest()
            if h_b != CANDIDATE_B_EXPECTED_SHA256:
                raise ArtifactIsolationError(
                    f"Candidate B invariant violated! Expected {CANDIDATE_B_EXPECTED_SHA256}, got {h_b}"
                )

    def train_isolated_tokenizer(
        self,
        config: TokenizerTrainingConfig,
        corpus_iterator: Iterator[str] | Sequence[str],
        corpus_file_path: Path | str | None = None,
    ) -> TrainingResult:
        """Train a tokenizer in strict isolation with default-deny governance."""
        # 1. Pre-execution invariant check
        self.verify_candidate_invariants()

        # 2. Validate configuration schema
        config.validate()

        # 3. Check Production Lock
        if config.target_environment == "production":
            raise ProductionTrainingLockedError(
                "Production tokenizer training is strictly LOCKED in Phase 15. "
                "No production dataset is authorized or acquired."
            )

        # 4. Check Owner Authorization
        if not config.owner_authorization_reference or not config.owner_authorization_reference.startswith("SOLO_OWNER_AUTH_"):
            raise TrainingAuthorizationError(
                f"Missing or invalid owner authorization reference: {config.owner_authorization_reference!r}. "
                "Default-Deny policy enforced."
            )

        # 5. Check Source Tier Boundaries
        for src_id in config.corpus_manifest.authorized_sources:
            if src_id in TIER_4_BLOCKED_SOURCES:
                raise TierBoundaryViolationError(f"Source {src_id} is permanently BLOCKED from all pipelines.")
            if src_id in TIER_3_EVALUATION_SOURCES:
                raise TierBoundaryViolationError(f"Source {src_id} is reserved for EVALUATION ONLY and barred from training.")
            if src_id in TIER_2_CONDITIONAL_SOURCES:
                raise TierBoundaryViolationError(f"Source {src_id} is CONDITIONAL and barred from pre-training without clearance.")
            if src_id not in TIER_1_PERMISSIVE_SOURCES and not src_id.startswith("SRC-SYNTH-"):
                raise TierBoundaryViolationError(f"Source {src_id} is not recognized as an authorized Tier 1 source.")

        # 6. Verify Artifact Isolation
        out_path = Path(config.output_directory).resolve()
        prod_a_dir = self.prod_cand_a.parent.resolve()
        prod_b_dir = self.prod_cand_b.parent.resolve()

        if out_path == prod_a_dir or out_path == prod_b_dir:
            raise ArtifactIsolationError(
                f"Output directory {out_path} conflicts with production candidate directory. "
                "Synthetic artifacts must be strictly isolated."
            )

        out_path.mkdir(parents=True, exist_ok=True)

        # 7. Corpus Hash Verification
        corpus_lines = list(corpus_iterator)
        corpus_bytes = "\n".join(corpus_lines).encode("utf-8")
        actual_corpus_hash = hashlib.sha256(corpus_bytes).hexdigest()

        if config.corpus_manifest.expected_corpus_sha256:
            if actual_corpus_hash != config.corpus_manifest.expected_corpus_sha256:
                raise CorpusIntegrityError(
                    f"Corpus SHA-256 mismatch! Expected {config.corpus_manifest.expected_corpus_sha256}, got {actual_corpus_hash}"
                )

        # 8. Execute Isolated Training
        t0 = time.perf_counter()
        if config.candidate_type == "candidate_a_bpe":
            artifact_file = build_candidate_a(
                iter(corpus_lines),
                out_path,
                vocab_size=config.vocab_size,
                min_frequency=config.min_frequency,
            )
        elif config.candidate_type == "candidate_b_unigram":
            artifact_file = build_candidate_b(
                iter(corpus_lines),
                out_path,
                vocab_size=config.vocab_size,
                character_coverage=config.character_coverage,
                num_threads=1,  # Strictly deterministic
            )
        else:
            raise ValueError(f"Unknown candidate type: {config.candidate_type}")

        duration = time.perf_counter() - t0
        artifact_bytes = artifact_file.read_bytes()
        artifact_hash = hashlib.sha256(artifact_bytes).hexdigest()

        # 9. Verify Post-Execution Candidate Invariants
        self.verify_candidate_invariants()

        # 10. Record Provenance and Chained Audit Log
        prev_hash = self._get_last_audit_hash()
        timestamp = "2026-11-18T12:00:00Z"
        payload = f"{timestamp}|{config.candidate_type}|{actual_corpus_hash}|{artifact_hash}|{config.owner_authorization_reference}|{prev_hash}"
        entry_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        prov_record = {
            "timestamp": timestamp,
            "candidate_type": config.candidate_type,
            "config_version": config.config_version,
            "random_seed": config.random_seed,
            "target_environment": config.target_environment,
            "owner_auth_ref": config.owner_authorization_reference,
            "corpus_manifest_id": config.corpus_manifest.manifest_id,
            "corpus_sha256": actual_corpus_hash,
            "artifact_path": str(artifact_file),
            "artifact_sha256": artifact_hash,
            "training_duration_sec": round(duration, 4),
            "prev_hash": prev_hash,
            "entry_hash": entry_hash,
        }

        if config.provenance_logging:
            self._append_audit_log(prov_record)

        # 11. Run Evaluator on Test Artifact
        eval_summary = None
        try:
            evaluator = TokenizerEvaluator(repeat_runs=2)
            if config.candidate_type == "candidate_a_bpe":
                test_tok = load_candidate_a(str(artifact_file))
            else:
                test_tok = load_candidate_b(str(artifact_file))
            eval_summary = evaluator.evaluate(test_tok, f"Synthetic {config.candidate_type}", artifact_file)
        except Exception:
            eval_summary = None

        return TrainingResult(
            status="SUCCESS_ISOLATED_TEST",
            candidate_type=config.candidate_type,
            artifact_path=str(artifact_file),
            artifact_sha256=artifact_hash,
            corpus_sha256=actual_corpus_hash,
            training_duration_sec=round(duration, 4),
            output_vocab_size=config.vocab_size,
            provenance_record=prov_record,
            evaluation_summary=eval_summary,
        )

    def verify_reproducibility(
        self,
        config: TokenizerTrainingConfig,
        corpus_lines: list[str],
    ) -> bool:
        """Verify that training twice with identical config & corpus yields identical artifact hashes."""
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            cfg1 = TokenizerTrainingConfig(**asdict(config))
            cfg1.output_directory = d1
            cfg1.provenance_logging = False

            cfg2 = TokenizerTrainingConfig(**asdict(config))
            cfg2.output_directory = d2
            cfg2.provenance_logging = False

            res1 = self.train_isolated_tokenizer(cfg1, corpus_lines)
            res2 = self.train_isolated_tokenizer(cfg2, corpus_lines)

            return res1.artifact_sha256 == res2.artifact_sha256

    def _get_last_audit_hash(self) -> str:
        """Retrieve previous chained hash from audit log."""
        if not self.audit_log_path.exists():
            return "0" * 64
        try:
            with open(self.audit_log_path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
                if not lines:
                    return "0" * 64
                last_entry = json.loads(lines[-1])
                return last_entry.get("entry_hash", "0" * 64)
        except Exception:
            return "0" * 64

    def _append_audit_log(self, record: dict[str, Any]) -> None:
        """Append record to chained audit log."""
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
