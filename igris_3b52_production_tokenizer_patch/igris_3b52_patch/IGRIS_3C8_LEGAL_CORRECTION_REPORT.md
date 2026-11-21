# IGRIS Milestone 3C.8 — Legal Jurisdiction Correction & Pipeline Authorization Audit Report

**Project:** IGRIS (Decoder-Only Multilingual Transformer)  
**Active Patch:** `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Milestone:** 3C.8 — Legal Jurisdiction Correction & Pipeline Authorization Audit  
**Date:** 2026-11-17  
**Access Control Gate:** `LOCKED` (Default-Deny Enforced)  
**Dataset Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary

Milestone 3C.8 executes an exhaustive legal jurisdiction audit, statutory correction, license classification refinement, and pipeline authorization decoupling for the IGRIS multilingual tokenizer evaluation project.

In strict compliance with all milestone constraints and safety protocols:
1. **Zero Production Access & Zero Tokenizer Training**: No production datasets were opened, read, downloaded, staged, or ingested. No PII scans or model training routines were executed.
2. **Candidate Invariants Preserved**: Candidate A (`tokenizer.json`) and Candidate B (`tokenizer.model`) SHA-256 hashes remain perfectly identical to baselines.
3. **Statutory Indian Copyright Correction**: Corrected the erroneous "Life+70 in India" claim from 3C.7. Documented Section 22 of India's Copyright Act, 1957, which prescribes **Life + 60 years**, establishing that for calendar year 2026, the author death-year threshold in India is **1965** ($\le 1965$ in public domain), whereas **1955** applies strictly to Life+70 jurisdictions (UK/EU).
4. **License Classification Separation**: Categorized all 32 sources across 9 explicit license classes: `CC0` (7), `CC-BY` (2), `Apache-2.0` (2), `MIT` (1), `Public Domain` (2), `ShareAlike` (4), `GPL` (1), `ODC-By` (3), `Other / Unknown` (10). Formally documented that neither CC-BY nor Apache-2.0 is "unrestricted."
5. **Decoupled Pipeline Authorization Boundaries**: Created six independent permission fields across all 32 sources. Enforced the foundational architectural rule that **tokenizer eligibility does not grant model-training permission**. Supervised Fine-Tuning (SFT), alignment evaluation, and safety evaluation remain **`NOT AUTHORIZED`** across the board.
6. **Anthropic HH-RLHF (`SRC-CV-04`) Isolation**: Confirmed that `SRC-CV-04` is strictly prohibited from tokenizer vocabulary training to prevent toxic vocabulary poisoning. Isolated its evaluation usage to post-training alignment/safety evaluation (currently `NOT AUTHORIZED`), with fertility evaluation strictly restricted to an isolated chosen-prompts subset (`SRC-CV-04-CHOSEN-PROMPTS-ISOLATED`).
7. **Multi-Jurisdictional Project Gutenberg Review**: Updated the Gutenberg review to account for Indian Life+60, US pre-1928, and UK/EU Life+70 divergence. Reaffirmed that zero global copyright risk cannot be claimed, and mandated four-pillar item-level clearance.
8. **Preservation of Four Core Roles**: Strictly preserved `DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, and `CHIEF_ARCHITECT` without alteration or signature fabrication.

---

## 2. Task 1: Indian Copyright Law Correction & Statutory Review

### 2.1 Statutory Basis (The Copyright Act, 1957)
In Milestone 3C.7, preliminary documentation conflated Indian copyright duration with European Life+70 standards. This has been corrected using official statutory authorities:
- **Principal Statute**: The Copyright Act, 1957 (Act No. 14 of 1957, as amended).
- **Section 22 (Ordinary Term for Literary Works)**:
  Copyright subsists in any literary, dramatic, musical, or artistic work published within the lifetime of the author until **60 years from the beginning of the calendar year next following the year in which the author dies**.

### 2.2 Threshold Calculation for Calendar Year 2026
Under Section 22:
$$\text{Indian Public Domain Entry Date} = \text{January 1, } (Y_{\text{death}} + 61)$$

