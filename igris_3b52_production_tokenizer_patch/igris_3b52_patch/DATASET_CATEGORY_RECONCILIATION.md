# IGRIS Milestone 3C.3 — Dataset Category Reconciliation

**Document Version:** 1.0.0  
**Status:** Canonical Category Specification  
**Reference Document:** `DATASET_SPECIFICATION.md` (Milestone 3B.59)  
**Governing Standard:** IGRIS Benchmark Stratification Policy

---

## 1. Executive Summary

This document performs a formal reconciliation between the **original 10-category benchmark dataset specification** defined in `DATASET_SPECIFICATION.md` and the dataset categories mapped in `DATASET_SOURCE_CATALOG.csv`.

In accordance with IGRIS milestone instructions:
- The original approved specification remains the single authoritative ground truth.
- All naming variations, casing discrepancies, and symbol substitutions are documented.
- No category additions, removals, or re-allocations are adopted without a formal human Architectural Change Request signed by the `CHIEF_ARCHITECT`.

---

## 2. Category Reconciliation Matrix

The following table compares each approved category from `DATASET_SPECIFICATION.md` against the raw entries in `DATASET_SOURCE_CATALOG.csv`:

| ID | Approved Specification Category (`DATASET_SPECIFICATION.md`) | Catalog Category String (`DATASET_SOURCE_CATALOG.csv`) | Discrepancy Type | Source Count in Catalog | Reconciliation Action & Canonical Status |
|:---:|:---|:---|:---:|:---:|:---|
| **1** | **Tamil** | `Tamil` | Exact Match | 3 (`SRC-TM-01` to `03`) | **Preserve `Tamil`**. Canonical. |
| **2** | **English** | `English` | Exact Match | 3 (`SRC-EN-01` to `03`) | **Preserve `English`**. Canonical. |
| **3** | **Tanglish** | `Tanglish` | Exact Match | 3 (`SRC-TG-01` to `03`) | **Preserve `Tanglish`**. Canonical. |
| **4** | **Hindi** | `Hindi` | Exact Match | 3 (`SRC-HI-01` to `03`) | **Preserve `Hindi`**. Canonical. |
| **5** | **Other Indian Languages** | `Other Indian languages` | Casing (Sentence vs Title Case) | 3 (`SRC-OI-01` to `03`) | **Normalize to `Other Indian Languages`**. Covers Telugu, Malayalam, Kannada. |
| **6** | **Multilingual Mixed Text** | `Multilingual mixed text` | Casing (Sentence vs Title Case) | 2 (`SRC-ML-01` to `02`) | **Normalize to `Multilingual Mixed Text`**. Covers code-switched text. |
| **7** | **Programming Code** | `Programming code` | Casing (Sentence vs Title Case) | 2 (`SRC-CD-01` to `02`) | **Normalize to `Programming Code`**. Covers source code & schemas. |
| **8** | **Technical Documentation** | `Technical documentation` | Casing (Sentence vs Title Case) | 3 (`SRC-TD-01` to `03`) | **Normalize to `Technical Documentation`**. Covers RFCs, manuals, API docs. |
| **9** | **Conversational Text** | `Conversational text` | Casing (Sentence vs Title Case) | 2 (`SRC-CV-01` to `02`) | **Normalize to `Conversational Text`**. Covers multi-turn dialogue. |
| **10** | **Emoji & Unicode Edge Cases** | `Emoji and Unicode edge cases` | Symbol & Casing (`&` replaced by `and`, lowercase) | 2 (`SRC-EM-01` to `02`) | **Normalize to `Emoji & Unicode Edge Cases`**. Covers UCD, Emoji 15.1, stress cases. |

---

## 3. Analysis of Discrepancies

### 3.1 Naming and Casing Discrepancies
- **Casing Variations**: Five categories in `DATASET_SOURCE_CATALOG.csv` used sentence casing (e.g. `Other Indian languages`, `Programming code`) rather than the formal Title Case defined in `DATASET_SPECIFICATION.md`.
- **Ampersand vs Conjunction**: Category 10 used `Emoji and Unicode edge cases` instead of the canonical `Emoji & Unicode Edge Cases`.
- **Impact**: In string-matching scripts, case sensitivity or ampersand differences would cause silent partitioning failures or orphan evaluation buckets.
- **Resolution**: All ingestion scripts, manifests, and catalog references must enforce case-insensitive string parsing with canonical normalization to the exact string specified in `DATASET_SPECIFICATION.md`.

### 3.2 Evaluation of Additional / Ancillary Categories
In preliminary research and acquisition planning notes (Milestone 3C.2), two operational concepts were discussed:
1. **Synthetic Edge Cases**:
   - *Status*: Not a separate category. In accordance with `DATASET_SPECIFICATION.md` Section 2 (Category 10), synthetic edge cases (decomposed NFD ligatures, lone surrogates, ZWJ sequences, control characters) are structurally subsumed within **Category 10: Emoji & Unicode Edge Cases**.
2. **Pre-training Distribution Blend**:
   - *Status*: Not an evaluation category. Pre-training blend refers to the planned token sampling ratio (40% Tamil, 25% English, 15% Hindi, 10% Other Indian, 5% Code, 5% Technical) for training tokenizer vocabularies or models. The evaluation benchmark, however, requires isolated stratified evaluation across all 10 distinct categories.

### 3.3 Sub-Language Coverage under Category 5
`DATASET_SPECIFICATION.md` designates Category 5 as **Other Indian Languages**, encompassing Telugu, Kannada, Malayalam, Bengali, and Gujarati. In `DATASET_SOURCE_CATALOG.csv`, Category 5 is currently covered by three specific Dravidian languages:
- `SRC-OI-01`: IndicCorp v2 (Telugu, `te`)
- `SRC-OI-02`: IndicCorp v2 (Malayalam, `ml`)
- `SRC-OI-03`: IndicCorp v2 (Kannada, `kn`)

*Recommendation*: While Telugu, Malayalam, and Kannada provide vital representation for southern Dravidian scripts, future expansion to Indo-Aryan languages under Category 5 (Bengali `bn`, Gujarati `gu`) should be submitted for human approval to meet the full script diversity envisioned in `DATASET_SPECIFICATION.md`.

---

## 4. Preservation & Invariance Rule

Until a formal, written Architectural Change Request is signed by the `CHIEF_ARCHITECT`, the following invariants are strictly preserved:

1. **Category Count Invariant**: Exactly 10 evaluation categories.
2. **Category Naming Invariant**: Exactly match `DATASET_SPECIFICATION.md`:
   - `Tamil`
   - `English`
   - `Tanglish`
   - `Hindi`
   - `Other Indian Languages`
   - `Multilingual Mixed Text`
   - `Programming Code`
   - `Technical Documentation`
   - `Conversational Text`
   - `Emoji & Unicode Edge Cases`
3. **No Automatic Ingestion**: No candidate dataset from any source may be staged into evaluation folders without automated category validation ensuring strict adherence to this 10-category taxonomy.
