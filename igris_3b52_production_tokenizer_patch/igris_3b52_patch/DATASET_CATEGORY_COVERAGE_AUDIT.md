# IGRIS Milestone 3C.4 — Dataset Category Coverage Audit

**Document Version:** 1.0.0  
**Status:** Canonical Category Coverage Audit  
**Governing Standard:** `DATASET_SPECIFICATION.md` (Milestone 3B.59)  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

This document performs an exhaustive audit of benchmark category coverage across all 26 candidate sources in `DATASET_SOURCE_CATALOG.csv`, evaluating compliance against the 10 approved benchmark categories in `DATASET_SPECIFICATION.md`.

In strict adherence to milestone instructions:
1. The original ten canonical categories are strictly preserved.
2. Coverage for the five specified languages under Category 5 (**Telugu, Kannada, Malayalam, Bengali, Gujarati**) is rigorously evaluated.
3. **Missing source coverage is explicitly identified without inventing replacement sources.**
4. No candidate dataset may be ingested or downloaded during this audit.

---

## 2. Category Coverage Evaluation Matrix

| Category ID | Canonical Category Name | Script & Target Requirements (`DATASET_SPECIFICATION.md`) | Proposed Sources in Catalog | Verified Compliant Sources | Coverage Status | Critical Coverage Gaps & Findings |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **1** | **Tamil** | Tamil script (`\u0B80`–`\u0BFF`); $\ge 500$ samples; $\ge 100\text{k}$ words; $\ge 700\text{k}$ chars | `SRC-TM-01`, `SRC-TM-02`, `SRC-TM-03` | `SRC-TM-01` (`CC0-1.0`) | **FULL COVERAGE** | `SRC-TM-01` (3.8 GB) provides complete unencumbered coverage across classical literature, formal prose, and Grantha ligatures. |
| **2** | **English** | Latin script (`\u0020`–`\u007F`); $\ge 500$ samples; $\ge 120\text{k}$ words; $\ge 650\text{k}$ chars | `SRC-EN-01`, `SRC-EN-02`, `SRC-EN-03` | `SRC-EN-01` (`Public Domain`) | **FULL COVERAGE** | `SRC-EN-01` (12 GB, ~70k books) provides complete public domain coverage with zero PII and zero copyleft taint. |
| **3** | **Tanglish** | Latin script Romanized Tamil; $\ge 300$ samples; $\ge 50\text{k}$ words; $\ge 300\text{k}$ chars | `SRC-TG-01`, `SRC-TG-02`, `SRC-TG-03` | `SRC-TG-01` (`CC-BY-4.0`), `SRC-TG-02` (`CC-BY-4.0`) | **FULL COVERAGE** | Despite rejection of `SRC-TG-03`, `SRC-TG-01` and `SRC-TG-02` provide 60 MB (~59k utterances) of peer-reviewed Romanized Tamil. |
| **4** | **Hindi** | Devanagari script (`\u0900`–`\u097F`); $\ge 400$ samples; $\ge 80\text{k}$ words; $\ge 500\text{k}$ chars | `SRC-HI-01`, `SRC-HI-02`, `SRC-HI-03` | `SRC-HI-01` (`CC0-1.0`) | **FULL COVERAGE** | `SRC-HI-01` (12.5 GB, ~180M sentences) provides full coverage of news, formal prose, and complex conjuncts under CC0. |
| **5** | **Other Indian Languages** | Telugu, Kannada, Malayalam, Bengali, Gujarati; $\ge 300$ samples; $\ge 50\text{k}$ words; $\ge 350\text{k}$ chars | `SRC-OI-01`, `SRC-OI-02`, `SRC-OI-03` | `SRC-OI-01` (`CC0-1.0`), `SRC-OI-02` (`CC0-1.0`), `SRC-OI-03` (`CC0-1.0`) | **PARTIAL COVERAGE** | **CRITICAL GAP**: Covers Telugu, Malayalam, and Kannada (8.9 GB total). **Bengali (`bn`) and Gujarati (`gu`) have ZERO proposed sources in the catalog.** |
| **6** | **Multilingual Mixed Text** | Mixed Indic + Latin; $\ge 300$ samples; $\ge 60\text{k}$ words; $\ge 400\text{k}$ chars | `SRC-ML-01`, `SRC-ML-02` | None (Both require human legal approval) | **CONDITIONAL COVERAGE** | Both sources (`SRC-ML-01` CC-BY-SA, `SRC-ML-02` ODC-By/Crawl) require human sign-off. Zero unconditionally verified sources. |
| **7** | **Programming Code** | ASCII / UTF-8; $\ge 400$ samples; $\ge 80\text{k}$ words; $\ge 500\text{k}$ chars | `SRC-CD-01`, `SRC-CD-02` | `SRC-CD-01` (`Permissive`), `SRC-CD-02` (`MIT/Apache`) | **FULL COVERAGE** | Permissive subset covers Python, TypeScript, Rust, SQL, and JSON/YAML schemas. `SRC-CD-02` held out for eval only. |
| **8** | **Technical Documentation** | Markdown / UTF-8; $\ge 300$ samples; $\ge 60\text{k}$ words; $\ge 450\text{k}$ chars | `SRC-TD-01`, `SRC-TD-02`, `SRC-TD-03` | `SRC-TD-02` (`RFC Trust`), `SRC-TD-03` (`PSF-2.0`) | **FULL COVERAGE** | `SRC-TD-02` (IETF RFCs, 320 MB) and `SRC-TD-03` (Python Docs, 110 MB) provide over 430 MB of verified technical documentation. |
| **9** | **Conversational Text** | Multilingual dialogue; $\ge 300$ samples; $\ge 50\text{k}$ words; $\ge 300\text{k}$ chars | `SRC-CV-01`, `SRC-CV-02` | **NONE** (Both rejected as `INCOMPATIBLE`) | **ZERO COMPLIANT COVERAGE** | **CRITICAL DEFICIT**: `SRC-CV-01` has non-commercial clause (`NC`); `SRC-CV-02` has copyright liability. **Zero compliant sources exist.** |
| **10** | **Emoji & Unicode Edge Cases** | Unicode 15.1.0; $\ge 200$ samples; $\ge 20\text{k}$ words; $\ge 150\text{k}$ chars | `SRC-EM-01`, `SRC-EM-02` | `SRC-EM-01` (`Unicode-DFS`), `SRC-EM-02` (`Unicode-DFS`) | **FULL COVERAGE** | Official Unicode 15.1.0 UCD and Emoji test suites provide complete, authoritative coverage under Unicode-DFS-2016. |

