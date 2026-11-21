# PHASE 25 — Reproducibility & Determinism Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Date:** 2026-11-19 12:27 UTC  
**Status:** VERIFIED DETERMINISTIC  

## 1. Objective

Verify that the Phase 25 processing pipeline is strictly deterministic, order-independent across records, and produces bit-for-bit identical manifests when re-executed.

## 2. Test Execution

Two full pipeline runs were conducted on the 150 benchmark records:
1. **Run 1:** Fresh pipeline instance processing records `P25-SYN-0001` through `P25-SYN-0150`.
2. **Run 2:** State reset (`pipeline.reset_state()`) followed by re-execution on identical inputs.

## 3. Verification Results

| Verification Criterion | Expected | Observed | Status |
|---|---|---|---|
| Processed Record Count | 150 | 150 | PASS |
| Record ID Order Stability | Sequential | Sequential | PASS |
| SHA-256 Normalized Text Invariance | Identical | 100% Identical | PASS |
| Language Classification Invariance | Identical | 100% Identical | PASS |
| Quality Verdict Invariance | Identical | 100% Identical | PASS |
| Duplicate Detection Invariance | Identical | 100% Identical | PASS |
| Final Action Invariance | Identical | 100% Identical | PASS |
| Field-by-Field Mismatches | **0** | **0** | **PASS** |

## 4. Conclusion

The Phase 25 pipeline demonstrates **100% deterministic reproducibility**. All cryptographic digests, classification decisions, and rejection tags are fully reproducible.
