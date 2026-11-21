# IGRIS Local Inference API Specification

**Service**: IGRIS Multilingual Small Language Model Local Runtime  
**Protocol**: HTTP/1.1 & Server-Sent Events (SSE)  
**Default Base URL**: `http://127.0.0.1:8000`  
**API Version**: `3B.53`  
**Tokenizer**: Candidate A ByteLevel BPE (`SHA-256: ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`)  
**Languages**: English (`en`), Tamil (`ta`), Tanglish (`tanglish`)

---

## 1. Overview & Architectural Principles

The IGRIS local inference runtime exposes a high-performance REST and Server-Sent Events (SSE) interface built with FastAPI and Uvicorn. It is engineered to communicate seamlessly with the IGRIS Liquid Glass frontend while enforcing strict governance and truth-in-reporting policies:

1. **Truthful State Reporting**: If no pre-trained weights are loaded into the transformer architecture, the runtime explicitly reports `model_state = "MODEL_NOT_TRAINED"`. It never fabricates responses or hallucinated performance metrics.
2. **Deterministic Candidate A Tokenization**: All token metrics (`prompt_tokens`, `completion_tokens`, `total_tokens`) are computed by the verified Candidate A BPE tokenizer rather than crude word-count heuristics.
3. **Full-Duplex Cancellation**: Both HTTP SSE streaming and internal autoregressive tensor generation listen for client disconnects or abort signals to immediately cease compute and free resources.
4. **Hardware-Aware Safety**: Automatically discovers available NVIDIA CUDA VRAM and falls back gracefully to CPU compute if free VRAM is below safe operational thresholds (< 1.0 GB).

---

## 2. API Endpoints

### 2.1 Health Check

Retrieves the current operational status of the inference engine, verified tokenizer parameters, active hardware device, and model lifecycle state.

- **Routes**: `GET /health`, `GET /v1/health`
- **Headers**: `Accept: application/json`

#### Response (`200 OK`)

```json
{
  "status": "healthy",
  "model_loaded": false,
  "model_state": "MODEL_NOT_TRAINED",
  "model_name": "igris-prod-16l",
  "active_device": "cuda:0",
  "tokenizer": {
    "name": "Candidate A (ByteLevel BPE)",
    "vocab_size": 32768,
    "sha256": "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561",
    "verified": true,
    "structural_tokens_count": 12
  },
  "hardware": {
    "device": "cuda:0",
    "device_name": "NVIDIA GeForce RTX 3050 6GB Laptop GPU",
    "cuda_available": true,
    "total_vram_gb": 6.0,
    "free_vram_gb": 5.42,
    "cpu_cores": 12,
    "total_ram_gb": 15.64,
    "safe_for_gpu": true
  },
  "checkpoint_path": null,
  "version": "3B.53"
}
```

---

### 2.2 Model Registry

Returns metadata, configuration, parameter counts, and status for supported IGRIS models and tokenizer artifacts.

- **Route**: `GET /v1/models`
- **Headers**: `Accept: application/json`

#### Response (`200 OK`)

```json
{
  "object": "list",
  "data": [
    {
      "id": "igris-prod-16l",
      "object": "model",
      "created": 1732100000,
      "owned_by": "igris",
      "family": "IGRIS Core",
      "parameters": "79.7M (tied) / 96.5M (untied)",
      "context_window": 2048,
      "quantization": "FP16 / INT8",
      "status": "MODEL_NOT_TRAINED",
      "architecture": {
        "layers": 16,
        "hidden_size": 512,
        "intermediate_size": 2048,
        "attention_heads": 8,
        "kv_heads": 4,
        "rope_theta": 10000.0,
        "swiglu": true,
        "rms_norm_eps": 1e-05
      }
    },
    {
      "id": "igris-50m-baseline",
      "object": "model",
      "created": 1732100000,
      "owned_by": "igris",
      "family": "IGRIS Baseline",
      "parameters": "51.6M (tied) / 68.4M (untied)",
      "context_window": 2048,
      "quantization": "FP16 / INT8",
      "status": "Architecture Baseline",
      "architecture": {
        "layers": 12,
        "hidden_size": 512,
        "intermediate_size": 1376,
        "attention_heads": 8,
        "kv_heads": 4,
        "rope_theta": 10000.0,
        "swiglu": true,
        "rms_norm_eps": 1e-05
      }
    },
    {
      "id": "igris-candidate-a",
      "object": "model",
      "created": 1732100000,
      "owned_by": "igris",
      "family": "IGRIS Tokenizer",
      "parameters": "32,768 Vocab",
      "context_window": 2048,
      "quantization": "ByteLevel BPE",
      "status": "VERIFIED INVARIANT",
      "architecture": {
        "structural_tokens": 12,
        "byte_fallback": true,
        "sha256": "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
      }
    }
  ]
}
```

---

### 2.3 Chat Completions

Generates autoregressive responses from structured multi-turn conversation histories with Candidate A special token delimiters.

- **Route**: `POST /v1/chat/completions`
- **Headers**: `Content-Type: application/json`

