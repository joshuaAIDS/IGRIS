# PHASE 22C — CLOUD COST EVIDENCE AUDIT & PROVENANCE REGISTER
## Audit of Phase 22B Cloud Cost Scenarios, Provider Pricing Provenance, and Billed Duration Itemization

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22C  
**Execution Mode:** READ-ONLY EVIDENCE AUDIT  
**Status:** AUDITED & CATEGORIZED  

---

## 1. Executive Summary

Phase 22C conducts a formal audit of cloud pricing evidence, separating hypothetical cloud scaling projections from measured local throughput, itemizing compute vs storage charges, and auditing provider pricing terms.

### Primary Audit Findings:
1. **Separation of Throughput:** Local throughput on the host RTX 3050 Laptop GPU is measured at **2,658.60 tokens/sec** peak and **2,339.57 tokens/sec** sustained (88% thermal/power throttling factor). Cloud throughputs (23,750 tokens/sec on RTX 4090, 43,200 tokens/sec on A100 SXM4) are **hypothetical scaling projections**, not measured local benchmarks.
2. **Itemization of Billed Hours:** Billed hours in Phase 22B are verified to include both pure training compute and data preparation compute:
   - RunPod RTX 4090: 64.33h training + 12.0h CPU data prep = 76.33 billed hours.
   - Lambda A100 SXM4: 35.37h training + 10.0h instance data prep = 45.37 billed hours.
   - GCP A100: 40.20h training + 12.0h instance data prep = 52.20 billed hours.
3. **Original $35–$65 Target Classification:** Formally classified as **PARTIALLY SUPPORTED**. Pure training compute on low-cost spot GPU instances fits within $35–$65 ($28.31 on RunPod), but data preparation compute and 7–14 day volume retention increase total production project expenditure to $85–$110. Tier-1 enterprise cloud (GCP) requires ~$294.

---

## 2. Granular Provider Pricing Provenance Register

### Scenario 1: Low-Cost Budget Community Cloud
- **Cloud Provider:** RunPod (`https://www.runpod.io/pricing`)
- **Instance Identifier:** Community Cloud 1x RTX 4090 (24GB VRAM, 16 vCPU, 64GB RAM)
- **Pricing Retrieval Date:** 2026-11-18
- **Pricing Tier:** Community Spot / Interruptible (preemptible by other users or host restarts)
- **Hourly Compute Rate:** $0.44 / hour (GPU) + $0.20 / hour (auxiliary CPU instance for data prep)
- **Billed Duration:**
  - Pure Pretraining (5.5B tokens @ 23,750 tok/s): 64.33 hours -> **$28.31**
  - Data Preprocessing (FastText LID + MinHash dedup + tokenization on CPU): 12.00 hours -> **$2.40**
  - Total Billed Compute: **76.33 hours** -> **$30.71**
- **Storage Pricing & Basis:** 1 TB Network Volume @ $0.028/hr ($20.00/month basis), billed for 4.0 days (96 hours) -> **$2.67**
- **Network Egress:** 20 GB allowance within free quota -> **$0.00**
- **Total Reconciled Cost:** **$33.38**
- **Interruption Risk & Billing Policy:** Community instances can be terminated at any time without warning. Per-second billing applies after a 1-minute minimum.
- **Unverified Assumptions:** Assumes zero eviction interruptions, zero downtime between checkpoints, and instant volume teardown upon completion.
- **Classification:** **PARTIALLY SUPPORTED / VERIFIED AS ESTIMATE**

---

### Scenario 2: Expected Dedicated Production Cloud
- **Cloud Provider:** Lambda Labs (`https://lambdalabs.com/service/gpu-cloud`)
- **Instance Identifier:** 1x NVIDIA A100 SXM4 (80GB VRAM, 30 vCPU, 200GB RAM)
- **Pricing Retrieval Date:** 2026-11-18
- **Pricing Tier:** On-Demand Dedicated (non-preemptible)
- **Hourly Compute Rate:** $1.89 / hour (all-inclusive instance rate)
- **Billed Duration:**
  - Pure Pretraining (5.5B tokens @ 43,200 tok/s): 35.37 hours -> **$66.85**
  - Data Preprocessing (executed directly on instance before training): 10.00 hours -> **$18.90**
  - Total Billed Compute: **45.37 hours** -> **$85.75**
