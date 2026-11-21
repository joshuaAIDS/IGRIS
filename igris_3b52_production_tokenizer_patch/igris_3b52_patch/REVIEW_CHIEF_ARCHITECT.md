# IGRIS Governance Review: Chief Architect (`CHIEF_ARCHITECT`)

**Document Version:** 1.0.0  
**Status:** PENDING HUMAN REVIEW (Unsigned)  
**Governing Role:** `CHIEF_ARCHITECT`  
**Governing Standard:** IGRIS Model Architecture & Benchmark Stratification Specification  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Role Responsibilities & Mandate

The **Chief Architect** possesses sole authority over:
1. Adherence to immutable model architecture parameters:
   - Decoder-only Transformer
   - 16 layers, 512 hidden dimension, 8 attention heads, 4 KV heads (GQA), 2,048 context length
   - Exactly 32,768 vocabulary entries
   - Exactly 12 structural tokens strictly pinned to IDs 0–11
2. Preservation and balance of the 10 approved benchmark evaluation categories (`DATASET_SPECIFICATION.md`).
3. Sequence tier stratification enforcement:
   - Short (1–64 tokens, 25%)
   - Medium (65–1024 tokens, 50%)
   - Long (1025–2048 tokens, 20%)
   - Overflow (>2048 tokens, 5%)
4. Identification and governance escalation of benchmark coverage deficits (Category 5 Indo-Aryan languages and Category 9 Conversational Text).
5. Verification of comparative evaluation methodology between Candidate A (ByteLevel BPE) and Candidate B (SentencePiece Unigram).

---

## 2. Evidentiary Checklist

Before signing, the Chief Architect must verify the following artifacts:
- [ ] [`DATASET_CATEGORY_COVERAGE_AUDIT.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_CATEGORY_COVERAGE_AUDIT.md) has been reviewed for domain coverage and gap analysis.
- [ ] [`DATASET_SPECIFICATION.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SPECIFICATION.md) targets ($\ge 3,500$ samples, $\ge 670\text{k}$ words, $\ge 4.3\text{M}$ chars) are preserved.
- [ ] Sequence tier stratification algorithm produces identical input tokens for both Candidate A and Candidate B.
- [ ] Structural tokens 0–11 remain strictly isolated from public text encoding.
- [ ] Benchmark deficits in Category 5 (Bengali/Gujarati) and Category 9 (Conversational Text) are documented for remediation.

---

## 3. Source-by-Source Architectural Assessment (All 26 Sources)

| Source ID | Dataset Name | Benchmark Category | Architectural Role | Architectural Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | Tamil | Primary Tamil benchmark corpus (Classical, news, administrative) | **APPROVED** |
| **SRC-TM-02** | Tamil Wikipedia Dump | Tamil | Supplementary Tamil encyclopedic articles | **CONDITIONAL** |
| **SRC-TM-03** | OSCAR 23.01 Tamil | Tamil | Secondary web crawl text (Unverified provenance) | **WITHHOLD** |
| **SRC-EN-01** | Project Gutenberg Open Archive | English | Primary English benchmark corpus (High lexical diversity) | **APPROVED** |
| **SRC-EN-02** | English Wikipedia Dump | English | Supplementary English encyclopedic text | **CONDITIONAL** |
| **SRC-EN-03** | C4 (Clean Crawled Corpus) | English | Web text evaluation slice | **CONDITIONAL** |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | Tanglish | Primary Tamil-English code-switching benchmark | **APPROVED** |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | Tanglish | Supplementary Romanized Tamil review sentences | **APPROVED** |
| **SRC-TG-03** | Social Dravidian Sentiment | Tanglish | Rejected on licensing grounds | **REJECTED** |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | Hindi | Primary Hindi benchmark corpus (Formal news, conjuncts) | **APPROVED** |
| **SRC-HI-02** | Hindi Wikipedia Dump | Hindi | Supplementary Hindi encyclopedic text | **CONDITIONAL** |
| **SRC-HI-03** | IIT Bombay Parallel Corpus | Hindi | Rejected on licensing grounds | **REJECTED** |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | Other Indian Languages | Primary Telugu benchmark corpus (Dravidian script transfer) | **APPROVED** |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | Other Indian Languages | Primary Malayalam benchmark corpus (Complex chillu ligatures) | **APPROVED** |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | Other Indian Languages | Primary Kannada benchmark corpus (Dravidian script transfer) | **APPROVED** |
| **SRC-ML-01** | FLORES-200 Multilingual | Multilingual Mixed Text | Multilingual parallel translation holdout benchmark | **CONDITIONAL** |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | Multilingual Mixed Text | Multilingual web text sample slice | **CONDITIONAL** |
| **SRC-CD-01** | The Stack v2 (Permissive Subset) | Programming Code | Primary source code benchmark (Python, TS, Rust, SQL, YAML) | **APPROVED** |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | Programming Code | Evaluation-only algorithmic coding benchmark | **APPROVED (EVAL)** |
| **SRC-TD-01** | Linux Kernel Documentation | Technical Documentation | Technical OS architecture documentation | **CONDITIONAL** |
| **SRC-TD-02** | IETF RFC Archive (Text) | Technical Documentation | Authoritative protocol specifications and ASCII tables | **APPROVED** |
| **SRC-TD-03** | Python Official Documentation | Technical Documentation | Highly structured API documentation and syntax guides | **APPROVED** |
| **SRC-CV-01** | DailyDialog Dataset | Conversational Text | Rejected on licensing grounds | **REJECTED** |
| **SRC-CV-02** | OpenSubtitles Multilingual | Conversational Text | Rejected on licensing grounds | **REJECTED** |
| **SRC-EM-01** | Unicode 15.1.0 Test Suite | Emoji & Unicode Edge Cases | Authoritative Unicode 15.1.0 UCD test suite | **APPROVED** |
| **SRC-EM-02** | Unicode 15.1.0 Emoji Data Files | Emoji & Unicode Edge Cases | Official Unicode Emoji 15.1 sequence test suites | **APPROVED** |

---

## 4. Architectural Determination & Sign-Off Record

```
[ ] APPROVED — Architectural invariants, context budgets, sequence tiers, and 10 categories verified.
[ ] REJECTED — Architectural invariants violated or domain stratification unbalanced.
[ ] CONDITIONAL — Approved for the 7 fully verified categories; Category 5/9 gaps held for remediation.

Reviewer Name:          __________________________________________________
Reviewer Title:         Chief Architect
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Architectural Notes:    __________________________________________________
```