#### Request Payload Schema

```json
{
  "model": "igris-prod-16l",
  "messages": [
    { "role": "system", "content": "You are IGRIS, an autonomous Voice-First Small Language Model." },
    { "role": "user", "content": "Explain SwiGLU activation in IGRIS." }
  ],
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 1024,
  "stream": false
}
```

#### Non-Streaming Response (`200 OK`)

```json
{
  "id": "chatcmpl-1732115000123",
  "object": "chat.completion",
  "created": 1732115000,
  "model": "igris-prod-16l",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "IGRIS utilizes SwiGLU activation defined as SwiGLU(x) = (xW_gate * SiLU(xW_up)) * W_down."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 34,
    "total_tokens": 62,
    "latency_ms": 142
  },
  "model_state": "MODEL_LOADED",
  "is_demo": false
}
```

#### Streaming Response (`text/event-stream`)

When `"stream": true`, the server streams Server-Sent Event chunks with `model_state = "MODEL_GENERATING"` followed by the final usage chunk and `data: [DONE]`:

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"id":"chatcmpl-1732115000","object":"chat.completion.chunk","created":1732115000,"model":"igris-prod-16l","choices":[{"index":0,"delta":{"role":"assistant","content":"IG"},"finish_reason":null}],"usage":null,"model_state":"MODEL_GENERATING"}

data: {"id":"chatcmpl-1732115000","object":"chat.completion.chunk","created":1732115000,"model":"igris-prod-16l","choices":[{"index":0,"delta":{"content":"RIS"},"finish_reason":null}],"usage":null,"model_state":"MODEL_GENERATING"}

...

data: {"id":"chatcmpl-1732115000","object":"chat.completion.chunk","created":1732115000,"model":"igris-prod-16l","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":14,"completion_tokens":42,"total_tokens":56,"latency_ms":195},"model_state":"MODEL_LOADED"}

data: [DONE]
```

#### Untrained Checkpoint Response (`503 Service Unavailable`)

When weights are unpopulated (in accordance with pretraining governance policies):

```json
{
  "error": {
    "message": "IGRIS model architecture and Candidate A tokenizer are verified, but no trained checkpoint has been loaded. Pretraining has not yet run in accordance with governance policies.",
    "type": "model_not_trained",
    "code": "MODEL_NOT_TRAINED",
    "model_state": "MODEL_NOT_TRAINED",
    "tokenizer_verified": true
  }
}
```

---

### 2.4 Raw Text Generation

Raw text autoregressive completion without chat structural prompt framing.

- **Route**: `POST /v1/generate`
- **Headers**: `Content-Type: application/json`

#### Request Payload Schema

```json
{
  "prompt": "Candidate A tokenizer vocabulary is",
  "max_tokens": 128,
  "temperature": 0.0,
  "top_p": 1.0,
  "stop": ["\n"]
}
```

#### Response (`200 OK`)

```json
{
  "id": "gen-1732115000456",
  "text": " exactly 32,768 tokens.",
  "prompt_tokens": 8,
  "completion_tokens": 7,
  "total_tokens": 15,
  "latency_ms": 48,
  "finish_reason": "stop",
  "model_state": "MODEL_LOADED",
  "is_demo": false
}
```

---

## 3. UI Lifecycle State Machine

The local runtime coordinates with the Liquid Glass frontend across 4 distinct states:

| Lifecycle State | HTTP Status / Code | UI Badge Color | Description |
| :--- | :--- | :--- | :--- |
| **`DEMO MODE`** | Internal Simulation | Amber / Gold | Frontend simulation adapter producing deterministic educational mock responses. |
| **`MODEL NOT TRAINED`** | `503 Service Unavailable` (`MODEL_NOT_TRAINED`) | Amber / Orange | Runtime connected, Candidate A tokenizer & architecture verified, but weights not yet trained. |
| **`MODEL LOADED`** | `200 OK` (`model_loaded: true`) | Emerald Green | Model checkpoint loaded into memory, ready to accept inference requests. |
| **`MODEL GENERATING`** | SSE Chunk stream | Electric Blue (pulsing) | Model is actively running autoregressive decoding steps. |

---

## 4. Error Handling Matrix

| HTTP Status | Error Code | Trigger Condition | Recovery Action |
| :--- | :--- | :--- | :--- |
| **`400 Bad Request`** | `VALIDATION_ERROR` | Empty prompt or empty `messages` array | Provide valid non-empty input. |
| **`503 Service Unavailable`** | `MODEL_NOT_TRAINED` | Request sent when no pre-trained weights are present | Switch to Demo Simulation or train checkpoint. |
| **`503 Service Unavailable`** | `OUT_OF_MEMORY` | GPU VRAM exhausted during forward pass | Engine purges CUDA cache; fall back to CPU execution. |
| **`500 Internal Error`** | `TOKENIZER_INTEGRITY_ERROR` | Candidate A SHA-256 hash does not match invariant | Restore authoritative Candidate A `tokenizer.json`. |
