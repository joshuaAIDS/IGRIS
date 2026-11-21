# IGRIS Human Review Package (Version 2): Chief Architect (`CHIEF_ARCHITECT`)

**Document Version:** 2.0.0  
**Status:** PENDING AUTHENTIC HUMAN REVIEW (Unsigned)  
**Governing Role:** `CHIEF_ARCHITECT`  
**Governing Standard:** IGRIS Architectural Invariant & Vocabulary Preservation Standard  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`

---

## 1. Role Responsibilities & Architectural Mandate

The **Chief Architect** possesses sole architectural authority over:
1. Strict preservation of the IGRIS decoder-only multilingual transformer specification:
   - **Context Window**: 2048 tokens.
   - **Hidden Dimension ($d_{\text{model}}$)**: 512.
   - **Transformer Layers**: 16.
   - **Attention Heads**: 8 Query Heads.
   - **Key-Value Heads**: 4 KV Heads (Grouped-Query Attention, 2:1 ratio).
   - **Intermediate FFN Size**: 2048.
   - **Exact Vocabulary Size**: 32,768 tokens.
   - **12 Structural Tokens**: Pinned at token IDs 0–11 (`<|pad|>`, `<|begin_of_text|>`, `<|end_of_text|>`, `<think>`, `</think>`, `<action>`, `</action>`, `<action_result>`, `</action_result>`, `<|system|>`, `<|user|>`, `<|assistant|>`).
2. Verification of Candidate A (`tokenizer.json`) and Candidate B (`tokenizer.model`) SHA-256 hash invariance.
3. Enforcement of Benchmark Contamination Guards: strict isolation of `SRC-CD-02` (HumanEval/MBPP) and `SRC-ML-01` (FLORES-200) from tokenizer training corpora.
4. Prevention of Vocabulary Poisoning: absolute exclusion of `SRC-CV-04` (Anthropic HH-RLHF preference pairs and red-team attacks) from vocabulary learning to preserve the 32,768 vocabulary budget for high-frequency natural tokens.
5. Strict enforcement of the **Independence Axiom**: confirming that tokenizer eligibility confers **zero** rights to execute Supervised Fine-Tuning (SFT), model pre-training, alignment evaluation, or safety evaluation.

---

## 2. Evidentiary References

Before signing, the Chief Architect must review:
- [x] [`DATASET_SOURCE_CATALOG_V3.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_CATALOG_V3.csv) — 32 candidate sources and functional allocations.
- [x] [`PIPELINE_GATE_AUDIT.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PIPELINE_GATE_AUDIT.md) — Seven-gate decoupling and SFT authorization locks.
- [x] [`TOKENIZER_DATA_ELIGIBILITY_MATRIX.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_DATA_ELIGIBILITY_MATRIX.md) — Vocabulary protection and boundary rationale.
- [x] [`artifacts/tokenizer/candidate_a/tokenizer.json`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_a/tokenizer.json) — Candidate A artifact (`ac7e18b1...`).
- [x] [`artifacts/tokenizer/candidate_b/tokenizer.model`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_b/tokenizer.model) — Candidate B artifact (`d3a3431e...`).

---

## 3. Architectural Source-by-Source Review (All 32 Sources)

