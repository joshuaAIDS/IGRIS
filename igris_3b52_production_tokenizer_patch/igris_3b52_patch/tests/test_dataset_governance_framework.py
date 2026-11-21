"""IGRIS Dataset Authorization and Governance Framework Comprehensive Test Suite.

Validates the full fail-closed governance framework:
1. Quorum consensus engine (4-of-4 requirement, veto handling).
2. Cryptographic signature and key validation (HMAC-SHA256, CRL, role-binding).
3. Document integrity verification (live SHA-256 vs submission).
4. Append-only tamper-evident hash-chained audit logging.
5. Programmatic access gatekeeper fail-closed enforcement.
6. Multi-register consistency across all 32 candidate sources.
7. Candidate A and Candidate B immutability invariants.
"""

from __future__ import annotations

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

from dataset_authorization import (
    REQUIRED_ROLES as AUTH_REQUIRED_ROLES,
    AuthorizationStatus,
    AuthorizationValidator,
    DatasetAccessDeniedError,
    DatasetAuthorizationRecord,
    SignOffRecord,
    SignOffRole as AuthSignOffRole,
)
from review_intake_verifier import (
    AuditRecord,
    AuditTrailLogger,
    KeyRecord,
    KeyRegistry,
    QuorumEngine,
    QuorumState,
    ReviewDecision,
    ReviewIntakeVerifier,
    SignOffRole as IntakeSignOffRole,
    canonical_json_bytes,
    compute_signature,
    verify_signature,
)

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

SYNTHETIC_TEST_SECRET = "gov_test_secret_key_secure_token_987654321"


def _create_test_key_registry() -> KeyRegistry:
    reg = KeyRegistry()
    roles = [
        IntakeSignOffRole.DATA_CUSTODIAN,
        IntakeSignOffRole.LEGAL_GOVERNANCE,
        IntakeSignOffRole.SECURITY_PRIVACY,
        IntakeSignOffRole.CHIEF_ARCHITECT,
    ]
    for r in roles:
        reg.register_key(
            KeyRecord(
                key_id=f"KEY-{r.value}-001",
                role=r,
                secret_key=f"{SYNTHETIC_TEST_SECRET}_{r.value}",
                created_at="2026-11-17T00:00:00Z",
                expires_at="2027-11-17T00:00:00Z",
            )
        )
    return reg


