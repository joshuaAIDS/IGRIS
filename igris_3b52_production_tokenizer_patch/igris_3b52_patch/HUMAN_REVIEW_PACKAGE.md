# IGRIS Milestone 3C.4 — Human Review Package

**Document Version:** 1.0.0  
**Status:** PENDING HUMAN REVIEW (All Fields Unsigned)  
**Governing Standard:** IGRIS Production Dataset Authorization Policy  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

> [!IMPORTANT]
> **GOVERNANCE NOTICE**: All approval fields, reviewer identities, digital signature hashes, and authorization dates in this document are strictly **PENDING HUMAN REVIEW**. No automated agent may sign, approve, or alter these records. Production access remains strictly `LOCKED`.

---

## 1. Overview & Sign-off Framework

Before any candidate dataset can be acquired, ingested, or processed for tokenizer evaluation, all **four independent governance authorities** must conduct formal reviews, verify evidentiary artifacts, and record their determinations.

Each review section below is dedicated to one authority and details:
- Core review questions that must be answered
- Evidentiary documentation required for review
- Key risks requiring specific scrutiny
- Formal determination, signature, and expiration fields

---

## 2. Review Section 1: Data Custodian (`DATA_CUSTODIAN`)

### 2.1 Role Mandate
The **Data Custodian** governs dataset ownership, physical custody, transport verification, SHA-256 cryptographic manifests, UTF-8 losslessness, NFC Unicode normalization, and storage isolation.

### 2.2 Custodial Review Questions
1. Have the upstream source endpoints (`official_source_url`) been confirmed as active, authentic, and free from DNS hijacking?
2. Are upstream release versions, snapshot dates, and published file sizes consistent with the catalog?
3. Has a formal transport protocol (e.g. SHA-256 checksum pre-validation prior to sandbox extraction) been established?
4. Is there an automated pre-processing filter to strip trademark disclaimers (e.g. Project Gutenberg headers) and Byte Order Marks (`U+FEFF`)?
5. Is the storage location configured as a write-once, isolated sandbox directory preventing contamination of the pre-training inventory?

