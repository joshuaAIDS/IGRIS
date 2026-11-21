# PHASE 22D — FILESYSTEM CAPACITY ANALYSIS & PLANNING PROJECTIONS
## Comparative Filesystem Overheads, Reserved Blocks, and 1 TB Volume Allocation Validation

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22D  
**Execution Mode:** READ-ONLY AUDIT AND PLANNING PROJECTION  
**Status:** EVALUATED & VALIDATED  

---

## 1. Explicit Planning Scenario Classification

In strict accordance with Phase 22D instructions, all filesystem capacity, reserved block, and metadata overhead calculations in this document are explicitly classified as:
$$\mathbf{PLANNING\ SCENARIOS\ (PROJECTIONS)}$$
Because no cloud infrastructure has been provisioned and no cloud expenditure committed, these figures represent mathematically rigorous projections based on standard filesystem structural behaviors, rather than measured host filesystem telemetry.

---

## 2. Comparative Filesystem Overhead Register

### Provisioned Volume Baseline:
- **Nominal Size:** 1,000.00 GB decimal ($10^{12} = 1,000,000,000,000	ext{ bytes}$).
- **Binary Volume Size:** **931.32 GiB** ($1,000,000,000,000 / 1,073,741,824	ext{ bytes}$).

```
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------+
| Filesystem Planning Parameter      | Scenario A: ext4 Default | Scenario B: ext4 Tuned   | Scenario C: Linux XFS    | Scenario D: Windows NTFS |
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------+
| Target Operating System            | Linux (Ubuntu/Debian)    | Linux (Ubuntu/Debian)    | Linux (RHEL/Rocky/Fedora)| Microsoft Windows 11     |
| Provisioned Volume Size            | 1,000.00 GB (931.32 GiB) | 1,000.00 GB (931.32 GiB) | 1,000.00 GB (931.32 GiB) | 1,000.00 GB (931.32 GiB) |
| Superuser Reserved Blocks          | **5.0%** (Default)       | **1.0%** (`tune2fs -m 1`)| **0.0%** (No root reserve| **0.0%** (Dynamic MFT)   |
| Reserved Capacity                  | 46.57 GiB (50.00 GB)     | 9.31 GiB (10.00 GB)      | 0.00 GiB (0.00 GB)       | 0.00 GiB (0.00 GB)       |
| Inode & Journal Metadata Overhead  | ~1.5% (13.97 GiB / 15 GB)| ~1.5% (13.97 GiB / 15 GB)| ~0.5% (4.66 GiB / 5.0 GB)| ~1.0% (9.31 GiB / 10 GB) |
| Total Structural Overhead          | **60.54 GiB** (65.00 GB) | **23.28 GiB** (24.98 GB) | **4.66 GiB** (5.00 GB)   | **9.31 GiB** (10.00 GB)  |
| Unprivileged Usable Capacity       | **870.78 GiB** (935.00 GB| **908.04 GiB** (975.02 GB| **926.66 GiB** (995.00 GB| **922.01 GiB** (990.00 GB|
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------+
| Sequential Peak Usage (Stage 5)    | 366.66 GiB (393.70 GB)   | 366.66 GiB (393.70 GB)   | 366.66 GiB (393.70 GB)   | 366.66 GiB (393.70 GB)   |
| Sequential Unprivileged Free Space | **504.12 GiB** (541.30 GB| **541.38 GiB** (581.32 GB| **560.00 GiB** (601.30 GB| **555.35 GiB** (596.30 GB|
| Conservative Peak (Stage 10 Base)  | 562.89 GiB (604.40 GB)   | 562.89 GiB (604.40 GB)   | 562.89 GiB (604.40 GB)   | 562.89 GiB (604.40 GB)   |
| Conservative Unprivileged Free Space| **307.89 GiB** (330.60 GB| **345.15 GiB** (370.62 GB| **363.77 GiB** (390.60 GB| **359.12 GiB** (385.60 GB|
| Conservative Peak (Stage 10 Full)  | 572.20 GiB (614.40 GB)   | 572.20 GiB (614.40 GB)   | 572.20 GiB (614.40 GB)   | 572.20 GiB (614.40 GB)   |
| Conservative Unprivileged Free Space| **298.58 GiB** (320.60 GB| **335.84 GiB** (360.62 GB| **354.46 GiB** (380.60 GB| **349.81 GiB** (375.60 GB|
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------+
```

---

## 3. Detailed Filesystem Overhead Analysis

### 1. Scenario A: Standard Linux `ext4` (Default 5% Reserve)
- `mke2fs` defaults to reserving 5% of filesystem blocks for the `root` user (`uid 0`) to prevent system fragmentation and allow root daemons to function during full-disk emergencies.
- On a 1 TB volume, this static reservation locks out **46.57 GiB (50.00 GB)** from unprivileged application users.
- Inode tables (allocated at a standard ratio of 1 inode per 16 KB) plus a 1 GB ext4 journal consume an additional ~1.5% (**13.97 GiB / 15.00 GB**).
- Resulting net unprivileged usable space is **870.78 GiB (935.00 GB)**.

### 2. Scenario B: Tuned Linux `ext4` (1% Reserve via `tune2fs -m 1`)
- For non-root dedicated data volumes, best practice in machine learning infrastructure is reducing the root reservation to 1% (or 0%):
  `sudo tune2fs -m 1 /dev/sdX`
- This releases **37.26 GiB (40.00 GB)** back to the unprivileged dataset processing user, expanding net usable capacity to **908.04 GiB (975.02 GB)**.

### 3. Scenario C: Linux `XFS` (Standard Data Volume Configuration)
- `XFS` allocates inodes dynamically as needed rather than reserving a static inode table at format time.
- `XFS` contains no root reserved-block concept; 100% of non-metadata blocks are immediately usable by unprivileged processes.
- Metadata overhead is limited to dynamic b-tree allocations and the internal log (~0.5% = **4.66 GiB**).
- Resulting net usable space is **926.66 GiB (995.00 GB)**.

### 4. Scenario D: Windows `NTFS`
- NTFS dynamically expands its Master File Table (MFT) zone (typically reserving ~12.5% of cluster space). However, if user files fill the remainder of the volume, NTFS automatically allocates user data within the MFT zone without blocking operations. Static volume metadata overhead is ~1.0% (**9.31 GiB**).

---

## 4. Final 1 TB Volume Allocation Sign-Off

### Evaluation of 1 TB Recommendation:
1. **Under Sequential Happy-Path Execution ($366.66	ext{ GiB}$ peak):**
   - The provisioned 1 TB volume provides **$504.12	ext{ to }560.00	ext{ GiB}$** of net unprivileged free cushion across all filesystems ($2.54	imes$ capacity factor).
2. **Under Cumulative Worst-Case Zero-Cleanup ($562.89–572.20	ext{ GiB}$ peak):**
   - Even in the absolute worst-case scenario (duplicate raw download copy + raw retained + cleaned retained + dedup index retained + token shards + checkpoints + logs + scratch), net unprivileged free space remains between **$298.58	ext{ GiB}$** (ext4 default) and **$363.77	ext{ GiB}$** (XFS).
3. **Double-Counting Avoidance:**
   - In all calculations, the 50.00 GB OS headroom is treated as an operational requirement within the volume, and filesystem structural reserves (46.57 GiB on ext4) are deducted from physical capacity, ensuring that system reserves are never counted twice.

### **Final Determination:**
The **1 TB (1,000 GB provisioned / 931.32 GiB)** recommendation remains **COMPLETELY APPROPRIATE, ROBUST, AND ECONOMICALLY OPTIMAL** under all evaluated filesystem scenarios.
