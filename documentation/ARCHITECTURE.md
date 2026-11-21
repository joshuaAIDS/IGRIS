# IGRIS — System Architecture & Technical Specifications

---

## 1. Architectural Philosophy

IGRIS is constructed as a modular, high-efficiency cognitive architecture comprising six core layers:
1. **Transformer SLM Core**: Autoregressive neural engine (~50M parameters, configurable).
2. **Trilingual BPE Tokenizer**: Unified subword vocabulary for English, Tamil Unicode, and Tanglish.
3. **Modular Audio Pipeline**: Wake-word spotter ("Hey IGRIS"), VAD, modular ASR, and male TTS.
4. **Cognitive Agent Engine**: Chain-of-Thought (CoT) reasoning, tool use, and self-reflection.
5. **Personal Memory Layer**: Hierarchical episodic and semantic vector storage.
6. **Permission-Gated Desktop Controller**: Sandboxed OS bridge and automation safety layer.

---

## 2. Transformer SLM Core Specification

The language model is a custom, decoder-only autoregressive Transformer implemented from first principles.

### 2.1 Baseline Architecture Parameters (Configurable ~50M Target)

```yaml
# configs/model_50m_baseline.yaml
model:
  name: "igris-50m-v1"
  vocab_size: 32768            # Unified English + Tamil + Tanglish vocabulary
  hidden_size: 512             # d_model
  intermediate_size: 1376      # SwiGLU hidden dimension (approximately 8/3 * hidden_size)
  num_hidden_layers: 12        # Number of Transformer decoder layers
  num_attention_heads: 8       # Query attention heads (d_head = 64)
  num_key_value_heads: 4       # Grouped Query Attention (GQA) with 2:1 sharing ratio
  max_position_embeddings: 2048 # Context window length
  rms_norm_eps: 1.0e-5         # Root Mean Square Normalization epsilon
  rope_theta: 10000.0          # Rotary Position Embedding base frequency
  tie_word_embeddings: false   # Separate input/output projection matrices
  dropout: 0.0                 # Standard modern pretraining zero-dropout
  dtype: "float16"             # Execution precision for NVIDIA RTX 3050
```

### 2.2 Mathematical Formulations

#### Rotary Position Embeddings (RoPE)
Applied to query ($Q$) and key ($K$) projections at each attention layer to guarantee translation invariance and relative distance decay:
$$R_{\Theta, m}^d = \text{diag}\left(R_{\theta_1, m}, R_{\theta_2, m}, \dots, R_{\theta_{d/2}, m}\right)$$
where each $2 \times 2$ submatrix rotates the orthogonal 2D feature subspace by angle $m \theta_i$.

#### RMSNorm (Root Mean Square Layer Normalization)
Replaces standard LayerNorm to eliminate mean-centering overhead while preserving scale invariance:
$$\text{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{d}\sum_{i=1}^d x_i^2 + \epsilon}} \odot \gamma$$

#### SwiGLU Activation Function
Utilized within the Feed-Forward Network (FFN) blocks for superior gradient flow compared to ReLU or standard GELU:
$$\text{SwiGLU}(x) = \left(x W_{\text{gate}} \cdot \text{SiLU}(x W_{\text{gate}})\right) \odot (x W_{\text{up}})$$
$$\text{FFN}(x) = \text{SwiGLU}(x) W_{\text{down}}$$

#### Grouped-Query Attention (GQA)
Uses 8 query heads and 4 key-value heads (2 query heads per KV head). This halves KV-cache memory consumption and accelerates inference on the RTX 3050 GPU without degrading expressivity.

---

## 3. Trilingual Tokenizer Architecture

The tokenizer is a custom Byte-Pair Encoding (BPE) engine constructed with the `tokenizers` library and customized pre-tokenization regex rules.

