"""
IGRIS Phase 12 Security Testing Suite
====================================
Tests for Secure Dataset Acquisition and Quarantine Pipeline

Covers 12 Critical Security Vectors:
1. Unauthorized domain blocking
2. Plain HTTP / scheme downgrade blocking
3. Redirect abuse (domain escape, excessive hops, downgrade)
4. Archive path traversal / Zip-Slip defense
5. Malicious file / executable binary header detection
6. Cryptographic SHA-256 mismatch detection and partial cleanup
7. Corrupted download handling and atomic cleanup
8. Oversized file streaming cutoff
9. Duplicate content archive detection
10. UTF-8 losslessness and Unicode replacement character detection
11. Quarantine isolation and write-once immutability
12. Append-only cryptographically chained audit log integrity
"""

import hashlib
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
    AcquisitionGateLockedError,
    AcquisitionAuditLogger,
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
# Vector 1: Unauthorized Domain Blocking
# ---------------------------------------------------------------------------
def test_unauthorized_domain_blocked():
    """Verify that requests to unapproved domains or malicious lookalikes are blocked."""
    unauthorized_urls = [
        "https://malicious-external-mirror.com/dataset.tar.gz",
        "https://phishing-huggingface.co/repo/data.zip",
        "https://192.168.1.100/data.parquet",
        "https://evil.corp.gutenberg.org.attacker.com/book.txt",
        "https://raw.githubusercontent.com.evil.com/payload.sh",
    ]
    for url in unauthorized_urls:
        with pytest.raises(DomainNotAllowedError):
            validate_url(url)


# ---------------------------------------------------------------------------
# Vector 2: HTTP Downgrade & Insecure Scheme Blocking
# ---------------------------------------------------------------------------
def test_http_downgrade_blocked():
    """Verify that plain HTTP, FTP, file, and other non-HTTPS schemes are strictly rejected."""
    insecure_urls = [
        "http://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/hi.txt",
        "http://huggingface.co/datasets/oasst1.jsonl.gz",
        "ftp://ftp.unicode.org/Public/UCD.zip",
        "file:///C:/IGRIS/local_data.txt",
        "gopher://gutenberg.org/11",
    ]
    for url in insecure_urls:
        with pytest.raises(InsecureSchemeError):
            validate_url(url)


# ---------------------------------------------------------------------------
# Vector 3: Redirect Abuse Blocking
# ---------------------------------------------------------------------------
def test_redirect_abuse_blocked():
    """Verify that redirect chains targeting unapproved domains, downgrading to HTTP, or exceeding 3 hops fail."""
    # Scenario A: Excessive hops (> 3)
    hops_excessive = [
        "https://huggingface.co/hop1",
        "https://huggingface.co/hop2",
        "https://huggingface.co/hop3",
        "https://huggingface.co/hop4",
    ]
    with pytest.raises(RedirectAbuseError, match="exceeds maximum permitted hops"):
        validate_redirect_chain("https://huggingface.co/initial", hops_excessive, max_redirects=3)

    # Scenario B: Hop downgrades to plain HTTP
    hops_downgrade = [
        "https://huggingface.co/hop1",
        "http://huggingface.co/hop2",
    ]
    with pytest.raises(RedirectAbuseError, match="downgraded security"):
        validate_redirect_chain("https://huggingface.co/initial", hops_downgrade)

    # Scenario C: Hop redirects to untrusted external domain
    hops_untrusted = [
        "https://huggingface.co/hop1",
        "https://attacker-redirect-target.com/payload.bin",
    ]
    with pytest.raises(RedirectAbuseError, match="targeted unapproved domain"):
        validate_redirect_chain("https://huggingface.co/initial", hops_untrusted)


