# IGRIS PHASE 16 — MODEL RESOURCE & HARDWARE ESTIMATION REPORT

**Document ID:** `IGRIS-PHASE16-RES-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Status:** Resource Footprint Audited & Sizing Verified  

---

## 1. Executive Summary

This report delivers a rigorous theoretical and empirical estimation of memory, compute, and hardware resources required to train the **IGRIS Multilingual Decoder-Only Transformer**. The analysis evaluates the **Target 16-Layer Production Model** (96,485,888 parameters) and the **Baseline 12-Layer Model** (68,366,848 parameters untied / 51,589,632 tied) against both the local developer machine and enterprise cloud hardware profiles.

---

## 2. Host Machine Profile (Empirical Measurement)

The local host environment was profiled via PyTorch hardware diagnostics (`scripts/model_resource_estimator.py`):

| Diagnostic Attribute | Measured Host Value | Notes |
| :--- | :--- | :--- |
| **Operating System** | `win32` (Windows 11 Enterprise) | Developer Workstation |
| **PyTorch Version** | `2.14.1+cu130` | Official CUDA 13.0 build |
| **CUDA Acceleration** | `True` (Operational) | GPU available for training |
| **GPU Model** | `NVIDIA GeForce RTX 3050 6GB Laptop GPU` | Ampere Architecture |
| **Total VRAM** | **5.999 GB** (6,441,926,656 bytes) | Physical VRAM limit |
| **Compute Capability** | `8.6` | Tensor Core support (FP16 / BF16) |

---

## 3. Memory Sizing & Breakdown

During model training, GPU memory comprises five distinct allocations:
$$M_{\text{total}} = M_{\text{weights}} + M_{\text{gradients}} + M_{\text{optimizer}} + M_{\text{activations}} + M_{\text{framework}}$$

### 3.1 Static Training Memory Components (Model, Gradients, Optimizer)

| Memory Component | Bit Precision | Formula | Production 16L Model (96.5M) | Baseline 12L Model (68.4M) |
| :--- | :--- | :--- | :--- | :--- |
| **Model Weights** | FP32 | $4 \times P$ | 368.1 MB | 260.8 MB |
| **Model Weights** | FP16 / BF16 | $2 \times P$ | 184.0 MB | 130.4 MB |
| **Gradients** | FP32 | $4 \times P_{\text{trainable}}$ | 368.1 MB | 260.8 MB |
| **Gradients** | FP16 / BF16 | $2 \times P_{\text{trainable}}$ | 184.0 MB | 130.4 MB |
| **AdamW Optimizer** | FP32 States | $8 \times P_{\text{trainable}}$ | 736.1 MB | 521.6 MB |
| **AdamW (Mixed Master)** | Mixed Precision | $12 \times P_{\text{trainable}}$ | 1,104.2 MB | 782.4 MB |
| **Framework / CUDA Overhead** | Base Allocation | Context + kernels | 750.0 MB | 750.0 MB |
| **Subtotal (Static VRAM)** | Mixed + AdamW | Weights + Grads + Opt + Base | **2,222.2 MB (~2.17 GB)** | **1,792.8 MB (~1.75 GB)** |

### 3.2 Dynamic Activation Memory Breakdown

Activation memory scales with batch size $B$, sequence length $L$, hidden dimension $d_{\text{model}}$, intermediate dimension $d_{\text{ffn}}$, and layer count $N_{\text{layers}}$:

| Batch Size ($B$) | Sequence Length ($L$) | Activation Memory (Standard) | Activation Memory (Checkpointed) | Total VRAM (16L Model, FP16) | Local 6GB GPU Feasible? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $B = 1$ | $L = 512$ | 192.5 MB | 45.2 MB | **2.36 GB** | **YES (Feasible)** |
| $B = 2$ | $L = 512$ | 385.0 MB | 90.4 MB | **2.55 GB** | **YES (Feasible)** |
| $B = 4$ | $L = 512$ | 770.0 MB | 180.8 MB | **2.92 GB** | **YES (Feasible)** |
| $B = 8$ | $L = 512$ | 1,540.0 MB | 361.6 MB | **3.68 GB** | **YES (Feasible)** |
| $B = 1$ | $L = 2048$ | 1,512.5 MB | 210.4 MB | **3.65 GB** | **YES (Feasible)** |
| $B = 2$ | $L = 2048$ | 3,025.0 MB | 420.8 MB | **5.13 GB** | **YES (Feasible)** |
| $B = 4$ | $L = 2048$ | 6,050.0 MB | 841.6 MB | **8.17 GB** (Std) / **3.04 GB** (Ckpt) | **YES (with Activation Ckpt)** |

**Local Hardware Feasibility Finding:**
The local NVIDIA GeForce RTX 3050 6GB Laptop GPU **can comfortably execute training runs up to sequence length $L=512$ with batch sizes $B \le 8$ without activation checkpointing** (utilizing $< 3.7$ GB of 6.0 GB). For full context length $L=2048$, training is feasible with batch size $B=1$ or $B=2$, or with activation checkpointing enabled at $B=4$.

---

## 4. Compute Budget & Training Duration Estimation

Following the standard scaling laws ($6P$ floating point operations per token for non-embedding parameters $P_{\text{non-embed}} = 62,931,456$):

$$\text{FLOPs/token} = 6 \times 62,931,456 = 377,588,736 \text{ FLOPs}$$

Assuming an empirical Model FLOPs Utilization (MFU) of 40% on the RTX 3050 Laptop GPU (~15 achieved TFLOPS in mixed precision):

| Training Token Budget | Total Floating Point Operations (FLOPs) | Estimated Training Time (RTX 3050 Laptop GPU) | Estimated Training Time (Single A100 80GB) | Estimated Training Time (8x A100 Cluster) |
| :--- | :--- | :--- | :--- | :--- |
| **100 Million Tokens** | $3.78 \times 10^{16}$ FLOPs | 0.7 hours (42 minutes) | 3.5 minutes | < 30 seconds |
| **1 Billion Tokens** | $3.78 \times 10^{17}$ FLOPs | 7.0 hours (0.3 days) | 35.0 minutes | 4.4 minutes |
| **5 Billion Tokens** | $1.89 \times 10^{18}$ FLOPs | 35.0 hours (1.5 days) | 2.9 hours | 22.0 minutes |
| **10 Billion Tokens** | $3.78 \times 10^{18}$ FLOPs | 70.0 hours (2.9 days) | 5.8 hours | 44.0 minutes |

---

## 5. Storage & Checkpoint Footprint

| Artifact Type | Per-Unit Size | Frequency | Storage Needed (10B Tokens) |
| :--- | :--- | :--- | :--- |
| **Model Checkpoint (`.pt`)** | ~368 MB (FP32) / ~184 MB (FP16) | Every 1,000 steps (top 3 kept) | ~1.1 GB |
| **Metadata Sidecar (`.json`)** | ~2 KB | Per checkpoint | < 1 MB |
| **Training Audit Log (`.jsonl`)** | ~150 bytes / step | Continuous streaming | ~15 MB |
| **Tokenized Preprocessed Data** | 2 bytes / token (`uint16`) | Static pre-tokenized bin | ~20 GB (for 10B tokens) |

---

## 6. Sizing Recommendations

1. **Development & Prototyping:** The existing developer workstation (RTX 3050 6GB) is fully sufficient for pipeline verification, synthetic validation, ablation experiments, and small-scale pilot runs.
2. **Production Pretraining Recommendation:** When human governance authorization is granted in future phases, executing pretraining on 1–4x enterprise cloud accelerators (e.g. NVIDIA A100 / H100) will reduce 10-billion-token training time from 3 days to under 6 hours.
