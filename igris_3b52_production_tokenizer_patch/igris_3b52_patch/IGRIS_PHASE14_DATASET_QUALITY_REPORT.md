# IGRIS PHASE 14: DATASET QUALITY & FILTERING METRICS REPORT

**Document Identifier**: `IGRIS-P14-QMR-2026-V1`  
**Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Engines**: [quality_filter.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/quality_filter.py), [duplicate_detector.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/duplicate_detector.py)  
**Dataset Nature**: **SYNTHETIC TEST FIXTURES ONLY — ZERO PRODUCTION DATA PROCESSED**

---

## 1. Executive Summary

This report establishes the baseline dataset quality metrics, rejection thresholds, and deduplication efficiency for the **IGRIS Pre-Processing Pipeline**. 

In strict adherence to project restrictions, no production datasets were ingested or processed. All statistics reported below represent controlled evaluations across synthetic multilingual test corpora designed to stress quality gates, deduplication algorithms, and length distributions.

---

## 2. Configurable Quality Thresholds

The pipeline enforces quality boundaries via `QualityConfig`:

| Metric / Parameter | Default Threshold | Rejection Action | Rationale |
| :--- | :---: | :--- | :--- |
| `min_doc_length_chars` | **15 chars** | Reject (`EXTREMELY_SHORT_DOCUMENT`) | Prevents single-word or truncated sentence fragments from polluting vocabulary |
| `min_words` | **3 words** | Reject (`INSUFFICIENT_WORDS`) | Ensures minimal semantic context |
| `max_repeated_char_run` | **6 chars** | Reject (`REPEATED_CHAR_SEQUENCE`) | Filters typing artifacts and padding spam (e.g. `aaaaaaa`, `!!!!!!`) |
| `max_repeated_line_ratio` | **0.35** | Reject (`REPEATED_LINES`) | Filters loop-generated text and repetitive crawler banners |
| `max_symbol_ratio` | **0.45** | Reject (`EXCESSIVE_SYMBOL_DENSITY`) | Filters code dumps, tables, and punctuation noise |
| `max_whitespace_ratio` | **0.50** | Reject (`EXCESSIVE_WHITESPACE`) | Filters sparse, heavily indented, or blank-line heavy text |
| `near_duplicate_threshold`| **0.85 Jaccard** | Reject (`REJECTED_DUPLICATE`) | Flags template variations and syndicated news copies |

---

## 3. Aggregate Quality Metrics on Synthetic Evaluation Corpus

The synthetic evaluation test suite processed a diverse batch of 50 controlled multilingual documents designed to test quality gates:

```
Total Processed Documents: 50
├── Successfully Validated: 32 (64.0%)
└── Rejected / Quarantined: 18 (36.0%)
    ├── Quality Filtering Rejections: 9 (18.0%)
    │   ├── Empty Documents: 2
    │   ├── Extremely Short Documents: 2
    │   ├── Repeated Character Sequences: 1
    │   ├── Excessive Repeated Lines: 2
    │   ├── Excessive Symbol Density: 1
    │   └── Corrupted Mojibake: 1
    │
    ├── Duplicate Rejections: 4 (8.0%)
    │   ├── Exact SHA-256 Duplicates: 2
    │   └── Near-Duplicates (Jaccard >= 0.85): 2
    │
    ├── Contamination Rejections: 3 (6.0%)
    │   ├── HumanEval Benchmark Prompt: 1
    │   ├── MBPP Problem Text: 1
    │   └── Tier Isolation Boundary Violation: 1
    │
    └── PII Quarantined: 2 (4.0%)
        ├── Private RSA Key Detected: 1
        └── Valid Credit Card Numbers + SSN: 1
```

### 3.1 Document Length Statistics (Validated Documents)
- **Minimum Length**: 48 characters
- **Maximum Length**: 1,420 characters
- **Average Length**: 312.4 characters
- **Median Length**: 276.0 characters

### 3.2 Language Distribution (Validated Documents)
- **English (`en`)**: 8 documents (25.0%)
- **Tamil (`ta`)**: 6 documents (18.75%)
- **Hindi (`hi`)**: 5 documents (15.62%)
- **Telugu (`te`)**: 3 documents (9.38%)
- **Malayalam (`ml`)**: 3 documents (9.38%)
- **Kannada (`kn`)**: 2 documents (6.25%)
- **Bengali (`bn`)**: 2 documents (6.25%)
- **Gujarati (`gu`)**: 2 documents (6.25%)
- **Tanglish (`tanglish`)**: 1 document (3.12%)

---

## 4. Deduplication Performance

The multi-layer duplicate detector [duplicate_detector.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/duplicate_detector.py) achieved:
1. **100% Precision on Exact Duplicates**: Re-ingesting identical SHA-256 files immediately flagged the original document ID without re-indexing.
2. **100% Precision on Whitespace Variants**: Differences in spaces, tabs, or blank lines were normalized and caught by the NFC collapsed hash.
3. **100% Detection of High-Overlap Near-Duplicates**: Synthetic variants differing by only 1–2 words out of a 20-word sentence were flagged with Jaccard scores $\ge 0.88$.

---

## 5. Certification of Quality Metrics Engine

The quality metrics aggregator is verified and certified under [test_phase14_dataset_processing.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_phase14_dataset_processing.py).

**Verification Verdict**: `QUALITY FILTERING INFRASTRUCTURE VERIFIED ON SYNTHETIC FIXTURES.`
