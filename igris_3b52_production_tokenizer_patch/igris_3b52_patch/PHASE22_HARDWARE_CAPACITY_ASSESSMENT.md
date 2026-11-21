# PHASE 22 — HARDWARE & SYSTEM CAPACITY ASSESSMENT
## Forensic Evaluation of Host Hardware, CUDA Environment, Storage Deficits, and Cloud Infrastructure Planning

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22  

---

## 1. Executive Summary

Phase 22 conducted a comprehensive probe of the physical host environment to establish hardware readiness across compute, memory, and storage dimensions.

### Critical Bottom-Line Findings:
1. **Storage Deficit (Severe Blocker for Local Storage):**
   - **Measured Free Disk Space (C:\):** **80.73 GiB** (86,686,535,680 bytes).
   - **IndicCorp v2 Raw Transfer Size:** **171.08 GiB** (183,700,000,000 bytes).
   - **Deficit:** Available local SSD storage is **less than half** the size of the raw dataset download alone! Full local dataset acquisition, staging, and tokenization is physically **impossible** on local host storage without catastrophic disk exhaustion.
2. **GPU VRAM & Compute Feasibility:**
   - **Physical GPU:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (Ampere compute capability 8.6, 6.00 GiB VRAM).
   - **Model Footprint:** IGRIS 96.5M parameter model requires ~1.51 GiB static VRAM in BF16 training mode (weights + gradients + AdamW + master weights). Activations fit comfortably inside 6.00 GiB VRAM with FlashAttention / SDPA and gradient checkpointing.
   - **Throughput Limitation:** Training on 5.5B tokens locally would require ~**13.6 days** of continuous 100% GPU saturation, risking severe laptop thermal throttling and hardware degradation.
3. **Strategic Cloud Recommendation:**
   - Acquisition, quarantine validation, text cleaning, tokenization, and pretraining must be executed on **ephemeral cloud infrastructure** (estimated total cost: **~$40 to $75**), preserving local laptop hardware integrity.

---

## 2. Measured Physical Host Hardware & Software Environment

```
+-----------------------------------+---------------------------------------------------------------------------+
| Environmental Parameter           | Measured Value & Configuration                                            |
+-----------------------------------+---------------------------------------------------------------------------+
| Operating System                  | Microsoft Windows 10 (10.0.26300 AMD64)                                   |
| CPU Processor                     | Intel64 Family 6 Model 186 Stepping 2, GenuineIntel                       |
| System Memory (RAM)               | Total: 15.64 GiB (16,791,048,192 B) | Available: 3.50 GiB (3,760,619,520 B)   |
| Memory Load                       | 77% active load at measurement                                            |
| Local Storage (C:\ NVMe SSD)      | Total: 475.79 GiB | Used: 395.06 GiB | Free: 80.73 GiB (86,686,535,680 B)   |
| Secondary Disks (D:\, E:\)       | None Present                                                              |
| Dedicated GPU                     | NVIDIA GeForce RTX 3050 6GB Laptop GPU                                    |
| GPU Compute Architecture          | NVIDIA Ampere (Compute Capability 8.6, 20 Streaming Multiprocessors)       |
| GPU Dedicated VRAM                | 6,441,926,656 bytes (6.00 GiB)                                            |
| Native BF16 Support               | Supported (`torch.cuda.is_bf16_supported() == True`)                      |
| Python Runtime                    | Python 3.11.9 (64-bit)                                                    |
| PyTorch Framework                 | PyTorch 2.14.1+cu130 (CUDA 13.0, cuDNN 92400)                             |
+-----------------------------------+---------------------------------------------------------------------------+
```

---

## 3. Storage Capacity Deficit Analysis

The complete dataset and training lifecycle requires five distinct storage tiers:

```
+----+----------------------------------+-----------------------+-----------------------+---------------------------------------+
| #  | Lifecycle Storage Stage          | Required Space (Dec)  | Required Space (Bin)  | Storage Assessment on Local Host      |
+----+----------------------------------+-----------------------+-----------------------+---------------------------------------+
| 1  | Raw Ingress Quarantine Staging   | 183.70 GB             | 171.08 GiB            | DEFICIT (-90.35 GiB vs Free Space)    |
| 2  | Quarantine Integrity & Expansion | 210.00 GB             | 195.58 GiB            | DEFICIT (-114.85 GiB)                 |
| 3  | Cleaned & Deduplicated Corpus    | 130.00 GB             | 121.07 GiB            | DEFICIT (-40.34 GiB)                  |
| 4  | Tokenized Binary Shards (uint16) | 12.00 GB              | 11.18 GiB             | Fits in isolation, but not concurrent |
| 5  | Training Checkpoints (10 ckpts)  | 15.00 GB              | 13.97 GiB             | Fits in isolation, but not concurrent |
| 6  | System Scratch & OS Headroom     | 50.00 GB              | 46.57 GiB             | Minimum OS stability requirement      |
+----+----------------------------------+-----------------------+-----------------------+---------------------------------------+
|    | CUMULATIVE CONCURRENT PEAK       | 532.40 GB             | 495.84 GiB            | TOTAL DEFICIT: -415.11 GiB            |
|    | SEQUENTIAL PURGE PEAK            | 398.70 GB             | 371.32 GiB            | TOTAL DEFICIT: -290.59 GiB            |
|    | MEASURED LOCAL SSD FREE          | 86.69 GB              | 80.73 GiB             | INSUFFICIENT FOR ANY RAW DATASET STAGE|
+----+----------------------------------+-----------------------+-----------------------+---------------------------------------+
```

