# IGRIS PHASE 13: CONTROLLED DATASET ACQUISITION SECURITY DESIGN

**Document Identifier**: `IGRIS-P13-ASD-2026-V1`  
**Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Status**: `VERIFIED_AND_LOCKED — ZERO UNAUTHORIZED INGRESS`  
**Architecture Invariant**: Candidate A (`ac7e18b1...`) & Candidate B (`d3a3431e...`) Unmodified

---

## 1. Architectural Scope & Operating Model

This document specifies the security architecture for **Phase 13: Controlled Dataset Acquisition**. Operating under the `SOLO_DEVELOPER_OWNER_REVIEW` governance model, the pipeline enforces strict individual, source-specific owner authorization before any network transfer can occur.

> [!IMPORTANT]
> **No Automated Bulk Authorization**: Permissive licensing does not confer automatic acquisition clearance. All 18 candidate sources remain in state `PENDING_EXPLICIT_OWNER_AUTHORIZATION` until individually granted by the project owner. Production data ingress remains **LOCKED**.

---

## 2. Source-Specific Authorization Architecture

```
[ Ingress Request ] 
       │
       ▼
[ Gate Lock Check ] ──────────(LOCKED)────────► [ AcquisitionGateLockedError ]
       │ (UNLOCKED)
       ▼
[ Authorizer Verification ]
       ├─ No Grant Record? ───────────────────► [ UnauthorizedAcquisitionError (Default-Deny) ]
       ├─ Status == REVOKED? ─────────────────► [ RevokedAuthorizationError ]
       ├─ Status == EXPIRED / Time Out? ──────► [ ExpiredAuthorizationError ]
       ├─ Replayed Nonce? ────────────────────► [ ReplayAcquisitionError ]
       ├─ URL Mismatch? ──────────────────────► [ UnauthorizedSourceURLError ]
       ├─ Tier 2/3/4 Training Request? ───────► [ TierIsolationViolationError ]
       ▼ (AUTHORIZED)
[ Concurrency Locking ] ──────(ALREADY LOCKED)► [ ConcurrentAcquisitionError ]
       │ (LOCK ACQUIRED)
       ▼
[ Network Transport & Streaming ]
       ├─ Insecure Scheme / Plain HTTP ───────► [ InsecureSchemeError ]
       ├─ Unapproved Domain / Phishing ───────► [ DomainNotAllowedError ]
       ├─ Redirect > 3 hops / Target Escape ──► [ RedirectAbuseError ]
       ├─ Stream > max_size_bytes? ───────────► [ OversizedFileError & Delete .part ]
       ├─ Connection Abort? ──────────────────► [ ConnectionError & Delete .part ]
       ▼
[ SHA-256 Hash Verification ] ─(MISMATCH)─────► [ HashMismatchError & Delete .part ]
       │ (MATCH)
       ▼
[ Atomic Promotion (.part -> dest) ]
       │
       ▼
[ Quarantine 10-Point Pipeline ] ─────────────► [ Safe Extraction, UTF-8, PII, Immutability ]
       │
       ▼
[ Persistent Ledger & Chained Audit ] ────────► [ Append to Ledger CSV & acquisition_audit.jsonl ]
       │
       ▼
[ Release Concurrency Lock ]
```

### 2.1 The Authorizer Component (`source_acquisition_authorizer.py`)

The [source_acquisition_authorizer.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/source_acquisition_authorizer.py) module enforces:

1. **Default-Deny Access Control**: A missing grant raises `UnauthorizedAcquisitionError`. No ambient or global approvals exist.
2. **Provenance & Release Pinning**: Each grant specifies the precise release version and upstream URL prefix. Divergence raises `UnauthorizedSourceURLError`.
3. **Temporal Validity & Revocation**:
   - An expired timestamp raises `ExpiredAuthorizationError`.
   - A revoked authorization record raises `RevokedAuthorizationError` immediately.
4. **Replay Protection**: Nonce consumption tracking rejects duplicate acquisition tokens with `ReplayAcquisitionError`.
5. **Operational Tier Isolation**:
   - Tier 2 (Conditional) and Tier 3 (Evaluation-Only) sources cannot be authorized for training ingress; attempting to authorize training raises `TierIsolationViolationError`.
   - Tier 4 (Permanently Rejected) sources cannot be authorized for any operation.

### 2.2 Concurrency Locking & Race Condition Prevention

Concurrent download attempts on the same source could corrupt partial downloads or race on extraction. The authorizer implements filesystem mutex locks (`quarantine/locks/<source_id>.lock`):
- Attempting a concurrent acquisition on an active source raises `ConcurrentAcquisitionError`.
- Locks are released strictly in `finally:` blocks upon success or exception.

---

## 3. Network Transport & Streaming Defense

The [secure_acquisition_engine.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/secure_acquisition_engine.py) provides network-level hardening:

1. **Approved Domain Whitelist**: Downloads permitted only from designated domains (`huggingface.co`, `github.com`, `raw.githubusercontent.com`, `archive.org`, `gutenberg.org`, `unicode.org`, `rfc-editor.org`, `python.org`, `ai4bharat.org`). Raw IP addresses and untrusted mirrors raise `DomainNotAllowedError`.
2. **HTTPS Strictness**: Scheme must be `https`. Plain HTTP or downgrade attempts raise `InsecureSchemeError`.
3. **Redirect Hop Inspector**: Multi-hop validation enforces max 3 hops, re-checking scheme and domain on every hop. Protocol downgrade or domain escape raises `RedirectAbuseError`.
4. **Streaming Byte Ceilings**: Incremental 64 KB chunk reads count total bytes. Exceeding `max_size_bytes` immediately closes the connection, purges the `.part` file, and raises `OversizedFileError`.
5. **Atomic Staging**: Downloads write to `<dest>.part`. On any failure, the temporary file is unlinked. Promotion to final `<dest>` occurs atomically via `os.replace` only after SHA-256 verification.

---

## 4. Persistent Acquisition Ledger

Every completed acquisition is recorded in [IGRIS_PHASE13_ACQUISITION_LEDGER.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_PHASE13_ACQUISITION_LEDGER.csv) with the following schema:

| Column | Description |
| :--- | :--- |
| `acquisition_id` | Unique identifier (e.g. `ACQ-SRC-TM-01-1794981994`) |
| `source_id` | Candidate source ID (e.g. `SRC-TM-01`) |
| `source_version` | Upstream version / release tag |
| `authorization_reference` | Specific owner approval reference |
| `official_download_url` | Full verified download endpoint |
| `download_timestamp` | ISO-8601 acquisition timestamp |
| `downloaded_byte_count` | Exact transferred bytes |
| `sha256` | Verified SHA-256 hash |
| `file_format` | Archive or document format (`tar.gz`, `zip`, `txt`, etc.) |
| `quarantine_location` | Isolated sandbox path (`quarantine/datasets/<source_id>/raw/`) |
| `validation_result` | Quarantine outcome (`SUCCESS` or `REJECTED`) |
| `rejection_reason` | Diagnostic error if rejected |
| `audit_chain_reference` | SHA-256 hash from chained audit log |

---

## 5. Security Invariant Summary

1. **Default-Deny Invariant**: `gate_unlocked=False` default.
2. **Zero Automated Ingress**: No dataset is fetched without explicit owner instruction.
3. **Artifact Immutability**: Candidate A and Candidate B tokenizers remain untouched.
4. **Audit Immutability**: All acquisition events cryptographically chained in `acquisition_audit.jsonl`.