# ---------------------------------------------------------------------------
# Vector 4: Archive Path Traversal / Zip-Slip Defense
# ---------------------------------------------------------------------------
def test_zip_slip_path_traversal_blocked(tmp_path):
    """Verify that malicious zip and tar archives containing directory traversal members are rejected."""
    target_extract = tmp_path / "sandbox_out"
    target_extract.mkdir()

    # Create a malicious zip in memory with ../ traversal
    zip_bytes_io = io.BytesIO()
    with zipfile.ZipFile(zip_bytes_io, "w") as zf:
        zf.writestr("../../escape_sandbox.txt", b"MALICIOUS_ESCAPE_PAYLOAD")
        zf.writestr("safe_file.txt", b"SAFE_CONTENT")

    malicious_zip = tmp_path / "malicious.zip"
    malicious_zip.write_bytes(zip_bytes_io.getvalue())

    with pytest.raises(ZipSlipTraversalError, match="Zip slip traversal"):
        safe_extract_zip(malicious_zip, target_extract)

    # Ensure payload did not escape
    assert not (tmp_path / "escape_sandbox.txt").exists()

    # Create a malicious tar archive in memory with absolute / traversal
    tar_bytes_io = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes_io, mode="w") as tf:
        info = tarfile.TarInfo(name="../escaped_tar.sh")
        data = b"echo pwned"
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))

    malicious_tar = tmp_path / "malicious.tar"
    malicious_tar.write_bytes(tar_bytes_io.getvalue())

    with pytest.raises(ZipSlipTraversalError, match="Tar slip traversal"):
        safe_extract_tar(malicious_tar, target_extract)

    assert not (tmp_path / "escaped_tar.sh").exists()


# ---------------------------------------------------------------------------
# Vector 5: Malicious Executable Detection
# ---------------------------------------------------------------------------
def test_malicious_file_detection(tmp_path):
    """Verify that files with executable binary headers (PE, ELF, Mach-O) are rejected."""
    # Windows PE executable (MZ)
    pe_file = tmp_path / "fake_dataset_pe.txt"
    pe_file.write_bytes(b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 60)
    with pytest.raises(MaliciousContentError, match="Windows PE Executable"):
        validate_magic_bytes(pe_file)

    # Linux ELF executable (\x7fELF)
    elf_file = tmp_path / "fake_dataset_elf.txt"
    elf_file.write_bytes(b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 60)
    with pytest.raises(MaliciousContentError, match="Linux ELF Executable"):
        validate_magic_bytes(elf_file)

    # Mach-O executable
    macho_file = tmp_path / "fake_dataset_macho.txt"
    macho_file.write_bytes(b"\xca\xfe\xba\xbe\x00\x00\x00\x02" + b"\x00" * 60)
    with pytest.raises(MaliciousContentError, match="Mach-O"):
        validate_magic_bytes(macho_file)


# ---------------------------------------------------------------------------
# Vector 6: Hash Mismatch Detection & Atomic Cleanup
# ---------------------------------------------------------------------------
def test_hash_mismatch_detection(tmp_path):
    """Verify that a hash mismatch aborts the download, raises HashMismatchError, and purges .part files."""
    dest = tmp_path / "downloaded_file.txt"
    audit_file = tmp_path / "audit.jsonl"
    engine = SecureAcquisitionEngine(gate_unlocked=True, audit_log_path=audit_file)

    fake_content = [b"Chunk 1 of data", b"Chunk 2 of data"]
    expected_wrong_hash = "0" * 64

    with pytest.raises(HashMismatchError, match="Cryptographic hash mismatch"):
        engine.download_source(
            source_id="SRC-TEST-01",
            url="https://huggingface.co/test/dataset.txt",
            destination_path=dest,
            max_size_bytes=10000,
            expected_sha256=expected_wrong_hash,
            mock_chunks=fake_content
        )

    # Verify destination does not exist and temporary .part file was purged
    assert not dest.exists()
    assert not Path(str(dest) + ".part").exists()


# ---------------------------------------------------------------------------
# Vector 7: Corrupted Download Handling & Cleanup
# ---------------------------------------------------------------------------
def test_corrupted_download_handling(tmp_path):
    """Verify that a download failure midway deletes any partial .part artifacts."""
    dest = tmp_path / "corrupted_file.txt"
    audit_file = tmp_path / "audit.jsonl"
    engine = SecureAcquisitionEngine(gate_unlocked=True, audit_log_path=audit_file)

    class ExplodingChunkIterator:
        def __iter__(self):
            yield b"Initial chunk valid"
            raise ConnectionResetError("Connection aborted by remote peer")

    with pytest.raises(ConnectionResetError):
        engine.download_source(
            source_id="SRC-TEST-02",
            url="https://raw.githubusercontent.com/test/corrupt.txt",
            destination_path=dest,
            max_size_bytes=100000,
            mock_chunks=ExplodingChunkIterator()
        )

    assert not dest.exists()
    assert not Path(str(dest) + ".part").exists()


