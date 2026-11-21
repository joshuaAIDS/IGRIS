# IGRIS PHASE 12: SECURE DATASET ACQUISITION ENGINE DESIGN

**Document Identifier**: `IGRIS-P12-SAD-2026-V1`  
**Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Status**: `APPROVED_INFRASTRUCTURE_DESIGN — INGRESS GATE REMAINS LOCKED`  
**Target Invariant**: Candidate A (`ac7e18b1...`) & Candidate B (`d3a3431e...`) Unmodified

---

## 1. Executive Summary

This document establishes the architectural specification and security controls for the **IGRIS Controlled Dataset Acquisition Pipeline**. Designed under the `SOLO_DEVELOPER_OWNER_REVIEW` governance model, this infrastructure enables secure, reproducible, and verifiable staging of candidate dataset sources into isolated quarantine environments.

> [!IMPORTANT]
> **Default-Deny Gate Invariant**: The production data ingress gate remains strictly **LOCKED**. The engine refuses automated acquisition requests unless explicit, cryptographic owner authorization is verified. No external production data is acquired during this milestone.

---

## 2. Core Security Requirements & Threat Mitigation

The acquisition engine addresses seven primary network and staging threats:

| Threat Vector | Attack Scenario | Mitigation Strategy | Enforced Error |
| :--- | :--- | :--- | :--- |
| **Unauthorized Origin** | Attacker injects malicious download URL or mirrors | Strict domain allowlist matching and subdomain validation | `DomainNotAllowedError` |
| **Protocol Downgrade** | Man-in-the-middle forces plain HTTP | Scheme check strictly requiring `https://` | `InsecureSchemeError` |
| **Redirect Hijacking** | Initial HTTPS redirects to malicious domain or plain HTTP | Multi-hop inspection (max 3 hops), re-validating domain and scheme on each hop | `RedirectAbuseError` |
| **Denial of Service** | Infinite stream or oversized archive crashes storage | Streaming byte counter terminating at `max_size_bytes` | `OversizedFileError` |
| **Data Tampering** | Bit-flip, proxy injection, or mirror corruption | Incremental SHA-256 computation and manifest verification | `HashMismatchError` |
| **Partial Artifact Leakage** | Aborted download leaves unverified bytes in production paths | Atomic `.part` staging; immediate unlinking on error; atomic promotion | Atomic rollback |
| **Audit Log Tampering** | Malicious actor modifies acquisition history | Cryptographic SHA-256 hash chaining on all log records | `verify_integrity()` mismatch |

---

## 3. Architecture & Component Workflow

```
[ Ingress Request ] ───► [ 1. Gate Lock Check ] ──(LOCKED)──► [ AcquisitionGateLockedError ]
                                │ (UNLOCKED)
                                ▼
                       [ 2. URL Scheme & Host ] ──(INVALID)─► [ SecurityValidationError ]
                                │ (HTTPS & WHITELIST)
                                ▼
                       [ 3. Redirect Validator ] ─(UNSAFE)──► [ RedirectAbuseError ]
                                │ (SAFE <= 3 HOPS)
                                ▼
                       [ 4. Streaming Transfer ] ───────────► [ Write to <dest>.part ]
                                │                                     │
                                ├─ Stream > max_bytes? ───────────────┼──► [ OversizedFileError & Delete .part ]
                                ├─ Connection Aborted? ───────────────┼──► [ ConnectionError & Delete .part ]
                                ▼                                     │
                       [ 5. SHA-256 Validation ] ─────────────┼──► [ HashMismatchError & Delete .part ]
                                │ (MATCH)                             │
                                ▼                                     ▼
                       [ 6. Atomic Promotion ] ─────────────► [ Rename .part -> <dest> ]
                                │
                                ▼
                       [ 7. Chained Audit Log ] ────────────► [ Append to acquisition_audit.jsonl ]
```

### 3.1 Domain Whitelist Specification

