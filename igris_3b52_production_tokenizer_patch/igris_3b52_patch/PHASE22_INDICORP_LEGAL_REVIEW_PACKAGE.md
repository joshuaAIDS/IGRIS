# PHASE 22 — INDICCORP V2 LEGAL REVIEW PACKAGE
## Comprehensive Source-by-Source Legal, Licensing, Provenance, and Rights Analysis for Qualified Counsel

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22  
**Target Dataset:** IndicCorp v2 (Seven Indic Language Subsets)  
**Authoritative Upstream:** `ai4bharat/IndicCorpV2`  
**Pinned Revision:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`  
**Legal Clearance Status:** **NOT CLEARED — PENDING QUALIFIED COUNSEL REVIEW**  

---

> [!CAUTION]
> **Legal Notice & Disclaimer:**  
> This document is a technical and factual briefing compiled solely to facilitate formal legal review by qualified intellectual property counsel. It does **not** constitute legal advice, legal clearance, or a determination of copyright non-infringement. Under IGRIS governance, an upstream curator's public domain dedication (CC0) does **not** automatically extinguish third-party copyright claims over underlying web-scraped content.

---

## 1. Upstream Dataset Identification & Publication Context

- **Academic Authors & Curators:** Sumanth Doddapaneni, Rahul Aralikatte, et al. (AI4Bharat, Indian Institute of Technology Madras).
- **Publication Reference:** Doddapaneni et al., *"Towards Leaving No Indic Language Behind: Building Monolingual Corpora, Benchmark and Models for Indian Languages"*, Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL 2023), pages 12402–12426.
- **Upstream Repository:** `https://huggingface.co/datasets/ai4bharat/IndicCorpV2`
- **Curator License Statement:** The repository and published dataset card state that IndicCorp v2 is released under the **Creative Commons CC0 1.0 Universal Public Domain Dedication (CC0-1.0)**.
- **Curator Waiver Scope:** AI4Bharat waives all copyright and related rights in their compilation, deduplication, filtering, and dataset packaging to the fullest extent permitted by law.

---

## 2. The Core Legal Issue: Web Crawl Compilation vs. Underlying Copyright

While AI4Bharat's original contributions (compilation selection, extraction scripts, metadata) are dedicated to the public domain under CC0, IndicCorp v2 is fundamentally a **web-crawled and news-scraped corpus**:
1. **Provenance:** Crawled from publicly accessible websites, online newspapers, news portals, magazine articles, government websites, and blogs across Indian language domains between 2020 and 2022.
2. **Third-Party Copyright Retention:** The underlying authors, journalists, news organizations, and media publishers did **not** execute CC0 waivers or assign their copyrights to AI4Bharat.
3. **Downstream Exposure:** Training commercial or redistributable AI foundation models on web-scraped text creates potential exposure under national copyright frameworks unless protected by fair use, fair dealing, or text-and-data-mining (TDM) statutory exceptions.

---

## 3. Language-by-Language Legal Profile Matrix

