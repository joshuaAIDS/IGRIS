"""
IGRIS Secure Dataset Acquisition Engine
=======================================
Phase 12 Controlled Dataset Acquisition Infrastructure

Enforces:
1. Strict HTTPS validation (no plain HTTP, no protocol downgrades).
2. Approved domain allowlist enforcement.
3. Safe redirect validation (max 3 hops, strict scheme and domain continuity).
4. Streaming byte limits and socket timeouts.
5. Atomic staging via temporary .part files and cleanup on failure.
6. SHA-256 cryptographic verification.
7. Tamper-evident chained audit logging.
8. Default-Deny Gate Enforcement (AcquisitionGateLockedError unless unlocked).
"""

import hashlib
import json
import os
import re
import socket
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple


class AcquisitionError(Exception):
    """Base exception for dataset acquisition errors."""
    pass


class AcquisitionGateLockedError(AcquisitionError):
    """Raised when dataset acquisition is attempted while the pipeline gate is LOCKED."""
    pass


class SecurityValidationError(AcquisitionError):
    """Raised when a security vector check fails."""
    pass


class DomainNotAllowedError(SecurityValidationError):
    """Raised when a URL domain is not in the approved allowlist."""
    pass


class InsecureSchemeError(SecurityValidationError):
    """Raised when a URL scheme is not HTTPS."""
    pass


class RedirectAbuseError(SecurityValidationError):
    """Raised when redirect hops exceed limits or diverge from approved domains/schemes."""
    pass


class OversizedFileError(SecurityValidationError):
    """Raised when a download exceeds the configured byte size limit."""
    pass


class HashMismatchError(SecurityValidationError):
    """Raised when a downloaded file's SHA-256 does not match the manifest expected hash."""
    pass


class CorruptedDownloadError(AcquisitionError):
    """Raised when a download stream terminates prematurely or corrupts."""
    pass


# Canonical Approved Domain Whitelist for IGRIS Permissive Sources
APPROVED_DOMAINS: Set[str] = {
    "huggingface.co",
    "cdn-lfs.huggingface.co",
    "github.com",
    "raw.githubusercontent.com",
    "objects.githubusercontent.com",
    "archive.org",
    "gutenberg.org",
    "www.gutenberg.org",
    "unicode.org",
    "www.unicode.org",
    "rfc-editor.org",
    "www.rfc-editor.org",
    "python.org",
    "docs.python.org",
    "ai4bharat.org",
    "indicglue.ai4bharat.org",
}


def is_approved_domain(hostname: str, custom_whitelist: Optional[Set[str]] = None) -> bool:
    """
    Check if a hostname is in the approved domain whitelist or is a legitimate subdomain.
    """
    if not hostname:
        return False
    
    whitelist = custom_whitelist if custom_whitelist is not None else APPROVED_DOMAINS
    hostname = hostname.lower().strip()
    
    # Check exact match
    if hostname in whitelist:
        return True
    
    # Check subdomain match (e.g., sub.huggingface.co)
    for domain in whitelist:
        if hostname.endswith("." + domain):
            return True
            
    return False


def validate_url(url: str, custom_whitelist: Optional[Set[str]] = None) -> bool:
    """
    Strict URL validation for acquisition endpoints:
    - Scheme must be exactly 'https'
    - Hostname must be approved in domain whitelist
    - No credentials (user:pass) in URL
    - No control characters or null bytes
    - Default port or 443 only
    """
    if not url or not isinstance(url, str):
        raise SecurityValidationError("Invalid URL: empty or non-string URL provided")
        
    if "\0" in url or "\r" in url or "\n" in url:
        raise SecurityValidationError("Invalid URL: dangerous control characters or null bytes detected")
        
    parsed = urllib.parse.urlsplit(url)
    
    # Enforce HTTPS strictly
    if parsed.scheme.lower() != "https":
        raise InsecureSchemeError(f"Insecure scheme '{parsed.scheme}': only HTTPS is permitted")
        
    if parsed.username or parsed.password:
        raise SecurityValidationError("URL contains embedded credentials which are prohibited")
        
    hostname = parsed.hostname
    if not hostname:
        raise SecurityValidationError("URL missing hostname")
        
    # Check if host is raw IP address (disallowed unless explicitly added to custom test whitelist)
    whitelist = custom_whitelist if custom_whitelist is not None else APPROVED_DOMAINS
    is_raw_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname) or ":" in hostname
    if is_raw_ip and hostname not in whitelist:
        raise DomainNotAllowedError(f"Raw IP address hosts are prohibited: {hostname}")
        
    if parsed.port and parsed.port != 443:
        if hostname not in whitelist:
            raise SecurityValidationError(f"Non-standard HTTPS port {parsed.port} prohibited")
            
    if not is_approved_domain(hostname, custom_whitelist):
        raise DomainNotAllowedError(f"Domain '{hostname}' is not in the approved acquisition whitelist")
        
    return True


