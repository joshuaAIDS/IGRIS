# PHASE 27 — TANGLISH SOURCE LEGAL & RIGHTS AUDIT
## Review of Tamil-English Code-Mixed Datasets, Platform Terms, and Research-Only Restrictions

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Phase:** Phase 27  
**Language Scope:** TANGLISH (`ta-Latn` / Tamil-English Code-Mixed)  
**Status:** AUDITED & CATEGORIZED (Zero Production Ingress Authorized)

---

## 1. Executive Summary

Tanglish (Tamil expressed in Roman script, conversational Tamil-English code-switching, and Tamil-inflected English) represents a core language category for IGRIS. In accordance with Phase 27 requirements, three candidate Tanglish sources were audited across creator copyright, platform terms of service, research-only restrictions, privacy/PII, and commercial model pretraining viability.

### Candidate Status Summary:
- **`SRC-TG-01` (DravidianCodeMix YouTube comments):** `PENDING_LEGAL_REVIEW` (CC-BY-4.0 compilation vs. YouTube Terms of Service scraping prohibitions; user commenter rights).
- **`SRC-TG-02` (IndicGLUE Tanglish Sentiment):** `PENDING_LEGAL_REVIEW` (CC-BY-4.0 compilation; social media crawl provenance; benchmark test split quarantine required).
- **`SRC-TG-03` (Spoken Tanglish Transcripts):** **`REJECTED`** (Non-commercial academic license strictly incompatible with commercial foundation model pretraining).

> [!CRITICAL]
> **Zero Tanglish sources are authorized for acquisition.** Production ingress remains locked. Synthetic Tanglish generators validated in Phase 25 and Phase 26 continue to serve as the exclusive validated Tanglish resource.

---

## 2. In-Depth Audit: `SRC-TG-01` (DravidianCodeMix Tamil-English)

### A. Provenance and Repository Identity
- **Dataset Name:** DravidianCodeMix (Tamil-English Sentiment Analysis)
- **Curators / Authors:** Chakravarthi et al., *A Sentiment Analysis Dataset for Code-Mixed Dravidian Languages*, ACL 2020 DravidianLangTech Workshop.
- **Repository:** `https://github.com/kmi-linguistics/dravidian-codemix` / Hugging Face.
- **Pinned Release:** v1.0 (`tamil_english_train.tsv`).
- **Declared Compilation License:** Creative Commons Attribution 4.0 International (`CC-BY-4.0`).
- **Data Provenance:** Public user comments scraped from YouTube under Tamil cinema trailers and music videos.

### B. The Platform Terms vs. Academic License Conflict
1. **The CC-BY-4.0 Compilation Mirage:**
   - Academic researchers frequently apply CC-BY licenses to scraped datasets.
   - However, under fundamental copyright and contract law, researchers **cannot grant a license over third-party creative expression they do not own**.
   - Individual YouTube users retain copyright in their original creative comments under YouTube Terms of Service § 6.B.
2. **YouTube Terms of Service Prohibitions (§ II.A & § II.B):**
   - Section II.A explicitly prohibits: *"accessing the Service using any automated means (such as robots, botnets or scrapers)"* without prior written consent from Google/YouTube.
   - Section II.B explicitly prohibits: *"collecting or harvesting any information that might identify a person (for example, usernames)"* unless permitted by that person.
   - **Contractual Breach Exposure:** Ingesting data scraped in violation of YouTube Terms of Service creates legal and reputational exposure, particularly for a commercial project.
3. **Google YouTube Developer Policy:**
   - Even when data is obtained via the official YouTube Data API, Developer Policy § 5 mandates that developers must delete cached/stored content upon request and cannot redistribute raw comment data outside approved applications.
4. **PII and Defamation in User Comments:**
   - YouTube comments contain usernames (`@user`), colloquial profanity, and potentially defamatory statements regarding cinema figures.
   - Strict automated regex handle stripping and toxicity filtering are mandatory prerequisites if legal review ever resolves the platform terms issue.

---

## 3. In-Depth Audit: `SRC-TG-02` (IndicGLUE Tanglish Sentiment)

### A. Provenance and Repository Identity
- **Dataset Name:** IndicGLUE Tanglish Sentiment Analysis Benchmark
- **Publisher:** AI4Bharat, IIT Madras (Kakwani et al., EMNLP 2020 Findings).
- **Repository:** `https://github.com/AI4Bharat/IndicGLUE` / `ai4bharat/IndicGLUE`
- **Pinned Version:** v1.0 (`tanglish_sentiment/train.csv`).
- **Declared License:** Creative Commons Attribution 4.0 International (`CC-BY-4.0`).
- **Content:** Romanized Tamil social media posts annotated for positive, negative, and neutral sentiment.

### B. Legal and Technical Analysis
1. **Benchmark Contamination Invariant:**
   - IndicGLUE is a widely used benchmark for evaluating Indian language language models.
   - If `test.csv` or `dev.csv` is ingested into pretraining, downstream evaluation scores on IndicGLUE will be artificially inflated, invalidating all reported scientific metrics.
   - **Mandatory Control:** Strict quarantine of `dev.csv` and `test.csv`. Only `train.csv` could ever be considered.
2. **Social Media Provenance:**
   - Posts originate from public social media crawls; subject to the same third-party copyright and platform terms considerations as `SRC-TG-01`.
3. **Status:** **`PENDING_LEGAL_REVIEW`**.

---

## 4. Rejection of `SRC-TG-03` (Spoken Tanglish Transcripts)

### A. Provenance and License Restriction
- **Dataset Name:** Spoken Tanglish Transcripts / Academic Code-Mixed Speech Corpora
- **Publisher:** Academic Research Consortia / University Linguistic Labs.
- **Declared License:** **Non-Commercial Academic User Agreement / CC-BY-NC-ND 4.0**.

### B. Mandatory Rejection Rationale
1. **Commercial Model Disqualification:**
   - Non-Commercial (`NC`) clauses legally bar any commercial use, commercial service, commercial deployment, or commercial downstream monetization of the model.
   - Pretraining on NC data permanently infects the resulting neural network weights with non-commercial restrictions, rendering the model legally unviable for commercial distribution.
2. **No Derivatives (`ND`) Clause:**
   - The ND clause prohibits the creation of derivative works. Model training may legally be argued to constitute a derivative adaptation of the underlying text.
3. **Irrevocable Rejection:**
   - **`SRC-TG-03` is formally REJECTED.** It is permanently excluded from the IGRIS dataset catalog.

---

## 5. Tanglish Candidate Summary Matrix

| Source ID | Source Name | Declared License | Platform Terms Risk | Commercial Pretraining Viability | Final Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`SRC-TG-01`** | DravidianCodeMix | CC-BY-4.0 | HIGH (YouTube ToS § II.A) | Unsettled (Scraping breach) | **`PENDING_LEGAL_REVIEW`** |
| **`SRC-TG-02`** | IndicGLUE Tanglish | CC-BY-4.0 | MEDIUM (Social media crawl) | Conditional (Train split only) | **`PENDING_LEGAL_REVIEW`** |
| **`SRC-TG-03`** | Spoken Tanglish | CC-BY-NC-ND | CRITICAL (NC/ND restrictions) | PROHIBITED | **`REJECTED`** |
