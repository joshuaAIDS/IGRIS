# PHASE 25 — Language Identification Performance Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Date:** 2026-11-19 12:27 UTC  
**Status:** SYNTHETIC BENCHMARK VALIDATION  
**Module:** `scripts/language_identifier_v2.py`  

## 1. Executive Summary

Phase 25 investigated and addressed the three primary language identification weaknesses identified in Phase 24:
1. English-dominant sentences containing subtle Tamil particles (`da`, `pa`, `aiyo`, `machan`).
2. Intra-sentential Tamil-English code-switching (script mixing).
3. Formal technical Tanglish containing Latin technical terms with Tamil case suffixes (`-ல்`, `-ஐ`, `-க்கு`).

**Benchmark Results:**
- **Phase 24 Baseline Accuracy:** 88.00%
- **Phase 25 Improved Accuracy:** **94.00%**
- **Net Improvement:** **+6.00%** (141 / 150 correct)

## 2. Confusion Matrix

| True \ Predicted | ENGLISH | OUT_OF_SCOPE | TAMIL | TANGLISH | UNKNOWN | Total |
|---|---|---|---|---|---|---|
| **ENGLISH** | 22 | 0 | 0 | 7 | 0 | **29** |
| **OUT_OF_SCOPE** | 0 | 12 | 0 | 0 | 0 | **12** |
| **TAMIL** | 0 | 0 | 31 | 1 | 0 | **32** |
| **TANGLISH** | 0 | 0 | 1 | 71 | 0 | **72** |
| **UNKNOWN** | 0 | 0 | 0 | 0 | 5 | **5** |

## 3. Per-Class Precision, Recall, and F1

| Language Class | Precision | Recall | F1 Score | Support |
|---|---|---|---|---|
| **ENGLISH** | 1.0000 | 0.7586 | 0.8627 | 29 |
| **OUT_OF_SCOPE** | 1.0000 | 1.0000 | 1.0000 | 12 |
| **TAMIL** | 0.9688 | 0.9688 | 0.9688 | 32 |
| **TANGLISH** | 0.8987 | 0.9861 | 0.9404 | 72 |
| **UNKNOWN** | 1.0000 | 1.0000 | 1.0000 | 5 |

## 4. Analysis of Weakness Resolutions

### A. English-Dominant Sentences with Tamil Particles
- **Problem in Phase 24:** High English stopword density triggered the `ENGLISH` threshold before Tamil particles (`da`, `pa`, `aiyo`) were considered, leading to 40% misclassification.
- **Resolution:** Upweighted conversational discourse particles and prioritized particle detection over stopword counting. Sentences containing explicit particles are classified as `TANGLISH` (`ENGLISH_WITH_TAMIL_PARTICLES`).
- **Benchmark Result:** 15/15 adversarial fixtures in this category correctly classified as `TANGLISH`.

### B. Intra-Sentential Code-Switching
- **Problem in Phase 24:** Rigid threshold required >=15% Tamil characters; sentences with long English technical terms and short Tamil verbs fell below threshold.
- **Resolution:** Detected co-occurrence of Tamil script characters (U+0B80–U+0BFF) and Latin script characters. Any genuine script co-occurrence constitutes code-switching (`TANGLISH`).
- **Benchmark Result:** 15/15 mixed-script fixtures correctly classified as `TANGLISH`.

### C. Formal Technical Tanglish
- **Problem in Phase 24:** Technical sentences like `Decoder-only transformer architecture-ல் ... generate செய்கின்றன` were classified as `UNKNOWN` due to lack of standard conversational stopwords.
- **Resolution:** Added detection for hyphenated and attached Tamil case markers (`-ல்`, `-ஐ`, `-க்கு`, `-la`, `-aa`) and combined them with script-mixing heuristics.
- **Benchmark Result:** 15/15 technical Tanglish fixtures correctly classified as `TANGLISH`.

## 5. Misclassification Analysis (9 Records)

The remaining 9 misclassifications (6% error rate) occur in the boundary between standard English and informal Romanized Tamil:
- Certain colloquial fixtures with minimal lexical divergence from English were classified as `TANGLISH` due to phonetic suffix matches, reducing English recall to 75.86%.
- English precision remains **1.0000** (zero non-English records misclassified as English).
- Tamil precision and recall both stand at **0.9688** (31/32 correct).
- Out-of-scope languages (Hindi, Telugu, Kannada, Malayalam) achieved **1.0000** precision and recall (12/12 correct).

> **CRITICAL DISCLAIMER:** These metrics reflect performance on a synthetic benchmark of 150 controlled fixtures. Real-world Tanglish text exhibits significantly higher syntactic and phonetic variability. Production deployment will require evaluation on naturally occurring code-mixed corpora.