def _make_signed_intake_submission(
    role: IntakeSignOffRole,
    decision: str = "APPROVE",
    source_ids: Optional[List[str]] = None,
    document_hash: Optional[str] = None,
    expiry_date: str = "2027-11-17T12:00:00Z",
    key_id: Optional[str] = None,
    secret_key: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    kid = key_id or f"KEY-{role.value}-001"
    sec = secret_key or f"{SYNTHETIC_TEST_SECRET}_{role.value}"
    doc_h = document_hash or ("a" * 64)

    role_code = {
        IntakeSignOffRole.DATA_CUSTODIAN: "CUST",
        IntakeSignOffRole.LEGAL_GOVERNANCE: "LEGL",
        IntakeSignOffRole.SECURITY_PRIVACY: "SECU",
        IntakeSignOffRole.CHIEF_ARCHITECT: "ARCH",
    }.get(role, "USER")

    sub: Dict[str, Any] = {
        "submission_id": f"SUB-{role_code}20261117",
        "reviewer_identity": f"{role.value.lower()}@igris-governance.org",
        "role": role.value,
        "public_key_id": kid,
        "source_ids_reviewed": source_ids or ["SRC-TM-01"],
        "decision": decision,
        "evidence_references": [
            {
                "reference_type": "CATALOG",
                "reference_uri": "file:///DATASET_SOURCE_CATALOG_V3.csv",
                "sha256": "c" * 64,
            }
        ],
        "document_sha256": doc_h,
        "timestamp": "2026-11-17T12:00:00Z",
        "expiry_date": expiry_date,
    }
    if notes:
        sub["notes"] = notes

    canon_bytes = canonical_json_bytes(sub)
    sig = compute_signature(canon_bytes, sec)
    sub["digital_signature"] = sig
    return sub


# ==============================================================================
# 1. QUORUM ENGINE POSITIVE & NEGATIVE TESTS
# ==============================================================================

def test_unanimous_four_of_four_approval_reaches_approved():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-TM-01"

    submissions = []
    for role in [
        IntakeSignOffRole.DATA_CUSTODIAN,
        IntakeSignOffRole.LEGAL_GOVERNANCE,
        IntakeSignOffRole.SECURITY_PRIVACY,
        IntakeSignOffRole.CHIEF_ARCHITECT,
    ]:
        sub = _make_signed_intake_submission(role=role, decision="APPROVE", source_ids=[source_id])
        res = verifier.verify_submission(sub)
        assert res.is_valid, f"Verification failed: {res.errors}"
        submissions.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    assert quorum_state == QuorumState.APPROVED
    assert any("unanimous 4-of-4" in r for r in reasons)


def test_single_rejection_vetoes_to_blocked_rejected():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-TM-02"

    submissions = []
    # 3 approve, 1 rejects
    for role, dec in [
        (IntakeSignOffRole.DATA_CUSTODIAN, "APPROVE"),
        (IntakeSignOffRole.LEGAL_GOVERNANCE, "REJECT"),
        (IntakeSignOffRole.SECURITY_PRIVACY, "APPROVE"),
        (IntakeSignOffRole.CHIEF_ARCHITECT, "APPROVE"),
    ]:
        sub = _make_signed_intake_submission(role=role, decision=dec, source_ids=[source_id])
        res = verifier.verify_submission(sub)
        assert res.is_valid
        submissions.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    assert quorum_state == QuorumState.BLOCKED_REJECTED
    assert any("explicit REJECT" in r for r in reasons)


def test_request_changes_blocks_approval():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-TM-03"

    submissions = []
    for role, dec in [
        (IntakeSignOffRole.DATA_CUSTODIAN, "APPROVE"),
        (IntakeSignOffRole.LEGAL_GOVERNANCE, "APPROVE"),
        (IntakeSignOffRole.SECURITY_PRIVACY, "REQUEST_CHANGES"),
        (IntakeSignOffRole.CHIEF_ARCHITECT, "APPROVE"),
    ]:
        sub = _make_signed_intake_submission(role=role, decision=dec, source_ids=[source_id])
        res = verifier.verify_submission(sub)
        assert res.is_valid
        submissions.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    assert quorum_state == QuorumState.BLOCKED_CHANGES_REQUESTED
    assert any("REQUEST_CHANGES" in r for r in reasons)


def test_incomplete_quorum_remains_pending():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-EN-01"

    # Only 2 roles submitted
    submissions = []
    for role in [IntakeSignOffRole.DATA_CUSTODIAN, IntakeSignOffRole.LEGAL_GOVERNANCE]:
        sub = _make_signed_intake_submission(role=role, decision="APPROVE", source_ids=[source_id])
        res = verifier.verify_submission(sub)
        assert res.is_valid
        submissions.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    assert quorum_state == QuorumState.PENDING
    assert any("Quorum incomplete" in r for r in reasons)


def test_duplicate_role_submission_does_not_satisfy_quorum():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-EN-02"

    submissions = []
    # 4 submissions but only from 2 roles
    for role in [
        IntakeSignOffRole.DATA_CUSTODIAN,
        IntakeSignOffRole.DATA_CUSTODIAN,
        IntakeSignOffRole.LEGAL_GOVERNANCE,
        IntakeSignOffRole.LEGAL_GOVERNANCE,
    ]:
        sub = _make_signed_intake_submission(role=role, decision="APPROVE", source_ids=[source_id])
        res = verifier.verify_submission(sub)
        submissions.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, submissions)
    assert quorum_state == QuorumState.PENDING
    assert any("Quorum incomplete" in r for r in reasons)


# ==============================================================================
# 2. CRYPTOGRAPHIC, SIGNATURE & KEY VALIDATION TESTS
# ==============================================================================

def test_canonical_json_serialization_determinism():
    dict1 = {"z": 1, "a": 2, "m": {"b": 10, "a": 20}}
    dict2 = {"a": 2, "m": {"a": 20, "b": 10}, "z": 1}
    b1 = canonical_json_bytes(dict1)
    b2 = canonical_json_bytes(dict2)
    assert b1 == b2
    assert b1 == b'{"a":2,"m":{"a":20,"b":10},"z":1}'


def test_signature_tamper_detection_in_payload():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _make_signed_intake_submission(role=IntakeSignOffRole.DATA_CUSTODIAN, decision="APPROVE")
    # Tamper payload without updating signature
    sub["decision"] = "REJECT"

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("signature does not match" in e for e in res.errors)


def test_signature_tamper_detection_in_signature_bytes():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _make_signed_intake_submission(role=IntakeSignOffRole.DATA_CUSTODIAN, decision="APPROVE")
    # Corrupt last character of signature hex
    orig_sig = sub["digital_signature"]
    corrupted_char = "0" if orig_sig[-1] != "0" else "1"
    sub["digital_signature"] = orig_sig[:-1] + corrupted_char

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("signature does not match" in e for e in res.errors)


