#!/usr/bin/env python3
"""IGRIS Tokenizer Dataset Authorization and Access Control Validator.

Milestone: 3B.61 — Dataset Authorization Dry Run & Security Validation
Module: scripts/dataset_authorization.py

Enforces default-deny dataset governance, parses multi-signature markdown
authorization records, verifies cryptographic manifest hashes, validates
inventory consistency, checks approval expiration, and acts as the
programmatic gatekeeper for evaluation and training pipelines.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

HEX_64_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")


class AuthorizationStatus(str, Enum):
    LOCKED = "LOCKED"
    PENDING = "PENDING"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class SignOffRole(str, Enum):
    DATA_CUSTODIAN = "DATA_CUSTODIAN"
    LEGAL_GOVERNANCE = "LEGAL_GOVERNANCE"
    SECURITY_PRIVACY = "SECURITY_PRIVACY"
    CHIEF_ARCHITECT = "CHIEF_ARCHITECT"


REQUIRED_ROLES: Set[SignOffRole] = {
    SignOffRole.DATA_CUSTODIAN,
    SignOffRole.LEGAL_GOVERNANCE,
    SignOffRole.SECURITY_PRIVACY,
    SignOffRole.CHIEF_ARCHITECT,
}


class DatasetAccessDeniedError(PermissionError):
    """Raised when access to a dataset is denied by the authorization gate."""
    pass


@dataclass
class SignOffRecord:
    role: SignOffRole
    name: str
    timestamp: str
    signature_hash: str
    decision: str
    notes: Optional[str] = None


@dataclass
class DatasetAuthorizationRecord:
    dataset_id: str
    dataset_name: str
    version: str
    target_milestone: str
    scope: str
    manifest_sha256: str
    status: AuthorizationStatus
    screening_verified: bool
    license_approved: bool
    issue_date: str
    expiry_date: str
    sign_offs: List[SignOffRecord]


class AuthorizationValidator:
    """Validates authorization records and programmatically enforces access gates."""

    @staticmethod
    def parse_authorization_file(auth_file_path: Union[str, Path]) -> DatasetAuthorizationRecord:
        path = Path(auth_file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Authorization file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON metadata block found in authorization file: {path}")

        raw_json_str = match.group(1)
        try:
            data = json.loads(raw_json_str)
        except json.JSONDecodeError as ex:
            raise ValueError(f"Malformed JSON in authorization block: {ex}") from ex

        # Verify essential fields are present
        required_keys = {
            "dataset_id",
            "version",
            "manifest_sha256",
            "status",
            "screening_verified",
            "license_approved",
            "sign_offs",
        }
        missing_keys = required_keys - set(data.keys())
        if missing_keys:
            raise ValueError(f"Authorization metadata missing required fields: {missing_keys}")

        sign_offs: List[SignOffRecord] = []
        for so in data.get("sign_offs", []):
            role_str = so.get("role", "")
            try:
                role_enum = SignOffRole(role_str)
            except ValueError:
                raise ValueError(f"Unrecognized sign-off role '{role_str}' in authorization record")

            sign_offs.append(
                SignOffRecord(
                    role=role_enum,
                    name=so.get("name", "").strip(),
                    timestamp=so.get("timestamp", "").strip(),
                    signature_hash=so.get("signature_hash", "").strip(),
                    decision=so.get("decision", "").strip().upper(),
                    notes=so.get("notes"),
                )
            )

        status_str = data.get("status", "").strip().upper()
        try:
            status_enum = AuthorizationStatus(status_str)
        except ValueError:
            raise ValueError(f"Unrecognized authorization status '{status_str}'")

        return DatasetAuthorizationRecord(
            dataset_id=data.get("dataset_id", "").strip(),
            dataset_name=data.get("dataset_name", "").strip(),
            version=data.get("version", "").strip(),
            target_milestone=data.get("target_milestone", "").strip(),
            scope=data.get("scope", "").strip(),
            manifest_sha256=data.get("manifest_sha256", "").strip(),
            status=status_enum,
            screening_verified=bool(data.get("screening_verified", False)),
            license_approved=bool(data.get("license_approved", False)),
            issue_date=data.get("issue_date", "").strip(),
            expiry_date=data.get("expiry_date", "").strip(),
            sign_offs=sign_offs,
        )

    @classmethod
    def verify_inventory_consistency(
        cls,
        record: DatasetAuthorizationRecord,
        inventory_record: Any,
    ) -> Tuple[bool, List[str]]:
        """Verify that an authorization record is strictly consistent with the inventory record."""
        issues: List[str] = []

        if record.dataset_id != inventory_record.dataset_id:
            issues.append(
                f"Dataset ID mismatch: auth has '{record.dataset_id}', inventory has '{inventory_record.dataset_id}'"
            )

        if record.version != inventory_record.version:
            issues.append(
                f"Version mismatch for '{record.dataset_id}': auth has '{record.version}', inventory has '{inventory_record.version}'"
            )

        if record.status.value != inventory_record.authorization_status:
            issues.append(
                f"Authorization status mismatch for '{record.dataset_id}': auth has '{record.status.value}', inventory has '{inventory_record.authorization_status}'"
            )

        if record.screening_verified and inventory_record.screening_status != "SCREENED_CLEAN":
            issues.append(
                f"Screening status mismatch for '{record.dataset_id}': auth claims verified, but inventory is '{inventory_record.screening_status}'"
            )

        return len(issues) == 0, issues

    @classmethod
    def verify_authorization(
        cls,
        record: DatasetAuthorizationRecord,
        manifest_path: Optional[Union[str, Path]] = None,
        target_dir: Optional[Union[str, Path]] = None,
        inventory_record: Optional[Any] = None,
        reference_time: Optional[datetime] = None,
    ) -> Tuple[bool, List[str]]:
        """Verify the full integrity and human approval compliance of an authorization record."""
        issues: List[str] = []

        # Check authorization status
        if record.status != AuthorizationStatus.APPROVED:
            issues.append(f"Status is '{record.status.value}', expected '{AuthorizationStatus.APPROVED.value}'")

        # Check screening and licensing flags
        if not record.screening_verified:
            issues.append("PII screening verification is incomplete or failed (screening_verified is false)")

        if not record.license_approved:
            issues.append("Licensing approval is incomplete or rejected (license_approved is false)")

        if not HEX_64_REGEX.match(record.manifest_sha256):
            issues.append(f"Invalid manifest_sha256 hash format: '{record.manifest_sha256}'")

        # Check expiration date
        if record.expiry_date:
            try:
                exp_dt = datetime.fromisoformat(record.expiry_date)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                now = reference_time or datetime.now(timezone.utc)
                if exp_dt < now:
                    issues.append(
                        f"Authorization expired on {record.expiry_date} (current check time: {now.isoformat()})"
                    )
            except Exception as ex:
                issues.append(f"Invalid expiry_date format '{record.expiry_date}': {ex}")

        # Check required roles
        present_roles = {so.role for so in record.sign_offs}
        missing_roles = REQUIRED_ROLES - present_roles
        if missing_roles:
            issues.append(f"Missing required human sign-offs for roles: {[r.value for r in missing_roles]}")

        for so in record.sign_offs:
            if so.decision != "APPROVED":
                issues.append(f"Sign-off for role '{so.role.value}' by '{so.name}' was '{so.decision}'")
            if not HEX_64_REGEX.match(so.signature_hash):
                issues.append(f"Invalid digital signature hash for role '{so.role.value}': '{so.signature_hash}'")

        # Check inventory consistency if inventory record provided
        if inventory_record is not None:
            inv_valid, inv_issues = cls.verify_inventory_consistency(record, inventory_record)
            if not inv_valid:
                issues.extend(inv_issues)

        # If manifest path provided, verify cryptographic checksum match
        if manifest_path:
            mf_path = Path(manifest_path)
            if not mf_path.is_file():
                issues.append(f"Cryptographic manifest file does not exist: {mf_path}")
            else:
                try:
                    with open(mf_path, "r", encoding="utf-8") as f:
                        mf_data = json.load(f)

                    # Compute manifest hash
                    mf_data_copy = dict(mf_data)
                    mf_data_copy.pop("manifest_sha256", None)
                    raw_str = json.dumps(mf_data_copy, indent=2, sort_keys=True)
                    computed_mf_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

                    expected_hash = record.manifest_sha256
                    file_recorded_hash = mf_data.get("manifest_sha256")

                    if computed_mf_hash.lower() != expected_hash.lower():
                        issues.append(
                            f"Tamper alert: Manifest computed hash '{computed_mf_hash}' does not match authorization record '{expected_hash}'"
                        )
                    elif file_recorded_hash and file_recorded_hash.lower() != expected_hash.lower():
                        issues.append(
                            f"Tamper alert: Manifest embedded hash '{file_recorded_hash}' does not match authorization record '{expected_hash}'"
                        )

                    # If target directory provided, verify individual file hashes
                    if target_dir:
                        t_dir = Path(target_dir)
                        for f_entry in mf_data.get("files", []):
                            rel_p = f_entry.get("relative_path")
                            expected_f_hash = f_entry.get("sha256")
                            expected_bytes = f_entry.get("byte_size")
                            target_file = t_dir / rel_p
                            if not target_file.is_file():
                                issues.append(f"File listed in manifest missing on disk: {target_file}")
                                continue

                            # Check hash
                            h = hashlib.sha256()
                            actual_bytes = 0
                            with open(target_file, "rb") as tf:
                                while True:
                                    chunk = tf.read(65536)
                                    if not chunk:
                                        break
                                    h.update(chunk)
                                    actual_bytes += len(chunk)

                            actual_f_hash = h.hexdigest()
                            if actual_bytes != expected_bytes:
                                issues.append(
                                    f"File byte mismatch for '{rel_p}': expected {expected_bytes}, got {actual_bytes}"
                                )
                            if actual_f_hash.lower() != expected_f_hash.lower():
                                issues.append(
                                    f"File hash mismatch for '{rel_p}': expected {expected_f_hash}, got {actual_f_hash}"
                                )

                except Exception as ex:
                    issues.append(f"Error parsing/verifying manifest {mf_path}: {ex}")

        is_valid = len(issues) == 0
        return is_valid, issues

    @classmethod
    def enforce_access_gate(
        cls,
        dataset_id: str,
        auth_record_path: Union[str, Path],
        manifest_path: Optional[Union[str, Path]] = None,
        target_dir: Optional[Union[str, Path]] = None,
        inventory_record: Optional[Any] = None,
        inventory_csv_path: Optional[Union[str, Path]] = None,
        reference_time: Optional[datetime] = None,
    ) -> DatasetAuthorizationRecord:
        """Enforces the Default-Deny access control gate.

        Raises:
            DatasetAccessDeniedError: If any condition, signature, expiration,
                                      consistency, or hash verification fails.
        """
        p = Path(auth_record_path)
        if not p.is_file():
            raise DatasetAccessDeniedError(
                f"Access denied for dataset '{dataset_id}': Authorization file does not exist at '{p}'. "
                "Production access requires explicit, recorded human authorization."
            )

        try:
            record = cls.parse_authorization_file(p)
        except Exception as ex:
            raise DatasetAccessDeniedError(
                f"Access denied for dataset '{dataset_id}': Failed to parse authorization record: {ex}"
            ) from ex

        if record.dataset_id != dataset_id:
            raise DatasetAccessDeniedError(
                f"Access denied for dataset '{dataset_id}': Authorization record belongs to '{record.dataset_id}', not '{dataset_id}'"
            )

        # If inventory CSV path provided and inventory record not provided, load record
        inv_rec = inventory_record
        if inv_rec is None and inventory_csv_path is not None:
            from dataset_inventory import DatasetInventory

            inv = DatasetInventory.load_from_csv(inventory_csv_path)
            inv_rec = inv.get_record(dataset_id)
            if inv_rec is None:
                raise DatasetAccessDeniedError(
                    f"Access denied for dataset '{dataset_id}': Record not found in inventory CSV '{inventory_csv_path}'"
                )

        is_valid, issues = cls.verify_authorization(
            record,
            manifest_path=manifest_path,
            target_dir=target_dir,
            inventory_record=inv_rec,
            reference_time=reference_time,
        )
        if not is_valid:
            issue_summary = "; ".join(issues)
            raise DatasetAccessDeniedError(
                f"Access denied for dataset '{dataset_id}': Authorization validation failed: {issue_summary}"
            )

        return record

    @classmethod
    def get_authorized_dataset_path(
        cls,
        dataset_id: str,
        auth_record_path: Union[str, Path],
        manifest_path: Optional[Union[str, Path]] = None,
        target_dir: Optional[Union[str, Path]] = None,
        inventory_csv_path: Optional[Union[str, Path]] = None,
        reference_time: Optional[datetime] = None,
    ) -> Path:
        """Safe programmatic entry point.

        Enforces the access gate before returning the verified target directory.
        Raises DatasetAccessDeniedError if unauthorized.
        """
        cls.enforce_access_gate(
            dataset_id=dataset_id,
            auth_record_path=auth_record_path,
            manifest_path=manifest_path,
            target_dir=target_dir,
            inventory_csv_path=inventory_csv_path,
            reference_time=reference_time,
        )
        if target_dir:
            return Path(target_dir)
        elif manifest_path:
            return Path(manifest_path).parent
        else:
            return Path(auth_record_path).parent


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IGRIS Dataset Authorization Gate Utility")
    parser.add_argument("--auth-file", type=str, required=True, help="Path to authorization markdown file")
    parser.add_argument("--dataset-id", type=str, help="Dataset ID to verify")
    parser.add_argument("--manifest", type=str, help="Optional path to manifest.json")
    parser.add_argument("--target-dir", type=str, help="Optional path to target data directory")
    parser.add_argument("--inventory-csv", type=str, help="Optional path to inventory CSV file")

    args = parser.parse_args()

    record = AuthorizationValidator.parse_authorization_file(args.auth_file)
    target_id = args.dataset_id or record.dataset_id

    try:
        validated_record = AuthorizationValidator.enforce_access_gate(
            dataset_id=target_id,
            auth_record_path=args.auth_file,
            manifest_path=args.manifest,
            target_dir=args.target_dir,
            inventory_csv_path=args.inventory_csv,
        )
        print(f"SUCCESS: Authorization gate passed for dataset '{validated_record.dataset_id}'.")
        print(f"Status: {validated_record.status.value}")
        print(f"Sign-offs verified: {len(validated_record.sign_offs)} roles approved.")
    except DatasetAccessDeniedError as ex:
        print(f"DENIED: {ex}")
        exit(1)
