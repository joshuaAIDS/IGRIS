# IGRIS — Phased Engineering Roadmap

---

## 1. Development Lifecycle & Governance

The IGRIS engineering plan is divided into six sequential, test-driven phases. Each phase requires successful validation against explicit completion criteria before transitioning to subsequent phases.

```
+-----------------------------------------------------------------------------------------+
|                                    IGRIS ROADMAP                                        |
+-----------------------------------------------------------------------------------------+
|  Phase 1: Environment Baseline, Corpus Curation & Trilingual Tokenizer                  |
|     └── Python 3.11, CUDA PyTorch on RTX 3050, English/Tamil/Tanglish Byte-Fallback BPE |
+-----------------------------------------------------------------------------------------+
                                           │
                                           ▼
+-----------------------------------------------------------------------------------------+
|  Phase 2: Custom Transformer SLM Architecture (~50M Baseline) & Pretraining             |
|     └── From-scratch PyTorch implementation, RoPE, RMSNorm, SwiGLU, GQA, Pretraining    |
+-----------------------------------------------------------------------------------------+
                                           │
                                           ▼
+-----------------------------------------------------------------------------------------+
|  Phase 3: Alignment, Chain-of-Thought Reasoning & Coding Specialization                 |
|     └── Supervised Fine-Tuning (SFT), <think> scratchpads, Python/C++ code synthesis    |
+-----------------------------------------------------------------------------------------+
                                           │
                                           ▼
+-----------------------------------------------------------------------------------------+
|  Phase 4: Modular Audio Subsystem & Wake-Word Pipeline ("Hey IGRIS")                    |
|     └── Low-latency Wake Word, VAD turn-taking, Modular ASR & Male Voice TTS            |
+-----------------------------------------------------------------------------------------+
                                           │
                                           ▼
+-----------------------------------------------------------------------------------------+
|  Phase 5: Local Personal Memory & Permission-Gated Desktop Control                      |
|     └── SQLite/Vector episodic store, OS automation sandbox, Human-in-the-loop security  |
+-----------------------------------------------------------------------------------------+
                                           │
                                           ▼
+-----------------------------------------------------------------------------------------+
|  Phase 6: Full Integration, C++/CUDA Acceleration & Edge Quantization                   |
|     └── Real-time conversational duplex voice loop, FP16/INT8 benchmarks on RTX 3050    |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Phase-by-Phase Milestones

### Phase 1: Environment Baseline, Corpus Curation & Trilingual Tokenizer
- [ ] **Milestone 1.1: Environment Verification**
  - Verify Python 3.11 virtual environment.
  - Install CUDA-compatible PyTorch for NVIDIA RTX 3050 (6GB) and verify `torch.cuda.is_available()`.
  - Install curated base dependencies from `requirements.txt`.
- [ ] **Milestone 1.2: Corpus Preparation & Manifest Schema**
  - Build ingestion pipelines for English technical/conversational text, native Tamil Unicode text, and phonetic Tanglish corpora.
  - Establish dataset manifests (`manifests/*.manifest.json`) tracked in Git for total data reproducibility.
- [ ] **Milestone 1.3: Trilingual BPE Tokenizer Construction**
  - Train custom 32,768 vocabulary Byte-Pair Encoding tokenizer with byte fallback enabled (no `<unk>`).
  - Reserve special control tokens (`<pad>`, `<bos>`, `<eos>`, `<think>`, `</think>`, `<action>`, `</action>`).
  - Preserve all tokenizer artifacts (`tokenizer.json`, `vocab.json`, `merges.txt`) in Git.
- [ ] **Milestone 1.4: Token Fragmentation Benchmarking**
  - Compute Tokens-per-Word (TPW) and Byte-to-Token Ratio (BTR) across English, Tamil Unicode, and Tanglish test splits.
  - Optimize pre-tokenization regex until Tamil Unicode TPW is under $1.65$.

---

### Phase 2: Custom Transformer SLM Architecture (~50M Baseline) & Pretraining
- [ ] **Milestone 2.1: Model Architecture Implementation**
  - Implement custom RoPE (Rotary Position Embeddings) module in `src/igris/model/embeddings.py`.
  - Implement custom RMSNorm in `src/igris/model/norm.py`.
  - Implement SwiGLU Feed-Forward Networks in `src/igris/model/feedforward.py`.
  - Implement Grouped Query Attention (GQA) with KV-cache support in `src/igris/model/attention.py`.
  - Assemble full decoder-only Transformer in `src/igris/model/transformer.py`.
- [ ] **Milestone 2.2: Unit Testing & Gradient Verification**
  - Validate shapes, parameter counts (~50M target), causal masking, and gradient propagation via `tests/test_model.py`.
- [ ] **Milestone 2.3: Configurable Parameter Management**
  - Store model configurations in `configs/model_50m.yaml`.
- [ ] **Milestone 2.4: Pretraining Loop & Validation**
  - Implement training harness with mixed-precision (FP16/BF16), AdamW optimizer, cosine learning rate scheduler, and gradient accumulation.
  - Validate training on RTX 3050 GPU, monitoring VRAM headroom and tokens/sec throughput.

---

### Phase 3: Alignment, Chain-of-Thought Reasoning & Coding Specialization
- [ ] **Milestone 3.1: Supervised Fine-Tuning (SFT) Dataset Construction**
  - Curate high-quality instruction datasets covering multi-turn English, Tamil, and Tanglish dialogue.
  - Construct Chain-of-Thought reasoning demonstrations utilizing `<think> ... </think>` scratchpad blocks.
  - Curate coding datasets focused on Python, C++, shell scripts, and system telemetry tasks.
- [ ] **Milestone 3.2: Instruction Tuning**
  - Execute SFT on the base 50M SLM.
  - Validate reasoning coherence and formatting compliance.
- [ ] **Milestone 3.3: Tool-Calling Alignment**
  - Train the model to generate structured JSON action schemas (`<action> ... </action>`) and handle tool execution feedback.

---

### Phase 4: Modular Audio Subsystem & Wake-Word Pipeline ("Hey IGRIS")
- [ ] **Milestone 4.1: Audio I/O Infrastructure**
  - Implement low-latency microphone capture and playback streaming in `src/igris/audio/stream.py`.
- [ ] **Milestone 4.2: Local Wake-Word Spotter**
  - Train/integrate an acoustic keyword spotting model specifically for the phrase **"Hey IGRIS"**.
  - Achieve continuous background listening with < 2% CPU and negligible GPU footprint.
- [ ] **Milestone 4.3: Real-Time Voice Activity Detection (VAD)**
  - Integrate fast VAD to detect speech start/end boundaries and enable natural turn-taking without re-triggering the wake word.
- [ ] **Milestone 4.4: Modular ASR & Male Voice TTS Integration**
  - Implement modular ASR adapter to transcribe audio into text streams.
  - Implement modular neural TTS adapter calibrated for a clear, conversational male vocal persona.
  - Strictly document and isolate third-party speech dependencies to maintain transparent attribution.

---

### Phase 5: Local Personal Memory & Permission-Gated Desktop Control
- [ ] **Milestone 5.1: Episodic & Semantic Memory Engine**
  - Implement local SQLite database for session tracking and past dialogue context in `src/igris/memory/episodic.py`.
  - Implement lightweight local vector search for user preferences and facts in `src/igris/memory/semantic.py`.
- [ ] **Milestone 5.2: Desktop Automation Sandbox**
  - Implement OS automation actions (file manipulation, process launching, window inspection) in `src/igris/automation/desktop.py`.
- [ ] **Milestone 5.3: Permission Enforcement Broker**
  - Implement the security gateway (`src/igris/automation/security.py`) enforcing Tier 0 through Tier 3 permission levels.
  - Build interactive voice/terminal authorization prompts for all non-read-only actions.
  - Ensure zero unconfirmed system executions.

---

### Phase 6: Full Integration, C++/CUDA Acceleration & Edge Quantization
- [ ] **Milestone 6.1: End-to-End Voice Agent Integration**
  - Connect Wake-Word -> VAD -> Modular ASR -> IGRIS SLM -> Modular Male TTS in a continuous duplex loop.
- [ ] **Milestone 6.2: C++/CUDA Extension Optimizations**
  - Implement high-performance C++/CUDA kernels in `src/csrc/` for attention bottlenecks and audio ring buffers.
- [ ] **Milestone 6.3: Quantization & Performance Profiling on RTX 3050**
  - Benchmark unquantized FP16 vs INT8/INT4 weights.
  - Measure end-to-end voice latency (from speech cessation to audio playback start), targeting < 500ms response time.
- [ ] **Milestone 6.4: System Hardening & Release**
  - Execute end-to-end integration tests in `tests/test_integration.py`.
  - Finalize documentation and release `igris-v0.1.0`.
