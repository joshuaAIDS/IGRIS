# IGRIS Hardware Measurement & Resource Profiling Audit

**Engineering Role**: Senior ML Systems Engineer & Hardware Auditor  
**Audit Type**: Empirical Host Telemetry & Resource Budgeting  
**Operating Model**: SOLO_DEVELOPER_OWNER_REVIEW  
**Date**: November 2026  
**Status**: **EMPIRICALLY MEASURED**

---

## 1. Measured System Hardware Profile

The following hardware specifications were measured directly on the host machine using PyTorch and Windows Win32 API calls (`GlobalMemoryStatusEx`):

| Hardware Component | Measured Specification | Source / Method |
| :--- | :--- | :--- |
| **Operating System** | Microsoft Windows 11 (`Windows-10-10.0.26300-SP0`) | `platform.platform()` |
| **Python Runtime** | Python 3.11.9 (64-bit) | `sys.version` |
| **CUDA Available** | **`True`** | `torch.cuda.is_available()` |
| **Discrete GPU** | **NVIDIA GeForce RTX 3050 6GB Laptop GPU** (`Device 0`) | `torch.cuda.get_device_name(0)` |
| **Total Dedicated VRAM** | **6.00 GB (6,441,926,656 bytes)** | `torch.cuda.mem_get_info()` |
| **Free VRAM Available** | **5.04 GB (5,411,700,736 bytes)** | `torch.cuda.mem_get_info()` |
| **Host System RAM (Total)** | **15.64 GB (16,791,048,192 bytes)** | `GlobalMemoryStatusEx` |
| **Host System RAM (Available)** | **1.83 GB (1,969,061,888 bytes)** | `GlobalMemoryStatusEx` |
| **Host Memory Load** | **88%** | `GlobalMemoryStatusEx` |
| **CPU Architecture** | 13th Gen Intel Core i5-13420H (12 logical processors) | `os.cpu_count()` |

---

## 2. Measured PyTorch Runtime Memory vs. Estimated Memory

To comply strictly with truth-in-reporting standards, **measured memory** is distinguished from **analytical estimates**:

### 2.1 Measured Runtime Memory (Live Daemon)
Because **no pre-trained checkpoint exists** in accordance with project governance policies:
- **PyTorch Allocated VRAM**: **0.00 MB (0 bytes)**
- **PyTorch Reserved VRAM**: **0.00 MB (0 bytes)**
- **Measured Inference Throughput**: **None (Not Measured)**. No production tokens or throughput rates are fabricated.

### 2.2 Analytical Memory Estimations (For Future Checkpoint Deployment)
When a 16-layer production checkpoint is loaded, the calculated memory footprint is:

1. **Model Weights (FP16 Tied)**:
   $$79,708,672\text{ parameters} \times 2\text{ bytes} = 159,417,344\text{ bytes} \approx \mathbf{152.03\text{ MB}}$$
2. **KV Cache at Context Length $T=2048$ ($B=1$)**:
   $$2 \times 16\text{ layers} \times 4\text{ KV heads} \times 64\text{ head\_dim} \times 2048 \times 2\text{ bytes} = 33,554,432\text{ bytes} \approx \mathbf{32.00\text{ MB}}$$
3. **Logits & Working Buffers**:
   $$\approx 45.00\text{ MB}$$
4. **CUDA Driver & Context Overhead**:
   $$\approx 280.00\text{ MB}$$
5. **Total Estimated Peak VRAM Footprint**:
   $$\approx \mathbf{509.03\text{ MB (< 0.51 GB)}}$$

### Conclusion
The estimated memory footprint of **~509 MB** consumes less than **10%** of the 6.0 GB total VRAM, leaving **> 4.5 GB of free headroom** for Windows display compositing, background processes, and the Liquid Glass Three.js starfield canvas.

---

## 3. Safe CPU Fallback Logic

The runtime includes an automated safe fallback mechanism:
- If free VRAM drops below **1.0 GB** or CUDA initialization fails, the engine falls back to CPU execution.
- If a GPU out-of-memory error occurs during tensor operations, `torch.cuda.OutOfMemoryError` is caught, `torch.cuda.empty_cache()` is called, and an HTTP 503 error is returned without terminating the runtime process.
