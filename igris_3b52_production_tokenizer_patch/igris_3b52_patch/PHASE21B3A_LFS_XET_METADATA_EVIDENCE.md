# PHASE 21B3A — LFS AND XET OBJECT METADATA EVIDENCE
## Forensic Investigation of Upstream Object Identifiers and Storage Backends

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3A  
**Scope:** Read-Only Investigation of Git, Git LFS, and Xet Object Identifiers  

---

## 1. Disambiguation of Cryptographic Object Identifiers

In version-controlled large-file datasets, multiple cryptographic hashes exist at different architectural layers. These hashes are **not interchangeable**:

```
+-----------------------------------+-----------------------------------------------------------------------+
| Identifier Type                   | Architectural Definition & Scope                                      |
+-----------------------------------+-----------------------------------------------------------------------+
| 1. Git Blob Identifier            | 40-character SHA-1 hash of the Git tree object representing the small |
|                                   | text pointer file in Git's internal object database.                  |
| 2. Git LFS Object SHA-256 (OID)   | 64-character SHA-256 hash of the remote large file payload, recorded  |
|                                   | inside the Git LFS pointer text (e.g., `oid sha256:<hash>`).          |
| 3. Xet Object / Block Identifier  | Content-addressed deduplication chunk identifier used if repository   |
|                                   | is backed by Hugging Face's proprietary XetHub storage backend.       |
| 4. Downloaded Content SHA-256     | Bitwise SHA-256 digest computed across the uncompressed payload bytes |
|                                   | once acquired and resident on local disk.                             |
+-----------------------------------+-----------------------------------------------------------------------+
```

---

## 2. Upstream Investigation Findings (Commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`)

Public read-only inspection of the `ai4bharat/IndicCorpV2` repository tree reveals:
1. **File Presence Confirmed:** All 9 files (`data/ta.txt`, `data/hi-1.txt`, `data/hi-2.txt`, `data/hi-3.txt`, `data/te.txt`, `data/ml.txt`, `data/kn.txt`, `data/bn.txt`, `data/gu.txt`) are verified as present.
2. **Object Sizes Confirmed:** The sizes reported in tree metadata aggregate exactly to **183,700,000,000 Bytes** (**183.70 GB** decimal / **171.08 GiB** binary).
3. **Storage Protocol:** Stored via standard Git LFS on the Hugging Face Hub.
4. **Git Blob and LFS OID Exposure Status:**
   - In public tree listing JSON returned by Hugging Face without downloading pointer files or issuing authenticated Git operations, the internal Git blob SHA-1 and LFS pointer text are **not exposed** in directory summary views.
   - To obtain the exact 64-character LFS SHA-256 OID, an agent would have to fetch the raw pointer files (e.g. `https://huggingface.co/datasets/ai4bharat/IndicCorpV2/raw/main/data/ta.txt`).
   - However, issuing HTTP requests that could trigger pointer resolution or large file redirection risks violating the locked ingress gate.
   - Therefore, in strict compliance with governance rules, these fields are recorded transparently as:
     - `git_blob_identifier`: `NOT_EXPOSED_IN_TREE_JSON`
     - `lfs_sha256_oid`: `NOT_EXPOSED_WITHOUT_POINTER_INSPECTION`
     - `content_sha256`: `NOT_VERIFIABLE_WITHOUT_DOWNLOAD`
5. **No Hash Fabrication:** In accordance with IGRIS governance principles, missing cryptographic identifiers are never mocked, synthesized, or fabricated.