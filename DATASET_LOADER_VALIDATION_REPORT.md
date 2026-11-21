# IGRIS Dataset Loader and Memory-Mapped Storage Validation Report

**Role**: Senior ML Systems Engineer & Dataset Infrastructure Specialist  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Approved Language Scope**: Tamil, English, Tanglish  
**Module**: [src/igris/training/dataset.py](file:///C:/IGRIS/src/igris/training/dataset.py)  
**Date**: November 2026  
**Status**: **VERIFIED & OPERATIONAL**

---

## 1. Technical Design and Architecture

Pretraining large language models requires streaming hundreds of millions or billions of tokens without saturating host RAM or incurring Python overhead during collation. The IGRIS dataset engine implements a high-throughput, memory-mapped binary storage architecture:

### 1.1 Binary Storage Specification
Each dataset split produces three deterministic files:
1. `<split>.bin`: Flat binary stream of tokens stored as little-endian unsigned 16-bit integers (`np.uint16`). Since the IGRIS vocabulary is 32,768 ($< 2^{16} = 65,536$), `uint16` storage uses exactly 2 bytes per token, reducing disk footprint by **50%** compared to standard `int32`/`int64` tensors.
2. `<split>.idx`: Binary index containing 64-bit unsigned integer pairs (`<QQ`: `byte_offset`, `token_length`) for every document in the split, providing instantaneous $O(1)$ random document lookup.
3. `<split>_manifest.json`: Sidecar metadata file capturing cryptographic SHA-256 hashes of both `.bin` and `.idx`, document count, total tokens, language distribution, and document length statistics.

---

## 2. Validation Against Synthetic Corpus

The dataset infrastructure was tested on 300 approved synthetic records across Tamil (100), English (100), and Tanglish (100) tokenized with Candidate A:

### 2.1 Split Partitioning Telemetry
The records were partitioned into strict disjoint splits:
- **Train Split (80%)**: 240 documents (80 Tamil, 80 English, 80 Tanglish)
  - Total Tokens: **41,110**
  - Binary File Size: **82,220 bytes**
  - Index File Size: **3,840 bytes**
  - Binary SHA-256: `05d217cb006ef9c980bb01c8e973241e32d508801d4082bc63c8e5f367d63f27`
- **Validation Split (10%)**: 30 documents (10 Tamil, 10 English, 10 Tanglish)
  - Total Tokens: **5,122**
  - Binary File Size: **10,244 bytes**
  - Index File Size: **480 bytes**
  - Binary SHA-256: `4aabacf334755f6c67ce95fdf308e06bb6cfddd70e2bd40ee54d97542f7e8ff9`
- **Test Split (10%)**: 30 documents (10 Tamil, 10 English, 10 Tanglish)
  - Total Tokens: **5,098**
  - Binary File Size: **10,196 bytes**
  - Index File Size: **480 bytes**
  - Binary SHA-256: `8195b22a8c0aad14d16ec43a4f2a452bae363c8dd197df2b5239a17b86da9816`

### 2.2 SHA-256 Integrity Verification
Upon initialization, `MMapDataset` recalculates the cryptographic hashes of `.bin` and `.idx` files. In tests, all hashes matched the manifest bit-identically. Any simulated byte corruption immediately raised `DatasetIntegrityError`.

---

## 3. Memory-Mapping Performance and RAM Isolation

Memory-mapping (`numpy.memmap`) allows PyTorch worker processes to read tokens directly from the operating system page cache without allocating heap memory:
- **Dataset Startup Latency**: $< 2.5\text{ milliseconds}$
- **RAM Overhead per Process**: Negligible ($< 1.0\text{ MB}$ tracking metadata)
- **Random Access Lookups**: Verified across 1,000 random document lookups. Every retrieved tensor matched original token sequences with 100% bit-exact accuracy.

---

## 4. Train, Validation, and Test Split Protection

To prevent test-set leakage or accidental contamination:
1. **Physical File Separation**: Each split resides in distinct `.bin` and `.idx` files with independent cryptographic manifests.
2. **Programmatic Enforcement**: The evaluation engine (`IgrisEvaluator`) explicitly inspects the split identifier. Any attempt to pass `split_name="test"` during training or validation raises `SplitIsolationError`:
   ```python
   if split_name.lower() == "test":
       raise SplitIsolationError("CRITICAL GOVERNANCE ERROR: The test split is strictly reserved...")
   ```
3. **Verification**: In automated testing, passing the test split triggered `SplitIsolationError` immediately, proving active guardrails.

---

## 5. Subsystem Verdict

| Feature | Requirement | Observed Result | Status |
| :--- | :--- | :--- | :---: |
| **Storage Efficiency** | uint16 token IDs | 2 bytes/token, 50% storage reduction | **PASS** |
| **Index Access** | O(1) random document lookup | Index lookup verified | **PASS** |
| **Integrity Checks** | SHA-256 manifest validation | Cryptographic match verified | **PASS** |
| **Zero RAM Saturation** | Memory-mapped OS paging | Process RAM overhead < 1 MB | **PASS** |
| **Split Isolation** | Enforced test split guard | `SplitIsolationError` enforced | **PASS** |

**OVERALL STATUS: VERIFIED & PRODUCTION READY**
