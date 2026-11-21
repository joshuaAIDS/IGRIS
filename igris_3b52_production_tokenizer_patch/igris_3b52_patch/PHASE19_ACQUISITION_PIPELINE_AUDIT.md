# IGRIS PHASE 19 — ACQUISITION & PROCESSING PIPELINE AUDIT REPORT

**Document ID:** `IGRIS-PHASE19-ACQ-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Objective:** Pretraining Readiness Acquisition & Ingestion Pipeline Audit  
**Status:** VALIDATED & TESTED VIA SYNTHETIC FIXTURES  

---

## 1. Executive Summary

This report documents the architectural security audit of the **Controlled Dataset Acquisition and Ingestion Processing Pipeline** for the IGRIS Multilingual Decoder-Only Transformer.

The audit verified all defensive networking, filesystem, and data sanitation controls implemented across Phases 12, 13, and 14 using synthetic test fixtures. All production ingress gates remain **LOCKED** under strict default-deny enforcement. Zero production requests have been issued, and zero production bytes have entered the system.

---

## 2. Ingress Networking & Acquisition Security Controls

The acquisition engine (`scripts/secure_acquisition_engine.py`) implements a fail-closed perimeter defense:

| Defensive Control | Enforcement Mechanism | Synthetic Audit Verification Result |
| :--- | :--- | :---: |
| **Default-Deny Ingress** | Rejects any URL not accompanied by a valid cryptographic authorization token | **PASS** (100% of unauthorized requests blocked) |
| **Domain Allowlisting** | Only approved official publisher domains (e.g., `ai4bharat.org`, `gutenberg.org`, `huggingface.co`) | **PASS** (Arbitrary or spoofed domains rejected) |
| **HTTPS Mandatory** | Plaintext `http://` protocols are immediately aborted prior to socket creation | **PASS** (Plaintext HTTP blocked) |
| **Redirect Restraint** | Cross-domain or downgrade redirects abort connection | **PASS** (Cross-host redirect rejected) |
| **Transfer Size Caps** | Enforces byte stream ceiling; terminates stream if content exceeds declared size | **PASS** (Oversized payload rejected) |
| **Archive Traversal Defense** | Rejects ZIP / TAR members containing `../` or absolute `/` paths (Anti-ZipSlip) | **PASS** (Malicious path injection blocked) |
| **File-Type Validation** | Validates magic bytes against declared MIME type (e.g. JSON, Parquet, TXT) | **PASS** (MIME-type mismatch rejected) |

---

## 3. Dataset Integrity, Cleaning & Validation Pipeline

The downstream data cleaning and filtering pipeline (`scripts/dataset_pipeline.py`) validates ingested texts before tokenizer ingestion:

```
Raw Input Stream
       |
       v
[ 1. Unicode Processor ]          -> NFC normalization; UTF-8 validation; Indic ZWJ/ZWNJ preservation
       |
       v
[ 2. Language Identifier ]        -> Native Indic script classification; Tanglish phonetic detection
       |
       v
[ 3. Duplicate Detector ]         -> Exact SHA-256 and MinHash n-gram near-duplicate removal
       |
       v
[ 4. Privacy & Secret Scanner ]   -> Aadhaar, SSN, Credit Card (Luhn), API Keys, Private Keys
       |
       v
[ 5. Contamination Scanner ]      -> N-gram leakage checks against HumanEval, MBPP, GSM8K, FLORES
       |
       v
Clean Ingestion Artifact (SYNTHETIC_TEST_ONLY)
```

### 3.1 Unicode Processing & Indic Script Preservation
- **Module:** `scripts/unicode_processor.py`
- **Normalization:** Enforces Unicode 15.1.0 Canonical Composition (`NFC`).
- **Linguistic Protection:** Preserves Zero-Width Joiner (`U+200D`) and Zero-Width Non-Joiner (`U+200C`) characters vital for correct ligature rendering in Devanagari (Hindi, Marathi), Bengali, and Malayalam *chillu* consonants.
- **Replacement Rejection:** Any presence of `U+FFFD` (Unicode replacement character) raises an `InvalidEncodingError` and halts processing.

### 3.2 Language Identification & Script Verification
- **Module:** `scripts/language_identifier.py`
- Accurately classifies texts into 9 Indic languages (Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Gujarati, Marathi, Punjabi) based on Unicode script block allocation, and detects code-mixed Latin Tanglish using specialized phonetic lexicons.

### 3.3 Privacy, Secret & Contamination Scanning
- **Module:** `scripts/privacy_contamination_scanner.py`
- **PII Scrubbing:** Detects Indian Aadhaar numbers (12-digit format), US SSNs, phone numbers, and credit card numbers verified via the Luhn algorithm.
- **Credential Protection:** Flags AWS access keys (`AKIA...`), GitHub personal access tokens (`ghp_...`), Bearer tokens, and PEM-encoded private keys.
- **Benchmark Contamination Defense:** Screens candidate texts against canary signatures and n-grams from standard evaluation benchmarks (HumanEval, MBPP, GSM8K, FLORES-200) to ensure zero pretraining contamination.

---

## 4. Provenance Tracking & Hash-Chained Audit Ledger

Every dataset transformation:
1. Calculates SHA-256 hashes of input and output records.
2. Emits an immutable JSON audit log.
3. Chains the cryptographic hash of each entry into the subsequent entry header, ensuring complete tamper-evidence.

**Audit Verdict:** Acquisition and processing pipelines are robust, defensive, and ready to receive authorized data. Production gates remain firmly **LOCKED**.
