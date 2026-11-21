"""Tests for IGRIS Dataset Authorization and Access Control Gatekeeper.

Milestone: 3B.60 — Dataset Authorization & Inventory Preparation
Module: tests/test_dataset_authorization.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
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

AUTH_TEMPLATE_PATH = _PATCH_ROOT / "DATASET_AUTHORIZATION_TEMPLATE.md"


def _create_synthetic_auth_record(
    dataset_id: str = "DS-TEST-001",
    status: AuthorizationStatus = AuthorizationStatus.APPROVED,
    manifest_sha256: str = "0" * 64,
    screening_verified: bool = True,
    license_approved: bool = True,
    roles_decisions: dict[SignOffRole, str] | None = None,
) -> DatasetAuthorizationRecord:
    if roles_decisions is None:
        roles_decisions = {
            SignOffRole.DATA_CUSTODIAN: "APPROVED",
            SignOffRole.LEGAL_GOVERNANCE: "APPROVED",
            SignOffRole.SECURITY_PRIVACY: "APPROVED",
            SignOffRole.CHIEF_ARCHITECT: "APPROVED",
        }

    sign_offs = [
        SignOffRecord(
            role=role,
            name=f"Approver {role.value}",
            timestamp="2026-11-17T12:00:00Z",
            signature_hash=hashlib.sha256(role.value.encode()).hexdigest(),
            decision=decision,
            notes="Synthetic test approval",
        )
        for role, decision in roles_decisions.items()
    ]

    return DatasetAuthorizationRecord(
        dataset_id=dataset_id,
        dataset_name="synthetic_dataset",
        version="1.0.0",
        target_milestone="3B.60",
        scope="TOKENIZER_EVALUATION_ONLY",
        manifest_sha256=manifest_sha256,
        status=status,
        screening_verified=screening_verified,
        license_approved=license_approved,
        issue_date="2026-11-17T00:00:00Z",
        expiry_date="2027-11-17T00:00:00Z",
        sign_offs=sign_offs,
    )


def _write_auth_markdown(record: DatasetAuthorizationRecord, target_path: Path) -> None:
    data_dict = {
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
    content = f"# Dataset Authorization\n\n```json\n{json.dumps(data_dict, indent=2)}\n```\n"
    target_path.write_text(content, encoding="utf-8")


class TestDatasetAuthorization:
    """Test suite for human approval records, access control gates, and tamper detection."""

    def test_authorization_template_parses_and_passes_gate(self):
        assert AUTH_TEMPLATE_PATH.is_file(), f"Template missing at {AUTH_TEMPLATE_PATH}"
        rec = AuthorizationValidator.parse_authorization_file(AUTH_TEMPLATE_PATH)
        assert rec.dataset_id == "DS-SYNTH-TM-001"
        assert rec.status == AuthorizationStatus.APPROVED
        assert len(rec.sign_offs) == 4

        # Gate check for template passes
        validated = AuthorizationValidator.enforce_access_gate(
            dataset_id="DS-SYNTH-TM-001",
            auth_record_path=AUTH_TEMPLATE_PATH,
        )
        assert validated.dataset_id == "DS-SYNTH-TM-001"

    def test_missing_auth_file_denies_access(self):
        non_existent = _PATCH_ROOT / "non_existent_auth.md"
        with pytest.raises(DatasetAccessDeniedError, match="Authorization file does not exist"):
            AuthorizationValidator.enforce_access_gate("DS-UNKNOWN", non_existent)

    def test_dataset_id_mismatch_denies_access(self):
        with pytest.raises(DatasetAccessDeniedError, match="Authorization record belongs to"):
            AuthorizationValidator.enforce_access_gate("DS-OTHER-ID", AUTH_TEMPLATE_PATH)

    def test_status_not_approved_denies_access(self):
        for status in [
            AuthorizationStatus.LOCKED,
            AuthorizationStatus.PENDING_REVIEW,
            AuthorizationStatus.REJECTED,
            AuthorizationStatus.REVOKED,
        ]:
            rec = _create_synthetic_auth_record(status=status)
            with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
                tf_path = Path(tf.name)
            try:
                _write_auth_markdown(rec, tf_path)
                with pytest.raises(DatasetAccessDeniedError, match=f"Status is '{status.value}'"):
                    AuthorizationValidator.enforce_access_gate(rec.dataset_id, tf_path)
            finally:
                if tf_path.exists():
                    tf_path.unlink()

    def test_missing_required_role_denies_access(self):
        # Omit Chief Architect
        roles = {
            SignOffRole.DATA_CUSTODIAN: "APPROVED",
            SignOffRole.LEGAL_GOVERNANCE: "APPROVED",
            SignOffRole.SECURITY_PRIVACY: "APPROVED",
        }
        rec = _create_synthetic_auth_record(roles_decisions=roles)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            tf_path = Path(tf.name)
        try:
            _write_auth_markdown(rec, tf_path)
            with pytest.raises(DatasetAccessDeniedError, match="Missing required human sign-offs"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, tf_path)
        finally:
            if tf_path.exists():
                tf_path.unlink()

    def test_rejected_decision_denies_access(self):
        # Security rejects
        roles = {
            SignOffRole.DATA_CUSTODIAN: "APPROVED",
            SignOffRole.LEGAL_GOVERNANCE: "APPROVED",
            SignOffRole.SECURITY_PRIVACY: "REJECTED",
            SignOffRole.CHIEF_ARCHITECT: "APPROVED",
        }
        rec = _create_synthetic_auth_record(roles_decisions=roles)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            tf_path = Path(tf.name)
        try:
            _write_auth_markdown(rec, tf_path)
            with pytest.raises(DatasetAccessDeniedError, match="was 'REJECTED'"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, tf_path)
        finally:
            if tf_path.exists():
                tf_path.unlink()

    def test_unverified_screening_denies_access(self):
        rec = _create_synthetic_auth_record(screening_verified=False)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            tf_path = Path(tf.name)
        try:
            _write_auth_markdown(rec, tf_path)
            with pytest.raises(DatasetAccessDeniedError, match="PII screening verification is incomplete"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, tf_path)
        finally:
            if tf_path.exists():
                tf_path.unlink()

    def test_unapproved_license_denies_access(self):
        rec = _create_synthetic_auth_record(license_approved=False)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            tf_path = Path(tf.name)
        try:
            _write_auth_markdown(rec, tf_path)
            with pytest.raises(DatasetAccessDeniedError, match="Licensing approval is incomplete"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, tf_path)
        finally:
            if tf_path.exists():
                tf_path.unlink()

    def test_invalid_signature_hash_denies_access(self):
        rec = _create_synthetic_auth_record()
        rec.sign_offs[0].signature_hash = "not_a_valid_hash"
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            tf_path = Path(tf.name)
        try:
            _write_auth_markdown(rec, tf_path)
            with pytest.raises(DatasetAccessDeniedError, match="Invalid digital signature hash"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, tf_path)
        finally:
            if tf_path.exists():
                tf_path.unlink()

    def test_manifest_hash_tamper_detection(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            data_file = td_path / "sample.jsonl"
            data_file.write_text("{\"text\": \"valid content\"}\n", encoding="utf-8")

            mf_path = td_path / "manifest.json"
            manifest = generate_manifest(td_path, dataset_id="DS-TAMPER-TEST", output_manifest_path=mf_path)

            rec = _create_synthetic_auth_record(
                dataset_id="DS-TAMPER-TEST",
                manifest_sha256=manifest["manifest_sha256"],
            )
            auth_path = td_path / "auth.md"
            _write_auth_markdown(rec, auth_path)

            # Legitimate access succeeds
            val = AuthorizationValidator.enforce_access_gate(
                dataset_id="DS-TAMPER-TEST",
                auth_record_path=auth_path,
                manifest_path=mf_path,
                target_dir=td_path,
            )
            assert val.dataset_id == "DS-TAMPER-TEST"

            # Tamper with manifest: change total_lines
            manifest["total_lines"] = 9999
            with open(mf_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, sort_keys=True)

            # Access gate catches tampering
            with pytest.raises(DatasetAccessDeniedError, match="Tamper alert: Manifest computed hash"):
                AuthorizationValidator.enforce_access_gate(
                    dataset_id="DS-TAMPER-TEST",
                    auth_record_path=auth_path,
                    manifest_path=mf_path,
                    target_dir=td_path,
                )

    def test_file_content_tamper_detection(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            data_file = td_path / "sample.jsonl"
            data_file.write_text("{\"text\": \"original content\"}\n", encoding="utf-8")

            mf_path = td_path / "manifest.json"
            manifest = generate_manifest(td_path, dataset_id="DS-FILE-TAMPER", output_manifest_path=mf_path)

            rec = _create_synthetic_auth_record(
                dataset_id="DS-FILE-TAMPER",
                manifest_sha256=manifest["manifest_sha256"],
            )
            auth_path = td_path / "auth.md"
            _write_auth_markdown(rec, auth_path)

            # Modify file content on disk without updating manifest
            data_file.write_text("{\"text\": \"tampered content!!\"}\n", encoding="utf-8")

            # Access gate catches file hash mismatch
            with pytest.raises(DatasetAccessDeniedError, match="File hash mismatch"):
                AuthorizationValidator.enforce_access_gate(
                    dataset_id="DS-FILE-TAMPER",
                    auth_record_path=auth_path,
                    manifest_path=mf_path,
                    target_dir=td_path,
                )
