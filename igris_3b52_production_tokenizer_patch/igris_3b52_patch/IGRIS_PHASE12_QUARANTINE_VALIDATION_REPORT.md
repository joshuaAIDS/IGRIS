# IGRIS PHASE 12: QUARANTINE VALIDATION PIPELINE SPECIFICATION & REPORT

**Document Identifier**: `IGRIS-P12-QVR-2026-V1`  
**Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Implementation**: [ingress_safety_pipeline.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/ingress_safety_pipeline.py)  
**Status**: `VERIFIED_AND_LOCKED — ZERO PRODUCTION INGRESS DETECTED`

---

## 1. Scope & Objective

This report details the architectural enforcement mechanisms of the **IGRIS Quarantine Validation Pipeline**. The quarantine pipeline acts as an impermeable airlock between external data sources and downstream tokenizer/model training pipelines. 

Every candidate dataset admitted to the quarantine sandbox must pass ten consecutive cryptographic, structural, and content-safety gates before being deemed eligible for pre-processing. Any single failure triggers immediate isolation into a rejection directory and write-once locking.

---

## 2. Quarantine Directory Layout & Staging Isolation

The pipeline isolates datasets in strict hierarchical boundaries:

```
quarantine/
├── datasets/
│   ├── <source_id>/
│   │   ├── raw/                  <-- Staged raw archive (Read-Only 0o444)
│   │   └── extracted/            <-- Sandbox-constrained decompressed members
├── rejected/
│   └── <source_id>/
│       └── <YYYYMMDD_HHMMSS>/
│           ├── <rejected_file>   <-- Quarantined invalid payload
│           └── rejection_reason.json
├── content_hash_ledger.json      <-- Global deduplication hash registry
└── quarantine_manifest.json      <-- Canonical audit trail of all validation runs
```

---

## 3. Ten-Point Quarantine Validation Gates

```
[ Raw Archive ]
       │
       ▼
[ Gate 1: SHA-256 Check ] ──────────(MISMATCH)─────► [ Reject to quarantine/rejected/ ]
       │ (MATCH)
       ▼
[ Gate 2: Deduplication Check ] ────(DUPLICATE)────► [ Reject to quarantine/rejected/ ]
       │ (UNIQUE)
       ▼
[ Gate 3: Magic Byte Check ] ───────(EXECUTABLE)───► [ Reject to quarantine/rejected/ ]
       │ (VALID ARCHIVE/TEXT)
       ▼
[ Gate 4: Zip-Slip Inspection ] ────(TRAVERSAL)────► [ Reject to quarantine/rejected/ ]
       │ (SAFE EXTRACTION)
       ▼
[ Gate 5: Safe Extraction ]
       │
       ▼
[ Gate 6: Strict UTF-8 Decode ] ────(INVALID)──────► [ Reject to quarantine/rejected/ ]
       │ (VALID)
       ▼
[ Gate 7: U+FFFD Replacement Check ] ─(DETECTED)───► [ Reject to quarantine/rejected/ ]
       │ (ZERO REPLACEMENTS)
       ▼
[ Gate 8: Unicode 15.1.0 NFC Check ] ─(NON-NFC)────► [ Flag / Quarantine Review ]
       │ (NORMALIZED)
       ▼
[ Gate 9: PII Screening ] ──────────(LOGGED)───────► [ Record PII Metrics ]
       │
       ▼
[ Gate 10: Immutability Lock ] ─────────────────────► [ chmod 0o444 & Quarantine Manifest ]
```

### 3.1 Gate 1: Cryptographic SHA-256 Hash Verification
- Incremental hash calculated on staged file.
- Compared against expected manifest hash. Mismatches raise `QuarantineValidationError`.

### 3.2 Gate 2: Content Hash Ledger & Duplicate Detection
- The pipeline maintains `content_hash_ledger.json`.
- Ingesting identical archive content under different names or sources raises `DuplicateContentError` and moves the file to `quarantine/rejected/`.

### 3.3 Gate 3: Header Magic Byte & Executable Binary Defense
- Header inspection blocks executable payloads disguised as text:
  - Windows PE: `b"MZ"`
  - Linux ELF: `b"\x7fELF"`
  - Mach-O / Java Class: `b"\xca\xfe\xba\xbe"`, `b"\xfe\xed\xfa\xce"`, `b"\xfe\xed\xfa\xcf"`
- Detection immediately raises `MaliciousContentError`.

### 3.4 Gate 4 & 5: Zip-Slip / Archive Traversal Protection
- Archive members in `.zip`, `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz` are inspected:
  - Any member containing `..`, leading `/` or `\\`, or drive letters is rejected.
  - Path resolution strictly checks `os.path.commonpath([target_dir, dest_path]) == target_dir`.
  - Symbolic links pointing outside the sandbox are strictly prohibited.
- Violations raise `ZipSlipTraversalError`.

### 3.5 Gate 6 & 7: Strict UTF-8 Losslessness & U+FFFD Prevention
- Text files are decoded in 64 KB blocks with `errors="strict"`.
- Any unmappable byte sequence raises `UnicodeEncodingError`.
- Scanned for Unicode Replacement Character `\uFFFD` (`\xef\xbf\xbd`). The presence of `\uFFFD` indicates upstream lossy transcode and causes immediate quarantine rejection.

### 3.6 Gate 8: Unicode 15.1.0 Canonical Normalization (NFC)
- All text is evaluated against `unicodedata.is_normalized('NFC', text)`.
- Enforces IGRIS Unicode stability invariants: tokenizers trained on non-NFC text experience vocabulary fragmentation and higher fertility rates.

### 3.7 Gate 9: Automated PII Screening
- The pipeline screens decoded text for personally identifiable information:
  - **Email addresses**: Standard RFC 5322 regex.
  - **Phone numbers**: US and Indian international/mobile formats (`+91` / 10 digits).
  - **National IDs**: US Social Security Numbers (`\d{3}-\d{2}-\d{4}`) and Indian Aadhaar numbers (`\d{4}\s\d{4}\s\d{4}`).
  - **Credit Card Numbers**: Luhn-pattern matches (samples redacted in logs: `XXXX-XXXX-XXXX-1234`).
  - **IP Addresses**: IPv4 dotted-quad patterns.
- High-density PII triggers manual owner review.

### 3.8 Gate 10: Write-Once Immutability & Manifest Recording
- Once all gates pass:
  - Read-only permissions (`0o444` / read-only attribute) are applied to the raw archive.
  - A structured record is appended to `quarantine_manifest.json`.

---

## 4. Verification & Operational Status

The quarantine validation pipeline is fully implemented in [ingress_safety_pipeline.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/ingress_safety_pipeline.py) and verified across 14 security tests in [test_phase12_acquisition_security.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_phase12_acquisition_security.py).

**Verification Verdict**: `INFRASTRUCTURE OPERATIONAL — ZERO PRODUCTION INGRESS PERMITTED.`
