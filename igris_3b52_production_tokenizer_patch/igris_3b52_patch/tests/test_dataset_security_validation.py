"""Tests for IGRIS Milestone 3B.61 — Dataset Authorization Dry Run & Security Validation.

Validates the full authorization lifecycle, default-deny enforcement,
tamper detection, failure modes, inventory-to-authorization consistency,
and CLI/library access control using synthetic fixtures only.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
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
from dataset_inventory import (
    DatasetInventory,
    DatasetInventoryRecord,
    generate_manifest,
)

AUTH_TEMPLATE_PATH = _PATCH_ROOT / "DATASET_AUTHORIZATION_TEMPLATE.md"
INVENTORY_TEMPLATE_PATH = _PATCH_ROOT / "DATASET_INVENTORY_TEMPLATE.csv"


def _create_synthetic_sign_off(role: SignOffRole, decision: str = "APPROVED") -> SignOffRecord:
    return SignOffRecord(
        role=role,
        name=f"Tester {role.value}",
        timestamp="2026-11-17T12:00:00Z",
        signature_hash=hashlib.sha256(f"SIG_{role.value}".encode()).hexdigest(),
        decision=decision,
        notes="Synthetic test fixture",
    )


def _create_synthetic_auth(
    dataset_id: str = "DS-SYNTH-SEC-001",
    status: AuthorizationStatus = AuthorizationStatus.APPROVED,
    manifest_sha256: str = "1" * 64,
    screening_verified: bool = True,
    license_approved: bool = True,
    expiry_date: str = "2027-11-17T00:00:00Z",
    sign_offs: list[SignOffRecord] | None = None,
) -> DatasetAuthorizationRecord:
    if sign_offs is None:
        sign_offs = [_create_synthetic_sign_off(r) for r in REQUIRED_ROLES]

    return DatasetAuthorizationRecord(
        dataset_id=dataset_id,
        dataset_name="synthetic_security_fixture",
        version="1.0.0",
        target_milestone="3B.61",
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
    content = f"# Synthetic Authorization\n\n```json\n{json.dumps(data, indent=2)}\n```\n"
    path.write_text(content, encoding="utf-8")


class TestMilestone3B61SecurityValidation:
    """Comprehensive test matrix for Milestone 3B.61 security validation."""

    # ------------------------------------------------------------------
    # TASK 1 & 2: Test all five authorization states
    # ------------------------------------------------------------------
    def test_state_locked_fails_gate(self):
        rec = _create_synthetic_auth(status=AuthorizationStatus.LOCKED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Status is 'LOCKED'"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_state_pending_review_fails_gate(self):
        rec = _create_synthetic_auth(status=AuthorizationStatus.PENDING_REVIEW)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Status is 'PENDING_REVIEW'"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_state_approved_passes_gate(self):
        rec = _create_synthetic_auth(status=AuthorizationStatus.APPROVED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            validated = AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
            assert validated.dataset_id == rec.dataset_id
            assert validated.status == AuthorizationStatus.APPROVED
        finally:
            if p.exists():
                p.unlink()

    def test_state_rejected_fails_gate(self):
        rec = _create_synthetic_auth(status=AuthorizationStatus.REJECTED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Status is 'REJECTED'"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_state_revoked_fails_gate(self):
        rec = _create_synthetic_auth(status=AuthorizationStatus.REVOKED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Status is 'REVOKED'"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    # ------------------------------------------------------------------
    # TASK 3: Detailed failure modes
    # ------------------------------------------------------------------
    def test_missing_signatures_partial(self):
        # 3 out of 4 sign-offs present
        partial_roles = [
            SignOffRole.DATA_CUSTODIAN,
            SignOffRole.LEGAL_GOVERNANCE,
            SignOffRole.SECURITY_PRIVACY,
        ]
        sign_offs = [_create_synthetic_sign_off(r) for r in partial_roles]
        rec = _create_synthetic_auth(sign_offs=sign_offs)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Missing required human sign-offs"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_invalid_role_in_json_fails_parse(self):
        raw_json = {
            "dataset_id": "DS-BAD-ROLE",
            "version": "1.0.0",
            "manifest_sha256": "2" * 64,
            "status": "APPROVED",
            "screening_verified": True,
            "license_approved": True,
            "sign_offs": [
                {
                    "role": "EXTERNAL_CONSULTANT",  # Invalid role
                    "name": "Jane Doe",
                    "timestamp": "2026-11-17T00:00:00Z",
                    "signature_hash": "3" * 64,
                    "decision": "APPROVED",
                }
            ],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            p.write_text(f"```json\n{json.dumps(raw_json)}\n```", encoding="utf-8")
            with pytest.raises(DatasetAccessDeniedError, match="Unrecognized sign-off role"):
                AuthorizationValidator.enforce_access_gate("DS-BAD-ROLE", p)
        finally:
            if p.exists():
                p.unlink()

    def test_expired_approval_fails_gate(self):
        # Expired in 2025
        rec = _create_synthetic_auth(expiry_date="2025-01-01T00:00:00Z")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            ref_time = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)
            with pytest.raises(DatasetAccessDeniedError, match="Authorization expired on 2025-01-01T00:00:00Z"):
                AuthorizationValidator.enforce_access_gate(
                    rec.dataset_id, p, reference_time=ref_time
                )
        finally:
            if p.exists():
                p.unlink()

    def test_malformed_metadata_missing_keys(self):
        # Missing 'manifest_sha256'
        raw_json = {
            "dataset_id": "DS-MISSING-KEYS",
            "version": "1.0.0",
            "status": "APPROVED",
            "screening_verified": True,
            "license_approved": True,
            "sign_offs": [],
        }
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            p.write_text(f"```json\n{json.dumps(raw_json)}\n```", encoding="utf-8")
            with pytest.raises(DatasetAccessDeniedError, match="missing required fields"):
                AuthorizationValidator.enforce_access_gate("DS-MISSING-KEYS", p)
        finally:
            if p.exists():
                p.unlink()

    def test_malformed_json_syntax_fails_gate(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            p.write_text("```json\n{ \"invalid\": [1, 2, } \n```", encoding="utf-8")
            with pytest.raises(DatasetAccessDeniedError, match="Malformed JSON in authorization block"):
                AuthorizationValidator.enforce_access_gate("DS-BAD-JSON", p)
        finally:
            if p.exists():
                p.unlink()

    # ------------------------------------------------------------------
    # TASK 4: Inventory-to-Authorization consistency
    # ------------------------------------------------------------------
    def test_inventory_consistency_status_mismatch(self):
        auth_rec = _create_synthetic_auth(dataset_id="DS-SYNTH-TM-001", status=AuthorizationStatus.APPROVED)
        # Create inventory record with PENDING_REVIEW
        inv_rec = DatasetInventoryRecord(
            dataset_id="DS-SYNTH-TM-001",
            dataset_name="tamil_news_eval_synthetic",
            version="1.0.0",
            category="Tamil",
            language="ta",
            script="Taml",
            file_path="synthetic/eval/tamil/sample_news.jsonl",
            format="jsonl",
            encoding="UTF-8",
            line_count=500,
            character_count=75240,
            byte_size=210450,
            sha256_checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            license="CC-BY-4.0",
            owner="DataPlatform",
            custodian="custodian_tamil@igris.internal",
            authorization_status="PENDING_REVIEW",  # Mismatch vs APPROVED
            approval_ticket_id="GOV-2026-3B60-01",
            screening_status="SCREENED_CLEAN",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(auth_rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Authorization status mismatch"):
                AuthorizationValidator.enforce_access_gate(
                    "DS-SYNTH-TM-001", p, inventory_record=inv_rec
                )
        finally:
            if p.exists():
                p.unlink()

    def test_inventory_consistency_screening_mismatch(self):
        auth_rec = _create_synthetic_auth(dataset_id="DS-SYNTH-TM-001", screening_verified=True)
        inv_rec = DatasetInventoryRecord(
            dataset_id="DS-SYNTH-TM-001",
            dataset_name="tamil_news_eval_synthetic",
            version="1.0.0",
            category="Tamil",
            language="ta",
            script="Taml",
            file_path="synthetic/eval/tamil/sample_news.jsonl",
            format="jsonl",
            encoding="UTF-8",
            line_count=500,
            character_count=75240,
            byte_size=210450,
            sha256_checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            license="CC-BY-4.0",
            owner="DataPlatform",
            custodian="custodian_tamil@igris.internal",
            authorization_status="APPROVED",
            approval_ticket_id="GOV-2026-3B60-01",
            screening_status="PENDING",  # Mismatch vs screening_verified=True
        )
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(auth_rec, p)
            with pytest.raises(DatasetAccessDeniedError, match="Screening status mismatch"):
                AuthorizationValidator.enforce_access_gate(
                    "DS-SYNTH-TM-001", p, inventory_record=inv_rec
                )
        finally:
            if p.exists():
                p.unlink()

    # ------------------------------------------------------------------
    # TASK 5: CLI and Library entry-point protection
    # ------------------------------------------------------------------
    def test_cli_blocks_unauthorized_dataset(self):
        # Call scripts/dataset_authorization.py on locked fixture via subprocess
        rec = _create_synthetic_auth(dataset_id="DS-CLI-BLOCK", status=AuthorizationStatus.LOCKED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(Path(_PATCH_SCRIPTS) / "dataset_authorization.py"),
                    "--auth-file",
                    str(p),
                ],
                capture_output=True,
                text=True,
            )
            assert proc.returncode != 0
            assert "DENIED" in proc.stdout or "DENIED" in proc.stderr
        finally:
            if p.exists():
                p.unlink()

    def test_library_get_authorized_dataset_path_blocks_unauthorized(self):
        rec = _create_synthetic_auth(status=AuthorizationStatus.LOCKED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            with pytest.raises(DatasetAccessDeniedError):
                AuthorizationValidator.get_authorized_dataset_path(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()

    def test_inventory_get_authorized_record_blocks_non_approved(self):
        inv = DatasetInventory.load_from_csv(INVENTORY_TEMPLATE_PATH)
        # DS-SYNTH-ML-006 is LOCKED in template
        with pytest.raises(PermissionError, match="is in 'LOCKED' state"):
            inv.get_authorized_record("DS-SYNTH-ML-006")

        # DS-SYNTH-TG-004 is PENDING_REVIEW in template
        with pytest.raises(PermissionError, match="is in 'PENDING_REVIEW' state"):
            inv.get_authorized_record("DS-SYNTH-TG-004")

    # ------------------------------------------------------------------
    # TASK 6: Deterministic manifest generation
    # ------------------------------------------------------------------
    def test_deterministic_manifest_repeated_generation(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            (td_path / "a.jsonl").write_text("{\"content\": \"line 1\"}\n", encoding="utf-8")
            (td_path / "b.txt").write_text("Sample text line\nAnother line\n", encoding="utf-8")

            mf1 = generate_manifest(td_path, dataset_id="DS-DET-01")
            mf2 = generate_manifest(td_path, dataset_id="DS-DET-01")

            assert mf1["manifest_sha256"] == mf2["manifest_sha256"]
            assert mf1["total_bytes"] == mf2["total_bytes"]
            assert mf1["total_lines"] == mf2["total_lines"]
            assert mf1["total_characters"] == mf2["total_characters"]
            assert len(mf1["files"]) == len(mf2["files"])
            for f1_entry, f2_entry in zip(mf1["files"], mf2["files"]):
                assert f1_entry["relative_path"] == f2_entry["relative_path"]
                assert f1_entry["sha256"] == f2_entry["sha256"]

    # ------------------------------------------------------------------
    # TASK 7: Authorization revocation blocks immediately
    # ------------------------------------------------------------------
    def test_revocation_blocks_immediately(self):
        rec = _create_synthetic_auth(status=AuthorizationStatus.APPROVED)
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            p = Path(tf.name)
        try:
            _write_auth_file(rec, p)
            # 1. APPROVED passes
            val = AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
            assert val.status == AuthorizationStatus.APPROVED

            # 2. Revoke status
            rec.status = AuthorizationStatus.REVOKED
            _write_auth_file(rec, p)

            # 3. Access is immediately blocked
            with pytest.raises(DatasetAccessDeniedError, match="Status is 'REVOKED'"):
                AuthorizationValidator.enforce_access_gate(rec.dataset_id, p)
        finally:
            if p.exists():
                p.unlink()
