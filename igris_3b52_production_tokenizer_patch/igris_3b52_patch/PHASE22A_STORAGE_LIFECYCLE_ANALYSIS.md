# PHASE 22A — STORAGE LIFECYCLE & ARITHMETIC RECONCILIATION
## Rigorous Recalculation of Storage Tiers, Simultaneous vs. Sequential Footprints, and Resolution of Phase 22 Inconsistencies

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22A  
**Status:** FULLY RECONCILED  

---

## 1. Executive Summary

Phase 22A resolves all numerical inconsistencies and accounting ambiguities identified in the Phase 22 storage planning package.

### Critical Reconciliations Established:
1. **Resolution of the 532.40 GB vs. 600.70 GB Discrepancy:**
   - In Phase 22, the reported cumulative peak of **532.40 GB** was calculated as:
     $$\text{Peak}_{\text{P22}} = 183.70\text{ (raw)} + 183.70\text{ (quarantine duplicate)} + 130.00\text{ (cleaned)} + 20.00\text{ (tokens)} + 15.00\text{ (checkpoints)} = 532.40\text{ GB}$$
   - However, the individual storage components listed across `PHASE22_STORAGE_REQUIREMENTS.csv` totaled **600.70 GB**:
     $$\text{Sum}_{\text{P22 CSV}} = 183.70\text{ (raw)} + 183.70\text{ (quarantine)} + 26.30\text{ (buffer)} + 130.00\text{ (clean)} + 12.00\text{ (tokens)} + 15.00\text{ (ckpts)} + 50.00\text{ (OS)} = 600.70\text{ GB}$$
   - **Reconciliation:** The 68.30 GB delta ($600.70 - 532.40$) arose because the 532.40 GB formula omitted the **50.00 GB OS headroom** and the **26.30 GB extraction/checksum buffer**, while budgeting 20.00 GB for tokens instead of the 12.00 GB specified in the CSV ($50.00 + 26.30 - 8.00 = 68.30\text{ GB}$).
2. **Identification of False Duplication (Raw vs. Quarantine):**
   - Both the 532.40 GB and 600.70 GB figures double-counted the raw corpus by assuming that `Raw Downloaded Corpus` (183.70 GB) and `Quarantine Staging` (183.70 GB) are distinct simultaneous physical copies.
   - Under `SecureAcquisitionEngine`, files are streamed **directly into quarantine**. Therefore, in an in-place architecture, this is **one single physical copy** (183.70 GB), not two (367.40 GB).
3. **Four Authoritative Capacity Metrics Formulated:**
   - **A. Minimum Theoretical Capacity:** **260.00 GB decimal (242.14 GiB binary)**.
   - **B. Peak Simultaneous Capacity (In-Place):** **447.00 GB decimal (416.30 GiB binary)** (or 630.70 GB if uncleaned scratch and duplicate copies coexist).
   - **C. Sequential Processing Capacity (with Verified Cleanup):** **393.70 GB decimal (366.66 GiB binary)** (high-water mark during Stage 2 cleaning).
   - **D. Recommended Provisioning Capacity (1 TB Standard Volume):** **1,000.00 GB decimal (931.32 GiB binary)**, providing an operational safety margin of **2.54x** over sequential peak.

---

## 2. Granular Breakdown of the Nine Storage Components

```
+----+----------------------------------+-----------+-----------+-----------------------+---------------------------+-----------------------+
| #  | Component Name                   | Dec (GB)  | Bin (GiB) | Stage Nature          | Lifecycle Timing          | Deletable Post-Verify |
+----+----------------------------------+-----------+-----------+-----------------------+---------------------------+-----------------------+
| 1  | Raw Downloaded Corpus (9 files)  | 183.70    | 171.08    | Source Ingress Text   | Simultaneous Ingress      | Yes (after cleaning)  |
| 2  | Quarantine Staging Directory     | 183.70    | 171.08    | Staging Container     | In-place / Duplicate copy | Yes (on unquarantine) |
| 3  | Extraction & Validation Buffer   | 26.30     | 24.49     | Transient Hash Buffer | Ephemeral validation      | Yes (immediate)       |
| 4  | Cleaned & Deduplicated Corpus    | 130.00    | 121.07    | Filtered Text Corpus  | Simultaneous with Raw     | Yes (post-tokenizing) |
| 5  | Deduplication Index & MinHash    | 10.00     | 9.31      | Metadata Hash Tables  | Simultaneous during Dedup | Yes (post-dedup)      |
| 6  | Tokenized Shards (uint16 IDs)    | 12.00     | 11.18     | Binary Training Shards| Persistent for Training   | No (retained)         |
| 7  | Training Checkpoints (10 ckpts)  | 15.00     | 13.97     | Model & Optimizer State| Accumulates in Training  | Rolling purge (save 1)|
| 8  | Scratch & Sorting Working Space  | 20.00     | 18.63     | Intermediate IO Buffer| Ephemeral per process     | Yes (automatic)       |
| 9  | OS Headroom & Swap Buffer        | 50.00     | 46.57     | System Reserve        | Permanent Host Headroom   | No (system requisite) |
+----+----------------------------------+-----------+-----------+-----------------------+---------------------------+-----------------------+
```

