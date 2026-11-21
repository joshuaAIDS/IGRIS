# IGRIS PHASE 20B — DATASET LEDGER CROSS-VERIFICATION

**Document ID:** `IGRIS-PHASE20B-DL-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target:** 32 Dataset Sources Across Catalogs and Registers  
**Status:** FULLY VERIFIED — ZERO SILENT RECLASSIFICATIONS — ZERO UNAUTHORIZED SOURCES  

---

## 1. Executive Summary

This audit performs an exhaustive cross-comparison of the 32 dataset sources documented in [PHASE20A_DATASET_CLASSIFICATION_RECONCILIATION.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE20A_DATASET_CLASSIFICATION_RECONCILIATION.csv) against the foundational governance registers:
1. `DATASET_SOURCE_CATALOG_V3.csv` (Source Baseline Catalog)
2. `IGRIS_PHASE11_DATASET_OWNER_REVIEW_REGISTER.csv` (Phase 11 Governance Transition Register)
3. `IGRIS_PHASE12_ACQUISITION_MANIFEST.csv` (Phase 12 Controlled Acquisition Preparation Manifest)
4. `IGRIS_PHASE13_SOURCE_AUTHORIZATION_REGISTER.csv` (Phase 13 Controlled Acquisition Register)
5. `PHASE20_DATASET_AUTHORIZATION_REVIEW.csv` (Phase 20 Pretraining Gate Review)

**Key Verification Findings:**
* **Total Registered Sources:** Exactly 32 across all registers.
* **Eligible Candidate Sources:** Exactly 18 (`ELIGIBLE`, pending explicit source-specific owner authorization).
* **Conditional Ineligible Sources:** Exactly 8 (`INELIGIBLE_CONDITIONAL`, blocked pending formal legal review).
* **Evaluation-Only Prohibited Sources:** Exactly 2 (`INELIGIBLE_PROHIBITED`, strictly prohibited from pretraining corpus).
* **Incompatible Rejected Sources:** Exactly 4 (`INELIGIBLE_REJECTED`, permanently blocked due to non-commercial terms).
* **Silent Reclassifications:** **0**. Every current status directly maps to its Phase 11 owner verdict and Phase 12 tier.
* **Authorized Sources:** **0**. Every source across every ledger has authorization status `NOT AUTHORIZED` or `PENDING_EXPLICIT_OWNER_AUTHORIZATION`.
* **Gate State:** **`LOCKED`** (100% of 32 sources).

---

## 2. Complete 32-Source Cross-Verification Ledger

| Source ID | Dataset Name | License | Phase 11 Composite Verdict | Phase 12 Tier | Current Classification | Gate State | Authorization State | Silent Reclassification? |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| `SRC-CD-01` | The Stack (Smol Subset) | Permissive (Various) | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-CD-02` | HumanEval & MBPP | MIT / CC-BY-4.0 | `OWNER_APPROVED_EVAL_ONLY` | `TIER_3` | **INELIGIBLE_PROHIBITED** | `LOCKED` | `BLOCKED_EVAL_ONLY` | **NO** |
| `SRC-CV-01` | Common Voice Hindi (NC) | CC-BY-NC-4.0 | `OWNER_REJECTED_INCOMPATIBLE`| `TIER_4` | **INELIGIBLE_REJECTED** | `LOCKED` | `PERMANENTLY_BLOCKED` | **NO** |
| `SRC-CV-02` | Common Voice Tamil (NC) | Non-commercial | `OWNER_REJECTED_INCOMPATIBLE`| `TIER_4` | **INELIGIBLE_REJECTED** | `LOCKED` | `PERMANENTLY_BLOCKED` | **NO** |
| `SRC-CV-03` | OpenSubtitles Hindi | Permissive (Public) | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-CV-04` | Anthropic HH-RLHF | MIT (Eval Only) | `OWNER_APPROVED_EVAL_ONLY` | `TIER_3` | **INELIGIBLE_PROHIBITED** | `LOCKED` | `BLOCKED_EVAL_ONLY` | **NO** |
| `SRC-CV-05` | Tatoeba Hindi-English | CC-BY-2.0-FR | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-CV-06` | Tatoeba Tamil-English | CC-BY-2.0-FR | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-EM-01` | Wikipedia Telugu | CC-BY-SA-3.0 (Text) | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-EM-02` | Wikipedia Malayalam | CC-BY-SA-3.0 (Text) | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-EN-01` | FineWeb-Edu (Sample) | ODC-By-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-EN-02` | C4 English (Subset) | ODC-BY / Terms | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |
| `SRC-EN-03` | RedPajama v2 English | Apache-2.0 / Terms | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |
| `SRC-HI-01` | IndicCorp v2 (Hindi) | CC0-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-HI-02` | Samanantar Hindi-English| CC-BY-4.0 (Curated) | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |
| `SRC-HI-03` | Bharat Parallel Corpus | CC-BY-NC-SA-4.0 | `OWNER_REJECTED_INCOMPATIBLE`| `TIER_4` | **INELIGIBLE_REJECTED** | `LOCKED` | `PERMANENTLY_BLOCKED` | **NO** |
| `SRC-ML-01` | Flores-200 Benchmark | CC-BY-SA-4.0 | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |
| `SRC-ML-02` | Aksharantar Translit. | CC-BY-4.0 (Mixed) | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |
| `SRC-OI-01` | IndicCorp v2 (Bengali) | CC0-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-OI-02` | IndicCorp v2 (Gujarati)| CC0-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-OI-03` | IndicCorp v2 (Kannada) | CC0-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-OI-04` | IndicCorp v2 (Malayalam)| CC0-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-OI-05` | IndicCorp v2 (Telugu) | CC0-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-TD-01` | MADLAD-400 (Indic Sub) | ODC-BY / Mixed | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |
| `SRC-TD-02` | Sangraha (Verified Perm)| MIT / CC0 / Apache | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-TD-03` | Wikipedia Hindi | CC-BY-SA-3.0 (Text) | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-TG-01` | L3Cube Tanglish Corpus | CC-BY-4.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-TG-02` | IndicGLUE Tanglish Sent.| CC-BY-4.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-TG-03` | Social Media Tanglish NC| Non-commercial | `OWNER_REJECTED_INCOMPATIBLE`| `TIER_4` | **INELIGIBLE_REJECTED** | `LOCKED` | `PERMANENTLY_BLOCKED` | **NO** |
| `SRC-TM-01` | IndicCorp v2 (Tamil) | CC0-1.0 | `OWNER_APPROVED_PERMISSIVE` | `TIER_1` | **ELIGIBLE** | `LOCKED` | `PENDING_OWNER_AUTH` | **NO** |
| `SRC-TM-02` | Samanantar Tamil-English| CC-BY-4.0 (Curated) | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |
| `SRC-TM-03` | Wikipedia Tamil | CC-BY-SA-3.0 (Text) | `OWNER_APPROVED_CONDITIONAL` | `TIER_2` | **INELIGIBLE_CONDITIONAL**| `LOCKED` | `BLOCKED_CONDITIONAL` | **NO** |

