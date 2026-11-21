# PHASE 22D — STORAGE ARITHMETIC CORRECTION & STAGE RECONCILIATION
## Forensic Audit of Pretraining Stage Discrepancies, Tokenization Stages, and Component Equations

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22D  
**Execution Mode:** READ-ONLY AUDIT AND DOCUMENTATION CORRECTION  
**Status:** RECONCILED & AUDITED  

---

## 1. Executive Summary

Phase 22D resolves all remaining storage accounting discrepancies from Phase 22C, establishing a single authoritative, mathematically closed component inventory and stage matrix.

### Core Arithmetic Corrections Resolved:
1. **Pretraining Stage Arithmetic Corrected to 37.00 GB:**
   - *Phase 22C listed:* Tokenized shards (12.00 GB) + Checkpoints (15.00 GB) + Logs (10.00 GB) = 37.00 GB application data, but the stage matrix reported 47.00 GB application data (and 97.00 GB total with 50 GB OS).
   - *Forensic Investigation:* The 47.00 GB figure was caused by carrying over an unverified 20.00 GB generic data processing scratch workspace from earlier stages ($12 + 15 + 20 = 47	ext{ GB}$) alongside 10.00 GB logs. Direct code inspection of `model_training_pipeline.py` confirms that pretraining performs zero text transformation or sorting. The only operational non-checkpoint/shard data produced during pretraining is training telemetry, TensorBoard events, and evaluation metrics (10.00 GB).
   - *Correction:* Application data is corrected to strictly **37.00 GB decimal (34.46 GiB binary)**. Total pretraining stage requirement with 50.00 GB OS headroom is corrected to **87.00 GB decimal (81.03 GiB binary)**. The 47.00 GB and 97.00 GB figures are formally documented as superseded.
2. **Reconciliation of Stage 3A vs. Stage 3B Tokenization:**
   - *Stage 3A (Post-Cleanup Enforced):* Cleaned text (130.00 GB) + Token shards (12.00 GB) + Token scratch (20.00 GB) = **162.00 GB decimal (150.87 GiB binary)** application data (+ 50 GB OS = **212.00 GB decimal / 197.44 GiB binary**).
   - *Stage 3B (Raw Retained / Partial Cleanup):* Raw corpus in quarantine (183.70 GB) + Cleaned text (130.00 GB) + Token shards (12.00 GB) + Token scratch (20.00 GB) = **345.70 GB decimal (321.96 GiB binary)** application data (+ 50 GB OS = **395.70 GB decimal / 368.52 GiB binary**). This confirms that 345.70 GB reflects retention of the raw corpus alongside cleaned and tokenized representations, with the 10.00 GB deduplication index purged after Stage 5.

---

## 2. Pretraining Stage Forensic Breakdown

```
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| Pretraining Component              | Decimal Size (GB)        | Binary Size (GiB)        | Physical Storage Location & Purpose                    |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| COMP-08: Tokenized Binary Shards   | 12.00 GB                 | 11.18 GiB                | `data/tokenized/` (int32 token arrays, read-only input)|
| COMP-10: Pretraining Checkpoints   | 15.00 GB                 | 13.97 GiB                | `checkpoints/pretraining/` (rolling window of 3–10)    |
| COMP-11: Training Telemetry & Logs | 10.00 GB                 | 9.31 GiB                 | `logs/pretraining/` (TensorBoard logs and eval metrics)|
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| CORRECTED APPLICATION TOTAL        | **37.00 GB**             | **34.46 GiB**            | Pure Pretraining Operational Footprint                 |
| Operating System Headroom Reserve  | 50.00 GB                 | 46.57 GiB                | Host OS, CUDA runtime, virtualenv baseline             |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| CORRECTED PRETRAINING STAGE PEAK   | **87.00 GB**             | **81.03 GiB**            | Total Physical Pretraining High-Water Mark             |
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
| Superseded Phase 22C Figure        | 47.00 GB / 97.00 GB      | 43.77 GiB / 90.34 GiB    | SUPERSEDED (Removed unverified 20 GB scratch carryover)|
+------------------------------------+--------------------------+--------------------------+--------------------------------------------------------+
```

### Forensic Analysis of Component Existence:
- **Did an additional 10 GB component exist?** No.
- **Why did Phase 22C report 47 GB?** Phase 22A and Phase 22B maintained a generic "Scratch Workspace = 20 GB" entry across data processing stages. When Phase 22C authored the matrix, it summed $12	ext{ (tokens)} + 15	ext{ (ckpts)} + 20	ext{ (scratch)} = 47	ext{ GB}$, but in prose described it as $12 + 15 + 10 = 37	ext{ GB}$.
- **Physical Reality:** In pretraining, no text sorting, deduplication, or chunking occurs. The training engine streams binary token batches directly from `data/tokenized/` into GPU memory, writes periodic checkpoints to `checkpoints/pretraining/`, and logs step metrics to `logs/pretraining/`. No intermediate sorting scratch is ever created. Adding an arbitrary 10 GB or 20 GB scratch workspace on top of 10 GB logs violates physical reality.
- **Audit Decision:** The pretraining application total is corrected to **37.00 GB decimal (34.46 GiB binary)** and total stage requirement to **87.00 GB decimal (81.03 GiB binary)**.

