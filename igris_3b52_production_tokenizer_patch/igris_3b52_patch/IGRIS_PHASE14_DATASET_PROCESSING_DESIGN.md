# IGRIS PHASE 14: DATASET PROCESSING & VALIDATION PIPELINE DESIGN

**Document Identifier**: `IGRIS-P14-DPD-2026-V1`  
**Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Status**: `APPROVED_DESIGN — ZERO PRODUCTION DATA INGRESS`  
**Invariant Check**: Candidate A (`ac7e18b1...`) & Candidate B (`d3a3431e...`) Intact

---

## 1. Architectural Scope & Operating Model

This document specifies the modular, production-grade dataset integrity, cleaning, filtering, and validation pipeline for the **IGRIS Multilingual Decoder-Only Transformer**.

Under the `SOLO_DEVELOPER_OWNER_REVIEW` framework:
- The processing engine supports multilingual text across English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Gujarati, and Tanglish.
- Because no production dataset is yet authorized or acquired, all pipeline verification uses isolated synthetic fixtures.
- Raw files remain strictly immutable (`0o444`).
- Downstream training gates remain strictly **LOCKED**.

---

## 2. Thirteen-Stage Modular Pre-Processing Architecture

```
[ INPUT ]
    │
    ▼
[ 1. SOURCE VERIFICATION ] ────────(UNAUTHORIZED / REJECTED)──► [ SourceVerificationError ]
    │ (APPROVED TIER 1 CANDIDATE)
    ▼
[ 2. FILE INTEGRITY VALIDATION ] ──(BAD HASH / EXECUTABLE)────► [ FileIntegrityError ]
    │ (INTACT & NON-EXECUTABLE)
    ▼
[ 3. FORMAT VALIDATION ] ──────────(UNSUPPORTED EXTENSION)────► [ FormatValidationError ]
    │ (SUPPORTED FORMAT)
    ▼
[ 4. TEXT EXTRACTION ] ────────────(INVALID UTF-8 / U+FFFD)───► [ InvalidEncodingError ]
    │ (DECODED UTF-8 STREAM)
    ▼
[ 5. UNICODE NORMALIZATION ] ──────(NFC CANONICAL NORMALIZATION; PRESERVE INDIC VOWELS & ZWJ)
    │ (NORMALIZED TEXT)
    ▼
[ 6. LANGUAGE IDENTIFICATION ] ────(SCRIPT RATIO + N-GRAMS + TANGLISH LEXICON -> LANG & CONF)
    │ (PRIMARY LANG & CONFIDENCE)
    ▼
[ 7. TEXT QUALITY FILTERING ] ─────(SHORT / REPEATED LINES / MOJIBAKE / SYMBOLS) ──► [ REJECTED_QUALITY ]
    │ (QUALITY PASSED)
    ▼
[ 8. DUPLICATE DETECTION ] ────────(EXACT SHA-256 / NORMALIZED HASH / NEAR-DUP JACCARD) ──► [ REJECTED_DUPLICATE ]
    │ (UNIQUE)
    ▼
[ 9. PII SCREENING ] ──────────────(EMAILS / PHONES / SSN / AADHAAR / CARDS / CREDS) ──► [ FLAGGED / QUARANTINED ]
    │ (CLEAN / REDACTED)
    ▼
[ 10. CONTAMINATION CHECKING ] ────(BENCHMARKS: HUMANEVAL, MBPP / RLHF PREFERENCE PAIRS) ──► [ REJECTED_CONTAMINATION ]
    │ (UNCONTAMINATED)
    ▼
[ 11. PROVENANCE RECORDING ] ──────(CRYPTOGRAPHIC AUDIT CHAIN -> dataset_processing_audit.jsonl)
    │
    ▼
[ 12. VALIDATION REPORT ] ─────────(COMPILED STATUS: VALIDATED / REJECTED / QUARANTINED)
```

---

## 3. Detailed Stage Specifications

### Stage 1: Input & Path Boundary Verification
- Verifies input file is located within authorized quarantine staging directories (`allowed_input_dirs`).
- Attempts to process files from external or unauthorized directories raise `UnauthorizedDirectoryError`.

### Stage 2: Source Verification
- Verifies `source_id` against the canonical 32-source register.
- Enforces tier boundaries: Tier 2 (Conditional) and Tier 3 (Evaluation-Only) are barred from training pipelines; Tier 4 (Permanently Blocked) is rejected for all operations.

### Stage 3: File Integrity Validation
- Recalculates SHA-256 hash across raw input bytes.
- Verifies absence of executable binary headers (`MZ` for PE, `\x7fELF` for ELF, `\xca\xfe\xba\xbe` for Mach-O).
- Rejects files failing size ceilings or showing truncation.

### Stage 4: Format Validation
- Restricts processing to supported text and structured formats: `.txt`, `.json`, `.jsonl`, `.csv`, `.tsv`, `.md`.
- Rejects unexpected or dangerous binary file extensions with `FormatValidationError`.

