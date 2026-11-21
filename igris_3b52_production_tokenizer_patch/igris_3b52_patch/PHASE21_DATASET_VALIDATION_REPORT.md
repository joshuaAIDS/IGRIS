# IGRIS PHASE 21 — DATASET INTEGRITY, CLEANING & VALIDATION REPORT

**Document ID:** `IGRIS-PHASE21-DVR-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Pipeline Engine:** Phase 14 Pre-Processing Pipeline ([ingress_safety_pipeline.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/ingress_safety_pipeline.py), [unicode_processor.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/unicode_processor.py), [quality_filter.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/quality_filter.py), [duplicate_detector.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/duplicate_detector.py), [language_identifier.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/language_identifier.py), [privacy_contamination_scanner.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/privacy_contamination_scanner.py))  
**Target Corpora:** 18 Permissive Candidate Sources (Pending Ingress)  
**Status:** VALIDATION INFRASTRUCTURE VERIFIED & ARMED — QUARANTINE EMPTY  

---

## 1. Executive Summary

This report establishes the dataset integrity, cleaning, and validation specifications for the 18 eligible candidate sources entering Phase 21 controlled acquisition.

Following the `SOLO_DEVELOPER_OWNER_REVIEW` operating model and strict governance invariants:
* **Production Quarantine Storage:** **EMPTY (0 Bytes)**. No external data has been acquired without individual, explicit owner authorization.
* **Validation Infrastructure Readiness:** The 10-stage multilingual validation engine is fully configured, unit tested, and ready to ingest authorized datasets directly into quarantine isolation.
* **Separation of Concerns:** In accordance with Task 6 directives, synthetic pipeline benchmarks are strictly separated from published production catalog projections.

---

## 2. Ten-Stage Validation Pipeline Architecture

The IGRIS dataset processing infrastructure enforces a strict linear pipeline:

```
[Quarantine Staging] 
        │
        ▼
1. Strict UTF-8 Validation (U+FFFD detection, invalid sequence rejection)
        │
        ▼
2. Unicode 15.1.0 NFC Normalization (Canonical composition)
        │
        ▼
3. Indic Script & Ligature Preservation (ZWJ / ZWNJ preservation for matras & conjuncts)
        │
        ▼
4. Language Identification & Script Verification (FastText / Unicode block heuristics)
        │
        ▼
5. Code-Switching & Dialectal Detection (Tamil-English / Hindi-English script mixing)
        │
        ▼
6. Content Deduplication (Exact 64-bit MurmurHash + MinHash LSH)
        │
        ▼
7. Document Quality Filtering (Length, repetition, whitespace, symbol density)
        │
        ▼
8. PII & Secret Redaction (Email, phone, Aadhaar, PAN, SSN, API/Private keys)
        │
        ▼
9. Benchmark Contamination Screening (n-gram decontamination vs HumanEval, MBPP, Flores-200)
        │
        ▼
10. Tamper-Evident Provenance Logging (Cryptographically chained SHA-256 ledger)
        │
        ▼
