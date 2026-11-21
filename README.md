# IGRIS (இக்ரிஸ்)

> **Voice-First Autonomous Small Language Model (SLM)**  
> *Engineered from first principles in PyTorch, C++, and CUDA.*

---

## 1. Overview

**IGRIS** is an original, voice-native Small Language Model (SLM) designed for low-latency local execution. Built from scratch with complete ownership over its architecture, tokenizer, and training pipeline, IGRIS combines compact conversational intelligence with multi-turn voice interaction, autonomous task planning, personal memory, and permission-gated desktop automation.

The architecture is calibrated for consumer-grade GPU hardware—specifically targeting an **NVIDIA GeForce RTX 3050 (6GB VRAM)** on **Python 3.11**.

---

## 2. Core Project Objectives

1. **Custom Transformer Architecture**: A decoder-only Transformer built from scratch (Pre-LayerNorm RMSNorm, SwiGLU activation, Rotary Position Embeddings).
2. **Configurable ~50M Parameter Baseline**: Compact footprint optimized for fast local autoregressive decoding within a 2,048-token context window.
3. **Trilingual Language Engine**: Deep native support for **English**, **Tamil (Unicode)**, and **Tanglish (Romanized Tamil)** using a custom Byte-Pair Encoding (BPE) tokenizer with byte fallback.
4. **Autonomous Reasoning & Planning**: Chain-of-Thought (CoT) reasoning and structured tool-calling capabilities.
5. **Specialized Coding Intelligence**: Native code comprehension, terminal script synthesis, and iterative debugging logic.
6. **Local Episodic & Semantic Memory**: Privacy-preserving, offline vector and key-value memory retention across sessions.
7. **Modular Speech Stack (Male Voice)**: A low-latency conversational audio pipeline supporting male-voice speech generation and speech recognition.
8. **Local "Hey IGRIS" Wake-Word Engine**: Continuous, low-overhead keyword spotting running locally.
9. **Continuous Conversational Loop**: Full duplex voice activity detection (VAD) and turn-taking without repeated trigger phrases.
10. **Permission-Gated Desktop Control**: OS interaction and desktop automation governed by an uncompromising human-in-the-loop authorization policy.

---

## 3. Architecture & Ownership Boundary

IGRIS maintains a strict separation of concerns between its proprietary core and auxiliary modular subsystems:

```
+-------------------------------------------------------------------------------+
|                             IGRIS ECOSYSTEM                                   |
+-------------------------------------------------------------------------------+
|  PROPRIETARY CORE (Built from scratch)                                        |
|  - Custom Transformer SLM (~50M parameters, configurable)                     |
|  - Trilingual BPE Tokenizer (English, Tamil Unicode, Tanglish)                |
|  - Pretraining, SFT, and Reasoning Alignment Pipelines                        |
|  - Personal Episodic Memory & Semantic Retrieval Store                        |
|  - Permission-Gated OS Automation Engine & State Machine                      |
+-------------------------------------------------------------------------------+
|  MODULAR SPEECH INTERFACE (Pluggable Audio Wrappers)                          |
|  - Keyword Spotting: "Hey IGRIS" Wake-Word Engine                             |
|  - ASR (Speech-to-Text): Modular local acoustic transcription                 |
|  - TTS (Text-to-Speech): Modular neural male-voice synthesizer                |
|  - VAD: Real-time Voice Activity Detection and turn management                |
|  * Note: External pretrained speech utilities are used strictly as modular    |
|    adapters and are never misrepresented as original IGRIS core models.       |
+-------------------------------------------------------------------------------+
```

---

## 4. Hardware & Environment Specifications

- **Operating System**: Windows 11 / Linux
- **Python Environment**: Python 3.11
- **Target GPU**: NVIDIA GeForce RTX 3050 (6GB GDDR6 VRAM)
- **Acceleration**: CUDA 12.x / C++ extensions (`src/csrc/`)
- **Memory Footprint Budget**:
  - Model Weights (FP16): ~100 MB
  - KV Cache (2,048 context): ~150 MB
  - Working Audio Buffers & Scratchpad: < 1.0 GB
  - Total Target Runtime VRAM: < 3.5 GB (leaves headroom on 6GB GPU)

---

## 5. Repository Structure

```text
IGRIS/
├── .gitignore                   # Reproducibility-preserving ignore rules
├── README.md                    # Project landing page and high-level manual
├── requirements.txt             # Core dependencies (PyTorch installed separately)
├── documentation/               # Comprehensive system documentation
│   ├── PROJECT_OVERVIEW.md      # Mission, linguistic design, and security model
│   ├── ARCHITECTURE.md          # Technical specs, layer dimensions, audio pipeline
│   └── DEVELOPMENT_ROADMAP.md   # Phased engineering milestones & deliverables
├── configs/                     # Model hyperparameter & training configurations
├── notebooks/                   # Tokenizer training, data analysis, and ablations
├── src/
│   ├── igris/                   # Primary Python package
│   │   ├── __init__.py
│   │   ├── model/               # Custom Transformer SLM implementation
│   │   ├── tokenizer/           # Trilingual BPE tokenizer with byte fallback
│   │   ├── audio/               # Wake-word, ASR, TTS, and VAD interfaces
│   │   ├── reasoning/           # CoT, agentic planning, and tool schemas
│   │   ├── memory/              # Local episodic and semantic memory
│   │   └── automation/          # Permission-gated desktop automation hooks
│   └── csrc/                    # C++/CUDA performance kernels
└── tests/                       # Unit and integration test suites
```

---

## 6. Setup & Installation (Preparation)

### Step 1: Environment Preparation (Python 3.11)
Ensure Python 3.11 is active in your virtual environment:
```bash
python --version
# Output should indicate Python 3.11.x
```

### Step 2: Install CUDA-Enabled PyTorch
*PyTorch is intentionally excluded from `requirements.txt` to guarantee clean CUDA matching for the NVIDIA RTX 3050 GPU.*

For CUDA 12.1:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Verify GPU visibility:
```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available(), '| Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

### Step 3: Install Base Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Launch IGRIS Frontend Studio (Liquid Glass UI)
```bash
# Install frontend dependencies (from root or within frontend/)
npm install --prefix frontend

# Run development server with Liquid Glass UI
npm run dev

# Or build for production
npm run build
```

---

## 7. Documentation Navigation

- **Detailed Project Blueprint**: [documentation/PROJECT_OVERVIEW.md](file:///c:/IGRIS/documentation/PROJECT_OVERVIEW.md)
- **Comprehensive Architectural Specifications**: [documentation/ARCHITECTURE.md](file:///c:/IGRIS/documentation/ARCHITECTURE.md)
- **Step-by-Step Engineering Roadmap**: [documentation/DEVELOPMENT_ROADMAP.md](file:///c:/IGRIS/documentation/DEVELOPMENT_ROADMAP.md)
- **Chat Interface & Design Guide**: [documentation/CHAT_INTERFACE.md](file:///c:/IGRIS/documentation/CHAT_INTERFACE.md)
- **Backend Inference Adapter Guide**: [documentation/BACKEND_CONNECTION.md](file:///c:/IGRIS/documentation/BACKEND_CONNECTION.md)
- **Integration Test Report**: [documentation/TEST_REPORT.md](file:///c:/IGRIS/documentation/TEST_REPORT.md)
- **Build Verification Report**: [documentation/BUILD_VERIFICATION_REPORT.md](file:///c:/IGRIS/documentation/BUILD_VERIFICATION_REPORT.md)

---

## 8. License & Ownership

All custom model architectures, tokenizers, training configurations, and original code within `src/igris/` are original works developed specifically for the IGRIS project.