- **Death Year $\le 1965$**: Author died on or before Dec 31, 1965. The 60-year statutory clock started Jan 1, 1966 and expired Dec 31, 2025. The work entered the Indian public domain on **January 1, 2026**.
- **Death Year $\ge 1966$**: Author died in 1966 or later. The 60-year statutory clock started Jan 1, 1967 and expires Dec 31, 2026. The work remains **under copyright in India throughout 2026**.
- **Correction**: The death-year threshold in India is **1965**, not 1955. The 1955 threshold applies strictly to jurisdictions with **Life + 70** rules (United Kingdom and European Union).

### 2.3 Statutory Exceptions to Section 22
A work cannot be cleared solely by checking whether the author died before 1966. Four statutory exceptions must be evaluated:
1. **Joint Authorship (Section 22 Explanation)**:
   Copyright subsists until 60 years after the death of the **last surviving author**. If a co-author died in 1970, the work remains protected in India until January 1, 2031.
2. **Anonymous and Pseudonymous Works (Section 23)**:
   Copyright subsists until **60 years from the year of first publication**, unless the author's identity is disclosed before expiry.
3. **Posthumous Works (Section 24)**:
   If a work was not published during the author's lifetime, copyright subsists until **60 years from the year of first publication**. A manuscript written by an author who died in 1920 but first published in 1980 is protected in India until January 1, 2041.
4. **Government Works (Section 28)**:
   Copyright subsists for 60 years from the date of first publication. Unlike US federal works, Indian government works are not automatically public domain.

### 2.4 Why Older Works Cannot Automatically Be Presumed Public Domain
- **Independent Translation Copyright (Section 2(d)(v) & 14)**: Modern translations of ancient or public domain epics (e.g., Sanskrit or Tamil classics) carry independent copyright owned by the translator.
- **Critical Editions & Annotations**: Editorial apparatus, commentary, textual reconstructions, and footnotes carry separate copyright.
- **Author's Special Moral Rights (Section 57)**: Author's paternity and integrity rights survive copyright assignment during lifetime and may be exercised by legal representatives under Section 57(2). Blanket claims of perpetual moral rights post-copyright expiry lack statutory consensus (*Amar Nath Sehgal v. Union of India*, 2005 arose during active copyright subsistence), but attribution preservation remains an ethical and governance mandate.

Full legal analysis is codified in [INDIA_COPYRIGHT_REVIEW.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/INDIA_COPYRIGHT_REVIEW.md).

---

## 3. Task 2: Granular License Classification & Restrictions

In [DATASET_LICENSE_CLASSIFICATION_V3.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_LICENSE_CLASSIFICATION_V3.csv), all 32 sources are categorized across 9 distinct license classes:

