# IGRIS Tokenizer Generalization Report
## Independent Benchmark of Candidate A and Experimental Candidate A on 3,000 Unseen Records

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Status:** **`GENERALIZATION_PASS`**  

---

## 1. Executive Summary

An independent, large-scale generalization benchmark was conducted evaluating the production-selected **Original Candidate A** tokenizer against the **Experimental Candidate A** tokenizer. The evaluation was performed on a brand new, uncontaminated corpus of **3,000 synthetic records** (1,000 Tamil, 1,000 English, 1,000 Tanglish) spanning five functional categories: Conversational, Formal, Educational, Technical, and Long-form.

### Key Benchmark Findings:
1. **Strong Generalization of Compression Efficiency (-45.19% Overall):**
   * Experimental Candidate A reduced total emitted tokens across the 3,000 documents from **1,145,340** down to **627,746**, achieving a **45.19% overall sequence length reduction**.
   * Average fertility per word improved from **8.31 tokens/word** (Original A) to **4.56 tokens/word** (Experimental A).
2. **Consistent Trilingual Improvements Across All Approved Languages:**
   * **English (N=1,000):** Fertility dropped from **6.81** to **2.93 tokens/word** (**-57.03% token reduction**).
   * **Tanglish (N=1,000):** Fertility dropped from **8.34** to **4.45 tokens/word** (**-46.67% token reduction**).
   * **Tamil (N=1,000):** Fertility dropped from **10.91** to **7.53 tokens/word** (**-31.02% token reduction**).
3. **Robust Performance Across All Functional Categories:**
   * Conversational: **-48.91%** | Formal: **-38.77%** | Educational: **-47.04%** | Technical: **-42.67%** | Long-form: **-47.37%**.
4. **Enhanced Detokenization Throughput (+37.3% Faster):**
   * Raw decode throughput increased from **1,056,209 words/s** to **1,683,234 words/s** due to shorter sequence lengths.
5. **Zero Cryptographic, Structural, or Round-Trip Regressions:**
   * 100.0% round-trip decode/encode accuracy on all 3,000 records.
   * Structural special tokens (`<|pad|>` through `<|assistant|>`) remain pinned at IDs 0–11.
   * Unknown token rate remained at **0.00%** via byte-level BPE fallback.

---

## 2. Core Generalization Metrics

