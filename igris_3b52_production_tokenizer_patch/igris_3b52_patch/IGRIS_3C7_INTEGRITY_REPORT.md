# IGRIS Milestone 3C.7 — Dataset Catalog Integrity & License Evidence Correction Report

**Project:** IGRIS (Decoder-Only Multilingual Transformer)  
**Active Patch:** `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Milestone:** 3C.7 — Dataset Catalog Integrity & License Evidence Correction  
**Date:** 2026-11-17  
**Access Control Status:** `LOCKED` (Default-Deny Enforced)  
**Dataset Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariant Status:** `PRESERVED & UNCHANGED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary

Milestone 3C.7 executes an exhaustive catalog integrity audit, source status reconciliation, license evidence verification, and functional pipeline decoupling across all 32 proposed dataset sources for the IGRIS multilingual tokenizer evaluation project.

In strict compliance with all milestone constraints and safety protocols:
1. **Zero Dataset Access**: No production datasets were opened, read, downloaded, staged, or ingested.
2. **Zero PII Scanning & Tokenizer Training**: No production PII scans or tokenizer training routines were executed.
3. **Candidate Invariants Preserved**: Candidate A (`tokenizer.json`) and Candidate B (`tokenizer.model`) SHA-256 hashes remain perfectly identical to baselines.
4. **Source Count Reconciliation**: Reconciled the historical tally discrepancy where previous 3C.6 summary text cited 30 sources instead of 32. The canonical catalog contains exactly **32 distinct sources** partitioned into:
   - `VERIFIED`: **20**
   - `CONDITIONAL`: **7**
   - `UNVERIFIED`: **1**
   - `INCOMPATIBLE`: **4**
   - **Total: 32** ($20 + 7 + 1 + 4 = 32$).
5. **Decoupled Governance & Pipeline Eligibility**: Established independent fields for license verification, commercial-use evidence, tokenizer training eligibility, tokenizer evaluation eligibility, and alignment evaluation eligibility.
6. **Safety & Benchmark Boundary Security**: Strictly quarantined `SRC-CV-04` (Anthropic HH-RLHF) and `SRC-CD-02` (HumanEval/MBPP) from tokenizer training to prevent vocabulary poisoning and benchmark contamination.
7. **Project Gutenberg Item-Level Mandate**: Established cross-jurisdictional copyright verification (US pre-1928 vs Life+70 in UK/EU/India), trademark removal mandates, and explicitly rejected any claim of "zero copyright risk globally".
8. **Preservation of Four Core Roles**: Strictly preserved `DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, and `CHIEF_ARCHITECT` without alteration or signature fabrication.

---

## 2. Task 1: Source Count & Status Reconciliation

### 2.1 Audit of the 30 vs 32 Discrepancy
In Milestone 3C.3, the catalog comprised 26 initial sources:
$$\text{Verified (14)} + \text{Conditional (7)} + \text{Unverified (1)} + \text{Incompatible (4)} = 26\text{ sources}$$

In Milestone 3C.5, six new permissive baseline sources were introduced:
- `SRC-OI-04`: IndicCorp v2 (Bengali) — CC0-1.0
- `SRC-OI-05`: IndicCorp v2 (Gujarati) — CC0-1.0
- `SRC-CV-03`: OpenAssistant (OASST1) — Apache-2.0
- `SRC-CV-04`: Anthropic HH-RLHF — MIT
- `SRC-CV-05`: MultiWOZ 2.4 — Apache-2.0
- `SRC-CV-06`: Project Gutenberg Theatrical Dialogue — Public Domain (US)

All 6 newly added sources are verified baseline sources. The updated verified total became:
$$14 + 6 = 20\text{ Verified sources}$$

However, the textual narrative summary in Milestone 3C.6 contained a typographical tally error that stated:
> *"18 Verified Baseline | 7 Conditional + 1 Unverified | 4 Rejected (Audit)"*

This written equation sums to $18 + 7 + 1 + 4 = 30$, omitting 2 verified sources from the narrative count, even though the underlying CSV file (`DATASET_SOURCE_CATALOG_V2.csv`) properly contained all 32 rows.

### 2.2 Canonical Reconciled Status Distribution
In Milestone 3C.7, `SOURCE_STATUS_RECONCILIATION.csv` audits every source ID individually. Every source has exactly one primary status:

| Reconciled Primary Status | Source Count | Percentage | Source IDs |
| :--- | :---: | :---: | :--- |
| **VERIFIED** | **20** | 62.5% | `SRC-TM-01`, `SRC-EN-01`, `SRC-TG-01`, `SRC-TG-02`, `SRC-HI-01`, `SRC-OI-01`, `SRC-OI-02`, `SRC-OI-03`, `SRC-OI-04`, `SRC-OI-05`, `SRC-CD-01`, `SRC-CD-02`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-03`, `SRC-CV-04`, `SRC-CV-05`, `SRC-CV-06`, `SRC-EM-01`, `SRC-EM-02` |
| **CONDITIONAL** | **7** | 21.9% | `SRC-TM-02`, `SRC-EN-02`, `SRC-EN-03`, `SRC-HI-02`, `SRC-ML-01`, `SRC-ML-02`, `SRC-TD-01` |
| **UNVERIFIED** | **1** | 3.1% | `SRC-TM-03` (OSCAR 23.01 Tamil) |
| **INCOMPATIBLE** | **4** | 12.5% | `SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02` |
| **Total** | **32** | **100.0%** | **All 32 canonical source IDs preserved without renumbering** |

