import csv
import hashlib
import json
from pathlib import Path
import pytest
import sys

PATCH_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PATCH_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from dataset_authorization import (
    REQUIRED_ROLES,
    AuthorizationStatus,
    AuthorizationValidator,
    DatasetAccessDeniedError,
    DatasetAuthorizationRecord,
    SignOffRecord,
    SignOffRole,
)

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

FOUR_CORE_ROLES = [
    "DATA_CUSTODIAN",
    "LEGAL_GOVERNANCE",
    "SECURITY_PRIVACY",
    "CHIEF_ARCHITECT",
]

DUMMY_SIG_HASH = "a" * 64
DUMMY_MANIFEST_HASH = "b" * 64


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_3c9_deliverables_exist():
    required_files = [
        "IGRIS_3C9_GOVERNANCE_READINESS_REPORT.md",
        "HUMAN_REVIEW_PACKAGE_V2.md",
        "REVIEW_DATA_CUSTODIAN_V2.md",
        "REVIEW_LEGAL_GOVERNANCE_V2.md",
        "REVIEW_SECURITY_PRIVACY_V2.md",
        "REVIEW_CHIEF_ARCHITECT_V2.md",
        "SOURCE_HUMAN_REVIEW_MATRIX.csv",
        "PIPELINE_GATE_AUDIT.md",
        "IGRIS_3C9_STATUS.md",
    ]
    for rel_path in required_files:
        p = PATCH_ROOT / rel_path
        assert p.is_file(), f"Missing required 3C.9 file: {rel_path}"
        assert p.stat().st_size > 0, f"Empty 3C.9 file: {rel_path}"


def test_legal_correction_freeze_content():
    india_doc = (PATCH_ROOT / "INDIA_COPYRIGHT_REVIEW.md").read_text(encoding="utf-8")
    assert "Section 22" in india_doc
    assert "Life + 60" in india_doc or "Life+60" in india_doc
    assert "1965" in india_doc
    # Check Section 57 moral rights correction avoiding unsupported blanket claims
    assert "perpetual moral right" in india_doc.lower()
    assert "blanket claims" in india_doc.lower() or "unsupported" in india_doc.lower()

    gutenberg_doc = (PATCH_ROOT / "GUTENBERG_JURISDICTION_REVIEW_V2.md").read_text(encoding="utf-8")
    assert "1928" in gutenberg_doc
    assert "1965" in gutenberg_doc
    assert "1955" in gutenberg_doc
    assert "zero copyright risk globally" in gutenberg_doc.lower()


def test_source_human_review_matrix_schema_and_counts():
    csv_path = PATCH_ROOT / "SOURCE_HUMAN_REVIEW_MATRIX.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in review matrix, got {len(rows)}"

    expected_cols = [
        "source_id",
        "dataset_name",
        "primary_status",
        "license_class",
        "commercial_use_evidence",
        "tokenizer_training_eligibility",
        "tokenizer_evaluation_eligibility",
        "privacy_provenance_risk",
        "required_human_reviewers",
        "final_approval_state",
    ]
    for col in expected_cols:
        assert col in reader.fieldnames, f"Missing column in review matrix: {col}"

    # All 32 sources must be in PENDING final approval state
    for r in rows:
        assert r["final_approval_state"] == "PENDING", (
            f"Source {r['source_id']} final_approval_state must be PENDING, got {r['final_approval_state']}"
        )
        for role in FOUR_CORE_ROLES:
            assert role in r["required_human_reviewers"], (
                f"Role {role} missing from required reviewers in {r['source_id']}"
            )


def test_four_human_review_packages_unpopulated_signatures():
    packages = [
        "REVIEW_DATA_CUSTODIAN_V2.md",
        "REVIEW_LEGAL_GOVERNANCE_V2.md",
        "REVIEW_SECURITY_PRIVACY_V2.md",
        "REVIEW_CHIEF_ARCHITECT_V2.md",
    ]
    for pkg in packages:
        text = (PATCH_ROOT / pkg).read_text(encoding="utf-8")
        assert "PENDING AUTHENTIC HUMAN REVIEW" in text
        assert "Reviewer Full Name" in text
        assert "Digital / Physical Signature" in text
        assert "Date of Review" in text
        assert "SRC-TM-01" in text
        assert "SRC-CV-06" in text
        assert "SRC-EM-02" in text


def test_pipeline_gate_audit_independence_axiom():
    audit_text = (PATCH_ROOT / "PIPELINE_GATE_AUDIT.md").read_text(encoding="utf-8")
    assert "THE INDEPENDENCE AXIOM" in audit_text
    assert "Gate 1: Dataset Acquisition" in audit_text
    assert "Gate 2: Production Data Access" in audit_text
    assert "Gate 3: Tokenizer Vocabulary Training" in audit_text
    assert "Gate 4: Tokenizer Evaluation" in audit_text
    assert "Gate 5: Supervised Fine-Tuning" in audit_text
    assert "Gate 6: Alignment Evaluation" in audit_text
    assert "Gate 7: Safety Evaluation" in audit_text
    assert "NOT AUTHORIZED" in audit_text
    assert "LOCKED" in audit_text


