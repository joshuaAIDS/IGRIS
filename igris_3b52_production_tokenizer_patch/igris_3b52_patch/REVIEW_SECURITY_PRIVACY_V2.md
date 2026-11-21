# IGRIS Human Review Package (Version 2): Security & Privacy (`SECURITY_PRIVACY`)

**Document Version:** 2.0.0  
**Status:** PENDING AUTHENTIC HUMAN REVIEW (Unsigned)  
**Governing Role:** `SECURITY_PRIVACY`  
**Governing Standard:** IGRIS Data Security, PII Policy & Adversarial Boundary Protection  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`

---

## 1. Role Responsibilities & Security Mandate

The **Security & Privacy Officer** possesses sole authority over:
1. Enforcement of the PII Screening Policy (detection and scrubbing of names, phone numbers, email addresses, Aadhaar numbers, PAN, SSNs, and payment data).
2. Strict architectural quarantine of adversarial red-team datasets (`SRC-CV-04` Anthropic HH-RLHF), ensuring zero toxic payloads or jailbreak prompts enter tokenizer pre-training.
3. Web crawl safety evaluation (assessing malware links, spam clusters, and private data leakage in OSCAR, C4, and mC4).
4. Code security screening (detecting hardcoded cryptographic secrets, API tokens, and private keys in The Stack v2).
5. Audit of filesystem and cryptographic access gates in `src/authorization.py`, confirming default-deny operation and audit logging.
6. Verification that all post-training pipelines (SFT, alignment evaluation, safety evaluation) remain **`NOT AUTHORIZED`**.

---

## 2. Evidentiary References

Before signing, the Security & Privacy Officer must review:
- [x] [`DATASET_SOURCE_CATALOG_V3.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_CATALOG_V3.csv) — PII risk levels and provenance classifications.
- [x] [`PIPELINE_GATE_AUDIT.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PIPELINE_GATE_AUDIT.md) — Seven-gate decoupling and default-deny mechanisms.
- [x] [`PIPELINE_AUTHORIZATION_MATRIX_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PIPELINE_AUTHORIZATION_MATRIX_V2.csv) — Permission fields and boundary notes.
- [x] [`CONVERSATIONAL_DATA_CLASSIFICATION.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CONVERSATIONAL_DATA_CLASSIFICATION.md) — Five-subtype taxonomy and toxic token exclusion rules.

---

## 3. Security & Privacy Source-by-Source Review (All 32 Sources)

| Source ID | Dataset Name | PII Risk Level | Provenance | Security Review & Quarantine Mandates | Security Officer Decision |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | LOW | Curated Crawl | Low PII risk; verified AI4Bharat deduplicated text; clean language baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-02** | Tamil Wikipedia Dump | LOW | Curated Wiki | Public encyclopedic articles; minimal PII risk; clean public content. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-03** | OSCAR 23.01 Tamil (Filtered) | **HIGH** | Web Crawl | Unfiltered web crawl; high risk of emails, phone numbers, and private addresses. Requires PII scrub. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-01** | Project Gutenberg Open Archive | **NONE** | Literary PD | Pre-1928 literary classics; zero living PII risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-02** | English Wikipedia Dump | LOW | Curated Wiki | Public encyclopedic content; community moderated; low privacy risk. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-03** | C4 English Corpus | **HIGH** | Web Crawl | Common Crawl extract; known PII leakage (names, emails); mandatory PII filter required. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | MEDIUM | Social Media | Social media comments; usernames and colloquial handles present; requires anonymization. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | MEDIUM | Social Media | Social sentences; moderate PII risk; inspect for personal identifying details. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-03** | Social Dravidian Sentiment Tanglish | MEDIUM | Social Media | Scraped user commentary; license incompatible; **MUST BLOCK**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | LOW | Curated Crawl | Deduplicated curated crawl; low privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-02** | Hindi Wikipedia Dump | LOW | Curated Wiki | Public encyclopedic content; community moderated; low privacy risk. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-03** | IIT Bombay Hindi-English | LOW | Academic Parallel | Academic parallel translations; low PII; license incompatible; **MUST BLOCK**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | LOW | Curated Crawl | Curated Indic text; low privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | LOW | Curated Crawl | Curated Indic text; low privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | LOW | Curated Crawl | Curated Indic text; low privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-04** | IndicCorp v2 (Bengali) | LOW | Curated Crawl | Curated Indic text; low privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-05** | IndicCorp v2 (Gujarati) | LOW | Curated Crawl | Curated Indic text; low privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-01** | FLORES-200 Benchmark | **NONE** | Commissioned Trans | Professional parallel benchmark; zero PII; isolated to evaluation. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | **HIGH** | Web Crawl | Broad web crawl; high risk of global PII and spam; mandatory PII regex screening. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-01** | The Stack v2 (Permissive) | MEDIUM | Open Source Code | Secrets scanning required: filter API keys, SSH private keys, and hardcoded tokens. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | **NONE** | Challenge Problems | Synthesized coding challenges; zero PII; isolated from training (contamination guard). | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-01** | Linux Kernel Documentation | LOW | Kernel Docs | Technical software documentation; developer email addresses present (allowlist required). | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-02** | IETF RFC Archive (Text) | LOW | Technical Standards | Internet standard RFCs; public author affiliations; low privacy risk. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-03** | Python Official Documentation | **NONE** | Technical Docs | Official Python language documentation; zero PII; clean technical text. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-01** | DailyDialog Dataset | LOW | Dialogue Textbook | Language learning dialogue; clean text; license incompatible; **MUST BLOCK**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-02** | OpenSubtitles Multilingual | MEDIUM | Movie Subtitles | Fan subtitle scrape; uncurated; severe legal defect; **MUST BLOCK**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-03** | OpenAssistant OASST1 | MEDIUM | Crowdworker Turns | Human-annotated dialogues; toxic prompts present (requires filtering based on toxicity flags). | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-04** | Anthropic HH-RLHF | **CRITICAL** | Red-Team / RLHF | **MANDATORY SECURITY LOCK**: Contains toxic completions, jailbreaks, and cyber attacks. Banned from training. Stage ONLY isolated chosen-prompts subset. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-05** | MultiWOZ 2.4 | LOW | Wizard-of-Oz Dialog | Synthetic/simulated tourist dialogues; zero real PII; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-06** | Project Gutenberg Theatrical | **NONE** | Dramatic Plays | Classical dramatic scripts; zero living PII; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-01** | Unicode Standard 15.1.0 Suite | **NONE** | Technical Spec | Character tables; zero privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-02** | Unicode 15.1 Emoji Data Files | **NONE** | Technical Spec | Emoji sequence definitions; zero privacy risk; verified safe. | `[ ] APPROVE  [ ] REJECT` |

---

## 4. Security Reviewer Sign-Off Field (Authentic Human Review)

> [!IMPORTANT]
> **INSTRUCTION TO HUMAN REVIEWER**: Do not approve any dataset or unlock filesystem access until this form is physically or digitally signed by the authorized Security & Privacy Officer. No automated system may populate this signature.

- **Designated Role**: `SECURITY_PRIVACY`
- **Reviewer Full Name**: `__________________________________________________`
- **Security Certifications (CISSP/CISM/etc.)**: `__________________________________________________`
- **Organizational Title**: `__________________________________________________`
- **Reviewer Corporate Email**: `__________________________________________________`
- **Security Clearance Decision**: `[ ] APPROVED FOR ISOLATED STAGING    [ ] REJECTED / WITHHELD`
- **Digital / Physical Signature**: `__________________________________________________`
- **Date of Review (YYYY-MM-DD)**: `____________________`
- **Cryptographic PGP Key ID / Hash**: `__________________________________________________`

---

## 5. Expiry and Revocation Conditions

1. **Validity Period**: This security approval shall remain valid for **90 calendar days** from the signature date, after which security re-audit is mandatory.
2. **Immediate Revocation Triggers**:
   - Detection of unredacted sensitive PII (Aadhaar, SSN, PAN, credit card numbers).
   - Any attempt to ingest `SRC-CV-04` rejected/red-team completions into tokenizer training.
   - Discovery of active secrets or credentials in code corpora (`SRC-CD-01`).
   - Unauthorized activation of SFT, alignment evaluation, or production data access.
