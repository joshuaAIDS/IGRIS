"""FastAPI HTTP and Server-Sent Events (SSE) server for IGRIS local inference."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, AsyncGenerator

import torch

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from igris.inference.engine import IgrisInferenceEngine, ModelNotTrainedError, TokenizerIntegrityError
from igris.inference.schemas import (
    ChatChoice,
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ChunkChoice,
    DeltaContent,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ModelCard,
    ModelListResponse,
    TokenizerStatus,
    TokenPiece,
    TokenizeRequest,
    TokenizeResponse,
    UsageInfo,
)

logger = logging.getLogger("igris.server")

app = FastAPI(
    title="IGRIS Inference Runtime",
    version="3B.53",
    description="Official local inference runtime and trilingual API service for IGRIS.",
)

# Enable CORS for local React/Vite development & production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(torch.cuda.OutOfMemoryError)
async def cuda_oom_handler(request: Request, exc: torch.cuda.OutOfMemoryError):
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "message": "CUDA out-of-memory detected during tensor allocation. Local inference engine managed safe fallback.",
                "type": "out_of_memory_error",
                "code": "OUT_OF_MEMORY",
            }
        },
    )

# Global engine instance
_engine: IgrisInferenceEngine | None = None


def get_engine() -> IgrisInferenceEngine:
    global _engine
    if _engine is None:
        ckpt_env = os.environ.get("IGRIS_CHECKPOINT_PATH")
        _engine = IgrisInferenceEngine(checkpoint_path=ckpt_env)
    return _engine


def set_engine(engine: IgrisInferenceEngine) -> None:
    global _engine
    _engine = engine


@app.get("/")
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>IGRIS Inference Runtime</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0b0f19; color: #f3f4f6; margin: 0; padding: 40px; display: flex; justify-content: center; align-items: center; min-height: 80vh; }
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 32px; max-width: 600px; width: 100%; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37); backdrop-filter: blur(12px); }
    h1 { margin-top: 0; font-size: 24px; color: #60a5fa; }
    p { color: #9ca3af; line-height: 1.6; }
    .badge { display: inline-block; padding: 4px 10px; background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 16px; }
    .endpoint-list { list-style: none; padding: 0; margin: 20px 0; }
    .endpoint-list li { margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); }
    .endpoint-list a { color: #38bdf8; text-decoration: none; font-family: monospace; font-weight: 600; }
    .endpoint-list a:hover { text-decoration: underline; }
    .btn { display: block; text-align: center; background: #2563eb; color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 24px; transition: background 0.2s; }
    .btn:hover { background: #1d4ed8; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">&#9679; ONLINE &bull; IGRIS Inference Runtime 3B.53</div>
    <h1>IGRIS Local Inference Runtime</h1>
    <p>The Python FastAPI + PyTorch backend service is running successfully on port 8000.</p>
    <p>This service provides local inference endpoints for the IGRIS Liquid Glass chat frontend.</p>
    <ul class="endpoint-list">
      <li><span>API Health Status</span> <a href="/health">/health</a></li>
      <li><span>Interactive API Documentation</span> <a href="/docs">/docs</a></li>
      <li><span>Model Inventory</span> <a href="/v1/models">/v1/models</a></li>
      <li><span>OpenAI Chat Completions</span> <a href="/v1/chat/completions">/v1/chat/completions</a></li>
    </ul>
    <a class="btn" href="http://localhost:3000" target="_blank">Open Liquid Glass Frontend (Port 3000) &rarr;</a>
    <p style="font-size: 12px; text-align: center; margin-top: 16px; color: #6b7280;">If the frontend is not yet running, start it by running <code>run_frontend.bat</code>.</p>
  </div>
</body>
</html>"""
        return Response(content=html_content, media_type="text/html")
    return JSONResponse(
        content={
            "service": "IGRIS Local Inference Runtime",
            "version": "3B.53",
            "status": "online",
            "endpoints": {
                "health": "/health",
                "models": "/v1/models",
                "chat_completions": "/v1/chat/completions",
                "generate": "/v1/generate",
                "docs": "/docs",
            },
        }
    )


