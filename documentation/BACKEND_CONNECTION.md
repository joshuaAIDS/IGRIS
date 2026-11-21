# IGRIS Backend Inference Adapter & Runtime Connection Guide

## 1. Overview

The IGRIS frontend architecture enforces a strict separation between UI rendering and inference model implementation. All model interactions are routed through the `IInferenceAdapter` abstraction layer.

This design guarantees that:
1. The frontend remains independent of the specific model runtime (PyTorch, C++, ONNX, or CUDA extensions).
2. The UI never misrepresents an unverified model as connected when it is not.
3. Hardware telemetry (GPU utilization, VRAM usage, throughput) reflects actual runtime measurements without fabricated metrics.
4. Candidate A tokenizer specifications are natively prepared for integration.

---

## 2. Architecture & Adapters

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        IGRIS FRONTEND (REACT / VITE)                   │
├────────────────────────────────────────────────────────────────────────┤
│  ConversationContext / PlaygroundPanel / ChatComposer                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   BackendConnectionManager (Singleton)                 │
│  - Mode: 'demo' | 'http'                                               │
│  - Health status listener & active adapter resolver                    │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
                   ▼                                 ▼
┌──────────────────────────────────────┐ ┌───────────────────────────────┐
│        DemoSimulationAdapter         │ │    IgrisHttpBackendAdapter    │
│  - Clearly identified demo responses │ │  - SSE stream parser          │
│  - Trilingual Tamil/English/Tanglish │ │  - Standard REST /v1/chat/... │
│  - Simulated progressive streaming   │ │  - AbortController signal     │
│  - Candidate A token estimation      │ │  - Graceful connection errors │
└──────────────────────────────────────┘ └───────────────┬───────────────┘
                                                         │
                                                         ▼
                                         ┌───────────────────────────────┐
                                         │   LOCAL IGRIS RUNTIME DAEMON  │
                                         │   - Default: http://localhost:│
                                         │     8000/v1/chat/completions  │
                                         │   - PyTorch / C++ Core (~50M) │
                                         │   - Zero-Egress Local GPU     │
                                         └───────────────────────────────┘
```

---

## 3. Adapters

### 3.1 `DemoSimulationAdapter` (Default until local daemon is connected)
- **Status Indicator**: `isDemo: true`, badge: `BACKEND: STANDBY (DEMO MODE)`.
- **Response Prefix**: Every output is labeled with an explicit notice:
  ```markdown
  > **[IGRIS DEMO MODE]** *This is a demonstration response. The actual IGRIS model runtime backend is not yet connected.*
  ```
- **Trilingual Comprehension**:
  - Automatically identifies whether the user input is Tamil Unicode (`[\u0B80-\u0BFF]`), Tanglish (phonetic markers like *enna*, *panreenga*, *epdi*), or English.
  - Returns appropriate, grammatically coherent responses in the detected language.
- **Paced Streaming**: Emits progressive token chunks with non-blocking delays while honoring `AbortSignal` for cancellation.
- **Telemetry**: Calculates token consumption using Candidate A subword ratios instead of displaying fabricated hardware utilization.

### 3.2 `IgrisHttpBackendAdapter` (Live Local Model Runtime)
- Connects directly to the local IGRIS inference server daemon.
- **Endpoint**: Configurable via Settings (defaults to `http://127.0.0.1:8000/v1/chat/completions`).
- **Streaming**: Implements Server-Sent Events (SSE) reading chunked HTTP responses (`data: {...}`).
- **Cancellation**: Passes the UI `AbortController.signal` directly into the fetch stream to cancel generation instantly on the server.
- **Health Check**: Probes `${baseUrl}/health` to retrieve online status, model checkpoint identity, and ping latency.
- **Error Handling**: Catches network failures, offline ports, connection timeouts, and HTTP status errors (500/503), exposing clean error alerts in the chat interface.

---

## 4. Tokenizer Integration: IGRIS Candidate A

The frontend prepares for integration with the selected IGRIS **Candidate A Tokenizer** (`igris_candidate_a_v228.py`):

| Property | Value | Notes |
| :--- | :--- | :--- |
| **Model Type** | ByteLevel BPE | Byte fallback with 256 initial bytes |
| **Vocabulary Size** | 32,768 | Unified across English, Tamil Unicode, Tanglish |
| **Special Control Tokens** | 12 tokens | Ordered: `<\|pad\|>`, `<\|begin_of_text\|>`, `<\|end_of_text\|>`, `<think>`, `</think>`, `<action>`, `</action>`, `<action_result>`, `</action_result>`, `<\|system\|>`, `<\|user\|>`, `<\|assistant\|>` |
| **English TPW Target** | 1.15 – 1.30 TPW | High subword efficiency |
| **Tamil TPW Target** | 1.30 – 1.65 TPW | Resolves Unicode character fragmentation |
| **Tanglish TPW Target** | 1.20 – 1.45 TPW | Normalizes colloquial Latin digraphs |

### Structural Prompt Delimitation Helper
The adapter formats conversational history turns according to Candidate A's required structural tokens:
```python
<|begin_of_text|>
<|system|>
You are IGRIS, an autonomous Voice-First Small Language Model.
<|user|>
Hello IGRIS
<|assistant|>
Greetings!
<|user|>
Explain SwiGLU activation.
<|assistant|>
```

---

## 5. Governance & Privacy Guarantees

In accordance with project governance:
1. **Zero External AI Egress**: The frontend does not connect to external AI APIs (e.g. OpenAI, Anthropic, Gemini) by default.
2. **Zero Secret Exposure**: No API keys, credentials, or private tokens are hardcoded or bundled in the frontend assets.
3. **Local Loopback**: All network requests target local loopback (`http://127.0.0.1:*` or `http://localhost:*`).
