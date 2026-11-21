# IGRIS Human Review Package (Version 2): Data Custodian (`DATA_CUSTODIAN`)

**Document Version:** 2.0.0  
**Status:** PENDING AUTHENTIC HUMAN REVIEW (Unsigned)  
**Governing Role:** `DATA_CUSTODIAN`  
**Governing Standard:** IGRIS Data Custody, Checksum & Ingestion Security Specification  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`

---

## 1. Role Responsibilities & Custodial Mandate

The **Data Custodian** possesses sole operational authority over:
1. Verification of upstream repository authenticity, official URLs, and source repository maintainers.
2. Cryptographic SHA-256 pre-validation of all candidate archives prior to sandbox extraction.
3. Enforcement of UTF-8 encoding losslessness (zero tolerance for replacement character `\uFFFD`).
4. Strict Unicode 15.1.0 NFC canonical normalization (zero decomposed ligatures in Indic/Tamil scripts).
5. Quarantine directory sandboxing (`quarantine/datasets/<dataset_id>/`) with strict write-once permissions.
6. Execution of mandatory header/footer stripping and trademark removal for Project Gutenberg (`SRC-EN-01`, `SRC-CV-06`).
7. Quarantine enforcement of `SRC-CV-04`, ensuring only the isolated chosen-prompts subset (`SRC-CV-04-CHOSEN-PROMPTS-ISOLATED`) is staged for fertility evaluation.

---

## 2. Evidentiary References

Before signing, the Data Custodian must examine and verify the following official records:
- [x] [`DATASET_SOURCE_CATALOG_V3.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_CATALOG_V3.csv) — Catalog records and official URLs.
- [x] [`DATASET_LICENSE_EVIDENCE_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_LICENSE_EVIDENCE_V2.csv) — Official license deeds and repository links.
- [x] [`SOURCE_STATUS_RECONCILIATION.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/SOURCE_STATUS_RECONCILIATION.csv) — 32-source status reconciliation audit.
- [x] [`GUTENBERG_JURISDICTION_REVIEW_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/GUTENBERG_JURISDICTION_REVIEW_V2.md) — Header stripping and trademark de-branding protocol.
- [x] [`PIPELINE_AUTHORIZATION_MATRIX_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PIPELINE_AUTHORIZATION_MATRIX_V2.csv) — Pipeline boundaries and gates.

---

## 3. Custodial Source-by-Source Review (All 32 Sources)

