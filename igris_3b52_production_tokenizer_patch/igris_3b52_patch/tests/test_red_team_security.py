"""IGRIS Phase 6: Red-Team Security Assessment Test Suite.

Rigorously evaluates the dataset governance and access-control framework
against 10 adversarial attack vectors:
1. Unauthorized dataset ingestion.
2. Approval signature forgery.
3. Signature replay across different sources/submissions.
4. Key revocation enforcement (CRL).
5. Approval expiration enforcement.
6. Role impersonation / privilege escalation.
7. Audit log tampering & hash-chain breakage.
8. Unauthorized pipeline transitions (SFT / vocab training).
9. Approval state manipulation & quorum inconsistency.
10. Candidate tokenizer substitution & hash mismatch.
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
    REQUIRED_ROLES,
    AuthorizationStatus,
    AuthorizationValidator,
    DatasetAccessDeniedError,
    DatasetAuthorizationRecord,
    SignOffRecord,
    SignOffRole,
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
    SignOffRole as IntakeRole,
    canonical_json_bytes,
    compute_signature,
    verify_signature,
)

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

REDTEAM_SECRET = "redteam_synthetic_attack_secret_key_884422"


def _setup_redteam_registry() -> KeyRegistry:
    registry = KeyRegistry()
    for role in [
        IntakeRole.DATA_CUSTODIAN,
        IntakeRole.LEGAL_GOVERNANCE,
        IntakeRole.SECURITY_PRIVACY,
        IntakeRole.CHIEF_ARCHITECT,
    ]:
        registry.register_key(
            KeyRecord(
                key_id=f"KEY-{role.value}-REDTEAM",
                role=role,
                secret_key=f"{REDTEAM_SECRET}_{role.value}",
                created_at="2026-11-17T00:00:00Z",
                expires_at="2027-11-17T00:00:00Z",
            )
        )
    return registry


def _build_signed_payload(
    role: IntakeRole,
    submission_id: str = "SUB-REDTEAM001",
    source_ids: Optional[List[str]] = None,
    decision: str = "APPROVE",
    document_hash: str = "e" * 64,
    expiry_date: str = "2027-11-17T12:00:00Z",
    secret: Optional[str] = None,
    key_id: Optional[str] = None,
) -> Dict[str, Any]:
    sec = secret or f"{REDTEAM_SECRET}_{role.value}"
    kid = key_id or f"KEY-{role.value}-REDTEAM"
    sub: Dict[str, Any] = {
        "submission_id": submission_id,
        "reviewer_identity": f"{role.value.lower()}@redteam.igris.internal",
        "role": role.value,
        "public_key_id": kid,
        "source_ids_reviewed": source_ids or ["SRC-TM-01"],
        "decision": decision,
        "evidence_references": [
            {
                "reference_type": "CATALOG",
                "reference_uri": "file:///DATASET_SOURCE_CATALOG_V3.csv",
                "sha256": "f" * 64,
            }
        ],
        "document_sha256": document_hash,
        "timestamp": "2026-11-17T12:00:00Z",
        "expiry_date": expiry_date,
    }
    canon = canonical_json_bytes(sub)
    sub["digital_signature"] = compute_signature(canon, sec)
    return sub


# ==============================================================================
# ATTACK VECTOR 1: Unauthorized Dataset Ingestion
# ==============================================================================
def test_redteam_attack_01_unauthorized_dataset_ingestion():
    """Adversary attempts to fetch authorized path without approved record."""
    with tempfile.TemporaryDirectory() as td:
        fake_data_dir = Path(td) / "unauthorized_tamil_corpus"
        fake_data_dir.mkdir()
        (fake_data_dir / "text.txt").write_text("unauthorized data", encoding="utf-8")

        # Non-existent auth file
        non_existent_auth = Path(td) / "missing_auth.md"

        with pytest.raises(DatasetAccessDeniedError) as exc_info:
            AuthorizationValidator.get_authorized_dataset_path(
                dataset_id="DS-PROD-TM-001",
                auth_record_path=non_existent_auth,
                target_dir=fake_data_dir,
            )
        assert "Authorization file does not exist" in str(exc_info.value)


# ==============================================================================
# ATTACK VECTOR 2: Approval Signature Forgery
# ==============================================================================
def test_redteam_attack_02_approval_signature_forgery():
    """Adversary generates fake HMAC signature without knowledge of genuine private key."""
    registry = _setup_redteam_registry()
    verifier = ReviewIntakeVerifier(registry)

    # Payload signed with wrong secret key
    sub = _build_signed_payload(
        role=IntakeRole.LEGAL_GOVERNANCE,
        secret="attacker_unknown_random_secret_string_9999",
    )

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("Cryptographic signature verification failed" in e for e in res.errors)


# ==============================================================================
# ATTACK VECTOR 3: Signature Replay Across Sources & Submissions
# ==============================================================================
def test_redteam_attack_03_signature_replay():
    """Adversary captures valid signature on SRC-TM-01 and replays it on SRC-HI-01."""
    registry = _setup_redteam_registry()
    verifier = ReviewIntakeVerifier(registry)

    # Valid submission for SRC-TM-01
    sub_orig = _build_signed_payload(role=IntakeRole.DATA_CUSTODIAN, source_ids=["SRC-TM-01"])
    res_orig = verifier.verify_submission(sub_orig)
    assert res_orig.is_valid

    # Adversary copies the exact digital_signature but changes source_ids to SRC-HI-01
    replayed_sub = dict(sub_orig)
    replayed_sub["source_ids_reviewed"] = ["SRC-HI-01"]

    res_replay = verifier.verify_submission(replayed_sub)
    assert not res_replay.is_valid
    assert any("Cryptographic signature verification failed" in e for e in res_replay.errors)


# ==============================================================================
# ATTACK VECTOR 4: Key Revocation (CRL Enforcement)
# ==============================================================================
def test_redteam_attack_04_revoked_key_rejection():
    """Adversary attempts to sign review using a decommissioned / revoked key."""
    registry = _setup_redteam_registry()
    compromised_key_id = "KEY-SECURITY_PRIVACY-REDTEAM"
    registry.revoke_key(compromised_key_id, reason="Exfiltrated private key drill")

    verifier = ReviewIntakeVerifier(registry)
    sub = _build_signed_payload(role=IntakeRole.SECURITY_PRIVACY, key_id=compromised_key_id)

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("revoked" in e for e in res.errors)
    assert any("Exfiltrated private key drill" in e for e in res.errors)


# ==============================================================================
# ATTACK VECTOR 5: Approval Expiration / Stale Sign-off Replay
# ==============================================================================
def test_redteam_attack_05_expired_approval_rejection():
    """Adversary attempts to utilize an approval past its mandatory expiration date."""
    registry = _setup_redteam_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _build_signed_payload(
        role=IntakeRole.CHIEF_ARCHITECT,
        expiry_date="2026-06-01T00:00:00Z",
    )
    # Check at current date (post-June 2026)
    ref_now = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)
    res = verifier.verify_submission(sub, reference_time=ref_now)

    assert not res.is_valid
    assert any("expired on 2026-06-01" in e for e in res.errors)


# ==============================================================================
# ATTACK VECTOR 6: Role Impersonation / Privilege Escalation
# ==============================================================================
def test_redteam_attack_06_role_impersonation():
    """Adversary uses Chief Architect credentials to sign as Legal Governance."""
    registry = _setup_redteam_registry()
    verifier = ReviewIntakeVerifier(registry)

    sub = _build_signed_payload(
        role=IntakeRole.LEGAL_GOVERNANCE,
        key_id="KEY-CHIEF_ARCHITECT-REDTEAM",
        secret=f"{REDTEAM_SECRET}_CHIEF_ARCHITECT",
    )

    res = verifier.verify_submission(sub)
    assert not res.is_valid
    assert any("cannot sign as 'LEGAL_GOVERNANCE'" in e for e in res.errors)


# ==============================================================================
# ATTACK VECTOR 7: Audit Log Tampering & Chain Breakage
# ==============================================================================
def test_redteam_attack_07_audit_log_tampering():
    """Adversary attempts to modify a historical record in the append-only audit trail."""
    with tempfile.TemporaryDirectory() as td:
        log_file = Path(td) / "audit_chain.jsonl"
        logger = AuditTrailLogger(log_file)

        logger.append_decision(
            source_id="SRC-TM-01",
            gate_name="tokenizer_vocab_training",
            previous_state="LOCKED",
            new_state="PENDING",
            reviewer_identity="custodian@igris.org",
            role="DATA_CUSTODIAN",
            evidence_hash="1" * 64,
            reason="Step 1",
        )
        logger.append_decision(
            source_id="SRC-TM-01",
            gate_name="tokenizer_vocab_training",
            previous_state="PENDING",
            new_state="APPROVED",
            reviewer_identity="architect@igris.org",
            role="CHIEF_ARCHITECT",
            evidence_hash="2" * 64,
            reason="Step 2",
        )

        # Confirm valid before attack
        valid, _ = logger.verify_chain_integrity()
        assert valid

        # Attack: alter parent hash of record 2
        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        rec2 = json.loads(lines[1])
        rec2["parent_audit_hash"] = "f" * 64
        lines[1] = json.dumps(rec2)
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        reloaded = AuditTrailLogger(log_file)
        valid_post_attack, err = reloaded.verify_chain_integrity()
        assert not valid_post_attack
        assert "Broken chain link at audit_id 2" in str(err) or "Tampered record" in str(err)


# ==============================================================================
# ATTACK VECTOR 8: Unauthorized Pipeline Transitions (Scope Creep)
# ==============================================================================
def test_redteam_attack_08_unauthorized_pipeline_transitions():
    """Verify that SFT and unvetted pre-training cannot be authorized."""
    pipe_path = PATCH_ROOT / "PIPELINE_AUTHORIZATION_MATRIX_V2.csv"
    with open(pipe_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 1. Supervised fine-tuning is strictly NOT AUTHORIZED across all 32 sources
    for r in rows:
        assert r["supervised_fine_tuning"] == "NOT AUTHORIZED", (
            f"Scope creep detected: {r['source_id']} has SFT permission '{r['supervised_fine_tuning']}'"
        )

    # 2. Preference evaluation dataset (SRC-CV-04 HH-RLHF) is strictly prohibited from vocab training
    hh_rlhf = next(r for r in rows if r["source_id"] == "SRC-CV-04")
    assert hh_rlhf["tokenizer_vocab_training"] in ["INELIGIBLE_REJECTED", "STRICTLY_PROHIBITED"], (
        f"HH-RLHF must not be eligible for vocab training: {hh_rlhf['tokenizer_vocab_training']}"
    )


# ==============================================================================
# ATTACK VECTOR 9: Approval State Manipulation & Quorum Verification
# ==============================================================================
def test_redteam_attack_09_approval_state_manipulation():
    """Adversary attempts to forge consensus when one role submitted REJECT."""
    registry = _setup_redteam_registry()
    verifier = ReviewIntakeVerifier(registry)
    source_id = "SRC-CV-01"

    # Three roles approve, but Legal Governance rejects
    subs = []
    for role, dec in [
        (IntakeRole.DATA_CUSTODIAN, "APPROVE"),
        (IntakeRole.LEGAL_GOVERNANCE, "REJECT"),
        (IntakeRole.SECURITY_PRIVACY, "APPROVE"),
        (IntakeRole.CHIEF_ARCHITECT, "APPROVE"),
    ]:
        role_suffix = role.value.replace("_", "")[:6]
        payload = _build_signed_payload(
            role=role,
            submission_id=f"SUB-REDTM{role_suffix}",
            source_ids=[source_id],
            decision=dec,
        )
        res = verifier.verify_submission(payload)
        assert res.is_valid
        subs.append(res)

    quorum_state, reasons = QuorumEngine.evaluate_source_consensus(source_id, subs)
    # Consensus MUST be BLOCKED_REJECTED, never APPROVED
    assert quorum_state == QuorumState.BLOCKED_REJECTED
    assert any("explicit REJECT" in r for r in reasons)


# ==============================================================================
# ATTACK VECTOR 10: Candidate Tokenizer Substitution Detection
# ==============================================================================
def test_redteam_attack_10_candidate_substitution_detection():
    """Verify that any alteration or substitution of tokenizer artifacts is detected."""
    tok_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    tok_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    # Live SHA-256 computation
    actual_a = hashlib.sha256(tok_a.read_bytes()).hexdigest()
    actual_b = hashlib.sha256(tok_b.read_bytes()).hexdigest()

    assert actual_a == CANDIDATE_A_HASH, "Candidate A tokenizer.json does not match verified hash"
    assert actual_b == CANDIDATE_B_HASH, "Candidate B tokenizer.model does not match verified hash"

    # Adversary attempts to substitute with altered content
    with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
        tmp.write("backdoored tokenizer json content")
        tmp_path = Path(tmp.name)

    try:
        tampered_hash = hashlib.sha256(tmp_path.read_bytes()).hexdigest()
        assert tampered_hash != CANDIDATE_A_HASH, "Hash collision or failure to distinguish tampered artifact"
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
