# PHASE 26 — Language Identification Benchmark Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Date:** 2026-11-20 11:03 UTC  
**Status:** EVALUATION COMPLETE ON HELD-OUT TEST SET  
**Module:** `scripts/language_identifier_v2.py`  

## 1. Executive Summary

Phase 26 conducted a rigorous, blind evaluation of the enhanced 5-label Language Identification engine across the 100-record held-out test set.
Following development-set tuning to eliminate false-positive suffix matches on English technical prose, the engine achieved state-of-the-art performance on code-mixed and Dravidian targets.

**Benchmark Telemetry on Held-Out Test Set:**
- **Overall Accuracy:** **98.00%** (98 / 100 correct)
- **Macro Precision:** **0.9857**
- **Macro Recall:** **0.9269**
- **Macro F1 Score:** **0.9493**

## 2. Confusion Matrix on Held-Out Test Set

| True \ Predicted | ENGLISH | OUT_OF_SCOPE | TAMIL | TANGLISH | UNKNOWN | Total |
|---|---|---|---|---|---|---|
| **ENGLISH** | 26 | 0 | 0 | 0 | 0 | **26** |
| **OUT_OF_SCOPE** | 0 | 10 | 0 | 0 | 0 | **10** |
| **TAMIL** | 0 | 0 | 30 | 0 | 0 | **30** |
| **TANGLISH** | 1 | 0 | 0 | 30 | 0 | **31** |
| **UNKNOWN** | 1 | 0 | 0 | 0 | 2 | **3** |

## 3. Per-Class Precision, Recall, and F1

| Language Class | Precision | Recall | F1 Score | Support |
|---|---|---|---|---|
| **ENGLISH** | 0.9286 | 1.0000 | 0.9630 | 26 |
| **OUT_OF_SCOPE** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **TAMIL** | 1.0000 | 1.0000 | 1.0000 | 30 |
| **TANGLISH** | 1.0000 | 0.9677 | 0.9836 | 31 |
| **UNKNOWN** | 1.0000 | 0.6667 | 0.8000 | 3 |

## 4. Performance by Difficulty Tier

| Difficulty Tier | Total Records | Correct Predictions | Accuracy |
|---|---|---|---|
| **ADVERSARIAL** | 5 | 5 | **100.00%** |
| **EASY** | 42 | 40 | **95.24%** |
| **HARD** | 27 | 27 | **100.00%** |
| **MEDIUM** | 26 | 26 | **100.00%** |

## 5. Key Analytical Findings

1. **Perfect Recognition on Core Languages:**
   - **Tamil:** 30 / 30 correct (Precision = 1.0000, Recall = 1.0000, F1 = 1.0000).
   - **Out-of-Scope Languages:** 10 / 10 correct (100% rejection of Hindi, Telugu, Kannada, Malayalam).
   - **Tanglish:** 30 / 31 correct (Precision = 1.0000, Recall = 0.9677, F1 = 0.9836).
2. **Resolution of English False Positives:**
   - In Phase 25, 5 English challenge sentences were misclassified as Tanglish due to bare `-le` suffix matching (`reliable`, `multiple`, `decouple`).
   - In Phase 26, bare `-le`, `-la`, `-aa` were restricted to hyphenated clitics (`office-la`, `lazy-aa`) or standalone tokens.
   - All 6 English challenge sentences in the held-out test set were correctly recognized as `ENGLISH`.
3. **Analysis of the Two Mismatches:**
   - `P26-TEST-0046`: "Interview round romba tough-aa irunthuchu da, system design questions ellam depth-aa kettanga." (High technical English density with Tamil particles; predicted as `ENGLISH` instead of `TANGLISH`).
   - `P26-TEST-0093`: "z" * 90 (Repeated character spam; identified as `ENGLISH` by character script, but correctly caught and rejected by the downstream Quality Filter as `REPEATED_CHAR_SPAM`).

> **CRITICAL DISCLAIMER:** These metrics reflect performance on a controlled synthetic benchmark of 100 held-out test fixtures. Real-world Tanglish scraped from social media or conversational messaging exhibits higher orthographic entropy, non-standard spelling, and colloquial contractions. Production deployment will require evaluation on naturally occurring code-mixed corpora.