---

## 3. Task 2: Training and Evaluation Eligibility Decoupling

In `DATASET_SOURCE_CATALOG_V3.csv` and `TOKENIZER_DATA_ELIGIBILITY_MATRIX.md`, legal verification is strictly decoupled from technical pipeline eligibility.

### 3.1 Eligibility Distribution Across the 32 Sources

```
+----------------------------------------------------------------------------------------------------+
|                                PIPELINE ELIGIBILITY SUMMARY (32 SOURCES)                           |
+----------------------------------------------------------------------------------------------------+
Tokenizer Training Eligibility:
  ├── ELIGIBLE:                 18 (56.3%) -> Unencumbered training data (CC0, CC-BY, Apache, PD)
  ├── INELIGIBLE_CONDITIONAL:    8 (25.0%) -> Blocked pending legal/crawler sign-off (SA, ODC-By, GPL)
  ├── INELIGIBLE_PROHIBITED:     2 ( 6.3%) -> Legally clear but architecturally banned (Contamination)
  └── INELIGIBLE_REJECTED:       4 (12.5%) -> Excluded due to NC clauses or unverified scrapes

Tokenizer Evaluation Eligibility:
  ├── ELIGIBLE:                 28 (87.5%) -> 18 training + 8 conditional + 2 prohibited
  └── INELIGIBLE_REJECTED:       4 (12.5%) -> Excluded

Alignment & Safety Evaluation Eligibility:
  ├── ELIGIBLE_PRIMARY:          1 ( 3.1%) -> SRC-CV-04 (Anthropic HH-RLHF)
  ├── ELIGIBLE_OPTIONAL:         2 ( 6.3%) -> SRC-CD-02 (HumanEval/MBPP), SRC-CV-03 (OASST1)
  ├── NOT_APPLICABLE:           25 (78.1%) -> General linguistic text
  └── INELIGIBLE_REJECTED:       4 (12.5%) -> Excluded
```

### 3.2 Specific Pipeline Boundaries:
1. **`SRC-CV-04` (Anthropic HH-RLHF)**:
   - **License**: MIT (Permissive).
   - **Tokenizer Training**: `INELIGIBLE_PROHIBITED`. Preference pairs (`chosen` vs `rejected`) and adversarial red-team queries must **never** be used for subword vocabulary learning. Doing so skews token frequency distributions and wastes vocabulary capacity on toxic phrases, vulgarities, and exploit sequences.
   - **Tokenizer Evaluation**: `ELIGIBLE` (strictly isolated chosen prompt evaluation).
   - **Alignment & Safety Evaluation**: `ELIGIBLE_PRIMARY`. Reserved as the primary benchmark for post-training safety and alignment auditing.
2. **`SRC-CD-02` (HumanEval & MBPP Benchmark)**:
   - **License**: MIT / Apache-2.0 (Permissive).
   - **Tokenizer Training**: `INELIGIBLE_PROHIBITED`. Including benchmark coding problems in tokenizer training creates severe test-set contamination and artificially inflates code compression metrics.
   - **Tokenizer Evaluation**: `ELIGIBLE`. Permitted for testing tokenizer compression and whitespace handling on unseen coding syntax.
3. **`SRC-ML-01` (FLORES-200 Benchmark)**:
   - **License**: CC-BY-SA 4.0.
   - **Tokenizer Training**: `INELIGIBLE_CONDITIONAL` (Quarantined benchmark test split).
   - **Tokenizer Evaluation**: `ELIGIBLE` (Standard multi-way parallel test suite).

---

## 4. Task 3: License Evidence Audit

`DATASET_LICENSE_EVIDENCE_V2.csv` documents primary legal evidence for all 32 sources:
- **Direct Evidence URLs**: Direct links to public repository license files, Creative Commons deeds, Open Data Commons licenses, and institutional copyright policies.
- **Commercial Use Permissions**:
  - `CONFIRMED` (19 sources): Explicit commercial grant under CC0, CC-BY, Apache-2.0, MIT, PSF, Unicode Data License.
  - `CONDITIONAL_COPYLEFT` (5 sources): CC-BY-SA 4.0 and GPL-2.0 requiring review of downstream model weight share-alike obligations.
  - `CONDITIONAL_ATTRIBUTION` (3 sources): ODC-By 1.0 requiring credit in model release manifests.
  - `UNCONFIRMED` (1 source): `SRC-TM-03` requires raw crawl rights audit.
  - `PROHIBITED` (4 sources): Non-commercial (`-NC`) licenses and copyright scrapes.