| Source ID | Dataset Name | Category | Vocab Training Role | Benchmark Role | Architectural Impact & Contamination Guard | Architect Decision |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | Tamil | **ELIGIBLE** | Background | Core Tamil vocabulary builder; validates script merge efficiency. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-02** | Tamil Wikipedia Dump | Tamil | CONDITIONAL | Background | High lexical diversity; legal sign-off required prior to training. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-03** | OSCAR 23.01 Tamil (Filtered) | Tamil | CONDITIONAL | Background | Web colloquial Tamil; crawler provenance unverified. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-01** | Project Gutenberg Open Archive | English | **ELIGIBLE** | Background | Classical English prose; baseline compression evaluation. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-02** | English Wikipedia Dump | English | CONDITIONAL | Background | Encyclopedic English; ShareAlike legal clearance required. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-03** | C4 English Corpus | English | CONDITIONAL | Background | Web crawl distribution; attribution verification required. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | Tanglish | **ELIGIBLE** | Primary Test | Crucial code-mixing benchmark; tests Romanized Indic fertility. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | Tanglish | **ELIGIBLE** | Primary Test | Social code-mixed sentences; evaluates token merge fragmentation. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-03** | Social Dravidian Sentiment Tanglish | Tanglish | **REJECTED** | N/A | Incompatible license; permanently excluded. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | Hindi | **ELIGIBLE** | Background | Core Hindi vocabulary builder; Devanagari script compression. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-02** | Hindi Wikipedia Dump | Hindi | CONDITIONAL | Background | High-register Devanagari vocabulary; ShareAlike clearance required. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-03** | IIT Bombay Hindi-English | Hindi | **REJECTED** | N/A | Incompatible license; permanently excluded. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | Other Indian Langs | **ELIGIBLE** | Background | Telugu script representation in 32,768 vocabulary budget. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | Other Indian Langs | **ELIGIBLE** | Background | Malayalam script representation; complex conjunct compression. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | Other Indian Langs | **ELIGIBLE** | Background | Kannada script representation; subword merge efficiency. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-04** | IndicCorp v2 (Bengali) | Other Indian Langs | **ELIGIBLE** | Background | Bengali script representation; resolves Eastern Indic coverage gap. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-05** | IndicCorp v2 (Gujarati) | Other Indian Langs | **ELIGIBLE** | Background | Gujarati script representation; resolves Western Indic coverage gap. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-01** | FLORES-200 Benchmark | Multilingual Mixed | CONDITIONAL | **Primary Eval** | **Evaluation Benchmark Only**: Must NOT enter tokenizer training. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | Multilingual Mixed | CONDITIONAL | Background | Broad web text; multi-script stress testing across Tiers 2–4. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-01** | The Stack v2 (Permissive) | Programming Code | **ELIGIBLE** | Background | Programming syntax vocabulary builder; whitespace and indent tokens. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | Programming Code | **PROHIBITED** | **Primary Eval** | **Strict Contamination Guard**: Absolute training ban; eval only. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-01** | Linux Kernel Documentation | Technical Docs | CONDITIONAL | Background | Technical C software syntax; GPL copyleft review required. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-02** | IETF RFC Archive (Text) | Technical Docs | **ELIGIBLE** | Background | Clean technical prose and protocol specifications. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-03** | Python Official Documentation | Technical Docs | **ELIGIBLE** | Background | High-quality standard library technical documentation. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-01** | DailyDialog Dataset | Conversational Text | **REJECTED** | N/A | Incompatible license; permanently excluded. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-02** | OpenSubtitles Multilingual | Conversational Text | **REJECTED** | N/A | Severe legal defect; permanently excluded. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-03** | OpenAssistant OASST1 | Conversational Text | **ELIGIBLE** | **Primary Eval** | Multi-turn dialogue trees; evaluates `<|user|>` and `<|assistant|>`. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-04** | Anthropic HH-RLHF | Conversational Text | **PROHIBITED** | **Alignment Eval** | **Vocabulary Poisoning Guard**: Training strictly banned. Fertility eval restricted to isolated prompt prefixes subset. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-05** | MultiWOZ 2.4 | Conversational Text | **ELIGIBLE** | **Primary Eval** | Goal-oriented task dialogue; tests turn boundary tokens. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-06** | Project Gutenberg Theatrical | Conversational Text | **ELIGIBLE** | **Primary Eval** | Clean dramatic dialogue; zero PII; public domain baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-01** | Unicode Standard 15.1.0 Suite | Emoji & Unicode | **ELIGIBLE** | Stress Test | Tests byte fallback (0x00–0xFF) and unassigned code point stability. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-02** | Unicode 15.1 Emoji Data Files | Emoji & Unicode | **ELIGIBLE** | Stress Test | Tests multi-codepoint grapheme clusters and ZWJ sequence preservation. | `[ ] APPROVE  [ ] REJECT` |

---

## 4. Architectural Sign-Off Field (Authentic Human Review)

> [!IMPORTANT]
> **INSTRUCTION TO HUMAN REVIEWER**: Do not approve any dataset or authorize tokenizer evaluation until this form is physically or digitally signed by the authorized Chief Architect. No automated system may populate this signature.

- **Designated Role**: `CHIEF_ARCHITECT`
- **Reviewer Full Name**: `__________________________________________________`
- **Engineering / Architecture Credentials**: `__________________________________________________`
- **Organizational Title**: `__________________________________________________`
- **Reviewer Corporate Email**: `__________________________________________________`
- **Architectural Clearance Decision**: `[ ] APPROVED FOR ISOLATED EVALUATION    [ ] REJECTED / WITHHELD`
- **Digital / Physical Signature**: `__________________________________________________`
- **Date of Review (YYYY-MM-DD)**: `____________________`
- **Cryptographic PGP Key ID / Hash**: `__________________________________________________`

---

## 5. Expiry and Revocation Conditions

1. **Validity Period**: This architectural approval shall remain valid for **180 calendar days** from the signature date, after which architectural re-validation is mandatory.
2. **Immediate Revocation Triggers**:
   - Any modification to Candidate A or Candidate B artifact SHA-256 checksums.
   - Any alteration to the 12 pinned structural token IDs (IDs 0–11).
   - Any attempt to train candidate tokenizers on benchmark evaluation sets (`SRC-CD-02`, `SRC-ML-01`).
   - Any inclusion of `SRC-CV-04` preference pairs in tokenizer pre-training.
   - Unauthorized activation of Supervised Fine-Tuning (SFT) or model pre-training.
