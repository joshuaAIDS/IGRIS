# IGRIS — Project Overview & Vision

---

## 1. Executive Summary

**IGRIS** is an original, voice-native Small Language Model (SLM) designed to demonstrate that high-utility conversational intelligence, reasoning, coding assistance, and system automation do not require hundred-billion-parameter cloud APIs. By engineering an autoregressive Transformer model from first principles, IGRIS is tailored for ultra-low latency, complete data privacy, and edge execution on consumer hardware (specifically an NVIDIA GeForce RTX 3050 6GB GPU).

Beyond pure text generation, IGRIS is built as an end-to-end cognitive voice agent:
- Activating on the local wake phrase **"Hey IGRIS"**.
- Conducting natural, continuous multi-turn voice conversations in a distinctive **male vocal persona**.
- Speaking and understanding **English**, native **Tamil (தமிழ்)**, and informal **Tanglish** (Tamil written in Latin characters).
- Formulating multi-step plans with explicit **Chain-of-Thought (CoT)** reasoning tokens.
- Executing desktop tasks and shell commands under an unyielding, **permission-gated security model**.

---

## 2. Motivation & Engineering Philosophy

### 2.1 The Small Language Model (SLM) Advantage
Cloud-based frontier models introduce latency, network dependency, subscription overhead, and data confidentiality concerns. For dedicated personal voice interaction and desktop task execution, a focused **~50 Million parameter** architecture offers unique advantages:
- **Instantaneous Time-to-First-Token (TTFT)**: Extremely rapid generation cycle, allowing natural spoken conversation without awkward delays.
- **Minimal VRAM Footprint**: Under 200 MB for model parameters, leaving ample VRAM on a 6GB card for the audio pipeline, KV-cache, and operating system overhead.
- **Local Determinism & Ownership**: Full control over tokenizer behavior, alignment data, safety boundaries, and inference kernels.

### 2.2 Ownership vs. Modular Speech Attribution
IGRIS draws a definitive boundary between its **original core** and **modular speech interfaces**:
1. **Original IGRIS Core**:
   - The Transformer architecture, mathematical implementation, and custom CUDA kernels.
   - The trilingual BPE tokenizer, vocabulary construction, and byte-fallback pipeline.
   - All training routines, learning rate schedulers, objective functions, and dataset curation logic.
   - The episodic memory architecture and agentic task execution engine.
2. **Modular Auxiliary Speech Components**:
   - Speech Recognition (ASR), Text-to-Speech (TTS), and Voice Activity Detection (VAD) are implemented as isolated, swappable modular adapters.
   - Pretrained speech engines utilized during initial stages are strictly treated as auxiliary peripherals and clearly documented as third-party modules—never misrepresented as original IGRIS neural architectures.

---

## 3. Linguistic Architecture: English, Tamil & Tanglish

A core deficiency of generic language models is severe token fragmentation when handling South Asian languages and informal romanized colloquialisms. IGRIS addresses this directly.

### 3.1 Linguistic Categories
1. **English**: Technical, conversational, and command-oriented vocabulary.
2. **Tamil Unicode (தமிழ்)**: Native Brahmi-derived script used across formal literature, news, and regional communication.
3. **Tanglish (Romanized Tamil)**: Phonetic Tamil transcribed into the Latin alphabet (e.g., *"Enna panreenga?"*, *"Kandippa mudiyum"*), prevalent in spoken conversation, instant messaging, and technical discussions.

### 3.2 Token Fragmentation & Byte Fallback Strategy
Standard BPE tokenizers split Tamil Unicode characters into multiple disjoint byte tokens, increasing sequence length, exploding inference latency, and degrading semantic coherence. IGRIS mitigates this by:
- Allocating dedicated vocabulary tokens for high-frequency Tamil character combinations and syllabic structures (Uyirmei letters).
- Ingesting a balanced parallel corpus of Latinized Tanglish n-grams to prevent character-by-character spelling fragmentation.
- Enforcing **Byte Fallback** (preserving raw UTF-8 byte tokens 0x00–0xFF) so that no rare character, emoji, or unseen symbol ever maps to an unknown `<unk>` token.
- Incorporating systematic **Token Fragmentation Evaluation** metrics:
  $$\text{Fragmentation Ratio} = \frac{\text{Number of Tokens}}{\text{Number of Words}}$$
  Tracking this ratio across English, Tamil Unicode, and Tanglish benchmarks ensures fair representation across all three linguistic modes.