---

## 3. Forensic Clarification of Evaluation-Only Sources

A key question addressed by Phase 20A/20B was the classification of evaluation-only benchmarks:
1. **Catalog Prohibited Benchmarks (`INELIGIBLE_PROHIBITED`):**
   * `SRC-CD-02` (HumanEval & MBPP): Strictly prohibited from pretraining corpus to prevent test set contamination.
   * `SRC-CV-04` (Anthropic HH-RLHF): Strictly prohibited from pretraining corpus; designated for downstream alignment and safety evaluation.
2. **Conditional Evaluation Benchmarks:**
   * `SRC-ML-01` (Flores-200 Multilingual Translation Benchmark): Subject to CC-BY-SA 4.0 copyleft share-alike terms. Classified as `INELIGIBLE_CONDITIONAL` rather than `INELIGIBLE_PROHIBITED`, preventing pretraining ingestion while remaining eligible for external translation evaluation.
3. **Eligible Colloquial Datasets:**
   * `SRC-TG-02` (IndicGLUE Tanglish Sentiment): Licensed permissively under CC-BY-4.0. Eligible as a pretraining candidate with attribution compliance.

---

## 4. Verification of Invariant Controls
- **Total Authorized Sources:** **0**. No authorization tokens have been minted.
- **Pipeline Gate State:** **`LOCKED`** across all 32 sources in all registries.
- **Acquisition Status:** **0 bytes acquired**.
- **Audit Conclusion:** All 32 source classifications and authorization states are consistent, verifiable, and strictly compliant with project governance.