```
+-----------+-----------+-------------------+-----------------------+-------------------+-------------------------------+-----------------------+
| Source ID | Language  | Upstream Path(s)  | Declared Size (Bytes) | Curator License   | Primary Crawl Domains         | Current Status        |
+-----------+-----------+-------------------+-----------------------+-------------------+-------------------------------+-----------------------+
| SRC-TM-01 | Tamil     | data/ta.txt       | 11,800,000,000        | CC0-1.0 (Curator) | Dinamalar, Dinamani, Web News | PENDING_LEGAL_REVIEW  |
| SRC-HI-01 | Hindi     | data/hi-[1-3].txt | 80,100,000,000 (3 sh) | CC0-1.0 (Curator) | Dainik Bhaskar, Amar Ujala    | PENDING_LEGAL_REVIEW  |
| SRC-OI-01 | Telugu    | data/te.txt       | 15,800,000,000        | CC0-1.0 (Curator) | Eenadu, Sakshi, Andhra Jyothi | PENDING_LEGAL_REVIEW  |
| SRC-OI-02 | Malayalam | data/ml.txt       | 26,300,000,000        | CC0-1.0 (Curator) | Manorama, Mathrubhumi, Portals| PENDING_LEGAL_REVIEW  |
| SRC-OI-03 | Kannada   | data/kn.txt       | 19,600,000,000        | CC0-1.0 (Curator) | Prajavani, Vijaya Karnataka   | PENDING_LEGAL_REVIEW  |
| SRC-OI-04 | Bengali   | data/bn.txt       | 16,000,000,000        | CC0-1.0 (Curator) | Anandabazar, Bartaman, Portals| PENDING_LEGAL_REVIEW  |
| SRC-OI-05 | Gujarati  | data/gu.txt       | 14,100,000,000        | CC0-1.0 (Curator) | Gujarat Samachar, Divya Bhaskar| PENDING_LEGAL_REVIEW |
+-----------+-----------+-------------------+-----------------------+-------------------+-------------------------------+-----------------------+
| TOTAL     | 7 Langs   | 9 Flat Objects    | 183,700,000,000 Bytes | CC0-1.0 (Curator) | Multi-Publisher Web Crawl     | 0 / 7 AUTHORIZED      |
+-----------+-----------+-------------------+-----------------------+-----------------------+-------------------------------+-----------------------+
```

---

## 4. Key Legal Questions for Qualified Counsel

Legal counsel engaged to evaluate IndicCorp v2 for IGRIS must address the following five specific questions:

### Question 1: Scope & Enforceability of the CC0 Waiver
- Does AI4Bharat’s CC0 dedication provide any legal defense or indemnity against infringement actions brought by the third-party owners of the scraped articles?
- *Preliminary Technical Finding:* No. A licensor can only dedicate rights they own. CC0 cannot waive rights held by non-participating third-party copyright holders.

### Question 2: Fair Dealing Under Indian Copyright Law (Copyright Act, 1957)
- Section 52(1)(a)(i) of the Indian Copyright Act protects "fair dealing with any work ... for the purpose of private or personal use, including research."
- Does training a foundation model for non-commercial research vs. potential commercial deployment qualify under Section 52?
- What are the legal precedents in Indian courts regarding commercial AI training on scraped domestic news and literature?

### Question 3: Fair Use Under United States Law (17 U.S.C. § 107)
- Under US copyright doctrine (e.g., *Authors Guild v. Google, Inc.* and pending generative AI jurisprudence):
  1. Is pretraining a multilingual transformer model transformative?
  2. Does pretraining affect the market for the original crawled web articles?
  3. Does memorization/extraction risk (verbatim reproduction of training text) create actionable exposure?

### Question 4: Website Terms of Service & Anti-Scraping Covenants
- Did the underlying crawl violate website Terms of Service (ToS) or bypass robots.txt instructions?
- If AI4Bharat performed the crawl, can a downstream user of the published dataset be held liable for breach of contract or Computer Fraud and Abuse Act (CFAA) violations?

### Question 5: Model Weights Redistribution Liability
- If the IGRIS model weights are trained on IndicCorp v2 and subsequently released (under an open-source license such as Apache-2.0 or commercial license), do the trained neural network weights constitute a "derivative work" of the underlying copyrighted text under applicable copyright statutes?

---

## 5. Technical Risk Mitigations Implemented

To protect the project pending counsel review, IGRIS has implemented the following technical safeguards:
1. **Zero Acquisition:** The dataset has **not** been downloaded or staged.
2. **Access Gate Locked:** Ingress gate enforces default-deny.
3. **Deduplication & PII Pipeline Prepared:** MinHash LSH and heuristic deduplication are planned to eliminate repetitive text blocks and minimize verbatim extraction risk.
4. **Isolated Tokenizer Decision:** Candidate A was selected and validated without training on unapproved text.
