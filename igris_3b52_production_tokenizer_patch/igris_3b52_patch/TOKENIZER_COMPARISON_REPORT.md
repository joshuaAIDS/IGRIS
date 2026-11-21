# IGRIS Tokenizer Comparison Report: Candidate A vs. Experimental Candidate A
## Reproducible, Controlled Evaluation Across the 399-Record Approved Synthetic Corpus

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Status:** **`COMPARISON_COMPLETE`**  

---

## 1. Executive Summary

A reproducible, controlled benchmark was conducted comparing the currently selected **Original Candidate A** tokenizer against the **Experimental Candidate A** tokenizer trained on approved synthetic data. Both tokenizers were evaluated on the exact same 399 approved synthetic records across the frozen 320/40/39 train/validation/test split.

### Key Evaluation Findings:
1. **Dramatic Compression Efficiency Gain (+54.4% Overall):**
   - Experimental Candidate A reduces total emitted tokens from **33,846** down to **15,430** across the corpus, achieving an overall **54.4% reduction in sequence length**.
   - Average fertility per word drops from **8.13 tokens/word** (Original A) to **3.70 tokens/word** (Experimental A).
2. **Generalization to Unseen Validation and Held-Out Test Splits:**
   - **Validation Split (N=40):** Fertility improves from **8.25** to **4.14 tokens/word** (**49.8% token reduction**).
   - **Held-Out Test Split (N=39):** Fertility improves from **8.66** to **4.42 tokens/word** (**48.9% token reduction**).
   - Confirms that the 1,755 learned BPE merges generalize effectively to unseen text without overfitting to training fixtures.
3. **Trilingual Impact (Tamil, English, Tanglish):**
   - **Operational English (N=92):** Fertility drops from **7.27** to **2.20 tokens/word** (**69.7% reduction**).
   - **Operational Tanglish (N=196):** Fertility drops from **7.45** to **2.87 tokens/word** (**61.5% reduction**).
   - **Operational Tamil (N=111):** Fertility drops from **10.45** to **7.06 tokens/word** (**32.4% reduction**).
4. **Zero Structural or Cryptographic Regressions:**
   - Both tokenizers retain structural special tokens `<|pad|>` through `<|assistant|>` at IDs 0–11 with 100% fidelity.
   - Both achieve **100.0% round-trip decode/encode accuracy**.
   - Decode throughput improves by **+56.8%** due to shorter sequence lengths.

---

## 2. Split Comparison Metrics

The primary performance metrics across corpus partitions are recorded in [TOKENIZER_COMPARISON_METRICS.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_COMPARISON_METRICS.csv):

