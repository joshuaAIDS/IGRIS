# PHASE 23 — TANGLISH SOURCE LEGAL & TECHNICAL READINESS AUDIT
## Review of Tamil-English Code-Mixed Datasets, Social Media Provenance, and Rights Architecture

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 23  
**Language Scope:** TANGLISH (`ta-Latn` / Tamil-English Code-Mixed)  
**Status:** AUDITED & CATEGORIZED  

---

## 1. Executive Summary

Tanglish (Tamil expressed in Roman script, English words in Tamil syntax, and conversational code-switching) is an essential approved language category for real-world digital Tamil communication.

Three candidate Tanglish datasets were audited:
1. `SRC-TG-01`: DravidianCodeMix (Tamil-English)
2. `SRC-TG-02`: IndicGLUE Tanglish Sentiment Benchmark
3. `SRC-TG-03`: Social Dravidian Sentiment Tanglish

**Summary Finding:**
- `SRC-TG-01` and `SRC-TG-02` contain authentic Tanglish text published under CC-BY-4.0. However, because their underlying data originates from scraped social media (YouTube comments and public posts), platform Terms of Service (YouTube ToS § II.A) and PII/privacy risks require outside legal review prior to authorization. Both are categorized as **`PENDING_LEGAL_REVIEW`**.
- `SRC-TG-03` is published under a Research-Only / Non-Commercial license and is formally **`REJECTED`**.

---

## 2. In-Depth Legal Review: `SRC-TG-01` (DravidianCodeMix Tamil-English)

```
+------------------------------------+----------------------------------------------------------+
| Review Parameter                   | Verified Source Metadata & Audit Findings                |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-TG-01                                                |
| Dataset Name                       | DravidianCodeMix (Tamil-English Sentiment)               |
| Upstream Repository                | kmi-linguistics/dravidian-codemix (GitHub / Hugging Face)|
| Publication / Origin               | ACL 2020 DravidianLangTech Workshop (Chakravarthi et al.)|
| Pinned Release                     | v1.0                                                     |
| Exact File Paths                   | tamil_english_train.tsv (also dev/test)                  |
| Declared Compilation License       | Creative Commons Attribution 4.0 International (CC-BY-4.0)|
| Language Representation            | Romanized Tamil (`ta-Latn`), Tamil script, English mix   |
+------------------------------------+----------------------------------------------------------+
```

### Technical Tanglish Verification:
- **Corpus Inspection:** Sample review confirms authentic digital Tanglish:
  - *"Thalaivar entry verithanam bro, waiting for FDFS!"* (Tamil slang + English loan words).
  - *"Nalla padam, acting super but BGM average"* (Tamil sentence structure + English adjectives).
  - Mixed script sentences containing both Tamil Unicode characters and Latin letters.
- **Linguistic Authenticity:** Verified as genuine digital conversational code-switching, not synthetic or machine-translated text.

### Seven-Layer Legal & Rights Analysis:
1. **Compilation License (CC-BY-4.0):** The dataset curators dedicated the compilation under CC-BY-4.0. Commercial training is permitted provided attribution is given.
2. **Underlying Content Rights:** The comments were authored by individual YouTube users who hold individual copyright in their original creative comments.
3. **YouTube Terms of Service Compliance:**
   - YouTube Terms of Service (Section II.A and Developer Policies) prohibit automated scraping of YouTube comments outside the official Google YouTube Data API.
   - Scraping text directly or redistributing raw comments without adhering to YouTube data deletion webhooks poses a contractual risk.
4. **Privacy & PII Exposure:**
   - Social media comments occasionally mention user handles, real names, or defamatory language. Strict automated PII screening and profanity/toxicity filtering are required.
5. **Model Training & Weight Redistribution:**
   - Extracting subword patterns from short comments (average 15 words) has minimal risk of verbatim memorization. However, legal clearance on third-party scraping terms is mandatory.

**Disposition:** Designated **`PENDING_LEGAL_REVIEW`**.

---

## 3. In-Depth Legal Review: `SRC-TG-02` (IndicGLUE Tanglish Sentiment)

- **Source ID:** `SRC-TG-02`
- **Dataset Name:** IndicGLUE Tanglish Sentiment Analysis
- **Upstream Repository:** `ai4bharat/IndicGLUE`
- **Declared License:** Creative Commons Attribution 4.0 International (`CC-BY-4.0`).
- **Linguistic Characteristics:** Short Romanized Tamil sentences with English vocabulary.
- **Key Legal and Governance Risks:**
  - *Benchmark Contamination:* Because IndicGLUE is a standard evaluation benchmark, ingesting the test split into pretraining would contaminate downstream model evaluation. If authorized, **only the training split** (`train.csv`) may be ingested; the evaluation splits (`dev.csv`, `test.csv`) must be quarantined.
  - *Provenance:* Scraped social media posts; subject to similar terms of service considerations as `SRC-TG-01`.
- **Disposition:** Designated **`PENDING_LEGAL_REVIEW`**.

---

## 4. Rejection of `SRC-TG-03` (Social Dravidian Sentiment Tanglish)

- **Source ID:** `SRC-TG-03`
- **Declared License:** Research-Only / Non-Commercial (`CC-BY-NC-ND` or proprietary university research agreement).
- **Rejection Rationale:** The Non-Commercial clause legally bars any commercial, unrestricted, or production deployment of models trained on this dataset.
- **Disposition:** **`REJECTED`**.
