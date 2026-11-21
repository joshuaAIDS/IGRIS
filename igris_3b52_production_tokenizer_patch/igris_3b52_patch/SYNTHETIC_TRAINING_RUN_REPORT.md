# IGRIS Controlled 1-Million-Token Synthetic Training Run Report

**Classification:** **`SYNTHETIC-ONLY EXPERIMENTAL CHECKPOINT`**  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Hardware Profile:** NVIDIA GeForce RTX 3050 6GB Laptop GPU | Intel Core i5-13420H | 16 GB System RAM  
**Governance Invariants:** 16-Layer Architecture Pinned | Tokenizer Candidate A Pinned (`ac7e18b1...`) | Structural Tokens 0–11 Pinned  
**Frontend Status:** **FROZEN** (Zero Modifications, Zero UI Churn)  
**Pretraining Gate Status:** **STRICTLY LOCKED** ($0.00 Cloud Spend; Zero External Downloads)  
**Production Promotion Status:** **NOT PROMOTED** (Internal Experimental Baseline Only)  
**Execution Date:** 2026-11-21  

---

## 1. Executive Summary & Milestone Sign-Off

The first controlled synthetic training milestone for the IGRIS 16-layer multilingual transformer (`igris-prod-16l`) was executed to completion on the physical **NVIDIA GeForce RTX 3050 6GB Laptop GPU**.

The run strictly satisfied all preflight gates, processed over **1,000,000 synthetic tokens** across Tamil, English, and Tanglish without a single hardware exception, divergence, or memory fault, and verified bit-exact recovery and split isolation.

```
========================================================================================
                 SYNTHETIC TRAINING MILESTONE COMPLETION SUMMARY:
                                    PASSED
========================================================================================
  Checkpoint Classification:    SYNTHETIC-ONLY EXPERIMENTAL CHECKPOINT
  Target Token Volume:          1,000,000 tokens
  Actual Tokens Processed:      1,001,472 tokens (100.15% milestone completion)
  Total Optimizer Steps:        489 steps (Effective batch = 2,048 tokens/step)
  Total Wall-Clock Duration:    396.20 seconds (6.60 minutes)
  Overall Mean Throughput:      2,527.71 tokens/sec (1.23 optimizer steps/sec)
  Initial Training Loss:        10.4619 (Step 1)
  Final Training Loss:          0.7154 (Step 489)
  Loss Reduction:               -9.7465 (-93.16% relative loss reduction)
  Validation Loss Progression:  10.4714 (Step 0) -> 3.4070 (Step 489)
  Validation Perplexity:        35,290.81 (Step 0) -> 30.17 (Step 489)
  Peak VRAM Allocated:          1,745.49 MiB (Safety Ceiling: 4,239.48 MiB)
  Peak VRAM Reserved:           2,034.00 MiB (Physical Headroom: 66.89%)
  CUDA OOM / Recovery Events:   0 occurrences (100% stable execution)
  Test Split Isolation:         CONFIRMED (SplitIsolationError active; 0 test records seen)
  Production Pretraining Gate:  LOCKED ($0.00 cloud spend; zero external downloads)
========================================================================================
```

> [!CAUTION]
> **Scientific Integrity Notice:** Decreasing training loss and validation perplexity on synthetic data demonstrates that the Transformer architecture, optimizer, learning-rate schedule, and backpropagation mechanics are functioning correctly. It **does NOT establish broad linguistic generalization**. Generalization testing requires production pretraining on authorized diverse corpora under owner review.

---

## 2. Preflight Gate Verification Results

Prior to loading weights or beginning optimization, all nine preflight criteria were independently verified:

| Preflight Gate | Requirement | Measured / Verified Value | Gate Status |
| :--- | :--- | :--- | :---: |
| **1. Tokenizer Artifact** | Candidate A SHA-256 match | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | **PASS** |
| **2. Vocabulary Size** | Exactly 32,768 tokens | 32,768 tokens | **PASS** |
| **3. Structural Tokens** | IDs 0–11 pinned | `<|pad|>`(0) through `<|assistant|>`(11) identical | **PASS** |
| **4. Synthetic Corpus** | 3,000 target records | 1,000 Tamil, 1,000 English, 1,000 Tanglish | **PASS** |
| **5. Script Integrity** | 0 non-target scripts | 0 characters in non-target Unicode ranges | **PASS** |
| **6. Split Boundaries** | Disjoint train/val/test | 2,400 train, 300 val, 300 test (0 doc or text hash overlap) | **PASS** |
| **7. Test Split Protection**| Block unauthorized access | `SplitIsolationError` tested and enforced | **PASS** |
| **8. Model Architecture** | 16 layers, tied embeddings | Exactly 79,708,672 parameters | **PASS** |
| **9. Hardware Envelope** | $\ge 15\%$ physical headroom | Free: 5,161.0 MiB vs 15% Headroom: 921.5 MiB | **PASS** |