| License Category | Source Count | Source IDs | Core Legal Characteristics & Obligations |
| :--- | :---: | :--- | :--- |
| **CC0** | **7** | `SRC-TM-01`, `SRC-HI-01`, `SRC-OI-01` to `05` | Unencumbered public domain dedication; no legal attribution mandated by deed, though academic citation is customary. |
| **CC-BY** | **2** | `SRC-TG-01`, `SRC-TG-02` | Permissive with **mandatory attribution**. **NOT unrestricted**: must credit author, link license, retain notices, and state changes. |
| **Apache-2.0** | **2** | `SRC-CV-03`, `SRC-CV-05` | Permissive with **mandatory attribution**. **NOT unrestricted**: must retain NOTICE/LICENSE files, copyright/patent notices, and document modified files. |
| **MIT** | **1** | `SRC-CV-04` | Permissive with mandatory copyright and permission notice retention. |
| **Public Domain** | **2** | `SRC-EN-01`, `SRC-CV-06` | Free from economic copyright in US and India; subject to mandatory removal of Project Gutenberg trademarks and headers (PGLAF Sec 1.E). |
| **ShareAlike** | **4** | `SRC-TM-02`, `SRC-EN-02`, `SRC-HI-02`, `SRC-ML-01` | Reciprocal viral copyleft: downstream derivative works (including model weights if deemed derivative) must be licensed under CC-BY-SA 4.0. |
| **GPL** | **1** | `SRC-TD-01` | Strong reciprocal copyleft (GPL-2.0). Linux kernel docs contain userspace syscall documentation exemption, but general modifications require GPL source availability. |
| **ODC-By** | **3** | `SRC-TM-03`, `SRC-EN-03`, `SRC-ML-02` | Open Data Commons Attribution License: database notice and attribution required in any public use; crawl underlying rights unvetted. |
| **Other / Unknown** | **10** | `SRC-TG-03`, `SRC-HI-03`, `SRC-CD-01`, `SRC-CD-02`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-01`, `SRC-CV-02`, `SRC-EM-01`, `SRC-EM-02` | Multi-license permissive mixes (The Stack v2, HumanEval/MBPP), standards provisions (IETF Trust, PSF-2.0, Unicode DFS), or incompatible non-commercial/scrape terms (`-NC`, OpenSubtitles). |
| **Total** | **32** | **All 32 Canonical Sources** | **Every source has an audited license classification.** |

---

## 4. Task 3: Decoupled Pipeline Authorization Boundaries

A critical architectural principle enforced in Milestone 3C.8:
> **Tokenizer eligibility does NOT grant model-training permission.**

In [PIPELINE_AUTHORIZATION_MATRIX_V2.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PIPELINE_AUTHORIZATION_MATRIX_V2.csv), six independent permission fields govern each source:

```
+----------------------------------------------------------------------------------------------------+
|                         PIPELINE AUTHORIZATION STATE BREAKDOWN (32 SOURCES)                        |
+----------------------------------------------------------------------------------------------------+
1. Tokenizer Vocabulary Training:
   ├── ELIGIBLE_PENDING_APPROVAL:     18 (56.3%)  [Verified baseline corpora]
   ├── INELIGIBLE_CONDITIONAL:         8 (25.0%)  [Conditional pending legal sign-off]
   ├── STRICTLY_PROHIBITED:            2 ( 6.3%)  [SRC-CD-02 (Contamination), SRC-CV-04 (Safety)]
   └── INELIGIBLE_REJECTED:            4 (12.5%)  [Incompatible licenses/scrapes]

2. Tokenizer Fertility Evaluation:
   ├── ELIGIBLE_PENDING_APPROVAL:     27 (84.4%)
   ├── ELIGIBLE_ISOLATED_PROMPTS_ONLY: 1 ( 3.1%)  [SRC-CV-04: Isolated chosen prompts only]
   └── INELIGIBLE_REJECTED:            4 (12.5%)

3. Tokenizer Regression Evaluation:
   ├── ELIGIBLE_PENDING_APPROVAL:     28 (87.5%)
   └── INELIGIBLE_REJECTED:            4 (12.5%)

4. Supervised Fine-Tuning (SFT):
   └── NOT AUTHORIZED:                32 (100.0%) [STRICTLY PROHIBITED FOR ALL SOURCES]

5. Alignment Evaluation:
   ├── NOT AUTHORIZED (DESIGNATED):    3 ( 9.4%)  [SRC-CV-04 Primary; SRC-CD-02, SRC-CV-03 Optional]
   └── NOT AUTHORIZED:                29 (90.6%)

6. Safety Evaluation:
   ├── NOT AUTHORIZED (DESIGNATED):    1 ( 3.1%)  [SRC-CV-04 Designated Benchmark]
   └── NOT AUTHORIZED:                31 (96.9%)
