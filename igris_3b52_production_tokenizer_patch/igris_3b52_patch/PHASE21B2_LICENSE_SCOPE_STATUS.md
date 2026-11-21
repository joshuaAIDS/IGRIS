# PHASE 21B2 — LICENSE SCOPE & RIGHTS STATUS
## Delineation of Publisher CC0 Waiver, Third-Party Copyrights, and Commercial Deployment Risks

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B2  
**Scope:** Legal & Licensing Governance Review  

---

## 1. Delineation of Legal Layers

To ensure absolute legal clarity and prevent premature commercial assumptions, the IGRIS project establishes a strict separation across the four distinct legal layers governing IndicCorp v2:

```
+---------------------------------------------------------------------------------------------------+
|                                  FOUR DISTINCT LEGAL LAYERS                                       |
+-----------------------------------+-----------------------------------+---------------------------+
| 1. AI4Bharat CC0 Declaration       | 2. Underlying Third-Party Text    | 3. Compilation Rights     |
| - Irrevocable waiver of rights    | - Scraped news articles, blogs    | - Database sui generis    |
|   held by compiler (IIT Madras)   | - Retained by original authors    |   rights dedicated to     |
| - Zero royalties or claims        | - CC0 explicitly disclaims 4(c)   |   public domain (CC0)     |
+-----------------------------------+-----------------------------------+---------------------------+
| 4. Commercial Model Deployment Risk                                                               |
| - Governed by computational non-expressive use / Text & Data Mining (TDM) exceptions              |
| - Requires formal jurisdiction-specific review by qualified intellectual property counsel         |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Core Legal Boundaries

### 2.1. Scope of AI4Bharat's CC0-1.0 Declaration
- **What Is Covered:** AI4Bharat (IIT Madras), as creator and compiler of IndicCorp v2, has dedicated its compilation copyright, database selection/arrangement rights, and extraction rights under Creative Commons CC0 1.0 Universal.
- **Grant:** Downstream users may reproduce, adapt, tokenize, and train models without payment, permissions, or royalty obligations owed to AI4Bharat.

### 2.2. Exclusion of Underlying Third-Party Rights (Section 4(c))
- **Express Disclaimer:** Creative Commons CC0 Section 4(c) unequivocally states:
  > *"Affirmer disclaims responsibility for clearing rights of other persons that may apply to the Work or any use thereof, including without limitation any person's Copyright and Related Rights in the Work."*
- **Fact:** The underlying news articles, editorials, and web content crawled from regional Indian portals (e.g., Dina Thanthi, Dinamalar, Eenadu, Mathrubhumi, Amar Ujala) were authored by third-party journalists and publishers who did **not** execute CC0 waivers.
- **Invariant:** CC0 does **NOT** eliminate third-party copyright in underlying texts.

---

## 3. Commercial Pretraining & Deployment Doctrine

The legal justification for pretraining transformer models on publicly accessible web crawl data does not rest on third-party copyright abandonment, but rather on **non-expressive computational utilization**:
1. **Non-Expressive Use:** Ingesting text to compute token co-occurrence probabilities and optimize multi-layer attention connection weights does not republish or substitute for the expressive literary value of original articles.
2. **Jurisdictional Variances:**
   - **India (Copyright Act, 1957 §52(1)(a)):** Fair dealing covers personal use and research. Commercial exploitation boundaries remain actively developing in Indian jurisprudence.
   - **United States (17 U.S.C. § 107):** Governed by the fair use doctrine (transformative purpose vs market harm). Anti-memorization safeguards are strictly required.
   - **European Union (Directive (EU) 2019/790 Arts 3 & 4):** Text and data mining exceptions permit commercial TDM unless rights holders have expressly opted out (e.g. machine-readable `robots.txt`).
3. **Mandatory Legal Restriction:** The project makes **no blanket conclusions** regarding fair dealing or fair use. Qualified intellectual property legal counsel review remains an outstanding, non-waivable requirement prior to commercial deployment.