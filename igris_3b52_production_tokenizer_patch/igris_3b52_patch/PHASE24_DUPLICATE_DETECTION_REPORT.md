# PHASE 24 — Duplicate Detection Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer
**Date:** 2026-11-19 17:43
**Module:** `scripts/duplicate_detector_v2.py`
**Status:** SYNTHETIC BENCHMARK ONLY

## 1. Architecture

### 1.1 Three-Level Detection

| Level | Method | Purpose |
|-------|--------|---------|
| Exact | SHA-256 hash | Identical text detection |
| Normalized | SHA-256 of NFC-normalized + whitespace-stripped | Whitespace/encoding variants |
| Near-duplicate | Jaccard similarity of word n-grams | Paraphrases and minor edits |

### 1.2 Configuration

| Parameter | Default |
|-----------|---------|
| Jaccard threshold | 0.85 |
| N-gram size | 3 (word trigrams) |

### 1.3 Output Structure

```python
@dataclass
class DupResult:
    is_duplicate: bool
    dup_type: str        # NONE | EXACT | NORMALIZED | NEAR_DUPLICATE
    matched_id: Optional[str]
    similarity: float
    notes: Optional[str]
```

## 2. Fixture Registration

| Metric | Value |
|--------|-------|
| Total fixtures registered | 100 |
| Unique | 100 |
| Duplicate within fixtures | 0 |

All 100 Phase 23A fixtures are unique (no duplicates among the fixture set).

## 3. Duplicate Injection Tests

| Test Type | Expected | Detected | Dup Type | Similarity | Correct |
|-----------|----------|----------|----------|------------|---------|
| exact_dup | True | True | EXACT | 1.00 | ✓ |
| whitespace_var | True | True | NORMALIZED | 1.00 | ✓ |
| near_dup | True | True | NEAR_DUPLICATE | 0.89 | ✓ |
| new_text | False | False | NONE | 0.00 | ✓ |
| tamil_exact | True | True | EXACT | 1.00 | ✓ |

## 4. Precision / Recall

| Metric | Value |
|--------|-------|
| True Positives | 4 |
| True Negatives | 1 |
| False Positives | 0 |
| False Negatives | 0 |
| Precision | 1.0000 |
| Recall | 1.0000 |
| F1 | 1.0000 |

> **NOTE:** Perfect scores are expected on this small synthetic test set. Real-world duplicate detection requires evaluation on naturally occurring near-duplicates at scale.

## 5. Module Location

- Implementation: `scripts/duplicate_detector_v2.py` (3,096 bytes)
- Tests: `tests/test_phase24_infrastructure.py` (5 duplicate tests)
