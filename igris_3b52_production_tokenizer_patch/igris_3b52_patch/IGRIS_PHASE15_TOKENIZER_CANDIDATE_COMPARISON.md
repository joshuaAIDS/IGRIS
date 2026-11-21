# IGRIS PHASE 15: CANDIDATE COMPARISON REPORT

**Document Identifier**: `IGRIS-P15-CCR-2026-V1`  
**Execution Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Artifact Status**: Immutable & Invariant  
**Evaluator**: [tokenizer_candidate_comparison.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/tokenizer_candidate_comparison.py)

---

## 1. Candidate Identification and Metadata

| Attribute | Candidate A | Candidate B |
| :--- | :--- | :--- |
| **Model Type** | ByteLevel BPE (Byte-Pair Encoding) | Unigram Language Model |
| **Engine Framework** | Hugging Face `tokenizers` (0.23.3) | Google `sentencepiece` (0.2.3) |
| **Artifact Format** | `tokenizer.json` | `tokenizer.model` (Protocol Buffer) |
| **Artifact Path** | [artifacts/tokenizer/candidate_a/tokenizer.json](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_a/tokenizer.json) | [artifacts/tokenizer/candidate_b/tokenizer.model](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_b/tokenizer.model) |
| **Verified SHA-256 Hash** | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` |
| **Total Vocabulary Size** | **32,768** | **32,768** |
| **Pinned Structural Tokens** | 12 tokens (IDs 0–11) | 12 tokens (IDs 0–11) |
| **Byte Fallback Capacity** | 256 individual bytes (`<0x00>`–`<0xFF>`) | 256 individual bytes (`<0x00>`–`<0xFF>`) |
| **PAD Token ID** | 0 (`<|pad|>`) | 0 (`<|pad|>`) |
| **Runtime UNK ID** | Not exposed (byte-level guaranteed) | `-1` (Runtime byte-fallback handled) |
| **Production Authorization**| **NOT AUTHORIZED** (Pending Owner Ingress Gate) | **NOT AUTHORIZED** (Pending Owner Ingress Gate) |

---

## 2. Side-by-Side Performance and Quality Comparison

### 2.1 Per-Language Tokenization Metrics

| Evaluation Category | Candidate A Tokens | Candidate B Tokens | Cand A Fertility (tok/word) | Cand B Fertility (tok/word) | Fertility Delta ($\Delta\%$) | Cand A Compression (chars/tok) | Cand B Compression (chars/tok) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **English** | 696 | 708 | **7.2500** | 7.3750 | +1.72% | 1.1580 | 1.1384 |
| **Hindi** | 766 | 791 | **7.9792** | 8.2396 | +3.26% | 0.6984 | 0.6764 |
| **Tamil** | 880 | 967 | **11.4286** | 12.5584 | +9.89% | 0.8761 | 0.7973 |
| **Telugu** | 1,247 | 1,247 | **23.5283** | 23.5283 | 0.00% | 0.3649 | 0.3649 |
| **Malayalam** | 1,342 | 1,342 | **26.8400** | 26.8400 | 0.00% | 0.3607 | 0.3607 |
| **Kannada** | 1,238 | 1,238 | **24.2745** | 24.2745 | 0.00% | 0.3651 | 0.3651 |
| **Bengali** | 1,345 | 1,339 | 20.6923 | **20.6000** | -0.45% | 0.3665 | 0.3682 |
| **Gujarati** | 1,194 | 1,194 | **16.5833** | 16.5833 | 0.00% | 0.3769 | 0.3769 |
| **Tanglish** | 363 | 365 | **5.9508** | 5.9836 | +0.55% | 1.1047 | 1.0986 |
| **Code-Switching** | 671 | 682 | **9.5857** | 9.7429 | +1.64% | 0.7750 | 0.7625 |
| **Robustness** | 2,361 | 2,484 | **8.3428** | 8.7774 | +5.21% | 1.1817 | 1.1232 |
| **Overall Benchmark** | **12,103** | **12,357** | **12.4261** | **12.6869** | **+2.10%** | **0.6740** | **0.6601** |

---

## 3. Operational Throughput and Latency Measurements

| Operational Dimension | Candidate A (ByteLevel BPE) | Candidate B (SentencePiece) | Comparative Analysis |
| :--- | :---: | :---: | :--- |
| **Encoding Speed (Chars/sec)** | 557,955.71 | **726,697.05** | Candidate B is **1.30x faster** in encoding raw characters |
| **Encoding Speed (Tokens/sec)**| 827,875.12 | **1,100,883.40** | Candidate B is **1.33x faster** in generating tokens |
| **Decoding Speed (Tokens/sec)**| 2,773,156.99 | **4,021,727.81** | Candidate B is **1.45x faster** in decoding token sequences |
| **Short-Doc Latency (Single sentence)** | 0.1235 ms | **0.0599 ms** | Candidate B processes interactive queries **2.06x faster** |
| **Long-Doc Latency (2,000 chars)** | 3.2721 ms | **2.3196 ms** | Candidate B sustains **1.41x faster** batch encoding |
| **Peak Heap Allocation** | **54.29 KB** | 101.35 KB | Candidate A requires **46.4% less heap memory** |
| **Unknown Token Rate** | **0.00%** | **0.00%** | Both achieve zero unknown tokens via byte fallback |
| **Lossless Round-Trip Rate** | **100.0%** | **100.0%** | Both achieve complete mathematical exact round-trip |

---

## 4. Linguistic Strengths, Weaknesses, and Known Limitations

### 4.1 Candidate A (ByteLevel BPE)
- **Strengths**:
  - Lowest overall token count on the evaluation suite (12,103 tokens vs 12,357 tokens, a 2.10% compression advantage).
  - Superior Tamil fertility (11.43 vs 12.56 tokens/word, 9.89% fewer tokens).
  - Superior Hindi fertility (7.98 vs 8.24 tokens/word, 3.26% fewer tokens).
  - Minimal heap overhead (54.29 KB peak).
  - Native JSON format allows direct introspection of merges and vocabulary without protobuf parsing.
- **Limitations**:
  - Slower encoding and decoding throughput compared to SentencePiece C++ backend ($1.30\times$ slower encoding, $1.45\times$ slower decoding).
  - Higher short-document latency (0.1235 ms vs 0.0599 ms).

### 4.2 Candidate B (SentencePiece Unigram)
- **Strengths**:
  - Significantly faster throughput across all workloads (726K chars/sec encoding, 4.02M tokens/sec decoding).
  - Extremely low interactive query latency (0.0599 ms for short prompts).
  - Highly robust unigram probabilistic regularization capability during training.
  - Consistent tokenization boundaries across diverse script families.
- **Limitations**:
  - Slightly higher token count on Tamil (+9.89%) and Hindi (+3.26%) on the current pre-pilot synthetic vocabulary.
  - Higher heap footprint during batch execution (101.35 KB vs 54.29 KB).
  - Binary Protocol Buffer format requires external tooling (`protoc` or `sentencepiece_model_pb2`) for inspection.

### 4.3 Unavailable Measurements
The following measurements were **NOT_MEASURED** during Phase 15:
- **Full Production Corpus Perplexity / Cross-Entropy**: Marked `NOT_MEASURED` because model pre-training is not authorized in Phase 15, and no language model weights have been trained.
- **Downstream Task Fine-Tuning Performance**: Marked `NOT_MEASURED` because downstream evaluation requires trained transformer checkpoints.

---

## 5. Comparative Verdict and Recommendations

$$\boxed{\textbf{EVALUATION VERDICT: BOTH CANDIDATES TECHNICALLY VIABLE — TRADE-OFF DOCUMENTED.}}$$

- **Candidate A** is superior if the primary optimization objective is **minimum context window consumption** and **maximum subword compression** for Tamil and Hindi (saving ~2–10% of context tokens).
- **Candidate B** is superior if the primary optimization objective is **inference / serving throughput** and **low query latency** ($1.30\times$–$1.45\times$ speedup).

Neither candidate is declared the definitive production winner at Phase 15. The final selection will be made after the owner explicitly authorizes training with the 18 permissive multilingual production datasets.
