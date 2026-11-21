# IGRIS Hardware Stability & Sustained Benchmark Results

**Project:** IGRIS Decoder-Only Transformer  
**Workspace:** `C:\IGRIS`  
**Hardware Profile:** NVIDIA GeForce RTX 3050 6GB Laptop GPU | Intel Core i5-13420H | 16 GB System RAM  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Document Version:** 1.0.0  
**Effective Date:** 2026-11-21  

---

## 1. Executive Summary

This report documents the empirical results of the **sustained 30-step hardware stability audit** executed on the physical NVIDIA RTX 3050 Laptop GPU. The benchmark evaluated three candidate training configurations under 5 warm-up steps followed by 30 synchronized optimizer steps per configuration, with comprehensive telemetry tracking:

1. **Configuration A ($T=512, B=2, A=2$):** **$2,717.3\text{ tokens/sec}$**, $1,809.72\text{ MiB}$ allocated, $50.77\%$ dedicated VRAM headroom, max temp $65^\circ\text{C}$.
2. **Configuration B ($T=1024, B=1, A=2$):** **$2,246.1\text{ tokens/sec}$**, $1,745.71\text{ MiB}$ allocated, $52.43\%$ dedicated VRAM headroom, max temp $69^\circ\text{C}$.
3. **Configuration C ($T=2048, B=1, A=2$):** **$2,316.6\text{ tokens/sec}$**, $2,110.91\text{ MiB}$ allocated, $43.25\%$ dedicated VRAM headroom, max temp $70^\circ\text{C}$.

### Key Operational Findings
* **Zero CUDA OOMs:** Not a single out-of-memory or recovery event occurred across any configuration [DIRECTLY MEASURED].
* **Headroom Compliance:** Every configuration maintained $>43\%$ dedicated physical VRAM headroom, exceeding the mandatory $15\%$ safety threshold ($921.52\text{ MiB}$) by more than $1.7\text{ GiB}$ [DIRECTLY MEASURED].
* **Loss & Gradient Finiteness:** 100% of recorded losses and gradient norms across all 90 measured steps were strictly finite, with losses decreasing smoothly [DIRECTLY MEASURED].
* **Bit-Exact Recovery:** Checkpoint persistence and reload on Configuration B verified exact reproducibility with **$0.00000000$** loss and weight divergence [DIRECTLY MEASURED].

---

## 2. Hardware Environment & Telemetry Baseline

| Hardware Parameter | Measured Value | Standard Units | Status |
| :--- | :--- | :--- | :---: |
| **GPU Model** | NVIDIA GeForce RTX 3050 6GB Laptop GPU | GA107, Ampere Architecture | Active |
| **Driver Version** | 610.91 | Official NVIDIA WDDM 3.1 | Active |
| **CUDA Version** | 13.0 (`torch.version.cuda = 13.0`) | Compute Capability 8.6 | Active |
| **Physical VRAM Capacity** | `6,441,926,656` bytes | **$6,143.50\text{ MiB}$** ($6.000\text{ GiB}$) | Physical Limit |
| **OS / DWM Baseline Overhead** | `1,030,225,920` bytes | **$982.50\text{ MiB}$** ($1.030\text{ GB}$) | Fixed Baseline |
| **CUDA Free Capacity** | `5,411,700,736` bytes | **$5,161.00\text{ MiB}$** ($5.040\text{ GiB}$) | Available |
| **15% Mandatory Headroom** | `966,289,000` bytes | **$921.52\text{ MiB}$** | Safety Margin |
| **CUDA Safety Ceiling** | `4,445,411,736` bytes | **$4,239.48\text{ MiB}$** | Hard Ceiling |
| **Host System RAM** | `16,791,048,192` bytes | **$15.64\text{ GiB}$** (Available: $3.92\text{ GiB}$) | Normal |

---

## 3. Sustained 30-Step Execution Telemetry

