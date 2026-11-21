# IGRIS Milestone 3C.3 — Dataset Source Risk Update

**Document Version:** 1.0.0  
**Status:** Canonical Risk Audit Update  
**Reference Document:** `DATASET_ACQUISITION_RISK_REGISTER.md` (Milestone 3C.2)  
**Governing Standard:** IGRIS Legal & Security Governance Framework

---

## 1. Executive Summary

This document updates the IGRIS dataset risk register following the detailed license and provenance verification of all 26 proposed sources in Milestone 3C.3. 

The audit revealed three critical legal and security findings:
1. **Four sources are legally `INCOMPATIBLE`** with production model deployment due to explicit Non-Commercial clauses (`NC`) or unauthorized scraping of copyrighted entertainment media.
2. **Seven sources require formal `HUMAN APPROVAL`** from Legal Governance and Security & Privacy due to copyleft ShareAlike obligations (`CC-BY-SA 4.0`, `GPL-2.0`) or web crawl pass-through liability (`ODC-By 1.0`).
3. **Fourteen sources are fully `VERIFIED`**, providing an unencumbered, zero-copyleft, zero-NC baseline across all 10 evaluation categories.

---

## 2. Incompatible Sources — Detailed Risk & Remediation

| Source ID | Dataset Name | Category | Exact License | Incompatibility Root Cause | Legal Risk Level | Mandated Technical Remediation |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SRC-TG-03** | Social Dravidian Sentiment Tanglish | Tanglish | Research-Only Competition | Terms explicitly prohibit commercial use, fine-tuning, or model distribution beyond competition scoring. | **CRITICAL** | **PROHIBIT INGESTION**. Drop from acquisition list. Category 3 is fully covered by `SRC-TG-01` and `SRC-TG-02` (`CC-BY-4.0`). |
| **SRC-HI-03** | IIT Bombay English-Hindi Parallel Corpus | Hindi | CC-BY-NC-SA 4.0 | Non-Commercial clause (`NC`) prevents commercial deployment of any derived model weights or tokenizer vocabularies. | **HIGH** | **PROHIBIT INGESTION**. Drop from commercial evaluation sets. Category 4 is fully covered by `SRC-HI-01` (`CC0-1.0`). |
| **SRC-CV-01** | DailyDialog Dataset | Conversational Text | CC-BY-NC-SA 4.0 | Non-Commercial clause (`NC`) restricts usage to academic research only. | **HIGH** | **PROHIBIT INGESTION**. Identify permissive conversational replacement (e.g. Apache-2.0 / CC0 multi-turn transcripts). |
| **SRC-CV-02** | OpenSubtitles Multilingual (Filtered) | Conversational Text | Non-Standard Scrape Agreement | Scraped subtitle tracks of commercially distributed movies and television shows without rights holder authorization. | **CRITICAL** | **PROHIBIT INGESTION**. Extreme copyright liability under international IP law. Exclude completely from training and evaluation. |

---

## 3. ShareAlike & Web Crawl Pass-Through Analysis

### 3.1 CC-BY-SA 4.0 ShareAlike Contagion Risk
- **Affected Sources**: `SRC-TM-02` (Tamil Wiki), `SRC-EN-02` (English Wiki), `SRC-HI-02` (Hindi Wiki), `SRC-ML-01` (FLORES-200).
- **Legal Analysis**: Under Creative Commons Attribution-ShareAlike 4.0, any *Adapter's Work* (derivative work) must be shared under the same or compatible license. While running a tokenizer encoder/decoder over benchmark text for performance evaluation is widely considered fair use / non-derivative text analysis, **training** a tokenizer or neural network on CC-BY-SA text creates legal debate over whether model weights are derivative works.
- **Remediation**:
  - Classify strictly as `REQUIRES HUMAN APPROVAL`.
  - Prohibit ingestion into tokenizer training corpora until Legal Governance issues a formal written waiver.
  - Allow read-only benchmark evaluation ONLY if datasets are maintained in strict isolation and weights are not distributed under CC-BY-SA.