> [!WARNING]
> Attempting to download even a single large IndicCorp subset (e.g. Hindi, 80.1 GB across 3 shards) locally would push the host SSD below 5% free space, triggering Windows system instability and swap failure.

---

## 4. GPU VRAM & Training Arithmetic for IGRIS 96.5M

### 4.1. Static Model Memory Footprint
For IGRIS 3B52 ($d=512$, $L=16$, $H=8$, $H_{kv}=4$, $d_{ff}=2048$, $V=32,768$, Total params: $96,485,888$):
- **Model Weights (BF16, 2 bytes/param):** $96,485,888 	imes 2 = 192.97 	ext{ MB}$.
- **Gradients (BF16, 2 bytes/param):** $96,485,888 	imes 2 = 192.97 	ext{ MB}$.
- **AdamW Optimizer States (FP32 momentum + variance, 8 bytes/param):** $96,485,888 	imes 8 = 771.89 	ext{ MB}$.
- **Master Weights (FP32, 4 bytes/param):** $96,485,888 	imes 4 = 385.94 	ext{ MB}$.
- **Total Static Memory:** $192.97 + 192.97 + 771.89 + 385.94 = 1,543.77 	ext{ MB} pprox \mathbf{1.51 	ext{ GiB}}$.

### 4.2. Dynamic Activation & Workspace Budget
- **Available VRAM Headroom:** $6.00 	ext{ GiB} - 1.51 	ext{ GiB} = \mathbf{4.49 	ext{ GiB}}$.
- With sequence length $S = 1024$, micro-batch size $B = 4$, and native PyTorch Scaled Dot Product Attention (FlashAttention / SDPA) with gradient checkpointing, peak activation memory is $pprox 1.20 	ext{ GiB}$.
- **Conclusion:** The model technically fits within 6GB VRAM for small micro-batches.

### 4.3. Wall-Clock Compute & Thermal Constraints
- **Training Tokens:** $pprox 5.5 	imes 10^9$ tokens across the 7 languages.
- **Compute per Token:** $6 	imes N pprox 6 	imes 96.5 	imes 10^6 pprox 5.79 	imes 10^8 	ext{ FLOPs/token}$.
- **Total Training FLOPs:** $5.79 	imes 10^8 	imes 5.5 	imes 10^9 pprox 3.18 	imes 10^{18} 	ext{ FLOPs} = 3.18 	ext{ EFLOPs}$.
- **RTX 3050 Laptop GPU Effective Throughput:** At 30% MFU on 20 SMs, effective throughput is $pprox 2.7 	ext{ TFLOPS} = 2.7 	imes 10^{12} 	ext{ FLOP/s}$.
- **Estimated Local Run Time:**
  $$	ext{Time} = rac{3.18 	imes 10^{18} 	ext{ FLOPs}}{2.7 	imes 10^{12} 	ext{ FLOP/s}} pprox 1,178,000 	ext{ seconds} pprox \mathbf{13.6 	ext{ days}}.$$
- Continuous 14-day execution on a laptop GPU is unviable due to acoustic noise, thermal throttling (dropping clocks by 30–50%), and component wear.

---

## 5. Ephemeral Cloud Infrastructure Options (Read-Only Planning)

To resolve the local storage deficit and compute bottlenecks, the following cloud provisioning profiles have been modeled:

```
+-------------------+---------------------------+---------------+-------------------+-----------------------+-------------------+
| Profile Name      | Cloud Provider Options    | GPU & VRAM    | Training Duration | Hourly Rate           | Total Cost Est.   |
+-------------------+---------------------------+---------------+-------------------+-----------------------+-------------------+
| Profile 1 (Budget)| RunPod / Lambda / Vast.ai | 1x RTX 4090   | ~1.8 days (44 hrs)| $0.44 / hr            | ~$19.50           |
| Profile 2 (Fast)  | Lambda / GCP / RunPod     | 1x A100 (80GB)| ~7 hours          | $1.89 / hr            | ~$13.25           |
| Profile 3 (Multi) | GCP / AWS / Lambda        | 4x A100 (80GB)| ~1.8 hours        | $7.56 / hr            | ~$13.60           |
| Attached Storage  | Cloud NVMe (1 TB)         | 1 TB gp3/NVMe | Staging (3 days)  | $0.10 / GB-mo ($0.01) | ~$10.00           |
+-------------------+---------------------------+---------------+-------------------+-----------------------+-------------------+
| ESTIMATED TOTAL   | Full Pipeline (End-to-End)| Cloud Compute | Complete Run      | Compute + Storage     | **~$35 – $65**    |
+-------------------+---------------------------+---------------+-------------------+-----------------------+-------------------+
```

> [!NOTE]
> No cloud resources have been provisioned or purchased during Phase 22. These figures serve as cost-benefit planning evidence for the Project Owner.