---

## 3. Reconciled Stage 3 Tokenization Equations

```
+------------------------------------+----------------------------------------------------------+--------------------------+--------------------------+
| Metric                             | Component Breakdown                                      | Decimal GB ($10^9$)      | Binary GiB ($2^{30}$)    |
+------------------------------------+----------------------------------------------------------+--------------------------+--------------------------+
| **Stage 3A: Tokenization (Cleaned)**| Cleaned Text (`data/cleaned/`)                           | 130.00 GB                | 121.07 GiB               |
|                                    | Token Shards (`data/tokenized/`)                         | 12.00 GB                 | 11.18 GiB                |
|                                    | Tokenization Scratch (`scratch/tokenization/`)           | 20.00 GB                 | 18.63 GiB                |
|                                    | **Application Subtotal (Stage 3A)**                      | **162.00 GB**            | **150.87 GiB**           |
|                                    | Operating System Reserve                                 | 50.00 GB                 | 46.57 GiB                |
|                                    | **Total Physical High-Water (Stage 3A)**                 | **212.00 GB**            | **197.44 GiB**           |
+------------------------------------+----------------------------------------------------------+--------------------------+--------------------------+
| **Stage 3B: Tokenization (Raw Kept)**| Raw IndicCorp v2 Corpus (`quarantine/raw/`)              | 183.70 GB                | 171.08 GiB               |
|                                    | Cleaned Text (`data/cleaned/`)                           | 130.00 GB                | 121.07 GiB               |
|                                    | Token Shards (`data/tokenized/`)                         | 12.00 GB                 | 11.18 GiB                |
|                                    | Tokenization Scratch (`scratch/tokenization/`)           | 20.00 GB                 | 18.63 GiB                |
|                                    | **Application Subtotal (Stage 3B)**                      | **345.70 GB**            | **321.96 GiB**           |
|                                    | Operating System Reserve                                 | 50.00 GB                 | 46.57 GiB                |
|                                    | **Total Physical High-Water (Stage 3B)**                 | **395.70 GB**            | **368.52 GiB**           |
+------------------------------------+----------------------------------------------------------+--------------------------+--------------------------+
```

### Physical Directory and Lifecycle Mapping:

1. **Cleaned Text (`data/cleaned/`):**
   - Size: 130.00 GB (121.07 GiB).
   - Representation: Filtered, normalized plain UTF-8 text documents produced by `quality_filter.py` and `unicode_processor.py`.
   - Creation Event: Stage 4 (Cleaning).
   - Deletion Event: Purged or archived upon tokenization completion and shard verification.
   - Evidence: Phase 14 / Phase 22 pilot yield data (~70.7% retention of 183.70 GB raw corpus).

2. **Token Shards (`data/tokenized/`):**
   - Size: 12.00 GB (11.18 GiB).
   - Representation: Compressed int32 token arrays stored in Apache Arrow format.
   - Creation Event: Stage 6/7 (Tokenization).
   - Deletion Event: Retained through pretraining until model completion.
   - Evidence: 3.0B–5.5B tokens in 4-byte integer representations with compression.

3. **Raw Corpus (`quarantine/raw/`):**
   - Size: 183.70 GB (171.08 GiB).
   - Representation: 9 flat UTF-8 files across 7 languages.
   - Creation Event: Stage 2 (Ingress).
   - Deletion Event: In Stage 3A, deleted post-cleaning verification. In Stage 3B, retained unpurged for safekeeping.
   - Evidence: Phase 21B3 immutable upstream metadata.

4. **Tokenization Scratch Workspace (`scratch/tokenization/`):**
   - Size: 20.00 GB (18.63 GiB).
   - Representation: Temporary in-flight token batch files, vocabulary frequency counting buffers, and shard serialization buffers.
   - Creation Event: Tokenizer training and dataset sharding start.
   - Deletion Event: Automatically purged upon shard closure.

5. **Deduplication Index Lifecycle Note:**
   - In Stage 3B, the 10.00 GB deduplication index (`data/indices/dedup/`) is omitted from the 345.70 GB equation because deduplication has completed, and the index is discarded before tokenization begins.
   - If an operational failure leaves the deduplication index unpurged as well, the application subtotal would be:
     $$183.70 + 130.00 + 10.00 + 12.00 + 20.00 = \mathbf{355.70	ext{ GB decimal (331.27 GiB binary)}},$$
     yielding a total stage requirement of **405.70 GB decimal (377.84 GiB binary)** with OS headroom.

---

## 4. Master 10-Stage Authoritative Capacity Matrix