### Stage 5: Text Extraction & UTF-8 Losslessness
- Decodes raw stream using strict UTF-8 (`errors='strict'`).
- Detects and rejects Unicode replacement character `\uFFFD` (`\xef\xbf\xbd`).

### Stage 6: Unicode Normalization & Script Preservation
- Canonical NFC normalization via `unicodedata.normalize('NFC', text)`.
- **Indic Script Invariant**: Strictly preserves vowel signs, matras, viramas, and combining characters across all 7 Indic scripts.
- **Zero-Width Character Policy**:
  - Legitimate Indic ligatures and Malayalam chillu characters utilizing ZWJ (`\u200D`) and ZWNJ (`\u200C`) are preserved when adjacent to Indic characters.
  - Invisible non-Indic zero-width characters (e.g. `\u200B`, `\uFEFF`, `\u2060`) are stripped.
- Non-printable ASCII control characters (`\x00-\x08`, `\x0b`, `\x0c`, `\x0e-\x1f`) are stripped while standard whitespace (`\t`, `\n`, `\r`, space) is preserved.

### Stage 7: Language Identification
- Multi-factor classification combining Unicode script distribution, character n-gram profiles, and Tanglish lexical heuristics.
- Distinguishes: English (`en`), Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Malayalam (`ml`), Kannada (`kn`), Bengali (`bn`), Gujarati (`gu`), Tanglish (`tanglish`), and `unknown`.
- Computes confidence score; scores below `min_confidence` (0.40) or ambiguous short strings are assigned `unknown`.

### Stage 8: Text Quality Filtering
Configurable checks via `QualityConfig`:
- **Length**: Rejects documents with length $< 15$ characters or $< 3$ words.
- **Character Runs**: Flags run-on repeated characters exceeding 6 repetitions (e.g. `aaaaaaa`, `!!!!!!`).
- **Whitespace**: Flags excessive whitespace exceeding 50% of document.
- **Line Loops**: Flags repetitive line loops exceeding 35% duplicate line ratio.
- **Mojibake**: Detects broken UTF-8 patterns (e.g. `Ã©`, `â€™`, `ï¿½`).
- **Symbol Density**: Rejects documents where non-alphanumeric symbol ratio exceeds 45%.
- **Boilerplate**: Detects low-information boilerplate phrases in short contexts.

### Stage 9: Duplicate Detection
Multi-layer deduplication via [duplicate_detector.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/duplicate_detector.py):
1. Exact SHA-256 hash lookup.
2. Normalized text hash lookup (NFC + whitespace-collapsed).
3. Near-duplicate detection via word 3-gram Jaccard similarity (threshold $\ge 0.85$).
4. Persistent, concurrency-safe index (`duplicate_index.json` protected by file lock).
5. Non-destructive mapping: original files are preserved; duplicate relationships and canonical document IDs are recorded.

### Stage 10: PII Screening
Screens for sensitive personal information:
- Emails (RFC 5322).
- Telephone numbers (US and Indian mobile/landline).
- Government IDs (US SSN, Indian 12-digit Aadhaar).
- Financial accounts (Credit cards with Luhn checksum validation).
- Credentials & Secrets (RSA/EC private keys, AWS keys, GitHub tokens, Bearer tokens).
- Samples are redacted in logs (`XXXX-XXXX-XXXX-1234`).
- Status assigned: `CLEAN`, `FLAGGED_FOR_REVIEW`, or `QUARANTINED`.

### Stage 11: Contamination & Leakage Checking
- Scans for evaluation benchmark prompts and solutions: HumanEval function signatures (`has_close_elements`, `separate_paren_groups`, etc.) and MBPP problem texts.
- Scans for RLHF preference pair formatting (`Human: ... Assistant: ...`, `chosen: ... rejected: ...`).
- Enforces operational tier isolation for evaluation and conditional datasets.

### Stage 12: Provenance Recording
- Every processed document generates an immutable provenance record:
  $$\text{Payload} = \text{timestamp} \parallel \text{doc\_id} \parallel \text{source\_id} \parallel \text{sha256} \parallel \text{quality\_score} \parallel \text{language} \parallel \text{prev\_hash}$$
  $$\text{entry\_hash} = \text{SHA-256}(\text{Payload})$$
- Appended to `quarantine/logs/dataset_processing_audit.jsonl`.
- Tamper-evident integrity verified via `verify_integrity()`.

### Stage 13: Final Validation Report
- Compiles composite validation outcome: `VALIDATED`, `REJECTED_QUALITY`, `REJECTED_DUPLICATE`, `REJECTED_CONTAMINATION`, or `QUARANTINED_PII`.
- Aggregates batch metrics via `DatasetQualityMetrics.aggregate()`.

---

## 4. Architectural Invariant Summary

1. **Production Ingress Gate**: `LOCKED` (Default-Deny Enforced).
2. **Raw File Immutability**: Inputs are never modified in place (`chmod 0o444`).
3. **Artifact Integrity**: Candidate A and Candidate B tokenizers remain untouched.
4. **Audit Trail**: Every transformation is traceable, deterministic, and hash-chained.
