#!/usr/bin/env python3
"""IGRIS Human Review Intake and Cryptographic Verification Engine.

Milestone: 3C.10 â€” Human Review Intake & Cryptographic Approval Verification
Module: scripts/review_intake_verifier.py

Enforces cryptographic integrity, key validation, schema compliance,
four-role quorum resolution, and append-only audit trail logging for
IGRIS dataset governance.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

HEX_64_REGEX = re.compile(r"^[0-9a-fA-F]{64}$")
SUBMISSION_ID_REGEX = re.compile(r"^SUB-[A-Z0-9]{8,16}$")
KEY_ID_REGEX = re.compile(r"^KEY-[A-Z0-9_\-]{6,32}$")
SOURCE_ID_REGEX = re.compile(r"^SRC-[A-Z]{2}-[0-9]{2}$")


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


class ReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class QuorumState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    BLOCKED_REJECTED = "BLOCKED_REJECTED"
    BLOCKED_CHANGES_REQUESTED = "BLOCKED_CHANGES_REQUESTED"


class KeyAlgorithm(str, Enum):
    ED25519 = "Ed25519"
    HMAC_SHA256 = "HMAC-SHA256"


@dataclass
class EvidenceReference:
    reference_type: str
    reference_uri: str
    sha256: str


@dataclass
class KeyRecord:
    key_id: str
    role: SignOffRole
    secret_key: str
    algorithm: str = KeyAlgorithm.HMAC_SHA256.value
    public_key_hex: Optional[str] = None
    reviewer_id: Optional[str] = None
    is_revoked: bool = False
    revocation_reason: Optional[str] = None
    created_at: str = "2026-11-17T00:00:00Z"
    expires_at: str = "2027-11-17T00:00:00Z"


class ReplayCache:
    """Maintains an indexed cache of processed submission IDs to defeat replay attacks."""

    def __init__(self, cache_path: Optional[Union[str, Path]] = None) -> None:
        self.cache_path = Path(cache_path) if cache_path else None
        self.seen_ids: Set[str] = set()
        self._load()

    def _load(self) -> None:
        if self.cache_path and self.cache_path.is_file():
            try:
                data = json.loads(self.cache_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.seen_ids.update(data)
            except Exception:
                pass

    def has_seen(self, submission_id: str) -> bool:
        return submission_id in self.seen_ids

    def record(self, submission_id: str) -> None:
        self.seen_ids.add(submission_id)
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(sorted(list(self.seen_ids)), indent=2), encoding="utf-8")


class KeyRegistry:
    """Manages authorized public/verification keys for governance roles."""

    def __init__(self) -> None:
        self._keys: Dict[str, KeyRecord] = {}

    def register_key(self, record: KeyRecord) -> None:
        self._keys[record.key_id] = record

    def revoke_key(self, key_id: str, reason: str) -> None:
        if key_id in self._keys:
            self._keys[key_id].is_revoked = True
            self._keys[key_id].revocation_reason = reason

    def get_key(self, key_id: str) -> Optional[KeyRecord]:
        return self._keys.get(key_id)

    def is_valid_key(
        self,
        key_id: str,
        declared_role: SignOffRole,
        reference_time: Optional[datetime] = None,
    ) -> Tuple[bool, Optional[str]]:
        record = self.get_key(key_id)
        if not record:
            return False, f"Key '{key_id}' is not recognized in governance key registry"

        if record.is_revoked:
            return False, f"Key '{key_id}' has been revoked: {record.revocation_reason}"

        if record.role != declared_role:
            return False, f"Key '{key_id}' is bound to role '{record.role.value}', cannot sign as '{declared_role.value}'"

        now = reference_time or datetime.now(timezone.utc)
        try:
            exp_dt = datetime.fromisoformat(record.expires_at)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if now > exp_dt:
                return False, f"Key '{key_id}' expired on {record.expires_at}"
        except Exception as ex:
            return False, f"Invalid key expiration format: {ex}"

        return True, None


def canonical_json_bytes(data: Dict[str, Any]) -> bytes:
    """Serialize dictionary to deterministic, canonical JSON bytes (RFC 8785 style)."""
    # Exclude digital_signature itself when computing signature payload
    payload = {k: v for k, v in data.items() if k != "digital_signature"}
    raw_str = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw_str.encode("utf-8")


def compute_ed25519_signature(payload_bytes: bytes, private_key_hex_or_bytes: Union[str, bytes]) -> str:
    """Compute Ed25519 digital signature (RFC 8032) for canonical bytes."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    if isinstance(private_key_hex_or_bytes, str):
        raw = bytes.fromhex(private_key_hex_or_bytes)
    else:
        raw = private_key_hex_or_bytes
    priv = ed25519.Ed25519PrivateKey.from_private_bytes(raw)
    return priv.sign(payload_bytes).hex()


