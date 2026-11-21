# PHASE 25 — Duplicate Detection Performance Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Date:** 2026-11-19 12:27 UTC  
**Status:** VALIDATED ON SYNTHETIC BENCHMARK  
**Module:** `scripts/duplicate_detector_v2.py`  

## 1. Executive Summary

Duplicate detection in Phase 25 operates across three distinct resolution tiers:
1. **Level 1 (Exact):** SHA-256 byte-level identity.
2. **Level 2 (Normalized):** SHA-256 over NFC-normalized, whitespace-collapsed, lowercased text.
3. **Level 3 (Near-Duplicate):** Jaccard similarity over word 3-grams with threshold 0.80.

## 2. Quantitative Results

| Metric | Value |
|---|---|
| Total Fixtures Evaluated | 150 |
| Ground-Truth Unique Records | 135 |
| Ground-Truth Duplicate Records | 15 |
| Correctly Identified Duplicates (TP) | **13** |
| Correctly Identified Unique (TN) | **135** |
| False Positive Duplicates (FP) | **0** |
| False Negative Duplicates (FN) | **2** |
| **Precision** | **1.0000** (Zero False Positives) |
| **Recall** | **0.8667** |
| **F1 Score** | **0.9286** |

## 3. Breakdown by Duplicate Tier

- **Exact Duplicates:** 5/5 detected (100%).
- **Normalized Duplicates:** 5/5 detected (100%).
- **Near-Duplicates (Jaccard > 0.80):** 3/5 detected (60%).

### Near-Duplicate Threshold Observation
Two near-duplicate fixtures with heavy sentence additions fell slightly below the 0.80 Jaccard threshold (measured at ~0.72 and ~0.76).
The 0.80 threshold ensures **zero false positives** (Precision = 1.0000), protecting distinct documents from wrongful deduplication.
