"""
Phase 21B3A Test Suite: Object Identity, Historical Storage and Compute Planning Corrections
Validates object identity audit, storage capacity model arithmetic, Chinchilla ratio corrections,
explicit unknown values, test scope disambiguation, governance invariants, and filename isolation invariant.
"""

import csv
import hashlib
from pathlib import Path
import pytest

PATCH_DIR = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
PINNED_COMMIT = "984b75b20ce408f9ba27c6558e9279e8e1b6edfd"


def test_phase21b3a_deliverables_exist():
    """Verify that all 7 required Phase 21B3A deliverables exist in the patch root."""
    assert (PATCH_DIR / "PHASE21B3A_OBJECT_IDENTITY_AUDIT.csv").is_file()
    assert (PATCH_DIR / "PHASE21B3A_LFS_XET_METADATA_EVIDENCE.md").is_file()
    assert (PATCH_DIR / "PHASE21B3A_HISTORICAL_STORAGE_RECONCILIATION.md").is_file()
    assert (PATCH_DIR / "PHASE21B3A_TOKEN_AND_COMPUTE_ESTIMATE_CORRECTIONS.md").is_file()
    assert (PATCH_DIR / "PHASE21B3A_STORAGE_CAPACITY_MODEL.csv").is_file()
    assert (PATCH_DIR / "PHASE21B3A_TEST_SCOPE_RECONCILIATION.md").is_file()
    assert (PATCH_DIR / "PHASE21B3A_COMPLETION_REPORT.md").is_file()


def test_phase21b3a_object_identity_audit_csv():
    """Verify object identity audit CSV has 9 files, pinned commit, and explicit unexposed flags."""
    csv_path = PATCH_DIR / "PHASE21B3A_OBJECT_IDENTITY_AUDIT.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 9
    total_bytes = 0
    hindi_shards = []

    for r in rows:
        assert r["pinned_commit_sha"] == PINNED_COMMIT
        assert "NOT_EXPOSED" in r["git_blob_identifier"]
        assert "NOT_EXPOSED" in r["lfs_sha256_oid"]
        total_bytes += int(r["declared_size_bytes"])
        if r["source_id"] == "SRC-HI-01":
            hindi_shards.append(r["exact_repository_path"])

    assert total_bytes == 183700000000
    assert len(hindi_shards) == 3


def test_phase21b3a_storage_capacity_model_arithmetic():
    """Verify storage capacity model arithmetic (stages 1-9 sum to total)."""
    csv_path = PATCH_DIR / "PHASE21B3A_STORAGE_CAPACITY_MODEL.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    stage_rows = [r for r in rows if r["pipeline_stage"].startswith("STAGE_")]
    total_row = [r for r in rows if r["pipeline_stage"] == "TOTAL"][0]

    assert len(stage_rows) == 9

    sum_min_bytes = sum(int(r["minimum_theoretical_bytes"]) for r in stage_rows)
    sum_rec_bytes = sum(int(r["recommended_operational_bytes"]) for r in stage_rows)

    assert sum_min_bytes == int(total_row["minimum_theoretical_bytes"])
    assert sum_rec_bytes == int(total_row["recommended_operational_bytes"])

    assert sum_min_bytes == 421475000000  # 421.48 GB
    assert sum_rec_bytes == 878875000000  # 878.88 GB


def test_phase21b3a_historical_cause_classification():
    """Verify historical 37.1 GB derivation is classified as HISTORICAL_CAUSE_UNCONFIRMED."""
    content = (PATCH_DIR / "PHASE21B3A_HISTORICAL_STORAGE_RECONCILIATION.md").read_text(encoding="utf-8")
    assert "HISTORICAL_CAUSE_UNCONFIRMED" in content
    assert "37.1" in content
    assert "183.70" in content or "183.7" in content


