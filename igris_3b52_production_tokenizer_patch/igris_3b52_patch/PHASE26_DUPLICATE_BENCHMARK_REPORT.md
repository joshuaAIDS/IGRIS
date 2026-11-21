# PHASE 26 — Duplicate Detection Benchmark Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Date:** 2026-11-20 11:03 UTC  
**Status:** EVALUATION COMPLETE ON HELD-OUT TEST SET  
**Module:** `scripts/duplicate_detector_v2.py`  

## 1. Executive Summary

Phase 26 conducted a two-stage evaluation of the multi-level duplicate detection engine:
1. **Validation Set Parameter Search:** Grid search across Jaccard thresholds (0.70 to 0.90) to optimize the near-duplicate boundary without consulting test set labels.
2. **Blind Held-Out Test Set Evaluation:** Evaluated at the selected threshold on the unseen test set.

## 2. Validation Set Threshold Grid Search

| Jaccard Threshold | Precision | Recall | F1 Score | TP | TN | FP | FN | Selection Decision |
|---|---|---|---|---|---|---|---|---|
| **0.7** | 1.0000 | 1.0000 | 1.0000 | 5 | 94 | 0 | 0 | **SELECTED (OPTIMAL)** |
| **0.75** | 1.0000 | 0.8000 | 0.8889 | 4 | 94 | 0 | 1 | Rejected |
| **0.8** | 1.0000 | 0.8000 | 0.8889 | 4 | 94 | 0 | 1 | Rejected |
| **0.85** | 1.0000 | 0.8000 | 0.8889 | 4 | 94 | 0 | 1 | Rejected |
| **0.9** | 1.0000 | 0.8000 | 0.8889 | 4 | 94 | 0 | 1 | Rejected |

### Threshold Selection Rationale
On the validation set, threshold **0.70** achieved **F1 = 1.0000** (5/5 duplicates detected, 0 false positives). Higher thresholds (0.75 – 0.90) missed 1 near-duplicate record whose Jaccard similarity was ~0.72 due to appended phrases. Threshold 0.70 was selected for all downstream test evaluation.

## 3. Held-Out Test Set Performance (Threshold = 0.7)

| Metric | Measured Value | Standard Target | Status |
|---|---|---|---|
| True Positives (Duplicates Caught) | **5** | 5 | PASS |
| True Negatives (Unique Verified) | **95** | 95 | PASS |
| False Positives (Unique Wrongly Deduplicated) | **0** | 0 | **PERFECT (100% PRECISION)** |
| False Negatives (Duplicates Missed) | **0** | 0 | **PERFECT (100% RECALL)** |
| **Precision** | **1.0000** | 1.0000 | **PASS** |
| **Recall** | **1.0000** | 1.0000 | **PASS** |
| **F1 Score** | **1.0000** | 1.0000 | **PASS** |

## 4. Multi-Tier Resolution Breakdown

- **Level 1 (Exact SHA-256):** 2/2 detected (100%).
- **Level 2 (Normalized SHA-256):** 2/2 detected (100% across whitespace and uppercase variations).
- **Level 3 (Near-Duplicate Word 3-grams):** 1/1 detected (100% on appended phrase variant).
