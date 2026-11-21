# IGRIS Milestone 3C.6 — Conversational Data Classification & Pipeline Allocation

**Document Version:** 1.0.0  
**Status:** Canonical Conversational Architecture Policy  
**Governing Standard:** `DATASET_SPECIFICATION.md` & IGRIS Tokenizer Boundary Security  
**Target Category:** Category 9 (Conversational Text)  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

Conversational text is frequently conflated in NLP into a single generic category. However, conversational data encompasses fundamentally distinct formats, semantic structures, and risk profiles ranging from natural informal discourse to adversarial red-team attacks.

In strict compliance with Milestone 3C.6 instructions:
1. Five distinct conversational subtypes are formally decoupled:
   - **Subtype A**: Ordinary conversational text
   - **Subtype B**: Multi-turn dialogue
   - **Subtype C**: Preference pairs
   - **Subtype D**: Rejected / red-team responses
   - **Subtype E**: Literary theatrical dialogue
2. Strict pipeline allocations are defined for:
   - **Tokenizer Training** (vocabulary formation and token frequency learning)
   - **Tokenizer Evaluation** (compression ratio, fertility, sequence tier stress-testing)
   - **Separate Alignment Evaluation** (post-training RLHF/DPO and safety auditing)
3. **Zero model or tokenizer training is performed.**

---

## 2. Five-Subtype Conversational Taxonomy

```
+-------------------------------------------------------------------------------------------------+
|                                CONVERSATIONAL DATA TAXONOMY                                     |
+-------------------------------------------------------------------------------------------------+
          |
          +---> Subtype A: Ordinary Conversational Text (Single-turn, casual social, colloquial)
          |
          +---> Subtype B: Multi-turn Dialogue (Interactive user/assistant turns, task trees)
          |
          +---> Subtype C: Preference Pairs (Binary chosen vs rejected completions, rankings)
          |
          +---> Subtype D: Rejected / Red-Team Responses (Adversarial probes, jailbreaks, toxic)
          |
          +---> Subtype E: Literary Theatrical Dialogue (Stage plays, dramatic scripts, turn-taking)
```

### 2.1 Subtype A: Ordinary Conversational Text
- **Definition**: Unstructured, single-turn or loosely coupled conversational exchanges, colloquial comments, forum replies, and informal social messaging.
- **Key Characteristics**: Informal vocabulary, internet slang, abbreviations (`lol`, `idk`, `ngl`), emoji sequences, non-standard punctuation, and casual syntax.
- **Representative Corpora**: Curated social forum threads, clean blog comments, informal product reviews.

### 2.2 Subtype B: Multi-Turn Dialogue
- **Definition**: Structured, sequential multi-party conversations exhibiting contextual continuity across multiple alternating turns.
- **Key Characteristics**: Explicit speaker roles (`User`, `Assistant`, `Agent`), conversational context tracking, goal-oriented task resolution, and long-context dependencies.
- **Representative Corpora**: `SRC-CV-03` (OpenAssistant OASST1 accepted message trees), `SRC-CV-05` (MultiWOZ 2.4 task dialogues).

### 2.3 Subtype C: Preference Pairs
- **Definition**: Explicitly paired completions evaluating model response quality given an identical conversational prompt: one labeled `chosen` (preferred, high quality) and one labeled `rejected` (sub-optimal or dispreferred).
- **Key Characteristics**: Comparative evaluation metadata, ranking scores, stylistic divergence, helpfulness differentials.
- **Representative Corpora**: `SRC-CV-04` (Anthropic HH-RLHF helpfulness preference splits).

### 2.4 Subtype D: Rejected / Red-Team Responses
- **Definition**: Conversational prompts and completions elicited during deliberate adversarial safety evaluations, red-teaming exercises, and jailbreak probes.
- **Key Characteristics**: Contains severe toxic discourse, hate speech, dangerous instructions, cyberattack prompts, or discriminatory language specifically designed to test model safety guardrails.
- **Representative Corpora**: `SRC-CV-04` (Anthropic HH-RLHF harmlessness red-team evaluation splits).

### 2.5 Subtype E: Literary Theatrical Dialogue
- **Definition**: Published dramatic plays, stage scripts, and theatrical dialogues authored with formal turn-taking notation (`CHARACTER: Dialogue`).
- **Key Characteristics**: High lexical diversity, archaic and classical dramatic prose, grammatically structured dialogue turns, zero PII, zero modern platform terms-of-service encumbrances.
- **Representative Corpora**: `SRC-CV-06` (Project Gutenberg Dramatic Plays: Shakespeare, Oscar Wilde, George Bernard Shaw, Sheridan).