# ---------------------------------------------------------------------------
# Vector 8: Oversized File Streaming Cutoff
# ---------------------------------------------------------------------------
def test_oversized_file_blocked(tmp_path):
    """Verify that streaming data exceeding max_size_bytes is terminated early without saving."""
    dest = tmp_path / "oversized.bin"
    audit_file = tmp_path / "audit.jsonl"
    engine = SecureAcquisitionEngine(gate_unlocked=True, audit_log_path=audit_file)

    # 10 chunks of 1000 bytes = 10,000 bytes; max allowed is 5,000 bytes
    large_chunks = [b"X" * 1000 for _ in range(10)]

    with pytest.raises(OversizedFileError, match="exceeded maximum size limit"):
        engine.download_source(
            source_id="SRC-TEST-03",
            url="https://huggingface.co/large/data.bin",
            destination_path=dest,
            max_size_bytes=5000,
            mock_chunks=large_chunks
        )

    assert not dest.exists()
    assert not Path(str(dest) + ".part").exists()


# ---------------------------------------------------------------------------
# Vector 9: Duplicate Content Detection
# ---------------------------------------------------------------------------
def test_duplicate_archive_detected(tmp_path):
    """Verify that ingesting identical archive hashes multiple times is rejected by content ledger."""
    quarantine_root = tmp_path / "quarantine"
    pipe = QuarantinePipeline(quarantine_root=quarantine_root)

    test_file_1 = tmp_path / "first_archive.txt"
    test_file_1.write_text("Unique text dataset corpus content line 1", encoding="utf-8")

    # First ingest succeeds
    rep1 = pipe.process_incoming_file("SRC-TEST-04", test_file_1, is_archive=False)
    assert rep1.status == "PASSED_QUARANTINE_VALIDATION"

    # Second file with identical content
    test_file_2 = tmp_path / "duplicate_archive.txt"
    test_file_2.write_text("Unique text dataset corpus content line 1", encoding="utf-8")

    with pytest.raises(DuplicateContentError, match="Duplicate archive detected"):
        pipe.process_incoming_file("SRC-TEST-05", test_file_2, is_archive=False)


# ---------------------------------------------------------------------------
# Vector 10: Unicode & Replacement Character Rejection
# ---------------------------------------------------------------------------
def test_unicode_validation_failures(tmp_path):
    """Verify that corrupted UTF-8 byte sequences or U+FFFD replacement characters are rejected."""
    # Case A: Invalid UTF-8 bytes (e.g. invalid continuation byte \x80 without leading byte)
    bad_utf8_file = tmp_path / "bad_utf8.txt"
    bad_utf8_file.write_bytes(b"Valid text prefix \x80\xFF invalid sequence")

    with pytest.raises(UnicodeEncodingError, match="Invalid UTF-8 byte sequence"):
        validate_utf8_losslessness(bad_utf8_file)

    # Case B: Unicode replacement character U+FFFD
    fffd_file = tmp_path / "fffd_text.txt"
    fffd_file.write_text("Corrupted text containing \uFFFD replacement character", encoding="utf-8")

    with pytest.raises(UnicodeEncodingError, match=r"Unicode replacement character U\+FFFD"):
        validate_utf8_losslessness(fffd_file)


# ---------------------------------------------------------------------------
# Vector 11: Quarantine Isolation and Write-Once Immutability
# ---------------------------------------------------------------------------
def test_quarantine_isolation_and_immutability(tmp_path):
    """Verify that raw files staged in quarantine receive write-once read-only protection."""
    quarantine_root = tmp_path / "quarantine"
    pipe = QuarantinePipeline(quarantine_root=quarantine_root)

    raw_file = tmp_path / "corpus_sample.txt"
    raw_file.write_text("Authentic validated Tamil corpus text", encoding="utf-8")

    rep = pipe.process_incoming_file("SRC-TM-01", raw_file, is_archive=False)
    assert rep.status == "PASSED_QUARANTINE_VALIDATION"

    # Check file mode permissions: write permission must be stripped
    file_mode = raw_file.stat().st_mode
    is_writeable_by_owner = bool(file_mode & stat.S_IWUSR)
    assert not is_writeable_by_owner, "Quarantined raw file should not be writeable"


