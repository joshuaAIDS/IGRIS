# PHASE 27 — TAMIL SOURCE LEGAL & RIGHTS AUDIT
## Forensic Rights Analysis, Provenance Verification, and Risk Architecture for Tamil Corpora

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Phase:** Phase 27  
**Language Scope:** TAMIL (`ta` / U+0B80–U+0BFF)  
**Status:** COMPLETED & CATEGORIZED (Zero Production Ingress Authorized)

---

## 1. Executive Summary

Tamil is a primary core language of IGRIS. In accordance with Phase 27 requirements, three candidate Tamil datasets were subjected to a 20-point forensic audit spanning repository provenance, compilation copyright, underlying article ownership, statutory fair dealing (Indian Copyright Act, 1957), terms of service compliance, and personal data protection (DPDP Act 2023).

### Candidate Status Summary:
- **`SRC-TM-01` (IndicCorp v2 Tamil):** `PENDING_LEGAL_REVIEW` (CC0 compilation vs. unreleased underlying news publisher copyright; Section 52(1)(a) Indian Copyright Act ambiguity).
- **`SRC-TM-02` (Tamil Wikipedia Dump):** `PENDING_LEGAL_REVIEW` (CC-BY-SA 4.0 copyleft ShareAlike risk to foundation model weights).
- **`SRC-TM-03` (OSCAR 23.01 Tamil):** `PENDING_LEGAL_REVIEW` (ODC-By 1.0 database license does not cover third-party web content; website ToS and GDPR/DPDP right-to-erasure exposure).

> [!CRITICAL]
> **Zero Tamil sources are authorized for acquisition or pretraining.** All three sources carry material legal risks that require formal review by qualified IP legal counsel prior to owner authorization.

---

## 2. In-Depth Audit: `SRC-TM-01` (IndicCorp v2 Tamil)

### A. Provenance and Repository Identity
- **Dataset Name:** IndicCorp v2 (Tamil Monolingual Corpus)
- **Official Publisher:** AI4Bharat, Department of Computer Science & Engineering, IIT Madras, Chennai, India.
- **Upstream Repository:** `https://github.com/AI4Bharat/IndicCorp` / `https://huggingface.co/datasets/ai4bharat/IndicCorp`
- **Pinned Commit SHA:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Target File Path:** `data/ta.txt` (or compressed archive `ta.txt.gz`)
- **Corpus Scale:** ~14,035,000 lines / ~386,000,000 words (~3.8 GB raw text; ~1.06 billion projected Candidate A tokens).
- **Primary Research Paper:** Kakwani et al., *"IndicNLPSuite: Monolingual Corpora, Evaluation Benchmarks and Pre-trained Multilingual Language Models for Indian Languages"*, Findings of EMNLP 2020.

### B. Seven-Layer Rights Architecture
1. **Compilation License (CC0-1.0):**
   - AI4Bharat dedicated the dataset compilation to the public domain under Creative Commons CC0 1.0 Universal (`AI4BHARAT_INDICCORP_LICENSE_STATEMENT.txt`).
   - This waives compilation copyright, database rights, and extraction claims held by IIT Madras.
2. **Underlying Article Ownership:**
   - The corpus was constructed by web-scraping Tamil digital newspapers, online journals, and portals (e.g., Dinamalar, Dinamani, Daily Thanthi, Oneindia Tamil, Vikatan).
   - **Critical Legal Reality:** Original article authors, journalists, and news publishers hold valid, unexpired copyright in their respective literary works under Section 13(1)(a) of the Indian Copyright Act, 1957.
   - AI4Bharat's CC0 dedication applies *only to the compilation*, not to the underlying third-party articles. AI4Bharat had no legal authority to license third-party copyrighted news articles to the public domain.
3. **Indian Statutory Fair Dealing Analysis (Section 52):**
   - Under Indian copyright law, copyright exceptions are governed by Section 52 of the Copyright Act, 1957.
   - Section 52(1)(a) permits "fair dealing with any work... for the purpose of private or personal use, including research" and "criticism or review".
   - **The Jurisprudential Gap:** Indian fair dealing is an **enumerated statutory list**, unlike the open-ended "fair use" doctrine of the United States (17 U.S.C. § 107) or explicit text and data mining (TDM) statutory exemptions enacted in the EU (Directive 2019/790 Arts. 3–4), Japan (Copyright Act Art. 30-4), and Singapore (Copyright Act 2021).
   - Indian courts have not yet ruled on whether commercial pretraining of generative foundation models qualifies as "research" under Section 52(1)(a). A commercial foundation model deployed outside an academic institution faces substantial legal ambiguity.
4. **Website Terms of Service (ToS):**
   - Major Tamil news portals maintain terms of service explicitly forbidding automated extraction, robotic scraping, and commercial harvesting of content.
5. **Personal Data & DPDP Act 2023:**
   - Web news contains references to living persons (politicians, crime victims, private citizens). While Section 3(c)(ii) of the Digital Personal Data Protection Act, 2023 exempts personal data made publicly available by the data principal, news reports often contain personal data published by *third parties*, requiring robust PII filtering.
6. **Model Weight Derivative Liability:**
   - Pretraining extracts statistical subword co-occurrences. While weights are generally non-infringing functional transformations in US law (*Authors Guild v. Google*), Indian copyright jurisprudence has not settled weight copyrightability or derivative liability.
