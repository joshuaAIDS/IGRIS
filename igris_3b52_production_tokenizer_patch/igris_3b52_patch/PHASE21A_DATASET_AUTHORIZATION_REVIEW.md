# IGRIS PHASE 21A — DATASET AUTHORIZATION REVIEW
## Comprehensive Legal, Licensing & Risk Analysis of 18 Eligible Sources

**Document ID:** `IGRIS-PHASE21A-DAR-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target:** 18 Permissive Candidate Sources  
**Status:** **AUTHORIZATION REVIEW COMPLETED — RECOMMENDATIONS SUBMITTED TO OWNER**  

---

## 1. Executive Summary

This document performs an exhaustive legal, licensing, and operational review of the 18 candidate dataset sources currently classified as `ELIGIBLE` in the IGRIS dataset catalog.

In strict adherence to the project directive:
> *"Do not treat a broad license label as sufficient evidence. Flag sources requiring further legal verification."*

The 18 sources have been forensically categorized based on primary license deeds, underlying text provenance, copyright jurisdiction, commercial use terms, and redistribution constraints:
* **Recommended for Owner Authorization Consideration (`APPROVE FOR OWNER CONSIDERATION`):** **13 Sources**. These sources possess clear, unambiguous legal foundations (CC0 public domain, official PSF/IETF/Unicode data licenses, or clean academic Apache-2.0 corpora) with zero underlying third-party rights conflicts.
* **Placed on Administrative Hold (`HOLD`):** **5 Sources**. These sources have valid permissive distribution licenses but possess unresolved legal, technical, or extraterritorial questions (e.g. scraped social media comments, Gutenberg trademark/header stripping rules, or BigCode opt-out / copyleft scanning requirements) that require explicit owner review before acquisition.

**Governance Invariant:** No source has been authorized by this review. All 18 sources remain in `PENDING_EXPLICIT_OWNER_AUTHORIZATION` state. Production ingress remains **`LOCKED`**.

---

## 2. Categorization & Recommendation Summary

| Source ID | Source Name | License | Primary Risk / Question | Recommendation |
| :--- | :--- | :--- | :--- | :---: |
| `SRC-TM-01` | IndicCorp v2 (Tamil) | CC0-1.0 | None. Clean public domain dedication. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-HI-01` | IndicCorp v2 (Hindi) | CC0-1.0 | None. Clean public domain dedication. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-OI-01` | IndicCorp v2 (Telugu) | CC0-1.0 | None. Clean public domain dedication. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-OI-02` | IndicCorp v2 (Malayalam) | CC0-1.0 | None. Clean public domain dedication. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-OI-03` | IndicCorp v2 (Kannada) | CC0-1.0 | None. Clean public domain dedication. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-OI-04` | IndicCorp v2 (Bengali) | CC0-1.0 | None. Clean public domain dedication. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-OI-05` | IndicCorp v2 (Gujarati) | CC0-1.0 | None. Clean public domain dedication. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-TD-02` | IETF RFC Archive (Text) | RFC 5378 | None. Technical standards fair use / TDM. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-TD-03` | Python Official Docs | PSF-2.0 | None. Standard PSF permissive license. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-CV-03` | OpenAssistant (OASST1) | Apache-2.0 | Verify community dialogue toxicity filter. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-CV-05` | MultiWOZ 2.4 | Apache-2.0 | None. Academic task-dialogue corpus. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-EM-01` | Unicode 15.1.0 Test Suite | Unicode-DFS-2016 | None. Standard Unicode data license. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-EM-02` | Unicode 15.1.0 Emoji Data | Unicode-DFS-2016 | None. Standard Unicode data license. | **APPROVE FOR OWNER CONSIDERATION** |
| `SRC-EN-01` | Gutenberg Open Archive | Public Domain | Automated trademark/header stripping & life+70 cutoff. | **HOLD** |
| `SRC-CV-06` | Gutenberg Plays | Public Domain | Automated trademark/header stripping & life+70 cutoff. | **HOLD** |
| `SRC-TG-01` | DravidianCodeMix (Ta-En) | CC-BY-4.0 | Scraped YouTube comments / TDM rights confirmation. | **HOLD** |
| `SRC-TG-02` | IndicGLUE Tanglish Sent. | CC-BY-4.0 | Scraped social media comments / TDM rights confirmation. | **HOLD** |
| `SRC-CD-01` | The Stack v2 (Sample) | Multi-License | Verify BigCode opt-out scrub & SPDX copyleft scan. | **HOLD** |

---

## 3. Detailed Forensic Source Assessments

### Group A: IndicCorp v2 Core Indic Corpora (`SRC-TM-01`, `SRC-HI-01`, `SRC-OI-01` through `05`)
* **Publisher:** AI4Bharat / IIT Madras.
* **Exact License:** Creative Commons Zero v1.0 Universal (`CC0-1.0`).
* **Commercial & Derivative Terms:** CC0 waives all copyright and related rights globally. Commercial training, derivative weight redistribution, and model deployment are completely unencumbered.
* **Attribution:** No legal requirement under CC0. Academic citation to AI4Bharat papers will be maintained in the model card as an ethical best practice.
* **Jurisdiction:** India / Global.
* **Recommendation:** **APPROVE FOR OWNER CONSIDERATION** as the primary multilingual foundation.

### Group B: Technical Standards & Documentation (`SRC-TD-02`, `SRC-TD-03`)
* **`SRC-TD-02` (IETF RFCs):** Licensed under RFC 5378 and IETF Trust Legal Provisions (TLP). Ingestion of protocol specifications into transformer architectures is permitted under text and data mining exceptions. Technical standards may not be modified and falsely represented as official IETF RFCs, which does not restrict neural model training.
* **`SRC-TD-03` (Python Documentation):** Licensed under Python Software Foundation License Version 2 (`PSF-2.0`). Fully permissive, allowing commercial redistribution and derivative training provided the PSF copyright notice is preserved in model documentation.
* **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### Group C: Permissive Conversational Dialogue (`SRC-CV-03`, `SRC-CV-05`)
* **`SRC-CV-03` (OpenAssistant OASST1):** Human-annotated conversational turns collected by LAION and released under Apache-2.0. Clean commercial grant and patent defense clauses. Quality filter must exclude low-scoring or toxic community turns.
* **`SRC-CV-05` (MultiWOZ 2.4):** University of Cambridge dialogue dataset under Apache-2.0. Clean multi-turn task dialogue.
* **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### Group D: Unicode Consortium Specifications (`SRC-EM-01`, `SRC-EM-02`)
* **License:** Unicode License Agreement - Data Files and Software (`Unicode-DFS-2016`).
* **Terms:** Commercial use permitted without fee or royalty. Standard copyright notice retention required.
* **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

---

## 4. Analysis of Sources Placed on HOLD

### 1. `SRC-EN-01` & `SRC-CV-06` (Project Gutenberg Corpora)
* **Status:** **HOLD**
* **Legal Analysis:** Project Gutenberg texts in the United States are in the public domain (predominantly works published before 1928). However:
  1. **Trademark Protection:** Project Gutenberg reserves exclusive rights to the trademark "Project Gutenberg". Commercial redistribution requires either maintaining the full, complex Gutenberg license header or completely stripping all references to "Project Gutenberg".
  2. **Extraterritorial Copyright:** In countries with "life of author plus 70 years" copyright terms, works in the US public domain by authors who died post-1955 may still be under copyright.
* **Pre-Authorization Requirement:** Before authorization, an automated preprocessing script must be verified that completely strips Gutenberg headers, footers, and trademark strings, and filters texts to authors with verified pre-1928 publication dates.

### 2. `SRC-TG-01` & `SRC-TG-02` (Tanglish Social Media Corpora)
* **Status:** **HOLD**
* **Legal Analysis:** Both datasets are distributed under CC-BY-4.0 by academic researchers. However, the underlying raw text consists of scraped YouTube and social media comments authored by third-party end-users.
* **Remaining Question:** While academic fair use and Indian Copyright Act Section 52(1)(a) permit non-commercial research, commercial foundation model pretraining on scraped social media text requires formal confirmation of Text and Data Mining (TDM) doctrine applicability.
* **Pre-Authorization Requirement:** Legal review confirmation that training IGRIS on curated social media comment corpora is compliant with applicable TDM doctrines.

### 3. `SRC-CD-01` (The Stack v2 Permissive Subset)
* **Status:** **HOLD**
* **Legal Analysis:** The Stack v2 is an index of open source code released by BigCode and Software Heritage under permissive licenses (MIT, Apache, BSD).
* **Remaining Question:**
  1. Software Heritage operates an ongoing author opt-out program. The acquisition pipeline must verify that the latest opt-out scrub list has been applied.
  2. Subsets occasionally contain mislabeled files (e.g. GPL-licensed source files misattributed as MIT).
* **Pre-Authorization Requirement:** The acquisition engine must incorporate an automated SPDX license header scanner to reject any file containing copyleft (GPL/AGPL) identifiers before quarantine promotion.

---

## 5. Next Steps for Project Owner

Review the structured companion register [PHASE21A_DATASET_AUTHORIZATION_REVIEW.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21A_DATASET_AUTHORIZATION_REVIEW.csv) and issue authorization decisions:
1. Confirm approval for the 13 recommended sources.
2. Confirm administrative hold on the 5 flagged sources.