def test_key_role_binding_violation_rejected():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)

    # Use Chief Architect's key to sign as Legal Governance
    sub = _make_signed_intake_submission(
        role=IntakeSignOffRole.LEGAL_GOVERNANCE,
        key_id="KEY-CHIEF_ARCHITECT-001",
        secret_key=f"{SYNTHETIC_TEST_SECRET}_CHIEF_ARCHITECT",
    )

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("Key validation failed" in e for e in res.errors)
    assert any("cannot sign as" in e for e in res.errors)


def test_revoked_key_rejected():
    registry = _create_test_key_registry()
    registry.revoke_key("KEY-DATA_CUSTODIAN-001", "Credential compromised in test drill")
    verifier = ReviewIntakeVerifier(registry)

    sub = _make_signed_intake_submission(role=IntakeSignOffRole.DATA_CUSTODIAN)
    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("revoked" in e for e in res.errors)


def test_expired_submission_rejected():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _make_signed_intake_submission(
        role=IntakeSignOffRole.SECURITY_PRIVACY,
        expiry_date="2026-01-01T00:00:00Z",
    )
    ref_time = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)
    res = verifier.verify_submission(sub, reference_time=ref_time)
    assert not res.is_valid
    assert any("expired" in e for e in res.errors)


def test_document_hash_verification_on_disk():
    registry = _create_test_key_registry()
    verifier = ReviewIntakeVerifier(registry)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tmp:
        tmp.write("# Genuine Review Package\nAudited findings.\n")
        tmp_path = Path(tmp.name)

    try:
        genuine_hash = hashlib.sha256(tmp_path.read_bytes()).hexdigest()

        # 1. Matching hash -> Valid
        sub_valid = _make_signed_intake_submission(
            role=IntakeSignOffRole.CHIEF_ARCHITECT,
            document_hash=genuine_hash,
        )
        res_valid = verifier.verify_submission(sub_valid, document_path=tmp_path)
        assert res_valid.is_valid

        # 2. Tampered / wrong hash -> Invalid
        sub_tampered = _make_signed_intake_submission(
            role=IntakeSignOffRole.CHIEF_ARCHITECT,
            document_hash="0" * 64,
        )
        res_tampered = verifier.verify_submission(sub_tampered, document_path=tmp_path)
        assert not res_tampered.is_valid
        assert any("Document SHA256 mismatch" in e for e in res_tampered.errors)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ==============================================================================
# 3. AUDIT TRAIL HASH CHAIN TAMPER-EVIDENCE TESTS
# ==============================================================================

def test_audit_trail_append_and_chain_verification():
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "governance_audit_trail.jsonl"
        logger = AuditTrailLogger(log_path)

        # Append 3 decisions
        r1 = logger.append_decision(
            source_id="SRC-TM-01",
            gate_name="tokenizer_vocab_training",
            previous_state="LOCKED",
            new_state="PENDING_REVIEW",
            reviewer_identity="custodian@igris.org",
            role="DATA_CUSTODIAN",
            evidence_hash="1" * 64,
            reason="Submitted for human governance review",
        )
        r2 = logger.append_decision(
            source_id="SRC-TM-01",
            gate_name="tokenizer_vocab_training",
            previous_state="PENDING_REVIEW",
            new_state="PENDING_LEGAL",
            reviewer_identity="legal@igris.org",
            role="LEGAL_GOVERNANCE",
            evidence_hash="2" * 64,
            reason="Legal jurisdiction review complete",
        )
        r3 = logger.append_decision(
            source_id="SRC-TM-01",
            gate_name="tokenizer_vocab_training",
            previous_state="PENDING_LEGAL",
            new_state="PENDING_SECURITY",
            reviewer_identity="security@igris.org",
            role="SECURITY_PRIVACY",
            evidence_hash="3" * 64,
            reason="PII screening clearance complete",
        )

        assert r1.parent_audit_hash == "0" * 64
        assert r2.parent_audit_hash == r1.record_hash
        assert r3.parent_audit_hash == r2.record_hash

        valid, err = logger.verify_chain_integrity()
        assert valid, f"Untampered chain failed verification: {err}"