- **Redistribution & Share-Alike Analysis**: Fully documented per source.

---

## 5. Task 4: Project Gutenberg Item-Level Review

As detailed in `GUTENBERG_ITEM_LEVEL_REVIEW.md`:
1. **Rejection of Global Zero-Risk Claim**: Project Gutenberg operates under US copyright law (pre-1928 publication rule). In jurisdictions governed by the **Life + 70** rule (UK, EU, India), works by authors who died **after 1955** remain under full copyright protection in 2026. Claiming zero copyright risk globally is factually false and legally prohibited.
2. **Item-Level Verification Protocol**: Every individual EBook considered for `SRC-EN-01` or `SRC-CV-06` must pass a 6-step review verifying:
   - Author death year $\le 1955$.
   - Translator death year $\le 1955$ (for translated works).
   - Publication year prior to 1928.
3. **Trademark & Header Excision**: Paragraph 1.E of the Project Gutenberg license legally requires removing all "Project Gutenberg" trademarks, headers, and footers prior to redistribution or commercial training.

---

## 6. Task 5: Category 9 Conversational Reconciliation

In alignment with `CONVERSATIONAL_DATA_CLASSIFICATION.md`:
1. **Conversational Subtypes Decoupled**:
   - Subtype A: Ordinary conversational text.
   - Subtype B: Multi-turn dialogue (`SRC-CV-03` OASST1, `SRC-CV-05` MultiWOZ).
   - Subtype C: Preference pairs (`SRC-CV-04` HH-RLHF).
   - Subtype D: Rejected / red-team responses (`SRC-CV-04` HH-RLHF).
   - Subtype E: Literary theatrical dialogue (`SRC-CV-06` Project Gutenberg Theatrical).
2. **Three Functional Roles Defined**:
   - **Tokenizer Fertility Evaluation**: Subtypes B & E (`SRC-CV-03`, `SRC-CV-05`, `SRC-CV-06`, plus isolated Subtype C chosen prompts).
   - **Downstream Fine-Tuning**: Subtypes A & B (Supervised Fine-Tuning dialogue trees).
   - **Post-Training Alignment Evaluation**: Subtypes C & D (Preference optimization and red-team safety evaluations).

---

## 7. Task 6: Four Human Approval Roles Preservation

The four core governance roles established in Milestone 3B.60 are strictly preserved without alteration:
1. `DATA_CUSTODIAN`: Custody verification, manifest checksums, duplicate detection.
2. `LEGAL_GOVERNANCE`: License verification, commercial rights, copyleft review, Gutenberg item audits.
3. `SECURITY_PRIVACY`: PII policy enforcement, crawler safety, adversarial dataset boundary isolation.
4. `CHIEF_ARCHITECT`: Tokenizer architecture alignment, vocabulary budgets, benchmark contamination guards.

**Status**: All four approval slots remain `PENDING`. No signatures or approvals have been fabricated. The production access gate remains `LOCKED`.

---

## 8. Milestone 3C.7 Deliverables Summary

| Deliverable | Path | Description |
| :--- | :--- | :--- |
| **Integrity Master Report** | `IGRIS_3C7_INTEGRITY_REPORT.md` | Comprehensive milestone report addressing Tasks 1–6. |
| **Master Source Catalog V3** | `DATASET_SOURCE_CATALOG_V3.csv` | 32-source catalog with five decoupled governance and eligibility fields. |
| **Status Reconciliation CSV** | `SOURCE_STATUS_RECONCILIATION.csv` | Item-by-item status audit reconciling $20 + 7 + 1 + 4 = 32$. |
| **License Evidence V2 CSV** | `DATASET_LICENSE_EVIDENCE_V2.csv` | Primary license evidence URLs, terms, copyleft, and privacy risks. |
| **Eligibility Matrix** | `TOKENIZER_DATA_ELIGIBILITY_MATRIX.md` | Architectural rules decoupling training, evaluation, and alignment. |
| **Gutenberg Review Spec** | `GUTENBERG_ITEM_LEVEL_REVIEW.md` | Cross-jurisdictional copyright rules, Life+70 checks, trademark removal. |
| **Milestone Status Tracker** | `IGRIS_3C7_STATUS.md` | Formal milestone sign-off and safety audit tracker. |
| **Integrity Test Suite** | `tests/test_dataset_3c7_integrity.py` | Automated tests verifying schemas, counts, boundaries, and invariants. |