```
+---------------------------------------------------------------------------------------+
|                              TRILINGUAL BPE PIPELINE                                  |
+---------------------------------------------------------------------------------------+
|  Input Text (English, Tamil Unicode: தமிழ், Tanglish: "Enna panreenga?")             |
+---------------------------------------------------------------------------------------+
                                           │
                                           ▼
+---------------------------------------------------------------------------------------+
|  Pre-Tokenizer Regex Splitting & Normalization (NFC Unicode Standard)                 |
|  - Isolates English words, contractions, numbers, and symbols                         |
|  - Clusters Tamil grapheme clusters & Uyirmei compound syllables                      |
|  - Normalizes colloquial Tanglish Latin digraphs (e.g., 'zh', 'dh', 'th')             |
+---------------------------------------------------------------------------------------+
                                           │
                                           ▼
+---------------------------------------------------------------------------------------+
|  Byte-Fallback Subword Tokenizer (~32,768 vocabulary)                                 |
|  - 256 Raw Byte Tokens (0x00 - 0xFF): Guarantees zero `<unk>` fallback                |
|  - English Frequent Subwords (~12,000 tokens)                                         |
|  - Tamil Unicode Characters & Compounds (~10,000 tokens)                              |
|  - Romanized Tanglish Frequent Syllables & Words (~8,000 tokens)                      |
|  - Control & Special Tokens (~2,500 tokens: `<pad>`, `<bos>`, `<eos>`, `<think>`,     |
|    `</think>`, `<action>`, `</action>`, `<action_result>`)                            |
+---------------------------------------------------------------------------------------+
```

### 3.1 Token Fragmentation Evaluation Metrics
To prevent disproportionate token inflation on non-English inputs, the build system evaluates:
1. **Tokens-per-Word (TPW)**:
   $$\text{TPW} = \frac{\sum \text{Tokens}}{\sum \text{Whitespace-Delimited Words}}$$
   - Target for English: $1.15 \le \text{TPW} \le 1.30$
   - Target for Tamil Unicode: $1.30 \le \text{TPW} \le 1.65$ (standard tokenizers frequently exceed $3.5+$)
   - Target for Tanglish: $1.20 \le \text{TPW} \le 1.45$
2. **Byte-to-Token Ratio (BTR)**:
   $$\text{BTR} = \frac{\text{Total UTF-8 Bytes}}{\text{Total Tokens}}$$
   Higher BTR indicates dense subword compression and efficient sequence utilization.

---

## 4. Modular Speech & Audio Subsystem

IGRIS incorporates an end-to-end voice loop designed with strict abstraction layers:

```
                  ┌──────────────────────────────────────────────┐
                  │              Microphone Input                │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │     Wake-Word Spotter: "Hey IGRIS"           │
                  │   (Continuous, low-overhead listening)       │
                  └──────────────────────┬───────────────────────┘
                                         │ (Triggered)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │       Voice Activity Detection (VAD)         │
                  │    (Detects speech boundaries & barge-in)    │
                  └──────────────────────┬───────────────────────┘
                                         │ (Speech Audio Chunk)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │         Modular ASR Adapter Engine           │
                  │     (Local speech-to-text transcription)     │
                  └──────────────────────┬───────────────────────┘
                                         │ (Transcribed Text)
                                         ▼
+---------------------------------------------------------------------------------------+
|  IGRIS SLM CORE (Proprietary Autoregressive Transformer)                               |
|  - Ingests user transcript and episodic memory                                        |
|  - Conducts reasoning in `<think>` block                                              |
|  - Emits conversational text stream & optional system actions                         |
+---------------------------------------------------------------------------------------+
                                         │ (Streamed Response Tokens)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │          Modular Male TTS Synthesizer        │
                  │  (Natural conversational acoustic synthesis) │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │               Speaker Output                 │
                  └──────────────────────────────────────────────┘
```