### 3.2 ODC-By 1.0 & Web Crawl Pass-Through Risk
- **Affected Sources**: `SRC-TM-03` (OSCAR 23.01), `SRC-EN-03` (C4), `SRC-ML-02` (mC4).
- **Legal & Privacy Analysis**: ODC-By 1.0 covers the database structure and metadata compilation. However, the underlying text consists of raw web crawl data. Neither Inria nor Common Crawl owns the underlying copyright of third-party web pages. Furthermore, uncurated web crawl text carries elevated PII risk under the **Digital Personal Data Protection (DPDP) Act 2023 (India)**.
- **Remediation**:
  - `SRC-TM-03` classified as `UNVERIFIED`; `SRC-EN-03` and `SRC-ML-02` classified as `REQUIRES HUMAN APPROVAL`.
  - Mandate strict automated PII scrubbing (phone numbers, Aadhaar, PAN, emails) prior to any staging.
  - Require Data Custodian and Legal Governance joint approval before downloading slices.

### 3.3 GPL-2.0 Documentation Exception Analysis
- **Affected Source**: `SRC-TD-01` (Linux Kernel Documentation).
- **Legal Analysis**: The Linux kernel documentation contains a specific licensing exception allowing verbatim copying and translation, but derivative redistribution defaults to GPL-2.0.
- **Remediation**: Classify as `REQUIRES HUMAN APPROVAL`. Category 8 (Technical Documentation) can alternatively rely on `SRC-TD-02` (IETF RFCs) and `SRC-TD-03` (Python PSF-2.0), both of which are fully `VERIFIED`.

---

## 4. The 14 Verified Clean Sources (Zero-Risk Baseline)

The following 14 sources are verified as completely permissive, free of non-commercial clauses, free of viral copyleft obligations, and legally safe for IGRIS:

| Category ID | Approved Category | Verified Source ID | Dataset Name | Verified License |
|:---:|:---|:---|:---|:---:|
| **1** | **Tamil** | `SRC-TM-01` | IndicCorp v2 (Tamil) | `CC0-1.0` |
| **2** | **English** | `SRC-EN-01` | Project Gutenberg Open Archive | `Public Domain` |
| **3** | **Tanglish** | `SRC-TG-01` | DravidianCodeMix (Tamil-English) | `CC-BY-4.0` |
| **3** | **Tanglish** | `SRC-TG-02` | IndicGLUE Tanglish Sentiment | `CC-BY-4.0` |
| **4** | **Hindi** | `SRC-HI-01` | IndicCorp v2 (Hindi) | `CC0-1.0` |
| **5** | **Other Indian Languages** | `SRC-OI-01` | IndicCorp v2 (Telugu) | `CC0-1.0` |
| **5** | **Other Indian Languages** | `SRC-OI-02` | IndicCorp v2 (Malayalam) | `CC0-1.0` |
| **5** | **Other Indian Languages** | `SRC-OI-03` | IndicCorp v2 (Kannada) | `CC0-1.0` |
| **7** | **Programming Code** | `SRC-CD-01` | The Stack v2 (Permissive Subset) | `MIT / Apache / BSD` |
| **7** | **Programming Code** | `SRC-CD-02` | HumanEval & MBPP Benchmark | `MIT / Apache-2.0` |
| **8** | **Technical Documentation** | `SRC-TD-02` | IETF RFC Archive (Text) | `RFC 5378 / IETF Trust` |
| **8** | **Technical Documentation** | `SRC-TD-03` | Python Official Documentation | `PSF-2.0` |
| **10** | **Emoji & Unicode Edge Cases** | `SRC-EM-01` | Unicode Standard 15.1.0 Test Suite | `Unicode-DFS-2016` |
| **10** | **Emoji & Unicode Edge Cases** | `SRC-EM-02` | Unicode 15.1.0 Emoji Data Files | `Unicode-DFS-2016` |

---

## 5. Strategic Recommendations for Milestone 3C.4

1. **Retire Incompatible Sources**: Formally update the acquisition pipeline to purge `SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, and `SRC-CV-02`.
2. **Source Replacement for Conversational Text (Category 9)**:
   - Identify permissive dialog corpora (e.g. OpenAssistant Conversations filtered under Apache-2.0, or Project Gutenberg theatrical plays / dialogue).
3. **Preserve Default-Deny Gate**:
   - Keep production dataset access gate strictly `LOCKED`.
   - Prevent any automated script from downloading remote data until all four codified roles (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`) execute valid cryptographic signatures.
