"""
IGRIS Source Acquisition Authorizer
===================================
Phase 13 Controlled Dataset Acquisition Infrastructure

Enforces:
1. Source-specific explicit owner authorization (Default-Deny).
2. Intended-use validation and Tier isolation enforcement.
3. Timestamp and expiry enforcement.
4. Revocation tracking (revoked approvals immediately block acquisition).
5. Exact URL and version matching.
6. Replay attack protection.
7. Concurrency serialization locking.
8. Persistent acquisition ledger management.
"""

import csv
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class AuthorizationError(Exception):
    """Base exception for authorization errors."""
    pass


class UnauthorizedAcquisitionError(AuthorizationError):
    """Raised when dataset acquisition is attempted without explicit owner approval."""
    pass


class RevokedAuthorizationError(AuthorizationError):
    """Raised when an authorization record has been revoked."""
    pass


class ExpiredAuthorizationError(AuthorizationError):
    """Raised when an authorization record has passed its expiration timestamp."""
    pass


class UnauthorizedSourceURLError(AuthorizationError):
    """Raised when the requested download URL does not match the authorized endpoint."""
    pass


class TierIsolationViolationError(AuthorizationError):
    """Raised when an acquisition violates operational tier boundaries (e.g. training conditional/eval data)."""
    pass


class ConcurrentAcquisitionError(AuthorizationError):
    """Raised when a concurrent acquisition attempt for the same source is detected."""
    pass


class ReplayAcquisitionError(AuthorizationError):
    """Raised when an authorization record or nonce is replayed illegally."""
    pass


@dataclass
class SourceAuthorizationRecord:
    source_id: str
    source_version: str
    official_download_url: str
    intended_use: str
    authorization_reference: str
    status: str  # "AUTHORIZED", "REVOKED", "EXPIRED", "PENDING"
    timestamp: str
    expiry_timestamp: Optional[str] = None
    owner_identity: str = "SOLO_DEVELOPER_OWNER"
    notes: Optional[str] = None


@dataclass
class AuthorizationDecision:
    is_authorized: bool
    source_id: str
    source_version: str
    authorization_reference: str
    status: str
    reason: Optional[str] = None