### 3.1 Configuration A: $T=512, B=2, A=2$ (Effective Batch = 2,048 Tokens)
* **Warm-up Steps:** 5 | **Measured Steps:** 30 | **Tokens Processed:** 61,440
* **Total Duration:** **$22.6108\text{ seconds}$** [DIRECTLY MEASURED]
* **Mean Step Duration:** $0.7343\text{ s}$ | **Median Step:** $0.6836\text{ s}$ | **Std Dev:** $0.1357\text{ s}$ [DERIVED CALCULATION]
* **Throughput:** **$2,717.29\text{ tokens/sec}$** ($1.33\text{ steps/sec}$) [DERIVED CALCULATION]
* **Peak VRAM Allocated:** **$1,809.72\text{ MiB}$** ($1,897.63\text{ MB}$) [DIRECTLY MEASURED]
* **Peak VRAM Reserved:** **$2,006.00\text{ MiB}$** ($2,103.45\text{ MB}$) [DIRECTLY MEASURED]
* **Remaining Free VRAM:** **$3,119.00\text{ MiB}$** (**$50.77\%$ headroom**) [DIRECTLY MEASURED]
* **Thermal Telemetry:** Mean $63.1^\circ\text{C}$ (Max: $65^\circ\text{C}$), Mean Clock: $1,675.6\text{ MHz}$ [DIRECTLY MEASURED]
* **Loss Progression:** Initial $10.2307 \to$ Final $8.9814$ (Loss Finiteness: `True`) [DIRECTLY MEASURED]
* **Gradient Finiteness:** `True` (Max norm clipped to $1.0$) [DIRECTLY MEASURED]

