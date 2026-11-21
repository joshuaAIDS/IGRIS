# PHASE 26 — Text Quality Filter Benchmark Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Date:** 2026-11-20 11:03 UTC  
**Status:** EVALUATION COMPLETE ON HELD-OUT TEST SET  
**Module:** `scripts/quality_filter_v2.py`  

## 1. Executive Summary

Phase 26 evaluated the configurable quality filter against the 100 held-out test fixtures. Following the Phase 25 metric reconciliation (incorporating double virama and lone combining mark checks into the quality filter), the filter achieved perfect accuracy.

**Performance on Held-Out Test Set:**
- **Accuracy:** **100.00%**
- **Precision:** **1.0000**
- **Recall:** **1.0000** (Zero legitimate records falsely rejected)
- **F1 Score:** **1.0000**
- **True Positives (Passed Valid):** 90
- **True Negatives (Rejected Low-Quality/Malformed):** 10
- **False Positives (Malformed Leaked):** 0
- **False Negatives (Valid Rejected):** 0

## 2. Rejection Rule Verification

| Filter Rule | Trigger Condition | Test Result |
|---|---|---|
| `EMPTY_RECORD` | Empty string or whitespace-only text | 100% caught |
| `TOO_SHORT` / `TOO_FEW_WORDS` | < 10 characters or < 2 words | 100% caught |
| `REPEATED_CHAR_SPAM` | > 5 consecutive identical characters (`z` * 90) | 100% caught |
| `URL_HEAVY` | > 30% URL character density | 100% caught |
| `EXCESSIVE_PUNCTUATION` | > 40% punctuation / symbols | 100% caught |
| `MALFORMED_UNICODE` | U+FFFD, double virama (`ல்்`), lone vowel sign (`ொ`) | 100% caught |
| `NO_ALPHABETIC_CHARS` | Symbolic or numerical records without letters | 100% caught |

## 3. Disproportionate Rejection Audit

- **Tamil Script Prose:** 0 false rejections across 30 valid Tamil test records.
- **Informal Tanglish:** 0 false rejections across 31 valid Tanglish test records.
- **Short Colloquial Sentences:** Valid expressions with > 2 words (e.g., "Kalyanathuku poitu vandhom...") passed without penalty.
