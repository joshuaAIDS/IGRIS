# IGRIS Runtime Startup & Live Smoke Test Report

**Engineering Role**: Senior ML Systems Engineer  
**Launch Command**: `.venv\Scripts\python.exe -m igris.inference.server`  
**Server Host & Port**: `http://127.0.0.1:8000`  
**Package Resolution**: `pyproject.toml` (`editable` mode)  
**Operating Model**: SOLO_DEVELOPER_OWNER_REVIEW  
**Date**: November 2026  
**Status**: **VERIFIED — LIVE SMOKE TEST 100% PASS**

---

## 1. Package Resolution & Dependency Integrity

### 1.1 Resolution Audit
To ensure that `.venv\Scripts\python.exe -m igris.inference.server` executes from any working directory without requiring an accidental working directory or undocumented `PYTHONPATH` environment variables:
- Configured [`pyproject.toml`](file:///c:/IGRIS/pyproject.toml) declaring `where = ["src"]`.
- Installed the package into `.venv` in editable mode via:
  ```powershell
  .venv\Scripts\pip.exe install -e . --no-deps
  ```
- Tested invocation from an external directory (`C:\Users\joshu`):
  ```
  Resolved igris from outside C:\IGRIS: C:\IGRIS\src\igris\__init__.py
  ```

### 1.2 Dependency Declaration in `requirements.txt`
All core runtime dependencies are formally pinned in [`requirements.txt`](file:///c:/IGRIS/requirements.txt):
- `fastapi>=0.110.0` (FastAPI Web Framework)
- `uvicorn>=0.28.0` (ASGI Production Server)
- `tokenizers>=0.19.0` (Hugging Face Byte-Level BPE)
- `regex>=2024.5.15` (Dravidian & Unicode Regular Expressions)
- `psutil>=5.9.0` (Host Hardware & Memory Profiling)
- `pytest>=8.0.0` (Verification Harness)

---

## 2. Live HTTP Smoke Test Results

An actual live HTTP smoke test was executed against the running local daemon on `http://127.0.0.1:8000`.

### 2.1 Service Welcome & Overview (`GET /`)
- **HTTP Status**: `200 OK`
- **Payload**:
  ```json
  {
    "service": "IGRIS Local Inference Runtime",
    "version": "3B.53",
    "status": "online",
    "endpoints": {
      "health": "/health",
      "models": "/v1/models",
      "chat_completions": "/v1/chat/completions",
      "generate": "/v1/generate",
      "docs": "/docs"
    }
  }
  ```

### 2.2 Health Status Verification (`GET /health` & `GET /v1/health`)
- **HTTP Status**: `200 OK`
- **Payload**:
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
      "free_vram_gb": 5.04,
      "cpu_threads": 12,
      "system_platform": "Windows-10-10.0.26300-SP0",
      "safe_for_gpu": true
    },
    "checkpoint_path": null,
    "version": "3B.53"
  }
  ```
- **Audit Findings**:
  - `model_loaded` is strictly `false`.
  - `model_state` accurately reports `MODEL_NOT_TRAINED`.
  - Candidate A SHA-256 is verified invariant.

### 2.3 Model Registry (`GET /v1/models`)
- **HTTP Status**: `200 OK`
- **Payload**:
  - `igris-prod-16l`: Status is `MODEL_NOT_TRAINED` (16 layers, 79.7M/96.5M).
  - `igris-50m-baseline`: Status is `Architecture Baseline` (12 layers, 51.6M/68.4M).
  - `igris-candidate-a`: Status is `VERIFIED INVARIANT` (32,768 vocab, 12 structural tokens).

### 2.4 Chat Completion Guard (`POST /v1/chat/completions`)
When an inference request is dispatched while weights are unpopulated:
- **HTTP Status**: `503 Service Unavailable`
- **Error Payload**:
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
- **Audit Findings**: The runtime strictly refuses to fabricate random tokens.

---

## 3. Server Startup & Shutdown Verification

1. **Startup**: Daemon binds to `127.0.0.1:8000` via Uvicorn with standard ASGI lifespan protocol.
2. **Signal Handling**: Responds cleanly to `SIGINT` (Ctrl+C) and terminates child threads without leaving orphaned TCP socket listeners.
3. **CORS Headers**: Configured with `allow_origins=["*"]`, enabling local browser connections from `http://localhost:3000`.