[Validated Pretraining Cache]
```

---

## 3. Detailed Validation Axes & Acceptance Criteria

### 3.1 Strict UTF-8 Validation
* **Rule:** All bytes must decode losslessly under standard `utf-8`.
* **Rejection Criteria:** Any byte sequence causing `UnicodeDecodeError`, containing raw null bytes (`\0`), or generating Unicode replacement characters (`\uFFFD`) is immediately flagged and rejected (`REJECT_INVALID_UTF8`).
* **Enforcement:** `ingress_safety_pipeline.py` inspects every incoming raw stream chunk before staging.

### 3.2 Unicode 15.1.0 NFC Canonical Normalization
* **Rule:** Every document is transformed to and validated against Normalization Form C (`NFC`).
* **Indic Stability:** Ensures that precomposed glyphs and decomposed base-character + combining-diacritic sequences are converted to canonical precomposed forms without altering phonological meaning.
* **Verification:** `unicodedata.is_normalized("NFC", text) == True`.

### 3.3 Indic-Script & Orthographic Preservation
* **Linguistic Rule:** South Asian scripts rely on Zero-Width Joiner (`ZWJ`, `U+200D`) and Zero-Width Non-Joiner (`ZWNJ`, `U+200C`) to represent distinct ligatures (e.g. Malayalam chillu letters, Hindi conjunct halants).
* **Policy:** ZWJ and ZWNJ characters within Indic script Unicode blocks are strictly preserved. Isolated or rogue format controls outside Indic contexts are sanitized.

### 3.4 Language Identification (LID)
* **Classifier:** Dual-engine architecture utilizing primary script range categorization and secondary character n-gram language classification.
* **Thresholds:**
  * Minimum primary language confidence: $\ge 0.85$.
  * Misclassified language documents are quarantined to script-mismatch queues.
* **Target Language Profiles:**
  * Devanagari (`hi`): $U+0900 - U+097F$
  * Tamil (`ta`): $U+0B80 - U+0BFF$
  * Telugu (`te`): $U+0C00 - U+0C7F$
  * Malayalam (`ml`): $U+0D00 - U+0D7F$
  * Kannada (`kn`): $U+0C80 - U+0CFF$
  * Bengali (`bn`): $U+0980 - U+09FF$
  * Gujarati (`gu`): $U+0A80 - U+0AFF$
  * Latin (`en`): $U+0000 - U+007F$

### 3.5 Code-Switch & Tanglish Detection
* **Metric:** Token-level script transition density.
* **Definition:** Tanglish documents exhibit Latin script syntax with Tamil phonology, characterized by alternating Tamil lexical stems and English connectors.
* **Classification:** If script transitions between Latin and Tamil exceed 0.20 or vocabulary matches DravidianCodeMix lexicons, tag as `ta-Latn` (Tanglish) rather than rejecting as low-confidence English.

### 3.6 Content Deduplication
* **Level 1 (Exact Deduplication):** 64-bit MurmurHash3 content hashing over normalized document text. Duplicate hashes are removed immediately.
* **Level 2 (Near Deduplication):** MinHash LSH with 128 permutation hashes, 5-gram tokenization, and Jaccard similarity threshold $\ge 0.80$.
* **Expected Yield:** Filters crawler spam, repeated boilerplate headers, and mirrored web pages.

### 3.7 Document Quality Filtering
* Configured thresholds from `quality_filter.py`:
  * Minimum document length: 15 characters (`EXTREMELY_SHORT_DOCUMENT`).
  * Minimum words: 3 whitespace-separated tokens (`INSUFFICIENT_WORDS`).
  * Maximum repeated character run: 6 consecutive identical characters (`REPEATED_CHAR_SEQUENCE`).
  * Maximum repeated line ratio: $\le 0.35$ (`REPEATED_LINES`).
  * Maximum symbol-to-alphanumeric ratio: $\le 0.45$ (`EXCESSIVE_SYMBOL_DENSITY`).
  * Maximum whitespace ratio: $\le 0.50$ (`EXCESSIVE_WHITESPACE`).

### 3.8 PII & Sensitive Secret Scanning
* **Regex Scanning Vectors:**
  * Email addresses (`[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+`)
  * Phone numbers (International and Indian 10-digit formats)
  * Indian Aadhaar numbers (12-digit format `\d{4}\s\d{4}\s\d{4}`)
  * Indian PAN cards (`[A-Z]{5}[0-9]{4}[A-Z]{1}`)
  * US Social Security Numbers (`\d{3}-\d{2}-\d{4}`)
  * Credit card numbers (Luhn-compliant 16-digit patterns)
  * Private keys (`-----BEGIN PRIVATE KEY-----`)
  * Cloud API tokens (AWS, Hugging Face, GitHub PATs)
* **Action:** Automatic redaction with semantic replacement tokens (`<PII:EMAIL>`, `<PII:PHONE>`, `<PII:AADHAAR>`) or full document rejection if PII density exceeds 3 items per 1,000 characters.

### 3.9 Benchmark Contamination Screening
* **Policy:** Zero contamination of downstream evaluation test sets.
* **Decontamination Targets:**
  * `HumanEval` & `MBPP` (Python coding evaluation)
  * `Flores-200` (Multilingual translation evaluation)
  * `IndicGLUE` test splits (Tanglish and Indic NLU evaluation)
* **Algorithm:** 13-gram token overlap sliding window. Any document matching $\ge 13$ consecutive tokens from an evaluation test split is completely purged from pretraining data.

### 3.10 Cryptographic Provenance Tracking
* Every processed batch generates an immutable manifest entry containing:
  * Raw source SHA-256.
  * Cleaning engine git commit hash.
  * Ingested timestamp.
  * Record count, raw byte count, clean byte count.
  * Cleaned partition SHA-256 digest.

---

## 4. Per-Source Validation Profile & Expected Yields

| Source ID | Source Name | Target Language | Primary Validation Focus | Projected Rejection % |
| :--- | :--- | :---: | :--- | :---: |
| `SRC-TM-01` | IndicCorp v2 (Tamil) | `ta` | Tamil NFC normalization, ZWJ ligature preservation | ~12% (web noise) |
| `SRC-EN-01` | Gutenberg Open Archive | `en` | License header stripping, archaic formatting | ~5% (metadata) |
| `SRC-TG-01` | DravidianCodeMix (Tamil-English)| `ta-Latn` | Script transition density, colloquial noise | ~8% (short utterances)|
| `SRC-TG-02` | IndicGLUE Tanglish Sentiment | `ta-Latn` | Sentiment label detachment, short-text filter | ~6% |
| `SRC-HI-01` | IndicCorp v2 (Hindi) | `hi` | Devanagari conjunct integrity, boilerplate removal | ~14% (crawler spam) |
| `SRC-OI-01` | IndicCorp v2 (Telugu) | `te` | Telugu vowel sign NFC integrity | ~12% |
| `SRC-OI-02` | IndicCorp v2 (Malayalam) | `ml` | Chillu letter ZWJ/ZWNJ preservation | ~11% |
| `SRC-OI-03` | IndicCorp v2 (Kannada) | `kn` | Kannada virama ligature preservation | ~12% |
| `SRC-OI-04` | IndicCorp v2 (Bengali) | `bn` | Bengali conjunct integrity, deduplication | ~13% |
| `SRC-OI-05` | IndicCorp v2 (Gujarati) | `gu` | Gujarati matra combination preservation | ~12% |
| `SRC-CD-01` | The Stack v2 (Permissive Sample)| `code` | PII/Secret scanning, license filter verification | ~18% (secrets/noise)|
| `SRC-TD-02` | IETF RFC Archive (Text) | `en` | Monospace formatting, ASCII diagram preservation | ~4% (page headers) |
| `SRC-TD-03` | Python Official Docs | `en` | Code block extraction, navigation bar stripping | ~6% |
| `SRC-CV-03` | OpenAssistant Conversations | `mul` | Toxic content screening, system prompt tagging | ~10% |
| `SRC-CV-05` | MultiWOZ 2.4 | `en` | Dialogue state annotation detachment | ~3% |
| `SRC-CV-06` | Gutenberg Theatrical Plays | `en` | Speaker turn tagging, stage direction filtering | ~5% |
| `SRC-EM-01` | Unicode 15.1.0 Test Suite | `mul` | Strict character properties, non-text filtering | ~1% |
| `SRC-EM-02` | Unicode 15.1.0 Emoji Data | `mul` | Emoji sequence validation, ZWJ integrity | ~0.5% |

---

## 5. Current Quarantine Status

```
====================================================================================================
PRODUCTION QUARANTINE STATUS:
Current Production Data: 0 Bytes
Acquired Production Datasets: 0
Processed Production Records: 0
Gate Status: LOCKED (Default-Deny Enforced)
====================================================================================================
```

All processing mechanisms have been forensically verified and remain armed awaiting individual owner authorization and cryptographic gate-unlock directives.
