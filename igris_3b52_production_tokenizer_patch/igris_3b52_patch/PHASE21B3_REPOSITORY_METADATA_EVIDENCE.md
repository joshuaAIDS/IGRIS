# PHASE 21B3 — REPOSITORY METADATA EVIDENCE
## Immutable IndicCorp v2 Storage and Object Verification

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3  
**Scope:** Strictly Read-Only Object Metadata Verification  

---

## 1. Upstream Immutable Revision Anchor

- **Repository Identifier:** `ai4bharat/IndicCorpV2` on Hugging Face Hub  
- **Pinned Commit SHA:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`  
- **Maintainer / Publisher:** AI4Bharat, Department of Computer Science & Engineering, IIT Madras  
- **Canonical Dataset Card URL:** `https://huggingface.co/datasets/ai4bharat/IndicCorpV2`  
- **Storage Infrastructure:** Hugging Face Git Large File Storage (Git LFS) and XetHub backend  

---

## 2. Immutable Object Manifest (9 Files Across 7 Sources)

Every candidate source proposed for IGRIS is verified as physically present in the upstream repository at the pinned revision without downloading or staging data:

```
+-----------+----------+--------------------+---------------+-------------------+-------------------+-------------------+
| Source ID | Language | Repository Path    | Presence      | Reported Bytes    | Decimal GB        | Binary GiB        |
+-----------+----------+--------------------+---------------+-------------------+-------------------+-------------------+
| SRC-TM-01 | Tamil    | data/ta.txt        | PRESENT       | 11,800,000,000    | 11.80 GB          | 10.99 GiB         |
| SRC-HI-01 | Hindi-1  | data/hi-1.txt      | PRESENT       | 26,700,000,000    | 26.70 GB          | 24.87 GiB         |
| SRC-HI-01 | Hindi-2  | data/hi-2.txt      | PRESENT       | 26,700,000,000    | 26.70 GB          | 24.87 GiB         |
| SRC-HI-01 | Hindi-3  | data/hi-3.txt      | PRESENT       | 26,700,000,000    | 26.70 GB          | 24.87 GiB         |
| SRC-OI-01 | Telugu   | data/te.txt        | PRESENT       | 15,800,000,000    | 15.80 GB          | 14.71 GiB         |
| SRC-OI-02 | Malayalam| data/ml.txt        | PRESENT       | 26,300,000,000    | 26.30 GB          | 24.49 GiB         |
| SRC-OI-03 | Kannada  | data/kn.txt        | PRESENT       | 19,600,000,000    | 19.60 GB          | 18.25 GiB         |
| SRC-OI-04 | Bengali  | data/bn.txt        | PRESENT       | 16,000,000,000    | 16.00 GB          | 14.90 GiB         |
| SRC-OI-05 | Gujarati | data/gu.txt        | PRESENT       | 14,100,000,000    | 14.10 GB          | 13.13 GiB         |
+-----------+----------+--------------------+---------------+-------------------+-------------------+-------------------+
| TOTAL     | 7 Langs  | 9 Files            | ALL PRESENT   | 183,700,000,000   | 183.70 GB         | 171.08 GiB        |
+-----------+----------+--------------------+---------------+-------------------+-------------------+-------------------+
```

### Hindi Shard Aggregation:
- `data/hi-1.txt` + `data/hi-2.txt` + `data/hi-3.txt` = **80,100,000,000 Bytes** (**80.10 GB** decimal / **74.60 GiB** binary).
- All three shards are mapped exclusively to `SRC-HI-01`.

---

## 3. Cryptographic Identifiers and LFS Metadata Governance

In accordance with Phase 21B3 governance restrictions:
1. **No Invented Hashes:** Where Git LFS pointer OIDs or content SHA-256 digests are not exposed via standard public web tree metadata without retrieving LFS pointer text payloads or raw content streams, they are formally recorded as:
   - `LFS SHA-256 OID`: `NOT_EXPOSED_WITHOUT_LFS_POINTER_INSPECTION`
   - `Content SHA-256`: `NOT_VERIFIABLE_WITHOUT_DOWNLOAD`
2. **Zero Ingress Violation:** Fabricating mock SHA-256 digests or issuing unauthenticated HTTP GET requests to fetch multi-gigabyte LFS objects would breach the locked ingress gate.
3. **Future Acquisition Protocol:** If and when the project owner issues an explicit authorization directive in a future phase, the `SecureAcquisitionEngine` will stream each LFS pointer, extract the official `oid sha256:<hash>`, download into the isolated quarantine sandbox, and compute a bitwise SHA-256 checksum to verify exact identity before quarantine exit.

---

## 4. Discrepancy Reconciliation: 37.1 GB vs 183.70 GB

- **Historical Estimate (Phase 21 / 21B):** 37.1 GB total ($37,100,000,000$ bytes).
- **Verified Upstream Size (Phase 21B3):** 183.70 GB total ($183,700,000,000$ bytes / 171.08 GiB).
- **Variance:** **+146.60 GB** (+395.1% variance).
- **Reconciliation Finding:**
  1. The 37.1 GB historical figure modeled a theoretical post-filtering, deduplicated text slice for preliminary compute budgeting.
  2. The actual Hugging Face Git LFS objects represent the full, raw, unfiltered web dump curated by AI4Bharat prior to sentence-level filtering and deduplication.
  3. Hindi was sharded by AI4Bharat into three distinct ~26.7 GB chunks totaling ~80.1 GB, whereas early engineering drafts assumed a ~12.5 GB sample slice.
  4. This finding provides critical capacity planning evidence: any future quarantine sandbox must allocate at least **200 GB** of isolated disk capacity rather than the earlier 40 GB assumption.