```
+----+--------------------------------+--------------------+--------------------+--------------------+--------------------+--------------------------+
| #  | Pipeline Stage Name            | Persistent App Data| Temp Workspace     | Total App Data     | Total Peak (+ OS)  | Behavior Classification  |
+----+--------------------------------+--------------------+--------------------+--------------------+--------------------+--------------------------+
| 1  | System Baseline                | 0.00 GB (0.00 GiB) | 0.00 GB (0.00 GiB) | 0.00 GB (0.00 GiB) | **50.00 GB** (46.57)| ACTUAL_IMPLEMENTATION    |
| 2A | Dataset Ingress (Measured)     | 183.70 GB (171.08) | 0.00 GB (0.00 GiB) | 183.70 GB (171.08) | **233.70 GB** (217.65)| ACTUAL_IMPLEMENTATION    |
| 2B | Dataset Ingress (Conservative) | 183.70 GB (171.08) | 26.70 GB (24.87)   | 210.40 GB (195.95) | **260.40 GB** (242.52)| CONSERVATIVE_HYPOTHETICAL|
| 3  | Validation & Schema Check      | 183.70 GB (171.08) | 5.00 GB (4.66 GiB) | 188.70 GB (175.74) | **238.70 GB** (222.31)| ACTUAL_IMPLEMENTATION    |
| 4  | Cleaning & Normalization       | 313.70 GB (292.16) | 20.00 GB (18.63)   | 333.70 GB (310.78) | **383.70 GB** (357.35)| ACTUAL_IMPLEMENTATION    |
| 5  | Deduplication (Sequential Peak)| 323.70 GB (301.47) | 20.00 GB (18.63)   | 343.70 GB (320.10) | **393.70 GB** (366.66)| ACTUAL_IMPLEMENTATION    |
| 6  | Tokenization (Post-Cleanup)    | 142.00 GB (132.25) | 20.00 GB (18.63)   | 162.00 GB (150.87) | **212.00 GB** (197.44)| ACTUAL_IMPLEMENTATION    |
| 7  | Tokenization (Raw Retained)    | 325.70 GB (303.33) | 20.00 GB (18.63)   | 345.70 GB (321.96) | **395.70 GB** (368.52)| CONSERVATIVE_HYPOTHETICAL|
| 8  | Pretraining (Corrected)        | 27.00 GB (25.15)   | 10.00 GB (9.31 GiB)| 37.00 GB (34.46)   | **87.00 GB** (81.03) | ACTUAL_IMPLEMENTATION    |
| 9  | Conservative Dual-Copy Ingress | 507.40 GB (472.55) | 20.00 GB (18.63)   | 527.40 GB (491.18) | **577.40 GB** (537.75)| CONSERVATIVE_HYPOTHETICAL|
| 10 | Conservative Zero-Cleanup      | 534.40 GB (497.70) | 30.00 GB (27.94)   | 564.40 GB (525.64) | **614.40 GB** (572.20)| CONSERVATIVE_HYPOTHETICAL|
+----+--------------------------------+--------------------+--------------------+--------------------+--------------------+--------------------------+
```

---

## 5. Audit of High-Water Marks & Margin Reconciliation

1. **Universal Sequential High-Water Mark:**
   - Occurs strictly at **Stage 5 (Deduplication Peak)**:
     $$	ext{Peak}_{	ext{seq}} = 183.70	ext{ (raw)} + 130.00	ext{ (cleaned)} + 10.00	ext{ (index)} + 20.00	ext{ (scratch)} + 50.00	ext{ (OS)} = \mathbf{393.70	ext{ GB decimal (366.66 GiB binary)}}.$$
2. **Cumulative Worst-Case Zero-Cleanup Peak:**
   - If duplicate raw data is retained AND intermediate files are never purged:
     $$	ext{Peak}_{	ext{zero\_cleanup}} = 183.70 	imes 2 + 130.00 + 10.00 + 12.00 + 15.00 + 10.00	ext{ (logs)} + 20.00	ext{ (scratch)} + 50.00	ext{ (OS)} = \mathbf{614.40	ext{ GB decimal (572.20 GiB binary)}}.$$
     *(Note: If logs are absorbed within the 20 GB scratch workspace, this peak is **604.40 GB decimal / 562.89 GiB binary**; if the 26.70 GB phantom buffer is also added, it reaches **641.10 GB decimal / 597.07 GiB binary**).*
3. **Provisioned 1 TB Headroom vs Margin:**
   - **Sequential Headroom:** $1,000.00 - 393.70 = \mathbf{606.30	ext{ GB decimal (564.66 GiB binary)}}$.
   - **Conservative Operational Margin:** $1,000.00 - 614.40 = \mathbf{385.60	ext{ GB decimal (359.12 GiB binary)}}$ (or $1,000.00 - 604.40 = \mathbf{395.60	ext{ GB decimal}}$).
