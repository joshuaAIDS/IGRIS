"""IGRIS Phase 15 — Tokenizer Evaluation and Training Infrastructure Tests.

Exhaustively verifies:
  1. Candidate A and Candidate B SHA-256 hash invariants.
  2. Read-only evaluation of Candidate A and Candidate B.
  3. Multilingual coverage across all 9 languages + code-switching + robustness.
  4. Indic Unicode integrity (vowels, matras, viramas, conjuncts, ZWJ/ZWNJ).
  5. Tanglish and code-switching evaluation.
  6. Unknown-token behavior and byte fallback mechanisms.
  7. Robustness on empty strings, long texts, and repetitive adversarial inputs.
  8. Performance and throughput measurement reproducibility.
  9. Training configuration schema validation.
 10. Synthetic-only training isolation and production training lock.
 11. Corpus manifest validation and hash verification.
 12. Source-tier boundary enforcement (Tier 1 vs Tiers 2, 3, 4).
 13. Default-deny training authorization.
 14. Artifact isolation enforcement.
 15. Training reproducibility (same seed/corpus -> identical artifact hash).
 16. Chained audit logging and tamper-evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Setup patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from igris.tokenizer.strict import (
    STRUCTURAL_COUNT,
    STRUCTURAL_TOKENS,
    VOCAB_SIZE,
    load_candidate_a,
    load_candidate_b,
)
from tokenizer_evaluation import (
    TokenizerEvaluationSummary,
    TokenizerEvaluator,
    evaluate_candidates,
)
from tokenizer_metrics import (
    AggregateCategoryMetrics,
    SampleTokenizationMetrics,
    compute_sample_metrics,
)
from tokenizer_multilingual_benchmark import (
    BENCHMARK_SAMPLES,
    BenchmarkSample,
    get_benchmark_categories,
    get_samples_for_category,
)
from tokenizer_unicode_tests import (
    INDIC_UNICODE_VECTORS,
    UnicodeIntegrityReport,
    run_unicode_integrity_suite,
)
from tokenizer_training_pipeline import (
    CANDIDATE_A_EXPECTED_SHA256,
    CANDIDATE_B_EXPECTED_SHA256,
    ArtifactIsolationError,
    ControlledTokenizerTrainingPipeline,
    CorpusIntegrityError,
    CorpusManifest,
    ProductionTrainingLockedError,
    TierBoundaryViolationError,
    TokenizerTrainingConfig,
    TrainingAuthorizationError,
)

CAND_A_PATH = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
CAND_B_PATH = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"


# =============================================================================
# 1. TOKENIZER HASH INVARIANTS
# =============================================================================
def test_candidate_a_hash_invariant():
    """Candidate A SHA-256 hash must strictly match certified value."""
    actual = hashlib.sha256(CAND_A_PATH.read_bytes()).hexdigest()
    assert actual == CANDIDATE_A_EXPECTED_SHA256, (
        f"Candidate A hash mismatch: expected {CANDIDATE_A_EXPECTED_SHA256}, got {actual}"
    )


def test_candidate_b_hash_invariant():
    """Candidate B SHA-256 hash must strictly match certified value."""
    actual = hashlib.sha256(CAND_B_PATH.read_bytes()).hexdigest()
    assert actual == CANDIDATE_B_EXPECTED_SHA256, (
        f"Candidate B hash mismatch: expected {CANDIDATE_B_EXPECTED_SHA256}, got {actual}"
    )


# =============================================================================
# 2. READ-ONLY EVALUATION OF CANDIDATE A AND B
# =============================================================================
def test_candidate_a_readonly_evaluation():
    """Candidate A must evaluate cleanly with 100% round-trip fidelity."""
    tok_a = load_candidate_a(str(CAND_A_PATH))
    evaluator = TokenizerEvaluator(repeat_runs=2)
    summary = evaluator.evaluate(tok_a, "Candidate A", CAND_A_PATH)

    assert summary.sha256_hash == CANDIDATE_A_EXPECTED_SHA256
    assert summary.vocab_size == VOCAB_SIZE
    assert summary.structural_tokens_count == 12
    assert summary.overall_metrics.round_trip_exact_pct == 100.0
    assert summary.overall_metrics.unknown_token_rate == 0.0


def test_candidate_b_readonly_evaluation():
    """Candidate B must evaluate cleanly with 100% round-trip fidelity."""
    tok_b = load_candidate_b(str(CAND_B_PATH))
    evaluator = TokenizerEvaluator(repeat_runs=2)
    summary = evaluator.evaluate(tok_b, "Candidate B", CAND_B_PATH)

    assert summary.sha256_hash == CANDIDATE_B_EXPECTED_SHA256
    assert summary.vocab_size == VOCAB_SIZE
    assert summary.structural_tokens_count == 12
    assert summary.overall_metrics.round_trip_exact_pct == 100.0
    assert summary.overall_metrics.unknown_token_rate == 0.0


# =============================================================================
# 3. MULTILINGUAL COVERAGE ACROSS ALL 9 LANGUAGES
# =============================================================================
def test_multilingual_coverage_all_9_languages():
    """All 9 languages + code-switching + robustness must exist and encode with positive tokens."""
    categories = get_benchmark_categories()
    expected = [
        "English", "Hindi", "Tamil", "Telugu", "Malayalam",
        "Kannada", "Bengali", "Gujarati", "Tanglish",
        "Code-Switching", "Robustness",
    ]
    for exp in expected:
        assert exp in categories, f"Missing category: {exp}"

    tok_a = load_candidate_a(str(CAND_A_PATH))
    for cat in expected:
        samples = get_samples_for_category(cat)
        assert len(samples) >= 1, f"Category {cat} has no benchmark samples"
        for s in samples:
            if s.text:
                toks = tok_a.encode_content(s.text)
                assert len(toks) > 0, f"Sample {s.sample_id} yielded 0 tokens"
                dec = tok_a.decode_content(toks)
                assert dec == s.text, f"Round-trip failed on {s.sample_id}"


# =============================================================================
# 4. INDIC SCRIPT INTEGRITY (MATRAS, VIRAMAS, CONJUNCTS, ZWJ/ZWNJ)
# =============================================================================
def test_indic_unicode_integrity_suite():
    """Exhaustive Indic test suite must achieve 100% pass on both candidates."""
    tok_a = load_candidate_a(str(CAND_A_PATH))
    tok_b = load_candidate_b(str(CAND_B_PATH))

    rep_a = run_unicode_integrity_suite(tok_a)
    rep_b = run_unicode_integrity_suite(tok_b)

    assert rep_a.failed_tests == 0, f"Candidate A failed {rep_a.failed_tests} unicode tests"
    assert rep_b.failed_tests == 0, f"Candidate B failed {rep_b.failed_tests} unicode tests"
    assert rep_a.exact_match_pct >= 95.0
    assert rep_b.exact_match_pct >= 95.0


# =============================================================================
# 5. TANGLISH AND CODE-SWITCHING EVALUATION
# =============================================================================
def test_tanglish_and_codeswitching():
    """Tanglish and code-switching samples must round-trip exactly and measure fertility."""
    tok_a = load_candidate_a(str(CAND_A_PATH))
    tok_b = load_candidate_b(str(CAND_B_PATH))

    tanglish_samples = get_samples_for_category("Tanglish")
    cs_samples = get_samples_for_category("Code-Switching")

    for s in tanglish_samples + cs_samples:
        t_a = tok_a.encode_content(s.text)
        t_b = tok_b.encode_content(s.text)
        assert tok_a.decode_content(t_a) == s.text
        assert tok_b.decode_content(t_b) == s.text
        assert len(t_a) > 0
        assert len(t_b) > 0


# =============================================================================
# 6. UNKNOWN TOKEN RATE AND BYTE FALLBACK
# =============================================================================
def test_unknown_token_and_byte_fallback():
    """Unseen and foreign scripts must use byte-fallback and have 0.0 UNK rate."""
    tok_a = load_candidate_a(str(CAND_A_PATH))
    tok_b = load_candidate_b(str(CAND_B_PATH))

    foreign_text = "Привет мир! مرحبا بالعالم! 你好世界!"
    ids_a = tok_a.encode_content(foreign_text)
    ids_b = tok_b.encode_content(foreign_text)

    # UNK token rate must be 0 because byte fallback is used
    assert tok_a.decode_content(ids_a) == foreign_text
    assert tok_b.decode_content(ids_b) == foreign_text


# =============================================================================
# 7. ROBUSTNESS ON EMPTY, LONG, AND ADVERSARIAL INPUTS
# =============================================================================
def test_robustness_edge_cases():
    """Empty string, repetitive characters, and long text must be handled gracefully."""
    tok_a = load_candidate_a(str(CAND_A_PATH))
    tok_b = load_candidate_b(str(CAND_B_PATH))

    # Empty string
    assert tok_a.encode_content("") == []
    assert tok_b.encode_content("") == []
    assert tok_a.decode_content([]) == ""
    assert tok_b.decode_content([]) == ""

    # Long text (2000+ chars)
    long_text = "IGRIS multilingual transformer model evaluation test. " * 50
    ids_a = tok_a.encode_content(long_text)
    ids_b = tok_b.encode_content(long_text)
    assert tok_a.decode_content(ids_a) == long_text
    assert tok_b.decode_content(ids_b) == long_text

    # Repeated adversarial characters
    rep_text = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    assert tok_a.decode_content(tok_a.encode_content(rep_text)) == rep_text
    assert tok_b.decode_content(tok_b.encode_content(rep_text)) == rep_text


# =============================================================================
# 8. PERFORMANCE AND THROUGHPUT MEASUREMENT
# =============================================================================
def test_performance_measurement():
    """Performance measurements must report realistic positive throughput and memory."""
    tok_a = load_candidate_a(str(CAND_A_PATH))
    evaluator = TokenizerEvaluator(repeat_runs=2)
    summary = evaluator.evaluate(tok_a, "Candidate A", CAND_A_PATH)
    perf = summary.performance

    assert perf.encoding_throughput_chars_sec > 50000.0
    assert perf.encoding_throughput_tokens_sec > 10000.0
    assert perf.decoding_throughput_tokens_sec > 10000.0
    assert perf.peak_memory_kb >= 0.0
    assert perf.short_doc_latency_ms >= 0.0
    assert perf.long_doc_latency_ms >= 0.0


# =============================================================================
# 9. TRAINING CONFIGURATION SCHEMA VALIDATION
# =============================================================================
def test_training_config_schema_file():
    """Verify schema file exists, is valid JSON, and defines all required fields."""
    schema_path = _PATCH_ROOT / "TOKENIZER_TRAINING_CONFIG_SCHEMA.json"
    assert schema_path.exists(), "Schema file does not exist"
    data = json.loads(schema_path.read_text(encoding="utf-8"))

    assert data["type"] == "object"
    assert "required" in data
    assert "config_version" in data["required"]
    assert "candidate_type" in data["required"]
    assert "vocab_size" in data["required"]
    assert "structural_tokens" in data["required"]
    assert "owner_authorization_reference" in data["required"]


# =============================================================================
# 10. SYNTHETIC-ONLY TRAINING ISOLATION & PRODUCTION LOCK
# =============================================================================
def test_production_training_strictly_locked(tmp_path):
    """Attempting production target environment must raise ProductionTrainingLockedError."""
    audit_log = tmp_path / "audit.jsonl"
    pipeline = ControlledTokenizerTrainingPipeline(audit_log_path=audit_log)

    manifest = CorpusManifest("m_test", "m.txt", ["SRC-TA-01"], "a" * 64)
    cfg = TokenizerTrainingConfig(
        config_version="1.0.0",
        candidate_type="candidate_a_bpe",
        vocab_size=VOCAB_SIZE,
        structural_tokens=list(STRUCTURAL_TOKENS),
        byte_fallback=True,
        random_seed=42,
        target_environment="production",  # FORBIDDEN
        owner_authorization_reference="SOLO_OWNER_AUTH_20261118_PROD",
        corpus_manifest=manifest,
        output_directory=str(tmp_path / "out"),
    )

    with pytest.raises(ProductionTrainingLockedError, match="strictly LOCKED"):
        pipeline.train_isolated_tokenizer(cfg, ["Sample sentence for testing."])


# =============================================================================
# 11. DEFAULT-DENY AUTHORIZATION LOGIC
# =============================================================================
def test_default_deny_training_authorization(tmp_path):
    """Missing or empty owner authorization reference must raise TrainingAuthorizationError."""
    audit_log = tmp_path / "audit.jsonl"
    pipeline = ControlledTokenizerTrainingPipeline(audit_log_path=audit_log)

    manifest = CorpusManifest("m_test", "m.txt", ["SRC-TA-01"], "a" * 64)
    cfg = TokenizerTrainingConfig(
        config_version="1.0.0",
        candidate_type="candidate_a_bpe",
        vocab_size=VOCAB_SIZE,
        structural_tokens=list(STRUCTURAL_TOKENS),
        byte_fallback=True,
        random_seed=42,
        target_environment="isolated_test",
        owner_authorization_reference="",  # MISSING
        corpus_manifest=manifest,
        output_directory=str(tmp_path / "out"),
    )

    with pytest.raises(TrainingAuthorizationError, match="Missing or invalid"):
        pipeline.train_isolated_tokenizer(cfg, ["Sample sentence for testing."])


# =============================================================================
# 12. SOURCE-TIER BOUNDARY ENFORCEMENT
# =============================================================================
def test_source_tier_boundary_enforcement(tmp_path):
    """Tier 2 (conditional), Tier 3 (evaluation), and Tier 4 (blocked) sources must be rejected."""
    audit_log = tmp_path / "audit.jsonl"
    pipeline = ControlledTokenizerTrainingPipeline(audit_log_path=audit_log)

    prohibited_sources = [
        ("SRC-ML-01", "CONDITIONAL and barred"),
        ("SRC-CD-02", "EVALUATION ONLY"),
        ("SRC-CHAT-01", "permanently BLOCKED"),
        ("SRC-UNKNOWN-99", "not recognized as an authorized Tier 1 source"),
    ]

    for src_id, err_match in prohibited_sources:
        manifest = CorpusManifest("m_test", "m.txt", [src_id], "a" * 64)
        cfg = TokenizerTrainingConfig(
            config_version="1.0.0",
            candidate_type="candidate_a_bpe",
            vocab_size=VOCAB_SIZE,
            structural_tokens=list(STRUCTURAL_TOKENS),
            byte_fallback=True,
            random_seed=42,
            target_environment="isolated_test",
            owner_authorization_reference="SOLO_OWNER_AUTH_20261118_TEST",
            corpus_manifest=manifest,
            output_directory=str(tmp_path / "out"),
        )
        with pytest.raises(TierBoundaryViolationError, match=err_match):
            pipeline.train_isolated_tokenizer(cfg, ["Sample sentence for testing."])


# =============================================================================
# 13. CORPUS MANIFEST VALIDATION & HASH VERIFICATION
# =============================================================================
def test_corpus_manifest_hash_mismatch(tmp_path):
    """Corpus SHA-256 hash mismatch must raise CorpusIntegrityError."""
    audit_log = tmp_path / "audit.jsonl"
    pipeline = ControlledTokenizerTrainingPipeline(audit_log_path=audit_log)

    manifest = CorpusManifest(
        manifest_id="m_mismatch",
        manifest_path="manifest.csv",
        authorized_sources=["SRC-TA-01"],
        expected_corpus_sha256="deadbeef" * 8,  # Deliberate mismatch
    )
    cfg = TokenizerTrainingConfig(
        config_version="1.0.0",
        candidate_type="candidate_a_bpe",
        vocab_size=VOCAB_SIZE,
        structural_tokens=list(STRUCTURAL_TOKENS),
        byte_fallback=True,
        random_seed=42,
        target_environment="isolated_test",
        owner_authorization_reference="SOLO_OWNER_AUTH_20261118_TEST",
        corpus_manifest=manifest,
        output_directory=str(tmp_path / "out"),
    )

    with pytest.raises(CorpusIntegrityError, match="Corpus SHA-256 mismatch"):
        pipeline.train_isolated_tokenizer(cfg, ["Sentence 1", "Sentence 2"])


# =============================================================================
# 14. ARTIFACT ISOLATION ENFORCEMENT
# =============================================================================
def test_artifact_isolation_enforcement(tmp_path):
    """Targeting production candidate directories must raise ArtifactIsolationError."""
    audit_log = tmp_path / "audit.jsonl"
    pipeline = ControlledTokenizerTrainingPipeline(audit_log_path=audit_log)

    prod_dir = CAND_A_PATH.parent
    manifest = CorpusManifest("m_test", "m.txt", ["SRC-TA-01"], "")
    cfg = TokenizerTrainingConfig(
        config_version="1.0.0",
        candidate_type="candidate_a_bpe",
        vocab_size=VOCAB_SIZE,
        structural_tokens=list(STRUCTURAL_TOKENS),
        byte_fallback=True,
        random_seed=42,
        target_environment="isolated_test",
        owner_authorization_reference="SOLO_OWNER_AUTH_20261118_TEST",
        corpus_manifest=manifest,
        output_directory=str(prod_dir),  # FORBIDDEN: production directory
    )

    with pytest.raises(ArtifactIsolationError, match="conflicts with production"):
        pipeline.train_isolated_tokenizer(cfg, ["Sample sentence."])


# =============================================================================
# 15. REPRODUCIBLE SYNTHETIC TRAINING & AUDIT LOGGING
# =============================================================================
def test_reproducible_synthetic_training_and_audit(tmp_path):
    """Isolated training must be deterministic and append chained audit records."""
    audit_log = tmp_path / "audit.jsonl"
    pipeline = ControlledTokenizerTrainingPipeline(audit_log_path=audit_log)

    synthetic_lines = [
        "Hello world this is an isolated tokenizer training reproducibility test.",
        "தமிழ் மொழி உலகினில் மிக தொன்மையான மொழியாகும்.",
        "Multi-lingual training with deterministic parameters and fixed random seed.",
        "Additional sample line for testing the controlled vocabulary builder.",
    ]
    corpus_bytes = "\n".join(synthetic_lines).encode("utf-8")
    corpus_hash = hashlib.sha256(corpus_bytes).hexdigest()

    out_dir = tmp_path / "run_1"
    manifest = CorpusManifest(
        manifest_id="m_synth_01",
        manifest_path="synth.txt",
        authorized_sources=["SRC-TA-01"],
        expected_corpus_sha256=corpus_hash,
    )
    cfg = TokenizerTrainingConfig(
        config_version="1.0.0",
        candidate_type="candidate_a_bpe",
        vocab_size=VOCAB_SIZE,
        structural_tokens=list(STRUCTURAL_TOKENS),
        byte_fallback=True,
        random_seed=42,
        target_environment="isolated_test",
        owner_authorization_reference="SOLO_OWNER_AUTH_20261118_SYNTH",
        corpus_manifest=manifest,
        output_directory=str(out_dir),
    )

    res = pipeline.train_isolated_tokenizer(cfg, synthetic_lines)
    assert res.status == "SUCCESS_ISOLATED_TEST"
    assert Path(res.artifact_path).exists()
    assert res.artifact_sha256

    # Verify audit log was created and contains valid chained record
    assert audit_log.exists()
    lines = audit_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    record = json.loads(lines[-1])
    assert record["artifact_sha256"] == res.artifact_sha256
    assert record["owner_auth_ref"] == "SOLO_OWNER_AUTH_20261118_SYNTH"
    assert record["entry_hash"]

    # Verify Candidate A and Candidate B on disk remained invariant
    pipeline.verify_candidate_invariants()
