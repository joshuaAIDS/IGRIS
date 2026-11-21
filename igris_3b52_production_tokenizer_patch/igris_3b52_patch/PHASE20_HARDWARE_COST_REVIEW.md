# IGRIS PHASE 20 — HARDWARE & PRETRAINING COST REVIEW
## Physical Host Characterization, Cloud Scaling Models, and Budget Projections

**Document ID:** `IGRIS-PHASE20-HW-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Objective:** Final Hardware Readiness & Cloud Pretraining Cost Audit  
**Status:** MEASURED LOCAL PERFORMANCE DISTINGUISHED FROM ESTIMATED CLOUD CAPACITY  

---

## 1. Executive Summary

This report establishes the physical hardware boundaries, local empirical benchmark results, and prospective cloud pretraining budgets for the IGRIS Multilingual Decoder-Only Transformer.

### Critical Operational Boundary:
1. **Measured Local Host:** Single NVIDIA GeForce RTX 3050 Laptop GPU (6,144 MB VRAM). This hardware is empirically verified and certified for local code development, tokenizer creation, architectural unit testing, and small-scale synthetic dry runs.
2. **Pretraining Constraint:** 6 GB VRAM cannot sustain full-scale multi-billion-token pretraining at production sequence length (2,048) and production batch sizes ($B \ge 256$). Full pretraining requires external cloud compute.
3. **Multi-GPU / FSDP Status:** Multi-process DDP via loopback is physically validated. FSDP multi-GPU sharding and multi-node scaling remain **UNVALIDATED ON PHYSICAL CLUSTER HARDWARE** pending cloud deployment.

---

## 2. Measured Local Host Hardware Performance

All measurements were empirically gathered on the physical development machine during Phases 17–19:

| Benchmark Parameter | Measured Metric | Operational Context / Conditions |
| :--- | :---: | :--- |
| **GPU Model** | NVIDIA GeForce RTX 3050 Laptop GPU | 2,048 CUDA Cores, 64 Tensor Cores |
| **Dedicated VRAM** | 6,144 MB GDDR6 | Ampere Architecture (Compute Capability 8.6) |
| **FP32 Throughput** | 2,551.4 tokens / sec | Standard PyTorch FloatTensor execution |
| **FP16 AMP Throughput** | 3,803.3 tokens / sec | Automatic Mixed Precision (`1.49x` speedup) |
| **Native BF16 Throughput** | 3,111.4 tokens / sec | Native bfloat16 tensor operations |
| **Gradient Accumulation Throughput** | 5,229.2 tokens / sec | Micro-batching $B=2, A=4$ |
| **Peak VRAM without Checkpointing** | 5,865.21 MB | Context length 2048, batch size 2 |
| **Peak VRAM with Checkpointing** | 2,092.54 MB | Context length 2048, batch size 2 |
| **Measured Memory Savings** | **64.32% Reduction** | **3,772.67 MB VRAM saved** |
| **Multi-Process DDP (Gloo Loopback)**| Bitwise Match ($\Delta=0.0$) | 2 spawned local workers, exact rank sync |

---

## 3. Cloud Pretraining Architectural Assumptions

For full-scale pretraining (5B, 20B, and 50B tokens), the following engineering parameters are modeled:

### 3.1 Model & Compute Mathematics
- **Authoritative Model Parameters:** $N_{\text{total}} = 96,485,888$ (Untied) / $N_{\text{tied}} = 79,708,672$
- **Non-Embedding Parameters ($N_{\text{non-embed}}$):** $62,931,456$ (~62.93M)
- **Theoretical Training FLOPs per Token:**
  $$\text{FLOPs/token} \approx 6 \times N_{\text{non-embed}} = 6 \times 62,931,456 = 377,588,736\ (\approx 3.78 \times 10^8\text{ FLOPs})$$
- **Total Compute for 50 Billion Tokens:**
  $$\text{Total FLOPs} = 50 \times 10^9 \times 3.7759 \times 10^8 \approx 1.89 \times 10^{19}\text{ FLOPs}\ (18.9\text{ ExaFLOPs})$$

### 3.2 Target Training Hyperparameters
- **Context Sequence Length ($S$):** 2,048 tokens
- **Global Batch Size:** 256 sequences = $524,288\text{ tokens/batch}$ ($\approx 0.524\text{M tokens}$)
- **Micro-batch size per GPU ($b$):** 4 sequences = 8,192 tokens
- **Gradient Accumulation Factor ($A$):**
  - On 8 GPUs: $8\text{ GPUs} \times 4\text{ micro-batch} \times 8\text{ accum steps} = 256\text{ sequences}$
- **Precision:** Native BF16 execution with FP32 AdamW master optimizer weights.
- **Model FLOPs Utilization (MFU):** Modeled conservatively at 42% on H100 SXM5 and 38% on A100 SXM4.

---

## 4. Cloud Cluster Options & Cost Projections

### Option A: Dedicated 8x NVIDIA H100 (80GB SXM5) Cluster (Recommended)
- **Effective Cluster Throughput:** ~700,000 tokens/sec
- **On-Demand Hourly Rate:** \$28.00 – \$35.00 / hour (e.g. Lambda Labs, RunPod, CoreWeave)
- **Checkpoint Overhead:** ~2% (periodic asynchronous atomic saves to NVMe + object store)
- **Storage & Network Allowance:** \$50 (1 TB NVMe SSD + egress)

### Option B: Dedicated 8x NVIDIA A100 (80GB SXM4) Cluster
- **Effective Cluster Throughput:** ~280,000 tokens/sec
- **On-Demand Hourly Rate:** \$16.00 – \$20.00 / hour
- **Checkpoint Overhead:** ~3%
- **Storage & Network Allowance:** \$50

### Comprehensive Cost Matrix:

| Pretraining Scale | Tokens | Target Cluster | Estimated Duration | Compute Cost | Storage & Egress | Total Estimated Cost |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **Pilot Pretraining** | 5 Billion | 8x NVIDIA A100 | ~5.2 hours | \$83 – \$104 | \$15 | **\$98 – \$119** |
| **Pilot Pretraining** | 5 Billion | 8x NVIDIA H100 | ~2.1 hours | \$59 – \$74 | \$15 | **\$74 – \$89** |
| **Standard Baseline** | 20 Billion | 8x NVIDIA H100 | ~8.0 hours | \$224 – \$280 | \$30 | **\$254 – \$310** |
| **Full Production** | 50 Billion | 8x NVIDIA H100 | ~20.0 hours | \$560 – \$700 | \$50 | **\$610 – \$750** |
| **Full Production** | 50 Billion | 8x NVIDIA A100 | ~50.0 hours | \$800 – \$1,000 | \$50 | **\$850 – \$1,050** |

---

## 5. Storage, Network & Checkpoint Overhead Accounting

1. **Checkpoint File Footprint:**
   - Model weights (BF16): $\approx 159.4\text{ MB}$
   - AdamW optimizer states (FP32 1st/2nd moments): $\approx 637.7\text{ MB}$
   - Checkpoint total size per snapshot: $\approx 797.1\text{ MB} \approx 0.8\text{ GB}$
2. **Storage Retention Policy:**
   - Retain last 3 checkpoints locally on NVMe ($3 \times 0.8\text{ GB} = 2.4\text{ GB}$).
   - Retain milestone checkpoints (every 5B tokens) in cloud object storage ($10 \times 0.8\text{ GB} = 8\text{ GB}$).
3. **Network Egress Costs:**
   - Transferring 10 milestone checkpoints ($8\text{ GB}$) to cold archive @ \$0.09/GB = \$0.72.

---

## 6. Physical Validation Boundaries

> [!IMPORTANT]
> - **Local GPU:** Physical measurements on the RTX 3050 Laptop GPU are verified.
> - **Multi-GPU / FSDP / Cloud Clusters:** All multi-GPU metrics, throughput rates, and cost models are theoretical simulations and empirical projections based on standard MFU curves. Physical multi-GPU performance must be formally certified upon provisioning the cloud accelerator cluster in Phase 20/Production.
