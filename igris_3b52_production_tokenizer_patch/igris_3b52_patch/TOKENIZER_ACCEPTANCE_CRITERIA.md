# IGRIS Tokenizer Acceptance Criteria & Thresholds Specification

**Document Version**: 1.0.0  
**Milestone**: 3B.59 — Production Evaluation Readiness  
**Target Architecture**: IGRIS Decoder-Only Transformer (Context Length: 2,048, Vocabulary: 32,768)  
**Evaluated Candidates**: Candidate A (ByteLevel BPE) & Candidate B (SentencePiece Unigram)

---

## 1. Overview & Purpose

This document establishes the measurable acceptance metrics, mathematical formulations, and tiered threshold criteria for validating IGRIS tokenizer candidates on the production evaluation corpus. Criteria are partitioned into:
1. **Mandatory Requirements (Hard Gates)**: Zero-tolerance engineering invariants that must pass $100\%$ before a candidate can be approved.
2. **Recommended Targets (Optimization Targets)**: Empirical efficiency and throughput targets expected from full production corpus training.
3. **Informational Metrics (Observability)**: System telemetry and diagnostic metrics recorded for capacity planning.

---

## 2. Metric Formulations & Calculations

| Metric | Notation | Formula / Mathematical Definition | Calculation Methodology |
|:---|:---:|:---|:---|
| **Tokens per Word** | $TPW$ | $TPW = \frac{T}{W} = \frac{\sum_{i=1}^N \text{len}(\text{tokens}_i)}{\sum_{i=1}^N \max(1, \text{len}(\text{words}_i))}$ | Standard whitespace tokenization `len(text.split())` defines word count $W$. Lower indicates better subword compression. |
| **Tokens per Character** | $TPC$ | $TPC = \frac{T}{C} = \frac{\sum_{i=1}^N \text{len}(\text{tokens}_i)}{\sum_{i=1}^N \text{len}(\text{chars}_i)}$ | Codepoint length of NFC normalized text defines character count $C$. |
| **Compression Ratio** | $CR$ | $CR = \frac{B_{\text{UTF-8}}}{T} = \frac{\sum_{i=1}^N \text{len}(\text{encode}_{\text{utf-8}}(\text{text}_i))}{\sum_{i=1}^N \text{len}(\text{tokens}_i)}$ | Bytes per token. Higher indicates greater information density per context slot. |
| **Average Sequence Length** | $\bar{L}$ | $\bar{L} = \frac{1}{N} \sum_{i=1}^N \text{len}(\text{tokens}_i)$ | Arithmetic mean of sequence lengths across all samples in the category or corpus. |
| **95th Percentile Length** | $P_{95}$ | $P_{95} = \text{Quantile}_{0.95}(\{\text{len}(\text{tokens}_1), \dots, \text{len}(\text{tokens}_N)\})$ | 95th percentile of sequence lengths; indicates effective context consumption of long-tail inputs. |
| **Maximum Sequence Length** | $L_{\max}$ | $L_{\max} = \max_{1 \le i \le N} \text{len}(\text{tokens}_i)$ | Longest sequence generated across evaluated samples. |
| **Encoding Throughput** | $TH_{\text{enc}}$ | $TH_{\text{enc}} = \frac{C}{\Delta t_{\text{enc}}} \text{ [chars/s]} \quad\text{or}\quad \frac{T}{\Delta t_{\text{enc}}} \text{ [tokens/s]}$ | High-resolution timer (`time.perf_counter()`) over $R \ge 10$ repeated runs. Reported as **mean** and **median**. |
| **Decoding Throughput** | $TH_{\text{dec}}$ | $TH_{\text{dec}} = \frac{T}{\Delta t_{\text{dec}}} \text{ [tokens/s]} \quad\text{or}\quad \frac{C}{\Delta t_{\text{dec}}} \text{ [chars/s]}$ | High-resolution timer (`time.perf_counter()`) over $R \ge 10$ repeated runs. Reported as **mean** and **median**. |
| **Peak Memory Usage** | $RAM_{\text{peak}}$ | $RAM_{\text{peak}} = \max_{t} \text{AllocatedMemory}(t)$ | Peak heap memory in KiB/MiB tracked via `tracemalloc` across $M \ge 5$ batch encode/decode runs. |
| **Round-Trip Fidelity** | $RF$ | $RF = \frac{\sum_{i=1}^N \mathbb{I}(\text{decode}(\text{encode}(x_i)) == \text{NFC}(x_i))}{N} \times 100\%$ | Strict binary equality between decoded text and canonical NFC input. Must be exactly $100.0\%$. |
| **Unicode Correctness** | $UC$ | $\forall x, \text{decode}_{\text{exact}}(\text{encode}_{\text{exact}}(x)) == x$ | Exact codepoints, canonical equivalences, decomposed forms, and Plane 15/16 characters verified. |
| **Structural Token Isolation** | $STI$ | $\forall x, \forall t \in \text{encode\_content}(x), t \ge 12$ | Content encoding must strictly never emit token IDs in $[0, 11]$. Literal structural spellings are escaped. |