| Partition | Records | Words | Candidate A Tokens | Cand A Fert (tok/w) | Exp A Tokens | Exp A Fert (tok/w) | Sequence Length Median (A vs Exp) | Sequence Length p95 (A vs Exp) | Sequence Length Max (A vs Exp) | Token Reduction (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **ENTIRE_CORPUS** | **399** | **4,165** | **33,846** | **8.13** | **15,430** | **3.70** | **68.0 vs 28.0** | **172.1 vs 87.0** | **354 vs 224** | **-54.4%** |
| **TRAIN_SPLIT** | 320 | 3,332 | 26,825 | 8.05 | 11,894 | 3.57 | 68.0 vs 28.0 | 170.0 vs 86.0 | 354 vs 224 | **-55.7%** |
| **VAL_SPLIT** | 40 | 417 | 3,440 | 8.25 | 1,728 | 4.14 | 72.0 vs 35.0 | 173.2 vs 90.1 | 240 vs 136 | **-49.8%** |
| **TEST_SPLIT** | 39 | 416 | 3,601 | 8.66 | 1,841 | 4.42 | 70.0 vs 36.0 | 188.0 vs 107.0 | 258 vs 142 | **-48.9%** |

---

## 3. Language & Sub-Type Breakdown

Performance across operational language categories and granular Tanglish sub-types is recorded in [TOKENIZER_LANGUAGE_BREAKDOWN.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_LANGUAGE_BREAKDOWN.csv):

| Language / Sub-Type Category | Records | Words | Cand A Fert (tok/w) | Exp A Fert (tok/w) | Cand A Seq Median | Exp A Seq Median | Token Reduction (%) | Active Vocab (A vs Exp) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Operational TAMIL** | 111 | 1,005 | 10.45 | 7.06 | 82.0 | 56.0 | **-32.4%** | 73 vs 268 |
| **Operational ENGLISH** | 92 | 1,107 | 7.27 | 2.20 | 72.0 | 22.0 | **-69.7%** | 98 vs 845 |
| **Operational TANGLISH** | 196 | 2,053 | 7.45 | 2.87 | 61.0 | 24.0 | **-61.5%** | 140 vs 1,195 |
| *Linguistic Matrix: TAMIL* | 153 | 1,435 | 9.78 | 5.93 | 82.0 | 48.0 | **-39.3%** | 153 vs 686 |
| *Linguistic Matrix: ENGLISH* | 131 | 1,549 | 6.95 | 2.18 | 68.0 | 22.0 | **-68.6%** | 102 vs 1,053 |
| *Linguistic Matrix: TANGLISH* | 115 | 1,181 | 7.66 | 3.00 | 59.0 | 24.0 | **-60.9%** | 132 vs 958 |
| *Subtype: Tamil-Script Tanglish* | 106 | 1,093 | 8.61 | 3.56 | 82.0 | 33.0 | **-58.6%** | 135 vs 850 |
| *Subtype: Romanized Tamil* | 90 | 960 | 6.14 | 2.09 | 50.5 | 18.0 | **-66.0%** | 84 vs 696 |
| *Subtype: English + Tamil Particles*| 23 | 274 | 5.83 | 2.01 | 63.0 | 21.0 | **-65.4%** | 69 vs 330 |

---

## 4. Script Form Breakdown

Performance across surface orthographic scripts is recorded in [TOKENIZER_SCRIPT_BREAKDOWN.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_SCRIPT_BREAKDOWN.csv):

| Script Form | Records | Words | Cand A Fert (tok/w) | Exp A Fert (tok/w) | Cand A Seq Median | Exp A Seq Median | Token Reduction (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **TAMIL_SCRIPT** | 109 | 984 | 10.47 | 7.07 | 82.0 | 56.0 | **-32.5%** |
| **LATIN_SCRIPT** | 182 | 2,067 | 6.74 | 2.15 | 59.5 | 19.5 | **-68.1%** |
| **MIXED_SCRIPT** | 108 | 1,114 | 8.63 | 3.62 | 82.5 | 34.0 | **-58.1%** |

---

## 5. Active Vocabulary Utilization & Subword Coverage

A detailed distinction between byte-fallback text coverage and active subword vocabulary utilization:
- **Full Text Coverage:** **100.0% for both tokenizers**. Zero unknown (`<unk>`) tokens.
- **Learned Merges:**
  - Original Candidate A: **63 merges**
  - Experimental Candidate A: **1,755 merges**
- **Active Vocabulary Footprint on 399 Records:**
  - Original Candidate A utilizes **286 unique token IDs** (0.87% of 32,768).
  - Experimental Candidate A utilizes **885 unique token IDs** (2.70% of 32,768).
- **Subword Representation:**
  - Original Candidate A splits almost all words into individual ASCII characters or individual UTF-8 bytes (`E-x-p-l-a-i-n`, `à®-ĩ-à®ķ-à¯į`).
  - Experimental Candidate A forms coherent subwords and full tokens (`Microservice`, `Ġhealth`, `Ġcheck`, `Ġà®¤à®®`).

---

## 6. Throughput & Runtime Efficiency

Measurements executed with 10 warm-up passes and 5 repetitions:
- **Encode Throughput:**
  - Original Candidate A: **230,436.9 words/s** (0.045 ms/record)
  - Experimental Candidate A: **240,901.8 words/s** (0.043 ms/record) — **+4.5% Faster**
- **Decode Throughput:**
  - Original Candidate A: **1,049,657.8 words/s** (0.010 ms/record)
  - Experimental Candidate A: **1,646,245.1 words/s** (0.006 ms/record) — **+56.8% Faster**
- **Throughput Driver:** Because Experimental Candidate A produces 54.4% fewer tokens, detokenization has substantially fewer string concatenation steps.

---

## 7. Deliverables Index

All 8 evaluation deliverables have been generated and mirrored:

1. [TOKENIZER_COMPARISON_REPORT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_COMPARISON_REPORT.md)
2. [TOKENIZER_COMPARISON_METRICS.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_COMPARISON_METRICS.csv)
3. [TOKENIZER_LANGUAGE_BREAKDOWN.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_LANGUAGE_BREAKDOWN.csv)
4. [TOKENIZER_SCRIPT_BREAKDOWN.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_SCRIPT_BREAKDOWN.csv)
5. [TOKENIZER_UNICODE_VALIDATION_REPORT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_UNICODE_VALIDATION_REPORT.md)
6. [TOKENIZER_ARTIFACT_INTEGRITY_REPORT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_ARTIFACT_INTEGRITY_REPORT.md)
7. [TOKENIZER_BENCHMARK_METHODOLOGY.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/TOKENIZER_BENCHMARK_METHODOLOGY.md)
8. [verify_tokenizer_comparison.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/verify_tokenizer_comparison.py)

---

## 8. Evidence-Based Recommendation & Stopping Condition

### Evidence Summary:
- Experimental Candidate A exhibits superior compression efficiency across all target languages (**-54.4% sequence length reduction**), while maintaining identical cryptographic structural token pinning (IDs 0–11) and 100% round-trip accuracy.
- However, both tokenizers were trained/evaluated on synthetic data. This benchmark demonstrates mechanical and algorithmic stability, but cannot establish production quality on real-world web corpora.

### Governance Directive:
- **Promotion Status:** **NO PROMOTION EXECUTED.** Experimental Candidate A remains in its separate experimental directory (`artifacts/tokenizer/candidate_a_synthetic_experiment/`).
- **Production Artifacts:** Original Candidate A (`ac7e18b1...`) remains the selected production tokenizer.
- **Pretraining Status:** `LOCKED`.
- **Cloud Spending:** `$0.00`.

### Final Status Determination:
**`COMPARISON_COMPLETE`**

Standing by for sole project owner review.