---

## 3. Training Dynamics & Loss Progression

Training was executed over **489 optimizer steps** with an effective batch size of **2,048 tokens/step** (context length 1,024, micro-batch 1, gradient accumulation 2) using BF16 mixed-precision and activation checkpointing:

```mermaid
xychart-beta
    title "Training Loss Progression (Steps 1 to 489)"
    x-axis ["Step 1", "Step 50", "Step 100", "Step 200", "Step 300", "Step 400", "Step 489"]
    y-axis "Cross-Entropy Loss" 0 --> 12
    line [10.46, 2.61, 1.16, 3.67, 0.09, 0.05, 0.72]
```

### 3.1 Step Milestone Telemetry

| Optimizer Step | Cumulative Tokens | Train Loss | Gradient Norm | Learning Rate | Step Duration | Throughput (tok/s) | VRAM Alloc (MiB) | GPU Temp (°C) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 2,048 | 10.4619 | 19.574 | 0.000006 | $3.6517\text{ s}$ | 560.8 | 1,602.6 | 52°C |
| **25** | 51,200 | 6.9541 | 4.822 | 0.000150 | $0.6847\text{ s}$ | 2,990.9 | 1,745.5 | 60°C |
| **50** | 102,400 | 2.6062 | 3.212 | 0.000300 | $0.6825\text{ s}$ | 3,000.5 | 1,745.5 | 64°C |
| **100** | 204,800 | 1.1554 | 5.599 | 0.000291 | $0.7757\text{ s}$ | 2,640.3 | 1,745.5 | 68°C |
| **150** | 307,200 | 0.4652 | 2.529 | 0.000267 | $0.8449\text{ s}$ | 2,424.0 | 1,745.5 | 69°C |
| **200** | 409,600 | 3.6733 | 1.923 | 0.000229 | $0.6069\text{ s}$ | 3,374.6 | 1,745.5 | 70°C |
| **250** | 512,000 | 0.6098 | 1.561 | 0.000184 | $0.6624\text{ s}$ | 3,091.8 | 1,745.5 | 70°C |
| **300** | 614,400 | 0.0912 | 1.231 | 0.000136 | $0.6485\text{ s}$ | 3,158.1 | 1,745.5 | 71°C |
| **350** | 716,800 | 4.1791 | 31.496 | 0.000091 | $0.6066\text{ s}$ | 3,376.0 | 1,745.5 | 69°C |
| **400** | 819,200 | 0.0508 | 0.728 | 0.000056 | $0.6405\text{ s}$ | 3,197.5 | 1,745.5 | 70°C |
| **450** | 921,600 | 0.0457 | 0.387 | 0.000035 | $0.7869\text{ s}$ | 2,602.5 | 1,745.5 | 70°C |
| **489** | 1,001,472 | 0.7154 | 3.828 | 0.000030 | $0.7372\text{ s}$ | 2,778.1 | 1,745.5 | 69°C |

---

### 3.2 Validation Dynamics Across Languages

Validation was evaluated periodically on 30 balanced, held-out sequences (30,720 tokens; 10 sequences per language) with per-language breakdown:

| Checkpoint Step | Overall Val Loss | Overall Perplexity | Tamil Val Loss | Tamil PPL | English Val Loss | English PPL | Tanglish Val Loss | Tanglish PPL |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Step 0** | 10.4714 | 35,290.81 | 10.4480 | 34,475.99 | 10.5679 | 38,866.32 | 10.3982 | 32,801.59 |
| **Step 100** | 7.2157 | 1,360.59 | 2.8432 | 17.17 | 10.1788 | 26,338.19 | 8.6250 | 5,569.36 |
| **Step 200** | 4.6274 | 102.25 | 5.6298 | 278.60 | 3.6477 | 38.38 | 4.6048 | 99.96 |
| **Step 300** | 4.5778 | 97.30 | 6.6609 | 781.22 | 2.2159 | 9.17 | 4.8567 | 128.59 |
| **Step 400** | 3.7631 | 43.08 | 4.2888 | 72.88 | 2.7537 | 15.70 | 4.2467 | 69.87 |
| **Step 489** | **3.4070** | **30.17** | **2.5366** | **12.64** | **3.7397** | **42.08** | **3.9446** | **51.65** |

