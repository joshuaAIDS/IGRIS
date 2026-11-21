# IGRIS PHASE 14: SECURITY TEST RESULTS REPORT

**Document Identifier**: `IGRIS-P14-STR-2026-V1`  
**Execution Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Test Suite**: [test_phase14_dataset_processing.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_phase14_dataset_processing.py)  
**Execution Engine**: `pytest-9.2.0`, Python 3.11.9 (`win32`)

---

## 1. Executive Summary

Phase 14 conducted extensive automated verification of the multilingual dataset integrity, cleaning, filtering, and validation infrastructure. All 28 security and quality test vectors specified in Section 13 were evaluated across isolated synthetic fixtures.

**Test Summary**:
- **Phase 14 Dataset Processing Tests**: **28 / 28 PASSED** (0 failures, 0 warnings, 0 skips).
- **Total Project Pytest Regression Suite**: **407 / 407 PASSED** in 4.90 seconds.
- **Production Acceptance Runner**: **162 / 162 CHECKS PASSED**.
- **Candidate Tokenizer Invariants**: **100% PRESERVED**.

---

## 2. Granular Results Across 28 Test Vectors

| # | Test Name | Target Requirement / Scenario | Mechanism | Result |
| :---: | :--- | :--- | :--- | :---: |
| **01** | `test_sha256_mismatch` | Tampered / corrupted input file bytes | Hash recalculation against expected | **PASSED** |
| **02** | `test_corrupted_files` | Executable binary headers (`MZ`, `ELF`) | Magic byte prefix inspection | **PASSED** |
| **03** | `test_invalid_utf8` | Broken byte sequences & `\uFFFD` chars | Strict UTF-8 decoder validation | **PASSED** |
| **04** | `test_unicode_normalization` | Decomposed NFD strings | Canonical NFC normalization | **PASSED** |
| **05** | `test_tamil_text_preservation` | Tamil vowel signs and pulli | Script preservation without loss | **PASSED** |
| **06** | `test_telugu_text_preservation` | Telugu vowel signs and wattulu | Script preservation without loss | **PASSED** |
| **07** | `test_malayalam_text_preservation`| Malayalam chillu characters & ZWJ ligatures | Context-aware zero-width preservation | **PASSED** |
| **08** | `test_kannada_text_preservation` | Kannada combining characters and virama | Script preservation without loss | **PASSED** |
| **09** | `test_hindi_text_preservation` | Hindi matras, conjuncts, nuktas | Devanagari preservation without loss | **PASSED** |
| **10** | `test_bengali_text_preservation` | Bengali vowel signs and hasant | Bengali preservation without loss | **PASSED** |
| **11** | `test_gujarati_text_preservation`| Gujarati matras and conjuncts | Gujarati preservation without loss | **PASSED** |
| **12** | `test_tanglish_classification` | Romanized/phonetic Tamil | Tanglish lexicon & suffix heuristics | **PASSED** |
| **13** | `test_mixed_script_text` | Mixed English and Indic text | Multi-script distribution tracking | **PASSED** |
| **14** | `test_empty_documents` | Empty and whitespace-only documents | Quality length check (`EMPTY_DOCUMENT`) | **PASSED** |
| **15** | `test_repeated_documents` | Repetitive line loops | Line duplicate ratio threshold check | **PASSED** |
| **16** | `test_near_duplicate_documents` | Near-identical document variations | Word 3-gram Jaccard similarity ($\ge 0.85$) | **PASSED** |
| **17** | `test_pii_detection` | Emails, phones, SSNs, Aadhaar, cards | Privacy regex and Luhn validation | **PASSED** |
| **18** | `test_credential_detection` | Private keys and AWS tokens | Secret patterns; tagged `QUARANTINED` | **PASSED** |
| **19** | `test_benchmark_contamination` | HumanEval / MBPP benchmark signatures | Prompt signature matching | **PASSED** |
| **20** | `test_evaluation_only_source_isolation` | Tier 3 evaluation datasets | Isolation check; training blocked | **PASSED** |
| **21** | `test_permanently_blocked_source_rejection` | Tier 4 permanently rejected sources | Tier rejection check | **PASSED** |
| **22** | `test_audit_chain_tampering` | Tampered processing audit record | SHA-256 chained hash verification | **PASSED** |
| **23** | `test_processing_interruption` | Unsupported format exception | Clean exception; zero state corruption | **PASSED** |
| **24** | `test_duplicate_index_concurrency`| Concurrent duplicate index access | File mutex locking (`.lock`) | **PASSED** |
| **25** | `test_deterministic_processing`| Repeated runs on identical text | Deterministic output verification | **PASSED** |
| **26** | `test_provenance_integrity` | Provenance generation per document | Full provenance record with entry hash | **PASSED** |
| **27** | `test_invalid_processing_configuration` | Empty pipeline configuration version | `PipelineError` raised | **PASSED** |
| **28** | `test_unauthorized_input_directory_rejection` | File outside allowed quarantine directory | `UnauthorizedDirectoryError` raised | **PASSED** |

---

## 3. Actual Command Execution Logs

### 3.1 Phase 14 Test Suite Run

