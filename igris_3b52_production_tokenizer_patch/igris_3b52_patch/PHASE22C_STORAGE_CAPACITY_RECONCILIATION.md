# PHASE 22C — STORAGE CAPACITY RECONCILIATION & SAFETY MARGIN AUDIT
## Definitive Mathematical Reconciliation of Storage Stages, Headroom vs Safety Margin, and Filesystem Overheads

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22C  
**Execution Mode:** READ-ONLY EVIDENCE AUDIT  
**Status:** RECONCILED & AUDITED  

---

## 1. Executive Summary

Phase 22C resolves the conceptual and arithmetic ambiguities regarding storage capacity across the IGRIS acquisition, preprocessing, tokenization, and pretraining lifecycles.

### Key Conclusions:
1. **Measured Code Ingress Peak:** Strictly **233.70 GB decimal (217.65 GiB binary)** including 50 GB OS headroom. The 26.70 GB buffer is an unverified conservative allowance.
2. **Sequential Pipeline Peak (High-Water Mark):** Strictly **393.70 GB decimal (366.66 GiB binary)** during Stage 2 (Cleaning & Deduplication). This high-water mark is identical regardless of whether the ingress buffer is counted, because ingress completes prior to cleaning.
3. **Conservative Dual-Copy Peak:**
   - Without phantom buffer: **604.40 GB decimal (562.89 GiB binary)**.
   - With phantom buffer (Phase 22B legacy): **631.10 GB decimal (587.76 GiB binary)**.
4. **Safety Margin vs. Headroom Distinction:**
   - **Sequential Remaining Headroom:** $1,000.00 - 393.70 = \mathbf{606.30	ext{ GB (564.66 GiB)}}$. (Operational headroom during normal sequential execution).
   - **Conservative Operational Safety Margin:** $1,000.00 - 604.40 = \mathbf{395.60	ext{ GB (368.43 GiB)}}$ (or $1,000.00 - 631.10 = \mathbf{368.90	ext{ GB (343.56 GiB)}}$).
   - Under no circumstances should the sequential headroom (606.30 GB) be confused with or reported as the conservative operational safety margin (368.90–395.60 GB).
5. **1 TB Recommendation Robustness:** A 1,000 GB provisioned volume (931.32 GiB) remains completely appropriate and safe, providing a $2.54	imes$ safety factor over sequential usage and a $1.58	imes$ to $1.65	imes$ factor over worst-case dual-copy accumulation.

---

## 2. Granular Storage Stage Calculations

### Mathematical Basis
All decimal gigabytes (GB) are defined as $10^9	ext{ bytes}$.  
All binary gibibytes (GiB) are defined as $2^{30} = 1,073,741,824	ext{ bytes}$.  
The exact conversion factor is:
$$	ext{Size}_{	ext{GiB}} = 	ext{Size}_{	ext{GB}} 	imes rac{10^9}{1,073,741,824} pprox 	ext{Size}_{	ext{GB}} 	imes 0.9313225746$$

---

### Stage-by-Stage Breakdown

```
+------------------------------------+--------------------------+--------------------------+--------------------------+
| Pipeline Stage                     | Application Data         | OS System Reserve        | Total Stage Peak         |
+------------------------------------+--------------------------+--------------------------+--------------------------+
| Stage 0: System Idle Baseline      | 0.00 GB (0.00 GiB)       | 50.00 GB (46.57 GiB)     | **50.00 GB** (46.57 GiB) |
| Stage 1A: Ingress (Measured Code)  | 183.70 GB (171.08 GiB)   | 50.00 GB (46.57 GiB)     | **233.70 GB** (217.65 GiB)|
| Stage 1B: Ingress (Conservative)   | 210.40 GB (195.95 GiB)   | 50.00 GB (46.57 GiB)     | **260.40 GB** (242.52 GiB)|
| Stage 2: Cleaning & Deduplication  | 343.70 GB (320.09 GiB)   | 50.00 GB (46.57 GiB)     | **393.70 GB** (366.66 GiB)|
| Stage 3A: Tokenization (Cleaned)   | 162.00 GB (150.87 GiB)   | 50.00 GB (46.57 GiB)     | **212.00 GB** (197.44 GiB)|
| Stage 3B: Tokenization (Raw Kept)  | 345.70 GB (321.96 GiB)   | 50.00 GB (46.57 GiB)     | **395.70 GB** (368.52 GiB)|
| Stage 4: Pretraining (Checkpoints) | 47.00 GB (43.77 GiB)     | 50.00 GB (46.57 GiB)     | **97.00 GB** (90.34 GiB)  |
+------------------------------------+--------------------------+--------------------------+--------------------------+
| WORST-CASE DUAL-COPY (MEASURED)    | 554.40 GB (516.32 GiB)   | 50.00 GB (46.57 GiB)     | **604.40 GB** (562.89 GiB)|
| WORST-CASE DUAL-COPY (PHANTOM)     | 581.10 GB (541.19 GiB)   | 50.00 GB (46.57 GiB)     | **631.10 GB** (587.76 GiB)|
+------------------------------------+--------------------------+--------------------------+--------------------------+
```

---

## 3. Detailed Component Sizing Equations

1. **Raw IndicCorp v2 Corpus (7 Languages, 9 Files):**
   - Tamil (`ta.txt`): 30.50 GB (28.41 GiB)
   - Hindi (`hi-1.txt`, `hi-2.txt`, `hi-3.txt`): 75.90 GB (70.69 GiB)
   - Telugu (`te.txt`): 22.10 GB (20.58 GiB)
   - Malayalam (`ml.txt`): 14.50 GB (13.50 GiB)
   - Kannada (`kn.txt`): 12.80 GB (11.92 GiB)
   - Bengali (`bn.txt`): 16.30 GB (15.18 GiB)
   - Gujarati (`gu.txt`): 11.60 GB (10.80 GiB)
   - **Total Raw Corpus:** $183.70	ext{ GB decimal} = \mathbf{171.08	ext{ GiB binary}}$.