### 2.3 Evidentiary Artifacts Required
- [`DATASET_SOURCE_EVIDENCE_REGISTER.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_EVIDENCE_REGISTER.csv)
- Upstream cryptographic release hashes published by original publishers
- Staging directory quarantine path specification: `quarantine/datasets/<dataset_id>/`
- Character encoding test log confirming strict UTF-8 losslessness and Unicode 15.1.0 NFC enforcement

### 2.4 Custodial Risks Requiring Attention
- **RSK-ENC-01**: Ingress files containing non-UTF-8 bytes or Byte Order Marks (BOM).
- **RSK-ENC-02**: Decomposed Unicode characters (NFD/NFKD) causing artificial vocabulary explosion.
- **RSK-SUP-01**: Upstream silent mutation of crawl archives altering benchmark reproducibility.

### 2.5 Custodial Determination Record
```
[ ] APPROVED — All custodial and data integrity controls verified.
[ ] REJECTED — Critical custodial or integrity deficiencies identified.
[ ] CONDITIONAL — Approved only for specified sources subject to conditions.

Reviewer Full Name:     __________________________________________________
Reviewer Title:         __________________________________________________
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Custodial Notes:        __________________________________________________
```

---

## 3. Review Section 2: Legal Governance (`LEGAL_GOVERNANCE`)

### 3.1 Role Mandate
The **Legal Governance Lead** enforces copyright compliance, open-source contract terms, commercial model training permissions, patent grants, terms of service adherence, and ShareAlike/copyleft contagion prevention.

### 3.2 Legal Review Questions
1. Does the license of each proposed source explicitly grant commercial use and the right to construct derived computational models?
2. Does tokenizing, encoding, and calculating vocabulary compression ratios constitute a "Derivative Work" / "Adapted Material" under Creative Commons (`CC-BY-SA 4.0`) or GPL (`GPL-2.0-with-exception`)?
3. For Common Crawl derived corpora (`C4`, `mC4`, `OSCAR`), does text extraction fall under applicable fair use / text and data mining exceptions?
4. Are attribution notices preserved in a machine-readable `NOTICE.txt` for all CC-BY, ODC-By, and PSF-licensed sources?
5. Have the four incompatible sources (`SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02`) been purged from the acquisition pipeline?

### 3.3 Evidentiary Artifacts Required
- [`DATASET_LICENSE_EVIDENCE_MATRIX.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_LICENSE_EVIDENCE_MATRIX.csv)
- [`DATASET_SOURCE_RISK_UPDATE.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_RISK_UPDATE.md)
- Formal Legal Opinion on CC-BY-SA 4.0 model weight encumbrance
- Machine-readable attribution inventory template

### 3.4 Legal Risks Requiring Attention
- **RSK-LEG-01**: Violation of Non-Commercial restrictions (`NC` clause breach on `SRC-HI-03` and `SRC-CV-01`).
- **RSK-LEG-02**: Viral ShareAlike copyleft contagion from Wikipedia or FLORES-200 contaminating model weights.
- **RSK-LEG-03**: Direct copyright infringement liability from scraped media subtitles (`SRC-CV-02`).

### 3.5 Legal Determination Record
```
[ ] APPROVED — All legal and licensing terms verified and approved.
[ ] REJECTED — Legal risks or copyleft encumbrances prohibit acquisition.
[ ] CONDITIONAL — Approved strictly for verified permissive sources (Tier 1).

Reviewer Full Name:     __________________________________________________
Reviewer Title:         __________________________________________________
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Legal Governance Notes: __________________________________________________
```

---

## 4. Review Section 3: Security & Privacy (`SECURITY_PRIVACY`)

### 4.1 Role Mandate
The **Security & Privacy Lead** enforces statutory data privacy compliance (India Digital Personal Data Protection Act 2023, GDPR), automated PII scrubbing, cryptographic secret scanning, ethical bias/toxicity screening, and 13-gram evaluation/pre-training leakage prevention.

### 4.2 Security & Privacy Review Questions
1. Has every candidate dataset passed automated PII screening for Indian mobile numbers, Aadhaar numbers, PAN cards, email addresses, and payment card numbers?
2. Has high-entropy secret scanning (detecting AWS keys, GitHub tokens, RSA private keys) been configured for Category 7 (Programming Code) sources?
3. Are social media user handles in Tanglish corpora (`SRC-TG-01`) pseudonymized or stripped before tokenization?
4. Has a 13-gram overlap test (`detect_train_eval_leakage`) been established between evaluation benchmarks (HumanEval, MBPP) and candidate pre-training sources to guarantee zero benchmark contamination?
5. Has an ethical safety audit been conducted to screen for abusive, defamatory, or extreme toxic content in web crawl datasets?

### 4.3 Evidentiary Artifacts Required
- DPDP Act 2023 & GDPR Privacy Compliance Statement
- Automated PII Regex Pattern Specification (`test_dataset_quality.py`)
- Secret Scanner Entropy Detector Ruleset
- 13-Gram Benchmark Leakage Verification Report (Zero overlap requirement)

### 4.4 Security & Privacy Risks Requiring Attention
- **RSK-PRI-01**: Inadvertent ingestion of Personally Identifiable Information under India DPDP Act 2023.
- **RSK-PRI-02**: Hardcoded API keys, private keys, or corporate credentials in code datasets.
- **RSK-CON-01**: 13-gram benchmark contamination between evaluation sets and pre-training data.

### 4.5 Security & Privacy Determination Record
```
[ ] APPROVED — Privacy, secret isolation, and decontamination controls verified.
[ ] REJECTED — Unmitigated PII or benchmark contamination risks present.
[ ] CONDITIONAL — Approved subject to mandatory automated PII quarantine.

Reviewer Full Name:     __________________________________________________
Reviewer Title:         __________________________________________________
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Security/Privacy Notes: __________________________________________________
```

---

## 5. Review Section 4: Chief Architect (`CHIEF_ARCHITECT`)

### 5.1 Role Mandate
The **Chief Architect** ensures architectural adherence to the approved Transformer specifications (16 layers, 512 hidden dimension, 8 attention heads, 4 KV heads [GQA], 2,048 context length, 32,768 vocabulary, structural tokens 0–11), context budget allocation, and the 10-category benchmark stratification.

### 5.2 Architectural Review Questions
1. Does the candidate evaluation corpus strictly preserve the approved 10-category benchmark taxonomy?
2. Are sequence lengths stratified across all four required tiers: Short (1–64 tokens, 25%), Medium (65–1024 tokens, 50%), Long (1025–2048 tokens, 20%), and Overflow (>2048 tokens, 5%)?
3. How will the documented sub-language gaps in Category 5 (absence of Bengali and Gujarati) and the complete absence of compliant sources for Category 9 (Conversational Text) be addressed?
4. Does the comparative evaluation plan ensure identical tokenization inputs and reproducible metrics for both Candidate A (ByteLevel BPE) and Candidate B (SentencePiece Unigram)?
5. Does the evaluation process guarantee that structural token IDs 0–11 remain strictly isolated and can never be emitted from user text?

### 5.3 Evidentiary Artifacts Required
- [`DATASET_CATEGORY_COVERAGE_AUDIT.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_CATEGORY_COVERAGE_AUDIT.md)
- [`DATASET_SPECIFICATION.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SPECIFICATION.md)
- Sequence Tier Stratification Specification (Tiers 1–4)
- Milestone 3B.58 Comparative Evaluation Methodology

### 5.4 Architectural Risks Requiring Attention
- **RSK-CON-02**: Sample duplication skewing compression metrics and sequence length distributions.
- **RSK-ENC-02**: Decomposed Unicode characters (NFD) causing artificial vocabulary explosion.
- **RSK-ARCH-01**: Category 5 and Category 9 deficits distorting multilingual representation.

### 5.5 Architectural Determination Record
```
[ ] APPROVED — Architectural budget, sequence tiers, and invariants verified.
[ ] REJECTED — Architectural invariants violated or domain stratification skewed.
[ ] CONDITIONAL — Approved for 7 verified categories; Category 5/9 gaps held pending.

Reviewer Full Name:     __________________________________________________
Reviewer Title:         __________________________________________________
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Architectural Notes:    __________________________________________________
```

---

## 6. Master Consolidated Sign-Off Summary

The production dataset access gate (`scripts/dataset_authorization.py`) remains locked until all four records below transition to `APPROVED` with valid SHA-256 signatures:

| Governance Role | Authority Title | Primary Mandate | Status | Signature Hash |
| :--- | :--- | :--- | :---: | :---: |
| **`DATA_CUSTODIAN`** | Data Custodian | Lineage, Cryptographic Hashes & UTF-8 | `PENDING` | `[PENDING]` |
| **`LEGAL_GOVERNANCE`** | Legal Counsel | Copyright, Commercial Rights & Copyleft | `PENDING` | `[PENDING]` |
| **`SECURITY_PRIVACY`** | Security & Privacy Lead | PII, Secret Scanning & AI Safety | `PENDING` | `[PENDING]` |
| **`CHIEF_ARCHITECT`** | Chief Architect | Architecture, Context & 10 Domains | `PENDING` | `[PENDING]` |

**Overall Gate Status:** **`LOCKED`**