```

**Policy Enforcement**:
- No source is authorized for Supervised Fine-Tuning.
- Post-training alignment and safety pipelines remain `NOT AUTHORIZED` until dedicated human governance approval.
- Production access gate remains locked at default-deny.

---

## 5. Task 4: Anthropic HH-RLHF (`SRC-CV-04`) Isolation

`SRC-CV-04` (Anthropic HH-RLHF) is strictly quarantined:
1. **Tokenizer Vocabulary Training**: `STRICTLY_PROHIBITED`. Merging preference pairs or red-team responses into subword tokenizers corrupts the 32,768 vocabulary budget with atomic tokens for toxic phrases, slurs, and cyberattack primitives.
2. **Alignment & Safety Evaluation**: Designated as the primary downstream benchmark for measuring helpfulness and harmlessness refusal rates. Currently `NOT AUTHORIZED` pending post-training milestone sign-offs.
3. **Tokenizer Fertility Evaluation**: Restricted strictly to an isolated, pre-processed subset: `SRC-CV-04-CHOSEN-PROMPTS-ISOLATED`. This subset extracts only user prompt prefixes from the helpful base split, completely omitting assistant completions, preference rankings, and red-team attacks.

---

## 6. Task 5: Project Gutenberg Multi-Jurisdictional Protocol (V2)

In [GUTENBERG_JURISDICTION_REVIEW_V2.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/GUTENBERG_JURISDICTION_REVIEW_V2.md):
1. **Tri-Jurisdictional Matrix**:
   - **United States**: Pre-1928 publication rule.
   - **India**: Section 22 Life + 60 rule ($\le 1965$ author death threshold in 2026).
   - **UK & EU**: Life + 70 rule ($\le 1955$ author death threshold in 2026).
2. **Rejection of Global Zero-Risk Claim**: It is legally impossible to claim zero global copyright risk for Project Gutenberg. A work published in 1925 by an author who died in 1962 is public domain in the US and India, but fully protected in the UK and EU until 2033! Global release requires meeting the **strictest applicable standard**.
3. **Four-Pillar Item-Level Review**:
   - Pillar 1: Author rights & last surviving co-author death date.
   - Pillar 2: Translator death date (derivative work rights).
   - Pillar 3: Lifetime vs posthumous publication check (Indian Section 24).
   - Pillar 4: Editorial, critical, and adaptation rights check.
4. **Trademark Removal**: Mandatory stripping of all "Project Gutenberg" trademarks and headers per PGLAF Section 1.E.

---

## 7. Milestone 3C.8 Deliverables

| Deliverable | Path | Description |
| :--- | :--- | :--- |
| **Milestone Master Report** | `IGRIS_3C8_LEGAL_CORRECTION_REPORT.md` | Master synthesis, legal corrections, and governance audit. |
| **Indian Copyright Review** | `INDIA_COPYRIGHT_REVIEW.md` | Statutory analysis of Section 22, Life+60, exceptions, and moral rights. |
| **License Classification V3** | `DATASET_LICENSE_CLASSIFICATION_V3.csv` | 32 sources categorized across 9 classes with detailed restrictions. |
| **Pipeline Authorization V2** | `PIPELINE_AUTHORIZATION_MATRIX_V2.csv` | 6 independent permission fields; SFT/Alignment `NOT AUTHORIZED`. |
| **Gutenberg Jurisdiction V2** | `GUTENBERG_JURISDICTION_REVIEW_V2.md` | Multi-jurisdictional review, Indian Life+60 integration, 4-pillar review. |
| **Milestone Status Tracker** | `IGRIS_3C8_STATUS.md` | Governance gate record and technical verification summary. |
| **Governance Test Suite** | `tests/test_dataset_3c8_governance.py` | Automated tests verifying legal rules, schemas, boundaries, and hashes. |

---

## 8. Governance Invariants & Technical Regression

1. **Four Core Approval Roles Preserved**:
   - `DATA_CUSTODIAN`: Pending
   - `LEGAL_GOVERNANCE`: Pending
   - `SECURITY_PRIVACY`: Pending
   - `CHIEF_ARCHITECT`: Pending
2. **Candidate Artifact Checksums (100% Invariant)**:
   - Candidate A (`tokenizer.json`): `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
   - Candidate B (`tokenizer.model`): `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
3. **Current Gate Status**: `LOCKED`. Zero datasets acquired.