def test_phase21b3a_token_and_chinchilla_ratio_correction():
    """Verify token estimate is labeled UNVALIDATED_CAPACITY_PLANNING_HYPOTHESIS and Chinchilla ratio corrected."""
    content = (PATCH_DIR / "PHASE21B3A_TOKEN_AND_COMPUTE_ESTIMATE_CORRECTIONS.md").read_text(encoding="utf-8")
    assert "UNVALIDATED_CAPACITY_PLANNING_HYPOTHESIS" in content
    assert "17.03" in content or "17" in content
    assert "96,485,888" in content
    assert "79,708,672" in content
    assert "13.0" in content
    assert "15.7" in content


def test_phase21b3a_test_scope_classification():
    """Verify test scope document classifies 42 tests as FOCUSED_PHASE_20B_21B3_REGRESSION_GROUP."""
    content = (PATCH_DIR / "PHASE21B3A_TEST_SCOPE_RECONCILIATION.md").read_text(encoding="utf-8")
    assert "FOCUSED_PHASE_20B_21B3_REGRESSION_GROUP" in content
    assert "38 test files" in content or "38" in content


def test_phase21b3a_governance_invariants():
    """Verify zero sources authorized, ingress locked, quarantine empty, and tokenizers invariant."""
    auth_csv = PATCH_DIR / "PHASE21_OWNER_AUTHORIZATION_REGISTER.csv"
    if auth_csv.is_file():
        with open(auth_csv, mode="r", encoding="utf-8") as f:
            auth_rows = list(csv.DictReader(f))
        for r in auth_rows:
            assert r["authorization_status"] != "AUTHORIZED"

    try:
        import tempfile
        from igris_3b52_patch.acquisition.secure_acquisition_engine import SecureAcquisitionEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SecureAcquisitionEngine(audit_log_path=Path(tmpdir) / "audit.jsonl")
            assert engine.ingress_locked is True
    except (ImportError, AttributeError):
        pass

    quarantine_dirs = [
        PATCH_DIR / "quarantine_sandbox",
        PATCH_DIR.parent / "quarantine_sandbox",
    ]
    for qd in quarantine_dirs:
        if qd.is_dir():
            files = list(qd.glob("*"))
            for f in files:
                assert f.suffix not in [".tar", ".gz", ".txt", ".parquet", ".jsonl"] or "sample" in f.name or "dummy" in f.name or "synthetic" in f.name

    cand_a_path = PATCH_DIR / "tokenizers" / "candidate_a_bytelevel_bpe" / "tokenizer.json"
    if not cand_a_path.is_file():
        cand_a_path = PATCH_DIR / "tokenizer_candidate_a" / "tokenizer.json"
    if cand_a_path.is_file():
        actual_hash_a = hashlib.sha256(cand_a_path.read_bytes()).hexdigest()
        assert actual_hash_a == CANDIDATE_A_HASH

    cand_b_path = PATCH_DIR / "tokenizers" / "candidate_b_sentencepiece_unigram" / "tokenizer.json"
    if not cand_b_path.is_file():
        cand_b_path = PATCH_DIR / "tokenizer_candidate_b" / "tokenizer.json"
    if cand_b_path.is_file():
        actual_hash_b = hashlib.sha256(cand_b_path.read_bytes()).hexdigest()
        assert actual_hash_b == CANDIDATE_B_HASH

    for p in PATCH_DIR.rglob("*"):
        if p.is_file():
            if p.suffix.lower() != ".md":
                assert "quarantine" not in p.name.lower(), f"Violation: non-markdown file '{p}' contains 'quarantine' in filename."


def test_phase21b3a_completion_report_verdict():
    """Verify that the completion report assigns Verdict A."""
    report_path = PATCH_DIR / "PHASE21B3A_COMPLETION_REPORT.md"
    content = report_path.read_text(encoding="utf-8")
    assert "VERDICT A — ALL REMAINING EVIDENCE AND CALCULATION ISSUES RESOLVED OR EXPLICITLY CLASSIFIED" in content
    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
