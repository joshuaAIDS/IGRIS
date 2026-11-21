# PHASE 24 — Tanglish Analysis Report

**Project:** IGRIS — Multilingual Decoder-Only Transformer
**Date:** 2026-11-19 17:43
**Module:** `scripts/tanglish_analyzer.py`
**Status:** SYNTHETIC BENCHMARK ONLY

## 1. Architecture

### 1.1 Analysis Features

The TanglishAnalyzer extracts structural features from code-mixed text:

1. **Script span extraction:** Identifies contiguous runs of Tamil script vs Latin script
2. **Code-switch point detection:** Locates boundaries where script changes within a sentence
3. **Discourse marker identification:** Finds Tamil particles embedded in English context
4. **Romanized Tamil candidate detection:** Identifies Latin-script words matching Tamil phonetic patterns
5. **Tamil suffix markers:** Detects Tamil morphological suffixes (-uku, -aal, -il, -um, -ai, -am)
6. **Structural plausibility assessment:** Boolean evaluation of whether text represents genuine code-mixing

### 1.2 Output Structure

```python
@dataclass
class TanglishAnalysis:
    spans: List[Dict]              # script spans with positions
    code_switch_points: List[int]  # character positions of script switches
    discourse_markers_found: List[str]
    romanized_tamil_candidates: List[str]
    tamil_suffixes_detected: List[str]
    is_structurally_plausible: bool
    plausibility_notes: List[str]
    tamil_char_count: int
    latin_char_count: int
    total_chars: int
    tamil_ratio: float
    latin_ratio: float
```

## 2. Fixture Analysis Results

| Metric | Value |
|--------|-------|
| Total fixtures analyzed | 100 |
| Avg code-switch points per fixture | 2.18 |
| Avg discourse markers per fixture | 0.38 |
| Avg romanized Tamil candidates per fixture | 0.32 |
| Avg Tamil suffixes per fixture | 0.29 |
| Structurally plausible | 100/100 (100.00%) |

### 2.1 Aggregate Totals

| Feature | Total Count |
|---------|-------------|
| Code-switch points | 218 |
| Discourse markers | 38 |
| Romanized Tamil candidates | 32 |
| Tamil suffixes | 29 |

## 3. Observations

1. All 100 synthetic fixtures are classified as structurally plausible.
2. Code-switch detection averages 2.18 points per fixture, consistent with the fixture design (each contains 2–4 language transitions).
3. Discourse markers are found in 38% of fixtures, concentrated in ENGLISH_TAMIL_COLLOQUIAL and DISCOURSE_PARTICLE_MIX categories.
4. Romanized Tamil candidates appear in 32% of fixtures, primarily from ROMANIZED_TAMIL_INFORMAL category.

> **DISCLAIMER:** These metrics are from synthetic Tanglish fixtures. Natural code-mixed text may have different distributions of switch points, markers and patterns.

## 4. Module Location

- Implementation: `scripts/tanglish_analyzer.py` (5,667 bytes)
- Tests: `tests/test_phase24_infrastructure.py` (5 Tanglish tests)
