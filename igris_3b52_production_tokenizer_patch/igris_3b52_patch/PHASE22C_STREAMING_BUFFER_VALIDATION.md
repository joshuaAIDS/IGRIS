# PHASE 22C — STREAMING BUFFER VALIDATION & CODE LIFECYCLE AUDIT
## Physical Code Path Inspection of SecureAcquisitionEngine, Transfer Buffers, Atomic Rename, and Storage Footprint Reality

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22C  
**Execution Mode:** READ-ONLY EVIDENCE AUDIT  
**Status:** VALIDATED & AUDITED  

---

## 1. Executive Summary & Core Physical Finding

Phase 22B identified a 26.70 GB transient shard buffer based on the single largest Hindi IndicCorp v2 shard (`data/hi-1.txt` or `data/hi-2.txt`, at ~26.70 GB decimal / 24.87 GiB binary). In Phase 22B, this buffer was assumed to be required on disk alongside the raw corpus during download, decompression, or in-flight processing.

A line-by-line inspection of the actual implementation in `scripts/secure_acquisition_engine.py` and `scripts/dataset_pipeline.py` reveals the following physical realities:
1. **No Duplicate Shard Copy:** The acquisition engine streams incoming network packets in bounded 64 KiB chunks directly into a `.part` file in quarantine. Upon download completion and cryptographic hash verification, the `.part` file is promoted to its final destination path via `os.replace()` (an atomic in-place filesystem rename). At no point does a second full-size copy of any shard exist simultaneously on disk.
2. **RAM Transfer Buffer:** Resident memory allocation during transfer is strictly bounded to `chunk_size = 65536` bytes (64 KiB), reused in a streaming loop.
3. **Zero Archive Workspace:** IndicCorp v2 corpus objects are raw uncompressed plain text files (`data/ta.txt`, `data/hi-[1-3].txt`, etc.). There is no `.tar.gz` or `.zip` extraction workspace.
4. **Zero Checksum Disk Workspace:** Cryptographic SHA-256 calculation occurs in RAM during the chunk streaming loop; no intermediate checksum file or temporary copy is created.
5. **Formal Classification:** The 26.70 GB buffer is categorized as an **UNVERIFIED CONSERVATIVE ALLOWANCE**, not a measured physical requirement of the codebase.

---

## 2. Granular 7-Component Code Path Breakdown

| # | Pipeline Component | Inspected Code Path | Expected Maximum Size | Physical Storage Footprint & Lifecycle Behavior |
|---|---|---|---|---|
| **1** | **Network Transfer Buffer (RAM)** | `scripts/secure_acquisition_engine.py`<br>Line 326 (`chunk_size: int = 65536`),<br>Line 453 (`chunk = response.read(chunk_size)`) | **64 KiB** (65,536 bytes) in RAM | Transient RAM buffer reused per HTTP chunk. Zero bytes written to disk outside the `.part` file. |
| **2** | **Temporary `.part` File (Disk)** | `scripts/secure_acquisition_engine.py`<br>Line 349 (`part_path = Path(str(dest) + ".part")`),<br>Line 442, 463 (`part_file.write(chunk)`) | **26.70 GB** (decimal)<br>**24.87 GiB** (binary)<br>*(Largest shard: `hi-1.txt`)* | Written directly inside quarantine staging. While `.part` is being written, the final file does NOT exist yet. |
| **3** | **Final Quarantined File** | `scripts/secure_acquisition_engine.py`<br>Line 481 (`os.replace(part_path, dest_path)`) | **26.70 GB** (decimal)<br>**24.87 GiB** (binary)<br>*(Total 183.70 GB for all 9 shards)* | Atomic filesystem rename (POSIX `rename` / Win32 `MoveFileEx`). Modifies filesystem directory pointer (inode/MFT). Copies 0 bytes. At the instant `dest_path` appears, `.part` disappears. |
| **4** | **Archive Extraction Workspace** | `scripts/dataset_pipeline.py`<br>Lines 374–377 (`ext in (".txt", ...)`),<br>Upstream IndicCorp v2 repository | **0 bytes** | IndicCorp v2 corpus objects are raw uncompressed text files (`data/*.txt`). No archive decompression (`tar`/`zip`/`gzip`) is performed. |
| **5** | **Checksum Workspace** | `scripts/secure_acquisition_engine.py`<br>Line 439 (`sha256_hasher = hashlib.sha256()`),<br>Line 462 (`sha256_hasher.update(chunk)`),<br>Line 465 (`computed_hash = sha256_hasher.hexdigest()`) | **0 bytes on disk**<br>*(~108 bytes internal state in RAM)* | Computed completely in-memory during chunk streaming. Zero disk storage required. |
| **6** | **Transformation Output (Cleaning)** | `scripts/dataset_pipeline.py`<br>Lines 228–407,<br>`quality_filter.py`, `duplicate_detector.py` | **130.00 GB** (decimal)<br>**121.07 GiB** (binary) | Cleaned, normalized, deduplicated text written to `cleaned/` directory. Co-exists on disk with raw corpus (183.70 GB) until raw data is purged. |
| **7** | **Additional Duplicate Copies** | Inspected entire repository codebase | **0 bytes** | The tested acquisition engine writes directly to `quarantine/raw/<file>.part` and renames to `quarantine/raw/<file>`. No secondary download directory, browser cache, or staging copy exists in code. |

