# PHASE 24 — Language Identification Engine Design

**Project:** IGRIS — Multilingual Decoder-Only Transformer
**Date:** 2026-11-19 17:43
**Module:** `scripts/language_identifier_v2.py`
**Status:** SYNTHETIC BENCHMARK ONLY — NOT PRODUCTION VALIDATED

## 1. Architecture

### 1.1 Three-Category Classification

The LanguageIdentifierV2 engine classifies text into five labels:

| Label | Description |
|-------|-------------|
| `TAMIL` | Native Tamil script text (U+0B80–U+0BFF dominant) |
| `ENGLISH` | Standard English in Latin script |
| `TANGLISH` | Tamil-English code-mixed (Romanized Tamil, discourse particles, intra-sentential switching) |
| `UNKNOWN` | Insufficient evidence for classification |
| `OUT_OF_SCOPE` | Detected non-target language (Hindi, Telugu, Bengali, etc.) |

### 1.2 Decision Pipeline

```
Input Text
  │
  ├─ Empty/whitespace → UNKNOWN
  │
  ├─ Script distribution analysis
  │   ├─ Non-target Indic script dominant → OUT_OF_SCOPE
  │   ├─ Tamil script > 90% → TAMIL
  │   ├─ Tamil script present + Latin script present → TANGLISH
  │   └─ Latin script only → (further analysis)
  │
  ├─ Tanglish lexicon matching
  │   ├─ Known Romanized Tamil words found → TANGLISH
  │   └─ Tamil discourse particles found → TANGLISH
  │
  ├─ English stopword ratio
  │   ├─ High English stopword ratio + no Tamil signals → ENGLISH
  │   └─ Otherwise → UNKNOWN
  │
  └─ Confidence scoring (0.0 – 1.0)
```

### 1.3 Tanglish Detection Features

1. **Script mixing:** Tamil (U+0B80–U+0BFF) + Latin in same text
2. **Romanized Tamil lexicon:** 65+ common words (vanakkam, epdi, romba, etc.)
3. **Discourse particles:** da, pa, di, machan, macha, aiyo, seri, la, dhan, nu
4. **Tamil suffixes in Latin:** -uku, -aal, -il, -um, -ai, -am
5. **Non-target script rejection:** Devanagari, Bengali, Telugu, Kannada, Malayalam, etc.

### 1.4 Output Structure

```python
@dataclass
class LangIDResult:
    label: str              # TAMIL | ENGLISH | TANGLISH | UNKNOWN | OUT_OF_SCOPE
    confidence: float       # 0.0 to 1.0
    is_code_mixed: bool     # True if multiple scripts detected
    script_ratios: Dict[str, float]
    detected_scripts: List[str]
    sublabel: Optional[str] # e.g. "ROMANIZED_TAMIL", "TAMIL_WITH_ENGLISH_TECH"
    notes: Optional[str]
```

## 2. Synthetic Benchmark Results

### 2.1 Overall Accuracy

| Metric | Value |
|--------|-------|
| Total fixtures | 100 |
| Correct (corrected mapping) | 88 |
| Accuracy | 88.00% |

### 2.2 Per-Category Accuracy

| Category | Total | Correct | Accuracy |
|----------|-------|---------|----------|
| ENGLISH_TAMIL_COLLOQUIAL | 20 | 12 | 60.00% |
| FORMAL_TECHNICAL_TANGLISH | 20 | 19 | 95.00% |
| INTRA_SENTENTIAL_CODE_SWITCH | 20 | 17 | 85.00% |
| ROMANIZED_TAMIL_INFORMAL | 20 | 20 | 100.00% |
| TAMIL_SCRIPT_ENGLISH_TECH | 20 | 20 | 100.00% |

### 2.3 Per-Class Metrics

| Class | Precision | Recall | F1 |
|-------|-----------|--------|-----|
| ENGLISH | 0.0000 | 0.0000 | 0.0000 |
| TANGLISH | 1.0000 | 0.8800 | 0.9362 |
| UNKNOWN | 0.0000 | 0.0000 | 0.0000 |

### 2.4 Additional Test Samples

| Metric | Value |
|--------|-------|
| Pure Tamil/English/Tanglish | 10/10 correct |

### 2.5 Failure Analysis

The 12 misclassified fixtures fall into two patterns:

1. **ENGLISH_TAMIL_COLLOQUIAL → ENGLISH (8/20):** Fixtures with high English content and only subtle Tamil discourse particles (e.g., trailing "da" or "pa") are classified as ENGLISH because the English stopword ratio exceeds the Tanglish detection threshold.

2. **INTRA_SENTENTIAL_CODE_SWITCH → ENGLISH (3/20):** Code-switching fixtures where Tamil words are used as proper nouns or the Tamil lexicon match is below threshold.

3. **FORMAL_TECHNICAL_TANGLISH → UNKNOWN (1/20):** One fixture with insufficient discriminating features.

> **DISCLAIMER:** These results are on synthetic benchmarks only. Real-world Tanglish exhibits greater variety and noise. Production-grade LID requires evaluation on naturally occurring code-mixed text.

## 3. Module Location

- Implementation: `scripts/language_identifier_v2.py` (10,080 bytes)
- Tests: `tests/test_phase24_infrastructure.py` (11 LID tests)
