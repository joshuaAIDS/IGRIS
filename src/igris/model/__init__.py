"""IGRIS Transformer SLM Core Module.

Implements a decoder-only, autoregressive transformer architecture with Rotary Position
Embeddings (RoPE), Grouped-Query Attention (GQA), Root Mean Square Normalization (RMSNorm),
and SwiGLU feed-forward networks.
"""
from __future__ import annotations

from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    IgrisRMSNorm,
    IgrisRotaryEmbedding,
    IgrisGroupedQueryAttention,
    IgrisSwiGLUMLP,
    IgrisTransformerBlock,
    get_production_config,
    get_baseline_50m_config,
    get_test_tiny_config,
)

__all__ = [
    "IgrisConfig",
    "IgrisDecoderTransformer",
    "IgrisRMSNorm",
    "IgrisRotaryEmbedding",
    "IgrisGroupedQueryAttention",
    "IgrisSwiGLUMLP",
    "IgrisTransformerBlock",
    "get_production_config",
    "get_baseline_50m_config",
    "get_test_tiny_config",
]