---

## 3. Deep-Dive: Category 5 Sub-Language Verification

`DATASET_SPECIFICATION.md` Section 2 mandates that Category 5 (**Other Indian Languages**) must represent both Dravidian and Indo-Aryan language families:
- Dravidian: **Telugu**, **Kannada**, **Malayalam**
- Indo-Aryan: **Bengali**, **Gujarati**

### Sub-Language Audit Findings:
1. **Telugu (`te`, `Telu`)**:
   - Source: `SRC-OI-01` (IndicCorp v2 Telugu)
   - Status: **VERIFIED** (4.2 GB, ~52M sentences, `CC0-1.0`).
2. **Malayalam (`ml`, `Mlym`)**:
   - Source: `SRC-OI-02` (IndicCorp v2 Malayalam)
   - Status: **VERIFIED** (2.6 GB, ~31M sentences, `CC0-1.0`).
3. **Kannada (`kn`, `Knda`)**:
   - Source: `SRC-OI-03` (IndicCorp v2 Kannada)
   - Status: **VERIFIED** (2.1 GB, ~28M sentences, `CC0-1.0`).
4. **Bengali (`bn`, `Beng`)**:
   - Source: **NONE IN CATALOG**
   - Status: **MISSING SOURCE COVERAGE**. Zero candidate sources exist in `DATASET_SOURCE_CATALOG.csv`.
5. **Gujarati (`gu`, `Gujr`)**:
   - Source: **NONE IN CATALOG**
   - Status: **MISSING SOURCE COVERAGE**. Zero candidate sources exist in `DATASET_SOURCE_CATALOG.csv`.

**Conclusion on Category 5**: Category 5 exhibits robust Dravidian coverage (>8.9 GB under `CC0-1.0`), but completely lacks Indo-Aryan representation for Bengali and Gujarati in the proposed catalog. This gap must be resolved by human reviewers before final benchmark assembly. No replacement sources are fabricated.

---

## 4. Deep-Dive: Category 9 Deficit (Conversational Text)

Category 9 (**Conversational Text**) represents the most severe compliance vulnerability in the current dataset catalog:
- Proposed Source 1: `SRC-CV-01` (DailyDialog)
  - License: `CC-BY-NC-SA 4.0`
  - Finding: The explicit **Non-Commercial (`NC`)** restriction strictly prohibits commercial model deployment, creating legal liability.
- Proposed Source 2: `SRC-CV-02` (OpenSubtitles Multilingual)
  - License: Non-standard scrape
  - Finding: Content comprises transcribed or ripped movie subtitles owned by commercial entertainment studios without express licensing. Extreme copyright infringement liability.

**Conclusion on Category 9**: **Category 9 currently has 0 compliant candidate sources.** The evaluation corpus cannot be constructed for Category 9 using the current candidate catalog without violating IGRIS legal standards. Human reviewers must explicitly evaluate and acquire compliant conversational text sources under separate governance authorization.

---

## 5. Strategic Recommendations for Human Reviewers

1. **Acknowledge and Record Category Gaps**:
   - Formalize the absence of Bengali and Gujarati in Category 5.
   - Formalize the zero-coverage state of Category 9 (Conversational Text).
2. **Do Not Synthesize or Scrape Without Authorization**:
   - Reject any attempt by automated pipelines to backfill Category 5 or Category 9 with unverified sources.
3. **Permit Benchmarking on the 7 Fully Covered Categories**:
   - If human reviewers grant approval, initial comparative evaluation between Candidate A and Candidate B can proceed on the 7 fully verified categories (Tamil, English, Tanglish, Hindi, Programming Code, Technical Documentation, Emoji/Unicode), while Category 5 and Category 9 are remediated.
