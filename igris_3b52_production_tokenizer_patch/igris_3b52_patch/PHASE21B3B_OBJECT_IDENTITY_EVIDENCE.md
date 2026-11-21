# PHASE 21B3B — OBJECT IDENTITY EVIDENCE REPORT
## Forensic Verification of Git Blobs, LFS Pointers, and Cryptographic Hash Layers

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3B  
**Target Repository:** `ai4bharat/IndicCorpV2`  
**Pinned Commit:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`  

---

## 1. Executive Summary & Objective

Phase 21B3B establishes the formal boundary of verifiable metadata for the nine IndicCorp v2 corpus files prior to any authorized data acquisition. Under the IGRIS governance mandate, no external data acquisition or active payload ingestion is permitted while the ingress gate remains **LOCKED**.

This forensic investigation addresses the cryptographic distinction between Git object layers and documents why public directory metadata does not expose Git blob identifiers or Git LFS SHA-256 pointer contents without pointer retrieval or content downloads.

---

## 2. Cryptographic Hash Layer Disambiguation

In Git LFS-backed repositories hosted on the Hugging Face Hub, distinct cryptographic identifiers operate at four separate architectural tiers. These identifiers must not be conflated:

```
+-----------------------------------+-----------+-----------------------------------------------------------------------+
| Architectural Tier                | Algorithm | Scope & Description                                                   |
+-----------------------------------+-----------+-----------------------------------------------------------------------+
| 1. Git Tree Entry SHA             | SHA-1     | 40-character hex hash representing the directory node entry in Git's   |
|                                   |           | internal Merkle tree for commit `984b75b2...`.                        |
| 2. Git Blob Identifier            | SHA-1     | 40-character hex hash of the Git blob object storing the small text   |
|                                   |           | pointer payload (typically ~130 bytes) in Git's object database.      |
| 3. Git LFS Object SHA-256 (OID)   | SHA-256   | 64-character hex hash recorded inside the LFS pointer text file       |
|                                   |           | (e.g., `oid sha256:<hash>`), identifying the large remote object.     |
| 4. Xet Chunk / Block ID           | BLAKE3    | Proprietary chunk hashes used if repository is backed by XetHub       |
|                                   |           | deduplication backend (not applicable to standard LFS repositories).  |
| 5. Downloaded Content SHA-256     | SHA-256   | Cryptographic digest computed over the physical uncompressed bytes     |
|                                   |           | of the target file once transferred and resident on local disk.       |
+-----------------------------------+-----------+-----------------------------------------------------------------------+
```

> [!IMPORTANT]
> A Git blob SHA-1 hash is **not** an LFS SHA-256 OID, and an LFS SHA-256 OID is **not** verifiable until the pointer payload itself is inspected or the file is acquired. Under no circumstances may an agent fabricate, guess, or mock these values.

---

## 3. Upstream Metadata Accessibility Findings

Inspection of the upstream Hugging Face repository API and web tree for `ai4bharat/IndicCorpV2` at pinned commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd` confirms:

1. **Existence and Path Resolution:**  
   All nine expected files exist under `data/`:
   - `data/ta.txt` (Tamil)
   - `data/hi-1.txt`, `data/hi-2.txt`, `data/hi-3.txt` (Hindi shards 1–3)
   - `data/te.txt` (Telugu)
   - `data/ml.txt` (Malayalam)
   - `data/kn.txt` (Kannada)
   - `data/bn.txt` (Bengali)
   - `data/gu.txt` (Gujarati)

2. **Declared Object Sizes:**  
   Public tree metadata provides declared file sizes summing to **183,700,000,000 bytes** (**183.70 GB** decimal / **171.08 GiB** binary).

3. **Inaccessibility of Git Blob SHA-1 and LFS Pointer OID:**  
   - Hugging Face directory tree API endpoints return file name, file size, LFS flag (`lfs: true`), and type (`file`). They do **not** serialize the internal Git blob SHA-1 or the inner text contents of the LFS pointer file.
   - Fetching the pointer text (e.g. via raw endpoint) would require issuing network HTTP requests against upstream remote endpoints. Issuing automated network fetches against unapproved production targets while the ingress gate is `LOCKED` violates the controlled acquisition governance protocol.
   - Running Git plumbing commands (`git ls-tree`, `git cat-file`) requires a local cloned Git repository database, which does not exist in the current read-only workspace.

4. **Forensic Classification:**  
   In strict compliance with governance rules, the verification state of all nine objects is formally classified as:
   - `git_tree_entry_status`: `NOT_EXPOSED_IN_TREE_JSON`
   - `git_blob_identifier`: `NOT_EXPOSED_IN_TREE_JSON`
   - `lfs_pointer_status`: `NOT_EXPOSED_WITHOUT_POINTER_INSPECTION`
   - `lfs_sha256_oid`: `NOT_EXPOSED_WITHOUT_POINTER_INSPECTION`
   - `content_sha256_status`: `NOT_VERIFIABLE_WITHOUT_DOWNLOAD`
   - `identity_verification_classification`: `PARTIAL_SIZE_ONLY` (also recorded as `METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED`).

> [!WARNING]
> An object whose cryptographic pointer OID is unexposed must **never** be labeled `FULLY_IDENTITY_VERIFIED`. It is verified solely at the level of public path existence and declared byte size.

---

## 4. Zero Hash Fabrication Invariant

The IGRIS architecture operates under the rule that absence of evidence is recorded truthfully. Missing hashes are explicitly designated `NOT_EXPOSED_IN_TREE_JSON` or `NOT_EXPOSED_WITHOUT_POINTER_INSPECTION`. No cryptographic hash has been synthesized, approximated, or mocked.