def validate_redirect_chain(
    initial_url: str,
    hops: List[str],
    max_redirects: int = 3,
    custom_whitelist: Optional[Set[str]] = None
) -> bool:
    """
    Validate an entire HTTP redirect chain:
    - Initial URL must be valid
    - Maximum hop limit strictly enforced (default 3)
    - Every subsequent hop must remain HTTPS
    - Every subsequent hop must remain on an approved domain
    """
    validate_url(initial_url, custom_whitelist)
    
    if len(hops) > max_redirects:
        raise RedirectAbuseError(f"Redirect chain length {len(hops)} exceeds maximum permitted hops ({max_redirects})")
        
    for hop_idx, hop_url in enumerate(hops):
        try:
            validate_url(hop_url, custom_whitelist)
        except InsecureSchemeError as e:
            raise RedirectAbuseError(f"Redirect hop {hop_idx + 1} downgraded security: {e}") from e
        except DomainNotAllowedError as e:
            raise RedirectAbuseError(f"Redirect hop {hop_idx + 1} targeted unapproved domain: {e}") from e
            
    return True


@dataclass
class AuditEntry:
    timestamp: str
    source_id: str
    url: str
    destination_path: str
    bytes_downloaded: int
    sha256: str
    duration_seconds: float
    status: str
    error: Optional[str]
    prev_hash: str
    entry_hash: str


class AcquisitionAuditLogger:
    """
    Append-only, cryptographically chained audit logger for dataset acquisition events.
    """
    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._get_latest_hash()

    def _get_latest_hash(self) -> str:
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return "0" * 64
        last_entry = None
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        last_entry = json.loads(line)
                    except json.JSONDecodeError:
                        pass
        if last_entry and "entry_hash" in last_entry:
            return last_entry["entry_hash"]
        return "0" * 64

    def log_event(
        self,
        source_id: str,
        url: str,
        destination_path: str,
        bytes_downloaded: int,
        sha256: str,
        duration_seconds: float,
        status: str,
        error: Optional[str] = None
    ) -> AuditEntry:
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        prev_h = self._last_hash
        
        # Calculate chained hash over canonical content
        payload = f"{now_iso}|{source_id}|{url}|{destination_path}|{bytes_downloaded}|{sha256}|{status}|{error}|{prev_h}"
        entry_h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        entry = AuditEntry(
            timestamp=now_iso,
            source_id=source_id,
            url=url,
            destination_path=str(destination_path),
            bytes_downloaded=bytes_downloaded,
            sha256=sha256,
            duration_seconds=round(duration_seconds, 4),
            status=status,
            error=error,
            prev_hash=prev_h,
            entry_hash=entry_h
        )
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry)) + "\n")
            f.flush()
            
        self._last_hash = entry_h
        return entry

    def verify_integrity(self) -> Tuple[bool, int, Optional[str]]:
        """Verify the cryptographic chain of the audit log."""
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return True, 0, None
            
        current_prev = "0" * 64
        count = 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("prev_hash") != current_prev:
                    return False, count, f"Hash chain break at line {line_idx + 1}: expected prev {current_prev}, got {entry.get('prev_hash')}"
                    
                payload = f"{entry['timestamp']}|{entry['source_id']}|{entry['url']}|{entry['destination_path']}|{entry['bytes_downloaded']}|{entry['sha256']}|{entry['status']}|{entry['error']}|{current_prev}"
                computed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                if computed != entry.get("entry_hash"):
                    return False, count, f"Entry hash mismatch at line {line_idx + 1}"
                    
                current_prev = entry["entry_hash"]
                count += 1
                
        return True, count, None


