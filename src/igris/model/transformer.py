"""IGRIS Decoder-Only Transformer Architecture Implementation.

Implements the formal architecture defined in Section 2 of IGRIS Architecture Specification:
  - Decoder-only autoregressive causal attention.
  - Grouped-Query Attention (GQA 8 query heads, 4 key-value heads, 2:1 ratio).
  - Rotary Position Embeddings (RoPE) with base theta = 10000.0.
  - Root Mean Square Layer Normalization (RMSNorm) with eps = 1e-5.
  - SwiGLU Feed-Forward Network (FFN).
  - Untied input embedding and output projection matrices.
  - 32,768 vocabulary matching Candidate A and Candidate B tokenizers.
  - Context length up to 2048 tokens.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.checkpoint


@dataclass
class IgrisConfig:
    """Hyperparameters for IGRIS Decoder-Only Transformer."""
    name: str = "igris-transformer"
    vocab_size: int = 32768
    hidden_size: int = 512
    intermediate_size: int = 2048  # Production target: 2048; Baseline 50M: 1376
    num_hidden_layers: int = 16    # Production target: 16 layers; Baseline 50M: 12 layers
    num_attention_heads: int = 8
    num_key_value_heads: int = 4   # GQA 2:1 ratio
    max_position_embeddings: int = 2048
    rms_norm_eps: float = 1e-5
    rope_theta: float = 10000.0
    tie_word_embeddings: bool = False
    dropout: float = 0.0
    pad_token_id: int = 0
    bos_token_id: int = 1
    eos_token_id: int = 2
    initializer_range: float = 0.02
    gradient_checkpointing: bool = False

    @property
    def head_dim(self) -> int:
        return self.hidden_size // self.num_attention_heads

    @property
    def num_key_value_groups(self) -> int:
        return self.num_attention_heads // self.num_key_value_heads

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IgrisConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def get_production_config() -> IgrisConfig:
    """Return production target configuration (16 layers, intermediate=2048, hidden=512)."""
    return IgrisConfig(
        name="igris-prod-16l",
        vocab_size=32768,
        hidden_size=512,
        intermediate_size=2048,
        num_hidden_layers=16,
        num_attention_heads=8,
        num_key_value_heads=4,
        max_position_embeddings=2048,
        tie_word_embeddings=False,
    )


def get_baseline_50m_config() -> IgrisConfig:
    """Return 50M baseline configuration from ARCHITECTURE.md (12 layers, intermediate=1376)."""
    return IgrisConfig(
        name="igris-50m-baseline",
        vocab_size=32768,
        hidden_size=512,
        intermediate_size=1376,
        num_hidden_layers=12,
        num_attention_heads=8,
        num_key_value_heads=4,
        max_position_embeddings=2048,
        tie_word_embeddings=False,
    )


def get_test_tiny_config() -> IgrisConfig:
    """Return tiny configuration for fast local unit testing and synthetic training."""
    return IgrisConfig(
        name="igris-test-tiny",
        vocab_size=32768,
        hidden_size=128,
        intermediate_size=256,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        max_position_embeddings=2048,
        tie_word_embeddings=False,
    )


class IgrisRMSNorm(nn.Module):
    """Root Mean Square Layer Normalization (RMSNorm)."""

    def __init__(self, hidden_size: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(hidden_size))

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.eps)
        return (self.weight * hidden_states).to(input_dtype)


class IgrisRotaryEmbedding(nn.Module):
    """Rotary Position Embedding (RoPE) applied to query and key projections."""

    def __init__(self, dim: int, max_position_embeddings: int = 2048, base: float = 10000.0):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2).float() / self.dim))
        self.register_buffer("inv_freq", inv_freq, persistent=False)

    def _rotate_half(self, x: torch.Tensor) -> torch.Tensor:
        x1 = x[..., : x.shape[-1] // 2]
        x2 = x[..., x.shape[-1] // 2 :]
        return torch.cat((-x2, x1), dim=-1)

    def forward(self, q: torch.Tensor, k: torch.Tensor, seq_len: int) -> Tuple[torch.Tensor, torch.Tensor]:
        device = q.device
        t = torch.arange(seq_len, device=device, dtype=self.inv_freq.dtype)
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        cos = emb.cos()[None, None, :, :]  # [1, 1, seq_len, dim]
        sin = emb.sin()[None, None, :, :]

        q_rot = (q * cos) + (self._rotate_half(q) * sin)
        k_rot = (k * cos) + (self._rotate_half(k) * sin)
        return q_rot.to(q.dtype), k_rot.to(k.dtype)


def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    """Repeat Key-Value heads to match Query heads for Grouped-Query Attention."""
    if n_rep == 1:
        return hidden_states
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)


class IgrisGroupedQueryAttention(nn.Module):
    """Grouped-Query Attention (GQA) with causal masking and RoPE."""

    def __init__(self, config: IgrisConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.head_dim = config.head_dim
        self.num_key_value_heads = config.num_key_value_heads
        self.num_key_value_groups = config.num_key_value_groups

        self.q_proj = nn.Linear(self.hidden_size, self.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(self.hidden_size, self.num_key_value_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(self.num_heads * self.head_dim, self.hidden_size, bias=False)

        self.rotary_emb = IgrisRotaryEmbedding(
            dim=self.head_dim,
            max_position_embeddings=config.max_position_embeddings,
            base=config.rope_theta,
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        bsz, q_len, _ = hidden_states.shape

        q = self.q_proj(hidden_states)
        k = self.k_proj(hidden_states)
        v = self.v_proj(hidden_states)

        q = q.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)
        v = v.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(1, 2)

        # Apply RoPE
        q, k = self.rotary_emb(q, k, q_len)

        # Repeat KV for GQA
        k = repeat_kv(k, self.num_key_value_groups)
        v = repeat_kv(v, self.num_key_value_groups)

        # Scaled dot-product attention
        scores = torch.matmul(q, k.transpose(2, 3)) / math.sqrt(self.head_dim)

        # Causal mask: prevent future-token leakage
        causal_mask = torch.triu(
            torch.full((q_len, q_len), float("-inf"), device=hidden_states.device),
            diagonal=1,
        )[None, None, :, :]
        scores = scores + causal_mask

        # Optional padding mask
        if attention_mask is not None:
            # attention_mask: [bsz, 1, 1, q_len] or [bsz, 1, q_len, q_len]
            scores = scores + attention_mask

        attn_weights = F.softmax(scores, dim=-1, dtype=torch.float32).to(q.dtype)
        output = torch.matmul(attn_weights, v)

        output = output.transpose(1, 2).contiguous().view(bsz, q_len, -1)
        return self.o_proj(output)


class IgrisSwiGLUMLP(nn.Module):
    """Feed-Forward Network (FFN) using SwiGLU activation."""

    def __init__(self, config: IgrisConfig):
        super().__init__()
        self.gate_proj = nn.Linear(config.hidden_size, config.intermediate_size, bias=False)
        self.up_proj = nn.Linear(config.hidden_size, config.intermediate_size, bias=False)
        self.down_proj = nn.Linear(config.intermediate_size, config.hidden_size, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # SwiGLU(x) = (SiLU(gate_proj(x)) * up_proj(x)) * down_proj
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class IgrisTransformerBlock(nn.Module):
    """Pre-layer-norm Transformer Decoder Layer."""

    def __init__(self, config: IgrisConfig):
        super().__init__()
        self.input_layernorm = IgrisRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.self_attn = IgrisGroupedQueryAttention(config)
        self.post_attention_layernorm = IgrisRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.mlp = IgrisSwiGLUMLP(config)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # Self-attention with pre-norm & residual
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states = self.self_attn(hidden_states, attention_mask=attention_mask)
        hidden_states = residual + hidden_states

        # MLP with pre-norm & residual
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states

        return hidden_states


class IgrisDecoderTransformer(nn.Module):
    """Full IGRIS Decoder-Only Autoregressive Transformer Model."""

    def __init__(self, config: IgrisConfig):
        super().__init__()
        self.config = config

        self.embed_tokens = nn.Embedding(
            config.vocab_size,
            config.hidden_size,
            padding_idx=config.pad_token_id,
        )
        self.layers = nn.ModuleList([IgrisTransformerBlock(config) for _ in range(config.num_hidden_layers)])
        self.norm = IgrisRMSNorm(config.hidden_size, eps=config.rms_norm_eps)

        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        if config.tie_word_embeddings:
            self.lm_head.weight = self.embed_tokens.weight

        # Weight initialization
        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module) -> None:
        std = self.config.initializer_range
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()

    def count_parameters(self) -> dict[str, int]:
        """Compute exact parameter breakdown."""
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        embed = self.embed_tokens.weight.numel()
        lm_head = self.lm_head.weight.numel() if not self.config.tie_word_embeddings else 0
        layers_total = sum(p.numel() for p in self.layers.parameters())
        norm = self.norm.weight.numel()

        return {
            "total_parameters": total,
            "trainable_parameters": trainable,
            "embedding_parameters": embed,
            "lm_head_parameters": lm_head,
            "layers_parameters": layers_total,
            "final_norm_parameters": norm,
        }

    def gradient_checkpointing_enable(self) -> None:
        """Enable activation / gradient checkpointing to reduce VRAM consumption."""
        self.config.gradient_checkpointing = True

    def gradient_checkpointing_disable(self) -> None:
        """Disable activation / gradient checkpointing."""
        self.config.gradient_checkpointing = False

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
    ) -> dict[str, Any]:
        """Forward pass with causal self-attention and optional loss computation."""
        bsz, seq_len = input_ids.shape

        if seq_len > self.config.max_position_embeddings:
            raise ValueError(
                f"Sequence length {seq_len} exceeds max_position_embeddings {self.config.max_position_embeddings}"
            )

        # Prepare attention mask for padding tokens
        extended_mask = None
        if attention_mask is not None:
            # attention_mask: [bsz, seq_len] with 1 for tokens, 0 for pad
            # Convert to [bsz, 1, 1, seq_len] additive mask with -inf for pad
            extended_mask = (1.0 - attention_mask[:, None, None, :].float()) * -10000.0

        hidden_states = self.embed_tokens(input_ids)

        for layer in self.layers:
            if self.config.gradient_checkpointing and self.training:
                hidden_states = torch.utils.checkpoint.checkpoint(
                    layer,
                    hidden_states,
                    extended_mask,
                    use_reentrant=False,
                )
            else:
                hidden_states = layer(hidden_states, attention_mask=extended_mask)

        hidden_states = self.norm(hidden_states)
        logits = self.lm_head(hidden_states)

        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
            loss = loss_fn(
                shift_logits.view(-1, self.config.vocab_size),
                shift_labels.view(-1),
            )

        return {
            "logits": logits,
            "loss": loss,
            "hidden_states": hidden_states,
        }
