# PHASE 21B1 — LICENSE SCOPE COMPARISON & LEGAL RECONCILIATION
## Comparative Analysis: IndicCorp v2 CC0-1.0 vs Legacy IndicCorp CC BY-NC-SA 4.0

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B1  
**Scope:** Legal & Licensing Scope Reconciliation  

---

## 1. Executive Summary

This document reconciles the critical licensing discrepancy between the **legacy IndicCorp (v1)** license deed and the **IndicCorp v2** license deed. It explicitly delineates what rights the publisher's CC0 declaration grants, what rights it *cannot* grant, and the precise commercial-use implications for IGRIS.

---

## 2. Comparative Matrix: Legacy IndicCorp vs IndicCorp v2

```
+-----------------------------------+-----------------------------------+-----------------------------------+
| Licensing Provision               | Legacy IndicCorp (v1, 2020)       | IndicCorp v2 (2022–2023) [IGRIS]  |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Stated License Deed               | CC BY-NC-SA 4.0 / CC BY-NC 4.0    | CC0 1.0 Universal                 |
| Commercial Use Allowed?           | NO (Strictly Non-Commercial)      | YES (Publisher waives rights)     |
| Derivative Works Allowed?         | Permitted under Share-Alike terms | YES (Unrestricted modification)   |
| Viral Copyleft Obligation?        | YES (Share-Alike encumbrance)     | NONE (No downstream copyleft)     |
| Mandatory Attribution?            | YES (Legal contractual breach     | NO (Academic citation customary,  |
|                                   | if omitted)                       | but de jure waiver under CC0)     |
| Impact on IGRIS Commercial Model  | FATAL BLOCKER (Cannot commercial- | ELIGIBLE FOR OWNER REVIEW         |
|                                   | ize or proprietary license weights)| (Subject to third-party rights)   |
+-----------------------------------+-----------------------------------+-----------------------------------+
```

---

## 3. Detailed Scope of the Publisher's CC0 Declaration

AI4Bharat (IIT Madras) released IndicCorp v2 on Hugging Face under the **Creative Commons CC0 1.0 Universal Public Domain Dedication**.

### 3.1. What CC0 Successfully Relinquishes
Under CC0 Section 2 (Waiver) and Section 3 (Public License Fallback), AI4Bharat irrevocably waives or licenses:
1. **Compilation Copyright:** AI4Bharat's original selection, arrangement, coordination, and indexing of text documents across the 24 languages.
2. **Database Sui Generis Rights:** All database rights arising under Directive 96/9/EC or equivalent national database legislation.
3. **Extraction & Re-utilization Rights:** Unrestricted permission to parse, tokenize, filter, convert, and ingest the corpus into binary training matrices.
4. **No Publisher Royalties or Fees:** AI4Bharat will not demand licensing fees or royalties for commercial exploitation of the resulting models.

---

## 4. Critical Legal Boundary: Third-Party Underlying Text Rights

> [!WARNING]
> A publisher's CC0 declaration covers **only the rights held by the affirmer**. It does NOT and CANNOT extinguish third-party copyrights in the underlying web texts crawled to create the dataset. AI4Bharat explicitly states that they do not claim ownership over raw underlying text content scraped from third-party sources.

### 4.1. The Express Disclaimer in CC0 Section 4(c)
Creative Commons CC0 1.0 explicitly disclaims warranty of third-party rights clearance:
> *"Affirmer disclaims responsibility for clearing rights of other persons that may apply to the Work or any use thereof, including without limitation any person's Copyright and Related Rights in the Work. Further, Affirmer disclaims responsibility for obtaining any necessary consents, permissions or other rights required for any use of the Work."* (CC0 Section 4.c)

### 4.2. Third-Party Provenance of IndicCorp v2 Text
The underlying content of IndicCorp v2 consists of text scraped from:
- Commercial Indian regional newspapers (e.g., Dainik Jagran, Dina Thanthi, Eenadu, Mathrubhumi, Anandabazar Patrika).
- Independent web blogs, cultural portals, and forums.
- Indian governmental and public sector portals.
- Indic Wikipedia projects (which are CC BY-SA 3.0 / 4.0).

**Key Legal Finding:** The individual articles crawled from commercial news portals remain the intellectual property of their original copyright owners. The authors of those articles did not dedicate their works under CC0.

---

## 5. Commercial-Use Implications for IGRIS

Because CC0 does not extinguish underlying third-party rights, the legality of using IndicCorp v2 in a commercial transformer model does **not** rely solely on CC0. It relies on the legal doctrine of **non-expressive computational use** (Text and Data Mining).

### 5.1. Non-Expressive Use & Machine Learning Pretraining
In neural network pretraining:
- Text is ingested as numeric token sequences to adjust floating-point connection weights ($W_q, W_k, W_v, W_{ffn}$).
- The model learns abstract statistical associations, syntactic grammar, and semantic representations.
- The expressive layout, prose styling, and communicative market value of the original articles are not republished, distributed, or substituted.

### 5.2. Jurisdiction-Specific Legal Landscape & Need for Qualified Legal Review

> [!IMPORTANT]
> The legal treatment of web crawling for AI pretraining varies significantly by jurisdiction and remains actively evolving in global courts. The IGRIS project maintains strict adherence to qualified legal review and makes NO blanket conclusions regarding fair dealing or fair use.

1. **Republic of India (Indian Copyright Act, 1957):**
   - Section 52(1)(a) provides fair dealing for research, private study, and critique.
   - Whether commercial AI model training falls squarely within Section 52 or constitutes commercial infringement has not yet been authoritatively settled by the Supreme Court of India.
   - **Requirement:** Commercial deployment in India requires formal evaluation by qualified Indian intellectual property counsel.
2. **United States (17 U.S.C. § 107 — Fair Use):**
   - Precedents such as *Authors Guild v. Google, Inc.* (Google Books) establish that intermediate reproduction of copyrighted texts for non-expressive, transformative indexing is fair use.
   - Ongoing litigations (e.g., *New York Times v. OpenAI*, *Getty Images v. Stability AI*) are currently testing the boundaries of fair use regarding model memorization and competitive market substitution.
   - **Requirement:** US commercial deployment requires qualified US copyright counsel review and implementation of anti-memorization safeguards.
3. **European Union (Directive (EU) 2019/790 — DSM Directive):**
   - Article 3 permits TDM for non-commercial scientific research.
   - Article 4 permits commercial TDM only where copyright owners have not expressly reserved their rights (e.g., via machine-readable `robots.txt` opt-outs).
   - IndicCorp v2 crawl methodology respected `robots.txt` at the time of scraping, but retroactive publisher opt-outs remain an ongoing compliance consideration.
   - **Requirement:** EU commercialization requires compliance verification under Article 53 of the EU AI Act (Regulation (EU) 2024/1689).

---

## 6. Recommendations & Actionable Safeguards

1. **Strictly Reject IndicCorp v1 Artifacts:** Never download or ingest any files from the legacy 2020 release. Enforce upstream URL verification targeting `ai4bharat/IndicCorpV2`.
2. **Implement Anti-Memorization Architecture:**
   - Apply MinHash deduplication to remove high-frequency duplicate passages that are prone to memorization.
   - Restrict inference decoding prompts to prevent verbatim recitation of copyrighted news articles.
3. **Formal Legal Review Before Commercial Monetization:**
   - Mark all third-party copyright questions for qualified IP counsel review prior to releasing commercial weights or charging end-users for inference services.
4. **Scholarly Attribution:**
   - While de jure voluntary under CC0, cite Doddapaneni et al. (ACL 2023) in all public technical releases.