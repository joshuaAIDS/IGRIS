"""
IGRIS Phase 13 Controlled Acquisition Security Test Suite
=========================================================
Tests for Source-Specific Owner Authorization, Controlled Acquisition,
and Quarantine Safety Pipeline.

Covers all 24 required security vectors:
1. Unauthorized acquisition rejection
2. Missing owner approval
3. Revoked authorization
4. Expired authorization
5. Unauthorized source URL
6. Unauthorized domain
7. HTTP downgrade
8. Redirect abuse
9. Oversized downloads
10. Interrupted downloads
11. Hash mismatch
12. Corrupted archives
13. Archive traversal / Zip-Slip
14. Executable-file rejection
15. Invalid UTF-8
16. Unicode normalization
17. PII screening
18. Duplicate acquisition
19. Replay attacks
20. Audit-chain tampering
21. Concurrent acquisition attempts
22. Quarantine integrity
23. Recovery after process interruption
24. Tier isolation
"""

import io
import json
import os
import shutil
import stat
import sys
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path
import pytest

# Ensure scripts directory is on sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from secure_acquisition_engine import (
    AcquisitionAuditLogger,
    AcquisitionGateLockedError,
    DomainNotAllowedError,
    HashMismatchError,
    InsecureSchemeError,
    OversizedFileError,
    RedirectAbuseError,
    SecureAcquisitionEngine,
    SecurityValidationError,
    validate_redirect_chain,
    validate_url,
)

from source_acquisition_authorizer import (
    ConcurrentAcquisitionError,
    ExpiredAuthorizationError,
    ReplayAcquisitionError,
    RevokedAuthorizationError,
    SourceAcquisitionAuthorizer,
    TierIsolationViolationError,
    UnauthorizedAcquisitionError,
    UnauthorizedSourceURLError,
)

from ingress_safety_pipeline import (
    DuplicateContentError,
    MaliciousContentError,
    PIISummary,
    QuarantinePipeline,
    QuarantineValidationError,
    UnicodeEncodingError,
    ValidationReport,
    ZipSlipTraversalError,
    make_file_immutable,
    safe_extract_tar,
    safe_extract_zip,
    scan_pii_in_text,
    validate_magic_bytes,
    validate_utf8_losslessness,
)


# ---------------------------------------------------------------------------
# Vector 1 & 2: Unauthorized Acquisition & Missing Owner Approval
# ---------------------------------------------------------------------------
def test_unauthorized_acquisition_rejection(tmp_path):
    """Verify that an ungranted source acquisition defaults to DENY."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")
    engine = SecureAcquisitionEngine(gate_unlocked=True, authorizer=auth, audit_log_path=tmp_path / "audit.jsonl")

    with pytest.raises(UnauthorizedAcquisitionError, match="Explicit source-specific owner authorization is required"):
        engine.download_source(
            source_id="SRC-TM-01",
            url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
            destination_path=tmp_path / "ta.txt.tar.gz",
            max_size_bytes=1000000,
            mock_chunks=[b"Valid sample payload"]
        )


def test_missing_owner_approval_default_deny(tmp_path):
    """Verify that any query for a source without owner approval returns an error."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")
    with pytest.raises(UnauthorizedAcquisitionError):
        auth.verify_authorization("SRC-EN-01", "https://www.gutenberg.org/robot/harvest")


# ---------------------------------------------------------------------------
# Vector 3: Revoked Authorization
# ---------------------------------------------------------------------------
def test_revoked_authorization_rejection(tmp_path):
    """Verify that a revoked authorization immediately blocks acquisition."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")
    auth.grant_source_authorization(
        source_id="SRC-TM-01",
        source_version="v2.0",
        official_download_url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
        intended_use="VOCABULARY_TRAINING_AND_FERTILITY_EVALUATION",
        authorization_reference="AUTH-OWNER-SRC-TM-01-20261118"
    )

    # Revoke authorization
    auth.revoke_source_authorization("SRC-TM-01", reason="Security review pause")

    engine = SecureAcquisitionEngine(gate_unlocked=True, authorizer=auth, audit_log_path=tmp_path / "audit.jsonl")
    with pytest.raises(RevokedAuthorizationError, match="REVOKED"):
        engine.download_source(
            source_id="SRC-TM-01",
            url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
            destination_path=tmp_path / "ta.txt.tar.gz",
            max_size_bytes=1000000,
            mock_chunks=[b"data"]
        )


# ---------------------------------------------------------------------------
# Vector 4: Expired Authorization
# ---------------------------------------------------------------------------
def test_expired_authorization_rejection(tmp_path):
    """Verify that an expired authorization record is rejected."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")
    # Grant with expiry in the past
    auth.grant_source_authorization(
        source_id="SRC-HI-01",
        source_version="v2.0",
        official_download_url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/hi.txt.tar.gz",
        intended_use="VOCABULARY_TRAINING_AND_FERTILITY_EVALUATION",
        authorization_reference="AUTH-OWNER-SRC-HI-01",
        expiry_timestamp="2020-01-01T00:00:00Z"
    )

    engine = SecureAcquisitionEngine(gate_unlocked=True, authorizer=auth, audit_log_path=tmp_path / "audit.jsonl")
    with pytest.raises(ExpiredAuthorizationError, match="EXPIRED|expired"):
        engine.download_source(
            source_id="SRC-HI-01",
            url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/hi.txt.tar.gz",
            destination_path=tmp_path / "hi.txt.tar.gz",
            max_size_bytes=1000000,
            mock_chunks=[b"data"]
        )


