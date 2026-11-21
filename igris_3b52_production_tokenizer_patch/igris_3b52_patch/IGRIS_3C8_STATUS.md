# IGRIS Milestone 3C.8 — Status & Governance Gate Record

**Milestone:** 3C.8 — Legal Jurisdiction Correction & Pipeline Authorization Audit  
**Project:** IGRIS (Decoder-Only Multilingual Transformer)  
**Patch Directory:** `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Timestamp:** 2026-11-17T16:47:00+05:30  
**Overall Milestone Status:** `COMPLETED (LEGAL AUDIT & PIPELINE AUTHORIZATION)`  
**Production Access Gate:** `LOCKED` (Default-Deny Enforced)  
**Dataset Acquisition Authorization:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`

---

## 1. Governance Gate & Security Invariants

| Gate / Security Invariant | State | Verification Method | Enforcement Mechanism |
| :--- | :---: | :--- | :--- |
| **Production Dataset Access** | **LOCKED** | Automated inspection & permission deny | Hardcoded default-deny gate in `src/authorization.py` |
| **Corpus Downloading / Ingestion** | **BLOCKED** | Zero download routines; no network fetch | Milestone directive & test assertion |
| **PII Scanning on Production Data** | **BLOCKED** | No production scanner invocation | Security rule & test assertion |
| **Tokenizer Re-Training** | **BLOCKED** | No vocabulary update or training call | Candidate artifact immutability rule |
| **Model Supervised Fine-Tuning** | **NOT AUTHORIZED** | SFT field set to NOT AUTHORIZED across all 32 sources | Pipeline matrix & test assertion |
| **Candidate A (`tokenizer.json`) Hash** | **VERIFIED** | SHA-256: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | Invariant assertion in test suite |
| **Candidate B (`tokenizer.model`) Hash** | **VERIFIED** | SHA-256: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | Invariant assertion in test suite |
| **Human Signatures** | **PENDING** | Explicit blank / pending fields in review packages | Zero fabricated approvals rule |

---

## 2. Reconciled License & Pipeline Metrics

```
================================================================================
IGRIS 3C.8 LEGAL & PIPELINE AUDIT METRICS
================================================================================
Canonical Source IDs Audited:        32
License Classification Breakdown (9 Classes):
  - Other / Unknown:                 10 (31.3%)
  - CC0:                              7 (21.9%)
  - ShareAlike:                       4 (12.5%)
  - ODC-By:                           3 ( 9.4%)
  - CC-BY:                            2 ( 6.3%)  [NOT unrestricted: attribution mandatory]
  - Apache-2.0:                       2 ( 6.3%)  [NOT unrestricted: attribution mandatory]
  - Public Domain:                    2 ( 6.3%)  [US pre-1928; Life+60 / Life+70 checks]
  - MIT:                              1 ( 3.1%)
  - GPL:                              1 ( 3.1%)  [GPL-2.0 syscall documentation exemption]
  ------------------------------------------------------------------------------
  Total:                             32 (100.0%)

Jurisdictional Public Domain Entry Thresholds (2026):
  - India (Section 22, Life + 60):   Author died on or before Dec 31, 1965 (<= 1965)
  - UK & EU (Directives, Life + 70): Author died on or before Dec 31, 1955 (<= 1955)
  - United States (17 U.S.C.):       Work published before 1928

Pipeline Authorization State Breakdown:
  - Tokenizer Vocab Training:        18 Eligible Pending | 8 Conditional | 2 Prohibited | 4 Rejected
  - Tokenizer Fertility Eval:        27 Eligible Pending | 1 Isolated Subset | 4 Rejected
  - Tokenizer Regression Eval:       28 Eligible Pending | 4 Rejected
  - Supervised Fine-Tuning (SFT):    32 NOT AUTHORIZED (100.0%)
  - Alignment Evaluation:            32 NOT AUTHORIZED (3 Designated Benchmarks)
  - Safety Evaluation:               32 NOT AUTHORIZED (1 Designated Benchmark)
================================================================================
```

---

## 3. Four Core Human Approval Roles

All four roles established in Milestone 3B.60 are maintained without replacement:
1. **`DATA_CUSTODIAN`**: Status = `PENDING` (Unsigned)
2. **`LEGAL_GOVERNANCE`**: Status = `PENDING` (Unsigned)
3. **`SECURITY_PRIVACY`**: Status = `PENDING` (Unsigned)
4. **`CHIEF_ARCHITECT`**: Status = `PENDING` (Unsigned)

---

## 4. Milestone 3C.8 Deliverables Checklist

- [x] `INDIA_COPYRIGHT_REVIEW.md`: Statutory analysis of Section 22, Life+60, exceptions, and moral rights.
- [x] `DATASET_LICENSE_CLASSIFICATION_V3.csv`: 32 sources categorized across 9 classes with detailed restrictions.
- [x] `PIPELINE_AUTHORIZATION_MATRIX_V2.csv`: 6 independent permission fields; SFT/Alignment NOT AUTHORIZED.
- [x] `GUTENBERG_JURISDICTION_REVIEW_V2.md`: Multi-jurisdictional review, Indian Life+60 integration, 4-pillar review.
- [x] `IGRIS_3C8_LEGAL_CORRECTION_REPORT.md`: Master synthesis, legal corrections, and governance audit.
- [x] `IGRIS_3C8_STATUS.md`: Governance tracking and status sign-off.
- [x] `tests/test_dataset_3c8_governance.py`: Automated test suite for 3C.8 governance checks.