| Source ID | Dataset Name | Primary Status | Custodial Action | Technical Verification & Sandboxing Requirements | Custodian Decision |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | VERIFIED | Ingest to Quarantine | Verify AI4Bharat SHA-256; enforce UTF-8 NFC; validate byte round-trip. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-02** | Tamil Wikipedia Dump | CONDITIONAL | Ingest to Quarantine | Verify Wikimedia XML dump MD5; strip Wikitext markup before staging. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-03** | OSCAR 23.01 Tamil (Filtered) | UNVERIFIED | **WITHHOLD** | Uncurated Common Crawl; crawler provenance audit required prior to staging. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-01** | Project Gutenberg Open Archive | VERIFIED | Ingest to Quarantine | Mandatory execution of PGLAF header/footer/trademark stripping. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-02** | English Wikipedia Dump | CONDITIONAL | Ingest to Quarantine | Verify Wikimedia multistream bz2 SHA-256; sanitize templates. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-03** | C4 English Corpus | CONDITIONAL | Ingest to Quarantine | Verify AllenAI / HuggingFace shards; check JSONL schema. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | VERIFIED | Ingest to Quarantine | Verify HuggingFace dataset checksum; inspect social formatting. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | VERIFIED | Ingest to Quarantine | Validate TSV structure; verify UTF-8 losslessness. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-03** | Social Dravidian Sentiment Tanglish | INCOMPATIBLE | **BLOCK** | Non-commercial restriction; do not download or stage in quarantine. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | VERIFIED | Ingest to Quarantine | Verify AI4Bharat SHA-256; enforce Devanagari Unicode 15.1 NFC. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-02** | Hindi Wikipedia Dump | CONDITIONAL | Ingest to Quarantine | Verify Wikimedia XML dump; strip templates and markup. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-03** | IIT Bombay Hindi-English | INCOMPATIBLE | **BLOCK** | CC-BY-NC-SA restriction; do not stage. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | VERIFIED | Ingest to Quarantine | Verify AI4Bharat SHA-256; validate Telugu script NFC. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | VERIFIED | Ingest to Quarantine | Verify AI4Bharat SHA-256; validate Malayalam script NFC. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | VERIFIED | Ingest to Quarantine | Verify AI4Bharat SHA-256; validate Kannada script NFC. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-04** | IndicCorp v2 (Bengali) | VERIFIED | Ingest to Quarantine | Verify AI4Bharat SHA-256; validate Bengali script NFC. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-05** | IndicCorp v2 (Gujarati) | VERIFIED | Ingest to Quarantine | Verify AI4Bharat SHA-256; validate Gujarati script NFC. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-01** | FLORES-200 Benchmark | CONDITIONAL | Ingest to Eval Only | Strict separation: stage to `quarantine/evaluation/`, never training. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | CONDITIONAL | Ingest to Quarantine | Verify multilingual JSONL gzip integrity; check language tags. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-01** | The Stack v2 (Permissive) | VERIFIED | Ingest to Quarantine | Verify Software Heritage release; audit automated license tags. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | VERIFIED | Ingest to Eval Only | **Strict Contamination Guard**: stage strictly to `quarantine/eval/code/`. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-01** | Linux Kernel Documentation | CONDITIONAL | Ingest to Quarantine | Extract from kernel.org tarball; verify PGP signature of release. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-02** | IETF RFC Archive (Text) | VERIFIED | Ingest to Quarantine | Verify RFC Editor rsync archive integrity; ASCII/UTF-8 validation. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-03** | Python Official Documentation | VERIFIED | Ingest to Quarantine | Extract from python.org documentation tarball; verify MD5/SHA-256. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-01** | DailyDialog Dataset | INCOMPATIBLE | **BLOCK** | Non-commercial restriction; do not download or stage. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-02** | OpenSubtitles Multilingual | INCOMPATIBLE | **BLOCK** | Unlicensed movie dialogue scrape; severe copyright risk; do not stage. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-03** | OpenAssistant OASST1 | VERIFIED | Ingest to Quarantine | Validate HuggingFace parquet checksum; verify dialogue turn tree format. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-04** | Anthropic HH-RLHF | VERIFIED | Isolated Eval Staging | **Mandatory Quarantine**: Extract ONLY prompt prefixes for fertility testing into `SRC-CV-04-CHOSEN-PROMPTS-ISOLATED`. Do not stage completions. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-05** | MultiWOZ 2.4 | VERIFIED | Ingest to Quarantine | Verify JSON dialogue schema; validate turn boundary tags. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-06** | Project Gutenberg Theatrical | VERIFIED | Ingest to Quarantine | Mandatory PGLAF header/trademark stripping on dramatic scripts. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-01** | Unicode Standard 15.1.0 Suite | VERIFIED | Ingest to Quarantine | Verify unicode.org official checksum; validate raw byte edge cases. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-02** | Unicode 15.1 Emoji Data Files | VERIFIED | Ingest to Quarantine | Verify unicode.org official checksum; validate ZWJ sequence tables. | `[ ] APPROVE  [ ] REJECT` |

---

## 4. Custodial Reviewer Sign-Off Field (Authentic Human Review)

> [!IMPORTANT]
> **INSTRUCTION TO HUMAN REVIEWER**: Do not execute or stage any dataset files until this form is physically or digitally signed by the authorized Data Custodian. No automated system may populate this signature.

- **Designated Role**: `DATA_CUSTODIAN`
- **Reviewer Full Name**: `__________________________________________________`
- **Organizational Title**: `__________________________________________________`
- **Reviewer Employee / ID Number**: `__________________________________________________`
- **Reviewer Corporate Email**: `__________________________________________________`
- **Custodial Decision**: `[ ] APPROVED FOR QUARANTINE STAGING    [ ] REJECTED / WITHHELD`
- **Digital / Physical Signature**: `__________________________________________________`
- **Date of Review (YYYY-MM-DD)**: `____________________`
- **Cryptographic PGP Key ID / Hash**: `__________________________________________________`

---

## 5. Expiry and Revocation Conditions

1. **Validity Period**: This custodial approval shall remain valid for **90 calendar days** from the signature date, after which re-validation is mandatory.
2. **Immediate Revocation Triggers**:
   - Upstream source archive hash mismatch upon transport.
   - Discovery of corrupted UTF-8 byte sequences or unnormalized Unicode.
   - Failure of the automated Project Gutenberg trademark de-branding filter.
   - Any attempt to stage un-isolated `SRC-CV-04` completions into pre-training paths.