The engine allows downloads exclusively from designated upstream endpoints hosting the 18 permissive candidate sources:

```python
APPROVED_DOMAINS = {
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
```

- **Subdomain Rules**: Subdomains of approved parents are permitted (e.g., `indicglue.ai4bharat.org`), but lookalike domains (e.g., `ai4bharat.org.attacker.com`) are strictly rejected.
- **Port Enforcement**: Only standard port 443 (or omitted) is allowed.
- **Embedded Credentials**: Any URL containing `user:pass@host` is rejected.
- **Raw IP Hosts**: Raw IPv4/IPv6 addresses are strictly forbidden.

### 3.2 Redirect Verification Engine

Upstream mirrors and CDNs frequently issue `301`, `302`, or `307` redirects. The engine executes hop-by-hop verification:
1. Maximum hop limit: **3 hops**. Exceeding 3 hops raises `RedirectAbuseError`.
2. Every intermediate hop and the final target URL must have scheme `https`.
3. Every intermediate hop and the final target URL must resolve to an approved domain in `APPROVED_DOMAINS`.
4. Protocol downgrade (HTTPS -> HTTP) immediately halts the connection and raises `RedirectAbuseError`.

### 3.3 Streaming Transfer & Atomic Placement

To ensure system stability and prevent disk exhaustion:
1. **Socket Timeout**: 30.0 seconds default timeout per read cycle.
2. **Chunk Size**: Fixed 64 KB buffers (`65,536` bytes).
3. **Byte Counter**: Total downloaded bytes are incremented per chunk. If `total > max_size_bytes`, the socket is closed immediately, the `.part` file is deleted, and `OversizedFileError` is raised.
4. **Incremental Hash**: `hashlib.sha256()` is updated chunk-by-chunk in memory.
5. **Atomic Promotion**: `os.replace("<dest>.part", "<dest>")` ensures that unverified or corrupted partial files are never visible to the quarantine parser or model training stages.

---

## 4. Cryptographic Chained Audit Logging

Every acquisition event (success or failure) is logged to `quarantine/logs/acquisition_audit.jsonl`.

### 4.1 Log Record Schema

```json
{
  "timestamp": "2026-11-18T05:52:00Z",
  "source_id": "SRC-TM-01",
  "url": "https://raw.githubusercontent.com/AI4Bharat/IndicCorp/main/downloads/ta.txt.tar.gz",
  "destination_path": "quarantine/datasets/SRC-TM-01/raw/ta.txt.tar.gz",
  "bytes_downloaded": 1048576,
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "duration_seconds": 1.452,
  "status": "SUCCESS",
  "error": null,
  "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "entry_hash": "a1b2c3d4..."
}
```

### 4.2 Hash Chain Invariant

For entry $i$:
$$\text{Payload}_i = \text{timestamp}_i \parallel \text{source\_id}_i \parallel \text{url}_i \parallel \text{dest}_i \parallel \text{bytes}_i \parallel \text{sha256}_i \parallel \text{status}_i \parallel \text{error}_i \parallel \text{entry\_hash}_{i-1}$$
$$\text{entry\_hash}_i = \text{SHA-256}(\text{Payload}_i)$$

Any line deletion, reordering, or field modification breaks the chain and is detected by `verify_integrity()`.

---

## 5. Summary of Engine Interfaces

The engine is implemented in [secure_acquisition_engine.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/secure_acquisition_engine.py):
- `validate_url(url, custom_whitelist=None) -> bool`
- `validate_redirect_chain(initial_url, hops, max_redirects=3) -> bool`
- `SecureAcquisitionEngine(gate_unlocked=False, audit_log_path=None)`
- `download_source(source_id, url, destination_path, max_size_bytes, expected_sha256=None, ...)`
- `AcquisitionAuditLogger.verify_integrity() -> Tuple[bool, int, Optional[str]]`

**Pipeline Gate State**: `LOCKED` (Default-Deny Enforced).
