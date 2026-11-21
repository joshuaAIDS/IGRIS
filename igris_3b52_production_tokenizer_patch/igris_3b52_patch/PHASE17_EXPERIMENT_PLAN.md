# IGRIS PHASE 17 — SMALL-SCALE PRETRAINING EXPERIMENT PLAN

**Document ID:** `IGRIS-PHASE17-PLAN-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Objective:** Controlled Small-Scale Pretraining Validation  
**Governance State:** LOCKED — Synthetic Pretraining Fixtures Only  

---

## 1. Executive Summary & Governance Mandates

This experiment plan establishes the protocol for executing **Phase 17 Small-Scale Pretraining Experiments** on the IGRIS Multilingual Decoder-Only Transformer. Operating strictly under the `SOLO_DEVELOPER_OWNER_REVIEW` model, Phase 17 serves as an empirical engineering validation exercise.

### 1.1 Non-Negotiable Governance Restrictions
1. **Synthetic Data Exclusivity:** All experiments execute strictly on synthetic multilingual datasets (`IGRIS-DS-PHASE17-SYNTHETIC-001`).
2. **Zero Production Ingress:** No production datasets shall be downloaded, acquired, unquarantined, or accessed.
3. **Strict Gate Preservation:** All production ingress gates and model pretraining gates remain **LOCKED** (Default-Deny).
4. **Tokenizer Immutability:** Candidate A (`ac7e18b1...`) and Candidate B (`d3a3431e...`) SHA-256 hashes must remain strictly unmodified.
5. **No Production Checkpoints:** All checkpoints generated are tagged `SYNTHETIC_TEST_ONLY` and stored in isolated experiment directories.
6. **No Silent Changes:** Model architecture ($V=32768, d=512, H_q=8, H_{kv}=4$), rotary embeddings, and normalization remain invariant.

---

## 2. Hardware Environment & Safety Guardrails

### 2.1 Hardware Profile
- **Host Workstation:** Windows 11 Enterprise (`win32`)
- **Accelerator:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (5.999 GB VRAM, Ampere Architecture, Compute Capability 8.6)
- **PyTorch / CUDA:** `2.14.1+cu130`
- **Host Physical RAM:** 15.64 GB (6.60 GB available)

### 2.2 Memory Safety Guardrails & Thresholds
- **Maximum GPU Allocation Threshold:** 5.0 GB (leaving $\approx 1.0$ GB for OS display and context buffers).
- **Graceful OOM Handling:** Every experiment encapsulates forward/backward passes in `torch.cuda.OutOfMemoryError` handlers, guaranteeing that memory boundary probes terminate cleanly, flush CUDA caches (`torch.cuda.empty_cache()`), and do not crash the runtime.
- **Fail-Closed Stop Conditions:**
  - Detection of any non-finite loss (`NaN` or `Inf`).
  - Detection of any non-finite gradient in any trainable parameter tensor.
  - Any attempt to access unauthorized paths or production network endpoints.
  - Parameter update delta diverging beyond numerical bounds.

---

## 3. Experiment Specifications

### 3.1 Experiment A: Hardware Training Throughput
- **Objective:** Measure empirical training throughput (tokens/sec and steps/sec) on actual hardware.
- **Model Target:** Production 16-Layer Transformer (96,485,888 parameters untied) and Baseline 12-Layer Transformer (68,366,848 parameters untied).
- **Configuration:** Batch size $B=2$, Sequence length $L=256$, Gradient accumulation steps = 2 (effective batch size 4).
- **Protocol:**
  - 5 warmup steps to stabilize CUDA kernels, memory allocator, and tensor core pipelines.
  - 25 timed measurement steps using precise `torch.cuda.synchronize()` and `time.perf_counter()`.
- **Recorded Metrics:**
  - Tokens per second ($\text{Tokens/sec} = \frac{B \times L}{\Delta t}$).
  - Steps per second ($\text{Steps/sec} = \frac{1}{\Delta t}$).
  - Average, median, minimum, and maximum step durations.
  - GPU allocated memory, reserved memory, and peak memory usage.
  - Host RAM utilization (via `ctypes.windll.kernel32.GlobalMemoryStatusEx`).
  - Data loading and tensor preparation overhead.

### 3.2 Experiment B: Training Stability & Numerical Dynamics
- **Objective:** Verify optimization stability, loss progression, and gradient clipping behavior.
- **Configuration:** 50 optimization steps on synthetic multilingual batches.
- **Hyperparameters:** AdamW ($\text{lr}=5 \times 10^{-4}$, $\beta_1=0.9, \beta_2=0.95$, weight decay = 0.01), Cosine schedule with 5 warmup steps, Gradient clipping max norm = 1.0.
- **Recorded Metrics:**
  - Step-by-step cross-entropy loss.
  - Unclipped gradient L2 norm $\|\mathbf{g}\|_2$.
  - Clipped gradient L2 norm.
  - Learning rate progression.
  - Parameter weight update norm $\|\mathbf{W}_{t} - \mathbf{W}_{t-1}\|_2$.
  - Real-time `isnan()` and `isinf()` verification.

### 3.3 Experiment C: Batch Size and Sequence Length Exploration Grid
- **Objective:** Explore the empirical trade-offs between batch size, sequence length, VRAM consumption, and throughput.
- **Test Matrix:**
  1. $B=1, L=256$ (256 tokens/step)
  2. $B=2, L=256$ (512 tokens/step)
  3. $B=4, L=256$ (1024 tokens/step)
  4. $B=1, L=512$ (512 tokens/step)
  5. $B=2, L=512$ (1024 tokens/step)
  6. $B=4, L=512$ (2048 tokens/step)
  7. $B=1, L=1024$ (1024 tokens/step)
  8. $B=2, L=1024$ (2048 tokens/step)
  9. $B=1, L=2048$ (2048 tokens/step)
- **Protocol:** Each grid point runs 10 steps. Peak VRAM is recorded using `torch.cuda.max_memory_allocated()`. Cache is reset before and after each configuration.

### 3.4 Experiment D: Checkpoint Reliability & Reproducibility
- **Objective:** Validate atomic checkpoint writing, SHA-256 integrity hashing, and exact resumption.
- **Protocol:**
  - Run continuous 20 steps, persisting checkpoint at step 10.
  - Compute SHA-256 of checkpoint binary and verify against sidecar JSON.
  - Instantiate fresh pipeline, restore from step 10 checkpoint, and train to step 20.
  - Compare model logits, optimizer momentum states, and loss curves between uninterrupted and resumed runs.
- **Success Criteria:** Exact logit equivalence ($\text{Max Diff} < 10^{-5}$) and identical step restoration.

### 3.5 Experiment E: Interruption Recovery & Fault Tolerance
- **Objective:** Simulate a hard interruption during checkpoint serialization and verify graceful recovery.
- **Protocol:**
  - Simulate interruption by injecting a corrupted/incomplete temporary file (`chk_step_000015.pt.tmp`).
  - Trigger recovery mechanism: verify that the incomplete `.tmp` file is recognized as unfinalized and rejected.
  - Validate that the previous clean checkpoint (`chk_step_000010.pt`) remains completely intact and valid.
  - Resume execution from the last intact checkpoint to the final step target.
  - Verify audit logs reflect interruption detection and clean resumption.

---

## 4. Hardware Benchmarking & Projection Methodology

### 4.1 Strict Distinction Between Measured and Projected Figures
- **Measured Data:** Metrics obtained directly from timed execution steps on the NVIDIA RTX 3050 Laptop GPU.
- **Calculated Projections:** Extrapolations based on empirical sustained throughput:
  $$\text{Estimated Time (hours)} = \frac{\text{Target Token Count}}{\text{Measured Sustained Tokens/sec} \times 3600}$$
- **Projections Target:** 100 Million, 1 Billion, 5 Billion, and 10 Billion tokens.
- **Unverified Estimates & Planning Figures:** The Phase 16 theoretical figure (~7.0 hours for 1B tokens) will be critically contrasted against actual measured throughput.

---

## 5. Execution Pipeline & Deliverables Workflow

```
[Phase 17 Synthetic Data Generator]
  --> Generates 500 multilingual records (96,184 tokens)
  --> Writes PHASE17_SYNTHETIC_DATA_MANIFEST.json
         |
         v
[Phase 17 Experiment Runner]
  --> Experiment A: Throughput & Latency (RTX 3050)
  --> Experiment B: Stability & Loss Dynamics (50 steps)
  --> Experiment C: (B, L) Exploration Grid
  --> Experiment D: Atomic Checkpointing & Resumption
  --> Experiment E: Interruption Recovery Simulation
         |
         +--> PHASE17_HARDWARE_BENCHMARK.json
         +--> PHASE17_TRAINING_METRICS.json
         |
         v
[Reports & Test Suites]
  --> PHASE17_CHECKPOINT_INTEGRITY_REPORT.md
  --> PHASE17_RECOVERY_TEST_REPORT.md
  --> PHASE17_RESOURCE_UTILIZATION_REPORT.md
  --> PHASE17_SECURITY_AND_GOVERNANCE_REPORT.md
  --> PHASE17_COMPLETION_REPORT.md
  --> tests/test_phase17_experiments.py
```
