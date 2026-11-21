# IGRIS Governance Review: Legal Governance (`LEGAL_GOVERNANCE`)

**Document Version:** 1.0.0  
**Status:** PENDING HUMAN REVIEW (Unsigned)  
**Governing Role:** `LEGAL_GOVERNANCE`  
**Governing Standard:** IGRIS Intellectual Property & Licensing Policy  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Role Responsibilities & Mandate

The **Legal Governance Lead** possesses sole authority over:
1. Intellectual property rights, copyright clearance, and commercial exploitation permissions.
2. Interpretation of license terms (`CC0-1.0`, `MIT`, `Apache-2.0`, `CC-BY-4.0`, `CC-BY-SA 4.0`, `GPL-2.0`, `ODC-By 1.0`).
3. Determination of whether model weights or tokenizer vocabularies constitute derivative works under ShareAlike or copyleft clauses.
4. Enforcement of Non-Commercial (`NC`) restrictions, preventing unauthorized deployment in commercial models.
5. Compliance with source repository Terms of Service, scraping prohibitions, and third-party media rights.

---

## 2. Evidentiary Checklist

Before signing, the Legal Governance Lead must verify the following artifacts:
- [ ] [`DATASET_LICENSE_EVIDENCE_MATRIX.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_LICENSE_EVIDENCE_MATRIX.csv) has been reviewed for exact license terms and governing jurisdictions.
- [ ] [`DATASET_SOURCE_RISK_UPDATE.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_RISK_UPDATE.md) has been reviewed for legal risk profiles.
- [ ] Formal legal assessment of whether tokenizer training/evaluation triggers CC-BY-SA 4.0 ShareAlike obligations on model weights.
- [ ] Rejection and purging of all four incompatible sources (`SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02`).
- [ ] Attribution inventory drafted for all sources requiring author credits.

---

## 3. Source-by-Source Legal Determination (All 26 Sources)

| Source ID | Dataset Name | Published License | Legal Verdict | Specific Legal Determination & Rationale |
| :--- | :--- | :--- | :---: | :--- |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | CC0-1.0 | **CLEARED** | Public domain dedication. Unconditional commercial and training rights. |
| **SRC-TM-02** | Tamil Wikipedia Dump | CC-BY-SA-4.0 | **REQUIRES WAIVER** | ShareAlike clause requires legal opinion on whether model weights constitute derivative works. |
| **SRC-TM-03** | OSCAR 23.01 Tamil | ODC-By / Common Crawl | **UNVERIFIED** | ODC-By covers database; underlying web crawl copyright unverified. |
| **SRC-EN-01** | Project Gutenberg Open Archive | Public Domain (US) | **CLEARED** | Pre-1928 literary works are in US public domain; strip PG trademark headers. |
| **SRC-EN-02** | English Wikipedia Dump | CC-BY-SA-4.0 | **REQUIRES WAIVER** | ShareAlike clause requires legal opinion on whether model weights constitute derivative works. |
| **SRC-EN-03** | C4 (Clean Crawled Corpus) | ODC-By / Common Crawl | **REQUIRES REVIEW** | Curation under ODC-By; web crawl fair use analysis required for commercial pre-training. |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | CC-BY-4.0 | **CLEARED** | Permissive attribution license. Commercial evaluation and training permitted. |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | CC-BY-4.0 | **CLEARED** | Permissive attribution license. Commercial evaluation and training permitted. |
| **SRC-TG-03** | Social Dravidian Sentiment | Research-Only | **REJECTED** | Competition license explicitly forbids commercial use and redistribution. |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | CC0-1.0 | **CLEARED** | Public domain dedication. Unconditional commercial and training rights. |
| **SRC-HI-02** | Hindi Wikipedia Dump | CC-BY-SA-4.0 | **REQUIRES WAIVER** | ShareAlike clause requires legal opinion on whether model weights constitute derivative works. |
| **SRC-HI-03** | IIT Bombay Parallel Corpus | CC-BY-NC-SA 4.0 | **REJECTED** | Non-Commercial (`NC`) clause prohibits commercial model training or deployment. |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | CC0-1.0 | **CLEARED** | Public domain dedication. Unconditional commercial and training rights. |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | CC0-1.0 | **CLEARED** | Public domain dedication. Unconditional commercial and training rights. |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | CC0-1.0 | **CLEARED** | Public domain dedication. Unconditional commercial and training rights. |
| **SRC-ML-01** | FLORES-200 Multilingual | CC-BY-SA 4.0 | **REQUIRES WAIVER** | Permitted for read-only benchmark evaluation; training use triggers ShareAlike scrutiny. |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | ODC-By / Common Crawl | **REQUIRES REVIEW** | Database rights under ODC-By; underlying 108-language crawl requires fair use review. |
| **SRC-CD-01** | The Stack v2 (Permissive Subset) | Permissive (MIT/Apache) | **CLEARED** | ScanCode verified permissive licenses. Commercial training authorized. |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | MIT / Apache-2.0 | **CLEARED (EVAL)** | Permissive licenses. Authorized for evaluation; must be isolated from pre-training. |
| **SRC-TD-01** | Linux Kernel Documentation | GPL-2.0-with-exception | **REQUIRES REVIEW** | Documentation exception permits copying; review required on copyleft derivative reach. |
| **SRC-TD-02** | IETF RFC Archive (Text) | RFC 5378 / IETF Trust | **CLEARED** | Worldwide royalty-free rights to reproduce specifications; modification restricted. |
| **SRC-TD-03** | Python Official Documentation | PSF-2.0 | **CLEARED** | Permissive open-source documentation license. Commercial use fully authorized. |
| **SRC-CV-01** | DailyDialog Dataset | CC-BY-NC-SA 4.0 | **REJECTED** | Non-Commercial clause forbids commercial deployment. |
| **SRC-CV-02** | OpenSubtitles Multilingual | Scraped Media | **REJECTED** | Unauthorized film subtitle scrapes. Extreme third-party copyright liability. |
| **SRC-EM-01** | Unicode 15.1.0 Test Suite | Unicode-DFS-2016 | **CLEARED** | Perpetual royalty-free data license. Fully authorized. |
| **SRC-EM-02** | Unicode 15.1.0 Emoji Data Files | Unicode-DFS-2016 | **CLEARED** | Perpetual royalty-free emoji sequence data license. Fully authorized. |

---

## 4. Legal Determination & Sign-Off Record

```
[ ] APPROVED — Intellectual property, copyright permissions, and commercial rights verified.
[ ] REJECTED — Unresolved copyright infringement, non-commercial, or copyleft risks present.
[ ] CONDITIONAL — Approved strictly for the 14 cleared permissive sources (Tier 1).

Reviewer Name:          __________________________________________________
Reviewer Title:         Legal Counsel / Governance Lead
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Legal Governance Notes: __________________________________________________
```