```powershell
PS C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch> C:\IGRIS\.venv\Scripts\python.exe -m pytest tests/test_phase14_dataset_processing.py -v
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0 -- C:\IGRIS\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch
plugins: anyio-4.16.0
collecting ... collected 28 items

tests/test_phase14_dataset_processing.py::test_sha256_mismatch PASSED    [  3%]
tests/test_phase14_dataset_processing.py::test_corrupted_files PASSED    [  7%]
tests/test_phase14_dataset_processing.py::test_invalid_utf8 PASSED       [ 10%]
tests/test_phase14_dataset_processing.py::test_unicode_normalization PASSED [ 14%]
tests/test_phase14_dataset_processing.py::test_tamil_text_preservation PASSED [ 17%]
tests/test_phase14_dataset_processing.py::test_telugu_text_preservation PASSED [ 21%]
tests/test_phase14_dataset_processing.py::test_malayalam_text_preservation PASSED [ 25%]
tests/test_phase14_dataset_processing.py::test_kannada_text_preservation PASSED [ 28%]
tests/test_phase14_dataset_processing.py::test_hindi_text_preservation PASSED [ 32%]
tests/test_phase14_dataset_processing.py::test_bengali_text_preservation PASSED [ 35%]
tests/test_phase14_dataset_processing.py::test_gujarati_text_preservation PASSED [ 39%]
tests/test_phase14_dataset_processing.py::test_tanglish_classification PASSED [ 42%]
tests/test_phase14_dataset_processing.py::test_mixed_script_text PASSED  [ 46%]
tests/test_phase14_dataset_processing.py::test_empty_documents PASSED    [ 50%]
tests/test_phase14_dataset_processing.py::test_repeated_documents PASSED [ 53%]
tests/test_phase14_dataset_processing.py::test_near_duplicate_documents PASSED [ 57%]
tests/test_phase14_dataset_processing.py::test_pii_detection PASSED      [ 60%]
tests/test_phase14_dataset_processing.py::test_credential_detection PASSED [ 64%]
tests/test_phase14_dataset_processing.py::test_benchmark_contamination PASSED [ 67%]
tests/test_phase14_dataset_processing.py::test_evaluation_only_source_isolation PASSED [ 71%]
tests/test_phase14_dataset_processing.py::test_permanently_blocked_source_rejection PASSED [ 75%]
tests/test_phase14_dataset_processing.py::test_audit_chain_tampering PASSED [ 78%]
tests/test_phase14_dataset_processing.py::test_processing_interruption PASSED [ 82%]
tests/test_phase14_dataset_processing.py::test_duplicate_index_concurrency PASSED [ 85%]
tests/test_phase14_dataset_processing.py::test_deterministic_processing PASSED [ 89%]
tests/test_phase14_dataset_processing.py::test_provenance_integrity PASSED [ 92%]
tests/test_phase14_dataset_processing.py::test_invalid_processing_configuration PASSED [ 96%]
tests/test_phase14_dataset_processing.py::test_unauthorized_input_directory_rejection PASSED [100%]

============================= 28 passed in 0.17s ==============================
```

### 3.2 Full Project Regression Suite Run

```powershell
PS C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch> C:\IGRIS\.venv\Scripts\python.exe -m pytest tests -q
........................................................................ [ 17%]
........................................................................ [ 35%]
........................................................................ [ 53%]
........................................................................ [ 70%]
........................................................................ [ 88%]
...............................................                          [100%]
407 passed in 4.90s
```

### 3.3 Acceptance Runner Run

```powershell
PS C:\IGRIS> C:\IGRIS\.venv\Scripts\python.exe C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts\run_acceptance_3b57.py
================================================================================
REQUIREMENT SUMMARY
================================================================================
Req  1 | [PASS] Clean-process artifact loading                                         (1/1 tests)
Req  2 | [PASS] Verify exact vocabulary size: 32,768                                   (6/6 tests)
Req  3 | [PASS] Verify exactly 12 structural tokens at IDs 0–11                        (5/5 tests)
Req  4 | [PASS] Verify Candidate A has no unintended special added tokens              (5/5 tests)
Req  5 | [PASS] Verify Candidate B PAD=0 and BOS/EOS/UNK=-1 at runtime                 (9/9 tests)
Req  6 | [PASS] Verify all 256 byte fallback mappings                                  (6/6 tests)
Req  7 | [PASS] Test raw binary round-trip for bytes 0x00–0xFF                         (16/16 tests)
Req  8 | [PASS] Test text round-trip in NFC and exact modes                            (32/32 tests)
Req  9 | [PASS] Test structural-token isolation                                        (68/68 tests)
Req 10 | [PASS] Test save/reload consistency                                           (4/4 tests)
Req 11 | [PASS] Verify SHA-256 hashes against metadata                                 (6/6 tests)
Req 12 | [PASS] Verify Unicode database version is actually 15.1.0                     (2/2 tests)
Req 13 | [PASS] Build twice from identical synthetic inputs and compare artifacts for deterministic output (2/2 tests)

--------------------------------------------------------------------------------
Total Individual Tests Executed: 162
Passed: 162
Failed: 0
Skipped: 0
--------------------------------------------------------------------------------
ARTIFACT HASHES:
  Candidate A (tokenizer.json):  ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561
  Candidate B (tokenizer.model): d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888
================================================================================
```

---

## 4. Cryptographic Artifact Integrity Verification

Candidate A and Candidate B cryptographic hashes remain strictly identical to certified baselines:
- **Candidate A SHA-256**: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- **Candidate B SHA-256**: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