---

## 3. Pipeline Allocation & Boundary Security Matrix

To preserve tokenizer integrity, security boundaries, and evaluation fairness, each conversational subtype is strictly allocated to specific model development pipelines:

| Subtype | Conversational Format | Tokenizer Pre-Training Allocation | Tokenizer Evaluation Allocation | Separate Alignment Allocation | Core Governance & Security Rationale |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **A** | **Ordinary Conversational** | **PERMITTED** | **PERMITTED** | N/A | Essential for vocabulary representation of informal words, contractions, and internet slang. |
| **B** | **Multi-Turn Dialogue** | **PERMITTED** | **PERMITTED** | N/A | Tests structural tokens (`<|user|>`, `<|assistant|>`), turn transitions, and long-context sequence tiers (Tiers 2–4). |
| **C** | **Preference Pairs** | **STRICTLY PROHIBITED** | **RESTRICTED** | **PRIMARY ALLOCATION** | Including preference metadata in tokenizer pre-training skews token frequencies and causes severe benchmark contamination. |
| **D** | **Rejected / Red-Team** | **ABSOLUTELY BANNED** | **RESTRICTED (ISOLATED)** | **PRIMARY ALLOCATION** | **Critical Security Rule**: Training tokenizers on toxic/adversarial text creates dedicated vocabulary pieces for slurs, exploits, and hate tokens. |
| **E** | **Literary Theatrical** | **PERMITTED** | **PERMITTED** | N/A | Completely unencumbered public domain baseline for testing multi-party dialogic structure without PII or legal risk. |

---

## 4. Deep-Dive: The Red-Team & Adversarial Exclusion Rule

> [!CAUTION]
> **TOKENIZER SAFETY MANDATE (SUBTYPE D)**: Under no circumstances may Subtype D (Rejected / Red-Team Responses) be ingested into candidate tokenizer training corpora.

### Technical & Safety Rationale:
1. **Vocabulary Poisoning**: Tokenizer algorithms (BPE and Unigram) merge frequent character sequences. Ingesting adversarial corpora causes the tokenizer to allocate precious vocabulary slots (from the 32,768 budget) to explicit slurs, toxic phrases, or attack payloads.
2. **Embedding Space Distortion**: If the tokenizer creates dedicated atomic tokens for harmful words, downstream Transformer embeddings for those concepts become localized and easily triggered, degrading safety fine-tuning.
3. **Decontamination Invariant**: Subtype D must be preserved in strict isolation for downstream **Alignment & Safety Evaluation** to objectively audit whether the trained model refuses harmful requests.

---

## 5. Source-to-Subtype Allocation for IGRIS Sources

| Source ID | Dataset Name | Subtype(s) Present | Tokenizer Pre-Training Role | Tokenizer Evaluation Role | Alignment Evaluation Role |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **SRC-CV-01** | DailyDialog | Subtypes A, B | **REJECTED** | **REJECTED** | **REJECTED** (Non-commercial clause) |
| **SRC-CV-02** | OpenSubtitles | Subtypes A, B | **REJECTED** | **REJECTED** | **REJECTED** (Copyright infringement) |
| **SRC-CV-03** | OpenAssistant (OASST1) | Subtypes A, B | Eligible (Clean trees) | **Primary Benchmark** (Multi-turn) | Optional (Reward data) |
| **SRC-CV-04** | Anthropic HH-RLHF | Subtypes C, D | **PROHIBITED** | **Evaluation Only** (Chosen split) | **Primary Benchmark** (Chosen vs Rejected) |
| **SRC-CV-05** | MultiWOZ 2.4 | Subtype B | Eligible (Task turns) | **Primary Benchmark** (Task dialog) | N/A |
| **SRC-CV-06** | Project Gutenberg Theatrical | Subtype E | Eligible (Public domain) | **Primary Benchmark** (Clean turns) | N/A |

---

## 6. Architectural Conclusion

1. **Category 9 Benchmark Stratification**:
   - Tokenizer evaluation for Category 9 will draw strictly from:
     - **Subtype B (Multi-turn)**: `SRC-CV-03` (OpenAssistant) & `SRC-CV-05` (MultiWOZ 2.4)
     - **Subtype E (Literary Theatrical)**: `SRC-CV-06` (Project Gutenberg Theatrical)
2. **Post-Training Alignment Isolation**:
   - `SRC-CV-04` (Anthropic HH-RLHF Subtypes C & D) is officially segregated and held in reserve for post-training alignment and safety benchmarking.
