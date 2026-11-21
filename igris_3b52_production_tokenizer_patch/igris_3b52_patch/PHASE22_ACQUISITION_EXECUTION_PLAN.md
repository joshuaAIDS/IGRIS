# PHASE 22 — DATASET ACQUISITION EXECUTION PLAN
## End-to-End Operational Specification for Secure, Resumable, Verified Ingress of IndicCorp v2

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22  
**Target Upstream Repository:** `ai4bharat/IndicCorpV2`  
**Pinned Revision:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`  
**Execution State:** **PLANNING ONLY — DOWNLOADS STRICTLY PROHIBITED IN PHASE 22**  

---

## 1. Upstream Target Objects & Declared Capacity

Acquisition is planned across the nine flat text objects comprising the seven target language subsets:

```
+-----------+---------------+-------------------+-----------------------+-----------------------+---------------------------------------+
| Source ID | Language      | Exact Remote Path | Declared Size (Bytes) | Size (Decimal / Binary| Transfer Verification Strategy        |
+-----------+---------------+-------------------+-----------------------+-----------------------+---------------------------------------+
| SRC-TM-01 | Tamil         | data/ta.txt       | 11,800,000,000        | 11.80 GB / 10.99 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-HI-01 | Hindi (S1)    | data/hi-1.txt     | 26,700,000,000        | 26.70 GB / 24.87 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-HI-01 | Hindi (S2)    | data/hi-2.txt     | 26,700,000,000        | 26.70 GB / 24.87 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-HI-01 | Hindi (S3)    | data/hi-3.txt     | 26,700,000,000        | 26.70 GB / 24.87 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-OI-01 | Telugu        | data/te.txt       | 15,800,000,000        | 15.80 GB / 14.71 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-OI-02 | Malayalam     | data/ml.txt       | 26,300,000,000        | 26.30 GB / 24.49 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-OI-03 | Kannada       | data/kn.txt       | 19,600,000,000        | 19.60 GB / 18.25 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-OI-04 | Bengali       | data/bn.txt       | 16,000,000,000        | 16.00 GB / 14.90 GiB  | Streaming SHA-256 + LFS Pointer Match |
| SRC-OI-05 | Gujarati      | data/gu.txt       | 14,100,000,000        | 14.10 GB / 13.13 GiB  | Streaming SHA-256 + LFS Pointer Match |
+-----------+---------------+-------------------+-----------------------+-----------------------+---------------------------------------+
| TOTAL     | 7 Languages   | 9 Flat Files      | 183,700,000,000 Bytes | 183.70 GB / 171.08 GiB| Full Pipeline Streaming Verification  |
+-----------+---------------+-------------------+-----------------------+-----------------------+---------------------------------------+
```

---

## 2. Secure Ingress Architecture & Protocol Controls

The future execution of this acquisition plan must adhere to the following strict technical protocols:

### 2.1. Isolated Quarantine Staging Directory Layout
- All downloads must be directed to an ephemeral, isolated quarantine volume (e.g. `/mnt/cloud_storage/igris_quarantine/`):
  ```
  /mnt/cloud_storage/igris_quarantine/
  ├── incoming/                  <-- Incomplete .part files during active transfer
  ├── staged/                    <-- Fully transferred files awaiting verification
  ├── pointers/                  <-- Git LFS pointer text sidecars
  ├── logs/                      <-- acquisition_audit.jsonl
  └── verified/                  <-- Cryptographically certified files ready for cleaning
  ```
- No files may enter `verified/` until streaming verification confirms exact byte-count and LFS OID matching.

### 2.2. Resumable Chunked Download Strategy
- Files range from 11.8 GB to 26.7 GB each. Network interruptions over public HTTPS must not result in discarded partial downloads.
- Downloads must use an HTTP client supporting:
  1. `Range: bytes=START-END` request headers for automatic resumption.
  2. Persistent chunk sidecars (`.meta.json`) recording byte offsets and partial hash accumulators.
  3. Atomic rename upon completion: `data.txt.part` $ightarrow$ `data.txt`.

### 2.3. Dual-Layer Cryptographic Verification
1. **Layer 1 (LFS Pointer Validation):** Prior to downloading the large payload, retrieve the small LFS pointer text file (under 200 bytes) and extract the declared `sha256:<OID>` and `size:<BYTES>`.
2. **Layer 2 (Streaming Payload Hash):** Stream the payload through Python’s `hashlib.sha256()` in 64 KiB chunks during disk writing. Compare the final computed digest against the extracted pointer OID.
3. If the final digest mismatches or the byte length diverges by even 1 byte, the file is immediately purged.

### 2.4. Cleaning, Deduplication, and PII Pipeline
Once unquarantined into the processing pipeline:
1. **Heuristic Line Filtering:** Filter lines shorter than 30 characters, HTML tags, boilerplate navigation text, and lines with excessive digit/symbol ratios.
2. **Language ID Verification:** FastText language identification model (`lid.176.bin`) runs on line samples to verify dialect authenticity (>90% target language threshold).
3. **MinHash LSH Deduplication:** 5-gram token MinHash with 128 permutations across Jaccard similarity threshold 0.85 to remove duplicate web articles.
4. **PII Masking:** Regex-based redaction of phone numbers, email addresses, Aadhaar numbers, and PAN card numbers.

### 2.5. Atomic Rollback Strategy
If any anomaly, authorization failure, or integrity breach occurs:
1. Active download processes are terminated immediately via SIGTERM.
2. All partial files in `incoming/` and unverified files in `staged/` are atomically deleted.
3. The event is recorded in `acquisition_audit.jsonl` with an `ABORT_ROLLBACK` event record.
4. Production ingress gate transitions immediately to `FORCE_LOCKED`.

---

## 3. Prerequisite Governance Checklist Before Execution

Acquisition cannot be initiated until all of the following conditions are formally satisfied:
- [ ] Formal legal review completed by qualified counsel for IndicCorp v2 web-crawled content.
- [ ] Explicit Project Owner authorization recorded for each individual source ID.
- [ ] 1 TB cloud staging volume provisioned and verified.
- [ ] SecureAcquisitionEngine configured with isolated cloud paths.
- [ ] Ephemeral execution script tested in dry-run mode.
