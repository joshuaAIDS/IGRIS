# IGRIS PHASE 19 — HARDWARE & COST READINESS REPORT

**Document ID:** `IGRIS-PHASE19-COST-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Objective:** Pretraining Hardware Resource & Cloud Cost Projections  
**Status:** ARCHITECTURALLY MODELLED & BUDGETED  

---

## 1. Executive Summary

This report establishes the physical hardware requirements, compute budgets, and cloud infrastructure cost projections for transitioning the IGRIS Multilingual Decoder-Only Transformer from local infrastructure validation to production pretraining.

### 1.1 Fundamental Hardware Truthfulness Declaration
- **Current Development Environment:** Single laptop GPU (NVIDIA GeForce RTX 3050 6GB Laptop GPU, 16 GB Host RAM, Windows 11).
- **Readiness Scope:** The local workstation is fully validated for **software engineering, tokenizer verification, architectural causality, small-scale experiment verification, and synthetic dry runs**.
- **Pretraining Limitation:** **A 6GB laptop GPU is NOT sufficient for full-scale multilingual pretraining.** Full pretraining requires transitioning to a multi-GPU accelerator cluster (e.g., 8x A100 80GB or 8x H100 80GB SXM5).

---

## 2. Measured Development Baseline vs Production Requirements

| Parameter | Local Host Measured (Phase 17 & 18) | Production Target Cluster (8x H100 80GB) | Production Target Cluster (8x A100 80GB) |
| :--- | :---: | :---: | :---: |
| **GPU Model** | NVIDIA GeForce RTX 3050 Laptop GPU | 8x NVIDIA H100 SXM5 | 8x NVIDIA A100 SXM4 |
| **VRAM per GPU** | 5.999 GB GDDR6 | 80 GB HBM3 | 80 GB HBM2e |
| **Tensor Core Precision** | FP16 AMP / BF16 Native | BF16 Tensor Core (FP8 optional) | BF16 Tensor Core |
| **Distributed Interconnect** | Loopback TCP (Gloo) | NVLink 4 (900 GB/s bidirectional) | NVLink 3 (600 GB/s bidirectional) |
| **Sustained Throughput** | **3,803 tokens/s** (FP16, $B=2, L=256$) | **~700,000 tokens/s** (Projected) | **~280,000 tokens/s** (Projected) |
| **Peak Accumulation Speed** | **5,229 tokens/s** ($A=4$) | **~850,000 tokens/s** (Projected) | **~350,000 tokens/s** (Projected) |

---

## 3. Pretraining Compute & Cloud Budget Projections

Computations evaluate pretraining the 16-layer, 96.5M parameter IGRIS transformer across three corpus scale regimes:
1. **Tier 1 (Proof-of-Concept):** 10 Billion Tokens
2. **Tier 2 (Chinchilla-Optimal Baseline):** 50 Billion Tokens
3. **Tier 3 (High-Capability Extended Pretraining):** 100 Billion Tokens

### 3.1 8x NVIDIA H100 80GB SXM5 Cluster Projections
*(Assumed cloud on-demand pricing: \$3.50 per GPU-hour = \$28.00/hour for an 8x H100 node; sustained throughput: 700,000 tokens/sec)*

| Pretraining Corpus Size | Total Tokens | Estimated Duration | Node Hours Required | Estimated Cloud Compute Cost |
| :---: | :---: | :---: | :---: | :---: |
| **10 Billion Tokens** | $10 \times 10^9$ | **~3.97 hours** | 4.0 node-hours | **\$112.00** |
| **50 Billion Tokens** | $50 \times 10^9$ | **~19.84 hours** | 20.0 node-hours | **\$560.00** |
| **100 Billion Tokens** | $100 \times 10^9$ | **~39.68 hours** | 40.0 node-hours | **\$1,120.00** |

---

### 3.2 8x NVIDIA A100 80GB SXM4 Cluster Projections
*(Assumed cloud on-demand pricing: \$2.00 per GPU-hour = \$16.00/hour for an 8x A100 node; sustained throughput: 280,000 tokens/sec)*

| Pretraining Corpus Size | Total Tokens | Estimated Duration | Node Hours Required | Estimated Cloud Compute Cost |
| :---: | :---: | :---: | :---: | :---: |
| **10 Billion Tokens** | $10 \times 10^9$ | **~9.92 hours** | 10.0 node-hours | **\$160.00** |
| **50 Billion Tokens** | $50 \times 10^9$ | **~49.60 hours** | 50.0 node-hours | **\$800.00** |
| **100 Billion Tokens** | $100 \times 10^9$ | **~99.21 hours** | 100.0 node-hours | **\$1,600.00** |

---

## 4. Storage & Ancillary Infrastructure Costs

1. **High-Speed Scratch Storage (NVMe / Shared FS):**
   - 100B token pre-tokenized corpus (uint16 array): $\approx 200\text{ GB}$.
   - High-performance NVMe scratch disk (1 TB): ~\$30 / month.
2. **Checkpoint Archival Storage:**
   - Single un-sharded checkpoint binary (`.pt`): `386 MB`.
   - Saving checkpoints every 5,000 steps (20 snapshots total): `7.7 GB`.
   - AWS S3 or Google Cloud Storage coldline storage: < \$1.00 / month.
3. **Egress & Logging Bandwidth:**
   - Weights and metrics synchronization: negligible (< \$5.00).

---

## 5. Strategic Pretraining Recommendations

1. **Recommended Architecture Tier for Phase 20:**
   - **8x NVIDIA H100 80GB Node:** Provides the optimal balance of turnaround time and cost (\$560 total budget for a 50B token model completed in under 20 hours).
2. **Batch Sizing Strategy:**
   - Micro-batch size $B=16$ per GPU with sequence length $L=2048$.
   - Global batch size per step: $16 \times 8 \times 2048 = 262,144\text{ tokens}$ (~0.26M tokens per step).
   - 50B tokens completed in $\approx 190,735$ global optimizer updates.
3. **FSDP Configuration:**
   - Mode: `FULL_SHARD` (ZeRO-3).
   - Precision: `MixedPrecision(param_dtype=torch.bfloat16, reduce_dtype=torch.bfloat16)`.
   - Activation Checkpointing: Enabled for $L=2048$.

**Audit Verdict:** Pretraining costs are highly manageable and economically feasible for an independent solo developer. Hardware requirements are clearly defined and realistic.
