"""Pydantic schemas for IGRIS Local Inference API (OpenAI-compatible & Native)."""
from __future__ import annotations

from typing import Any, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "igris-prod-16l"
    messages: List[ChatMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=512, ge=1, le=2048)
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = None


class GenerateRequest(BaseModel):
    prompt: str
    model: str = "igris-prod-16l"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=512, ge=1, le=2048)
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = None


class UsageInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: Optional[int] = None
    tokens_per_second: Optional[float] = None


class ChatChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: Optional[str] = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: UsageInfo
    model_state: str = "MODEL_LOADED"
    is_demo: bool = False


class DeltaContent(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class ChunkChoice(BaseModel):
    index: int = 0
    delta: DeltaContent
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChunkChoice]
    usage: Optional[UsageInfo] = None
    model_state: str = "MODEL_GENERATING"
    is_demo: bool = False


class GenerateResponse(BaseModel):
    id: str
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    finish_reason: str = "stop"
    model_state: str = "MODEL_LOADED"
    is_demo: bool = False


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "igris-core"
    family: str
    parameters: str
    context_window: int
    quantization: str
    status: str
    architecture: dict[str, Any]


class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelCard]


class TokenizerStatus(BaseModel):
    name: str = "Candidate A (ByteLevel BPE)"
    vocab_size: int = 32768
    sha256: str
    verified: bool
    structural_tokens_count: int = 12


class TokenPiece(BaseModel):
    id: int
    piece: str
    decoded: str
    raw_hex: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None


class TokenizeRequest(BaseModel):
    text: str
    add_special_tokens: bool = False


class TokenizeResponse(BaseModel):
    tokens: List[TokenPiece]
    token_count: int
    character_count: int
    byte_count: int
    reconstructed_text: str
    exact_roundtrip: bool
    tokenizer_name: str
    tokenizer_sha256: str


class HealthResponse(BaseModel):
    status: str = "healthy"
    model_loaded: bool
    model_state: Literal["MODEL_NOT_TRAINED", "MODEL_LOADED", "DEMO_MODE", "MODEL_GENERATING"]
    model_name: str
    active_device: str
    tokenizer: TokenizerStatus
    hardware: dict[str, Any]
    checkpoint_path: Optional[str] = None
    version: str = "3B.53"
