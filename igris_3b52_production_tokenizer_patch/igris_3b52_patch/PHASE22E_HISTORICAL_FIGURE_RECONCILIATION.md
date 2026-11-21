# PHASE 22E — HISTORICAL CAPACITY FIGURE RECONCILIATION & FORENSIC AUDIT
## Reconciliation of Dual-Copy Peaks, Shard Allowances, and Historical Storage Benchmarks

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22E  
**Execution Mode:** READ-ONLY FORENSIC AUDIT AND DOCUMENTATION CORRECTION  
**Status:** RECONCILED & AUDITED  

---

## 1. Executive Summary

Phase 22E resolves the remaining arithmetic and lifecycle ambiguities in the IGRIS storage capacity model, providing an exact mathematical accounting of the 27.00 GB difference between Stage 9 and the 604.40 GB base peak, a multi-scenario audit of the 26.70 GB allowance, and a formal disposition register for all historical capacity figures.

---

## 2. Reconciliation of Stage 9 vs. Stage 10 vs. 604.40 GB Base

```
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| Storage Scenario Metric            | Application Subtotal     | OS Reserve (50.00 GB)    | Total Storage Peak       | Detailed Component Composition                         |
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **Stage 9: Dual-Copy Ingress Peak**| **527.40 GB** (491.18 GiB)| 50.00 GB (46.57 GiB)     | **577.40 GB** (537.75 GiB)| Raw ($183.70) + DupRaw ($183.70) + Cleaned ($130.00)   |
| *(Active during Dedup Peak)*       |                          |                          |                          | + Index ($10.00) + Scratch ($20.00)                    |
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **Dual-Copy Zero-Cleanup Base**    | **554.40 GB** (516.33 GiB)| 50.00 GB (46.57 GiB)     | **604.40 GB** (562.89 GiB)| Stage 9 Components ($507.40) + Token Shards ($12.00)   |
| *(Logs absorbed in 20 GB scratch)* |                          |                          |                          | + Checkpoints ($15.00) + Scratch ($20.00)              |
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **Stage 10: Zero-Cleanup Itemized**| **564.40 GB** (525.64 GiB)| 50.00 GB (46.57 GiB)     | **614.40 GB** (572.20 GiB)| Stage 9 Components ($507.40) + Token Shards ($12.00)   |
| *(Itemized logs + scratch)*        |                          |                          |                          | + Checkpoints ($15.00) + Logs ($10.00) + Scratch ($20) |
+------------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
```

### Forensic Proof of the 27.00 GB Difference:
- Stage 9 Application Total: **527.40 GB**
- Dual-Copy Base Application Total: **554.40 GB**
- Exact Difference:
  $$554.40\text{ GB} - 527.40\text{ GB} = \mathbf{27.00\text{ GB}}.$$
- **Physical Identification of the 27.00 GB Difference:**
  1. `COMP-08` Tokenized Binary Shards: **12.00 GB**
  2. `COMP-10` Pretraining Checkpoints: **15.00 GB**
  $$\text{Sum} = 12.00\text{ GB} + 15.00\text{ GB} = \mathbf{27.00\text{ GB}}.$$
- **Lifecycle Explanation:**
  - **Stage 9** represents the pipeline state during the **Deduplication Peak** (Stage 5). At this point in the workflow, tokenization and pretraining have not yet started. Therefore, token shards (12 GB) and checkpoints (15 GB) do not yet exist on disk.
  - **The 604.40 GB base figure** represents the cumulative state **after Pretraining completes**, assuming an unmanaged external download folder was kept ($183.70\text{ GB}$) AND zero cleanup of intermediate cleaned text, dedup index, token shards, checkpoints, and scratch workspace occurred.
  - **Stage 10 (614.40 GB)** is identical to the 604.40 GB base, except that Pretraining Logs (10.00 GB) are itemized as a separate directory alongside the 20.00 GB scratch workspace ($554.40 + 10.00 = 564.40\text{ GB}$ application data, $+ 50\text{ GB}$ OS = $614.40\text{ GB}$).

---

## 3. Comprehensive Audit of the 26.70 GB Allowance

The 26.70 GB allowance represents the size of the single largest Hindi IndicCorp v2 shard (`data/hi-1.txt` or `data/hi-2.txt`). As verified in Phase 22C, `SecureAcquisitionEngine` streams incoming chunks directly into a `.part` file in quarantine (64 KiB RAM buffer) and performs an in-place atomic rename via `os.replace()`. It does not create a second copy of any shard on disk.