def test_audit_trail_tamper_detection_in_prior_record():
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "governance_audit_trail.jsonl"
        logger = AuditTrailLogger(log_path)

        logger.append_decision(
            source_id="SRC-HI-01",
            gate_name="tokenizer_vocab_training",
            previous_state="LOCKED",
            new_state="PENDING",
            reviewer_identity="custodian@igris.org",
            role="DATA_CUSTODIAN",
            evidence_hash="1" * 64,
            reason="Initial intake",
        )
        logger.append_decision(
            source_id="SRC-HI-01",
            gate_name="tokenizer_vocab_training",
            previous_state="PENDING",
            new_state="APPROVED",
            reviewer_identity="architect@igris.org",
            role="CHIEF_ARCHITECT",
            evidence_hash="2" * 64,
            reason="Architect sign-off",
        )

        # Tamper directly with the JSONL file on disk
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        data0 = json.loads(lines[0])
        data0["reason_for_decision"] = "FORGED REASON"
        lines[0] = json.dumps(data0)
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        # Reload logger and verify detection
        reloaded_logger = AuditTrailLogger(log_path)
        valid, err = reloaded_logger.verify_chain_integrity()
        assert not valid
        assert "Tampered record at audit_id 1" in str(err)


# ==============================================================================
# 4. DEFAULT-DENY GATEKEEPER FAIL-CLOSED TESTS
# ==============================================================================

def test_gatekeeper_denies_unapproved_dataset_records():
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tmp:
        # Markdown record with status PENDING
        auth_doc = """# Dataset Authorization Record
```json
{
  "dataset_id": "DS-TEST-PENDING-001",
  "dataset_name": "test_pending_corpus",
  "version": "1.0.0",
  "target_milestone": "3C.11",
  "scope": "TOKENIZER_EVALUATION",
  "manifest_sha256": "4444444444444444444444444444444444444444444444444444444444444444",
  "status": "PENDING",
  "screening_verified": true,
  "license_approved": true,
  "issue_date": "2026-11-17T00:00:00Z",
  "expiry_date": "2027-11-17T00:00:00Z",
  "sign_offs": []
}
```
"""
        tmp.write(auth_doc)
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(DatasetAccessDeniedError) as exc_info:
            AuthorizationValidator.enforce_access_gate(
                dataset_id="DS-TEST-PENDING-001",
                auth_record_path=tmp_path,
            )
        assert "expected 'APPROVED'" in str(exc_info.value)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_gatekeeper_denies_missing_role_signoff():
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tmp:
        # Approved status but only 3 roles signed
        auth_doc = """# Dataset Authorization Record
```json
{
  "dataset_id": "DS-TEST-MISSING-ROLE",
  "dataset_name": "test_missing_role_corpus",
  "version": "1.0.0",
  "target_milestone": "3C.11",
  "scope": "TOKENIZER_EVALUATION",
  "manifest_sha256": "5555555555555555555555555555555555555555555555555555555555555555",
  "status": "APPROVED",
  "screening_verified": true,
  "license_approved": true,
  "issue_date": "2026-11-17T00:00:00Z",
  "expiry_date": "2027-11-17T00:00:00Z",
  "sign_offs": [
    {
      "role": "DATA_CUSTODIAN",
      "name": "Signer 1",
      "timestamp": "2026-11-17T00:00:00Z",
      "signature_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "decision": "APPROVED"
    },
    {
      "role": "LEGAL_GOVERNANCE",
      "name": "Signer 2",
      "timestamp": "2026-11-17T00:00:00Z",
      "signature_hash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "decision": "APPROVED"
    },
    {
      "role": "SECURITY_PRIVACY",
      "name": "Signer 3",
      "timestamp": "2026-11-17T00:00:00Z",
      "signature_hash": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      "decision": "APPROVED"
    }
  ]
}
```
"""
        tmp.write(auth_doc)
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(DatasetAccessDeniedError) as exc_info:
            AuthorizationValidator.enforce_access_gate(
                dataset_id="DS-TEST-MISSING-ROLE",
                auth_record_path=tmp_path,
            )
        assert "Missing required human sign-offs" in str(exc_info.value)
        assert "CHIEF_ARCHITECT" in str(exc_info.value)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_gatekeeper_denies_expired_authorization():
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as tmp:
        auth_doc = """# Dataset Authorization Record
```json
{
  "dataset_id": "DS-TEST-EXPIRED",
  "dataset_name": "test_expired_corpus",
  "version": "1.0.0",
  "target_milestone": "3C.11",
  "scope": "TOKENIZER_EVALUATION",
  "manifest_sha256": "6666666666666666666666666666666666666666666666666666666666666666",
  "status": "APPROVED",
  "screening_verified": true,
  "license_approved": true,
  "issue_date": "2025-01-01T00:00:00Z",
  "expiry_date": "2026-01-01T00:00:00Z",
  "sign_offs": [
    {"role": "DATA_CUSTODIAN", "name": "S1", "timestamp": "2025-01-01T00:00:00Z", "signature_hash": "1111111111111111111111111111111111111111111111111111111111111111", "decision": "APPROVED"},
    {"role": "LEGAL_GOVERNANCE", "name": "S2", "timestamp": "2025-01-01T00:00:00Z", "signature_hash": "2222222222222222222222222222222222222222222222222222222222222222", "decision": "APPROVED"},
    {"role": "SECURITY_PRIVACY", "name": "S3", "timestamp": "2025-01-01T00:00:00Z", "signature_hash": "3333333333333333333333333333333333333333333333333333333333333333", "decision": "APPROVED"},
    {"role": "CHIEF_ARCHITECT", "name": "S4", "timestamp": "2025-01-01T00:00:00Z", "signature_hash": "4444444444444444444444444444444444444444444444444444444444444444", "decision": "APPROVED"}
  ]
}
```
"""
        tmp.write(auth_doc)
        tmp_path = Path(tmp.name)

    try:
        ref_time = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(DatasetAccessDeniedError) as exc_info:
            AuthorizationValidator.enforce_access_gate(
                dataset_id="DS-TEST-EXPIRED",
                auth_record_path=tmp_path,
                reference_time=ref_time,
            )
        assert "expired" in str(exc_info.value).lower()
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ==============================================================================
# 5. REPOSITORY REGISTER INTEGRITY & IMMUTABILITY INVARIANTS
# ==============================================================================

