# PHASE 22C — HARDWARE EVIDENCE NOTE & HISTORICAL PROBE RECONCILIATION
## Direct WMI Interrogation of Host Platform and Forensic Record of Historical CPU Label Discrepancy

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22C  
**Execution Mode:** READ-ONLY EVIDENCE AUDIT  
**Status:** DEFINITIVE WMI RECONCILIATION  

---

## 1. Definitive Host Hardware Identity

The host development machine identity is verified via direct Windows Management Instrumentation (WMI / Win32 CIM) interrogation:

```
+------------------------------------+----------------------------------------------------------+
| Hardware Subsystem                 | Verified Physical Specification                          |
+------------------------------------+----------------------------------------------------------+
| Host CPU Model                     | 13th Gen Intel(R) Core(TM) i5-13420H                     |
| CPU Architecture                   | Intel Raptor Lake-H (Intel 7 process)                    |
| CPU Physical Cores                 | 8 Cores (4 Performance Cores + 4 Efficient Cores)         |
| CPU Logical Processors             | 12 Logical Processors (Hyper-Threading on P-cores)       |
| CPU Cache Hierarchy                | 12 MB Intel Smart Cache (L3), 7 MB L2 Cache              |
| Operating System                   | Microsoft Windows 11 Home (Build 10.0.26300 AMD64)       |
| Host Physical RAM Total            | 16,791,048,192 bytes (15.64 GiB / 16.79 GB)              |
| RAM Dynamic Free Range             | 3,760,619,520 to 5,038,080,000 bytes (3.50 to 4.69 GiB) |
| RAM Load Percentage                | 70% to 79% (dynamically varying with background tasks)   |
| Host Dedicated GPU                 | NVIDIA GeForce RTX 3050 6GB Laptop GPU (GA107)           |
| Dedicated Video RAM (VRAM)         | 6,441,926,656 bytes (6.00 GiB / 6.44 GB) GDDR6           |
| GPU Compute Capability             | 8.6 (Ampere Architecture)                                |
| Streaming Multiprocessors (SMs)    | 20 SMs (2,560 CUDA Cores, 80 Tensor Cores, 20 RT Cores) |
| BF16 Hardware Acceleration         | Supported via Ampere Tensor Cores (`bf16_supported=True`)|
| PyTorch & CUDA Environment         | PyTorch 2.14.1+cu130, CUDA 13.0, cuDNN 92400             |
| System Drive (C: NTFS) Total       | 510,880,903,168 bytes (475.79 GiB / 510.88 GB)           |
| System Drive (C: NTFS) Free        | 86,449,737,728 bytes (80.51 GiB / 86.45 GB)              |
+------------------------------------+----------------------------------------------------------+
```

---

## 2. Forensic Investigation of Earlier `i7-13620H` Probe Discrepancy

### Investigation Findings:
1. **Inspection of Repository Probe Scripts:**
   - `scratch/probe_hardware.py` was inspected. It queries `platform.processor()`, which returns the generic x86 family string:
     `"Intel64 Family 6 Model 186 Stepping 2, GenuineIntel"`.
   - `scratch/probe_hardware.py` does not call WMI or parse CPU model names; it did not emit `i7-13620H`.
   - `scratch/probe_hardware_detail.py` was inspected. It executes:
     `powershell -Command "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors | ConvertTo-Json"`
     This command returned `Name: "13th Gen Intel(R) Core(TM) i5-13420H"`, `NumberOfCores: 8`, `NumberOfLogicalProcessors: 12`.
2. **Origin of the `i7-13620H` String:**
   - The label `Intel Core i7-13620H` (10 physical cores [6P+4E], 16 logical threads) first appeared in prompt text or diagnostic logs prior to Phase 22B.
   - The repository code and scratch scripts contain no code that programmatically generated the `i7-13620H` string.
3. **Audit Rule Compliance:**
   - In accordance with Phase 22C instructions: *"Do not invent a cause. If the historical cause cannot be demonstrated, document it as an unexplained earlier probe discrepancy superseded by the direct WMI interrogation."*
   - **Formal Record:** The earlier `i7-13620H` report is documented as an **unexplained earlier probe anomaly**, definitively superseded by direct Win32 CIM interrogation (`Get-CimInstance Win32_Processor`).

---

## 3. Dynamic RAM and Available Disk Space Tracking

| Measurement Timestamp | RAM Total (GiB) | RAM Available (GiB) | RAM Load (%) | Free Disk Bytes (C:) | Free Disk (GiB) |
|---|---|---|---|---|---|
| 2026-11-18 22:01 (Phase 22 Initial) | 15.64 GiB | 3.50 GiB | 77% | 86,686,535,680 | 80.73 GiB |
| 2026-11-18 22:13 (Phase 22A Detailed) | 15.64 GiB | 4.59 GiB | 70% | 86,449,737,728 | 80.51 GiB |
| 2026-11-18 22:24 (Phase 22B Verification) | 15.64 GiB | 3.30 GiB | 78% | 86,459,998,208 | 80.52 GiB |
| 2026-11-18 22:30 (Phase 22C Audit) | 15.64 GiB | 4.69 GiB | 70% | 86,449,737,728 | 80.51 GiB |

*Finding:* Total physical RAM ($15.64	ext{ GiB}$) and total disk capacity ($475.79	ext{ GiB}$) remain strictly invariant. Available RAM dynamically oscillates between 3.30 GiB and 4.69 GiB based on transient OS background processes. Local free disk space is stable at ~80.51–80.73 GiB (~86.45 GB).