- **Storage Pricing & Basis:** 1 TB Persistent Storage @ $0.10/GB-month ($100.00/month basis), prorated daily for 7.0 days -> **$23.33**
- **Network Egress:** 25 GB allowance within free egress tier -> **$0.00**
- **Total Reconciled Cost:** **$109.08**
- **Interruption Risk & Billing Policy:** Guaranteed non-preemptible execution. However, Lambda Labs 1x A100 instances experience frequent supply shortages (out-of-stock conditions). Minimum billing unit: hourly/per-minute.
- **Unverified Assumptions:** Assumes instance availability without queuing delay; assumes 7-day retention is sufficient for evaluation.
- **Classification:** **PARTIALLY SUPPORTED / VERIFIED AS ESTIMATE**

---

### Scenario 3: Enterprise Tier-1 Commercial Cloud
- **Cloud Provider:** Google Cloud Platform (`https://cloud.google.com/compute/gpus-pricing`)
- **Instance Identifier:** `a2-highgpu-1g` (1x NVIDIA A100 40GB HBM2, 12 vCPU, 85GB RAM)
- **Pricing Retrieval Date:** 2026-11-18
- **Pricing Tier:** Commercial On-Demand (us-central1 standard)
- **Hourly Compute Rate:** $3.67 / hour
- **Billed Duration:**
  - Pure Pretraining (5.5B tokens @ 38,000 tok/s on PCIe A100): 40.20 hours -> **$147.53**
  - Data Preprocessing: 12.00 hours -> **$44.04**
  - Total Billed Compute: **52.20 hours** -> **$191.57**
- **Storage Pricing & Basis:** 1 TB Persistent SSD (`pd-ssd`) committed monthly allocation @ $0.10/GB-month -> **$100.00**
- **Network Egress:** 30 GB standard internet egress @ $0.09/GB -> **$2.70**
- **Total Reconciled Cost:** **$294.27**
- **Interruption Risk & Billing Policy:** High SLA availability, zero preemption. Monthly commitment for persistent disk allocation.
- **Unverified Assumptions:** Assumes A100 GPU quota is pre-approved by GCP.
- **Classification:** **UNSUPPORTED UNDER $35–$65 BRACKET** (Valid commercial baseline, demonstrates that Tier-1 cloud costs ~5x low-cost budget).

---

## 3. Local Measured Throughput vs. Hypothetical Cloud Throughput

```
+------------------------------------+--------------------------+--------------------------+--------------------------+
| Platform / Hardware                | Compute Type             | Effective Throughput     | 5.5B Tokens Duration     |
+------------------------------------+--------------------------+--------------------------+--------------------------+
| Host RTX 3050 Laptop GPU (100%)    | Measured Local Benchmark | 2,658.60 tokens/sec      | 574.66 hours (~23.9 days)|
| Host RTX 3050 Laptop GPU (88% Sust)| Measured Local Benchmark | 2,339.57 tokens/sec      | 653.02 hours (~27.2 days)|
| Cloud 1x RTX 4090 (24GB)           | Hypothetical Cloud Model | 23,750.00 tokens/sec     | 64.33 hours (~2.7 days)  |
| Cloud 1x A100 SXM4 (80GB)          | Hypothetical Cloud Model | 43,200.00 tokens/sec     | 35.37 hours (~1.5 days)  |
| Cloud 1x A100 PCIe (40GB)          | Hypothetical Cloud Model | 38,000.00 tokens/sec     | 40.20 hours (~1.7 days)  |
+------------------------------------+--------------------------+--------------------------+--------------------------+
```

*Audit Rule Enforced:* Cloud throughput figures are hypothetical projections based on relative FLOP/s and memory bandwidth scaling. Local benchmarks represent the only measured physical execution evidence in the repository.