# ---------------------------------------------------------------------------
# Vector 12: Audit Log Cryptographic Integrity & Tamper Detection
# ---------------------------------------------------------------------------
def test_audit_log_integrity(tmp_path):
    """Verify that chained audit logs detect tampering or omitted lines."""
    audit_file = tmp_path / "tamper_audit.jsonl"
    logger = AcquisitionAuditLogger(audit_file)

    logger.log_event("SRC-01", "https://huggingface.co/1", "p1", 100, "hash1", 0.1, "SUCCESS")
    logger.log_event("SRC-02", "https://huggingface.co/2", "p2", 200, "hash2", 0.2, "SUCCESS")
    logger.log_event("SRC-03", "https://huggingface.co/3", "p3", 300, "hash3", 0.3, "SUCCESS")

    ok, count, err = logger.verify_integrity()
    assert ok is True
    assert count == 3
    assert err is None

    # Tamper with the second entry
    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tampered_entry = json.loads(lines[1])
    tampered_entry["bytes_downloaded"] = 999999  # Tampering with byte count
    lines[1] = json.dumps(tampered_entry) + "\n"

    with open(audit_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    ok_after_tamper, _, err_msg = logger.verify_integrity()
    assert ok_after_tamper is False
    assert "mismatch" in err_msg.lower() or "break" in err_msg.lower()


# ---------------------------------------------------------------------------
# Default-Deny Gate Lock Check
# ---------------------------------------------------------------------------
def test_default_deny_gate_lock(tmp_path):
    """Verify that an acquisition attempt with default gate_unlocked=False fails immediately."""
    engine = SecureAcquisitionEngine(gate_unlocked=False, audit_log_path=tmp_path / "gate_audit.jsonl")
    with pytest.raises(AcquisitionGateLockedError, match="Production Data Ingress Gate is LOCKED"):
        engine.download_source(
            source_id="SRC-TM-01",
            url="https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
            destination_path=tmp_path / "ta.txt.tar.gz",
            max_size_bytes=10000000
        )


# ---------------------------------------------------------------------------
# Phase 12 Manifest and Verification Register Validation
# ---------------------------------------------------------------------------
def test_phase12_registers_integrity():
    """Verify that Phase 12 verification and acquisition registers exist and have 32 consistent entries."""
    patch_dir = Path(__file__).resolve().parent.parent
    verif_csv = patch_dir / "IGRIS_PHASE12_SOURCE_VERIFICATION_REGISTER.csv"
    manifest_csv = patch_dir / "IGRIS_PHASE12_ACQUISITION_MANIFEST.csv"

    assert verif_csv.exists(), "Verification register CSV missing"
    assert manifest_csv.exists(), "Acquisition manifest CSV missing"

    import csv
    with open(verif_csv, "r", encoding="utf-8") as f:
        verif_rows = list(csv.DictReader(f))
    assert len(verif_rows) == 32

    with open(manifest_csv, "r", encoding="utf-8") as f:
        manifest_rows = list(csv.DictReader(f))
    assert len(manifest_rows) == 32

    permissive_count = sum(1 for r in verif_rows if r["acquisition_tier"] == "TIER_1_PERMISSIVE")
    conditional_count = sum(1 for r in verif_rows if r["acquisition_tier"] == "TIER_2_CONDITIONAL_BLOCKED")
    eval_only_count = sum(1 for r in verif_rows if r["acquisition_tier"] == "TIER_3_EVALUATION_ISOLATED")
    rejected_count = sum(1 for r in verif_rows if r["acquisition_tier"] == "TIER_4_PERMANENTLY_REJECTED")

    assert permissive_count == 18
    assert conditional_count == 8
    assert eval_only_count == 2
    assert rejected_count == 4

    # Every manifest row must have pipeline_gate_state == LOCKED
    for r in manifest_rows:
        assert r["pipeline_gate_state"] == "LOCKED"
