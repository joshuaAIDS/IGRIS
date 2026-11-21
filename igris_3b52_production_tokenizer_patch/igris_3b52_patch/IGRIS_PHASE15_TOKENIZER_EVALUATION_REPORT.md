# IGRIS PHASE 15: TOKENIZER EVALUATION REPORT

**Document Identifier**: `IGRIS-P15-TER-2026-V1`  
**Execution Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Evaluation Framework**: [tokenizer_evaluation.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/tokenizer_evaluation.py)  
**Status**: `READ_ONLY_AUDIT_COMPLETE — INVARIANTS PRESERVED`

---

## 1. Executive Summary

Phase 15 executed an exhaustive, reproducible, read-only evaluation of the two certified candidate tokenizer artifacts for the **IGRIS Multilingual Decoder-Only Transformer**:
- **Candidate A**: ByteLevel BPE (`tokenizer.json`, Hugging Face Tokenizers engine)  
  SHA-256: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- **Candidate B**: SentencePiece Unigram (`tokenizer.model`, SentencePiece engine)  
  SHA-256: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`

Both candidate artifacts were evaluated strictly in **read-only mode**. Neither artifact was modified, replaced, or retrained.

### Key Evaluation Findings
1. **100.0% Round-Trip Fidelity**: Both Candidate A and Candidate B achieve 100.0% exact lossless round-trip decoding across all 11 evaluation categories and 35 benchmark text samples.
2. **0.0% Unknown-Token Rate**: Both candidates utilize 256-byte fallback vocabularies, ensuring that any Unicode codepoint, emoji, or malformed byte sequence is decoded losslessly with zero unknown (`<unk>`) token emissions.
3. **Indic Unicode Script Preservation**: Both tokenizers preserve dependent vowel signs, matras, viramas, conjuncts, and context-aware ZWJ (`\u200D`) and ZWNJ (`\u200C`) ligatures without normalization drift or semantic destruction.
4. **Throughput Performance**: Candidate B (SentencePiece C++ backend) demonstrated higher raw encoding throughput (726,697 chars/sec vs 557,955 chars/sec, a $1.30\times$ speedup) and decoding throughput (4.02M tokens/sec vs 2.77M tokens/sec, a $1.45\times$ speedup).
5. **Memory Footprint**: Candidate A demonstrated a smaller peak memory overhead during batch evaluation (54.29 KB vs 101.35 KB).

---

## 2. Evaluation Methodology & Measurement Environment

### 2.1 Host Environment
- **Operating System**: Windows 11 Enterprise (`win32`)
- **Python Version**: 3.11.9
- **Processor**: Intel/AMD 64-bit Architecture
- **SentencePiece Version**: 0.2.3
- **Tokenizers Version**: 0.23.3
- **Unicode Database Standard**: Unicode 15.1.0

### 2.2 Benchmarking Protocol
- **Corpus**: Standardized 11-category benchmark suite [tokenizer_multilingual_benchmark.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/tokenizer_multilingual_benchmark.py) containing 35 diverse test texts.
- **Warmup**: Every tokenizer undergoes full warmup iterations on all samples prior to timing.
- **Timing**: Repeated iterations measured with microsecond precision via `time.perf_counter()`.
- **Memory**: Peak heap allocation measured using Python's `tracemalloc` profiler.

---

## 3. Multilingual Coverage & Fertility Measurements

Fertility is measured as **Tokens per Word** ($\text{Fertility} = \frac{\text{Tokens}}{\text{Words}}$). Lower fertility indicates superior subword aggregation and vocabulary efficiency.

| Language / Category | Sample Count | Total Words | Cand A Tokens | Cand B Tokens | Cand A Fertility | Cand B Fertility | Difference |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** (`en`) | 4 | 96 | 696 | 708 | **7.2500** | 7.3750 | +1.72% |
| **Hindi** (`hi`) | 3 | 96 | 766 | 791 | **7.9792** | 8.2396 | +3.26% |
| **Tamil** (`ta`) | 4 | 77 | 880 | 967 | **11.4286** | 12.5584 | +9.89% |
| **Telugu** (`te`) | 3 | 53 | 1,247 | 1,247 | **23.5283** | 23.5283 | 0.00% |
| **Malayalam** (`ml`)| 3 | 50 | 1,342 | 1,342 | **26.8400** | 26.8400 | 0.00% |
| **Kannada** (`kn`) | 3 | 51 | 1,238 | 1,238 | **24.2745** | 24.2745 | 0.00% |
| **Bengali** (`bn`) | 3 | 65 | 1,345 | 1,339 | 20.6923 | **20.6000** | -0.45% |
| **Gujarati** (`gu`) | 3 | 72 | 1,194 | 1,194 | **16.5833** | 16.5833 | 0.00% |
| **Tanglish** (`tanglish`)| 3 | 61 | 363 | 365 | **5.9508** | 5.9836 | +0.55% |
| **Code-Switching** | 4 | 70 | 671 | 682 | **9.5857** | 9.7429 | +1.64% |
| **Robustness / Stress** | 5 | 283 | 2,361 | 2,484 | **8.3428** | 8.7774 | +5.21% |
| **OVERALL TOTAL** | **35** | **974** | **12,103** | **12,357** | **12.4261** | **12.6869** | **+2.10%** |

### Observations on Multilingual Subword Aggregation
- **High English and Tanglish Efficiency**: Both candidates demonstrate compact tokenization on English (7.25 vs 7.38 tokens/word) and Tanglish (5.95 vs 5.98 tokens/word).
- **Tamil and Hindi Differences**: Candidate A exhibits a 9.89% fertility advantage on Tamil (11.43 vs 12.56 tokens/word) and a 3.26% advantage on Hindi (7.98 vs 8.24 tokens/word), reflecting BPE merge frequency characteristics on the initial pilot dataset.
- **South Asian Low-Resource Baseline**: Telugu, Malayalam, Kannada, and Gujarati exhibit identical fertility across both candidates (e.g. 23.53, 26.84, 24.27, 16.58). Because these languages were not part of the initial synthetic pre-pilot vocabulary optimization, both candidates tokenize them at the granular character and byte-fallback level. This will improve once production training with the authorized 18 permissive corpora is approved.

---

## 4. Indic Script Integrity & Robustness Evaluation

The dedicated Indic integrity suite [tokenizer_unicode_tests.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/tokenizer_unicode_tests.py) executed 28 specialized vectors:

| Test Dimension | Test Cases | Cand A Result | Cand B Result | Verification Note |
| :--- | :---: | :---: | :---: | :--- |
| **Tamil Matras & Pulli** | 4 | **100% PASS** | **100% PASS** | Consonants with pulli and dependent vowel signs round-trip losslessly |
| **Hindi Matras & Halant** | 4 | **100% PASS** | **100% PASS** | Halant conjuncts, nuktas, and candrabindu preserved |
| **Telugu Wattulu & Vowels**| 3 | **100% PASS** | **100% PASS** | Subscript consonants and vowel signs preserved |
| **Malayalam Chillu & ZWJ** | 4 | **100% PASS** | **100% PASS** | Atomic chillu (U+0D7A-U+0D7F) and virama+ZWJ sequences preserved |
| **Kannada Ottu Forms** | 2 | **100% PASS** | **100% PASS** | Ottu subscripts and consonant clusters preserved |
| **Bengali Yuktakshar** | 2 | **100% PASS** | **100% PASS** | Hasant conjuncts preserved |
| **Gujarati Conjuncts** | 2 | **100% PASS** | **100% PASS** | Matras and viramas preserved |
| **Zero-Width & NFC** | 2 | **100% PASS** | **100% PASS** | ZWNJ conjunct prevention and canonical NFC normalization verified |
| **Robustness Vectors** | 5 | **100% PASS** | **100% PASS** | Empty string (`[]`), repeated chars, emoji, and 2000+ char texts pass |
| **Total Integrity Suite** | **28** | **28 / 28 PASS** | **28 / 28 PASS** | **100.0% Pass Rate across both candidates** |

---

## 5. Performance and Throughput Benchmarks

| Metric | Candidate A (ByteLevel BPE) | Candidate B (SentencePiece) | Speedup / Ratio |
| :--- | :---: | :---: | :---: |
| **Encoding Throughput** | **557,955 chars/sec** | **726,697 chars/sec** | $1.30\times$ (Candidate B faster) |
| **Encoding Throughput (Tokens)** | **827,875 tokens/sec** | **1,100,883 tokens/sec** | $1.33\times$ (Candidate B faster) |
| **Decoding Throughput** | **2,773,157 tokens/sec**| **4,021,728 tokens/sec** | $1.45\times$ (Candidate B faster) |
| **Encoding Latency** | **1.8353 ms/KB** | **1.4091 ms/KB** | $1.30\times$ (Candidate B faster) |
| **Short Document Latency (~50 chars)**| **0.1235 ms** | **0.0599 ms** | $2.06\times$ (Candidate B faster) |
| **Long Document Latency (~2000 chars)**| **3.2721 ms** | **2.3196 ms** | $1.41\times$ (Candidate B faster) |
| **Peak Heap Allocation** | **54.29 KB** | **101.35 KB** | $1.87\times$ (Candidate A leaner) |

---

## 6. Evaluation Verification Status

Both candidates successfully fulfill all read-only evaluation criteria. All automated verification tests pass in [test_phase15_tokenizer_infrastructure.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_phase15_tokenizer_infrastructure.py).