---

## 3. Sequential Lifecycle Progression & Disk Footprint

When executed sequentially with immediate verified cleanup, disk usage evolves through five distinct phases:

### Phase 1: Ingress & Quarantine Validation
- Raw files downloaded directly into quarantine + streaming validation buffer + OS reserve:
  $$\text{Disk}_{\text{Phase 1}} = 183.70\text{ (raw/quarantine)} + 26.30\text{ (validation buffer)} + 50.00\text{ (OS)} = \mathbf{260.00\text{ GB (242.14 GiB)}}.$$
- *Cleanup:* Purge transient validation buffer (-26.30 GB). Resident: 183.70 GB raw + 50.00 GB OS = 233.70 GB.

### Phase 2: Cleaning & Deduplication (High-Water Mark)
- Raw files read while generating cleaned text, MinHash signatures, and sorting scratch:
  $$\text{Disk}_{\text{Phase 2}} = 183.70\text{ (raw)} + 130.00\text{ (clean)} + 10.00\text{ (dedup)} + 20.00\text{ (scratch)} + 50.00\text{ (OS)} = \mathbf{393.70\text{ GB (366.66 GiB)}}.$$
- *High-Water Point:* This is the absolute peak sequential requirement of the entire pipeline.
- *Cleanup:* Upon certifying cleaned text checksums, immediately purge raw files (-183.70 GB), dedup indexes (-10.00 GB), and scratch (-20.00 GB).
- Resident remaining: 130.00 GB clean + 50.00 GB OS = 180.00 GB.

### Phase 3: Tokenization
- Cleaned text streamed through Candidate A tokenizer to write memory-mapped uint16 binary shards:
  $$\text{Disk}_{\text{Phase 3}} = 130.00\text{ (clean)} + 12.00\text{ (token shards)} + 20.00\text{ (scratch)} + 50.00\text{ (OS)} = \mathbf{212.00\text{ GB (197.44 GiB)}}.$$
- *Cleanup:* Purge cleaned text (-130.00 GB) and scratch (-20.00 GB).
- Resident remaining: 12.00 GB token shards + 50.00 GB OS = 62.00 GB.

### Phase 4: Model Pretraining & Checkpointing
- Model pretraining executes on token shards, accumulating rolling checkpoints:
  $$\text{Disk}_{\text{Phase 4}} = 12.00\text{ (token shards)} + 15.00\text{ (10 checkpoints)} + 20.00\text{ (scratch)} + 50.00\text{ (OS)} = \mathbf{97.00\text{ GB (90.34 GiB)}}.$$

---

## 4. Reconciliation with Local Workstation Physical Limits

```
+-----------------------------------+-------------------+-------------------+-------------------------------------------+
| Capacity Metric                   | Decimal (GB)      | Binary (GiB)      | Comparison vs. Local Free SSD (80.51 GiB) |
+-----------------------------------+-------------------+-------------------+-------------------------------------------+
| Minimum Theoretical Capacity      | 260.00 GB         | 242.14 GiB        | DEFICIT: -161.63 GiB (3.0x local space)   |
| Peak Sequential Processing        | 393.70 GB         | 366.66 GiB        | DEFICIT: -286.15 GiB (4.6x local space)   |
| Peak Simultaneous (In-Place)      | 447.00 GB         | 416.30 GiB        | DEFICIT: -335.79 GiB (5.2x local space)   |
| Peak Simultaneous (Naive Dual)    | 630.70 GB         | 587.39 GiB        | DEFICIT: -506.88 GiB (7.3x local space)   |
| Recommended Cloud Volume (1 TB)   | 1,000.00 GB       | 931.32 GiB        | SURPLUS: +564.66 GiB over sequential peak |
| Measured Local Free SSD (C:\)     | 86.45 GB          | 80.51 GiB         | INSUFFICIENT FOR ANY PRODUCTION STAGE     |
+-----------------------------------+-------------------+-------------------+-------------------------------------------+
```

### Forensic Conclusion:
Under no execution strategy (even aggressive sequential unlinking) can the raw IndicCorp v2 corpus be ingested onto the host workstation's local SSD. A dedicated **1 TB cloud volume** is mathematically mandatory.
