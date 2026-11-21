import csv
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import pytest
import sys

PATCH_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PATCH_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from review_intake_verifier import (
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

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

DUMMY_KEY_SECRET = "super_secure_synthetic_secret_key_12345"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _make_valid_submission(
    role: SignOffRole = SignOffRole.DATA_CUSTODIAN,
    decision: str = "APPROVE",
    doc_hash: Optional[str] = None,
    expiry_date: str = "2027-11-17T12:00:00Z",
    source_ids: Optional[list] = None,
    key_id: str = "KEY-TEST-001",
    secret: str = DUMMY_KEY_SECRET,
) -> dict:
    sub = {
        "submission_id": "SUB-2026111701",
        "reviewer_identity": "reviewer@igris-governance.org",
        "role": role.value,
        "public_key_id": key_id,
        "source_ids_reviewed": source_ids or ["SRC-TM-01"],
        "decision": decision,
        "evidence_references": [
            {
                "reference_type": "CATALOG",
                "reference_uri": "file:///DATASET_SOURCE_CATALOG_V3.csv",
                "sha256": "a" * 64,
            }
        ],
        "document_sha256": doc_hash or ("b" * 64),
        "timestamp": "2026-11-17T12:00:00Z",
        "expiry_date": expiry_date,
    }
    canon_bytes = canonical_json_bytes(sub)
    sub["digital_signature"] = compute_signature(canon_bytes, secret)
    return sub


def test_3c10_deliverables_exist():
    required_files = [
        "IGRIS_3C10_REVIEW_INTAKE_REPORT.md",
        "HUMAN_APPROVAL_SCHEMA_V1.json",
        "REVIEW_SIGNATURE_VERIFICATION.md",
        "SOURCE_APPROVAL_STATE_V2.csv",
        "GOVERNANCE_AUDIT_TRAIL_SPEC.md",
        "IGRIS_3C10_STATUS.md",
    ]
    for rel_path in required_files:
        p = PATCH_ROOT / rel_path
        assert p.is_file(), f"Missing required 3C.10 file: {rel_path}"
        assert p.stat().st_size > 0, f"Empty 3C.10 file: {rel_path}"


def test_human_approval_schema_v1_valid():
    schema_path = PATCH_ROOT / "HUMAN_APPROVAL_SCHEMA_V1.json"
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)

    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert "required" in schema
    expected_req = [
        "submission_id",
        "reviewer_identity",
        "role",
        "public_key_id",
        "source_ids_reviewed",
        "decision",
        "evidence_references",
        "document_sha256",
        "timestamp",
        "expiry_date",
        "digital_signature",
    ]
    for req in expected_req:
        assert req in schema["required"]


def test_source_approval_state_v2_schema_and_counts():
    csv_path = PATCH_ROOT / "SOURCE_APPROVAL_STATE_V2.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 32, f"Expected 32 sources in approval state V2, got {len(rows)}"

    expected_cols = [
        "source_id",
        "dataset_name",
        "canonical_category",
        "published_license",
        "custodian_decision",
        "legal_decision",
        "security_decision",
        "architect_decision",
        "composite_approval_state",
        "pipeline_gate_state",
        "approval_timestamp",
        "expiry_timestamp",
        "audit_notes",
    ]
    for col in expected_cols:
        assert col in reader.fieldnames, f"Missing column in approval state V2: {col}"

    for r in rows:
        assert r["composite_approval_state"] == "PENDING"
        assert r["pipeline_gate_state"] == "LOCKED"
        assert r["custodian_decision"] == "PENDING"
        assert r["legal_decision"] == "PENDING"
        assert r["security_decision"] == "PENDING"
        assert r["architect_decision"] == "PENDING"


def test_cryptographic_verification_valid_signature():
    reg = KeyRegistry()
    reg.register_key(KeyRecord("KEY-TEST-001", SignOffRole.DATA_CUSTODIAN, DUMMY_KEY_SECRET))
    verifier = ReviewIntakeVerifier(reg)

    sub = _make_valid_submission()
    res = verifier.verify_submission(sub)
    assert res.is_valid
    assert len(res.errors) == 0
    assert res.role == SignOffRole.DATA_CUSTODIAN
    assert res.decision == ReviewDecision.APPROVE


def test_cryptographic_verification_invalid_and_missing_signature():
    reg = KeyRegistry()
    reg.register_key(KeyRecord("KEY-TEST-001", SignOffRole.DATA_CUSTODIAN, DUMMY_KEY_SECRET))
    verifier = ReviewIntakeVerifier(reg)

    # Invalid signature
    sub_bad = _make_valid_submission()
    sub_bad["digital_signature"] = "f" * 64
    res_bad = verifier.verify_submission(sub_bad)
    assert not res_bad.is_valid
    assert any("signature verification failed" in err.lower() for err in res_bad.errors)

    # Missing signature
    sub_missing = _make_valid_submission()
    sub_missing["digital_signature"] = ""
    res_missing = verifier.verify_submission(sub_missing)
    assert not res_missing.is_valid
    assert any("missing digital signature" in err.lower() for err in res_missing.errors)


def test_cryptographic_verification_expired_approval_and_revoked_key():
    reg = KeyRegistry()
    reg.register_key(KeyRecord("KEY-TEST-001", SignOffRole.DATA_CUSTODIAN, DUMMY_KEY_SECRET))
    verifier = ReviewIntakeVerifier(reg)

    # Expired approval
    sub_expired = _make_valid_submission(expiry_date="2024-01-01T00:00:00Z")
    res_exp = verifier.verify_submission(sub_expired)
    assert not res_exp.is_valid
    assert any("expired" in err.lower() for err in res_exp.errors)

    # Revoked key
    reg.revoke_key("KEY-TEST-001", "Security credential compromise test")
    sub_revoked = _make_valid_submission()
    res_rev = verifier.verify_submission(sub_revoked)
    assert not res_rev.is_valid
    assert any("revoked" in err.lower() for err in res_rev.errors)