# ---------------------------------------------------------------------------
# Vector 5: Unauthorized Source URL
# ---------------------------------------------------------------------------
def test_unauthorized_source_url_rejection(tmp_path):
    """Verify that downloading from a URL differing from the authorized URL is blocked."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")
    auth.grant_source_authorization(
        source_id="SRC-TM-01",
        source_version="v2.0",
        official_download_url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
        intended_use="VOCABULARY_TRAINING_AND_FERTILITY_EVALUATION",
        authorization_reference="AUTH-OWNER-SRC-TM-01"
    )

    engine = SecureAcquisitionEngine(gate_unlocked=True, authorizer=auth, audit_log_path=tmp_path / "audit.jsonl")
    with pytest.raises(UnauthorizedSourceURLError, match="does not match authorized URL"):
        engine.download_source(
            source_id="SRC-TM-01",
            url="https://raw.githubusercontent.com/AttackerRepo/IndicCorp/main/downloads/ta.txt.tar.gz",
            destination_path=tmp_path / "ta.txt.tar.gz",
            max_size_bytes=1000000,
            mock_chunks=[b"data"]
        )


# ---------------------------------------------------------------------------
# Vector 6: Unauthorized Domain
# ---------------------------------------------------------------------------
def test_unauthorized_domain_rejection(tmp_path):
    """Verify that domains outside APPROVED_DOMAINS are rejected."""
    with pytest.raises(DomainNotAllowedError):
        validate_url("https://unapproved-mirror.com/data.tar.gz")


# ---------------------------------------------------------------------------
# Vector 7: HTTP Downgrade
# ---------------------------------------------------------------------------
def test_http_downgrade_rejection(tmp_path):
    """Verify that plain HTTP requests are blocked."""
    with pytest.raises(InsecureSchemeError):
        validate_url("http://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/hi.txt")


# ---------------------------------------------------------------------------
# Vector 8: Redirect Abuse
# ---------------------------------------------------------------------------
def test_redirect_abuse_rejection(tmp_path):
    """Verify that redirects targeting unapproved domains or exceeding 3 hops fail."""
    hops = [
        "https://huggingface.co/hop1",
        "https://unapproved-cdn.com/payload.bin"
    ]
    with pytest.raises(RedirectAbuseError, match="targeted unapproved domain"):
        validate_redirect_chain("https://huggingface.co/initial", hops)


# ---------------------------------------------------------------------------
# Vector 9: Oversized Downloads Cutoff
# ---------------------------------------------------------------------------
def test_oversized_download_cutoff(tmp_path):
    """Verify that streaming data exceeding byte limits terminates immediately and purges .part."""
    dest = tmp_path / "oversized.bin"
    engine = SecureAcquisitionEngine(gate_unlocked=True, audit_log_path=tmp_path / "audit.jsonl")

    chunks = [b"A" * 2000, b"B" * 2000, b"C" * 2000]  # 6000 bytes > 4000 limit
    with pytest.raises(OversizedFileError, match="exceeded maximum size limit"):
        engine.download_source(
            source_id="SRC-TEST-01",
            url="https://huggingface.co/test/large.bin",
            destination_path=dest,
            max_size_bytes=4000,
            mock_chunks=chunks
        )
    assert not dest.exists()
    assert not Path(str(dest) + ".part").exists()


# ---------------------------------------------------------------------------
# Vector 10: Interrupted Downloads Handling & Cleanup
# ---------------------------------------------------------------------------
def test_interrupted_downloads_cleanup(tmp_path):
    """Verify that an interrupted stream cleans up temporary files without residual artifacts."""
    dest = tmp_path / "interrupted.bin"
    engine = SecureAcquisitionEngine(gate_unlocked=True, audit_log_path=tmp_path / "audit.jsonl")

    class AbortedStream:
        def __iter__(self):
            yield b"First partial chunk"
            raise ConnectionAbortedError("Socket abruptly closed by host")

    with pytest.raises(ConnectionAbortedError):
        engine.download_source(
            source_id="SRC-TEST-02",
            url="https://huggingface.co/test/abort.bin",
            destination_path=dest,
            max_size_bytes=100000,
            mock_chunks=AbortedStream()
        )
    assert not dest.exists()
    assert not Path(str(dest) + ".part").exists()


# ---------------------------------------------------------------------------
# Vector 11: Hash Mismatch Rejection
# ---------------------------------------------------------------------------
def test_hash_mismatch_rejection(tmp_path):
    """Verify that unexpected content hash aborts promotion and removes .part file."""
    dest = tmp_path / "hash_fail.txt"
    engine = SecureAcquisitionEngine(gate_unlocked=True, audit_log_path=tmp_path / "audit.jsonl")

    with pytest.raises(HashMismatchError, match="Cryptographic hash mismatch"):
        engine.download_source(
            source_id="SRC-TEST-03",
            url="https://huggingface.co/test/hash.txt",
            destination_path=dest,
            max_size_bytes=10000,
            expected_sha256="ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            mock_chunks=[b"Valid text content but different hash"]
        )
    assert not dest.exists()
    assert not Path(str(dest) + ".part").exists()


# ---------------------------------------------------------------------------
# Vector 12: Corrupted Archive Rejection
# ---------------------------------------------------------------------------
def test_corrupted_archive_rejection(tmp_path):
    """Verify that a corrupted or truncated zip archive fails quarantine validation."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")
    corrupt_zip = tmp_path / "corrupt.zip"
    corrupt_zip.write_bytes(b"PK\x03\x04" + b"random corrupted garbage data without central directory")

    with pytest.raises((QuarantineValidationError, zipfile.BadZipFile)):
        pipe.process_incoming_file("SRC-TEST-04", corrupt_zip, is_archive=True)