@app.get("/health", response_model=HealthResponse)
@app.get("/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    engine = get_engine()
    return HealthResponse(
        status="healthy",
        model_loaded=engine.is_trained,
        model_state=engine.model_state,  # "MODEL_NOT_TRAINED" or "MODEL_LOADED"
        model_name=engine.model_name,
        active_device=str(engine.device),
        tokenizer=TokenizerStatus(
            name="Candidate A (ByteLevel BPE)",
            vocab_size=engine.tokenizer.get_vocab_size(),
            sha256=engine.tokenizer_sha256,
            verified=engine.tokenizer_verified,
            structural_tokens_count=12,
        ),
        hardware=engine.hardware.to_dict(),
        checkpoint_path=str(engine.checkpoint_path) if engine.checkpoint_path else None,
        version="3B.53",
    )


@app.get("/v1/models", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    engine = get_engine()
    models = [
        ModelCard(
            id="igris-prod-16l",
            created=1732100000,
            family="IGRIS Core",
            parameters="79.7M (tied) / 96.5M (untied)",
            context_window=2048,
            quantization="FP16 / INT8",
            status=engine.model_state,
            architecture={
                "layers": 16,
                "hidden_size": 512,
                "intermediate_size": 2048,
                "attention_heads": 8,
                "kv_heads": 4,
                "rope_theta": 10000.0,
                "swiglu": True,
                "rms_norm_eps": 1e-5,
            },
        ),
        ModelCard(
            id="igris-50m-baseline",
            created=1732100000,
            family="IGRIS Baseline",
            parameters="51.6M (tied) / 68.4M (untied)",
            context_window=2048,
            quantization="FP16 / INT8",
            status="Architecture Baseline",
            architecture={
                "layers": 12,
                "hidden_size": 512,
                "intermediate_size": 1376,
                "attention_heads": 8,
                "kv_heads": 4,
                "rope_theta": 10000.0,
                "swiglu": True,
                "rms_norm_eps": 1e-5,
            },
        ),
        ModelCard(
            id="igris-candidate-a",
            created=1732100000,
            family="IGRIS Tokenizer",
            parameters="32,768 Vocab",
            context_window=2048,
            quantization="ByteLevel BPE",
            status="VERIFIED INVARIANT",
            architecture={
                "structural_tokens": 12,
                "byte_fallback": True,
                "sha256": engine.tokenizer_sha256,
            },
        ),
    ]
    return ModelListResponse(data=models)


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest, raw_request: Request):
    engine = get_engine()

    if not req.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request 'messages' cannot be empty.",
        )

    # Check if model weights are trained
    if not engine.is_trained:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "message": (
                        "IGRIS model architecture and Candidate A tokenizer are verified, but no trained checkpoint "
                        "has been loaded. Pretraining has not yet run in accordance with governance policies."
                    ),
                    "type": "model_not_trained",
                    "code": "MODEL_NOT_TRAINED",
                    "model_state": "MODEL_NOT_TRAINED",
                    "tokenizer_verified": engine.tokenizer_verified,
                }
            },
        )

    dict_messages = [{"role": m.role, "content": m.content} for m in req.messages]
    req_id = f"chatcmpl-{int(time.time() * 1000)}"

    # SSE Streaming response
    if req.stream:
        async def event_generator() -> AsyncGenerator[str, None]:
            async def is_cancelled() -> bool:
                return await raw_request.is_disconnected()

            try:
                async for chunk in engine.generate_stream(
                    prompt_or_messages=dict_messages,
                    temperature=req.temperature,
                    top_p=req.top_p,
                    max_tokens=req.max_tokens,
                    cancellation_check=is_cancelled,
                ):
                    delta_text = chunk.get("delta_text", "")
                    is_final = chunk.get("is_final", False)

                    if not is_final:
                        payload = ChatCompletionChunk(
                            id=req_id,
                            created=int(time.time()),
                            model=req.model,
                            choices=[
                                ChunkChoice(
                                    index=0,
                                    delta=DeltaContent(role="assistant", content=delta_text),
                                    finish_reason=None,
                                )
                            ],
                            model_state="MODEL_GENERATING",
                        )
                        yield f"data: {payload.model_dump_json()}\n\n"
                    else:
                        usage_dict = chunk.get("usage")
                        usage = UsageInfo(**usage_dict) if usage_dict else None
                        finish_reason = chunk.get("finish_reason", "stop")

                        payload = ChatCompletionChunk(
                            id=req_id,
                            created=int(time.time()),
                            model=req.model,
                            choices=[
                                ChunkChoice(
                                    index=0,
                                    delta=DeltaContent(),
                                    finish_reason=finish_reason,
                                )
                            ],
                            usage=usage,
                            model_state="MODEL_LOADED",
                        )
                        yield f"data: {payload.model_dump_json()}\n\n"
                        yield "data: [DONE]\n\n"

            except Exception as stream_err:
                logger.error(f"Error during SSE stream: {stream_err}")
                err_payload = {"error": {"message": str(stream_err), "type": "stream_error"}}
                yield f"data: {json.dumps(err_payload)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # Standard non-streaming response
    start_time = time.perf_counter()
    res = await engine.generate(
        dict_messages,
        temperature=req.temperature,
        top_p=req.top_p,
        max_tokens=req.max_tokens,
    )

    latency_ms = int((time.perf_counter() - start_time) * 1000)
    usage = UsageInfo(
        prompt_tokens=res["usage"]["prompt_tokens"],
        completion_tokens=res["usage"]["completion_tokens"],
        total_tokens=res["usage"]["total_tokens"],
        latency_ms=latency_ms,
    )

    return ChatCompletionResponse(
        id=req_id,
        created=int(time.time()),
        model=req.model,
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=res["text"]),
                finish_reason=res.get("finish_reason", "stop"),
            )
        ],
        usage=usage,
        model_state=engine.model_state,
        is_demo=False,
    )


