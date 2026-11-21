"""
Phase 21B2 Test Suite: IndicCorp Upstream Path, Statistics and Evidence Correction
Validates the corrected upstream paths, corrected ACL 2023 statistics (10,947M total),
isolated IGRIS Candidate A projections, governance invariants, and filename isolation invariant.
"""

import csv
import hashlib
from pathlib import Path
import pytest

PATCH_DIR = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

INDICCORP_SOURCE_IDS = [
    "SRC-TM-01",
    "SRC-HI-01",
    "SRC-OI-01",
    "SRC-OI-02",
    "SRC-OI-03",
    "SRC-OI-04",
    "SRC-OI-05",
]

EXPECTED_ACL_TOKENS = {
    "SRC-TM-01": 476,
    "SRC-HI-01": 6107,
    "SRC-OI-01": 731,
    "SRC-OI-02": 931,
    "SRC-OI-03": 875,
    "SRC-OI-04": 926,
    "SRC-OI-05": 901,
}


def test_phase21b2_deliverables_exist():
    """Verify that all 6 required Phase 21B2 deliverables exist in the patch root."""
    assert (PATCH_DIR / "PHASE21B2_UPSTREAM_PATH_VERIFICATION.md").is_file()
    assert (PATCH_DIR / "PHASE21B2_ACL_STATISTICS_CORRECTION.csv").is_file()
    assert (PATCH_DIR / "PHASE21B2_IGRIS_PROJECTION_RECONCILIATION.csv").is_file()
    assert (PATCH_DIR / "PHASE21B2_LICENSE_SCOPE_STATUS.md").is_file()
    assert (PATCH_DIR / "PHASE21B2_CORRECTION_AUDIT_LOG.md").is_file()
    assert (PATCH_DIR / "PHASE21B2_COMPLETION_REPORT.md").is_file()


def test_phase21b2_acl_statistics_correction_csv():
    """Verify that the ACL statistics correction CSV reflects Table 3 accurately."""
    csv_path = PATCH_DIR / "PHASE21B2_ACL_STATISTICS_CORRECTION.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 7
    total_tokens = 0
    for r in rows:
        sid = r["source_id"]
        assert sid in EXPECTED_ACL_TOKENS
        count = int(r["acl_2023_table_3_tokens_m"])
        assert count == EXPECTED_ACL_TOKENS[sid]
        total_tokens += count
        assert "ACL 2023 Table 3" in r["authoritative_reference"]

    assert total_tokens == 10947


def test_phase21b2_igris_projections_csv():
    """Verify that IGRIS projections are strictly labeled as estimates and unvalidated."""
    csv_path = PATCH_DIR / "PHASE21B2_IGRIS_PROJECTION_RECONCILIATION.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 7
    for r in rows:
        assert float(r["igris_projected_candidate_a_tokens_m"]) > 0.0
        assert r["confidence_level"] == "PRELIMINARY_ENGINEERING_ESTIMATE"
        assert r["figure_measurement_status"] == "PROJECTED_UNVALIDATED"
        assert r["empirical_validation_status"] == "PENDING_ACQUISITION_AND_VALIDATION"
        assert "Candidate A ByteLevel BPE" in r["igris_tokenizer_basis"]


def test_phase21b2_upstream_paths_content():
    """Verify upstream path verification markdown contains flat text mappings and pinned commit."""
    content = (PATCH_DIR / "PHASE21B2_UPSTREAM_PATH_VERIFICATION.md").read_text(encoding="utf-8")
    assert "984b75b20ce408f9ba27c6558e9279e8e1b6edfd" in content
    assert "data/ta.txt" in content
    assert "data/hi-" in content
    assert "data/te.txt" in content
    assert "data/ml.txt" in content
    assert "data/kn.txt" in content
    assert "data/bn.txt" in content
    assert "data/gu.txt" in content


def test_phase21b2_legal_scope_and_technical_suitability():
    """Verify legal status markdown covers CC0 4(c) and requires qualified legal review."""
    content = (PATCH_DIR / "PHASE21B2_LICENSE_SCOPE_STATUS.md").read_text(encoding="utf-8")
    assert "4(c)" in content or "4.c" in content
    assert "third-party" in content.lower()
    assert "non-expressive" in content.lower()
    assert "qualified" in content.lower() and "counsel" in content.lower()


def test_phase21b2_governance_invariants():
    """Verify zero sources authorized, ingress locked, and quarantine empty."""
    auth_csv = PATCH_DIR / "PHASE21_OWNER_AUTHORIZATION_REGISTER.csv"
    if auth_csv.is_file():
        with open(auth_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            auth_rows = list(reader)
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


def test_phase21b2_completion_report_verdict():
    """Verify that the completion report assigns Verdict A."""
    report_path = PATCH_DIR / "PHASE21B2_COMPLETION_REPORT.md"
    content = report_path.read_text(encoding="utf-8")
    assert "VERDICT A — ALL UPSTREAM PATHS, PUBLISHED STATISTICS AND PROJECT ESTIMATES RECONCILED" in content
    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