# ---------------------------------------------------------------------------
# Vector 13: Archive Traversal / Zip-Slip Rejection
# ---------------------------------------------------------------------------
def test_archive_traversal_zip_slip_rejection(tmp_path):
    """Verify that an archive containing ../ path traversal is caught and rejected."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr("../../etc/passwd", b"root:x:0:0:root")
        zf.writestr("normal.txt", b"safe content")

    bad_zip = tmp_path / "traversal.zip"
    bad_zip.write_bytes(zip_buf.getvalue())

    with pytest.raises(ZipSlipTraversalError, match="Zip slip traversal"):
        pipe.process_incoming_file("SRC-TEST-05", bad_zip, is_archive=True)


# ---------------------------------------------------------------------------
# Vector 14: Executable File Rejection
# ---------------------------------------------------------------------------
def test_executable_file_rejection(tmp_path):
    """Verify that disguised executable files (ELF, PE, Mach-O) are rejected."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")
    elf_file = tmp_path / "disguised_dataset.txt"
    elf_file.write_bytes(b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 128)

    with pytest.raises(MaliciousContentError, match="Linux ELF Executable"):
        pipe.process_incoming_file("SRC-TEST-06", elf_file, is_archive=False)


# ---------------------------------------------------------------------------
# Vector 15: Invalid UTF-8 Rejection
# ---------------------------------------------------------------------------
def test_invalid_utf8_rejection(tmp_path):
    """Verify that non-UTF-8 bytes or U+FFFD replacement characters are rejected."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")

    # Invalid byte sequence
    bad_file = tmp_path / "bad_bytes.txt"
    bad_file.write_bytes(b"Line 1 text\n\x80\xFF invalid\nLine 3 text")
    with pytest.raises(UnicodeEncodingError, match="Invalid UTF-8 byte sequence"):
        pipe.process_incoming_file("SRC-TEST-07", bad_file, is_archive=False)

    # U+FFFD character
    fffd_file = tmp_path / "fffd_sample.txt"
    fffd_file.write_text("Text containing corrupted \ufffd character", encoding="utf-8")
    with pytest.raises(UnicodeEncodingError, match=r"Unicode replacement character U\+FFFD"):
        pipe.process_incoming_file("SRC-TEST-08", fffd_file, is_archive=False)


# ---------------------------------------------------------------------------
# Vector 16: Unicode Normalization Verification
# ---------------------------------------------------------------------------
def test_unicode_normalization_enforced(tmp_path):
    """Verify that non-NFC text is identified and recorded."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")
    nfd_text = "e\u0301"  # NFD decomposed 'é'
    nfd_file = tmp_path / "nfd_corpus.txt"
    nfd_file.write_text(nfd_text, encoding="utf-8")

    rep = pipe.process_incoming_file("SRC-TEST-09", nfd_file, is_archive=False)
    assert rep.status == "PASSED_QUARANTINE_VALIDATION"
    assert rep.nfc_normalized is False, "NFD text should be flagged as non-NFC"


