"""IGRIS Phase 7: Approval Intake Validation & Source Authorization Test Suite.

Rigorously tests:
1. Valid authentic signatures (using synthetic test keys).
2. Invalid signatures.
3. Missing signatures.
4. Expired signatures.
5. Revoked keys.
6. Role mismatches / privilege escalation.
7. Source ID mismatches & malformed source identifiers.
8. Approval scope mismatches & cross-pipeline isolation (Independence Axiom).
9. Replayed approval submissions.
10. Modified review documents (live disk SHA-256 tampering).
11. Four-role unanimous consensus required for quarantine staging eligibility.
12. Veto power of REJECT / REQUEST_CHANGES.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import pytest
import sys

PATCH_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PATCH_ROOT / "scripts"
SRC_DIR = PATCH_ROOT / "src"
for p in [str(SCRIPTS_DIR), str(SRC_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from review_intake_verifier import (
    AuditRecord,
    AuditTrailLogger,
    KeyRecord,
    KeyRegistry,
    QuorumEngine,
    QuorumState,
    ReviewDecision,
    ReviewIntakeVerifier,
    SignOffRole,
    canonical_json_bytes,
    compute_signature,
    verify_signature,
)
from dataset_authorization import (
    AuthorizationStatus,
    AuthorizationValidator,
    DatasetAccessDeniedError,
)

SYNTHETIC_PHASE7_SECRET = "phase7_synthetic_test_secret_key_9988776655"


def _create_phase7_registry() -> KeyRegistry:
    registry = KeyRegistry()
    roles = [
        SignOffRole.DATA_CUSTODIAN,
        SignOffRole.LEGAL_GOVERNANCE,
        SignOffRole.SECURITY_PRIVACY,
        SignOffRole.CHIEF_ARCHITECT,
    ]
    for r in roles:
        registry.register_key(
            KeyRecord(
                key_id=f"KEY-{r.value}-P7",
                role=r,
                secret_key=f"{SYNTHETIC_PHASE7_SECRET}_{r.value}",
                created_at="2026-11-17T00:00:00Z",
                expires_at="2027-11-17T00:00:00Z",
            )
        )
    return registry


def _build_intake_payload(
    role: SignOffRole,
    submission_id: str = "SUB-P7CUST0001",
    source_ids: Optional[List[str]] = None,
    decision: str = "APPROVE",
    document_hash: str = "d" * 64,
    expiry_date: str = "2027-11-17T12:00:00Z",
    secret: Optional[str] = None,
    key_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    sec = secret or f"{SYNTHETIC_PHASE7_SECRET}_{role.value}"
    kid = key_id or f"KEY-{role.value}-P7"
    actual_source_ids = ["SRC-TM-01"] if source_ids is None else source_ids
    sub: Dict[str, Any] = {
        "submission_id": submission_id,
        "reviewer_identity": f"{role.value.lower()}@igris-governance.org",
        "role": role.value,
        "public_key_id": kid,
        "source_ids_reviewed": actual_source_ids,
        "decision": decision,
        "evidence_references": [
            {
                "reference_type": "CATALOG",
                "reference_uri": "file:///DATASET_SOURCE_CATALOG_V3.csv",
                "sha256": "1" * 64,
            }
        ],
        "document_sha256": document_hash,
        "timestamp": "2026-11-17T12:00:00Z",
        "expiry_date": expiry_date,
    }
    if notes:
        sub["notes"] = notes
    canon = canonical_json_bytes(sub)
    sub["digital_signature"] = compute_signature(canon, sec)
    return sub


# ==============================================================================
# TEST 1: Valid Authentic Intake Submission
# ==============================================================================
def test_valid_authentic_intake_submission():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _build_intake_payload(role=SignOffRole.DATA_CUSTODIAN)
    res = verifier.verify_submission(sub)

    assert res.is_valid
    assert len(res.errors) == 0
    assert res.role == SignOffRole.DATA_CUSTODIAN
    assert res.decision == ReviewDecision.APPROVE


# ==============================================================================
# TEST 2: Invalid Signature
# ==============================================================================
def test_invalid_signature_fails_closed():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _build_intake_payload(role=SignOffRole.LEGAL_GOVERNANCE)
    # Mutate signature characters
    sub["digital_signature"] = "0" * len(sub["digital_signature"])

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("signature verification failed" in e for e in res.errors)


# ==============================================================================
# TEST 3: Missing Signature
# ==============================================================================
def test_missing_signature_fails_closed():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _build_intake_payload(role=SignOffRole.SECURITY_PRIVACY)
    del sub["digital_signature"]

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("Missing digital signature" in e for e in res.errors)


# ==============================================================================
# TEST 4: Expired Signature / Approval
# ==============================================================================
def test_expired_signature_fails_closed():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _build_intake_payload(
        role=SignOffRole.CHIEF_ARCHITECT,
        expiry_date="2026-01-01T00:00:00Z",
    )
    ref_time = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)
    res = verifier.verify_submission(sub, reference_time=ref_time)

    assert not res.is_valid
    assert any("expired" in e for e in res.errors)


# ==============================================================================
# TEST 5: Revoked Key Rejection
# ==============================================================================
def test_revoked_key_fails_closed():
    registry = _create_phase7_registry()
    revoked_kid = "KEY-LEGAL_GOVERNANCE-P7"
    registry.revoke_key(revoked_kid, reason="Key compromised in security drill")

    verifier = ReviewIntakeVerifier(registry)
    sub = _build_intake_payload(role=SignOffRole.LEGAL_GOVERNANCE, key_id=revoked_kid)

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("has been revoked" in e for e in res.errors)
    assert any("Key compromised in security drill" in e for e in res.errors)


# ==============================================================================
# TEST 6: Role Mismatch / Privilege Escalation
# ==============================================================================
def test_role_mismatch_fails_closed():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    # Use Data Custodian key to sign as Chief Architect
    sub = _build_intake_payload(
        role=SignOffRole.CHIEF_ARCHITECT,
        key_id="KEY-DATA_CUSTODIAN-P7",
        secret=f"{SYNTHETIC_PHASE7_SECRET}_DATA_CUSTODIAN",
    )

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("cannot sign as 'CHIEF_ARCHITECT'" in e for e in res.errors)


# ==============================================================================
# TEST 7: Source ID Mismatches & Malformed Source Identifiers
# ==============================================================================
def test_source_id_mismatch_and_malformed_fails_closed():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    # Malformed source ID (invalid pattern)
    sub_malformed = _build_intake_payload(
        role=SignOffRole.DATA_CUSTODIAN,
        source_ids=["INVALID_SOURCE_ID_999"],
    )
    res_malformed = verifier.verify_submission(sub_malformed)
    assert not res_malformed.is_valid
    assert any("Malformed source ID" in e for e in res_malformed.errors)

    # Empty source ID list
    sub_empty = _build_intake_payload(
        role=SignOffRole.DATA_CUSTODIAN,
        source_ids=[],
    )
    res_empty = verifier.verify_submission(sub_empty)
    assert not res_empty.is_valid
    assert any("source_ids_reviewed must be a non-empty list" in e for e in res_empty.errors)


# ==============================================================================
# TEST 8: Approval Scope Independence (Source Isolation)
# ==============================================================================
def test_approval_scope_independence_axiom():
    """Verify that approving a source for evaluation NEVER authorizes vocab training or SFT."""
    pipe_path = PATCH_ROOT / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv"
    with open(pipe_path, "r", encoding="utf-8") as f:
        pipe_rows = {r["source_id"]: r for r in csv.DictReader(f)}

    # SRC-CV-04 (Anthropic HH-RLHF) is eligible for evaluation, but STRICTLY PROHIBITED from vocab training
    hh_rlhf = pipe_rows["SRC-CV-04"]
    assert "ELIGIBLE" in hh_rlhf["tokenizer_fertility_evaluation"]
    assert hh_rlhf["tokenizer_vocab_training"] in ["STRICTLY_PROHIBITED", "INELIGIBLE_REJECTED"]
    assert hh_rlhf["supervised_fine_tuning"] == "NOT AUTHORIZED"

    # All 32 sources have SFT completely locked
    for sid, row in pipe_rows.items():
        assert row["supervised_fine_tuning"] == "NOT AUTHORIZED", f"{sid} has unapproved SFT scope"


# ==============================================================================
# TEST 9: Replayed Approval Submissions Fail Closed
# ==============================================================================
def test_replayed_approval_submission_fails_closed():
    """Adversary attempts to replay signature across modified payload."""
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub_orig = _build_intake_payload(role=SignOffRole.DATA_CUSTODIAN, source_ids=["SRC-TM-01"])
    res_orig = verifier.verify_submission(sub_orig)
    assert res_orig.is_valid

    # Replay signature on different timestamp
    sub_replayed = copy.deepcopy(sub_orig)
    sub_replayed["timestamp"] = "2026-11-17T13:00:00Z"
    res_replayed = verifier.verify_submission(sub_replayed)
    assert not res_replayed.is_replayed if hasattr(res_replayed, "is_replayed") else not res_replayed.is_valid
    assert any("signature verification failed" in e for e in res_replayed.errors)


# ==============================================================================
# TEST 10: Modified Review Documents (Live Disk SHA-256 Check)
# ==============================================================================
def test_modified_review_document_fails_closed():
    """Review document on disk is modified by a single byte; intake fails closed."""
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tmp:
        tmp.write("# Genuine Review Dossier\nAuthentic evaluation notes.\n")
        tmp_path = Path(tmp.name)

    try:
        genuine_hash = hashlib.sha256(tmp_path.read_bytes()).hexdigest()

        # Submit claiming genuine hash
        sub = _build_intake_payload(
            role=SignOffRole.LEGAL_GOVERNANCE,
            document_hash=genuine_hash,
        )

        # Confirm valid with unmodified document
        res_valid = verifier.verify_submission(sub, document_path=tmp_path)
        assert res_valid.is_valid

        # Attack: Modify document on disk by appending a single space
        with open(tmp_path, "a", encoding="utf-8") as f:
            f.write(" ")

        # Re-verify -> MUST FAIL
        res_tampered = verifier.verify_submission(sub, document_path=tmp_path)
        assert not res_tampered.is_valid
        assert any("Document SHA256 mismatch" in e for e in res_tampered.errors)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ==============================================================================
# TEST 11: Four-Role Unanimous Consensus Required for Quarantine Staging
# ==============================================================================
def test_unanimous_consensus_required_for_quarantine_staging():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-TM-01"

    # Only 3 roles sign APPROVE (missing Security/Privacy)
    submissions = []
    for role in [
        SignOffRole.DATA_CUSTODIAN,
        SignOffRole.LEGAL_GOVERNANCE,
        SignOffRole.CHIEF_ARCHITECT,
    ]:
        sub = _build_intake_payload(
            role=role,
            submission_id=f"SUB-P7{role.value.replace('_', '')[:4]}01",
            source_ids=[source_id],
            decision="APPROVE",
        )
        res = verifier.verify_submission(sub)
        assert res.is_valid
        submissions.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    # Must remain PENDING until Security & Privacy approves
    assert quorum_state == QuorumState.PENDING
    assert any("Quorum incomplete" in r for r in reasons)

    # Now add Security & Privacy sign-off
    sec_sub = _build_intake_payload(
        role=SignOffRole.SECURITY_PRIVACY,
        submission_id="SUB-P7SECU0001",
        source_ids=[source_id],
        decision="APPROVE",
    )
    res_sec = verifier.verify_submission(sec_sub)
    assert res_sec.is_valid
    submissions.append(res_sec)

    quorum_approved, reasons_app = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    assert quorum_approved == QuorumState.APPROVED
    assert any("unanimous 4-of-4 approval consensus" in r for r in reasons_app)


# ==============================================================================
# TEST 12: Veto Power of Single Rejection
# ==============================================================================
def test_single_rejection_overrides_all_approvals():
    registry = _create_phase7_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-HI-03"  # Incompatible CC-BY-NC-SA

    submissions = []
    # 3 approve, but Legal Governance REJECTS
    for role, dec in [
        (SignOffRole.DATA_CUSTODIAN, "APPROVE"),
        (SignOffRole.LEGAL_GOVERNANCE, "REJECT"),
        (SignOffRole.SECURITY_PRIVACY, "APPROVE"),
        (SignOffRole.CHIEF_ARCHITECT, "APPROVE"),
    ]:
        sub = _build_intake_payload(
            role=role,
            submission_id=f"SUB-P7{role.value.replace('_', '')[:4]}02",
            source_ids=[source_id],
            decision=dec,
        )
        res = verifier.verify_submission(sub)
        assert res.is_valid
        submissions.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    assert quorum_state == QuorumState.BLOCKED_REJECTED
    assert any("explicit REJECT decision" in r for r in reasons)
