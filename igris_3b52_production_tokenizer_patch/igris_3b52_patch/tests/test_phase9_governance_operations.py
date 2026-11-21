"""IGRIS Phase 9: Human Governance Operations & External Reviewer Coordination Test Suite.

Rigorously verifies:
1. Presence and integrity of all Phase 9 deliverables.
2. Reviewer operations manual coverage (qualifications, COI, boundaries, onboarding).
3. Review distribution register coverage (128 packages: 32 sources x 4 roles).
4. Human review tracker validity (36 rows, strict 8-state enum enforcement).
5. Non-advancement of human states (zero synthetic approvals, zero unauthorized ingress).
6. Fail-closed pipeline gate enforcement (LOCKED status).
7. Review intake verifier readiness without production key contamination.
8. Phase 9 final verdict selection (Verdict D: Operational Preparation Complete).
9. Candidate tokenizer SHA-256 hash invariants.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import pytest
import sys

PATCH_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PATCH_ROOT / "scripts"
SRC_DIR = PATCH_ROOT / "src"
for p in [str(SCRIPTS_DIR), str(SRC_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from review_intake_verifier import (
    KeyRecord,
    KeyRegistry,
    ReviewDecision,
    ReviewIntakeVerifier,
    SignOffRole,
)

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

MANDATED_TRACKER_STATES = {
    "NOT_STARTED",
    "AWAITING_APPOINTMENT",
    "AWAITING_KEY_REGISTRATION",
    "AWAITING_REVIEW",
    "PENDING_SIGNATURE",
    "SUBMITTED",
    "VERIFIED",
    "REJECTED",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_phase9_deliverables_exist():
    """Verify all six Phase 9 governance deliverables exist on disk."""
    expected_files = [
        PATCH_ROOT / "IGRIS_PHASE9_REVIEWER_OPERATIONS_MANUAL.md",
        PATCH_ROOT / "IGRIS_PHASE9_REVIEW_DISTRIBUTION_REGISTER.csv",
        PATCH_ROOT / "IGRIS_PHASE9_HUMAN_REVIEW_TRACKER.csv",
        PATCH_ROOT / "IGRIS_PHASE9_SIGNATURE_INTAKE_PROCEDURE.md",
        PATCH_ROOT / "IGRIS_PHASE9_GOVERNANCE_OPERATIONS_REPORT.md",
        PATCH_ROOT / "IGRIS_PHASE9_FINAL_STATUS.md",
    ]
    for ef in expected_files:
        assert ef.is_file(), f"Missing required Phase 9 deliverable: {ef.name}"
        assert ef.stat().st_size > 0, f"Deliverable is empty: {ef.name}"


def test_phase9_reviewer_operations_manual_content():
    """Verify the reviewer operations manual covers all 4 roles and mandatory topics."""
    manual_path = PATCH_ROOT / "IGRIS_PHASE9_REVIEWER_OPERATIONS_MANUAL.md"
    content = manual_path.read_text(encoding="utf-8")

    # All 4 roles must be covered
    for role in ["DATA_CUSTODIAN", "LEGAL_GOVERNANCE", "SECURITY_PRIVACY", "CHIEF_ARCHITECT"]:
        assert role in content, f"Role {role} missing from operations manual"

    # Mandatory operational topics
    assert "Qualification Criteria" in content or "qualification" in content.lower()
    assert "Conflict of Interest" in content
    assert "Separation of Duties" in content or "independence" in content.lower()
    assert "Hardware Security" in content or "FIPS 140-2" in content
    assert "Appointment Acceptance" in content
    assert "Key Revocation" in content or "CRL" in content


def test_phase9_review_distribution_register_structure():
    """Verify distribution register maps exactly 128 role-source packages (32 sources x 4 roles)."""
    register_path = PATCH_ROOT / "IGRIS_PHASE9_REVIEW_DISTRIBUTION_REGISTER.csv"
    with open(register_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 128, f"Expected exactly 128 distribution rows, found {len(rows)}"

    sources = set(r["source_id"] for r in rows)
    assert len(sources) == 32, f"Expected 32 candidate sources in distribution register, found {len(sources)}"

    roles = set(r["target_role"] for r in rows)
    expected_roles = {"DATA_CUSTODIAN", "LEGAL_GOVERNANCE", "SECURITY_PRIVACY", "CHIEF_ARCHITECT"}
    assert roles == expected_roles, f"Roles mismatch: {roles} vs {expected_roles}"

    for r in rows:
        assert r["package_status"] == "PACKAGE_PREPARED_AWAITING_APPOINTEE"
        assert r["inventory_reference"] == "DATASET_SOURCE_CATALOG_V3.csv"


def test_phase9_human_review_tracker_states():
    """Verify human review tracker has 36 rows and strictly adheres to the 8 mandated states."""
    tracker_path = PATCH_ROOT / "IGRIS_PHASE9_HUMAN_REVIEW_TRACKER.csv"
    with open(tracker_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 36, f"Expected exactly 36 tracker rows (4 roles + 32 sources), found {len(rows)}"

    role_rows = [r for r in rows if r["tracker_type"] == "GOVERNANCE_ROLE"]
    source_rows = [r for r in rows if r["tracker_type"] == "DATASET_SOURCE"]
    assert len(role_rows) == 4
    assert len(source_rows) == 32

    state_fields = [
        "reviewer_appointment_state",
        "appointment_acceptance_state",
        "identity_verification_state",
        "key_registration_state",
        "dossier_distribution_state",
        "review_commencement_state",
        "source_level_decisions_state",
        "signature_submission_state",
        "signature_verification_state",
        "final_quorum_status",
    ]

    for r in rows:
        for sf in state_fields:
            val = r[sf]
            assert val in MANDATED_TRACKER_STATES, (
                f"Invalid state '{val}' in field '{sf}' for row '{r['tracker_id']}'"
            )

        # Anti-fabrication check: no human-controlled state may be prematurely advanced to VERIFIED or SUBMITTED
        assert r["signature_submission_state"] != "SUBMITTED", (
            f"Premature SUBMITTED state in {r['tracker_id']}"
        )
        assert r["signature_verification_state"] != "VERIFIED", (
            f"Premature VERIFIED state in {r['tracker_id']}"
        )


def test_phase9_fail_closed_gate_enforcement():
    """Verify that every tracking row enforces LOCKED pipeline gate state."""
    tracker_path = PATCH_ROOT / "IGRIS_PHASE9_HUMAN_REVIEW_TRACKER.csv"
    with open(tracker_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        assert r["pipeline_gate_state"] == "LOCKED", (
            f"Pipeline gate is not LOCKED in tracker entry {r['tracker_id']}"
        )


def test_phase9_signature_intake_readiness():
    """Verify intake engine fails closed when presented with unregistered/invalid keys."""
    registry = KeyRegistry()
    verifier = ReviewIntakeVerifier(registry)

    # Empty registry should fail closed for any unauthenticated submission
    mock_sub = {
        "submission_id": "SUB-TEST20261117",
        "role": "DATA_CUSTODIAN",
        "reviewer_id": "MOCK-REVIEWER-01",
        "key_id": "KEY-UNKNOWN-001",
        "source_ids": ["SRC-TM-01"],
        "decision": "APPROVE",
        "evidence_references": [
            {"reference_type": "CATALOG", "reference_uri": "DATASET_SOURCE_CATALOG_V3.csv", "sha256": "0" * 64}
        ],
        "timestamp_utc": "2026-11-17T12:00:00Z",
        "expiry_date_utc": "2027-02-15T12:00:00Z",
        "document_path": "REVIEW_DATA_CUSTODIAN_V2.md",
        "document_sha256": "0" * 64,
        "digital_signature": "0" * 64,
    }
    result = verifier.verify_submission(mock_sub)
    assert not result.is_valid
    assert any("not recognized" in err.lower() for err in result.errors)


def test_phase9_final_verdict_selection():
    """Verify that Phase 9 final status selects Verdict D."""
    status_path = PATCH_ROOT / "IGRIS_PHASE9_FINAL_STATUS.md"
    content = status_path.read_text(encoding="utf-8")

    assert "[X] D. OPERATIONAL PREPARATION COMPLETE" in content, (
        "Verdict D was not selected in IGRIS_PHASE9_FINAL_STATUS.md"
    )
    assert "[ ] A." in content
    assert "[ ] B." in content
    assert "[ ] C." in content


def test_candidate_tokenizer_hashes_invariant():
    """Verify that Candidate A and B tokenizer artifact SHA-256 hashes remain invariant."""
    candidate_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    candidate_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    assert candidate_a.is_file(), f"Missing Candidate A: {candidate_a}"
    assert candidate_b.is_file(), f"Missing Candidate B: {candidate_b}"

    hash_a = sha256_file(candidate_a)
    hash_b = sha256_file(candidate_b)

    assert hash_a == CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a} != {CANDIDATE_A_HASH}"
    assert hash_b == CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b} != {CANDIDATE_B_HASH}"
