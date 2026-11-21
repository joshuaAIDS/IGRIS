# IGRIS Runtime Test & Verification Report

**Engineering Role**: Senior ML Systems Engineer  
**Scope**: Local Inference Engine, Candidate A Tokenizer, HTTP/SSE API, Frontend Integration  
**Date**: November 2026  
**Overall Verdict**: **100% PASS (All Suites Green, Zero Regressions)**  

---

## 1. Executive Summary

This report documents the verification and quality assurance runs conducted across the IGRIS codebase following the implementation of the local Python inference runtime, Candidate A tokenizer integration, and frontend connectivity updates.

All test inputs used throughout the verification procedure were synthetic. In accordance with project governance mandates:
- No production datasets were downloaded.
- No model pretraining runs were initiated.
- No external third-party AI APIs were contacted.
- Candidate A tokenizer invariant SHA-256 was verified with zero modifications.

---

## 2. Test Execution Breakdown

### 2.1 Local Inference Runtime Unit Tests

- **Runner**: Python `unittest` (`c:\IGRIS\.venv\Scripts\python.exe`)
- **Target**: `tests/test_inference_runtime.py`
- **Results**: **13 Passed / 0 Failed / 0 Errors** (Duration: 2.56s)

| Test ID | Test Name | Target Functionality | Result |
| :---: | :--- | :--- | :---: |
| `test_01` | `test_candidate_a_tokenizer_integrity` | Cryptographic SHA-256 hash match (`ac7e18b1...`), vocab size 32,768 | **PASS** |
| `test_02` | `test_trilingual_tokenizer_encoding` | True BPE token counting for English, Tamil Unicode, and Tanglish | **PASS** |
| `test_03` | `test_hardware_inspection_and_vram_profiling` | Target RTX 3050 6GB detection, VRAM headroom, safe fallback check | **PASS** |
| `test_04` | `test_architecture_parameter_counts` | Production 79.7M (tied) / Baseline 51.6M (tied) parameter counts | **PASS** |
| `test_05` | `test_health_endpoint` | `GET /health` schema, tokenizer status, model status `MODEL_NOT_TRAINED` | **PASS** |
| `test_06` | `test_models_endpoint` | `GET /v1/models` registry containing `prod-16l`, `50m-baseline`, `candidate-a` | **PASS** |
| `test_07` | `test_untrained_chat_completion_reports_model_not_trained` | `POST /v1/chat/completions` returns HTTP 503 `MODEL_NOT_TRAINED` when weights missing | **PASS** |
| `test_08` | `test_invalid_chat_request_handling` | Empty messages or invalid payload returns HTTP 400 Bad Request | **PASS** |
| `test_09` | `test_synthetic_trained_mode_autoregressive_and_streaming` | Autoregressive forward pass, GQA/RoPE/SwiGLU, SSE generator, real token usage | **PASS** |
| `test_10` | `test_synthetic_streaming_cancellation` | Client abort signal immediately terminates generation and marks `abort` | **PASS** |
| `test_11` | `test_trilingual_synthetic_generation` | Trilingual prompts (Tamil Unicode, Tanglish) processed cleanly through generation | **PASS** |
| `test_12` | `test_out_of_memory_handling` | `torch.cuda.OutOfMemoryError` caught cleanly, returning HTTP 503 without crash | **PASS** |
| `test_13` | `test_v1_health_alias` | `GET /v1/health` verified as identical valid alias to `GET /health` | **PASS** |

---

### 2.2 Unicode 15.1 Compliance Suites

Ensures strict compliance with official Unicode 15.1 standards for Dravidian graphemes and Tamil Unicode codepoints (`U+0B80`–`U+0BFF`).

1. **Normalization Conformance**:
   - **Script**: `unicode_15_1_tests/run_normalization.py`
   - **Assertions**: 190,740 assertions across NFC, NFD, NFKC, and NFKD
   - **Failures**: 0
   - **Verdict**: **PASS**

2. **Grapheme Cluster Break Conformance**:
   - **Script**: `unicode_15_1_tests/run_grapheme.py`
   - **Official Cases**: 1,187 test cases
   - **Failures**: 0
   - **Verdict**: **PASS**

---

### 2.3 Candidate A Configuration Suite

- **Script**: `igris_candidate_a_v228.py`
- **Configuration Checks**:
  1. BPE model construction: **PASS**
  2. ByteLevel pre-tokenizer: **PASS**
  3. ByteLevel decoder: **PASS**
  4. 32,768 vocabulary target configured: **PASS**
  5. 12 structural tokens ordered: **PASS**
  6. 256-byte initial alphabet configured: **PASS**
  7. Pretraining status unstarted: **PASS**
- **Verdict**: **PASS (7/7 checks passed)**

---

### 2.4 Frontend Unit Tests

- **Runner**: Node.js `tsx --test`
- **Target**: `frontend/src/**/*.test.ts`
- **Results**: **28 Passed / 0 Failed** (Duration: 4.05s)

| Module | Tests | Functionality Verified |
| :--- | :---: | :--- |
| `conversation.test.ts` | 4 | Session creation, message ordering, clearing session, multi-session switching/deletion |
| `inference.test.ts` | 7 | Demo adapter simulation, trilingual responses (en/ta/tanglish), streaming chunks, abort cancellation, HTTP connection refusal error, offline health check |
| `language.test.ts` | 5 | Strict 3-language limitation (en, ta, tanglish), regex detection for Tamil Unicode, Tanglish phonetics, English default |
| `tokenizer_candidate_a.test.ts` | 4 | 12 structural tokens in specification order, 32,768 vocab, trilingual token estimation ratios, prompt formatting |
| `liquidGlassProximity.test.ts` | 3 | Proximity radius math, monotonic decrease, frost glass shift clamping |
| `studioEngine.test.ts` | 5 | Token estimation, metric formatting, model catalog query filtering, deterministic SLM demo responses, throughput series |

---

### 2.5 Production Frontend Build

- **Runner**: Vite v8.3.8 / Rollup
- **Command**: `npm run build` in `frontend/`
- **Output**:
  - `dist/index.html`: 1.37 kB (gzip: 0.60 kB)
  - `dist/assets/index-gUmIQeKj.css`: 55.88 kB (gzip: 10.13 kB)
  - `dist/assets/index-Gfd6Mzsp.js`: 857.28 kB (gzip: 231.04 kB)
- **Duration**: **583 ms**
- **Status**: **ZERO ERRORS**
