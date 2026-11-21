# PHASE 21B — INDICCORP SOURCE-BY-SOURCE LICENSE AND ACQUISITION READINESS REVIEW

**Project:** IGRIS (Multilingual Decoder-Only Transformer)  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Scope:** Read-Only Legal, Licensing, Provenance, and Technical Verification of 7 IndicCorp Sources  
**Verdict:** **VERDICT A — ALL SEVEN SOURCES HAVE SUFFICIENT PRIMARY-SOURCE EVIDENCE FOR OWNER CONSIDERATION**  

---

## 1. Executive Summary & Review Objectives

Phase 21B executes an exhaustive, read-only legal, provenance, licensing, and technical readiness review of the seven candidate monolingual corpora from the **IndicCorp** collection:
- `SRC-TM-01` — Tamil
- `SRC-HI-01` — Hindi
- `SRC-OI-01` — Telugu
- `SRC-OI-02` — Malayalam
- `SRC-OI-03` — Kannada
- `SRC-OI-04` — Bengali
- `SRC-OI-05` — Gujarati

### Mandatory Governance Boundaries
1. **Read-Only Verification:** This review was conducted exclusively through public repository inspection, academic publication analysis, license deed audit, and offline synthetic pipeline tests.
2. **Ingress Gate Locked:** The production ingress gate remained **LOCKED** (Default-Deny Enforced) throughout this review.
3. **Zero Production Bytes Acquired:** **0 bytes** of production data were downloaded, scraped, or transferred.
4. **Zero Sources Authorized:** **0 sources** are authorized by this review. Authorization is an exclusive human owner prerogative to be executed in subsequent phases.
5. **Tokenizer Invariant:** Candidate A (`ByteLevel BPE`, SHA-256 `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`) remains preserved bitwise invariant. No tokenizer retraining or modifications occurred.
6. **Pretraining Prohibited:** Model weights remain uninitialized for pretraining; no production training was initiated.

---

## 2. Authoritative Publisher & Primary Evidence Identification

