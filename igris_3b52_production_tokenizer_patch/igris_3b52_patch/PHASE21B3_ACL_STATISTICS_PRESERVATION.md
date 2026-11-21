# PHASE 21B3 — ACL 2023 STATISTICS PRESERVATION
## Authoritative Upstream Paper Statistics vs Physical Repository Measurements

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3  
**Scope:** Factual Statistics Preservation & Invariant Audit  

---

## 1. Authoritative Upstream Publication Baseline

The official token statistics published in Table 3 of the ACL 2023 paper (Doddapaneni et al., *"Towards Leaving No Indic Language Behind: Building Monolingual Corpora, Benchmark and Models for Indic Languages"*) represent the authoritative scientific baseline for IndicCorp v2:

```
+-----------+----------+--------------------+-----------------------+-----------------------------+
| Source ID | Language | ISO 639-1 Code     | Script (ISO 15924)    | Published ACL 2023 Tokens   |
+-----------+----------+--------------------+-----------------------+-----------------------------+
| SRC-TM-01 | Tamil    | ta                 | Tamil (Taml)          | 476 Million                 |
| SRC-HI-01 | Hindi    | hi                 | Devanagari (Deva)     | 6,107 Million               |
| SRC-OI-01 | Telugu   | te                 | Telugu (Telu)         | 731 Million                 |
| SRC-OI-02 | Malayalam| ml                 | Malayalam (Mlym)      | 931 Million                 |
| SRC-OI-03 | Kannada  | kn                 | Kannada (Knda)        | 875 Million                 |
| SRC-OI-04 | Bengali  | bn                 | Bengali (Beng)        | 926 Million                 |
| SRC-OI-05 | Gujarati | gu                 | Gujarati (Gujr)       | 901 Million                 |
+-----------+----------+--------------------+-----------------------+-----------------------------+
| TOTAL     | 7 Langs  | 7 Languages        | 6 Native Scripts      | 10,947 Million (~10.95 B)   |
+-----------+----------+--------------------+-----------------------+-----------------------------+
```

$$\sum_{i=1}^7 	ext{Tokens}_i = 476 + 6107 + 731 + 931 + 875 + 926 + 901 = 10,947	ext{ Million Tokens}$$

---

## 2. Invariant: Paper Statistics $
eq$ Physical Object Sizes

> [!IMPORTANT]
> Published paper token counts are **scientific measurements reported in academic literature**, NOT direct measurements of the raw physical files residing on Hugging Face.

1. **Tokenizer Discrepancy:** The token counts reported in Doddapaneni et al. (ACL 2023) were generated using the **IndicNLP / SentencePiece tokenizer** featuring a massive **250,000 subword vocabulary** optimized for IndicBERT v2.
2. **Pre-Processing Filtering:** The token counts in Table 3 were measured after document-level and sentence-level language identification (LID threshold > 0.85) and cleaning.
3. **Physical Repository Files:** The raw `.txt` files in `ai4bharat/IndicCorpV2` contain the full text crawl (~183.7 GB total).
4. **Mandatory Prohibition:** IGRIS governance strictly prohibits inferring actual usable token counts, sentence counts, or deduplication yields from raw repository object sizes without empirical execution.