# ---------------------------------------------------------------------------
# Vector 17: PII Screening
# ---------------------------------------------------------------------------
def test_pii_screening(tmp_path):
    """Verify that PII patterns (email, phone, SSN, Aadhaar, credit cards, IP) are detected."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")
    sample_text = """
    Contact user at test.user@example.com or calling +919876543210.
    US SSN is 123-45-6789 and Indian Aadhaar is 2345 6789 0123.
    Card number: 4111 1111 1111 1111 from IP 192.168.1.50.
    """
    pii_file = tmp_path / "pii_sample.txt"
    pii_file.write_text(sample_text, encoding="utf-8")

    rep = pipe.process_incoming_file("SRC-TEST-10", pii_file, is_archive=False)
    assert rep.pii_summary.email_count == 1
    assert rep.pii_summary.phone_count == 1
    assert rep.pii_summary.ssn_count == 1
    assert rep.pii_summary.aadhaar_count == 1
    assert rep.pii_summary.credit_card_count == 1
    assert rep.pii_summary.ip_count == 1
    # Sample credit cards must be redacted
    for c in rep.pii_summary.samples.get("credit_cards", []):
        assert c.startswith("XXXX-XXXX-XXXX-")


# ---------------------------------------------------------------------------
# Vector 18: Duplicate Acquisition Rejection
# ---------------------------------------------------------------------------
def test_duplicate_acquisition_rejection(tmp_path):
    """Verify that ingesting identical file content twice raises DuplicateContentError."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")

    file1 = tmp_path / "f1.txt"
    file1.write_text("Identical unique dataset text sample line 1", encoding="utf-8")

    rep1 = pipe.process_incoming_file("SRC-TEST-11", file1, is_archive=False)
    assert rep1.status == "PASSED_QUARANTINE_VALIDATION"

    file2 = tmp_path / "f2.txt"
    file2.write_text("Identical unique dataset text sample line 1", encoding="utf-8")

    with pytest.raises(DuplicateContentError, match="Duplicate archive detected"):
        pipe.process_incoming_file("SRC-TEST-12", file2, is_archive=False)


# ---------------------------------------------------------------------------
# Vector 19: Replay Attack Rejection
# ---------------------------------------------------------------------------
def test_replay_attack_rejection(tmp_path):
    """Verify that reusing the same authorization nonce is blocked."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")
    auth.grant_source_authorization(
        source_id="SRC-TM-01",
        source_version="v2.0",
        official_download_url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
        intended_use="VOCABULARY_TRAINING_AND_FERTILITY_EVALUATION",
        authorization_reference="AUTH-SRC-TM-01"
    )

    # First authorization check with nonce succeeds
    auth.verify_authorization(
        source_id="SRC-TM-01",
        requested_url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
        nonce="NONCE-12345"
    )

    # Second authorization check with the same nonce must fail as replay
    with pytest.raises(ReplayAcquisitionError, match="Replay attack detected"):
        auth.verify_authorization(
            source_id="SRC-TM-01",
            requested_url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
            nonce="NONCE-12345"
        )


# ---------------------------------------------------------------------------
# Vector 20: Audit-Chain Tampering Detection
# ---------------------------------------------------------------------------
def test_audit_chain_tampering_detection(tmp_path):
    """Verify that tampering with an audit log line invalidates the chain."""
    audit_file = tmp_path / "audit.jsonl"
    logger = AcquisitionAuditLogger(audit_file)

    logger.log_event("SRC-01", "https://huggingface.co/1", "dest1", 100, "h1", 0.1, "SUCCESS")
    logger.log_event("SRC-02", "https://huggingface.co/2", "dest2", 200, "h2", 0.2, "SUCCESS")

    ok, _, _ = logger.verify_integrity()
    assert ok is True

    # Tamper with the log file
    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    data = json.loads(lines[0])
    data["sha256"] = "tampered_hash_value"
    lines[0] = json.dumps(data) + "\n"
    with open(audit_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    ok_tampered, _, err = logger.verify_integrity()
    assert ok_tampered is False
    assert "mismatch" in err.lower() or "break" in err.lower()


# ---------------------------------------------------------------------------
# Vector 21: Concurrent Acquisition Attempts
# ---------------------------------------------------------------------------
def test_concurrent_acquisition_attempts_serialized(tmp_path):
    """Verify that concurrent acquisition requests on the same source are serialized/locked."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")
    auth.grant_source_authorization(
        source_id="SRC-TM-01",
        source_version="v2.0",
        official_download_url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
        intended_use="VOCABULARY_TRAINING_AND_FERTILITY_EVALUATION",
        authorization_reference="AUTH-SRC-TM-01"
    )

    # Acquire lock for SRC-TM-01
    auth.acquire_concurrency_lock("SRC-TM-01")

    # Second acquire should raise ConcurrentAcquisitionError
    with pytest.raises(ConcurrentAcquisitionError, match="Concurrent acquisition in progress"):
        auth.acquire_concurrency_lock("SRC-TM-01")

    # Releasing allows acquisition again
    auth.release_concurrency_lock("SRC-TM-01")
    auth.acquire_concurrency_lock("SRC-TM-01")
    auth.release_concurrency_lock("SRC-TM-01")


