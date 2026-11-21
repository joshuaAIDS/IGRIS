# IGRIS Governance Review: Data Custodian (`DATA_CUSTODIAN`)

**Document Version:** 1.0.0  
**Status:** PENDING HUMAN REVIEW (Unsigned)  
**Governing Role:** `DATA_CUSTODIAN`  
**Governing Standard:** IGRIS Data Lineage, Custody & Integrity Policy  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Role Responsibilities & Mandate

The **Data Custodian** possesses sole authority over:
1. Verification of upstream dataset ownership, source repository authenticity, and transport protocols.
2. Cryptographic SHA-256 pre-validation before physical extraction into quarantine sandboxes.
3. Strict enforcement of UTF-8 encoding losslessness (zero unrecognized byte replacements `\uFFFD`).
4. Automated Unicode 15.1.0 NFC normalization (zero tolerance for decomposed NFD ligatures).
5. Physical isolation between candidate evaluation sets and pre-training corpora.
6. Execution of trademark/preamble stripping (e.g. Project Gutenberg header cleaning).

---

## 2. Evidentiary Checklist

Before signing, the Data Custodian must verify the following artifacts:
- [ ] [`DATASET_SOURCE_EVIDENCE_REGISTER.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_EVIDENCE_REGISTER.csv) has been reviewed for active URLs and authentic owners.
- [ ] Upstream official release manifests and checksums match the catalog entries.
- [ ] Sandbox extraction directory `quarantine/datasets/<dataset_id>/` is configured with strict write-once permissions.
- [ ] UTF-8 losslessness and Unicode 15.1.0 NFC filters in `scripts/dataset_inventory.py` have passed synthetic testing.
- [ ] Header stripping script for Project Gutenberg (`SRC-EN-01`) is tested and validated.

---

## 3. Source-by-Source Custodial Evaluation (All 26 Sources)

| Source ID | Dataset Name | Technical Verification | Custodial Recommendation | Specific Custodial Conditions & Requirements |
| :--- | :--- | :---: | :---: | :--- |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | VERIFIED | **PROCEED** | Validate upstream AI4Bharat SHA-256; enforce NFC normalization. |
| **SRC-TM-02** | Tamil Wikipedia Dump | VERIFIED | **CONDITIONAL** | Verify Wikimedia XML dump MD5/SHA-256; strip Wikitext markup before tokenization. |
| **SRC-TM-03** | OSCAR 23.01 Tamil (Filtered) | UNVERIFIED | **WITHHOLD** | Upstream provenance is uncurated web crawl; verify archive integrity before staging. |
| **SRC-EN-01** | Project Gutenberg Open Archive | VERIFIED | **PROCEED** | Automated filter must strip "Project Gutenberg™" trademark preambles/postambles. |
| **SRC-EN-02** | English Wikipedia Dump | VERIFIED | **CONDITIONAL** | Verify XML dump hash; mandate wikitext parser to isolate clean body paragraphs. |
| **SRC-EN-03** | C4 (Clean Crawled Corpus) | VERIFIED | **CONDITIONAL** | Large footprint (305 GB); verify slice checksum; quarantine until PII scrub is complete. |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | VERIFIED | **PROCEED** | Validate TSV structure; enforce UTF-8 validation on mixed scripts. |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | VERIFIED | **PROCEED** | Validate JSONL line integrity; confirm NFC normalization. |
| **SRC-TG-03** | Social Dravidian Sentiment | INCOMPATIBLE | **REJECT** | Incompatible license; do not allocate custodial staging space. |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | VERIFIED | **PROCEED** | Validate upstream SHA-256; enforce NFC normalization on Devanagari conjuncts. |
| **SRC-HI-02** | Hindi Wikipedia Dump | VERIFIED | **CONDITIONAL** | Verify XML dump hash; strip wikitext markup. |
| **SRC-HI-03** | IIT Bombay Parallel Corpus | INCOMPATIBLE | **REJECT** | Non-commercial restriction; do not stage. |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | VERIFIED | **PROCEED** | Validate Telugu script encoding fidelity and NFC normalization. |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | VERIFIED | **PROCEED** | Validate Malayalam chillu characters and atomic ligatures. |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | VERIFIED | **PROCEED** | Validate Kannada script encoding fidelity and NFC normalization. |
| **SRC-ML-01** | FLORES-200 Multilingual | VERIFIED | **CONDITIONAL** | Verify TSV line alignment across 200 languages; maintain evaluation holdout isolation. |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | VERIFIED | **CONDITIONAL** | Enforce language ID threshold verification on sample slices. |
| **SRC-CD-01** | The Stack v2 (Permissive Subset) | VERIFIED | **PROCEED** | Synchronize with Software Heritage opt-out list; enforce strict UTF-8 decoding. |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | VERIFIED | **PROCEED** | Strictly quarantine from pre-training storage to prevent benchmark contamination. |
| **SRC-TD-01** | Linux Kernel Documentation | VERIFIED | **CONDITIONAL** | RST/Sphinx markup stripping required before tokenization. |
| **SRC-TD-02** | IETF RFC Archive (Text) | VERIFIED | **PROCEED** | Pure ASCII text; strip page break headers/footers (`RFC XXXX [Page Y]`). |
| **SRC-TD-03** | Python Official Documentation | VERIFIED | **PROCEED** | HTML/Sphinx documentation; extract raw documentation text losslessly. |
| **SRC-CV-01** | DailyDialog Dataset | INCOMPATIBLE | **REJECT** | Non-commercial restriction; do not stage. |
| **SRC-CV-02** | OpenSubtitles Multilingual | INCOMPATIBLE | **REJECT** | Copyright infringement liability; do not stage. |
| **SRC-EM-01** | Unicode 15.1.0 Test Suite | VERIFIED | **PROCEED** | Authoritative Unicode Consortium data; verify against published SHA-256. |
| **SRC-EM-02** | Unicode 15.1.0 Emoji Data Files | VERIFIED | **PROCEED** | Official emoji sequence files; verify against published SHA-256. |

---

## 4. Custodial Determination & Sign-Off Record

```
[ ] APPROVED — Custodial integrity, transport protocols, and UTF-8/NFC controls fully verified.
[ ] REJECTED — Transport, data integrity, or custody validation failed.
[ ] CONDITIONAL — Approved strictly for the 14 verified sources subject to staging conditions.

Reviewer Name:          __________________________________________________
Reviewer Title:         Data Custodian
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Custodial Conditions:   __________________________________________________
```
