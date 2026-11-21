"""IGRIS Phase 11: Solo Developer Governance & Cryptographic Remediation Test Suite.

Rigorously verifies:
1. Presence and integrity of all Phase 11 deliverables.
2. Solo owner approval register (single identity, four responsibilities, no fake personas).
3. Document approval register (52 tracked documents, live SHA-256 validation).
4. Dataset owner review register (32 sources, 4 incompatible strictly rejected, operation boundaries).
5. Ed25519 asymmetric signature generation and verification.
6. Persistent replay protection in intake engine.
7. Retraction of unverified FIPS 140-2 claims across key registers.
8. Candidate A and Candidate B tokenizer SHA-256 hash invariants.
9. Final Phase 11 verdict selection (Verdict A: Owner Approval Recorded; Transition Complete).
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path
import pytest
import sys

PATCH_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PATCH_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from review_intake_verifier import (
    KeyAlgorithm,
    KeyRecord,
    KeyRegistry,
    ReplayCache,
    ReviewIntakeVerifier,
    SignOffRole,
    canonical_json_bytes,
    compute_ed25519_signature,
    verify_ed25519_signature,
)

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_phase11_deliverables_exist():
    """Verify all six Phase 11 deliverables exist on disk."""
    expected_files = [
        PATCH_ROOT / "IGRIS_PHASE11_SOLO_OWNER_APPROVAL_REGISTER.csv",
        PATCH_ROOT / "IGRIS_PHASE11_DOCUMENT_APPROVAL_REGISTER.csv",
        PATCH_ROOT / "IGRIS_PHASE11_DATASET_OWNER_REVIEW_REGISTER.csv",
        PATCH_ROOT / "IGRIS_PHASE11_SOLO_GOVERNANCE_POLICY.md",
        PATCH_ROOT / "IGRIS_PHASE11_CRYPTOGRAPHIC_REMEDIATION_REPORT.md",
        PATCH_ROOT / "IGRIS_PHASE11_FINAL_STATUS.md",
    ]
    for ef in expected_files:
        assert ef.is_file(), f"Missing Phase 11 deliverable: {ef.name}"
        assert ef.stat().st_size > 0, f"Deliverable is empty: {ef.name}"


def test_phase11_solo_owner_approval_register():
    """Verify single owner identity structure across the four review responsibilities."""
    reg_path = PATCH_ROOT / "IGRIS_PHASE11_SOLO_OWNER_APPROVAL_REGISTER.csv"
    with open(reg_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 4, f"Expected 4 rows (one per responsibility), got {len(rows)}"

    expected_roles = {"DATA_CUSTODIAN", "LEGAL_GOVERNANCE", "SECURITY_PRIVACY", "CHIEF_ARCHITECT"}
    found_roles = set(r["responsibility_domain"] for r in rows)
    assert found_roles == expected_roles

    for r in rows:
        assert r["governance_model"] == "SOLO_DEVELOPER_OWNER_REVIEW"
        assert r["accountable_owner_designation"] == "PROJECT_OWNER_AND_SOLE_DEVELOPER"
        assert r["declared_approval_state"] == "OWNER_APPROVED_DECLARED"
        assert r["cryptographic_signature_status"] == "UNSIGNED_DECLARED_APPROVAL"


def test_phase11_document_approval_register():
    """Verify document register covers Phase 1-10 docs with valid SHA-256 hashes."""
    doc_path = PATCH_ROOT / "IGRIS_PHASE11_DOCUMENT_APPROVAL_REGISTER.csv"
    with open(doc_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) >= 50, f"Expected at least 50 tracked documents, got {len(rows)}"

    for r in rows:
        fn = r["document_filename"]
        target = PATCH_ROOT / fn
        assert target.is_file(), f"Tracked document does not exist: {fn}"
        live_hash = sha256_file(target)
        assert live_hash == r["document_sha256"], f"Hash mismatch in {fn}: {live_hash} != {r['document_sha256']}"
        assert r["owner_approval_declaration"] == "OWNER_APPROVED_DECLARED"


def test_phase11_dataset_owner_review_register():
    """Verify all 32 candidate sources preserve legal rejections and operation boundaries."""
    ds_path = PATCH_ROOT / "IGRIS_PHASE11_DATASET_OWNER_REVIEW_REGISTER.csv"
    with open(ds_path, "r", encoding="utf-8") as f:
        rows = {r["source_id"]: r for r in csv.DictReader(f)}

    assert len(rows) == 32

    # 4 Incompatible sources must remain REJECTED
    incompatible_ids = ["SRC-CV-01", "SRC-CV-02", "SRC-HI-03", "SRC-TG-03"]
    for sid in incompatible_ids:
        r = rows[sid]
        assert r["owner_composite_review_verdict"] == "OWNER_REJECTED_INCOMPATIBLE"
        assert r["vocab_training_authorization"] == "BLOCKED_REJECTED"
        assert r["fertility_eval_authorization"] == "BLOCKED_REJECTED"
        assert r["pipeline_gate_state"] == "LOCKED"

    # Evaluation-only benchmarks
    cd02 = rows["SRC-CD-02"]
    assert cd02["owner_composite_review_verdict"] == "OWNER_APPROVED_EVAL_ONLY"
    assert cd02["vocab_training_authorization"] == "STRICTLY_PROHIBITED_BENCHMARK"
    assert cd02["fertility_eval_authorization"] == "AUTHORIZED_PENDING_STAGING"

    cv04 = rows["SRC-CV-04"]
    assert cv04["owner_composite_review_verdict"] == "OWNER_APPROVED_EVAL_ONLY"
    assert cv04["vocab_training_authorization"] == "STRICTLY_PROHIBITED_PREFERENCE"
    assert cv04["fertility_eval_authorization"] == "AUTHORIZED_ISOLATED_PROMPTS_ONLY"

    # All sources must be locked at the production gate
    for sid, r in rows.items():
        assert r["pipeline_gate_state"] == "LOCKED"
        assert r["sft_authorization"] == "NOT AUTHORIZED"


def test_phase11_ed25519_and_replay_protection():
    """Verify live Ed25519 signing, verification, and ReplayCache deduplication."""
    from cryptography.hazmat.primitives.asymmetric import ed25519

    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_hex = priv.private_bytes_raw().hex()
    pub_hex = pub.public_bytes_raw().hex()

    registry = KeyRegistry()
    key_rec = KeyRecord(
        key_id="KEY-TEST-ED25519-01",
        role=SignOffRole.DATA_CUSTODIAN,
        secret_key=pub_hex,
        algorithm=KeyAlgorithm.ED25519.value,
        public_key_hex=pub_hex,
        reviewer_id="PROJECT_OWNER",
    )
    registry.register_key(key_rec)

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f_cache:
        replay_cache = ReplayCache(f_cache.name)

    verifier = ReviewIntakeVerifier(registry, replay_cache=replay_cache)

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as f_doc:
        f_doc.write("# Test Dossier")
        doc_path = Path(f_doc.name)

    doc_hash = hashlib.sha256(doc_path.read_bytes()).hexdigest()

    sub = {
        "submission_id": "SUB-TESTED25519A",
        "role": "DATA_CUSTODIAN",
        "reviewer_id": "PROJECT_OWNER",
        "public_key_id": "KEY-TEST-ED25519-01",
        "source_ids_reviewed": ["SRC-TM-01"],
        "decision": "APPROVE",
        "evidence_references": [
            {"reference_type": "CATALOG", "reference_uri": "DATASET_SOURCE_CATALOG_V3.csv", "sha256": "0" * 64}
        ],
        "timestamp": "2026-11-17T12:00:00Z",
        "expiry_date": "2027-02-15T12:00:00Z",
        "document_path": str(doc_path),
        "document_sha256": doc_hash,
    }
    payload_bytes = canonical_json_bytes(sub)
    sub["digital_signature"] = compute_ed25519_signature(payload_bytes, priv_hex)

    # 1. First verification: must pass
    res1 = verifier.verify_submission(sub, document_path=doc_path)
    assert res1.is_valid, f"Ed25519 submission verification failed: {res1.errors}"

    # 2. Replay of same submission: must fail
    res2 = verifier.verify_submission(sub, document_path=doc_path)
    assert not res2.is_valid
    assert any("Replay" in e for e in res2.errors)

    # 3. Tampered signature: must fail
    sub_bad = dict(sub)
    sub_bad["submission_id"] = "SUB-TESTED25519B"
    sub_bad["digital_signature"] = "a" * 128
    res3 = verifier.verify_submission(sub_bad, document_path=doc_path)
    assert not res3.is_valid

    # Cleanup
    doc_path.unlink()
    Path(f_cache.name).unlink()


def test_phase11_fips_claims_retracted():
    """Verify that unverified FIPS 140-2 claims have been retracted from key registration status."""
    key_reg_path = PATCH_ROOT / "IGRIS_PHASE8_KEY_REGISTRATION_STATUS.csv"
    content = key_reg_path.read_text(encoding="utf-8")
    assert "FIPS 140-2 Level 3" not in content
    assert "FIPS Unverified" in content or "TPM 2.0" in content


def test_candidate_tokenizer_hashes_invariant():
    """Verify Candidate A and Candidate B tokenizer SHA-256 hashes remain invariant."""
    cand_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
    assert sha256_file(cand_a) == CANDIDATE_A_HASH
    assert sha256_file(cand_b) == CANDIDATE_B_HASH


def test_phase11_final_verdict():
    """Verify Phase 11 final status selects Verdict A."""
    status_path = PATCH_ROOT / "IGRIS_PHASE11_FINAL_STATUS.md"
    content = status_path.read_text(encoding="utf-8")
    assert "[X] A. OWNER APPROVAL RECORDED; GOVERNANCE TRANSITION COMPLETE." in content
    assert "[ ] B." in content
    assert "[ ] C." in content
    assert "[ ] D." in content