# ---------------------------------------------------------------------------
# Vector 22: Quarantine Integrity Preservation
# ---------------------------------------------------------------------------
def test_quarantine_integrity_preserved(tmp_path):
    """Verify that quarantined files receive read-only write-once permissions."""
    pipe = QuarantinePipeline(quarantine_root=tmp_path / "quarantine")
    raw_file = tmp_path / "immutable_test.txt"
    raw_file.write_text("Verified corpus line for immutability testing", encoding="utf-8")

    rep = pipe.process_incoming_file("SRC-TEST-13", raw_file, is_archive=False)
    assert rep.status == "PASSED_QUARANTINE_VALIDATION"

    # Must be read-only
    mode = raw_file.stat().st_mode
    assert not (mode & stat.S_IWUSR)


# ---------------------------------------------------------------------------
# Vector 23: Recovery After Process Interruption
# ---------------------------------------------------------------------------
def test_recovery_after_process_interruption(tmp_path):
    """Verify that if a process leaves a leftover .part file, engine recovers cleanly."""
    dest = tmp_path / "recovered_file.txt"
    part_file = Path(str(dest) + ".part")
    # Simulate orphan partial download from crashed process
    part_file.write_bytes(b"STALE_HALF_WRITTEN_BYTES_FROM_CRASH")

    engine = SecureAcquisitionEngine(gate_unlocked=True, audit_log_path=tmp_path / "audit.jsonl")

    res = engine.download_source(
        source_id="SRC-TEST-14",
        url="https://huggingface.co/test/recovered.txt",
        destination_path=dest,
        max_size_bytes=10000,
        mock_chunks=[b"Clean fresh data"]
    )

    assert res["status"] == "SUCCESS"
    assert dest.exists()
    assert dest.read_bytes() == b"Clean fresh data"
    assert not part_file.exists()


# ---------------------------------------------------------------------------
# Vector 24: Operational Tier Isolation Enforcement
# ---------------------------------------------------------------------------
def test_tier_isolation_enforcement(tmp_path):
    """Verify that Tier 2, Tier 3, and Tier 4 sources cannot be authorized for training ingress."""
    auth = SourceAcquisitionAuthorizer(locks_dir=tmp_path / "locks")

    # Tier 2 Conditional: blocked from vocab training
    with pytest.raises(TierIsolationViolationError, match="Tier 2 source SRC-TM-02 is conditionally restricted"):
        auth.verify_authorization(
            source_id="SRC-TM-02",
            requested_url="https://dumps.wikimedia.org/tawiki/",
            intended_use="VOCABULARY_TRAINING"
        )

    # Tier 3 Evaluation-Only: blocked from training
    with pytest.raises(TierIsolationViolationError, match="Tier 3 source SRC-CD-02 is evaluation-only"):
        auth.verify_authorization(
            source_id="SRC-CD-02",
            requested_url="https://github.com/openai/human-eval",
            intended_use="VOCABULARY_TRAINING"
        )

    # Tier 4 Permanently Rejected: blocked from all operations
    with pytest.raises(TierIsolationViolationError, match="Tier 4 source SRC-CV-01 is permanently rejected"):
        auth.verify_authorization(
            source_id="SRC-CV-01",
            requested_url="https://huggingface.co/datasets/daily_dialog",
            intended_use="EVALUATION_OR_TRAINING"
        )
