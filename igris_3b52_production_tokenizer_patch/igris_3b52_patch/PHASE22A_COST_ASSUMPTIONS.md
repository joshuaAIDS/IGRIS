# PHASE 22A — CLOUD COST ASSUMPTIONS & SENSITIVITY AUDIT
## Forensic Evaluation of Proposed Cloud Configurations, Lifecycle Cost Drivers, and Classification of the Phase 22 Estimate

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22A  
**Status:** RECONCILED & CLASSIFIED  

---

## 1. Executive Summary

Phase 22A reconciles the cloud infrastructure cost estimates presented in Phase 22 against public cloud pricing models and real-world pipeline execution requirements.

### Formal Classification of Original Phase 22 Estimate ($35–$65):
$$\mathbf{CLASSIFICATION:\ PARTIALLY\ SUPPORTED}$$

- **Why Partially Supported:**
  - The estimate accurately models the **isolated GPU compute cost** for the training stage alone when operating on low-cost spot or community cloud accelerators (e.g., RunPod RTX 4090 @ $0.44/hr for 64 hours = $28.16, or Lambda Labs A100 @ $1.89/hr for 35 hours = $66.15).
- **Why Incomplete / Deficient:**
  1. **Omission of Data Preparation Compute:** Assumed that the 183.7 GB dataset arrives pre-cleaned and pre-tokenized. Ingesting, running FastText LID filtering, MinHash deduplicating 3.72B words, and tokenizing 5.5B tokens requires **10 to 14 hours** of high-memory compute. Running this on an attached A100 adds ~$20 to $26 in idle GPU billing.
  2. **Storage Minimums & Retention Duration:** Assumed a 1 TB volume costs only ~$10. While prorated billing on some providers allows 3-day teardown, real-world retention for evaluation, loss curve inspection, and model export typically spans **7 to 30 days**, increasing storage costs from $10 to $23–$100.
  3. **Enterprise Tier-1 Variance:** On major cloud providers (AWS EC2 / GCP), standard on-demand pricing elevates the full end-to-end pipeline to **~$293.54**.

---

## 2. Granular Cloud Cost Drivers & Lifecycle Breakdown

```
+-----------------------------------+---------------------------+---------------------------+---------------------------+
| Pipeline Cost Component           | Low-Cost Scenario (RunPod)| Expected Scenario (Lambda)| Enterprise Scenario (GCP) |
+-----------------------------------+---------------------------+---------------------------+---------------------------+
| Primary Instance Type             | 1x RTX 4090 (24GB VRAM)   | 1x A100 (80GB SXM)        | 1x A100 (40GB, a2-highgpu)|
| Compute Hourly Rate               | $0.44 / hr                | $1.89 / hr                | $3.67 / hr                |
| Ingress & Quarantine Verification | 1.5 hours (Free ingress)  | 1.0 hour (Free ingress)   | 1.0 hour (Free ingress)   |
| FastText LID & Heuristic Filter   | 4.0 hours (CPU offloaded) | 3.5 hours (on-instance)   | 4.0 hours (on-instance)   |
| MinHash LSH Deduplication (3.7B w)| 5.0 hours (CPU offloaded) | 4.0 hours (on-instance)   | 5.0 hours (on-instance)   |
| Tokenization (5.5B Tokens, uint16)| 1.5 hours (16 vCPU)       | 1.5 hours (30 vCPU)       | 2.0 hours (12 vCPU)       |
| Pretraining Runtime (5.5B Tokens) | 64.3 hours (@ 23,750 t/s) | 35.4 hours (@ 43,200 t/s) | 40.0 hours (@ 38,000 t/s) |
| Total Billable Compute Hours      | 76.3 hours                | 45.4 hours                | 52.0 hours                |
| Total Compute Cost                | **$30.69**                | **$85.81**                | **$190.84**               |
| Storage Volume (1 TB NVMe)        | 4 days ($20/mo prorated)  | 7 days ($100/mo prorated) | 30 days ($100/mo full mo) |
| Storage Cost                      | **$2.67**                 | **$23.33**                | **$100.00**               |
| Artifact Egress (20–30 GB)        | Free ($0.00)              | Free ($0.00)              | $0.09/GB ($2.70)          |
+-----------------------------------+---------------------------+---------------------------+---------------------------+
| TOTAL ESTIMATED END-TO-END COST   | **$33.36**                | **$109.14**               | **$293.54**               |
+-----------------------------------+---------------------------+---------------------------+---------------------------+
```

---

## 3. Provider Architecture Options & Recommendation

1. **Option 1 (Budget Ephemeral — $33.36):**
   - *Architecture:* Provision a 1 TB volume and a single RTX 4090 on RunPod. Perform data preparation and training within a strict 4-day window, then immediately download checkpoints and destroy the pod.
   - *Feasibility:* Feasible, but depends on community GPU availability and spot preemptibility.
2. **Option 2 (Recommended Production Profile — $109.14):**
   - *Architecture:* Dedicated on-demand 1x A100 (80GB) on Lambda Labs. Run data prep and training sequentially without interruption. Retain storage for 7 days to run evaluation benchmarks before volume deletion.
   - *Feasibility:* Highly reliable, predictable, and completes the full 5.5B token pretraining in under 36 hours.
3. **Option 3 (Enterprise Cloud — $293.54):**
   - *Architecture:* AWS / GCP on-demand instance with persistent EBS/pd-ssd volume retained for standard monthly billing.
   - *Feasibility:* Unnecessary financial overhead for an independent project unless corporate credits are available.

> [!NOTE]
> All options are purely analytical models. In accordance with Phase 22A restrictions, zero cloud infrastructure has been provisioned, and zero funds have been committed.