The high-level benchmark results are recorded in [TOKENIZER_GENERALIZATION_METRICS.csv](file:///C:/IGRIS/TOKENIZER_GENERALIZATION_METRICS.csv):

| Language Subset | Records | Words | Cand A Tokens | Cand A Fert (tok/w) | Exp A Tokens | Exp A Fert (tok/w) | Cand A Seq Median | Exp A Seq Median | Exp A Seq Max | Token Reduction (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **FULL_CORPUS** | **3,000** | **137,800** | **1,145,340** | **8.3116** | **627,746** | **4.5555** | **398.0** | **212.0** | **684** | **45.19%** |
| **TAMIL** | 1,000 | 45,600 | 497,616 | 10.9126 | 343,264 | 7.5277 | 406.0 | 290.0 | 684 | **31.02%** |
| **ENGLISH** | 1,000 | 48,000 | 326,812 | 6.8086 | 140,444 | 2.9259 | 471.0 | 205.0 | 461 | **57.03%** |
| **TANGLISH** | 1,000 | 44,200 | 320,912 | 8.3412 | 144,038 | 4.448 | 326.5 | 195.0 | 444 | **46.67%** |

---

## 3. Functional Category Breakdown

Performance across document genres is recorded in [TOKENIZER_CATEGORY_BREAKDOWN.csv](file:///C:/IGRIS/TOKENIZER_CATEGORY_BREAKDOWN.csv):

| Category | Records | Total Words | Cand A Fert (tok/w) | Exp A Fert (tok/w) | Cand A Seq Median | Exp A Seq Median | Token Reduction (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Conversational** | 600 | 18,600 | 6.7872 | 3.4675 | 203.0 | 89.0 | **48.91%** |
| **Formal** | 600 | 25,200 | 8.7968 | 5.3865 | 336.0 | 195.0 | **38.77%** |
| **Educational** | 600 | 26,400 | 7.5046 | 3.9748 | 400.0 | 211.5 | **47.04%** |
| **Technical** | 600 | 25,800 | 9.1207 | 5.2289 | 404.0 | 250.0 | **42.67%** |
| **Long-form** | 600 | 41,800 | 8.5457 | 4.498 | 880.5 | 446.0 | **47.37%** |

---

## 4. Orthographic Script Breakdown

Performance across surface scripts is recorded in [TOKENIZER_SCRIPT_GENERALIZATION.csv](file:///C:/IGRIS/TOKENIZER_SCRIPT_GENERALIZATION.csv):

| Script Form | Records | Words | Cand A Fert (tok/w) | Exp A Fert (tok/w) | Cand A Seq Median | Exp A Seq Median | Token Reduction (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **TAMIL_SCRIPT** | 1,000 | 45,600 | 10.9126 | 7.5277 | 406.0 | 290.0 | **31.02%** |
| **LATIN_SCRIPT** | 1,400 | 62,600 | 6.7115 | 2.8559 | 331.0 | 163.5 | **57.45%** |
| **MIXED_SCRIPT** | 600 | 29,600 | 9.1604 | 5.1936 | 398.0 | 261.0 | **43.3%** |

---

## 5. Active Vocabulary Footprint & Subword Utilization

* **Emitted Token IDs on 3,000 Records:**
  * Original Candidate A: **152 distinct token IDs** (0.46% of 32,768).
  * Experimental Candidate A: **1,117 distinct token IDs** (3.41% of 32,768).
* **Text Coverage:** **100.00%** for both tokenizers via byte-level BPE fallback.
* **Interpretation:** Experimental Candidate A activates over 63% of its 1,755 learned merges on unseen text, showing that its learned subwords generalize beyond the training sentences without causing fragmentation.

---

## 6. Runtime Throughput Benchmark

Timed over 5 warm-up passes and 5 full-corpus repetitions:
* **Encode Speed:**
  * Candidate A: **226683.7 words/s**
  * Experimental Candidate A: **244564.9 words/s** (**+7.3%**)
* **Decode Speed:**
  * Candidate A: **1056209.2 words/s**
  * Experimental Candidate A: **1683234.0 words/s** (**+37.3% faster**)

---

## 7. Deliverables Index

All 8 evaluation deliverables have been generated and mirrored:

1. [TOKENIZER_GENERALIZATION_REPORT.md](file:///C:/IGRIS/TOKENIZER_GENERALIZATION_REPORT.md)
2. [INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv](file:///C:/IGRIS/INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv)
3. [TOKENIZER_GENERALIZATION_METRICS.csv](file:///C:/IGRIS/TOKENIZER_GENERALIZATION_METRICS.csv)
4. [TOKENIZER_CATEGORY_BREAKDOWN.csv](file:///C:/IGRIS/TOKENIZER_CATEGORY_BREAKDOWN.csv)
5. [TOKENIZER_SCRIPT_GENERALIZATION.csv](file:///C:/IGRIS/TOKENIZER_SCRIPT_GENERALIZATION.csv)
6. [TOKENIZER_CONTAMINATION_AUDIT.md](file:///C:/IGRIS/TOKENIZER_CONTAMINATION_AUDIT.md)
7. [TOKENIZER_VOCABULARY_METRIC_RECONCILIATION.md](file:///C:/IGRIS/TOKENIZER_VOCABULARY_METRIC_RECONCILIATION.md)
8. [verify_tokenizer_generalization.py](file:///C:/IGRIS/verify_tokenizer_generalization.py)

---

## 8. Governance Recommendation & Decision Status

### Finding:
Experimental Candidate A demonstrated superior compression efficiency (**-45.19% sequence length reduction**) and faster decode throughput (**+37.3%**) across 3,000 unseen independent records without regressions or lexical collapse.

### Governance Directive:
* **No Promotion:** Experimental Candidate A remains quarantined in its separate experimental directory.
* **Production Tokenizer Invariant:** Original Candidate A (`ac7e18b1...`) remains the official selected production tokenizer.
* **Pretraining Status:** `LOCKED`.
* **Zero Production Data / Zero Cloud Spend:** `$0.00`.

**Final Decision Status:** **`GENERALIZATION_PASS`**  
Standing by for sole project owner review.
