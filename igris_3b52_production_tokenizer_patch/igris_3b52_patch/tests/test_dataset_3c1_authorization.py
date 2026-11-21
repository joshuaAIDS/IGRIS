"""Tests for IGRIS Milestone 3C.1 — Human Authorization & Dataset Approval.

Validates the Phase 4 requirements:
- Missing approvals are rejected.
- Invalid signatures are rejected.
- Expired approvals are rejected.
- Modified manifests are rejected.
- Revoked approvals are rejected.
- Pending approvals are rejected.
- Only fully authorized records pass.
- Proposed production datasets remain strictly blocked under default-deny.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
import pytest

# Add patch src and scripts
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
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
from dataset_inventory import generate_manifest

REGISTER_CSV_PATH = _PATCH_ROOT / "DATASET_APPROVAL_REGISTER.csv"
HUMAN_APPROVAL_RECORDS_PATH = _PATCH_ROOT / "HUMAN_APPROVAL_RECORDS.md"


def _create_synthetic_3c1_auth(
    dataset_id: str = "DS-SYNTH-3C1-001",
    status: AuthorizationStatus = AuthorizationStatus.APPROVED,
    manifest_sha256: str = "4" * 64,
    screening_verified: bool = True,
    license_approved: bool = True,
    expiry_date: str = "2027-11-17T00:00:00Z",
    roles_decisions: dict[SignOffRole, str] | None = None,
) -> DatasetAuthorizationRecord:
    if roles_decisions is None:
        roles_decisions = {r: "APPROVED" for r in REQUIRED_ROLES}

    sign_offs = [
        SignOffRecord(
            role=role,
            name=f"Signatory {role.value}",
            timestamp="2026-11-17T12:00:00Z",
            signature_hash=hashlib.sha256(f"SIG_3C1_{role.value}".encode()).hexdigest(),
            decision=decision,
            notes="Milestone 3C.1 synthetic fixture",
        )
        for role, decision in roles_decisions.items()
    ]

    return DatasetAuthorizationRecord(
        dataset_id=dataset_id,
        dataset_name="synthetic_3c1_fixture",
        version="1.0.0",
        target_milestone="3C.1",
        scope="TOKENIZER_EVALUATION_ONLY",
        manifest_sha256=manifest_sha256,
        status=status,
        screening_verified=screening_verified,
        license_approved=license_approved,
        issue_date="2026-11-17T00:00:00Z",
        expiry_date=expiry_date,
        sign_offs=sign_offs,
    )


def _write_auth_file(record: DatasetAuthorizationRecord, path: Path) -> None:
    data = {
        "dataset_id": record.dataset_id,
        "dataset_name": record.dataset_name,
        "version": record.version,
        "target_milestone": record.target_milestone,
        "scope": record.scope,
        "manifest_sha256": record.manifest_sha256,
        "status": record.status.value,
        "screening_verified": record.screening_verified,
        "license_approved": record.license_approved,
        "issue_date": record.issue_date,
        "expiry_date": record.expiry_date,
        "sign_offs": [
            {
                "role": so.role.value,
                "name": so.name,
                "timestamp": so.timestamp,
                "signature_hash": so.signature_hash,
                "decision": so.decision,
                "notes": so.notes,
            }
            for so in record.sign_offs
        ],
    }
    content = f"# Authorization Record\n\n```json\n{json.dumps(data, indent=2)}\n```\n"
    path.write_text(content, encoding="utf-8")


class TestMilestone3C1Validation:
    """Test suite for Milestone 3C.1 Phase 4 validation."""

    def test_approval_register_exists_and_proposed_are_pending(self):
        assert REGISTER_CSV_PATH.is_file(), f"Missing {REGISTER_CSV_PATH}"
        with open(REGISTER_CSV_PATH, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        assert len(reader) >= 13  # 10 proposed + 3 reference
        proposed = [r for r in reader if r["dataset_id"].startswith("DS-PROD-")]
        assert len(proposed) == 10, f"Expected 10 proposed production datasets, found {len(proposed)}"

        for p in proposed:
            assert p["overall_authorization_status"] == "PENDING"
            assert p["custodian_approval"] == "PENDING"
            assert p["legal_approval"] == "PENDING"
            assert p["security_approval"] == "PENDING"
            assert p["architect_approval"] == "PENDING"
            assert p["privacy_screening_status"] == "PENDING"

    def test_human_approval_records_file_exists(self):
        assert HUMAN_APPROVAL_RECORDS_PATH.is_file(), f"Missing {HUMAN_APPROVAL_RECORDS_PATH}"
        content = HUMAN_APPROVAL_RECORDS_PATH.read_text(encoding="utf-8")
        assert "DS-PROD-TM-001" in content
        assert "DATA_CUSTODIAN" in content
        assert "LEGAL_GOVERNANCE" in content
        assert "SECURITY_PRIVACY" in content
        assert "CHIEF_ARCHITECT" in content

    def test_missing_approvals_rejected(self):
        # Omit Legal and Security
        roles = {
            SignOffRole.DATA_CUSTODIAN: "APPROVED",
            SignOffRole.CHIEF_ARCHITECT: "APPROVED",
        }
        rec = _create_synthetic_3c1_auth(roles_decisions=roles)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Missing required human sign-offs"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_invalid_signatures_rejected(self):
        rec = _create_synthetic_3c1_auth()
        # Corrupt signature to non-hex
        rec.sign_offs[0].signature_hash = "NOT_A_VALID_HEX_HASH_12345"
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Invalid digital signature hash"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_expired_approvals_rejected(self):
        rec = _create_synthetic_3c1_auth(expiry_date="2024-01-01T00:00:00Z")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            ref_now = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)
            with pytest.raises(DatasetAccessDeniedError, match="Authorization expired"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p, reference_time=ref_now)
        finally:
            if p.exists():
                p.unlink()

    def test_modified_manifests_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            data_file = td_path / "corpus.jsonl"
            data_file.write_text("{\"text\": \"milestone 3c1 content\"}\n", encoding="utf-8")

            mf_path = td_path / "manifest.json"
            mf = generate_manifest(td_path, dataset_id="DS-MOD-MF", output_manifest_path=mf_path)

            rec = _create_synthetic_3c1_auth(
                dataset_id="DS-MOD-MF",
                manifest_sha256=mf["manifest_sha256"],
            )
            auth_path = td_path / "auth.md"
            _write_auth_file(rec, auth_path)

            # Valid initially
            assert AuthorizationValidator.enforce_access_gate(
                "DS-MOD-MF", auth_path, manifest_path=mf_path, target_dir=td_path
            )

            # Modify manifest content
            mf["total_bytes"] += 100
            with open(mf_path, "w", encoding="utf-8") as f:
                json.dump(mf, f, indent=2, sort_keys=True)

            # Access gate catches modification
            with pytest.raises(DatasetAccessDeniedError, match="Tamper alert"):
                AuthorizationValidator.enforce_access_gate(
                    "DS-MOD-MF", auth_path, manifest_path=mf_path, target_dir=td_path
                )

    def test_revoked_approvals_rejected(self):
        rec = _create_synthetic_3c1_auth(status=AuthorizationStatus.REVOKED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Status is 'REVOKED'"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_pending_approvals_rejected(self):
        for pending_status in [AuthorizationStatus.PENDING, AuthorizationStatus.PENDING_REVIEW]:
            rec = _create_synthetic_3c1_auth(status=pending_status)
            with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
                p = Path(tf.name)
            try:
                _write_auth_file(rec, p)
                with pytest.raises(DatasetAccessDeniedError, match="Status is 'PENDING"):
                    AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
            finally:
                if p.exists():
                    p.unlink()

    def test_only_fully_authorized_records_pass(self):
        rec = _create_synthetic_3c1_auth(
            dataset_id="DS-VALID-3C1",
            status=AuthorizationStatus.APPROVED,
            screening_verified=True,
            license_approved=True,
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            val = AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
            assert val.dataset_id == "DS-VALID-3C1"
            assert val.status == AuthorizationStatus.APPROVED
            assert len(val.sign_offs) == 4
        finally:
            if p.exists():
                p.unlink()

    def test_proposed_production_datasets_are_strictly_blocked(self):
        # A pending production dataset cannot be accessed through the gate
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            raw_pending_json = {
                "dataset_id": "DS-PROD-TM-001",
                "version": "1.0.0",
                "manifest_sha256": "0" * 64,
                "status": "PENDING",
                "screening_verified": False,
                "license_approved": False,
                "sign_offs": [],
            }
            p.write_text(f"```json\n{json.dumps(raw_pending_json)}\n```", encoding="utf-8")
            with pytest.raises(DatasetAccessDeniedError, match="Status is 'PENDING'"):
                AuthorizationValidator.enforce_access_gate("DS-PROD-TM-001", p)
        finally:
            if p.exists():
                p.unlink()
