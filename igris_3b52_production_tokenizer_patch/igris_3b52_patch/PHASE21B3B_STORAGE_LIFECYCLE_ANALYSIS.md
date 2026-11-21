# PHASE 21B3B — STORAGE LIFECYCLE ANALYSIS
## Multi-Stage Capacity Models, Pipeline Lifecycle, and Simultaneous Coexistence Analysis

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3B  

---

## 1. Executive Summary

Phase 21B3B establishes three mathematically rigorous, mutually exclusive storage capacity models for the IGRIS pretraining data infrastructure. These models reconcile the operational differences between sequential streaming pipelines, peak simultaneous processing stages, and permanent long-term retention.

All calculations are expressed in both decimal units ($10^9$ bytes, GB) and binary units ($2^{30}$ bytes, GiB).

```
+---------------------------------------+-------------------+-------------------+-----------------------------------+
| Storage Model Configuration           | Decimal (GB)      | Binary (GiB)      | Operational Classification        |
+---------------------------------------+-------------------+-------------------+-----------------------------------+
| Model A: Minimum Theoretical          | 421.48 GB         | 392.53 GiB        | Sequential Streaming (High Risk)  |
| Model B: Peak Simultaneous (Stage 6)  | 511.48 GB         | 476.35 GiB        | Recommended Production Baseline   |
| Model B: Worst-Case Unpruned Buffers  | 878.88 GB         | 818.52 GiB        | Unconstrained Upper Bound         |
| Model C: Long-Term Retained State     | 441.48 GB         | 411.16 GiB        | Permanent Steady-State Storage    |
+---------------------------------------+-------------------+-------------------+-----------------------------------+
```

---

## 2. Model A: Minimum Theoretical Capacity (Streaming / Aggressive In-Place)

### Operational Hypothesis
Model A models the absolute minimum storage required if the pipeline executes with aggressive streaming and immediate garbage collection:
- Raw LFS downloads stream into an in-memory or single-pass validator without duplicate disk buffering.
- Plaintext normalization and regex cleaning are piped directly without staging intermediate working plaintext files.
- Deduplication and MinHash signatures are sized minimally (15 GB).
- Binary sharding targets the lower bound of the tokenization estimate (17.5B tokens = 35.00 GB uint16).
- Ephemeral scratch is strictly limited to 20 GB, and checkpoints are pruned to the single latest weights (10 GB).

### Capacity Breakdown:
- Raw Upstream Archive: **183.70 GB** ($183,700,000,000$ B / 171.08 GiB)
- Quarantine Staging Buffer: **0.00 GB** (in-place streaming)
- Working Plaintext Copy: **0.00 GB** (piped in memory)
- Cleaned & PII-Redacted Corpus: **137.78 GB** ($137,775,000,000$ B / 128.31 GiB) [**PROJECTED_UNVALIDATED**]
- Deduplication & MinHash Indexes: **15.00 GB** ($15,000,000,000$ B / 13.97 GiB)
- Tokenized Binary Shards: **35.00 GB** ($35,000,000,000$ B / 32.60 GiB)
- Ephemeral Processing Scratch: **20.00 GB** ($20,000,000,000$ B / 18.63 GiB)
- Training Checkpoints: **10.00 GB** ($10,000,000,000$ B / 9.31 GiB)
- Safety Margin: **20.00 GB** ($20,000,000,000$ B / 18.63 GiB)
- **Total Model A Footprint:** **421.48 GB** ($421,475,000,000$ B) = **392.53 GiB**

### Explicit Limitations & Failure Modes:
1. **Zero Fault Tolerance:** If a network stream or worker process fails mid-tokenization, partial shards cannot be resumed without restarting the entire pipeline.
2. **No Data Lineage Inspection:** Bypassing intermediate text stages prevents manual spot-checking of PII redaction and token boundary artifacts.
3. **Engineering Overhead:** Requires custom streaming tokenizers and IPC pipelines rather than battle-tested batch tooling (e.g., Hugging Face Datasets, Arrow IPC).

---

## 3. Model B: Peak Simultaneous Operational Capacity

