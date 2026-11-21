# PHASE 23 — TAMIL SOURCE LEGAL & TECHNICAL READINESS AUDIT
## Comprehensive Rights Layer Analysis, Provenance Verification, and Risk Assessment

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 23  
**Language Scope:** TAMIL (`ta`)  
**Status:** AUDITED & CATEGORIZED  

---

## 1. Executive Summary

This review package conducts a source-specific legal, contractual, and technical audit of all candidate Tamil datasets in the IGRIS inventory under the narrowed language scope.

Three candidate Tamil sources were reviewed:
1. `SRC-TM-01`: IndicCorp v2 (Tamil subset, `data/ta.txt`)
2. `SRC-TM-02`: Tamil Wikipedia Articles Dump
3. `SRC-TM-03`: OSCAR 23.01 Tamil (Filtered)

**Summary Finding:** All 3 Tamil sources carry underlying copyright, terms of service, or copyleft sharealike risks that prevent immediate automatic authorization. In accordance with strict governance principles, all 3 sources are designated as **`PENDING_LEGAL_REVIEW`** and **`PENDING_OWNER_AUTHORIZATION`**. Zero sources are authorized for production acquisition.

---

## 2. In-Depth Legal Review: `SRC-TM-01` (IndicCorp v2 Tamil)

```
+------------------------------------+----------------------------------------------------------+
| Review Parameter                   | Verified Source Metadata & Audit Findings                |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-TM-01                                                |
| Dataset Name                       | IndicCorp v2 (Tamil Subset)                              |
| Upstream Repository                | ai4bharat/IndicCorpV2 (Hugging Face / GitHub)            |
| Pinned Revision                    | 984b75b20ce408f9ba27c6558e9279e8e1b6edfd                 |
| Exact File Path                    | data/ta.txt                                              |
| Git Tree Entry Blob SHA            | c64366bb320573be263d91f1bcf4b664fc8c11e7                 |
| Declared Payload Size              | 30.50 GB decimal (28.41 GiB binary)                       |
| Line Count / Word Count            | ~14,035,000 lines / ~386,000,000 words                   |
| Published Compilation License      | Creative Commons Zero 1.0 Universal (CC0-1.0)            |
+------------------------------------+----------------------------------------------------------+
```

### Seven-Layer Legal Rights Analysis:
1. **Dataset Compilation License (CC0-1.0):**
   - AI4Bharat (IIT Madras) released the dataset compilation under CC0-1.0. This waives all compilation copyright, database sui generis rights, and related extraction claims held by the compiler.
2. **Copyright in Underlying Content:**
   - *Risk Finding:* The underlying content consists of crawled web pages, digital newspapers (e.g. Dinamalar, Dinamani, Daily Thanthi), online literary magazines, and Tamil blogs. Original article authors and publishers have **not** released their content under CC0.
   - *Statutory Basis:* Under the Indian Copyright Act, 1957 (amended 2012):
     - Section 14 grants exclusive reproduction rights to authors.
     - Section 52(1)(a) provides fair dealing exceptions for "private or personal use, including research" and "criticism or review".
     - *Ambiguity:* The applicability of Section 52(1)(a) to commercial or downstream production training of generative AI foundation models is untested in Indian courts. Unlike US fair use (17 U.S.C. § 107) or EU Text and Data Mining exceptions (Directive 2019/790, Arts. 3–4), Indian fair dealing is enumerated and historically narrower.
3. **Database Rights:**
   - Sui generis database rights do not exist under Indian law; compilations are protected under copyright as "literary works" (Section 2(o)). AI4Bharat's CC0 dedication successfully waives compilation copyright.
4. **Website Terms of Service (ToS):**
   - Certain source news domains crawled in 2020–2022 contained website terms forbidding automated scraping or commercial derivative harvesting.
5. **Privacy and Personal Data Protection (DPDP Act 2023):**
   - Web crawled articles mention real persons, politicians, journalists, and private individuals. The Digital Personal Data Protection Act, 2023 (India) exempts personal data publicly disclosed by the data principal. However, pretraining pipelines must implement regex and NER PII screening to prevent memorization of phone numbers, email addresses, and Aadhaar identifiers.
6. **Model Training Permissions:**
   - Model training per se extracts statistical subword co-occurrence weights. In major jurisdictions (US, EU, Singapore, Japan), TDM is recognized as non-infringing functional transformation. In India, absent judicial precedent, outside legal counsel advice is required.
7. **Model-Weight Redistribution Considerations:**
   - Weights do not contain verbatim copies of text documents, but generative models may memorize training samples. Implementing deduplication and min-p sampling reduces verbatim extraction risks.

**Disposition:** Designated **`PENDING_LEGAL_REVIEW`**. Controlled acquisition is deferred until Project Owner reviews outside legal risk assessment.

---

## 3. Legal Review: `SRC-TM-02` (Tamil Wikipedia Dump)

- **Source ID:** `SRC-TM-02`
- **Published License:** Creative Commons Attribution-ShareAlike 4.0 International (`CC-BY-SA 4.0`).
- **Underlying Rights:** Crowdsourced text contributed by thousands of Wikipedia editors under CC-BY-SA 4.0.
- **Copyleft / ShareAlike Legal Analysis:**
  - CC-BY-SA 4.0 Section 3(b) mandates that if you produce "Adapted Material", you must license the adapted material under the same license or a compatible license.
  - *Core Legal Question:* Does a neural network trained on CC-BY-SA text constitute "Adapted Material" (derivative work)?
  - If trained model weights are held to be Adapted Material, distributing the model weights under a proprietary or non-ShareAlike open license would violate CC-BY-SA 4.0.
  - *Attribution Obligation:* Section 3(a) requires reasonable attribution, including URI, title, and notice of license. In pretraining, providing full author attribution in the model weights is technologically impossible unless published in model documentation.
- **Disposition:** Designated **`PENDING_LEGAL_REVIEW`**.

---

## 4. Legal Review: `SRC-TM-03` (OSCAR 23.01 Tamil)

- **Source ID:** `SRC-TM-03`
- **Published License:** Open Data Commons Attribution License (`ODC-By 1.0`).
- **Underlying Rights:** Common Crawl web crawl. Subject to website terms of service, robots.txt exclusions, and right to erasure requests.
- **Risks:** Right to be forgotten (GDPR / DPDP) mandates that if a data subject demands removal, unretrainable model weights cannot easily purge individual documents.
- **Disposition:** Designated **`PENDING_LEGAL_REVIEW`**.