### 4.1 Speech Subsystem Governance & Attribution
- **Wake-Word Detection**: Lightweight neural acoustic model specifically keyed to the phonetic signature of *"Hey IGRIS"*.
- **ASR & TTS Modules**: Implemented as swappable interfaces in `src/igris/audio/`. External open-source speech models may be deployed as temporary runtime backends during development, but are clearly documented as third-party modules and never claimed as original IGRIS neural architectures.
- **Continuous Conversation**: Once triggered by the wake word, the conversational session remains open via VAD until a prolonged silence or an explicit termination phrase (e.g., *"Thanks IGRIS"*, *"Sleep"*) is detected.

---

## 5. Cognitive Agent & Reasoning Architecture

IGRIS structures its generation cycle into distinct operational phases:

```
[Prompt + Context] ──► [Reasoning Phase: <think> ... </think>] ──► [Action / Speech Phase]
```

### 5.1 Chain-of-Thought (CoT) Scratchpad
Intermediate planning is wrapped within explicit semantic tags:
```xml
<think>
1. User wants to check CPU utilization and create a status report in Tamil.
2. Step 1: Run read-only telemetry action (Tier 0).
3. Step 2: Format findings in Tanglish/Tamil based on user preference.
</think>
<action>
{"tool": "system_telemetry", "parameters": {"metric": "cpu"}}
</action>
```

### 5.2 Action Invocation Schema
Action proposals emitted by the SLM are serialized into deterministic JSON schemas validated against an internal type registry before reaching the security gate.

---

## 6. Personal Memory Architecture

The memory layer resides in `src/igris/memory/` and operates locally on the filesystem:

```
+-------------------------------------------------------------------------------+
|                             MEMORY SUBSYSTEM                                  |
+-------------------------------------------------------------------------------+
|  1. Working Memory (Short-Term):                                              |
|     - Active conversation context buffer (last N turns in KV-cache)           |
|                                                                               |
|  2. Episodic Memory (Medium-Term):                                            |
|     - SQLite database recording past dialogues, session goals, and summaries   |
|                                                                               |
|  3. Semantic Memory (Long-Term):                                              |
|     - Local vector index storing user facts, recurring workflows,             |
|       custom coding preferences, and knowledge graphs                         |
+-------------------------------------------------------------------------------+
```

---

## 7. Permission-Gated Desktop Automation

To ensure complete safety, desktop automation commands pass through a deterministic security broker:

```
[Model Emits Action] 
         │
         ▼
[Permission Broker: Inspect Action & Target]
         │
         ├──► Tier 0: Read-only (e.g. read directory, get time) ──► Auto-Execute
         │
         ├──► Tier 1: Workspace File Creation ──► Brief Terminal Notification
         │
         ├──► Tier 2: Process Launch / Mouse / Keystroke ──► Voice/GUI Authorization
         │                                                    │
         │                                                    ├── Approved ──► Execute
         │                                                    └── Rejected ──► Abort & Learn
         │
         └──► Tier 3: Privileged / Destructive ──► Explicit Two-Step Confirmation
```

Every executed action generates an audit trail log in `logs/audit.jsonl` with timestamps, exact parameters, user approval status, and execution return codes.

---

## 8. Hardware Allocation & CUDA Optimization (RTX 3050 6GB)

### 8.1 Memory Layout
- **Total Dedicated VRAM**: 6,144 MB
- **Allocated Budget**:
  - `igris-50m` Weights (FP16): ~100 MB
  - KV-Cache (2,048 Tokens, GQA): ~150 MB
  - Activation Memory (Forward pass): ~400 MB
  - Modular ASR / TTS Audio Engine: ~1,500 MB
  - CUDA Runtime & PyTorch Overhead: ~600 MB
  - Safety Headroom & OS Display: ~3,394 MB available

### 8.2 C++/CUDA Acceleration Layer (`src/csrc/`)
Performance-critical operations are targeted for native compilation:
- Custom fused RMSNorm and SwiGLU kernels.
- Ring-buffer audio streaming DSP wrappers.
- High-efficiency KV-cache rotary embedding transformations.