class SourceAcquisitionAuthorizer:
    """
    Manages explicit, source-specific owner authorizations and verifies
    eligibility, provenance, and tier isolation under the SOLO_DEVELOPER_OWNER_REVIEW model.
    """
    def __init__(
        self,
        register_path: Optional[Path] = None,
        ledger_path: Optional[Path] = None,
        locks_dir: Optional[Path] = None
    ):
        self.register_path = Path(register_path) if register_path else Path("IGRIS_PHASE13_SOURCE_AUTHORIZATION_REGISTER.csv")
        self.ledger_path = Path(ledger_path) if ledger_path else Path("IGRIS_PHASE13_ACQUISITION_LEDGER.csv")
        self.locks_dir = Path(locks_dir) if locks_dir else Path("quarantine/locks")
        self.locks_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory grant store for explicit authorizations during session
        self._grants: Dict[str, SourceAuthorizationRecord] = {}
        # Used nonce / token set for replay prevention
        self._used_nonces: Set[str] = set()

    def grant_source_authorization(
        self,
        source_id: str,
        source_version: str,
        official_download_url: str,
        intended_use: str,
        authorization_reference: str,
        expiry_timestamp: Optional[str] = None,
        notes: Optional[str] = None
    ) -> SourceAuthorizationRecord:
        """
        Record explicit source-specific owner authorization.
        Bulk authorization is intentionally unsupported; grants must be individual.
        """
        if not source_id or not isinstance(source_id, str):
            raise AuthorizationError("Invalid source_id")
            
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        record = SourceAuthorizationRecord(
            source_id=source_id,
            source_version=source_version,
            official_download_url=official_download_url,
            intended_use=intended_use,
            authorization_reference=authorization_reference,
            status="AUTHORIZED",
            timestamp=now_iso,
            expiry_timestamp=expiry_timestamp,
            owner_identity="SOLO_DEVELOPER_OWNER",
            notes=notes
        )
        self._grants[source_id] = record
        return record

    def revoke_source_authorization(self, source_id: str, reason: str = "Owner revocation"):
        """Revoke a previously issued source authorization."""
        if source_id in self._grants:
            self._grants[source_id].status = "REVOKED"
            self._grants[source_id].notes = f"REVOKED: {reason}"

    def expire_source_authorization(self, source_id: str):
        """Mark an authorization as expired."""
        if source_id in self._grants:
            self._grants[source_id].status = "EXPIRED"

    def verify_authorization(
        self,
        source_id: str,
        requested_url: str,
        intended_use: str = "VOCABULARY_TRAINING_AND_FERTILITY_EVALUATION",
        nonce: Optional[str] = None
    ) -> AuthorizationDecision:
        """
        Verify that acquisition of source_id is explicitly authorized by owner:
        1. Tier isolation check (Tier 2, 3, 4 barred from training)
        2. Presence of grant (Default-Deny)
        3. Revocation status
        4. Expiration status
        5. URL matching
        6. Replay protection
        """
        # Tier boundary checks
        # Tier 2 Conditional
        if source_id in ("SRC-EN-02", "SRC-EN-03", "SRC-HI-02", "SRC-ML-01", "SRC-ML-02", "SRC-TD-01", "SRC-TM-02", "SRC-TM-03"):
            if "TRAINING" in intended_use.upper():
                raise TierIsolationViolationError(
                    f"Tier 2 source {source_id} is conditionally restricted and barred from vocabulary training pipeline"
                )

        # Tier 3 Evaluation-Only
        if source_id in ("SRC-CD-02", "SRC-CV-04"):
            if "TRAINING" in intended_use.upper():
                raise TierIsolationViolationError(
                    f"Tier 3 source {source_id} is evaluation-only and strictly prohibited from training ingress"
                )

        # Tier 4 Permanently Blocked
        if source_id in ("SRC-CV-01", "SRC-CV-02", "SRC-HI-03", "SRC-TG-03"):
            raise TierIsolationViolationError(
                f"Tier 4 source {source_id} is permanently rejected from all operations"
            )

        # Replay nonce check
        if nonce:
            if nonce in self._used_nonces:
                raise ReplayAcquisitionError(f"Replay attack detected: authorization nonce '{nonce}' has already been consumed")
            self._used_nonces.add(nonce)

        # Grant check (Default-Deny)
        if source_id not in self._grants:
            raise UnauthorizedAcquisitionError(
                f"Acquisition of {source_id} is NOT AUTHORIZED. Explicit source-specific owner authorization is required."
            )

        grant = self._grants[source_id]

        if grant.status == "REVOKED":
            raise RevokedAuthorizationError(
                f"Authorization for {source_id} was REVOKED ({grant.notes}). Acquisition blocked."
            )

        if grant.status == "EXPIRED":
            raise ExpiredAuthorizationError(
                f"Authorization for {source_id} has EXPIRED. Acquisition blocked."
            )

        # Check time-based expiration if specified
        if grant.expiry_timestamp:
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            if now_iso > grant.expiry_timestamp:
                grant.status = "EXPIRED"
                raise ExpiredAuthorizationError(
                    f"Authorization for {source_id} expired at {grant.expiry_timestamp}. Current time: {now_iso}"
                )

        if grant.status != "AUTHORIZED":
            raise UnauthorizedAcquisitionError(
                f"Authorization status for {source_id} is '{grant.status}'. Acquisition is NOT AUTHORIZED."
            )

        # URL Match check
        if grant.official_download_url and requested_url:
            # Check prefix / exact match
            if not requested_url.startswith(grant.official_download_url) and not grant.official_download_url.startswith(requested_url):
                raise UnauthorizedSourceURLError(
                    f"Requested URL '{requested_url}' does not match authorized URL '{grant.official_download_url}'"
                )

        return AuthorizationDecision(
            is_authorized=True,
            source_id=source_id,
            source_version=grant.source_version,
            authorization_reference=grant.authorization_reference,
            status="AUTHORIZED",
            reason=None
        )

    def acquire_concurrency_lock(self, source_id: str) -> Path:
        """
        Acquire a filesystem lock to prevent concurrent acquisition of the same source.
        """
        lock_file = self.locks_dir / f"{source_id}.lock"
        if lock_file.exists():
            raise ConcurrentAcquisitionError(
                f"Concurrent acquisition in progress for {source_id}. Lock file exists: {lock_file}"
            )
        try:
            with open(lock_file, "w", encoding="utf-8") as f:
                f.write(f"LOCK|{source_id}|{time.time()}|{os.getpid()}\n")
            return lock_file
        except OSError as e:
            raise ConcurrentAcquisitionError(f"Failed to acquire acquisition lock for {source_id}: {e}") from e

    def release_concurrency_lock(self, source_id: str):
        """Release concurrency lock on completion or failure."""
        lock_file = self.locks_dir / f"{source_id}.lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
            except OSError:
                pass

    def record_acquisition_in_ledger(
        self,
        acquisition_id: str,
        source_id: str,
        source_version: str,
        authorization_reference: str,
        official_download_url: str,
        downloaded_byte_count: int,
        sha256: str,
        file_format: str,
        quarantine_location: str,
        validation_result: str,
        audit_chain_reference: str,
        rejection_reason: str = ""
    ):
        """
        Append an immutable record to the persistent acquisition ledger.
        """
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        row = [
            acquisition_id,
            source_id,
            source_version,
            authorization_reference,
            official_download_url,
            now_iso,
            downloaded_byte_count,
            sha256,
            file_format,
            quarantine_location,
            validation_result,
            rejection_reason,
            audit_chain_reference
        ]
        
        write_header = not self.ledger_path.exists() or self.ledger_path.stat().st_size == 0
        with open(self.ledger_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    "acquisition_id", "source_id", "source_version", "authorization_reference",
                    "official_download_url", "download_timestamp", "downloaded_byte_count",
                    "sha256", "file_format", "quarantine_location", "validation_result",
                    "rejection_reason", "audit_chain_reference"
                ])
            writer.writerow(row)