### Identification of Peak Processing Stage
The storage footprint of a data pipeline is not static; it fluctuates across lifecycle phases.
The **peak simultaneous stage** occurs at **Stage 6 (Tokenization & Binary Sharding)**. At this exact junction:
- The Raw Gold Archive (183.70 GB) must be preserved for provenance and bitwise verification.
- The Cleaned & Normalized Corpus (137.78 GB projected) must reside in full on disk to feed multi-process tokenizers.
- The Deduplication and MinHash LSH Index (25.00 GB) must remain accessible for cross-shard duplicate filtering.
- The Tokenized Binary Shards (uint16, 50.00 GB) are being written to disk.
- High-throughput merge scratch, sort buffers, and chunking tables (40.00 GB) are actively occupied.
- Initial model checkpoints (25.00 GB) and operational safety headroom (50.00 GB) must be allocated.

### Capacity Breakdown at Peak Stage 6:
- Raw Upstream Archive: **183.70 GB** (171.08 GiB)
- Cleaned Corpus (Projected): **137.78 GB** (128.31 GiB)
- Deduplication & MinHash Indexes: **25.00 GB** (23.28 GiB)
- Tokenized Binary Shards (25B tokens): **50.00 GB** (46.57 GiB)
- Temporary Processing Scratch: **40.00 GB** (37.25 GiB)
- Training Checkpoints & Optimizer States: **25.00 GB** (23.28 GiB)
- Operational Safety Margin & Paging Headroom: **50.00 GB** (46.57 GiB)
- **Total Peak Operational Capacity (Stage 6):** **511.48 GB** ($511,475,000,000$ B) = **476.35 GiB**

### Worst-Case Unpruned Buffer Footprint (Upper Bound):
If the engineering pipeline fails to prune the ephemeral quarantine buffer (183.70 GB) and working plaintext buffer (183.70 GB) prior to Stage 6, all intermediate states would accumulate simultaneously:
$$	ext{Worst-Case Peak} = 511.48	ext{ GB} + 183.70	ext{ GB} + 183.70	ext{ GB} = \mathbf{878.88	ext{ GB}}\quad (818.52	ext{ GiB})$$
Production tooling must mandate automated teardown of Stages 2 and 3 before Stage 6 commences to prevent triggering this unconstrained upper bound.

---

## 4. Model C: Long-Term Retained Production Capacity (Steady State)

### Operational Hypothesis
Once pretraining binary sharding is verified against checksums, all transient files (temporary sort buffers, merge scratch, ephemeral chunking tables) are permanently unlinked.
Model C models the long-term disk requirement during active pretraining iterations.

### Capacity Breakdown:
- Raw Gold Archive (9 upstream LFS files preserved immutable): **183.70 GB** (171.08 GiB)
- Cleaned & PII-Redacted Corpus (Golden Text Reference): **137.78 GB** (128.31 GiB) [**PROJECTED_UNVALIDATED**]
- Deduplication MinHash Signatures & Inverted Index: **25.00 GB** (23.28 GiB)
- Pretraining Binary Token Shards (uint16 Arrow/NumPy): **50.00 GB** (46.57 GiB)
- Retained Model Checkpoints & Optimizer States (Rolling): **25.00 GB** (23.28 GiB)
- Retained Maintenance & Paging Safety Headroom: **20.00 GB** (18.63 GiB)
- Ephemeral Scratch: **0.00 GB** (Purged)
- **Total Long-Term Retained Footprint:** **441.48 GB** ($441,475,000,000$ B) = **411.16 GiB**

*(Note: If training checkpoints are hosted on an independent model storage volume, the dedicated dataset-only retained footprint is **416.48 GB** / **387.88 GiB**).*

---

## 5. Formal Projection Status of the 137.78 GB Cleaned Corpus

The figure **137.78 GB** ($137,775,000,000$ bytes) represents a projected 25% gross reduction from the 183.70 GB raw corpus via line deduplication, regex PII masking, and non-Indic script filtering.
Under Phase 21B3B governance, this figure is strictly designated:

**PROJECTED_UNVALIDATED**  
$$\mathbf{PROJECTED\_UNVALIDATED}$$

It must not be treated as empirical fact until sample-based empirical filtering benchmarks are performed in future acquisition phases.