2. **Cleaned and Normalized Text:**
   - Yield after quality filtering, script normalization, and deduplication: ~130.00 GB decimal ($130.00 	imes 10^9 / 1024^3 = \mathbf{121.07	ext{ GiB binary}}$).

3. **Deduplication Index (Bloom Filter / MinHash Hash Tables):**
   - In-memory and on-disk persistent index: 10.00 GB decimal ($10.00 	imes 10^9 / 1024^3 = \mathbf{9.31	ext{ GiB binary}}$).

4. **Tokenized Binary Shards (int32 token IDs / Apache Arrow format):**
   - Compressed int32 token arrays for 3.0B–5.5B tokens: 12.00 GB decimal ($12.00 	imes 10^9 / 1024^3 = \mathbf{11.18	ext{ GiB binary}}$).

5. **Model Pretraining Checkpoints (Rolling Window of 3 Checkpoints):**
   - 3 checkpoints (model weights, optimizer states, lr scheduler states, rng states): 15.00 GB decimal ($15.00 	imes 10^9 / 1024^3 = \mathbf{13.97	ext{ GiB binary}}$).

6. **Scratch / Temporary Sorting / Log Buffer:**
   - Disk workspace for intermediate text chunks and training logs: 20.00 GB decimal ($20.00 	imes 10^9 / 1024^3 = \mathbf{18.63	ext{ GiB binary}}$).

7. **Operating System & System Tooling Reserve:**
   - OS root filesystem, CUDA drivers, virtualenv, system logs: 50.00 GB decimal ($50.00 	imes 10^9 / 1024^3 = \mathbf{46.57	ext{ GiB binary}}$).

---

## 4. Headroom vs. Operational Safety Margin Reconciliation

### Sequential Remaining Headroom
Under strict sequential execution with verified deletion of raw data post-cleaning:
- Peak Storage (Stage 2): $393.70	ext{ GB decimal}$ ($366.66	ext{ GiB binary}$).
- Provisioned Volume: $1,000.00	ext{ GB decimal}$ ($931.32	ext{ GiB binary}$).
- **Sequential Remaining Headroom:**
  $$	ext{Headroom}_{	ext{seq}} = 1,000.00 - 393.70 = \mathbf{606.30	ext{ GB decimal}} = \mathbf{564.66	ext{ GiB binary}}.$$
  *Operational Meaning:* Unused capacity during the peak processing stage when intermediate files are properly cleaned up.

### Conservative Operational Safety Margin
Under worst-case operational conditions where intermediate files are NOT deleted and duplicate raw files accumulate:
- Dual-Copy Peak (Measured Ingress Base): $604.40	ext{ GB decimal}$ ($562.89	ext{ GiB binary}$).
- Dual-Copy Peak (With Phantom Buffer): $631.10	ext{ GB decimal}$ ($587.76	ext{ GiB binary}$).
- **Conservative Operational Safety Margin:**
  $$	ext{Margin}_{	ext{measured}} = 1,000.00 - 604.40 = \mathbf{395.60	ext{ GB decimal}} = \mathbf{368.43	ext{ GiB binary}}.$$
  $$	ext{Margin}_{	ext{phantom}} = 1,000.00 - 631.10 = \mathbf{368.90	ext{ GB decimal}} = \mathbf{343.56	ext{ GiB binary}}.$$
  *Operational Meaning:* The true fail-safe buffer protecting the system from disk exhaustion even if every cleanup step fails completely.

---

## 5. Filesystem Overheads and Usable Capacity Audit

Provisioning a 1,000 GB cloud block volume (1 TB) provides $931.32	ext{ GiB}$ of addressable storage blocks. Filesystem layout imposes structural overheads:

### Linux `ext4` Filesystem:
- **Root Superuser Reserve:** Default `ext4` reserves 5% of volume blocks for the root user (`tune2fs -m 5`):
  $$0.05 	imes 931.32	ext{ GiB} = \mathbf{46.57	ext{ GiB}} = \mathbf{50.00	ext{ GB}}.$$
- **Inodes & Journal Overhead:** Inode tables and journal metadata consume ~1.5% (~$14.00	ext{ GiB}$).
- **Net Usable Unprivileged Space:**
  $$	ext{Usable}_{	ext{ext4}} pprox 931.32 - 46.57 - 14.00 = \mathbf{870.75	ext{ GiB}} pprox \mathbf{935.00	ext{ GB}}.$$
  *(Note: The root reserve can be tuned to 1% via `tune2fs -m 1`, freeing an additional ~37 GiB).*

### NTFS Filesystem:
- **Master File Table (MFT) Zone:** Reserves ~12.5% dynamically, though non-MFT files can allocate within this space if the volume nears full capacity.

### Usable Space Verification:
- Even against unprivileged `ext4` ($870.75	ext{ GiB}$ net usable):
  - Peak Sequential ($366.66	ext{ GiB}$): Leaves $870.75 - 366.66 = \mathbf{504.09	ext{ GiB}}$ ($541.27	ext{ GB}$) free.
  - Worst-Case Dual-Copy ($562.89	ext{ GiB}$): Leaves $870.75 - 562.89 = \mathbf{307.86	ext{ GiB}}$ ($330.56	ext{ GB}$) free.
- **Audit Conclusion:** The 1 TB recommendation is completely robust against filesystem reserve overheads under both operational models.