def test_document_tamper_and_sha256_mismatch():
    reg = KeyRegistry()
    reg.register_key(KeyRecord("KEY-TEST-001", SignOffRole.DATA_CUSTODIAN, DUMMY_KEY_SECRET))
    verifier = ReviewIntakeVerifier(reg)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
        tf.write("Official audited review document text.")
        tmp_path = Path(tf.name)

    try:
        actual_hash = hashlib.sha256(tmp_path.read_bytes()).hexdigest()

        # Matching document hash passes
        sub_good = _make_valid_submission(doc_hash=actual_hash)
        res_good = verifier.verify_submission(sub_good, document_path=tmp_path)
        assert res_good.is_valid

        # Altered document on disk fails
        with open(tmp_path, "a", encoding="utf-8") as tf2:
            tf2.write("\nTampered unauthorized text insertion.")

        res_tampered = verifier.verify_submission(sub_good, document_path=tmp_path)
        assert not res_tampered.is_valid
        assert any("mismatch" in err.lower() for err in res_tampered.errors)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_quorum_consensus_and_conflicts():
    reg = KeyRegistry()
    for role in SignOffRole:
        reg.register_key(KeyRecord(f"KEY-{role.value}", role, DUMMY_KEY_SECRET))
    verifier = ReviewIntakeVerifier(reg)

    # 1. Incomplete quorum (only Custodian & Legal)
    sub_cust = _make_valid_submission(role=SignOffRole.DATA_CUSTODIAN, key_id="KEY-DATA_CUSTODIAN")
    sub_legal = _make_valid_submission(role=SignOffRole.LEGAL_GOVERNANCE, key_id="KEY-LEGAL_GOVERNANCE")
    res_cust = verifier.verify_submission(sub_cust)
    res_legal = verifier.verify_submission(sub_legal)

    state, reasons = QuorumEngine.evaluate_source_consensus("SRC-TM-01", [res_cust, res_legal])
    assert state == QuorumState.PENDING
    assert any("missing roles" in r.lower() for r in reasons)

    # 2. Conflicting decision: Security votes REJECT
    sub_sec_rej = _make_valid_submission(role=SignOffRole.SECURITY_PRIVACY, decision="REJECT", key_id="KEY-SECURITY_PRIVACY")
    sub_arch = _make_valid_submission(role=SignOffRole.CHIEF_ARCHITECT, key_id="KEY-CHIEF_ARCHITECT")
    res_sec_rej = verifier.verify_submission(sub_sec_rej)
    res_arch = verifier.verify_submission(sub_arch)

    state_rej, reasons_rej = QuorumEngine.evaluate_source_consensus(
        "SRC-TM-01", [res_cust, res_legal, res_sec_rej, res_arch]
    )
    assert state_rej == QuorumState.BLOCKED_REJECTED
    assert any("reject" in r.lower() for r in reasons_rej)

    # 3. Request changes blocks approval
    sub_sec_chg = _make_valid_submission(role=SignOffRole.SECURITY_PRIVACY, decision="REQUEST_CHANGES", key_id="KEY-SECURITY_PRIVACY")
    res_sec_chg = verifier.verify_submission(sub_sec_chg)
    state_chg, reasons_chg = QuorumEngine.evaluate_source_consensus(
        "SRC-TM-01", [res_cust, res_legal, res_sec_chg, res_arch]
    )
    assert state_chg == QuorumState.BLOCKED_CHANGES_REQUESTED
    assert any("request_changes" in r.lower() for r in reasons_chg)

    # 4. Full 4-of-4 approval
    sub_sec_app = _make_valid_submission(role=SignOffRole.SECURITY_PRIVACY, decision="APPROVE", key_id="KEY-SECURITY_PRIVACY")
    res_sec_app = verifier.verify_submission(sub_sec_app)
    state_app, reasons_app = QuorumEngine.evaluate_source_consensus(
        "SRC-TM-01", [res_cust, res_legal, res_sec_app, res_arch]
    )
    assert state_app == QuorumState.APPROVED


def test_audit_trail_hash_chain():
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
        log_path = Path(tf.name)

    try:
        logger = AuditTrailLogger(log_path)
        rec1 = logger.append_decision("SRC-TM-01", "Gate 1", "LOCKED", "PENDING", "user@test", "DATA_CUSTODIAN", "h1", "Init")
        rec2 = logger.append_decision("SRC-TM-01", "Gate 1", "PENDING", "BLOCKED_REJECTED", "user2@test", "LEGAL_GOVERNANCE", "h2", "Rejected")

        assert rec1.parent_audit_hash == "0" * 64
        assert rec2.parent_audit_hash == rec1.record_hash

        valid, err = logger.verify_chain_integrity()
        assert valid, f"Audit chain verification failed: {err}"

        # Tamper test
        logger.records[0].reason_for_decision = "Tampered unauthorized modification"
        valid_tampered, err_tampered = logger.verify_chain_integrity()
        assert not valid_tampered
        assert err_tampered is not None
        assert "tampered" in err_tampered.lower()
    finally:
        if log_path.exists():
            log_path.unlink()


def test_candidate_invariants_preserved():
    cand_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    assert cand_a.exists(), f"Candidate A missing at {cand_a}"
    assert cand_b.exists(), f"Candidate B missing at {cand_b}"
    assert sha256_file(cand_a) == CANDIDATE_A_HASH
    assert sha256_file(cand_b) == CANDIDATE_B_HASH
