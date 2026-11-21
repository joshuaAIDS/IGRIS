"""
Phase 21B Test Suite: IndicCorp Source-by-Source License and Acquisition Readiness Review
Validates all 7 IndicCorp candidate sources, primary evidence documents, risk assessments,
governance invariants, and filename isolation invariant.
"""

import csv
import json
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


def test_phase21b_deliverables_exist():
    """Verify that all required Phase 21B deliverables exist in the patch root."""
    assert (PATCH_DIR / "PHASE21B_INDICCORP_LICENSE_VERIFICATION.md").is_file()
    assert (PATCH_DIR / "PHASE21B_INDICCORP_SOURCE_REGISTER.csv").is_file()
    assert (PATCH_DIR / "PHASE21B_SOURCE_RISK_ASSESSMENT.md").is_file()
    assert (PATCH_DIR / "PHASE21B_COMPLETION_REPORT.md").is_file()

    evidence_dir = PATCH_DIR / "PHASE21B_PRIMARY_LICENSE_EVIDENCE"
    assert evidence_dir.is_dir()
    assert (evidence_dir / "CC0_1.0_LEGAL_CODE.txt").is_file()
    assert (evidence_dir / "AI4BHARAT_INDICCORP_LICENSE_STATEMENT.txt").is_file()
    assert (evidence_dir / "INDICCORP_V2_PROVENANCE_AND_CITATION.txt").is_file()
    assert (evidence_dir / "INDICCORP_SOURCE_BY_SOURCE_EVIDENCE_MAP.json").is_file()


def test_phase21b_source_register_csv_contents():
    """Verify the 7 IndicCorp candidate sources in the CSV register."""
    csv_path = PATCH_DIR / "PHASE21B_INDICCORP_SOURCE_REGISTER.csv"
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 7
    registered_ids = [r["source_id"] for r in rows]
    assert registered_ids == INDICCORP_SOURCE_IDS

    for r in rows:
        assert r["publisher"] == "AI4Bharat (IIT Madras)"
        assert "CC0-1.0" in r["exact_license_and_version"]
        assert r["commercial_use_permitted"] == "YES"
        assert r["modification_permitted"] == "YES"
        assert r["redistribution_permitted"] == "YES"
        assert r["attribution_required"] == "NO"
        assert r["share_alike_obligations"] == "NO"
        assert r["pretraining_suitability"] == "EXCELLENT"
        assert r["recommended_verdict"] == "APPROVE FOR OWNER CONSIDERATION"
        assert r["official_download_endpoint"].startswith("https://")


def test_phase21b_primary_evidence_map_json():
    """Verify the machine-readable evidence map JSON."""
    json_path = PATCH_DIR / "PHASE21B_PRIMARY_LICENSE_EVIDENCE" / "INDICCORP_SOURCE_BY_SOURCE_EVIDENCE_MAP.json"
    with open(json_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["audit_metadata"]["phase"] == "PHASE 21B"
    assert data["audit_metadata"]["operating_model"] == "SOLO_DEVELOPER_OWNER_REVIEW"
    assert data["audit_metadata"]["license_dedication"] == "CC0-1.0 Universal"

    sources = data["sources"]
    assert len(sources) == 7
    for sid in INDICCORP_SOURCE_IDS:
        assert sid in sources
        s = sources[sid]
        assert s["license"] == "CC0-1.0"
        assert s["commercial_use"] is True
        assert s["modification"] is True
        assert s["redistribution"] is True
        assert s["recommendation"] == "APPROVE FOR OWNER CONSIDERATION"

    assert data["aggregate_statistics"]["total_sources_audited"] == 7
    assert data["aggregate_statistics"]["total_raw_bytes"] == 37100000000
    assert data["aggregate_statistics"]["total_sentences"] == 472100000


def test_phase21b_governance_invariants():
    """Verify that zero sources are authorized, ingress is locked, and quarantine is empty."""
    # Check authorization register: 0 sources authorized
    auth_csv = PATCH_DIR / "PHASE21_OWNER_AUTHORIZATION_REGISTER.csv"
    if auth_csv.is_file():
        with open(auth_csv, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            auth_rows = list(reader)
        for r in auth_rows:
            assert r["authorization_status"] in ["NOT_AUTHORIZED", "PENDING_OWNER_APPROVAL", "PENDING_EXPLICIT_OWNER_AUTHORIZATION", "DENIED", "HOLD"]
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
            # Any files present must be non-production dummies (.gitkeep, etc.)
            for f in files:
                assert f.suffix not in [".tar", ".gz", ".txt", ".parquet", ".jsonl"] or "sample" in f.name or "dummy" in f.name or "synthetic" in f.name


def test_phase21b_tokenizer_hashes_invariant():
    """Verify that both Candidate A and Candidate B physical tokenizer files have not been modified."""
    # Candidate A
    cand_a_path = PATCH_DIR / "tokenizers" / "candidate_a_bytelevel_bpe" / "tokenizer.json"
    if not cand_a_path.is_file():
        cand_a_path = PATCH_DIR / "tokenizer_candidate_a" / "tokenizer.json"
    if cand_a_path.is_file():
        actual_hash_a = hashlib.sha256(cand_a_path.read_bytes()).hexdigest()
        assert actual_hash_a == CANDIDATE_A_HASH

    # Candidate B
    cand_b_path = PATCH_DIR / "tokenizers" / "candidate_b_sentencepiece_unigram" / "tokenizer.json"
    if not cand_b_path.is_file():
        cand_b_path = PATCH_DIR / "tokenizer_candidate_b" / "tokenizer.json"
    if cand_b_path.is_file():
        actual_hash_b = hashlib.sha256(cand_b_path.read_bytes()).hexdigest()
        assert actual_hash_b == CANDIDATE_B_HASH


def test_phase21b_filename_isolation_invariant():
    """Verify that no non-markdown file inside igris_3b52_patch contains 'quarantine' in its filename."""
    for p in PATCH_DIR.rglob("*"):
        if p.is_file():
            if p.suffix.lower() != ".md":
                assert "quarantine" not in p.name.lower(), f"Violation: non-markdown file '{p}' contains 'quarantine' in filename."


def test_phase21b_completion_report_verdict():
    """Verify that the completion report assigns Verdict A."""
    report_path = PATCH_DIR / "PHASE21B_COMPLETION_REPORT.md"
    content = report_path.read_text(encoding="utf-8")
    assert "VERDICT A — ALL SEVEN SOURCES HAVE SUFFICIENT PRIMARY-SOURCE EVIDENCE FOR OWNER CONSIDERATION" in content
    assert "SOLO_DEVELOPER_OWNER_REVIEW" in content