def verify_ed25519_signature(payload_bytes: bytes, signature_hex: str, public_key_hex_or_bytes: Union[str, bytes]) -> bool:
    """Verify Ed25519 digital signature in constant time against public key."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    try:
        if isinstance(public_key_hex_or_bytes, str):
            pub_raw = bytes.fromhex(public_key_hex_or_bytes)
        else:
            pub_raw = public_key_hex_or_bytes
        pub = ed25519.Ed25519PublicKey.from_public_bytes(pub_raw)
        sig_raw = bytes.fromhex(signature_hex)
        pub.verify(sig_raw, payload_bytes)
        return True
    except Exception:
        return False


def compute_signature(payload_bytes: bytes, secret_key: str) -> str:
    """Compute HMAC-SHA256 signature for canonical bytes using authorized secret."""
    return hmac.new(secret_key.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def verify_signature(
    payload_bytes: bytes,
    signature: str,
    secret_key: str,
    algorithm: Optional[str] = None,
    public_key_hex: Optional[str] = None,
) -> bool:
    """Verify digital signature. Supports both asymmetric Ed25519 and symmetric HMAC-SHA256."""
    target_algo = algorithm or ("Ed25519" if len(signature) == 128 else "HMAC-SHA256")
    if target_algo == KeyAlgorithm.ED25519.value or len(signature) == 128:
        pub = public_key_hex or secret_key
        if verify_ed25519_signature(payload_bytes, signature, pub):
            return True
        if target_algo == KeyAlgorithm.ED25519.value:
            return False
    expected = compute_signature(payload_bytes, secret_key)
    return hmac.compare_digest(expected.lower(), signature.lower())


@dataclass
class IntakeVerificationResult:
    is_valid: bool
    submission_id: str
    errors: List[str] = field(default_factory=list)
    role: Optional[SignOffRole] = None
    decision: Optional[ReviewDecision] = None
    source_ids: List[str] = field(default_factory=list)
    document_sha256: Optional[str] = None


class ReviewIntakeVerifier:
    """Validates human review intake submissions for schema, signature, and integrity."""

    def __init__(self, key_registry: KeyRegistry, replay_cache: Optional[ReplayCache] = None) -> None:
        self.key_registry = key_registry
        self.replay_cache = replay_cache

    def verify_submission(
        self,
        submission: Dict[str, Any],
        document_path: Optional[Union[str, Path]] = None,
        reference_time: Optional[datetime] = None,
    ) -> IntakeVerificationResult:
        errors: List[str] = []
        sub_id = submission.get("submission_id", "UNKNOWN")

        # 1. Check Submission ID
        if not SUBMISSION_ID_REGEX.match(sub_id):
            errors.append(f"Invalid submission_id format: '{sub_id}'")
        elif self.replay_cache is not None and self.replay_cache.has_seen(sub_id):
            errors.append(f"Replay attack detected: submission_id '{sub_id}' has already been processed")

        # 2. Check Role
        role_str = submission.get("role", "")
        role_enum: Optional[SignOffRole] = None
        try:
            role_enum = SignOffRole(role_str)
        except ValueError:
            errors.append(f"Invalid or unrecognized governance role: '{role_str}'")

        # 3. Check Decision
        dec_str = submission.get("decision", "")
        dec_enum: Optional[ReviewDecision] = None
        try:
            dec_enum = ReviewDecision(dec_str)
        except ValueError:
            errors.append(f"Invalid or unrecognized review decision: '{dec_str}'")

        # 4. Check Source IDs
        source_ids = submission.get("source_ids_reviewed", [])
        if not isinstance(source_ids, list) or len(source_ids) == 0:
            errors.append("source_ids_reviewed must be a non-empty list of source IDs")
        else:
            for sid in source_ids:
                if not SOURCE_ID_REGEX.match(str(sid)):
                    errors.append(f"Malformed source ID: '{sid}'")

        # 5. Check Document SHA256 format
        doc_hash = submission.get("document_sha256", "")
        if not HEX_64_REGEX.match(doc_hash):
            errors.append(f"Invalid document_sha256 format: '{doc_hash}'")

        # 6. Verify Document Hash on Disk if document provided
        if document_path is not None:
            doc_p = Path(document_path)
            if not doc_p.is_file():
                errors.append(f"Audited document path does not exist on disk: {doc_p}")
            else:
                computed_hash = hashlib.sha256(doc_p.read_bytes()).hexdigest()
                if computed_hash.lower() != doc_hash.lower():
                    errors.append(
                        f"Document SHA256 mismatch: on disk='{computed_hash}', submission claims='{doc_hash}'"
                    )

        # 7. Check Timestamps and Expiration
        now = reference_time or datetime.now(timezone.utc)
        ts_str = submission.get("timestamp", "")
        exp_str = submission.get("expiry_date", "")

        try:
            exp_dt = datetime.fromisoformat(exp_str)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if now > exp_dt:
                errors.append(f"Approval submission expired on {exp_str} (current time: {now.isoformat()})")
        except Exception as ex:
            errors.append(f"Invalid expiry_date format '{exp_str}': {ex}")

        # 8. Check Public Key & Signature
        key_id = submission.get("public_key_id", "")
        sig = submission.get("digital_signature", "")

        if not sig:
            errors.append("Missing digital signature")
        elif not re.match(r"^[0-9a-fA-F]{64,128}$", sig):
            errors.append(f"Invalid digital signature format: '{sig}'")

        if role_enum is not None:
            key_valid, key_err = self.key_registry.is_valid_key(key_id, role_enum, reference_time=now)
            if not key_valid:
                errors.append(f"Key validation failed: {key_err}")
            else:
                key_rec = self.key_registry.get_key(key_id)
                if key_rec and sig:
                    payload_bytes = canonical_json_bytes(submission)
                    if not verify_signature(
                        payload_bytes,
                        sig,
                        key_rec.secret_key,
                        algorithm=getattr(key_rec, "algorithm", "HMAC-SHA256"),
                        public_key_hex=getattr(key_rec, "public_key_hex", None),
                    ):
                        errors.append("Cryptographic signature verification failed: signature does not match canonical payload")

        is_valid = (len(errors) == 0)
        if is_valid and self.replay_cache is not None:
            self.replay_cache.record(sub_id)

        return IntakeVerificationResult(
            is_valid=is_valid,
            submission_id=sub_id,
            errors=errors,
            role=role_enum,
            decision=dec_enum,
            source_ids=source_ids,
            document_sha256=doc_hash,
        )


class QuorumEngine:
    """Evaluates multi-signature submissions against the four-role quorum mandate."""

    @staticmethod
    def evaluate_source_consensus(
        source_id: str,
        verified_submissions: List[IntakeVerificationResult],
    ) -> Tuple[QuorumState, List[str]]:
        reasons: List[str] = []
        relevant_subs = [
            sub for sub in verified_submissions
            if sub.is_valid and source_id in sub.source_ids and sub.role is not None
        ]

        # Check for role duplicates
        roles_present: List[SignOffRole] = []
        for s in relevant_subs:
            assert s.role is not None
            if s.role in roles_present:
                reasons.append(f"Duplicate submission detected for role '{s.role.value}' on {source_id}")
            roles_present.append(s.role)

        unique_roles = set(roles_present)
        missing_roles = REQUIRED_ROLES - unique_roles

        # Check for conflicting or blocking decisions
        has_reject = any(s.decision == ReviewDecision.REJECT for s in relevant_subs)
        has_changes = any(s.decision == ReviewDecision.REQUEST_CHANGES for s in relevant_subs)
        has_approve = any(s.decision == ReviewDecision.APPROVE for s in relevant_subs)

        if has_reject:
            reasons.append(f"Source {source_id} received explicit REJECT decision from at least one reviewer")
            return QuorumState.BLOCKED_REJECTED, reasons

        if has_changes:
            reasons.append(f"Source {source_id} received REQUEST_CHANGES; approval is blocked pending changes")
            return QuorumState.BLOCKED_CHANGES_REQUESTED, reasons

        if missing_roles:
            reasons.append(f"Quorum incomplete: missing roles {[r.value for r in missing_roles]}")
            return QuorumState.PENDING, reasons

        if len(unique_roles) == 4 and all(s.decision == ReviewDecision.APPROVE for s in relevant_subs):
            reasons.append(f"Source {source_id} achieved unanimous 4-of-4 approval consensus")
            return QuorumState.APPROVED, reasons

        reasons.append(f"Source {source_id} quorum state indeterminate; defaulting to PENDING")
        return QuorumState.PENDING, reasons


@dataclass
class AuditRecord:
    audit_id: int
    timestamp: str
    source_id: str
    gate_name: str
    previous_state: str
    new_state: str
    reviewer_identity: str
    role: str
    evidence_hash: str
    reason_for_decision: str
    parent_audit_hash: str
    record_hash: str = ""


class AuditTrailLogger:
    """Maintains an append-only, tamper-evident cryptographic hash chain of governance decisions."""

    GENESIS_HASH = "0" * 64

    def __init__(self, log_file_path: Union[str, Path]) -> None:
        self.log_file_path = Path(log_file_path)
        self.records: List[AuditRecord] = []
        self._load_existing_log()

    def _load_existing_log(self) -> None:
        if not self.log_file_path.exists():
            return
        with open(self.log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    rec = AuditRecord(**data)
                    self.records.append(rec)
                except Exception:
                    pass

    def get_latest_hash(self) -> str:
        if not self.records:
            return self.GENESIS_HASH
        return self.records[-1].record_hash

    def append_decision(
        self,
        source_id: str,
        gate_name: str,
        previous_state: str,
        new_state: str,
        reviewer_identity: str,
        role: str,
        evidence_hash: str,
        reason: str,
        timestamp: Optional[str] = None,
    ) -> AuditRecord:
        parent_hash = self.get_latest_hash()
        audit_id = len(self.records) + 1
        ts = timestamp or datetime.now(timezone.utc).isoformat()

        rec = AuditRecord(
            audit_id=audit_id,
            timestamp=ts,
            source_id=source_id,
            gate_name=gate_name,
            previous_state=previous_state,
            new_state=new_state,
            reviewer_identity=reviewer_identity,
            role=role,
            evidence_hash=evidence_hash,
            reason_for_decision=reason,
            parent_audit_hash=parent_hash,
        )

        # Compute tamper-evident record hash
        rec_data = asdict(rec)
        rec_data.pop("record_hash", None)
        raw_str = json.dumps(rec_data, sort_keys=True)
        rec.record_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        self.records.append(rec)

        # Append to disk
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(rec)) + "\n")

        return rec

    def verify_chain_integrity(self) -> Tuple[bool, Optional[str]]:
        prev_hash = self.GENESIS_HASH
        for i, rec in enumerate(self.records):
            if rec.parent_audit_hash != prev_hash:
                return False, f"Broken chain link at audit_id {rec.audit_id}: parent hash '{rec.parent_audit_hash}' != previous '{prev_hash}'"

            rec_data = asdict(rec)
            recorded_hash = rec_data.pop("record_hash")
            raw_str = json.dumps(rec_data, sort_keys=True)
            computed_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

            if computed_hash != recorded_hash:
                return False, f"Tampered record at audit_id {rec.audit_id}: computed '{computed_hash}' != recorded '{recorded_hash}'"

            prev_hash = recorded_hash

        return True, None
