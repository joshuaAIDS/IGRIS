# PHASE 22A — HARDWARE ENVIRONMENT VERIFICATION
## Forensic Host Diagnostic Reconciliation and VRAM Workload Boundary Analysis

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22A  
**Status:** MEASURED EVIDENCE CERTIFIED  

---

## 1. Executive Summary

Phase 22A verifies and reconciles the physical hardware diagnostics of the developer workstation.

All figures presented below represent **directly measured system values** captured via Windows Management Instrumentation (WMI), Win32 API calls (`ctypes.windll.kernel32`), and PyTorch CUDA runtime introspection.

### Core Hardware Diagnostics Summary:
- **Processor:** 13th Gen Intel(R) Core(TM) i5-13420H (8 physical cores [4 Performance + 4 Efficient], 12 logical threads).
- **Physical RAM:** 16,791,048,192 bytes (**15.64 GiB**), with ~4.92 GiB available (~70% load).
- **GPU Accelerator:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (Ampere `sm_86`, Compute Capability 8.6, 20 SMs, **6.00 GiB VRAM**).
- **CUDA & PyTorch Stack:** PyTorch `2.14.1+cu130`, CUDA `13.0`, cuDNN `92400`. Native BF16 supported.
- **Primary Storage (C:\):** NTFS Volume, Total: 510,880,903,168 bytes (**475.79 GiB**), Free: 86,449,737,728 bytes (**80.51 GiB**).

---

## 2. Measured Diagnostic Specification Matrix

```
+-----------------------------------+---------------------------------------------------------------------------+
| Diagnostic Attribute              | Measured System Specification                                             |
+-----------------------------------+---------------------------------------------------------------------------+
| CPU Model                         | 13th Gen Intel(R) Core(TM) i5-13420H                                      |
| CPU Architecture / Stepping       | Intel64 Family 6 Model 186 Stepping 2, GenuineIntel (AMD64)               |
| CPU Physical Cores                | 8 Cores (4 Performance Cores @ up to 4.6 GHz + 4 Efficient Cores)         |
| CPU Logical Processors            | 12 Threads (4 P-cores hyperthreaded [8] + 4 E-cores [4])                  |
| Host RAM Total                    | 16,791,048,192 bytes (15.64 GiB / 16.79 GB decimal)                       |
| Host RAM Available                | 4,925,583,360 bytes (4.59 GiB / 4.93 GB decimal)                          |
| System Memory Load                | 70% active system utilization at benchmark                               |
| Dedicated GPU Model               | NVIDIA GeForce RTX 3050 6GB Laptop GPU                                    |
| Dedicated VRAM Total              | 6,441,926,656 bytes (6.00 GiB / 6.44 GB decimal)                          |
| GPU Architecture & Compute        | NVIDIA Ampere Architecture, Compute Capability 8.6                        |
| Streaming Multiprocessors (SMs)   | 20 SMs (2,560 CUDA cores, 80 Tensor Cores)                                |
| Native Bfloat16 (BF16) Support    | Supported (`torch.cuda.is_bf16_supported() == True`)                      |
| PyTorch Version                   | 2.14.1+cu130 (Official CUDA 13.0 Wheel)                                   |
| cuDNN Version                     | 92400 (cuDNN v9.2.4)                                                      |
| Primary Disk Volume (C:\)         | NTFS Filesystem (Volume Label: "Windows")                                 |
| C:\ Total Disk Capacity           | 510,880,903,168 bytes (475.79 GiB / 510.88 GB decimal)                    |
| C:\ Used Disk Space               | 424,431,165,440 bytes (395.28 GiB / 424.43 GB decimal)                    |
| C:\ Available Free Disk Space     | 86,449,737,728 bytes (80.51 GiB / 86.45 GB decimal)                      |
| Secondary Storage Volumes         | None (Only 932 MB hidden NTFS recovery partition)                         |
+-----------------------------------+---------------------------------------------------------------------------+
```

---

## 3. Critical Technical Boundary: Why Weights Fitting $
e$ Training Fitting

A common planning fallacy is assuming that because model weights take only ~193 MB, a 6 GB GPU has ample capacity for training. Phase 22A rigorously documents why the full training workload pushes the 6.00 GiB VRAM to absolute saturation:

### 3.1. Static Training State Breakdown (IGRIS 96.5M Parameters)
1. **Model Weights (BF16, 2 bytes/param):** $96,485,888 	imes 2 = \mathbf{192.97	ext{ MB}}$.
2. **Gradient Buffer (BF16, 2 bytes/param):** $96,485,888 	imes 2 = \mathbf{192.97	ext{ MB}}$.
3. **AdamW Optimizer States (FP32 momentum $m$ + variance $v$, 8 bytes/param):** $2 	imes 96,485,888 	imes 4 = \mathbf{771.89	ext{ MB}}$.
4. **FP32 Master Weights (Mandatory for stable optimizer updates, 4 bytes/param):** $96,485,888 	imes 4 = \mathbf{385.94	ext{ MB}}$.
5. **Static Training State Subtotal:** $192.97 + 192.97 + 771.89 + 385.94 = \mathbf{1,543.77	ext{ MB}~(1.51	ext{ GiB})}$.

### 3.2. Dynamic Runtime Overhead & Activation Scaling
1. **CUDA Driver & PyTorch Runtime Context:** Initializing CUDA on Windows allocates **~550 MB to 750 MB** of VRAM before any tensor allocation.
2. **Activation Memory Scaling:**
   - During the forward pass, every layer stores activations for backpropagation.
   - For attention layers without gradient checkpointing, intermediate $Q 	imes K^T$ logits require $B 	imes H 	imes S 	imes S 	imes 2	ext{ bytes}$ per layer.
   - At full context $S = 2048$, a single attention layer materializes **67.1 MB** per batch item. Across 16 layers, this exceeds **1.07 GB** of attention activation memory alone!
   - SwiGLU MLP activations add another **~400 MB** per batch item.
3. **Empirical Evidence from Phase 17 Experiment C:**
   - At $B=1, L=2048$, peak VRAM reached **5,884.8 MB (98.1% of capacity)**!
   - Attempting $B=2, L=2048$ resulted in an immediate `torch.cuda.OutOfMemoryError`.
   - **Conclusion:** While weights (193 MB) fit trivially, the complete training workload (static state + CUDA context + full-context activations) leaves less than **115 MB** of headroom on a 6GB GPU.
