# PHASE 23 — LANGUAGE SCOPE POLICY
## Formal Definition, Boundary Rules, and Exclusion Directives for IGRIS

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 23  
**Status:** FORMALLY ADOPTED & STRICTLY ENFORCED  

---

## 1. Updated Project Language Scope

By formal directive of the Project Owner, the language scope of the IGRIS pretraining corpus and model capability has been narrowed from generic Indic-multilingual coverage to exactly **three approved language categories**:

1. **Tamil (`ta` / `TAMIL`):**
   - Modern Standard Tamil, literary Tamil, news reporting, formal prose, and conversational Tamil expressed in the standard Tamil script (`U+0B80`–`U+0BFF`).
2. **English (`en` / `ENGLISH`):**
   - Standard English, technical prose, engineering specifications, dialogue, and reference documentation.
3. **Tanglish (`ta-Latn` / `TANGLISH`):**
   - Tamil-English code-mixed and code-switched text, comprising:
     - Tamil words and sentences expressed in Roman script (Latin script phonetics).
     - English loan words and phrases embedded within Tamil grammatical structures.
     - Tamil colloquial expressions embedded within English conversational sentences.
     - Natural bidirectional intra-sentential and inter-sentential code-switching typical of conversational digital discourse in Tamil Nadu and the global Tamil diaspora.

---

## 2. Explicit Language Exclusion Directives

All languages and dialects outside the three approved categories are **STRICTLY EXCLUDED** from dataset acquisition, cleaning, tokenization evaluation, and pretraining.

### Explicitly Excluded Languages:
- **Hindi (`hi`):** All IndicCorp v2 Hindi shards (`data/hi-1.txt`, `data/hi-2.txt`, `data/hi-3.txt`), Hindi Wikipedia dumps, IIT Bombay parallel corpora, and Hindi social media texts.
- **Telugu (`te`):** IndicCorp v2 Telugu (`data/te.txt`).
- **Malayalam (`ml`):** IndicCorp v2 Malayalam (`data/ml.txt`).
- **Kannada (`kn`):** IndicCorp v2 Kannada (`data/kn.txt`).
- **Bengali (`bn`):** IndicCorp v2 Bengali (`data/bn.txt`).
- **Gujarati (`gu`):** IndicCorp v2 Gujarati (`data/gu.txt`).
- **All other non-target languages:** Urdu, Marathi, Punjabi, Odia, Assamese, Sanskrit, French, German, Spanish, etc.

### Multilingual Web Corpus Ineligibility Rule:
Generic multilingual datasets (e.g. mC4, Common Crawl raw dumps, FLORES-200, OpenSubtitles) are **NOT** eligible for acquisition merely because they contain a minor fraction of Tamil or English. Ingesting unpartitioned multilingual dumps introduces language contamination and breaches the approved scope.

---

## 3. Tokenizer Governance Under Narrowed Scope

The project tokenizer configuration remains frozen:
- **Selected Tokenizer:** Candidate A (ByteLevel BPE, vocabulary size $V=32,768$, 12 structural tokens pinned at IDs 0–11).
- **Cryptographic Hash:**
  `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- **Candidate B Hash:**
  `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
- **Scope Alignment:** Candidate A's byte-fallback ByteLevel BPE tokenizer natively encodes:
  1. UTF-8 Tamil bytes (`0xE0 0xAE ...` to `0xE0 0xAF ...`).
  2. ASCII English bytes (`0x20` to `0x7E`).
  3. Romanized Tamil (Tanglish) phonemic sequences.
  No tokenizer retraining, vocabulary modification, or structural token alteration is authorized or required.

---

## 4. Enforcement Mechanisms

1. **Ingress Filtering:** Any prospective dataset containing non-target languages must be partitioned prior to ingress or filtered with FastText language identification (`lid.176.bin`) retaining only `ta`, `en`, and code-mixed `ta-Latn`.
2. **Quota and Storage Impact:** Narrowing the scope from 7 Indic languages (183.70 GB raw) to Tamil (30.50 GB raw) plus curated English and Tanglish sources drastically reduces raw storage demand, eliminating the 75.90 GB Hindi corpus and other non-target subsets.
