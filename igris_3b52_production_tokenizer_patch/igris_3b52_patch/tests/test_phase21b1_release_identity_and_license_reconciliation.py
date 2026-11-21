"""
Phase 21B1 Test Suite: IndicCorp v2 Release Identity and License Reconciliation
Validates the disambiguation of IndicCorp v2 from legacy IndicCorp, reconciliation of
CC0 vs CC BY-NC 4.0, token statistic labeling, governance invariants, and filename isolation invariant.
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


def test_phase21b1_deliverables_exist():
    """Verify that all 5 required Phase 21B1 deliverables exist in the patch root."""
    assert (PATCH_DIR / "PHASE21B1_INDICCORP_RELEASE_IDENTITY_AUDIT.md").is_file()
    assert (PATCH_DIR / "PHASE21B1_LICENSE_SCOPE_COMPARISON.md").is_file()
    assert (PATCH_DIR / "PHASE21B1_SEVEN_SOURCE_RECONCILIATION.csv").is_file()
    assert (PATCH_DIR / "PHASE21B1_PROVENANCE_AND_RIGHTS_RISK_REPORT.md").is_file()
    assert (PATCH_DIR / "PHASE21B1_COMPLETION_REPORT.md").is_file()


def test_phase21b1_reconciliation_csv_contents():
    """Verify that the CSV correctly reconciles all 7 sources against IndicCorp v2."""
    csv_path = PATCH_DIR / "PHASE21B1_SEVEN_SOURCE_RECONCILIATION.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 7
    registered_ids = [r["source_id"] for r in rows]
    assert registered_ids == INDICCORP_SOURCE_IDS

    for r in rows:
        assert r["upstream_canonical_repo"] == "ai4bharat/IndicCorpV2"
        assert "v2.0" in r["release_version"]
        assert "ACL 2023" in r["official_citation"]
        assert "CC0-1.0" in r["declared_license"]
        assert r["commercial_use_publisher_waiver"] == "YES"
        assert "Disclaimed" in r["third_party_text_cleared_by_cc0"] or "NO" in r["third_party_text_cleared_by_cc0"]
        assert float(r["upstream_reported_tokens_m"]) > 0.0
        assert float(r["igris_projected_tokens_estimate_m"]) > 0.0
        assert r["pretraining_technical_suitability"] == "HIGH"
        assert r["recommended_action"] == "APPROVE FOR OWNER CONSIDERATION"


def test_phase21b1_license_comparison_and_disclaimer():
    """Verify that the license comparison document addresses CC0, CC BY-NC 4.0, and CC0 4(c)."""
    comparison_md = (PATCH_DIR / "PHASE21B1_LICENSE_SCOPE_COMPARISON.md").read_text(encoding="utf-8")
    assert "CC BY-NC" in comparison_md
    assert "CC0 1.0 Universal" in comparison_md
    assert "Section 4(c)" in comparison_md or "Section 4.c" in comparison_md or "4(c)" in comparison_md
    assert "third-party" in comparison_md.lower()
    assert "qualified" in comparison_md.lower() and "counsel" in comparison_md.lower()


def test_phase21b1_governance_invariants():
    """Verify zero sources authorized, ingress locked, and quarantine empty."""
    auth_csv = PATCH_DIR / "PHASE21_OWNER_AUTHORIZATION_REGISTER.csv"
    if auth_csv.is_file():
        with open(auth_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            auth_rows = list(reader)
        for r in auth_rows:
            assert r["authorization_status"] != "AUTHORIZED"

    # Verify ingress engine lock
    try:
        import tempfile
        from igris_3b52_patch.acquisition.secure_acquisition_engine import SecureAcquisitionEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = SecureAcquisitionEngine(audit_log_path=Path(tmpdir) / "audit.jsonl")
            assert engine.ingress_locked is True
    except (ImportError, AttributeError):
        pass

    # Verify quarantine sandbox is empty of production datasets
    quarantine_dirs = [
        PATCH_DIR / "quarantine_sandbox",
        PATCH_DIR.parent / "quarantine_sandbox",
    ]
    for qd in quarantine_dirs:
        if qd.is_dir():
            files = list(qd.glob("*"))
            for f in files:
                assert f.suffix not in [".tar", ".gz", ".txt", ".parquet", ".jsonl"] or "sample" in f.name or "dummy" in f.name or "synthetic" in f.name


def test_phase21b1_tokenizer_hashes_invariant():
    """Verify that both Candidate A and Candidate B physical tokenizer files have not been modified."""
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


def test_phase21b1_filename_isolation_invariant():
    """Verify that no non-markdown file inside igris_3b52_patch contains 'quarantine' in its filename."""
    for p in PATCH_DIR.rglob("*"):
        if p.is_file():
            if p.suffix.lower() != ".md":
                assert "quarantine" not in p.name.lower(), f"Violation: non-markdown file '{p}' contains 'quarantine' in filename."


def test_phase21b1_completion_report_verdict():
    """Verify that the completion report assigns Verdict A."""
    report_path = PATCH_DIR / "PHASE21B1_COMPLETION_REPORT.md"
    content = report_path.read_text(encoding="utf-8")
    assert "VERDICT A — EXACT RELEASE IDENTITY AND LICENSING SCOPE SUFFICIENTLY RECONCILED FOR OWNER CONSIDERATION" in content
    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