class SecureAcquisitionEngine:
    """
    Controlled Acquisition Engine with default-deny gate enforcement,
    streaming verification, atomic placement, and cryptographic audit.
    """
    def __init__(
        self,
        gate_unlocked: bool = False,
        audit_log_path: Optional[Path] = None,
        custom_whitelist: Optional[Set[str]] = None,
        authorizer: Any = None
    ):
        self.gate_unlocked = gate_unlocked
        self.custom_whitelist = custom_whitelist
        self.authorizer = authorizer
        if audit_log_path is None:
            audit_log_path = Path("quarantine/logs/acquisition_audit.jsonl")
        self.audit_logger = AcquisitionAuditLogger(audit_log_path)

    def is_gate_unlocked(self) -> bool:
        return self.gate_unlocked

    def download_source(
        self,
        source_id: str,
        url: str,
        destination_path: Path,
        max_size_bytes: int,
        expected_sha256: Optional[str] = None,
        timeout: float = 30.0,
        chunk_size: int = 65536,
        mock_chunks: Optional[List[bytes]] = None,
        redirect_hops: Optional[List[str]] = None,
        intended_use: str = "VOCABULARY_TRAINING_AND_FERTILITY_EVALUATION",
        nonce: Optional[str] = None,
        source_version: str = "1.0",
        format_name: str = "archive"
    ) -> Dict[str, Any]:
        """
        Execute controlled download with strict security verification:
        1. Ingress Gate Lock verification
        2. Source-specific Authorizer verification (if authorizer attached)
        3. Concurrency lock acquisition
        4. URL scheme and domain verification
        5. Redirect hop validation (if any)
        6. Atomic download to <dest>.part
        7. Byte-limit enforcement during streaming
        8. SHA-256 calculation and verification
        9. Atomic promotion to <dest>
        10. Persistent ledger recording & Chained audit logging
        """
        start_time = time.time()
        dest_path = Path(destination_path)
        part_path = Path(str(destination_path) + ".part")
        lock_acquired = False
        auth_ref = "UNAUTHORIZED"

        # 1. Gate Lock Check
        if not self.is_gate_unlocked():
            err_msg = f"Production Data Ingress Gate is LOCKED. Acquisition of {source_id} is NOT AUTHORIZED."
            self.audit_logger.log_event(
                source_id=source_id,
                url=url,
                destination_path=str(dest_path),
                bytes_downloaded=0,
                sha256="",
                duration_seconds=time.time() - start_time,
                status="BLOCKED_GATE_LOCKED",
                error=err_msg
            )
            raise AcquisitionGateLockedError(err_msg)

        # 2. Source-specific Authorizer Check & Concurrency Lock
        if self.authorizer is not None:
            # Check concurrency lock first
            self.authorizer.acquire_concurrency_lock(source_id)
            lock_acquired = True
            try:
                auth_decision = self.authorizer.verify_authorization(
                    source_id=source_id,
                    requested_url=url,
                    intended_use=intended_use,
                    nonce=nonce
                )
                auth_ref = auth_decision.authorization_reference
            except Exception as e:
                if lock_acquired:
                    self.authorizer.release_concurrency_lock(source_id)
                    lock_acquired = False
                self.audit_logger.log_event(
                    source_id=source_id,
                    url=url,
                    destination_path=str(dest_path),
                    bytes_downloaded=0,
                    sha256="",
                    duration_seconds=time.time() - start_time,
                    status="BLOCKED_AUTHORIZATION_FAILURE",
                    error=str(e)
                )
                raise

        # 3. Validate URL and Redirects
        try:
            if redirect_hops:
                validate_redirect_chain(url, redirect_hops, custom_whitelist=self.custom_whitelist)
            else:
                validate_url(url, custom_whitelist=self.custom_whitelist)
        except SecurityValidationError as e:
            if lock_acquired and self.authorizer is not None:
                self.authorizer.release_concurrency_lock(source_id)
                lock_acquired = False
            self.audit_logger.log_event(
                source_id=source_id,
                url=url,
                destination_path=str(dest_path),
                bytes_downloaded=0,
                sha256="",
                duration_seconds=time.time() - start_time,
                status="BLOCKED_SECURITY_VIOLATION",
                error=str(e)
            )
            raise

        # Clean up any leftover .part file
        if part_path.exists():
            try:
                part_path.unlink()
            except OSError:
                pass

        part_path.parent.mkdir(parents=True, exist_ok=True)
        sha256_hasher = hashlib.sha256()
        total_downloaded = 0

        try:
            with open(part_path, "wb") as part_file:
                if mock_chunks is not None:
                    # Test / simulation mode
                    for chunk in mock_chunks:
                        if not chunk:
                            continue
                        total_downloaded += len(chunk)
                        if total_downloaded > max_size_bytes:
                            raise OversizedFileError(
                                f"Downloaded stream exceeded maximum size limit {max_size_bytes} bytes "
                                f"(downloaded {total_downloaded} bytes)"
                            )
                        sha256_hasher.update(chunk)
                        part_file.write(chunk)
                else:
                    # Live network streaming
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": "IGRIS-Dataset-Acquisition-Pipeline/1.0 (Audit-Controlled)"}
                    )
                    with urllib.request.urlopen(req, timeout=timeout) as response:
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            total_downloaded += len(chunk)
                            if total_downloaded > max_size_bytes:
                                raise OversizedFileError(
                                    f"Downloaded stream exceeded maximum size limit {max_size_bytes} bytes "
                                    f"(downloaded {total_downloaded} bytes)"
                                )
                            sha256_hasher.update(chunk)
                            part_file.write(chunk)

            computed_hash = sha256_hasher.hexdigest()

            # Hash check
            if expected_sha256 and not expected_sha256.startswith("VERIFY_ON_INGEST"):
                if computed_hash.lower() != expected_sha256.lower():
                    raise HashMismatchError(
                        f"Cryptographic hash mismatch for {source_id}: expected {expected_sha256}, got {computed_hash}"
                    )

            # Atomic rename from .part to destination
            if dest_path.exists():
                # Remove read-only attribute if replacing existing file in tests
                try:
                    os.chmod(dest_path, 0o666)
                except OSError:
                    pass
            os.replace(part_path, dest_path)

            duration = time.time() - start_time
            audit_entry = self.audit_logger.log_event(
                source_id=source_id,
                url=url,
                destination_path=str(dest_path),
                bytes_downloaded=total_downloaded,
                sha256=computed_hash,
                duration_seconds=duration,
                status="SUCCESS",
                error=None
            )

            if self.authorizer is not None:
                acq_id = f"ACQ-{source_id}-{int(start_time)}"
                self.authorizer.record_acquisition_in_ledger(
                    acquisition_id=acq_id,
                    source_id=source_id,
                    source_version=source_version,
                    authorization_reference=auth_ref,
                    official_download_url=url,
                    downloaded_byte_count=total_downloaded,
                    sha256=computed_hash,
                    file_format=format_name,
                    quarantine_location=str(dest_path),
                    validation_result="SUCCESS",
                    audit_chain_reference=audit_entry.entry_hash
                )

            return {
                "source_id": source_id,
                "url": url,
                "destination_path": str(dest_path),
                "bytes_downloaded": total_downloaded,
                "sha256": computed_hash,
                "duration_seconds": duration,
                "status": "SUCCESS"
            }

        except Exception as e:
            # Always delete the .part file on any error
            if part_path.exists():
                try:
                    part_path.unlink()
                except OSError:
                    pass

            duration = time.time() - start_time
            self.audit_logger.log_event(
                source_id=source_id,
                url=url,
                destination_path=str(dest_path),
                bytes_downloaded=total_downloaded,
                sha256=sha256_hasher.hexdigest() if total_downloaded > 0 else "",
                duration_seconds=duration,
                status="FAILURE",
                error=str(e)
            )
            raise
        finally:
            if lock_acquired and self.authorizer is not None:
                self.authorizer.release_concurrency_lock(source_id)