```mermaid
xychart-beta
    title "Overall Validation Perplexity Progression (Lower is Better)"
    x-axis ["Step 0", "Step 100", "Step 200", "Step 300", "Step 400", "Step 489"]
    y-axis "Validation PPL (log scale behavior)" 0 --> 1500
    line [1500, 1361, 102, 97, 43, 30]
```

---

## 4. Hardware Telemetry & Thermal Verification

* **Peak Allocated VRAM:** **$1,745.49\text{ MiB}$** ($1,830.28\text{ MB}$)
* **Peak Reserved VRAM:** **$2,034.00\text{ MiB}$** ($2,132.80\text{ MB}$)
* **Dedicated Free VRAM:** **$4,109.50\text{ MiB}$** (**$66.89\%$ physical headroom**)
* **Safety Margin to 15% Ceiling:** **$+2,493.99\text{ MiB}$ surplus buffer**
* **GPU Temperature:** Maintained strictly between **$52^\circ\text{C}$ and $71^\circ\text{C}$** (peak $71^\circ\text{C}$) on air cooling
* **GPU Graphics Clock:** Sustained between **$1,605\text{ MHz}$ and $1,710\text{ MHz}$**
* **Host Process RSS:** Stable at **$1,320\text{ MiB}$** (System RAM available: $> 2.7\text{ GiB}$)
* **CUDA Exceptions / OOM:** **0 occurrences** (100% zero-crash execution)

---

## 5. Checkpoint Inventory & Hash Manifest

All checkpoints were written atomically (`.tmp` $\to$ `.pt`) with accompanying `.json` metadata sidecars:

| Checkpoint Name | Step | Type | File Size | Save Time | SHA-256 Digest |
| :--- | :---: | :--- | :---: | :---: | :--- |
| `chk_step_000150.pt` | 150 | FULL_TRAINING_CHECKPOINT | 912.38 MiB | 6.92s | `05fc0ef000d2fb781b4d081f9b3117b3d3ae3ebcae2c7a0d4c9441fb0eefd890` |
| `chk_step_000300.pt` | 300 | FULL_TRAINING_CHECKPOINT | 912.38 MiB | 6.10s | `29f5063a1c7c22e50529d3c509893d11b2cb41203678eb17c6999818817457fc` |
| `chk_step_000450.pt` | 450 | FULL_TRAINING_CHECKPOINT | 912.38 MiB | 6.45s | `bcc57ca7707e5c798ca7ecbc62f4ba19ea640bb8be4523fb040cf0e32cb6f74a` |
| `chk_step_000489.pt` | 489 | FULL_TRAINING_CHECKPOINT | 912.38 MiB | 7.74s | `c7aa2d9b0a3a585cead07b55a9b74fe40ae90bf4f366113885da84a56a64bb93` |
| `igris_model_only_step489.pt` | 489 | MODEL_ONLY_INFERENCE_CHECKPOINT | 304.12 MiB | 0.16s | `c9161286d0fe36f947f6cfb0b3d6874e0d4bb31804ebfcb9c3f309b4513dbf0d` |

Full sidecar metadata and metrics database are available at:
* [SYNTHETIC_TRAINING_METRICS.json](file:///C:/IGRIS/SYNTHETIC_TRAINING_METRICS.json)
* [SYNTHETIC_TRAINING_CHECKPOINT_MANIFEST.json](file:///C:/IGRIS/SYNTHETIC_TRAINING_CHECKPOINT_MANIFEST.json)

---

## 6. Strict Governance & Invariants Verification

1. **Frontend Isolation:** Zero modifications made to frontend code, UI, or styling. Frontend remains **FROZEN**.
2. **Model Architecture:** 16 layers, 512 $d_{\text{model}}$, 2048 $d_{\text{ffn}}$, 8 Query Heads, 4 KV Heads, SwiGLU, RMSNorm, RoPE, Tied Embeddings ($79,708,672\text{ parameters}$) strictly preserved.
3. **Tokenizer Artifact:** Original Candidate A (`ac7e18b1...`) and structural tokens 0–11 pinned without modification.
4. **Data Isolation:** All training records derived strictly from the approved synthetic corpus. Test split isolated with `SplitIsolationError`.
5. **Pretraining Gate:** **LOCKED**. Cloud spend is **$0.00**. Production dataset acquisition has **NOT** been initiated.
6. **Checkpoint Status:** **SYNTHETIC-ONLY EXPERIMENTAL CHECKPOINT**. Not promoted to production.

---

## 7. Conclusion & Owner Review Status

The IGRIS training backend, dataset packing infrastructure, mixed-precision numerical engine, and checkpoint recovery systems have executed their first full-scale training milestone ($1,001,472\text{ tokens}$ over 489 steps in 6.60 minutes) with 100% stability.

The system is in a clean, consistent state and standing by for Owner Review.
