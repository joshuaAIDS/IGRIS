# IGRIS Hardware Compatibility & Resource Profiling Report

**Engineering Role**: Senior ML Systems Engineer  
**Target Hardware Platform**: NVIDIA RTX 3050 Laptop GPU (6GB VRAM) & Intel i5-13420H  
**Inference Precision**: FP16 / INT8  
**Safe CPU Fallback**: Implemented & Verified  
**Date**: November 2026  

---

## 1. Measured System Hardware Profile

The local runtime performs programmatic hardware detection upon startup via `igris/inference/hardware.py`. The measured host specifications are:

| Subsystem | Detected Specification | Verification Status |
| :--- | :--- | :--- |
| **GPU** | NVIDIA GeForce RTX 3050 6GB Laptop GPU | Detected (`cuda:0`) |
| **GPU Architecture** | Ampere (Compute Capability 8.6) | Fully Supported |
| **Dedicated VRAM** | **6.0 GB (6,144 MB)** | Confirmed via `cudaMemGetInfo` |
| **Available VRAM Headroom** | **~5.42 GB** free at baseline | Measured |
| **CPU** | 13th Gen Intel Core i5-13420H | Detected |
| **CPU Topology** | 8 Cores (4 Performance + 4 Efficient), 12 Logical Processors | Confirmed via `os.cpu_count()` |
| **Host System RAM** | **15.64 GB DDR5** | Detected |
| **Operating System** | Microsoft Windows 11 Home (64-bit) | Supported |
| **PyTorch Runtime** | PyTorch `2.14.1+cu130` (CUDA 13.0 Driver / CUDA 12.x Runtime) | Active |

---

## 2. Memory Footprint Calculation (FP16 & INT8)

The model is sized specifically to operate comfortably within consumer-grade 6GB VRAM boundaries with significant headroom for OS desktop compositing, Liquid Glass WebGL rendering, and background applications.

### 2.1 Model Weights Memory

Each parameter requires 2 bytes in FP16/BF16, or 1 byte in INT8:

$$\text{Memory}_{\text{weights}} = \text{Parameters} \times \text{Bytes per parameter}$$

- **Authoritative Production (79,708,672 tied parameters)**:
  - **FP16 / BF16**: $79,708,672 \times 2 = 159,417,344\text{ bytes} \approx \mathbf{152.03\text{ MB}}$
  - **INT8 Quantized**: $79,708,672 \times 1 = 79,708,672\text{ bytes} \approx \mathbf{76.01\text{ MB}}$
- **Baseline Profile (51,589,632 tied parameters)**:
  - **FP16 / BF16**: $51,589,632 \times 2 = 103,179,264\text{ bytes} \approx \mathbf{98.40\text{ MB}}$
  - **INT8 Quantized**: $51,589,632 \times 1 = 51,589,632\text{ bytes} \approx \mathbf{49.20\text{ MB}}$

---

### 2.2 Key-Value (KV) Cache Memory

IGRIS employs Grouped-Query Attention (GQA) with $H_{KV} = 4$ key/value heads (compared to 8 query heads). The head dimension is $d_{\text{head}} = 64$.
At maximum context sequence length ($T = 2,048$ tokens) and batch size $B = 1$:

$$\text{KV Cache Size} = 2 \times L \times H_{KV} \times d_{\text{head}} \times T \times \text{Bytes per element}$$

For the 16-layer production model in FP16 ($2\text{ bytes}$):
$$\text{KV Cache Size} = 2 \times 16 \times 4 \times 64 \times 2,048 \times 2 = 33,554,432\text{ bytes} \approx \mathbf{32.00\text{ MB}}$$

Even if the batch size expands to $B = 4$ concurrent streams:
$$\text{KV Cache Size}_{B=4} = 4 \times 32.00\text{ MB} = \mathbf{128.00\text{ MB}}$$

---

### 2.3 Total Peak Runtime VRAM Consumption

| Component | VRAM Consumption (FP16) | VRAM Consumption (INT8) |
| :--- | :--- | :--- |
| **Model Weights (Tied)** | 152.03 MB | 76.01 MB |
| **KV Cache ($T=2048, B=1$)** | 32.00 MB | 32.00 MB |
| **Activation Buffers & RoPE Cache** | ~45.00 MB | ~30.00 MB |
| **CUDA Context & Driver Overhead** | ~280.00 MB | ~280.00 MB |
| **Total Peak Runtime VRAM** | **~509.03 MB (< 0.51 GB)** | **~418.01 MB (< 0.42 GB)** |

### Conclusion on Headroom
With 6.0 GB total VRAM and ~5.42 GB free, IGRIS utilizes **less than 10%** of available VRAM. This leaves **~4.9 GB of free VRAM headroom** for the host operating system, high-resolution multi-monitor displays, and the Liquid Glass Three.js cosmic canvas.

---

## 3. Safe CPU Fallback Logic

To guarantee high availability on systems where the discrete GPU is suspended, under heavy gaming/3D load, or powered off on battery saver mode, `HardwareInspector` implements automated safe fallback:

```python
# Hardware Inspector Rule
if cuda_available:
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    free_gb = free_bytes / (1024 ** 3)
    # Require at least 1.0 GB of unreserved VRAM to operate on GPU
    if free_gb >= 1.0:
        device = "cuda:0"
        safe_for_gpu = True
    else:
        logger.warning("Free VRAM (%.2f GB) is below 1.0 GB threshold. Falling back to CPU.", free_gb)
        device = "cpu"
        safe_for_gpu = False
```

### Out-of-Memory (OOM) Protection

If an unforeseen tensor allocation error occurs during autoregressive generation:
1. `torch.cuda.OutOfMemoryError` is trapped by FastAPI exception handlers.
2. `torch.cuda.empty_cache()` immediately flushes all orphaned GPU memory blocks.
3. The server responds with `HTTP 503` (`code: OUT_OF_MEMORY`) without terminating the server daemon.
4. Subsequent requests can be routed to CPU.
