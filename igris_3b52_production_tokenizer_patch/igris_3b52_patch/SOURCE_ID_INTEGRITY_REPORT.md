# IGRIS Milestone 3C.6 — Source Identifier Integrity Report

**Document Version:** 1.0.0  
**Status:** Canonical Identifier Audit  
**Governing Standard:** IGRIS Data Catalog Integrity & Provenance Policy  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

During Milestone 3C.5, the conversational dataset research proposed several new candidate sources for Category 9 (Conversational Text). However, an apparent numerical gap occurred: `SRC-CV-03`, `SRC-CV-04`, and `SRC-CV-06` appeared in the gap resolution summary table, while `SRC-CV-05` was omitted.

In accordance with strict IGRIS governance principles:
1. **Existing records and identifiers must never be silently renumbered or repurposed.**
2. Source identifiers must remain stable, immutable, and globally unique across all milestone documents.
3. This report investigates the historical provenance of `SRC-CV-05`, resolves the omission, and codifies the master numbering schema for `DATASET_SOURCE_CATALOG_V2.csv`.

---

## 2. Investigation of `SRC-CV-05`

### 2.1 Provenance & Root Cause Analysis
- **Milestone 3C.5 Research (`CONVERSATIONAL_DATASET_RESEARCH.md`)**:
  - In Section 3.3, the research evaluated **MultiWOZ 2.4 (Multi-Domain Wizard-of-Oz)**, assigning it identifier **`SRC-CV-05`**:
    - *Owner*: University of Cambridge Dialogue Systems Group (Budzianowski et al.)
    - *Official URL*: `https://github.com/budzianowski/multiwoz`
    - *License*: `Apache-2.0`
    - *Characteristics*: ~10,400 task-oriented dialogues (~143,000 turns) covering booking, customer service, and structured user-system interactions.
  - In Section 3.4, **Project Gutenberg Theatrical Dramatic Dialogue** was evaluated and assigned identifier **`SRC-CV-06`**:
    - *Owner*: Project Gutenberg Literary Archive Foundation
    - *License*: `Public Domain` (US)
- **The Omission Root Cause**:
  - In Section 4 of `CONVERSATIONAL_DATASET_RESEARCH.md` and subsequent summary tables in `DATASET_GAP_RESOLUTION_PLAN.md`, the author condensed the conversational suite to a 3-source primary blend (`SRC-CV-03` OpenAssistant, `SRC-CV-04` Anthropic HH-RLHF, `SRC-CV-06` Project Gutenberg), omitting `SRC-CV-05` (MultiWOZ 2.4) as a secondary task-dialogue source.
  - This created a cosmetic gap between `04` and `06` in summary tables, though `SRC-CV-05` was legitimately defined in the research text.

### 2.2 Re-numbering Prohibition & Ruling
- **Prohibition**: Renumbering `SRC-CV-06` to `SRC-CV-05` would invalidate cryptographic references, test scripts, and documentation cross-references in Milestone 3C.5 deliverables (`BENGALI_GUJARATI_SOURCE_RESEARCH.md`, `CONVERSATIONAL_DATASET_RESEARCH.md`, `DATASET_GAP_RESOLUTION_PLAN.md`, `tests/test_dataset_3c5_review.py`).
- **Ruling**: **Preserve stable source IDs.**
  - `SRC-CV-05` is formally restored to the active catalog as **MultiWOZ 2.4 (Multi-Domain Task Dialogue)** under `Apache-2.0`.
  - `SRC-CV-06` remains **Project Gutenberg Theatrical Dramatic Dialogue** under `Public Domain`.
  - This ensures all conversational identifiers `SRC-CV-01` through `SRC-CV-06` form a continuous, fully reconciled sequence.

---

## 3. Master Category 9 Identifier Sequence

| Source ID | Dataset Name | Governing License | Volume Estimate | Provenance Type | Catalog Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **SRC-CV-01** | DailyDialog Dataset | `CC-BY-NC-SA 4.0` | 12 MB (~13k dialogues) | Simulated ESL dialogues | **INCOMPATIBLE (REJECTED)** |
| **SRC-CV-02** | OpenSubtitles Multilingual (Filtered) | Non-Standard Scrape | 4.5 GB (Subtitles) | Scraped commercial film subtitles | **INCOMPATIBLE (REJECTED)** |
| **SRC-CV-03** | OpenAssistant Conversations (OASST1) | `Apache-2.0` | 50 MB (~161k messages) | Human crowd-worker dialogue trees | **VERIFIED (CLEARED)** |
| **SRC-CV-04** | Anthropic HH-RLHF | `MIT` | 40 MB (~160k sessions) | Human-model conversational evaluations | **VERIFIED (CLEARED)** |
| **SRC-CV-05** | MultiWOZ 2.4 | `Apache-2.0` | 15 MB (~10.4k dialogues) | Task-oriented goal dialogue | **VERIFIED (CLEARED)** |
| **SRC-CV-06** | Project Gutenberg Theatrical Dialogue | `Public Domain` | 25 MB (Dramatic plays) | Published historical stage plays | **VERIFIED (CLEARED)** |

---

## 4. Master Category 5 Identifier Sequence

Similarly, the addition of Bengali and Gujarati in Category 5 follows a strictly sequential, non-conflicting numbering schema:

| Source ID | Dataset Name | Sub-Language | Governing License | Volume Estimate | Catalog Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | Telugu (`te`) | `CC0-1.0` | 4.2 GB (~52M sentences) | **VERIFIED (CLEARED)** |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | Malayalam (`ml`) | `CC0-1.0` | 2.6 GB (~31M sentences) | **VERIFIED (CLEARED)** |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | Kannada (`kn`) | `CC0-1.0` | 2.1 GB (~28M sentences) | **VERIFIED (CLEARED)** |
| **SRC-OI-04** | IndicCorp v2 (Bengali) | Bengali (`bn`) | `CC0-1.0` | 7.8 GB (~85M sentences) | **VERIFIED (CLEARED)** |
| **SRC-OI-05** | IndicCorp v2 (Gujarati) | Gujarati (`gu`) | `CC0-1.0` | 4.1 GB (~48M sentences) | **VERIFIED (CLEARED)** |

---

## 5. Catalog Stability Invariant

1. **Immutable Source IDs**: Once assigned, a `SRC-<CAT>-<NUM>` identifier is permanent. It represents a specific dataset version, ownership, and license.
2. **Rejection Retention**: Rejected or incompatible sources (`SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02`) retain their IDs in historical catalogs to prevent accidental re-introduction and maintain auditability.
3. **Additive Numbering**: Any future expansion must increment the category sequence (`SRC-OI-06`, `SRC-CV-07`, etc.) without backfilling or altering existing records.
