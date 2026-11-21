# IGRIS Tokenizer Data Eligibility Matrix

**Document Version:** 1.0.0  
**Status:** Canonical Eligibility Specification (Milestone 3C.7)  
**Governing Standard:** `DATASET_SPECIFICATION.md` & `CONVERSATIONAL_DATA_CLASSIFICATION.md`  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Dataset Acquisition Status:** `NOT AUTHORIZED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary & Purpose

In strict compliance with IGRIS Milestone 3C.7 instructions, this document decouples legal/license verification status from functional pipeline eligibility across all 32 candidate dataset sources in the IGRIS catalog.

A common flaw in ML governance is treating a dataset that is legally verified as automatically eligible for training. Within the IGRIS architecture, **license verification is a necessary prerequisite but not a sufficient condition for tokenizer training eligibility**. Specifically:
- **Evaluation Benchmarks** (`SRC-CD-02` HumanEval/MBPP, `SRC-ML-01` FLORES-200) are legally clear (MIT/Apache/CC-BY-SA) but must be **strictly quarantined** from tokenizer training to avoid benchmark contamination and artificial compression inflation.
- **Preference and Adversarial Safety Datasets** (`SRC-CV-04` Anthropic HH-RLHF) are licensed under permissive MIT terms, but ingesting them into tokenizer vocabulary formation would create dedicated subword tokens for slurs, exploits, and toxic sequences, polluting the 32,768 vocabulary.
- **Copyright Incompatible Datasets** (`SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02`) carry non-commercial (NC) or unauthorized scrape encumbrances and are **ineligible across all pipelines**.

---

## 2. Decoupled Governance Fields Definition

Every dataset source in the IGRIS V3 catalog is evaluated across five independent governance axes:

1. **License Verification Status**:
   - `VERIFIED`: Source has unambiguous public domain, CC0, or permissive OSI-approved licensing (20 sources).
   - `CONDITIONAL`: Permissive or copyleft (CC-BY-SA, ODC-By, GPL-exception) requiring human legal review of attribution or share-alike obligations (7 sources).
   - `UNVERIFIED`: Ambiguous or contradictory licensing documentation requiring primary custodian audit (1 source: `SRC-TM-03`).
   - `INCOMPATIBLE`: Carries non-commercial clauses (CC-BY-NC-SA) or unverified scraping terms prohibited by IGRIS commercial governance (4 sources: `SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02`).

2. **Commercial Use Evidence Status**:
   - `CONFIRMED`: Public license explicitly permits commercial training, distribution, and commercial model deployment.
   - `CONDITIONAL_ATTRIBUTION`: Permitted for commercial use provided attribution notices are packaged in model documentation.
   - `CONDITIONAL_COPYLEFT`: Commercial use permitted, but copyleft / ShareAlike viral implications require legal clearance.
   - `UNCONFIRMED`: Commercial permissions cannot be established from public docs without primary creator confirmation.
   - `PROHIBITED`: Explicit `-NC` clause or unauthorized copyright scrape forbids commercial use.

3. **Tokenizer Training Eligibility**:
   - `ELIGIBLE`: Unencumbered, non-benchmark, non-adversarial corpora approved for subword vocabulary learning and merge operations (18 sources).
   - `INELIGIBLE_CONDITIONAL`: Blocked from training pending legal/provenance sign-off (8 sources).
   - `INELIGIBLE_PROHIBITED`: Legally verified but architecturally banned from training due to benchmark contamination or vocabulary safety risks (2 sources: `SRC-CD-02`, `SRC-CV-04`).
   - `INELIGIBLE_REJECTED`: Permanently excluded due to incompatible license or severe copyright defect (4 sources).

4. **Tokenizer Evaluation Eligibility**:
   - `ELIGIBLE`: Permitted for out-of-domain compression ratio, fertility ($r_{\text{char/tok}}$), and sequence length stress testing across Tiers 1–4 (28 sources).
   - `INELIGIBLE_REJECTED`: Excluded from all pipelines (4 sources).

5. **Alignment & Safety Evaluation Eligibility**:
   - `ELIGIBLE_PRIMARY`: Primary benchmark for downstream post-training alignment, preference modeling, and safety auditing (`SRC-CV-04`).
   - `ELIGIBLE_OPTIONAL`: Secondary conversational or code execution evaluation (`SRC-CD-02`, `SRC-CV-03`).
   - `NOT_APPLICABLE`: General language/domain corpora not structured for safety or preference evaluation (25 sources).
   - `INELIGIBLE_REJECTED`: Excluded (4 sources).

---

## 3. Master 32-Source Eligibility Matrix

| Source ID | Dataset Name | Category | License Verification Status | Commercial Use Evidence | Tokenizer Training Eligibility | Tokenizer Evaluation Eligibility | Alignment / Safety Evaluation Eligibility | Pipeline Boundary Restrictions |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | Tamil | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | None; unencumbered baseline. |
| **SRC-TM-02** | Tamil Wikipedia Dump | Tamil | CONDITIONAL | CONDITIONAL_COPYLEFT | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | ShareAlike legal sign-off required prior to training. |
| **SRC-TM-03** | OSCAR 23.01 Tamil | Tamil | UNVERIFIED | UNCONFIRMED | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | Crawler provenance audit required prior to training. |
| **SRC-EN-01** | Project Gutenberg Open Archive | English | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | Mandatory item-level public domain check (author death + 70 yrs). |
| **SRC-EN-02** | English Wikipedia Dump | English | CONDITIONAL | CONDITIONAL_COPYLEFT | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | CC-BY-SA 4.0 review required. |
| **SRC-EN-03** | OSCAR 23.01 English | English | CONDITIONAL | CONDITIONAL_ATTRIBUTION | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | ODC-By attribution verification required. |
| **SRC-TG-01** | AI4Bharat Romanized Indic | Tanglish | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | CC-BY-4.0 attribution notice required. |
| **SRC-TG-02** | Dakshina Lexicon (ta-Latn) | Tanglish | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | CC-BY-4.0 attribution notice required. |
| **SRC-TG-03** | L3Cube-Pune Tanglish | Tanglish | INCOMPATIBLE | PROHIBITED | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | Non-commercial restriction; banned from all pipelines. |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | Hindi | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | None; unencumbered CC0 baseline. |
| **SRC-HI-02** | Hindi Wikipedia Dump | Hindi | CONDITIONAL | CONDITIONAL_COPYLEFT | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | CC-BY-SA 4.0 review required. |
| **SRC-HI-03** | IIT Bombay Hindi-English | Hindi | INCOMPATIBLE | PROHIBITED | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | CC-BY-NC-SA 4.0; banned from all pipelines. |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | Other Indian Languages | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | None; unencumbered CC0 baseline. |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | Other Indian Languages | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | None; unencumbered CC0 baseline. |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | Other Indian Languages | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | None; unencumbered CC0 baseline. |
| **SRC-OI-04** | IndicCorp v2 (Bengali) | Other Indian Languages | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | None; unencumbered CC0 baseline. |
| **SRC-OI-05** | IndicCorp v2 (Gujarati) | Other Indian Languages | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | None; unencumbered CC0 baseline. |
| **SRC-ML-01** | FLORES-200 Benchmark | Multilingual Mixed | CONDITIONAL | CONDITIONAL_COPYLEFT | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | Evaluation benchmark; do not contaminate training splits. |
| **SRC-ML-02** | mC4 Multilingual Web Crawl | Multilingual Mixed | CONDITIONAL | CONDITIONAL_ATTRIBUTION | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | Common Crawl provenance and ODC-By review required. |
| **SRC-CD-01** | The Stack v2 Permissive | Programming Code | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | Permissive license filtering audit required. |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | Programming Code | VERIFIED | CONFIRMED | **INELIGIBLE_PROHIBITED** | **ELIGIBLE** | **ELIGIBLE_OPTIONAL** | **Contamination Guard**: strictly prohibited from tokenizer training. |
| **SRC-TD-01** | Linux Kernel Documentation | Technical Documentation | CONDITIONAL | CONDITIONAL_COPYLEFT | **INELIGIBLE_CONDITIONAL** | **ELIGIBLE** | NOT_APPLICABLE | GPL-2.0 syscall exemption audit required. |
| **SRC-TD-02** | IETF RFC Open Standards | Technical Documentation | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | IETF Trust provisions apply; clean technical prose. |
| **SRC-TD-03** | Python 3 Documentation | Technical Documentation | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | PSF-2.0 license notice required. |
| **SRC-CV-01** | DailyDialog Corpus | Conversational Text | INCOMPATIBLE | PROHIBITED | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | CC-BY-NC-SA 4.0; banned from all pipelines. |
| **SRC-CV-02** | OpenSubtitles Multilingual | Conversational Text | INCOMPATIBLE | PROHIBITED | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | **INELIGIBLE_REJECTED** | Web scrape of commercial subtitles; copyright violation risk. |
| **SRC-CV-03** | OpenAssistant OASST1 | Conversational Text | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | **ELIGIBLE_OPTIONAL** | Subtype B clean dialogue trees permitted; toxic flags filtered. |
| **SRC-CV-04** | Anthropic HH-RLHF | Conversational Text | VERIFIED | CONFIRMED | **INELIGIBLE_PROHIBITED** | **ELIGIBLE** | **ELIGIBLE_PRIMARY** | **Strict Prohibited**: Red-team & preference data banned from training. |
| **SRC-CV-05** | MultiWOZ 2.4 | Conversational Text | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | Subtype B task-oriented dialogue; Apache-2.0. |
| **SRC-CV-06** | Gutenberg Theatrical Dialogue | Conversational Text | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | Subtype E dramatic text; item-level public domain check required. |
| **SRC-EM-01** | Unicode Standard 15.1 Suite | Emoji & Unicode | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | Unicode Data License unencumbered. |
| **SRC-EM-02** | Unicode 15.1 Emoji Files | Emoji & Unicode | VERIFIED | CONFIRMED | **ELIGIBLE** | **ELIGIBLE** | NOT_APPLICABLE | Unicode Data License unencumbered. |

---

## 4. Pipeline Boundary Allocations for Conversational Data (Category 9)

Milestone 3C.6 established the five-subtype taxonomy for conversational text. Here we clarify the exact destination pipelines for conversational corpora:

```
+----------------------------------------------------------------------------------------------------+
|                         CONVERSATIONAL DATA PIPELINE ROUTING                                       |
+----------------------------------------------------------------------------------------------------+
                                            |
        +-----------------------------------+-----------------------------------+
        |                                                                       |
        v                                                                       v