7. **Redistribution Restrictions:**
   - Distributing the raw corpus (`data/ta.txt`) poses direct copyright infringement risk for underlying articles. Distributing trained model weights poses significantly lower risk, provided verbatim memorization is suppressed via deduplication.

### C. Legal Counsel Action Required
- Retain qualified Indian IP counsel to deliver a formal legal opinion on:
  1. The applicability of Section 52(1)(a) fair dealing to commercial foundation model pretraining in India.
  2. Potential liability arising from news publisher scraping terms.
  3. Pre-filtering requirements to ensure immunity under the DPDP Act 2023.

---

## 3. In-Depth Audit: `SRC-TM-02` (Tamil Wikipedia Dump)

### A. Provenance and Repository Identity
- **Dataset Name:** Tamil Wikipedia Article Dump
- **Official Publisher:** Wikimedia Foundation, San Francisco, CA.
- **Upstream Repository:** `https://dumps.wikimedia.org/tawiki/`
- **Target Dump:** `tawiki-latest-pages-articles.xml.bz2` (or snapshot 2024-Q3)
- **Declared License:** Creative Commons Attribution-ShareAlike 4.0 International (`CC-BY-SA 4.0`).
- **Copyright Ownership:** Held individually by thousands of volunteer Wikipedia editors who contributed text under CC-BY-SA 4.0.

### B. The ShareAlike (Copyleft) Dilemma for Foundation Models
1. **Section 3(b) ShareAlike Obligation:**
   - CC-BY-SA 4.0 stipulates: *"If You Share Adapted Material You Produce, the following conditions also apply: The Adapter's License You apply must be a Creative Commons license with the same License Elements... or a Compatible License."*
2. **The Core Legal Question:**
   - Does training a neural network on CC-BY-SA 4.0 text produce "Adapted Material" (a derivative work) of that text?
   - **Risk Scenario:** If a court or rights holder establishes that trained foundation model weights constitute Adapted Material, the owner would be legally compelled to release the entire model (including proprietary architecture and weights) under CC-BY-SA 4.0.
   - **Counter-Argument:** Neural pretraining extracts statistical language representations rather than expressive copyrightable elements; weights do not contain expressive text fragments (*fair use / functional transformation*).
   - **Current Legal Status:** Completely unresolved internationally. No court has definitively adjudicated whether model weights inherit CC-BY-SA copyleft obligations.
3. **Attribution Feasibility (Section 3(a)):**
   - CC-BY-SA mandates that downstream distributors provide reasonable attribution (author credit, license notice, URI). In foundation model pretraining across millions of articles, encoding individual editor credits inside the neural network is technologically impossible. Attribution can only be provided in external model documentation.
4. **Living Persons Biographies (BLP):**
   - Tamil Wikipedia contains extensive biographical entries regarding living politicians, writers, and artists. Strict biographical filtering is required to eliminate defamatory or outdated claims.

---

## 4. In-Depth Audit: `SRC-TM-03` (OSCAR 23.01 Tamil)

### A. Provenance and Repository Identity
- **Dataset Name:** OSCAR 23.01 Tamil Subset (Open Supervised Carmina Arxiv)
- **Official Publisher:** Inria / OSCAR Project (Ortiz Suárez, Romary, Sagot).
- **Upstream Repository:** `https://oscar-project.org/` / Hugging Face `oscar-corpus/OSCAR-2301`
- **Target File:** `ta_meta.jsonl.zst`
- **Declared License:** Open Data Commons Attribution License (`ODC-By 1.0`).
- **Underlying Provenance:** Common Crawl web crawl.

### B. Legal and Privacy Analysis
1. **Database Right vs. Content Copyright:**
   - ODC-By 1.0 licenses only the *database compilation rights* (sui generis database rights in the EU).
   - ODC-By 1.0 explicitly **does not license the underlying text**. Each website owner retains copyright in their scraped pages.
2. **Robots.txt and Scraping Exclusions:**
   - Common Crawl respects `robots.txt` at crawl time, but websites frequently update exclusion policies post-crawl.
3. **GDPR / DPDP Right to Erasure Exposure:**
   - Data subjects frequently submit right-to-erasure requests to Common Crawl and OSCAR.
   - Once text is integrated into foundation model pretraining, surgically "unlearning" a specific individual's personal data from neural weights is scientifically unresolved without complete retraining.

---

## 5. Summary Classification Matrix for Tamil Corpora

| Candidate | Primary License | Underlying Content Rights | Statutory Defense | Privacy Risk | Evidence Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`SRC-TM-01`** (IndicCorp v2) | CC0-1.0 | Third-party news publishers | Section 52(1)(a) Indian Copyright Act (Unsettled) | Medium (DPDP Act) | **`PENDING_LEGAL_REVIEW`** |
| **`SRC-TM-02`** (Tamil Wikipedia) | CC-BY-SA 4.0 | Crowdsourced editors | CC-BY-SA License (Copyleft risk to weights) | Low (BLP screening) | **`PENDING_LEGAL_REVIEW`** |
| **`SRC-TM-03`** (OSCAR 23.01) | ODC-By 1.0 | Unreleased web domains | EU TDM / US Fair Use (Jurisdiction-dependent) | High (Right to Erasure) | **`PENDING_LEGAL_REVIEW`** |