---

## 4. Cognitive & Functional Capabilities

### 4.1 Autonomous Reasoning & Task Execution
IGRIS separates reflexive generation from conscious planning:
- **Reasoning Tokens**: The model utilizes internal scratchpad delimitation (`<think> ... </think>`) to formulate intermediate steps before delivering vocal answers or executing commands.
- **Structured Tool Calling**: Standardized JSON-based action schema allowing the model to invoke system functions, inspect directories, read files, or control desktop applications.

### 4.2 Specialized Coding Intelligence
Optimized for developer assistance and self-automation:
- Deep syntax grounding in Python, C++, Bash/PowerShell, and system APIs.
- Iterative debugging: The ability to ingest execution error logs, reason over root causes, and propose targeted patches.

### 4.3 Personal Memory Subsystem
To serve as a genuine personal companion, IGRIS implements persistent context:
- **Short-Term Session Memory**: Ring buffer holding current dialogue turns and active working state.
- **Episodic & Semantic Long-Term Memory**: Local SQLite and vector database storing user preferences, habitual tasks, project configurations, and past interactions.
- **Zero Cloud Leakage**: All memories are stored encrypted in the local file system.

---

## 5. Security & Permission-Gated Desktop Control

Giving a language model desktop automation capabilities demands uncompromising safety controls:

```
  [User Voice / Input] 
           │
           ▼
     [IGRIS SLM] ──(Generates Plan & Action Schema)──► [Security Gateway]
                                                              │
                                            ┌─────────────────┴─────────────────┐
                                            ▼                                   ▼
                                   [Read-Only Action]                 [Write / Execute Action]
                                            │                                   │
                                    (Auto-Permitted)                 [Prompt User For Permission]
                                            │                                   │
                                            │                       ┌───────────┴───────────┐
                                            │                       ▼                       ▼
                                            │                   [Approved]              [Denied]
                                            │                       │                       │
                                            └───────────────┬───────┘                       ▼
                                                            ▼                          [Halt & Log]
                                                [Execute in Sandbox / OS]
                                                            │
                                                            ▼
                                                [Feedback Loop to IGRIS]
```

### 5.1 Permission Tiers
- **Tier 0 (Inspection)**: Read files, inspect system status, check CPU/GPU temperatures, query time/weather. (Automated).
- **Tier 1 (Safe Modifications)**: Create/edit files in designated workspace directories. (Requires implicit/brief confirmation).
- **Tier 2 (System Execution)**: Running shell commands, launching processes, sending keystrokes, controlling mouse pointer. (Explicit voice or UI confirmation mandatory: *"IGRIS requires permission to run: `powershell build.ps1`. Proceed?"*).
- **Tier 3 (Destructive/Privileged)**: Deleting files, modifying system registry, network reconfiguration, executing with administrative rights. (Blocked by default; requires explicit two-factor confirmation).

---

## 6. Target Hardware Budget (NVIDIA RTX 3050 6GB)

| Component | Target Allocation | Format / Strategy |
| :--- | :--- | :--- |
| **Model Weights (~50M params)** | ~100 MB | FP16 / BF16 baseline |
| **KV-Cache (2,048 tokens)** | ~150 MB | Grouped Query Attention (GQA) |
| **CUDA Activation Workspace** | ~500 MB | PyTorch memory pool management |
| **Modular Speech Engine (ASR/TTS)** | ~1.5 GB | Quantized/streamed local audio models |
| **OS & Display Headroom** | ~1.5 GB | Reserved for Windows Desktop Manager & GPU display |
| **Total VRAM Utilization** | **< 3.8 GB** | Well within the 6.0 GB hardware ceiling |

---

## 7. Development Discipline & Reproducibility

- **Python 3.11** as the pinned development standard.
- **PyTorch with CUDA** configured independently of standard requirements to maintain precise hardware alignment.
- **Complete Reproducibility Artifacts**: Tokenizer merge tables, vocabulary mappings, dataset manifests, and training hyperparameters are tracked in Git.
- **Incremental Verification**: Every module undergoes rigorous unit testing and validation before integration.