[TOKENIZER PRE-TRAINING]                                            [POST-TRAINING ALIGNMENT]
        |                                                                       |
+-------+-------------------------------+                       +---------------+---------------+
| Subtype B: Multi-Turn (OASST1 clean)  |                       | Subtype C: Preference Pairs   |
| Subtype B: Task Dialogue (MultiWOZ)   |                       | Subtype D: Red-Team Attacks   |
| Subtype E: Theatrical (Gutenberg)     |                       | (Anthropic HH-RLHF Chosen/Rej)|
+---------------------------------------+                       +-------------------------------+
        |                                                                       |
        +-----------------------------------> [TOKENIZER EVALUATION] <---------+
                                              (Fertility & Tier Stress Testing)
                                              - OASST1 Test Splits
                                              - MultiWOZ Test Splits
                                              - Gutenberg Theatrical Test Splits
                                              - HH-RLHF Chosen Prompts (isolated)
```

### 4.1 Tokenizer Fertility Evaluation
- **Intended Use**: Measuring token compression ratio ($\text{bytes} / \text{tokens}$), fertility score ($r_{\text{char/tok}}$), and vocabulary coverage across colloquial expressions, turns, and conversational pauses.
- **Eligible Datasets**:
  - `SRC-CV-03` (OpenAssistant clean dialogue trees)
  - `SRC-CV-05` (MultiWOZ 2.4 task-oriented dialogues)
  - `SRC-CV-06` (Project Gutenberg Theatrical dialogues)
  - `SRC-CV-04` (Anthropic HH-RLHF: **Chosen prompts only**, strictly isolated from completions and preference labels).

### 4.2 Downstream Fine-Tuning
- **Intended Use**: Supervised Fine-Tuning (SFT) of the decoder-only transformer model post-pretraining to develop instruction-following and conversation abilities.
- **Eligible Datasets**:
  - `SRC-CV-03` (OASST1 multi-turn conversation trees)
  - `SRC-CV-05` (MultiWOZ 2.4 structured task turns)
  - *Note*: Downstream SFT data selection is out of scope for tokenizer construction, but structural tokens (`<|user|>`, `<|assistant|>`) must be validated to support these formats.

### 4.3 Post-Training Alignment Evaluation
- **Intended Use**: Direct Preference Optimization (DPO), Reinforcement Learning from Human Feedback (RLHF), and safety benchmarking (measuring harmfulness refusal rates).
- **Eligible Datasets**:
  - `SRC-CV-04` (Anthropic HH-RLHF: Full chosen and rejected preference pairs; helpfulness and harmlessness splits).
- **Absolute Boundary Rule**: `SRC-CV-04` preference pairs and adversarial red-team dialogue must **never** be mixed into tokenizer training or general pre-training corpora.

---

## 5. Technical Rationale for Banning Adversarial Data from Tokenizer Training

### 5.1 Preventing Vocabulary Poisoning
The IGRIS tokenizer utilizes a strictly constrained vocabulary size of **32,768 tokens**. Subword tokenizers (Byte-Pair Encoding and Unigram) optimize merge operations based on token n-gram frequency.
- Ingesting red-team data (`SRC-CV-04` harmlessness rejected completions, jailbreak prompts) creates atomic tokens for vulgarities, racial slurs, chemical weapon precursors, and exploit payloads.
- Once an atomic token is created for a toxic term, that token cannot be pruned without breaking vocabulary alignment and candidate artifact hashes.
- Furthermore, having dedicated atomic tokens for harmful terms reduces the embedding space distance between benign concepts and malicious actions, severely complicating downstream safety guardrail training.

### 5.2 Preventing Benchmark Contamination
If preference pairs (`chosen` vs `rejected`) are digested by the tokenizer:
- The tokenizer becomes artificially optimized to compress the specific syntax, tone, and sentence structure of the evaluation benchmark.
- Evaluation metrics such as compression ratio and bits-per-byte (BPB) become falsely inflated, leading to flawed candidate selection decisions.

---

## 6. Summary Tally of 32-Source Eligibility

```
Total Sources Audited: 32