---

## 3. Acceptance Threshold Tiers

All thresholds are configurable via [reports/readiness_3b59/acceptance_thresholds.json](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/reports/readiness_3b59/acceptance_thresholds.json).

### Tier 1: Mandatory Requirements (Hard Gates)
A failure in any mandatory requirement automatically disqualifies the artifact from production deployment.

| Metric | Required Threshold | Verification Method | Enforcement Level |
|:---|:---:|:---|:---:|
| **Round-Trip Fidelity** | $\mathbf{100.0\%}$ | Exact string match across all benchmark samples | **MANDATORY** |
| **Structural Token Isolation** | $\mathbf{100.0\%}$ ($0$ emissions of IDs 0–11) | Content encoding check on diverse adversarial & normal text | **MANDATORY** |
| **Vocabulary Size** | Exactly $\mathbf{32,768}$ entries | `vocab_size == 32768` in wrapper, model, and metadata | **MANDATORY** |
| **Structural Token Positions** | Exactly $\mathbf{12}$ at IDs $\mathbf{0–11}$ | `<|pad|>`..`<|assistant|>` at indices 0 through 11 | **MANDATORY** |
| **Byte Fallback Completeness** | Exactly $\mathbf{256}$ byte mappings | Complete mapping for bytes `0x00`–`0xFF` in $[0, 32768)$ | **MANDATORY** |
| **Unicode Database Version** | Strictly $\mathbf{15.1.0}$ | `unicodedata2.unidata_version == "15.1.0"` | **MANDATORY** |
| **Context Length Compatibility** | Exactly $\mathbf{2,048}$ tokens | Sequence classification, exact truncation, chunking verification | **MANDATORY** |
| **Build Determinism** | Bit-for-bit identical SHA-256 | Independent builds from identical inputs yield equal hash | **MANDATORY** |

### Tier 2: Recommended Targets (Production Training Targets)
These criteria represent optimization targets to be evaluated once the tokenizer is trained on the full production corpus.

| Metric | Target Threshold | Scope | Rationale |
|:---|:---:|:---|:---|
| **English Compression ($TPW$)** | $\le \mathbf{1.35}$ | Production trained model | Standard subword compression for English technical text. |
| **Tamil Compression ($TPW$)** | $\le \mathbf{2.50}$ | Production trained model | Subword compression for morphologically rich agglutinative Tamil. |
| **Hindi Compression ($TPW$)** | $\le \mathbf{2.20}$ | Production trained model | Subword compression for Devanagari script and complex conjuncts. |
| **Code Compression ($TPW$)** | $\le \mathbf{1.80}$ | Production trained model | Efficient tokenization of programming language syntax and keywords. |
| **Encoding Throughput (Median)** | $\ge \mathbf{250,000}$ chars/sec | Single-core CPU evaluation | Prevents tokenizer from becoming an inference serving bottleneck. |
| **Decoding Throughput (Median)** | $\ge \mathbf{1,000,000}$ tokens/sec | Single-core CPU evaluation | High-speed autoregressive token-to-text generation. |
| **Sequence Length $P_{95}$** | $\le \mathbf{1,800}$ tokens | Production evaluation samples | Leaves sufficient context margin for multi-turn conversational framing. |

> [!NOTE]
> On the current synthetic artifacts, Indic $TPW$ reflects byte-fallback piece frequencies ($11.78$ for Tamil, $8.73$ for Hindi) because the synthetic training corpus contained only 10 sentences. Full production corpus training with balanced multilingual allocations will achieve the Tier 2 recommended compression targets.

### Tier 3: Informational Metrics (Observability)
Recorded for telemetry and runtime profiling:
1. **Tokens per Character ($TPC$)** across all 10 evaluation categories.
2. **Compression Ratio ($CR$)** (UTF-8 bytes per token).
3. **Peak Heap Allocation ($RAM_{\text{peak}}$)**: Baseline target $\le 1,024 \text{ KB}$ per single-thread batch ingestion.
4. **Subword Vocabulary Script Distribution**: Percentage allocation of vocabulary across Tamil, Latin, Devanagari, Common/Punctuation, and Reserved/Byte pieces.