def test_governance_security_missing_signatures():
    # Verify that omitting any required role prevents APPROVED state
    sign_offs = [
        SignOffRecord(SignOffRole.DATA_CUSTODIAN, "Custodian", "2026-11-17T12:00:00Z", DUMMY_SIG_HASH, "APPROVED"),
        SignOffRecord(SignOffRole.LEGAL_GOVERNANCE, "Legal", "2026-11-17T12:00:00Z", DUMMY_SIG_HASH, "APPROVED"),
        SignOffRecord(SignOffRole.SECURITY_PRIVACY, "Security", "2026-11-17T12:00:00Z", DUMMY_SIG_HASH, "APPROVED"),
        # Missing CHIEF_ARCHITECT
    ]
    record = DatasetAuthorizationRecord(
        dataset_id="SYNTH-TEST-01",
        dataset_name="Synthetic Test Dataset",
        version="1.0.0",
        target_milestone="3C.9",
        scope="TOKENIZER_EVALUATION",
        manifest_sha256=DUMMY_MANIFEST_HASH,
        status=AuthorizationStatus.APPROVED,
        screening_verified=True,
        license_approved=True,
        issue_date="2026-11-17T12:00:00Z",
        expiry_date="2027-11-17T12:00:00Z",
        sign_offs=sign_offs,
    )
    is_valid, issues = AuthorizationValidator.verify_authorization(record)
    assert not is_valid
    assert any("CHIEF_ARCHITECT" in err for err in issues)


def test_governance_security_conflicting_decisions_and_invalid_status():
    # 3 Approve, 1 Rejects
    sign_offs = [
        SignOffRecord(SignOffRole.DATA_CUSTODIAN, "Custodian", "2026-11-17T12:00:00Z", DUMMY_SIG_HASH, "APPROVED"),
        SignOffRecord(SignOffRole.LEGAL_GOVERNANCE, "Legal", "2026-11-17T12:00:00Z", DUMMY_SIG_HASH, "APPROVED"),
        SignOffRecord(SignOffRole.SECURITY_PRIVACY, "Security", "2026-11-17T12:00:00Z", DUMMY_SIG_HASH, "REJECTED"),
        SignOffRecord(SignOffRole.CHIEF_ARCHITECT, "Architect", "2026-11-17T12:00:00Z", DUMMY_SIG_HASH, "APPROVED"),
    ]
    record = DatasetAuthorizationRecord(
        dataset_id="SYNTH-TEST-02",
        dataset_name="Synthetic Test Dataset 2",
        version="1.0.0",
        target_milestone="3C.9",
        scope="TOKENIZER_EVALUATION",
        manifest_sha256=DUMMY_MANIFEST_HASH,
        status=AuthorizationStatus.APPROVED,
        screening_verified=True,
        license_approved=True,
        issue_date="2026-11-17T12:00:00Z",
        expiry_date="2027-11-17T12:00:00Z",
        sign_offs=sign_offs,
    )
    is_valid, issues = AuthorizationValidator.verify_authorization(record)
    assert not is_valid
    assert any("REJECTED" in err for err in issues)

    # Test non-APPROVED status (e.g. LOCKED)
    record.status = AuthorizationStatus.LOCKED
    is_valid, issues = AuthorizationValidator.verify_authorization(record)
    assert not is_valid
    assert any("LOCKED" in err for err in issues)


def test_governance_security_tamper_detection_and_expiry():
    # Expired approval
    sign_offs = [
        SignOffRecord(role, f"Tester {role.value}", "2024-01-01T12:00:00Z", DUMMY_SIG_HASH, "APPROVED")
        for role in SignOffRole
    ]
    record = DatasetAuthorizationRecord(
        dataset_id="SYNTH-TEST-03",
        dataset_name="Synthetic Test Dataset 3",
        version="1.0.0",
        target_milestone="3C.9",
        scope="TOKENIZER_EVALUATION",
        manifest_sha256=DUMMY_MANIFEST_HASH,
        status=AuthorizationStatus.APPROVED,
        screening_verified=True,
        license_approved=True,
        issue_date="2024-01-01T12:00:00Z",
        expiry_date="2024-06-01T12:00:00Z",  # In the past
        sign_offs=sign_offs,
    )
    is_valid, issues = AuthorizationValidator.verify_authorization(record)
    assert not is_valid
    assert any("expired" in err.lower() for err in issues)

    # Tampered manifest hash format (not 64-hex)
    record.expiry_date = "2027-01-01T12:00:00Z"
    record.manifest_sha256 = "invalid_short_hash"
    is_valid, issues = AuthorizationValidator.verify_authorization(record)
    assert not is_valid
    assert any("manifest_sha256" in err for err in issues)


def test_candidate_invariants_preserved():
    cand_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    assert cand_a.exists(), f"Candidate A missing at {cand_a}"
    assert cand_b.exists(), f"Candidate B missing at {cand_b}"
    assert sha256_file(cand_a) == CANDIDATE_A_HASH
    assert sha256_file(cand_b) == CANDIDATE_B_HASH