# IGRIS PHASE 18 — DISTRIBUTED TRAINING ARCHITECTURE & SCALABILITY PLAN

**Document ID:** `IGRIS-PHASE18-PLAN-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Objective:** Distributed Training Infrastructure Design & Scalability Validation  
**Governance State:** LOCKED — Synthetic Training Fixtures Only  

---

## 1. Executive Summary & Governance Restrictions

This plan establishes the architecture and implementation roadmap for **Phase 18 Distributed Training Architecture & Scalability Validation** of the IGRIS Multilingual Decoder-Only Transformer.

Under the `SOLO_DEVELOPER_OWNER_REVIEW` operating model, Phase 18 serves strictly as an engineering infrastructure validation phase. **No production pretraining, production dataset acquisition, or unquarantining is authorized.** All experiments execute exclusively on synthetic multilingual data.

### 1.1 Non-Negotiable Governance Invariants
1. **Synthetic Data Exclusivity:** All distributed workers ingest exclusively synthetic data fixtures (`IGRIS-DS-PHASE17-SYNTHETIC-001`).
2. **Zero Production Ingress:** No production data acquisition; production ingress gates remain **LOCKED** (Default-Deny).
3. **No Full-Scale Pretraining:** Multi-GPU scaling tests are restricted to infrastructure validation runs.
4. **Tokenizer Immutability:** Candidate A (`ac7e18b1...`) and Candidate B (`d3a3431e...`) hashes must remain strictly unmodified.
5. **No Production Checkpoints:** Checkpoints are tagged `SYNTHETIC_TEST_ONLY` and isolated in experiment directories.
6. **Fail-Closed Principle:** Any unapproved source path, network access attempt, or configuration anomaly halts execution immediately.

---

## 2. Infrastructure Scope & Technical Modules

Phase 18 implements six core distributed training capabilities:

```
+-----------------------------------------------------------------------------------+
|                        IGRIS DISTRIBUTED TRAINING ENGINE                          |
+-----------------------------------------------------------------------------------+
         |                                                 |
         v                                                 v
+----------------------------------+     +----------------------------------+
| Distributed Data Parallel (DDP)  |     |  Fully Sharded Data Parallel     |
| - Gloo backend (Windows/CPU/GPU) |     |  (FSDP) Architecture             |
| - Process group initialization   |     | - Block-level auto-wrap policy   |
| - DistributedSampler sharding    |     | - Parameter & grad sharding spec |
| - All-reduce gradient sync       |     | - StateDict handling & offload   |
+----------------------------------+     +----------------------------------+
         |                                                 |
         v                                                 v
+----------------------------------+     +----------------------------------+
|    Activation Checkpointing      |     |     Mixed-Precision Engine       |
| - Pre-norm block recomputation   |     | - FP32 / FP16 AMP / BF16 native  |
| - ~65% activation VRAM reduction |     | - Dynamic GradScaler             |
| - Gradient numerical equivalence |     | - Numerical NaN/Inf detection    |
+----------------------------------+     +----------------------------------+
         |                                                 |
         v                                                 v
+----------------------------------+     +----------------------------------+
|      Gradient Accumulation       |     |   Distributed Checkpoint Engine  |
| - Loss scaling (1 / N_accum)     |     | - Atomic write (.tmp -> .pt)     |
| - DDP no_sync() micro-steps      |     | - Rank-0 synchronized write      |
| - Unscaled gradient clipping     |     | - External SHA-256 sidecar JSON  |
+----------------------------------+     +----------------------------------+
```

---

## 3. Hardware Environment & Realistic Validation Strategy

### 3.1 Host Hardware Baseline (Phase 17 Measured Profile)
- **Host GPU:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (Ampere, Compute Capability 8.6, 5.999 GB VRAM).
- **Host CPU / OS:** Windows 11 Enterprise (`win32`), 16 GB Physical RAM.
- **PyTorch Distributed Backend:** `gloo` (native Windows multi-process backend; `nccl` is Linux-only).
- **Hardware BF16 Support:** `True` (Ampere Tensor Cores natively support BF16).

### 3.2 Transparent Validation Methodology
To ensure absolute technical integrity:
1. **Physical GPU Validation:** Single-GPU mixed-precision (FP16/BF16), activation checkpointing, gradient accumulation, and local checkpointing are executed directly on the physical RTX 3050 Laptop GPU.
2. **Multi-Process DDP Validation:** DDP process group initialization, rank coordination, `DistributedSampler`, gradient all-reduce synchronization, and worker failure recovery are verified via multi-process testing (`torch.multiprocessing.spawn`, 2 workers) using the `gloo` backend.
3. **FSDP Multi-GPU Scaling:** FSDP wrapping policies, state-dict serialization, and multi-node cluster scaling are thoroughly implemented, tested via configuration validation, and projected through theoretical models.

---

## 4. Experiment & Validation Matrix

| Area | Key Test / Verification | Target Metric / Tolerance |
| :--- | :--- | :--- |
| **DDP Multi-Process** | Process group init, rank sync, loss all-reduce | Clean worker exit, identical synced weights |
| **Distributed Sampler** | Sharding without sample overlap across ranks | Disjoint indices between Rank 0 and Rank 1 |
| **Activation Checkpointing** | Gradient equivalence vs standard forward | $\text{Max Gradient Diff} < 10^{-5}$ |
| **Activation Checkpointing** | VRAM reduction on full context ($L=2048$) | $> 50\%$ activation memory saved |
| **Mixed Precision (FP16)** | GradScaler unscaling, clipping, loss stability | Finite loss, bounded gradients $\le 1.0$ |
| **Mixed Precision (BF16)** | Native Ampere BF16 execution without scaler | Finite loss, 0 NaNs / 0 Infs |
| **Gradient Accumulation** | Accumulated gradients vs single large batch | $\text{Max Gradient Diff} < 10^{-5}$ |
| **DDP `no_sync()`** | Communication bypass on intermediate micro-steps | Zero all-reduce until accumulation boundary |
| **Distributed Checkpoints** | Rank-0 atomic save, sidecar SHA-256 | Bit-flip rejection, exact resumption |
| **Worker Interruption** | Simulated worker crash & unfinalized write | Graceful fallback to last valid checkpoint |
