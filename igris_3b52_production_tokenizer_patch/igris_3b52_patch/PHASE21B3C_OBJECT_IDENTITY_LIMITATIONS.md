# PHASE 21B3C — OBJECT IDENTITY LIMITATIONS REPORT
## Technical Limitations of Read-Only Public Metadata Inspection for Git LFS Datasets

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3C  
**Target Repository:** `ai4bharat/IndicCorpV2`  
**Pinned Commit:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`  

---

## 1. Executive Summary

This report establishes the technical and cryptographic boundary of accessible evidence for the nine IndicCorp v2 corpus files prior to authorized data acquisition. Under the governing constraints of Phase 21B3C, the ingress gate remains strictly **LOCKED**, and zero bytes of corpus payloads may be downloaded or staged.

Consequently, while public repository metadata confirms the existence, exact file paths, and declared sizes of all nine objects, the underlying cryptographic hashes (Git blob SHA-1, LFS pointer SHA-256 OID, downloaded payload SHA-256) remain **unavailable without authorized acquisition**.

---

## 2. Technical Limitations by Architectural Layer

```
+-----------------------------------+-----------------------+-----------------------------------------------------------------------+
| Layer                             | Status                | Technical Reason for Inaccessibility                                  |
+-----------------------------------+-----------------------+-----------------------------------------------------------------------+
| 1. Git Tree Entry Identifier      | NOT_EXPOSED           | Hugging Face directory JSON endpoints return file objects without     |
|                                   |                       | exposing internal 40-character Git tree SHA-1 hashes.                 |
| 2. Git Blob Identifier            | NOT_EXPOSED           | The blob SHA-1 of the pointer text file resides inside Git's object   |
|                                   |                       | database, inaccessible without a local Git clone or low-level API.    |
| 3. LFS Pointer SHA-256 OID        | UNAVAILABLE           | The 64-character SHA-256 payload digest is stored inside the raw      |
|                                   |                       | pointer file text; fetching raw text requires external HTTP requests. |
| 4. Xet Chunk / Block ID           | NOT_APPLICABLE        | The repository uses standard Git LFS, not Hugging Face XetHub.        |
| 5. Downloaded Payload SHA-256     | UNAVAILABLE           | Requires transferring 183.70 GB of uncompressed text to local disk,   |
|                                   |                       | which is strictly prohibited while the ingress gate is LOCKED.        |
+-----------------------------------+-----------------------+-----------------------------------------------------------------------+
```

---

## 3. Explicit Proscription Against Hash Fabrication

In compliance with IGRIS integrity standards:
- No cryptographic hash has been synthesized, guessed, or mocked.
- Missing values are explicitly recorded as:
  - `git_blob_sha1`: `NOT_EXPOSED_IN_TREE_JSON`
  - `lfs_pointer_sha256_oid`: `NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD`
  - `downloaded_payload_sha256`: `NOT_VERIFIABLE_WITHOUT_DOWNLOAD`
- All objects are classified under:
  **PARTIAL_SIZE_ONLY / METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED**  
  $$\mathbf{PARTIAL\_SIZE\_ONLY\ /\ METADATA\_ACCESSIBLE\_PAYLOAD\_UNINSPECTED}$$
- No object is classified as `FULLY_IDENTITY_VERIFIED`.

---

## 4. Verification Prerequisites for Future Acquisition

To transition these objects from `PARTIAL_SIZE_ONLY` to `FULLY_IDENTITY_VERIFIED`, a future authorized acquisition phase must:
1. Obtain explicit owner authorization to unlock the ingress gate for specific source IDs.
2. Ingest the Git LFS pointer files into an isolated quarantine staging environment.
3. Parse the LFS pointer text to extract the authoritative 64-character `oid sha256:<hash>` and verify declared size.
4. Stream or download the remote payload directly into quarantine while verifying the incoming stream against the pointer OID.
5. Compute the final bitwise SHA-256 of the uncompressed corpus files on local disk prior to quarantine release.