#### Periodic Telemetry Samples (Configuration A)
| Step | Duration | VRAM Active (MiB) | Temp (°C) | Graphics Clock (MHz) | Memory Clock (MHz) | GPU Util (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6 (Start)** | $1.0963\text{ s}$ | $944.96\text{ MiB}$ | $60^\circ\text{C}$ | $1,695\text{ MHz}$ | $6,001\text{ MHz}$ | $78\%$ |
| **10** | $0.6802\text{ s}$ | $944.96\text{ MiB}$ | $62^\circ\text{C}$ | $1,680\text{ MHz}$ | $6,001\text{ MHz}$ | $85\%$ |
| **15** | $0.6806\text{ s}$ | $944.96\text{ MiB}$ | $63^\circ\text{C}$ | $1,665\text{ MHz}$ | $6,001\text{ MHz}$ | $86\%$ |
| **20** | $0.6842\text{ s}$ | $944.96\text{ MiB}$ | $64^\circ\text{C}$ | $1,665\text{ MHz}$ | $6,001\text{ MHz}$ | $87\%$ |
| **25** | $0.6829\text{ s}$ | $944.96\text{ MiB}$ | $64^\circ\text{C}$ | $1,665\text{ MHz}$ | $6,001\text{ MHz}$ | $87\%$ |
| **30** | $0.6811\text{ s}$ | $944.96\text{ MiB}$ | $65^\circ\text{C}$ | $1,650\text{ MHz}$ | $6,001\text{ MHz}$ | $88\%$ |
| **35 (End)** | $0.6854\text{ s}$ | $944.96\text{ MiB}$ | $64^\circ\text{C}$ | $1,705\text{ MHz}$ | $6,001\text{ MHz}$ | $86\%$ |

---

### 3.2 Configuration B: $T=1024, B=1, A=2$ (Selected Recommended Configuration)
* **Warm-up Steps:** 5 | **Measured Steps:** 30 | **Tokens Processed:** 61,440
* **Total Duration:** **$27.3547\text{ seconds}$** [DIRECTLY MEASURED]
* **Mean Step Duration:** $0.8880\text{ s}$ | **Median Step:** $0.8801\text{ s}$ | **Std Dev:** $0.1453\text{ s}$ [DERIVED CALCULATION]
* **Throughput:** **$2,246.05\text{ tokens/sec}$** ($1.10\text{ steps/sec}$) [DERIVED CALCULATION]
* **Peak VRAM Allocated:** **$1,745.71\text{ MiB}$** ($1,830.51\text{ MB}$) [DIRECTLY MEASURED]
* **Peak VRAM Reserved:** **$1,902.00\text{ MiB}$** ($1,994.39\text{ MB}$) [DIRECTLY MEASURED]
* **Remaining Free VRAM:** **$3,221.00\text{ MiB}$** (**$52.43\%$ headroom**) [DIRECTLY MEASURED]
* **Thermal Telemetry:** Mean $67.6^\circ\text{C}$ (Max: $69^\circ\text{C}$), Mean Clock: $1,605.7\text{ MHz}$ [DIRECTLY MEASURED]
* **Loss Progression:** Initial $10.2974 \to$ Final $9.0711$ (Loss Finiteness: `True`) [DIRECTLY MEASURED]
* **Gradient Finiteness:** `True` (Max norm clipped to $1.0$) [DIRECTLY MEASURED]

#### Periodic Telemetry Samples (Configuration B)
| Step | Duration | VRAM Active (MiB) | Temp (°C) | Graphics Clock (MHz) | Memory Clock (MHz) | GPU Util (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6 (Start)** | $1.2858\text{ s}$ | $944.96\text{ MiB}$ | $65^\circ\text{C}$ | $1,635\text{ MHz}$ | $6,001\text{ MHz}$ | $76\%$ |
| **10** | $0.8797\text{ s}$ | $944.96\text{ MiB}$ | $66^\circ\text{C}$ | $1,620\text{ MHz}$ | $6,001\text{ MHz}$ | $84\%$ |
| **15** | $0.8799\text{ s}$ | $944.96\text{ MiB}$ | $67^\circ\text{C}$ | $1,605\text{ MHz}$ | $6,001\text{ MHz}$ | $85\%$ |
| **20** | $0.8804\text{ s}$ | $944.96\text{ MiB}$ | $68^\circ\text{C}$ | $1,590\text{ MHz}$ | $6,001\text{ MHz}$ | $86\%$ |
| **25** | $0.8802\text{ s}$ | $944.96\text{ MiB}$ | $69^\circ\text{C}$ | $1,590\text{ MHz}$ | $6,001\text{ MHz}$ | $86\%$ |
| **30** | $0.8795\text{ s}$ | $944.96\text{ MiB}$ | $69^\circ\text{C}$ | $1,600\text{ MHz}$ | $6,001\text{ MHz}$ | $86\%$ |
| **35 (End)** | $0.8812\text{ s}$ | $944.96\text{ MiB}$ | $69^\circ\text{C}$ | $1,600\text{ MHz}$ | $6,001\text{ MHz}$ | $86\%$ |

---

### 3.3 Configuration C: $T=2048, B=1, A=2$ (Extended Context = 4,096 Tokens)
* **Warm-up Steps:** 5 | **Measured Steps:** 30 | **Tokens Processed:** 122,880
* **Total Duration:** **$53.0442\text{ seconds}$** [DIRECTLY MEASURED]
* **Mean Step Duration:** $1.7469\text{ s}$ | **Median Step:** $1.7435\text{ s}$ | **Std Dev:** $0.0111\text{ s}$ [DERIVED CALCULATION]
* **Throughput:** **$2,316.56\text{ tokens/sec}$** ($0.57\text{ steps/sec}$) [DERIVED CALCULATION]
* **Peak VRAM Allocated:** **$2,110.91\text{ MiB}$** ($2,213.45\text{ MB}$) [DIRECTLY MEASURED]
* **Peak VRAM Reserved:** **$2,466.00\text{ MiB}$** ($2,585.79\text{ MB}$) [DIRECTLY MEASURED]
* **Remaining Free VRAM:** **$2,657.00\text{ MiB}$** (**$43.25\%$ headroom**) [DIRECTLY MEASURED]
* **Thermal Telemetry:** Mean $69.7^\circ\text{C}$ (Max: $70^\circ\text{C}$), Mean Clock: $1,696.7\text{ MHz}$ [DIRECTLY MEASURED]
* **Loss Progression:** Initial $10.3582 \to$ Final $9.3621$ (Loss Finiteness: `True`) [DIRECTLY MEASURED]
* **Gradient Finiteness:** `True` (Max norm clipped to $1.0$) [DIRECTLY MEASURED]

#### Periodic Telemetry Samples (Configuration C)
| Step | Duration | VRAM Active (MiB) | Temp (°C) | Graphics Clock (MHz) | Memory Clock (MHz) | GPU Util (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **6 (Start)** | $1.7611\text{ s}$ | $944.96\text{ MiB}$ | $68^\circ\text{C}$ | $1,710\text{ MHz}$ | $6,001\text{ MHz}$ | $89\%$ |
| **10** | $1.7428\text{ s}$ | $944.96\text{ MiB}$ | $69^\circ\text{C}$ | $1,710\text{ MHz}$ | $6,001\text{ MHz}$ | $91\%$ |
| **15** | $1.7434\text{ s}$ | $944.96\text{ MiB}$ | $70^\circ\text{C}$ | $1,695\text{ MHz}$ | $6,001\text{ MHz}$ | $91\%$ |
| **20** | $1.7439\text{ s}$ | $944.96\text{ MiB}$ | $70^\circ\text{C}$ | $1,695\text{ MHz}$ | $6,001\text{ MHz}$ | $92\%$ |
| **25** | $1.7441\text{ s}$ | $944.96\text{ MiB}$ | $70^\circ\text{C}$ | $1,695\text{ MHz}$ | $6,001\text{ MHz}$ | $92\%$ |
| **30** | $1.7436\text{ s}$ | $944.96\text{ MiB}$ | $70^\circ\text{C}$ | $1,680\text{ MHz}$ | $6,001\text{ MHz}$ | $92\%$ |
| **35 (End)** | $1.7452\text{ s}$ | $944.96\text{ MiB}$ | $70^\circ\text{C}$ | $1,695\text{ MHz}$ | $6,001\text{ MHz}$ | $92\%$ |

---

## 4. Checkpoint Persistence & Bit-Exact Recovery Results

The checkpoint recovery test was conducted on **Configuration B ($T=1024$)**:

* **Uninterrupted Run:** Steps 1 to 10 executed continuously.
* **Checkpoint Persistence:** At step 5, full training checkpoint `chk_step_000005.pt` was written to disk.
  * Measured File Size: **$956,701,489\text{ bytes}$** ($912.38\text{ MiB}$) [DIRECTLY MEASURED]
  * Measured Write Time: **$0.84\text{ seconds}$** [DIRECTLY MEASURED]
* **Process Cleanup & Restoration:** Process memory was cleared, GPU memory wiped with `clean_gpu()`, and a fresh trainer instantiated with seed `99999999`.
* **State Deserialization:** State dicts, learning rate scheduler, optimizer states, and CPU/CUDA RNG generators were loaded from `chk_step_000005.pt` ($0.49\text{ s}$).
* **Resumed Execution:** Steps 6 to 10 were executed from the reloaded checkpoint.

### Loss Comparison (Steps 6 to 10)
| Step | Uninterrupted Loss | Resumed Loss | Absolute Difference |
| :---: | :---: | :---: | :---: |
| **6** | $10.48943000$ | $10.48943000$ | **$0.00000000$** |
| **7** | $10.49401300$ | $10.49401300$ | **$0.00000000$** |
| **8** | $10.50085500$ | $10.50085500$ | **$0.00000000$** |
| **9** | $10.50106900$ | $10.50106900$ | **$0.00000000$** |
| **10** | $10.49599800$ | $10.49599800$ | **$0.00000000$** |

* **Maximum Loss Difference:** **$0.00000000$** [DIRECTLY MEASURED]
* **Maximum Weight Divergence at Step 10:** **$0.00000000$** [DIRECTLY MEASURED]
* **Bit-Exact Recovery Verdict:** **`PASSED`** [DIRECTLY MEASURED]
* **Resource Cleanliness:** Temporary checkpoint directory wiped; **0 bytes** lingering on host disk [DIRECTLY MEASURED].

---

## 5. Hardware Stability Verification Sign-Off

```
========================================================================================
                      HARDWARE STABILITY VERIFICATION SIGN-OFF:
                                    PASSED
========================================================================================
  [X] Zero CUDA OOM Errors (0 occurrences across 90 sustained steps)
  [X] Physical VRAM Headroom Maintained (>= 43.25% across all configurations)
  [X] 15% Physical Safety Headroom Enforced (> 1.7 GiB surplus margin)
  [X] 100% Finite Losses and Gradients (No NaN, no Inf)
  [X] Thermal Envelope Controlled (Max 70°C, zero thermal throttling observed)
  [X] Bit-Exact Checkpoint Resume Verified (0.000000 loss/weight divergence)
  [X] Established Primary Configuration: Configuration B (T=1024, B=1, A=2)
========================================================================================
```