License Verification Status:
  - VERIFIED:             20 (62.5%)
  - CONDITIONAL:           7 (21.9%)
  - UNVERIFIED:            1 ( 3.1%)
  - INCOMPATIBLE:          4 (12.5%)

Commercial Use Evidence Status:
  - CONFIRMED:            19 (59.4%)
  - CONDITIONAL_COPYLEFT:  5 (15.6%)
  - CONDITIONAL_ATTRIB:    3 ( 9.4%)
  - UNCONFIRMED:           1 ( 3.1%)
  - PROHIBITED:            4 (12.5%)

Tokenizer Training Eligibility:
  - ELIGIBLE:                 18 (56.3%)
  - INELIGIBLE_CONDITIONAL:    8 (25.0%)
  - INELIGIBLE_PROHIBITED:     2 ( 6.3%)  [SRC-CD-02, SRC-CV-04]
  - INELIGIBLE_REJECTED:       4 (12.5%)  [SRC-TG-03, SRC-HI-03, SRC-CV-01, SRC-CV-02]

Tokenizer Evaluation Eligibility:
  - ELIGIBLE:                 28 (87.5%)
  - INELIGIBLE_REJECTED:       4 (12.5%)

Alignment / Safety Evaluation Eligibility:
  - ELIGIBLE_PRIMARY:          1 ( 3.1%)  [SRC-CV-04]
  - ELIGIBLE_OPTIONAL:         2 ( 6.3%)  [SRC-CD-02, SRC-CV-03]
  - NOT_APPLICABLE:           25 (78.1%)
  - INELIGIBLE_REJECTED:       4 (12.5%)
```

---

## 7. Mandatory Governance Check

- [x] All 32 source IDs explicitly listed and accounted for ($18 + 8 + 2 + 4 = 32$).
- [x] Five decoupled governance fields created and tracked.
- [x] `SRC-CV-04` explicitly prohibited from tokenizer training.
- [x] Preference pairs and red-team datasets isolated to post-training alignment.
- [x] Project Gutenberg subject to item-level public domain review.
- [x] Four human approval roles preserved (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`).
- [x] Production access gate remains `LOCKED`.