---

## 3. Physical Storage Reality vs. Conservative Allowance

### Ingress Peak Comparison (Stage 1)
```
+------------------------------------+--------------------------+--------------------------+
| Metric                             | Measured Code Reality    | Conservative Allowance   |
+------------------------------------+--------------------------+--------------------------+
| Raw Corpus Ingress (9 shards)      | 183.70 GB (171.08 GiB)   | 183.70 GB (171.08 GiB)   |
| Streaming Ingress Buffer           | 0.00 GB (64 KiB in RAM)  | 26.70 GB (24.87 GiB)     |
| Subtotal Application Ingress       | **183.70 GB** (171.08 GiB)| **210.40 GB** (195.95 GiB)|
| Operating System Headroom          | 50.00 GB (46.57 GiB)     | 50.00 GB (46.57 GiB)     |
+------------------------------------+--------------------------+--------------------------+
| TOTAL INGRESS PEAK STORAGE         | **233.70 GB** (217.65 GiB)| **260.40 GB** (242.52 GiB)|
+------------------------------------+--------------------------+--------------------------+
| Status                             | VERIFIED FROM CODE PATHS | UNVERIFIED SAFETY MARGIN |
+------------------------------------+--------------------------+--------------------------+
```

### Filesystem Atomic Rename Mechanics
In both POSIX (`rename(2)`) and Windows (`MoveFileExW` with `MOVEFILE_REPLACE_EXISTING`), an atomic rename within the same filesystem volume performs an in-place metadata update:
1. A new directory entry pointer is created for `dest_path` pointing to the existing inode / file record cluster chain.
2. The old directory entry pointer for `part_path` is unlinked.
3. No physical data blocks are copied or duplicated on the storage device.
4. Transient disk space consumed during the promotion is literally zero bytes.

---

## 4. Operational Classification and Audit Determination

1. **Measured Requirement:** The measured physical capacity required for raw ingress is strictly **183.70 GB decimal (171.08 GiB binary)** plus 50 GB OS headroom = **233.70 GB decimal (217.65 GiB binary)**.
2. **Conservative Planning Allowance:** Retaining a 26.70 GB buffer provides a safety margin for non-standard operational eventualities (such as temporary local tool logs, accidental interrupted download residuals, or parallel uncompressed scratch buffers).
3. **Formal Verdict:** The 26.70 GB figure is **NOT a physical code requirement**; it is classified as an **UNVERIFIED CONSERVATIVE ALLOWANCE**. Both calculations are preserved side-by-side in Phase 22C documentation.
