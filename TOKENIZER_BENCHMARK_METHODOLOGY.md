# IGRIS Tokenizer Benchmark Methodology & Performance Specification

**Document Identifier:** `IGRIS-SPEC-TOKENIZER-BENCHMARK-V1`  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  

---

## 1. Hardware, Environment & Software Specifications

All benchmark throughput measurements were captured under identical, controlled conditions on the host development machine:

- **Operating System:** Windows 11 Enterprise (Build 10.0.26300)
- **Processor:** Intel64 Family 6 Model 186 Stepping 2, GenuineIntel
- **Machine Architecture:** AMD64
- **Python Runtime:** Python 3.11.9
- **Tokenizer Engine:** Hugging Face Tokenizers (Rust Core) v0.23.3
- **Unicode Database:** Unicode Standard v15.1.0

---

## 2. Benchmark Protocol & Warm-Up Procedure

To eliminate JIT compilation artifacts, OS page-fault overhead, and disk cache latencies, the benchmark employed a multi-stage protocol:

1. **Corpus Pre-loading:** All 399 synthetic text fixtures were pre-loaded into memory and NFC-normalized.
2. **Warm-Up Phase:** Executed **10 complete corpus passes** (3,990 text encodings per candidate) before initiating performance timers.
3. **Measurement Phase:** Executed **5 consecutive full-corpus repetitions** using high-resolution monotonic timers (`time.perf_counter()`).
4. **Timing Scope:** Timings measure **raw tokenization and detokenization only**, excluding file I/O and pre-processing text normalization.

---

## 3. Empirical Throughput Results

| Operation | Metric | Original Candidate A | Experimental Candidate A | Variance / Relative Impact |
|---|---|:---:|:---:|:---:|
| **Encode** | Mean Time per Corpus Run | 0.0181 s | 0.0173 s | - |
| **Encode** | Standard Deviation | 0.0004 s | 0.0003 s | Low jitter |
| **Encode Throughput** | **Words / Second** | **230,436.9** | **240,901.8** | **+4.5% Faster** |
| **Encode Throughput** | **Characters / Second** | **1,525,488.2** | **1,594,764.0** | **+4.5% Faster** |
| **Encode Latency** | Mean Latency per Document | 0.045 ms | 0.043 ms | Sub-millisecond |
| **Decode** | Mean Time per Corpus Run | 0.0040 s | 0.0025 s | - |
| **Decode Throughput** | **Words / Second** | **1,049,657.8** | **1,646,245.1** | **+56.8% Faster** |
| **Decode Latency** | Mean Latency per Document | 0.010 ms | 0.006 ms | Sub-millisecond |

### Throughput Analysis:
Experimental Candidate A achieves substantially higher decode throughput (+56.8%) because it emits **54.4% fewer token IDs** per document, reducing the number of token ID lookups and string concats required during decoding.

---

## 4. Methodological Distinction: Full Text Coverage vs. Active Utilization

In subword tokenizer evaluation, conflating byte fallback coverage with learned vocabulary coverage is a common methodological error:

1. **Full Text Coverage (100.0% for both tokenizers):**
   - Both tokenizers implement ByteLevel BPE with initial alphabet size 256. Consequently, neither tokenizer ever emits an `<unk>` token. Every arbitrary Unicode character or malformed byte sequence can be represented.
2. **Active Vocabulary Utilization (Empirical Vocabulary Footprint):**
   - Refers to the fraction of the 32,768 vocabulary slots actively utilized by learned merges on the evaluation corpus.
   - On the 399 synthetic records:
     - Candidate A uses only **286 tokens** (0.87% of vocabulary) because it has only 63 learned merges.
     - Experimental Candidate A uses **885 tokens** (2.70% of vocabulary) across 1,755 learned merges.
3. **Subword Fertility:**
   - Defined as the average number of tokens generated per whitespace-delimited word. Lower fertility indicates longer subwords and superior compression efficiency.

---

## 5. Scope Limitations & Caveats

> [!WARNING]
> **Limitations of Small Synthetic Evaluation:**  
> The 399-record corpus represents a focused synthetic test harness totaling 4,165 words. While this provides a rigorous, controlled test of tokenizer mechanical behavior, NFC stability, and relative compression efficiency:
> - It **cannot establish real-world production quality** on diverse web-scale Tamil or English literature.
> - Final vocabulary design for IGRIS pretraining requires web-scale pretraining data (e.g. Tamil news, Wikipedia, domain technical documents) acquired under formal owner approval.