```
+----+--------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| #  | Pipeline Scenario Description  | App Subtotal (GB/GiB)    | OS Reserve (GB/GiB)      | Total Peak (GB/GiB)      | Allowance Inclusion & Physical Feasibility Status      |
+----+--------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| 1  | Measured Implementation        | 183.70 GB (171.08 GiB)   | 50.00 GB (46.57 GiB)     | **233.70 GB** (217.65 GiB)| **EXCLUDED** (Code-verified physical reality; no dup)  |
| 2  | Conservative Ingress           | 210.40 GB (195.95 GiB)   | 50.00 GB (46.57 GiB)     | **260.40 GB** (242.52 GiB)| **INCLUDED** (Hypothetical in-flight shard allowance)  |
| 3  | Dual-Copy Ingress Peak         | 527.40 GB (491.18 GiB)   | 50.00 GB (46.57 GiB)     | **577.40 GB** (537.75 GiB)| **EXCLUDED** (All 9 shards fully downloaded by Stage 5)|
| 4  | Zero-Cleanup (Single Raw Copy) | 380.70 GB (354.55 GiB)   | 50.00 GB (46.57 GiB)     | **430.70 GB** (401.12 GiB)| **EXCLUDED** (Cumulative single-copy pipeline retention|
| 5  | Dual-Copy Zero-Cleanup         | 564.40 GB (525.64 GiB)   | 50.00 GB (46.57 GiB)     | **614.40 GB** (572.20 GiB)| **EXCLUDED** (Ingress buffer gone before training ckpt)|
| 6  | Theoretical Stacking Ceiling   | 591.10 GB (550.51 GiB)   | 50.00 GB (46.57 GiB)     | **641.10 GB** (597.07 GiB)| **INCLUDED AS UNVERIFIED THEORETICAL STACKING LIMIT**  |
+----+--------------------------------+--------------------------+--------------------------+--------------------------+--------------------------------------------------------+
```

*Lifecycle Incompatibility Finding:* The 26.70 GB shard buffer cannot physically coexist with pretraining checkpoints. The `.part` file ceases to exist the moment ingress finishes and `os.replace()` is executed. It is temporally and physically impossible for an incoming `.part` shard buffer to persist into the pretraining stage. Scenario 6 (641.10 GB) is strictly a hypothetical mathematical ceiling, not an operational state.

---

## 4. Historical Capacity Figure Disposition Register

```
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| Historical Benchmark Figure        | Decimal / Binary Value   | Final Classification     | Detailed Audit Provenance & Disposition Status         |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **393.70 GB Sequential Peak**      | 393.70 GB (366.66 GiB)   | **RETAINED**             | **Verified physical high-water mark** of the sequential|
|                                    |                          |                          | pipeline during Stage 5 (Deduplication).               |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **395.70 GB Raw-Retained Peak**    | 395.70 GB (368.52 GiB)   | **RETAINED / HYPOTHETICAL| **Verified operational scenario** representing Stage 7 |
|                                    |                          |                          | Tokenization where raw data is kept on disk for audit. |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **604.40 GB Dual-Copy Base Peak**  | 604.40 GB (562.89 GiB)   | **RETAINED / HYPOTHETICAL| **Verified conservative baseline** representing worst- |
|                                    |                          |                          | case failure of raw ingress and intermediate cleanup.  |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **614.40 GB Zero-Cleanup Itemized**| 614.40 GB (572.20 GiB)   | **RETAINED / HYPOTHETICAL| **Verified itemized worst-case** where pretraining     |
|                                    |                          |                          | logs (10 GB) and scratch (20 GB) are both tracked.     |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **631.10 GB Previous Conservative**| 631.10 GB (587.76 GiB)   | **SUPERSEDED / RETIRED** | **Superseded.** Incorporates 26.70 GB phantom buffer   |
|                                    |                          |                          | on top of 604.40 GB base; physically incompatible.     |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| **641.10 GB Zero-Cleanup + Allow** | 641.10 GB (597.07 GiB)   | **UNVERIFIED STACKING**  | **Retired from operational planning.** Retained only as|
|                                    |                          |                          | an unverified mathematical stacking ceiling.           |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
```