@app.post("/v1/generate")
@app.post("/generate")
async def generate_endpoint(req: GenerateRequest, raw_request: Request):
    engine = get_engine()

    if not req.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request 'prompt' cannot be empty.",
        )

    if not engine.is_trained:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "message": "IGRIS model is not trained. Checkpoint weights are required to perform inference.",
                    "code": "MODEL_NOT_TRAINED",
                    "model_state": "MODEL_NOT_TRAINED",
                }
            },
        )

    req_id = f"gen-{int(time.time() * 1000)}"
    start_time = time.perf_counter()

    res = await engine.generate(
        req.prompt,
        temperature=req.temperature,
        top_p=req.top_p,
        max_tokens=req.max_tokens,
    )

    latency_ms = int((time.perf_counter() - start_time) * 1000)
    return GenerateResponse(
        id=req_id,
        text=res["text"],
        prompt_tokens=res["usage"]["prompt_tokens"],
        completion_tokens=res["usage"]["completion_tokens"],
        total_tokens=res["usage"]["total_tokens"],
        latency_ms=latency_ms,
        finish_reason=res.get("finish_reason", "stop"),
        model_state=engine.model_state,
        is_demo=False,
    )


def _bytes_char_mapping() -> dict[str, int]:
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {chr(c): b for b, c in zip(bs, cs)}


_BYTE_DEC = _bytes_char_mapping()


def _decode_token_safely(token_str: str) -> tuple[str, bytes]:
    raw_bytes = bytes([_BYTE_DEC.get(c, 0) for c in token_str])
    try:
        decoded = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        decoded = "".join(f"<0x{b:02X}>" for b in raw_bytes)
    return decoded, raw_bytes


@app.post("/v1/tokenize", response_model=TokenizeResponse)
@app.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text(req: TokenizeRequest) -> TokenizeResponse:
    """Tokenize input text using the verified Candidate A ByteLevel BPE tokenizer."""
    engine = get_engine()
    if not req.text:
        return TokenizeResponse(
            tokens=[],
            token_count=0,
            character_count=0,
            byte_count=0,
            reconstructed_text="",
            exact_roundtrip=True,
            tokenizer_name="Candidate A (ByteLevel BPE)",
            tokenizer_sha256=engine.tokenizer_sha256,
        )

    encoding = engine.tokenizer.encode(req.text, add_special_tokens=req.add_special_tokens)
    token_pieces: List[TokenPiece] = []
    all_bytes = bytearray()
    for token_id, token_str, (start, end) in zip(encoding.ids, encoding.tokens, encoding.offsets):
        decoded, raw_bytes = _decode_token_safely(token_str)
        all_bytes.extend(raw_bytes)
        token_pieces.append(
            TokenPiece(
                id=token_id,
                piece=token_str,
                decoded=decoded,
                raw_hex=raw_bytes.hex(),
                start=start,
                end=end,
            )
        )

    reconstructed = all_bytes.decode("utf-8", errors="replace")
    exact_match = (reconstructed == req.text)

    return TokenizeResponse(
        tokens=token_pieces,
        token_count=len(token_pieces),
        character_count=len(req.text),
        byte_count=len(all_bytes),
        reconstructed_text=reconstructed,
        exact_roundtrip=exact_match,
        tokenizer_name="Candidate A (ByteLevel BPE)",
        tokenizer_sha256=engine.tokenizer_sha256,
    )


def start_server(host: str = "127.0.0.1", port: int = 8000, log_level: str = "info"):
    """Launch local uvicorn server daemon."""
    import uvicorn
    uvicorn.run("igris.inference.server:app", host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    start_server()