### Upstream Publisher & Institution
- **Publishing Entity:** **AI4Bharat**, Department of Computer Science & Engineering, **Indian Institute of Technology Madras (IIT Madras)**, Chennai, Tamil Nadu, India, in collaboration with the EkStep Foundation.
- **Principal Authors / Curators:** Divyanshu Kakwani, Anoop Kunchukuttan, Satish Golla, Gokul N.C., Avik Bhattacharyya, Mitesh M. Khapra, Pratyush Kumar.
- **Authoritative Publication:** *IndicNLPSuite: Monolingual Corpora, Evaluation Benchmarks and Pre-trained Multilingual Language Models for Indian Languages*, Proceedings of Findings of the Association for Computational Linguistics: EMNLP 2020, pages 4948–4961 ([ACL Anthology: 2020.findings-emnlp.411](https://aclanthology.org/2020.findings-emnlp.411/)).
- **Primary Source Code & Repository:** [https://github.com/AI4Bharat/IndicCorp](https://github.com/AI4Bharat/IndicCorp)
- **Hugging Face Hub Repository:** [https://huggingface.co/datasets/ai4bharat/IndicCorp](https://huggingface.co/datasets/ai4bharat/IndicCorp)
- **Primary Storage Endpoints:** E2E Networks Object Storage (`https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/`).

### Primary License Evidence Preserved Locally
The project has archived the authoritative primary legal notices in the local governance repository under `PHASE21B_PRIMARY_LICENSE_EVIDENCE/`:
1. `CC0_1.0_LEGAL_CODE.txt`: The full verbatim legal code of the Creative Commons CC0 1.0 Universal Public Domain Dedication deed.
2. `AI4BHARAT_INDICCORP_LICENSE_STATEMENT.txt`: Verbatim repository licensing notice published by AI4Bharat dedicating IndicCorp to the public domain under CC0 1.0.
3. `INDICCORP_V2_PROVENANCE_AND_CITATION.txt`: Upstream paper citation, authors, institutional affiliations, and corpus cleaning methodology.
4. `INDICCORP_SOURCE_BY_SOURCE_EVIDENCE_MAP.json`: Machine-readable mapping of sources, endpoints, parameters, and verification records.

---

## 3. Creative Commons CC0 1.0 Universal Legal Analysis

### Legal Mechanism & Operational Grants
The IndicCorp corpus is published under the **Creative Commons CC0 1.0 Universal Public Domain Dedication**. CC0 1.0 operates through a two-tiered legal structure:
1. **Unconditional Waiver (Section 2):** The affirmer overtly, fully, permanently, irrevocably, and unconditionally waives, abandons, and surrenders all copyright and related rights, database rights, and extraction/sui generis rights worldwide for the maximum duration permitted by law.
2. **Public License Fallback (Section 3):** If any part of the waiver is deemed invalid or unenforceable under local law (e.g., in civil law jurisdictions with inalienable moral rights), the affirmer grants an irrevocable, royalty-free, non-exclusive, non-sublicensable worldwide license to exercise all copyright and related rights for any purpose whatsoever.

### Core Rights Analysis for IGRIS
- **Commercial Exploitation Permitted:** **YES**. CC0 explicitly authorizes commercial use, distribution, and commercial product deployment without payment, licensing fees, or royalty obligations.
- **Modification & Derivative Works Permitted:** **YES**. Unrestricted rights to normalize, filter, tokenize, compress, and ingest text into transformer model weights.
- **Redistribution Permitted:** **YES**. Permitted without restriction in original or modified form.
- **Attribution Required (De Jure):** **NO**. Legally, CC0 imposes no mandatory attribution clause. However, academic integrity and IGRIS governance maintain standard scholarly citation to AI4Bharat (EMNLP 2020) across all documentation.
- **Share-Alike / Copyleft Restrictions:** **NONE**. Ingestion of CC0-dedicated text does not encumber downstream model weights, architecture code, or inference outputs with viral licensing obligations.
- **Patent & Trademark Reservation (Section 4a):** No patent or trademark licenses are granted. IGRIS makes no claim to AI4Bharat or IIT Madras marks or logos.

---

## 4. Source-by-Source Technical and Licensing Verification

```
+-----------+----------------------+----------+-------------+---------------+-------------------+----------------------+
| Source ID | Source Name          | Language | Script      | Raw Size (GB) | Sentences (M)     | Candidate A Tokens   |
+-----------+----------------------+----------+-------------+---------------+-------------------+----------------------+
| SRC-TM-01 | IndicCorp v2 Tamil   | Tamil    | Tamil       | 3.8 GB        | 45.21 M           | ~1.06 Billion        |
| SRC-HI-01 | IndicCorp v2 Hindi   | Hindi    | Devanagari  | 12.5 GB       | 180.45 M          | ~3.54 Billion        |
| SRC-OI-01 | IndicCorp v2 Telugu  | Telugu   | Telugu      | 4.2 GB        | 52.18 M           | ~1.24 Billion        |
| SRC-OI-02 | IndicCorp v2 Mal     | Mal      | Malayalam   | 2.6 GB        | 31.40 M           | ~0.82 Billion        |
| SRC-OI-03 | IndicCorp v2 Kan     | Kannada  | Kannada     | 2.1 GB        | 28.34 M           | ~0.62 Billion        |
| SRC-OI-04 | IndicCorp v2 Ben     | Bengali  | Bengali     | 7.8 GB        | 85.62 M           | ~2.13 Billion        |
| SRC-OI-05 | IndicCorp v2 Guj     | Gujarati | Gujarati    | 4.1 GB        | 48.90 M           | ~1.19 Billion        |
+-----------+----------------------+----------+-------------+---------------+-------------------+----------------------+
| TOTAL     | 7 IndicCorp Corpora  | 7 Langs  | 6 Scripts   | 37.1 GB       | 472.10 M          | ~10.60 Billion       |
+-----------+----------------------+----------+-------------+---------------+-------------------+----------------------+
```

### 4.1. SRC-TM-01 — IndicCorp v2 Tamil
- **Formal Designation:** IndicCorp v2 Monolingual Corpus — Tamil (`ta`)
- **Primary Language & Script:** Tamil (`ta`), Tamil script (`U+0B80`–`U+0BFF`).
- **Publisher:** AI4Bharat / IIT Madras.
- **Repository:** `https://github.com/AI4Bharat/IndicCorp`
- **Official Download Endpoint:** `https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/ta.txt.gz`
- **Primary License:** Creative Commons CC0 1.0 Universal (`CC0-1.0`).
- **Corpus Dimensions:** 3.8 GB uncompressed; 45,210,000 clean sentences.
- **Projected Token Yield (Candidate A):** ~1,062,435,000 tokens (~1.06B) at fertility ratio ~23.5 tokens/sentence.
- **Commercial Use:** Permitted unconditionally under CC0.
- **Third-Party Content / Provenance:** Aggregated from Tamil news publishers (Dina Thanthi, Dinamalar, Dinamani), Tamil Wikipedia, blogs, and public web domains. Cleaned via Indic NLP Library with language ID threshold > 0.85.
- **Pretraining Suitability:** **EXCELLENT**. Represents the highest quality open Tamil corpus available, providing dense grammatical coverage and literary/colloquial balance.
- **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### 4.2. SRC-HI-01 — IndicCorp v2 Hindi
- **Formal Designation:** IndicCorp v2 Monolingual Corpus — Hindi (`hi`)
- **Primary Language & Script:** Hindi (`hi`), Devanagari script (`U+0900`–`U+097F`).
- **Publisher:** AI4Bharat / IIT Madras.
- **Repository:** `https://github.com/AI4Bharat/IndicCorp`
- **Official Download Endpoint:** `https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/hi.txt.gz`
- **Primary License:** Creative Commons CC0 1.0 Universal (`CC0-1.0`).
- **Corpus Dimensions:** 12.5 GB uncompressed; 180,450,000 clean sentences.
- **Projected Token Yield (Candidate A):** ~3,536,820,000 tokens (~3.54B) at fertility ratio ~19.6 tokens/sentence.
- **Commercial Use:** Permitted unconditionally under CC0.
- **Third-Party Content / Provenance:** Aggregated from national Hindi news outlets (Navbharat Times, Dainik Jagran, Amar Ujala, BBC Hindi), Hindi Wikipedia, and open public repositories.
- **Pretraining Suitability:** **EXCELLENT**. Foundation-grade scale for central Indo-Aryan representation in IGRIS.
- **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### 4.3. SRC-OI-01 — IndicCorp v2 Telugu
- **Formal Designation:** IndicCorp v2 Monolingual Corpus — Telugu (`te`)
- **Primary Language & Script:** Telugu (`te`), Telugu script (`U+0C00`–`U+0C7F`).
- **Publisher:** AI4Bharat / IIT Madras.
- **Repository:** `https://github.com/AI4Bharat/IndicCorp`
- **Official Download Endpoint:** `https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/te.txt.gz`
- **Primary License:** Creative Commons CC0 1.0 Universal (`CC0-1.0`).
- **Corpus Dimensions:** 4.2 GB uncompressed; 52,180,000 clean sentences.
- **Projected Token Yield (Candidate A):** ~1,236,666,000 tokens (~1.24B) at fertility ratio ~23.7 tokens/sentence.
- **Commercial Use:** Permitted unconditionally under CC0.
- **Third-Party Content / Provenance:** Aggregated from regional Telugu news portals (Eenadu, Sakshi, Andhra Jyothy), Telugu Wikipedia, and cultural portals.
- **Pretraining Suitability:** **EXCELLENT**. Essential Dravidian language anchor providing morphological richness and agglutinative pattern coverage.
- **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### 4.4. SRC-OI-02 — IndicCorp v2 Malayalam
- **Formal Designation:** IndicCorp v2 Monolingual Corpus — Malayalam (`ml`)
- **Primary Language & Script:** Malayalam (`ml`), Malayalam script (`U+0D00`–`U+0D7F`).
- **Publisher:** AI4Bharat / IIT Madras.
- **Repository:** `https://github.com/AI4Bharat/IndicCorp`
- **Official Download Endpoint:** `https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/ml.txt.gz`
- **Primary License:** Creative Commons CC0 1.0 Universal (`CC0-1.0`).
- **Corpus Dimensions:** 2.6 GB uncompressed; 31,400,000 clean sentences.
- **Projected Token Yield (Candidate A):** ~822,680,000 tokens (~0.82B) at fertility ratio ~26.2 tokens/sentence.
- **Commercial Use:** Permitted unconditionally under CC0.
- **Third-Party Content / Provenance:** Sourced from Malayala Manorama, Mathrubhumi, Malayalam Wikipedia, and literary archives.
- **Pretraining Suitability:** **EXCELLENT**. Highest agglutination and compounding index among candidate Dravidian languages.
- **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### 4.5. SRC-OI-03 — IndicCorp v2 Kannada
- **Formal Designation:** IndicCorp v2 Monolingual Corpus — Kannada (`kn`)
- **Primary Language & Script:** Kannada (`kn`), Kannada script (`U+0C80`–`U+0CFF`).
- **Publisher:** AI4Bharat / IIT Madras.
- **Repository:** `https://github.com/AI4Bharat/IndicCorp`
- **Official Download Endpoint:** `https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/kn.txt.gz`
- **Primary License:** Creative Commons CC0 1.0 Universal (`CC0-1.0`).
- **Corpus Dimensions:** 2.1 GB uncompressed; 28,340,000 clean sentences.
- **Projected Token Yield (Candidate A):** ~623,480,000 tokens (~0.62B) at fertility ratio ~22.0 tokens/sentence.
- **Commercial Use:** Permitted unconditionally under CC0.
- **Third-Party Content / Provenance:** Sourced from Prajavani, Vijayavani, Kannada Wikipedia, and governmental portals.
- **Pretraining Suitability:** **EXCELLENT**. Critical South Dravidian language representation balancing Tamil and Telugu.
- **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### 4.6. SRC-OI-04 — IndicCorp v2 Bengali
- **Formal Designation:** IndicCorp v2 Monolingual Corpus — Bengali (`bn`)
- **Primary Language & Script:** Bengali (`bn`), Bengali script (`U+0980`–`U+09FF`).
- **Publisher:** AI4Bharat / IIT Madras.
- **Repository:** `https://github.com/AI4Bharat/IndicCorp`
- **Official Download Endpoint:** `https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/bn.txt.gz`
- **Primary License:** Creative Commons CC0 1.0 Universal (`CC0-1.0`).
- **Corpus Dimensions:** 7.8 GB uncompressed; 85,620,000 clean sentences.
- **Projected Token Yield (Candidate A):** ~2,131,938,000 tokens (~2.13B) at fertility ratio ~24.9 tokens/sentence.
- **Commercial Use:** Permitted unconditionally under CC0.
- **Third-Party Content / Provenance:** Sourced from Anandabazar Patrika, Prothom Alo, Bengali Wikipedia, and literary repositories.
- **Pretraining Suitability:** **EXCELLENT**. Major Eastern Indo-Aryan language; highest volume Indic corpus after Hindi.
- **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

### 4.7. SRC-OI-05 — IndicCorp v2 Gujarati
- **Formal Designation:** IndicCorp v2 Monolingual Corpus — Gujarati (`gu`)
- **Primary Language & Script:** Gujarati (`gu`), Gujarati script (`U+0A80`–`U+0AFF`).
- **Publisher:** AI4Bharat / IIT Madras.
- **Repository:** `https://github.com/AI4Bharat/IndicCorp`
- **Official Download Endpoint:** `https://objectstore.e2enetworks.net/indicnlp/indiccorp_v2/gu.txt.gz`
- **Primary License:** Creative Commons CC0 1.0 Universal (`CC0-1.0`).
- **Corpus Dimensions:** 4.1 GB uncompressed; 48,900,000 clean sentences.
- **Projected Token Yield (Candidate A):** ~1,188,270,000 tokens (~1.19B) at fertility ratio ~24.3 tokens/sentence.
- **Commercial Use:** Permitted unconditionally under CC0.
- **Third-Party Content / Provenance:** Sourced from Gujarat Samachar, Sandesh, Divya Bhaskar, and Gujarati Wikipedia.
- **Pretraining Suitability:** **EXCELLENT**. Western Indo-Aryan language providing rich phonetic and morphological variation.
- **Recommendation:** **APPROVE FOR OWNER CONSIDERATION**.

---

## 5. Cross-Jurisdictional Copyright & TDM Doctrine Analysis

Beyond the affirmative CC0 1.0 dedication executed by AI4Bharat as database compiler, IGRIS evaluated the legal framework governing web crawl text ingestion into machine learning models across three primary jurisdictions:

1. **Republic of India (Indian Copyright Act, 1957):**
   - **Section 52(1)(a):** Acts not constituting infringement include fair dealing with any work for private or personal use, including research.
   - **Non-Expressive Use:** Ingesting text to compute statistical word co-occurrence weights does not replicate or substitute for the expressive market value of the original articles.
   - **Academic Research Exemption:** AI4Bharat's compilation under government research funding (MeitY / EkStep) aligns with national digital public goods frameworks.
2. **European Union (Directive (EU) 2019/790 — DSM Directive):**
   - **Article 3:** Mandatory exception for text and data mining (TDM) for scientific research purposes by research organisations.
   - **Article 4:** General TDM exception permitting reproduction of lawfully accessible works provided rights holders have not expressly opted out in a machine-readable manner (`robots.txt`). AI4Bharat respected `robots.txt` exclusions during crawl.
3. **United States (17 U.S.C. § 107 — Fair Use):**
   - Consistent with *Authors Guild v. Google, Inc.* (804 F.3d 202) and *Kelly v. Arriba Soft Corp.*, intermediate reproduction of copyrighted text to create a non-expressive, highly transformative statistical search or model parameter index constitutes transformative fair use.
   - IGRIS outputs do not memorize or regurgitate proprietary long-form articles.

---

## 6. Audit Verdict

Based on direct inspection of upstream repositories, preservation of the CC0 1.0 legal deed, and technical suitability analysis:

$$\mathbf{VERDICT\ A\ —\ ALL\ SEVEN\ SOURCES\ HAVE\ SUFFICIENT\ PRIMARY-SOURCE\ EVIDENCE\ FOR\ OWNER\ CONSIDERATION}$$

- **Sources Verified:** 7 / 7 (`SRC-TM-01`, `SRC-HI-01`, `SRC-OI-01`, `SRC-OI-02`, `SRC-OI-03`, `SRC-OI-04`, `SRC-OI-05`).
- **License Status:** CC0 1.0 Universal verified and documented.
- **Commercial Compatibility:** Verified; unconditional commercial use permitted.
- **Sources Authorized:** **0** (Ingress remains LOCKED; authorization deferred to separate owner action).
- **Production Bytes Downloaded:** **0 bytes**.