def test_all_32_sources_aligned_across_v2_and_v3_registers():
    cat_path = PATCH_ROOT / "DATASET_SOURCE_CATALOG_V3.csv"
    lic_path = PATCH_ROOT / "DATASET_LICENSE_CLASSIFICATION_V3.csv"
    pipe_path = PATCH_ROOT / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv"
    app_path = PATCH_ROOT / "SOURCE_APPROVAL_STATE_V2.csv"
    recon_path = PATCH_ROOT / "SOURCE_STATUS_RECONCILIATION.csv"

    with open(cat_path, "r", encoding="utf-8") as f:
        cat_ids = [r["source_id"] for r in csv.DictReader(f)]
    with open(lic_path, "r", encoding="utf-8") as f:
        lic_ids = [r["source_id"] for r in csv.DictReader(f)]
    with open(pipe_path, "r", encoding="utf-8") as f:
        pipe_ids = [r["source_id"] for r in csv.DictReader(f)]
    with open(app_path, "r", encoding="utf-8") as f:
        app_ids = [r["source_id"] for r in csv.DictReader(f)]
    with open(recon_path, "r", encoding="utf-8") as f:
        recon_ids = [r["source_id"] for r in csv.DictReader(f)]

    assert len(cat_ids) == 32
    assert cat_ids == lic_ids
    assert cat_ids == pipe_ids
    assert cat_ids == app_ids
    assert cat_ids == recon_ids


def test_source_approval_state_v2_all_pending_and_locked():
    app_path = PATCH_ROOT / "SOURCE_APPROVAL_STATE_V2.csv"
    with open(app_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 32
    for r in rows:
        assert r["composite_approval_state"] == "PENDING"
        assert r["pipeline_gate_state"] == "LOCKED"
        assert r["custodian_decision"] == "PENDING"
        assert r["legal_decision"] == "PENDING"
        assert r["security_decision"] == "PENDING"
        assert r["architect_decision"] == "PENDING"


def test_pipeline_matrix_sft_alignment_safety_not_authorized():
    pipe_path = PATCH_ROOT / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv"
    with open(pipe_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 32
    for r in rows:
        assert r["supervised_fine_tuning"] == "NOT AUTHORIZED"
        assert "NOT AUTHORIZED" in r["alignment_evaluation"]
        assert "NOT AUTHORIZED" in r["safety_evaluation"]


def test_candidate_a_and_b_hashes_invariant():
    tok_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    tok_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    assert tok_a.is_file(), "Candidate A tokenizer.json missing"
    assert tok_b.is_file(), "Candidate B tokenizer.model missing"

    h_a = hashlib.sha256(tok_a.read_bytes()).hexdigest()
    h_b = hashlib.sha256(tok_b.read_bytes()).hexdigest()

    assert h_a == CANDIDATE_A_HASH, f"Candidate A hash changed: {h_a}"
    assert h_b == CANDIDATE_B_HASH, f"Candidate B hash changed: {h_b}"
