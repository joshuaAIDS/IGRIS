# IGRIS Model Architecture Reconciliation Report

**Engineering Role**: Senior ML Systems Engineer  
**Project**: IGRIS — Multilingual Decoder-Only Transformer  
**Status**: Authoritative Production & Baseline Profiles Reconciled  
**Date**: November 2026  

---

## 1. Executive Summary & Audit Scope

Prior to deploying the local inference runtime and connecting the Liquid Glass frontend, a comprehensive architectural audit was performed to resolve discrepancies between:
1. Early exploratory design documents (e.g. `documentation/ARCHITECTURE.md` referencing a 12-layer, 51.6M parameter model termed `IGRIS-50M-Baseline`).
2. The frozen authoritative Phase 19/20/22 Production Architecture implemented in `src/igris/model/transformer.py` featuring 16 layers, an intermediate size of 2048, and 79.7M unique tied parameters.

This report documents the architectural audit, resolves parameter count discrepancies, details the exact mathematical formulas for every parameter group, and verifies that the approved production architecture is fully preserved without silent mutations.

---

## 2. Architecture Comparison Matrix

| Architectural Feature | Early Baseline Profile (`igris-50m-baseline`) | Authoritative Production (`igris-prod-16l`) | Reconciled Status |
| :--- | :--- | :--- | :--- |
| **Model Type** | Causal Decoder-Only Transformer | Causal Decoder-Only Transformer | **Identical** |
| **Vocabulary Size ($V$)** | 32,768 (Candidate A BPE) | 32,768 (Candidate A BPE) | **Identical** |
| **Context Window ($T$)** | 2,048 tokens | 2,048 tokens | **Identical** |
| **Hidden Dimension ($d_{\text{model}}$)** | 512 | 512 | **Identical** |
| **Transformer Layers ($L$)** | **12** | **16** | **Reconciled (Profiled)** |
| **Intermediate Size ($d_{\text{ffn}}$)** | **1,376** | **2,048** | **Reconciled (Profiled)** |
| **Query Heads ($H_Q$)** | 8 | 8 | **Identical** |
| **Key/Value Heads ($H_{KV}$)** | 4 | 4 | **Identical (GQA 2:1)** |
| **Head Dimension ($d_{\text{head}}$)** | 64 ($512 / 8$) | 64 ($512 / 8$) | **Identical** |
| **Attention Mechanism** | Grouped-Query Attention (GQA) | Grouped-Query Attention (GQA) | **Identical** |
| **Positional Embedding** | Rotary Position Embedding (RoPE) | Rotary Position Embedding (RoPE) | **Identical** |
| **RoPE $\theta$ Base** | 10,000.0 | 10,000.0 | **Identical** |
| **Activation Function** | SwiGLU | SwiGLU | **Identical** |
| **Normalization** | Pre-LayerNorm RMSNorm (`eps=1e-5`) | Pre-LayerNorm RMSNorm (`eps=1e-5`) | **Identical** |
| **Embedding Tying** | `tie_word_embeddings = True` | `tie_word_embeddings = True` | **Identical** |
| **Tied Parameter Count** | **51,589,632 (~51.6M)** | **79,708,672 (~79.7M)** | **Fully Accounted** |
| **Untied Parameter Count** | **68,366,848 (~68.4M)** | **96,485,888 (~96.5M)** | **Fully Accounted** |

---

## 3. Discrepancy Investigation & Root Cause

### Root Cause Analysis

1. **Phase 1 Exploration (Draft Architecture)**:
   In initial planning phases, a minimal 50M parameter target was drafted to test extreme low-memory limits on embedded microcontrollers. The draft configuration used $L = 12$ layers and an intermediate feed-forward dimension of $d_{\text{ffn}} = 1,376 \approx \frac{8}{3} d_{\text{model}}$. With tied embeddings, this yielded:
   $$\text{Params}_{\text{tied}} = 51,589,632 \approx 51.6\text{M}$$
   The initial Liquid Glass UI retained this label as `IGRIS-50M-Baseline`.

2. **Phase 19/20/22 Scaling Freeze (Production Architecture)**:
   During multilingual ablation experiments with Candidate A, scaling to $L = 16$ layers and $d_{\text{ffn}} = 2,048 = 4 \times d_{\text{model}}$ provided significantly superior Tamil Unicode grapheme coherence and Tanglish code-switching stability, while remaining exceptionally lightweight (< 200 MB in FP16, < 1 GB runtime VRAM).
   With tied embeddings, this yielded:
   $$\text{Params}_{\text{tied}} = 79,708,672 \approx 79.7\text{M}$$

### Resolution Strategy
- **Production Truth**: `igris-prod-16l` is registered as the primary, authoritative IGRIS model architecture in both the Python engine and frontend catalog.
- **Baseline Preservation**: The 12-layer `igris-50m-baseline` is retained in the engine and model registry as an architectural baseline profile for comparative benchmarking, satisfying all historical references without ambiguity.

---

## 4. Parameter Mathematical Breakdown

### 4.1 Global Parameters (Common to Both Profiles)

1. **Token Embeddings ($W_{\text{embed}}$)**:
   $$V \times d_{\text{model}} = 32,768 \times 512 = 16,777,216\text{ parameters}$$

2. **Final Output Norm ($\text{RMSNorm}_{\text{final}}$)**:
   $$d_{\text{model}} = 512\text{ parameters}$$

3. **Language Modeling Head ($W_{\text{lm\_head}}$)**:
   - When **untied**: $V \times d_{\text{model}} = 32,768 \times 512 = 16,777,216\text{ parameters}$.
   - When **tied**: $0$ additional parameters (shares storage with $W_{\text{embed}}$).

---

### 4.2 Per-Layer Attention Parameters (GQA 8:4)

Each transformer layer contains:
- Input Attention RMSNorm: $d_{\text{model}} = 512$
- $W_Q$ Projection: $d_{\text{model}} \times (H_Q \times d_{\text{head}}) = 512 \times 512 = 262,144$
- $W_K$ Projection: $d_{\text{model}} \times (H_{KV} \times d_{\text{head}}) = 512 \times (4 \times 64) = 512 \times 256 = 131,072$
- $W_V$ Projection: $d_{\text{model}} \times (H_{KV} \times d_{\text{head}}) = 512 \times (4 \times 64) = 512 \times 256 = 131,072$
- $W_O$ Output Projection: $(H_Q \times d_{\text{head}}) \times d_{\text{model}} = 512 \times 512 = 262,144$

$$\text{Params}_{\text{Attention Layer}} = 512 + 262,144 + 131,072 + 131,072 + 262,144 = 786,944\text{ parameters}$$

---

### 4.3 Per-Layer Feed-Forward Parameters (SwiGLU)

SwiGLU requires three linear projections: Gate, Up, and Down.
- Post-Attention RMSNorm: $d_{\text{model}} = 512$
- $W_{\text{gate}}$ Projection: $d_{\text{model}} \times d_{\text{ffn}}$
- $W_{\text{up}}$ Projection: $d_{\text{model}} \times d_{\text{ffn}}$
- $W_{\text{down}}$ Projection: $d_{\text{ffn}} \times d_{\text{model}}$

#### For Authoritative Production ($d_{\text{ffn}} = 2,048$):
- $W_{\text{gate}} = 512 \times 2048 = 1,048,576$
- $W_{\text{up}} = 512 \times 2048 = 1,048,576$
- $W_{\text{down}} = 2048 \times 512 = 1,048,576$
- RMSNorm $= 512$
$$\text{Params}_{\text{FFN}} = 512 + 3 \times 1,048,576 = 3,146,240\text{ parameters}$$

$$\text{Params}_{\text{Total Per Layer}} = 786,944 + 3,146,240 = 3,933,184\text{ parameters}$$

#### For 16 Layers:
$$\text{Params}_{\text{Layers}} = 16 \times 3,933,184 = 62,930,944\text{ parameters}$$

#### Total Model Parameters (Production):
$$\text{Params}_{\text{tied}} = 16,777,216 + 62,930,944 + 512 = \mathbf{79,708,672}\text{ (~79.7M)}$$
$$\text{Params}_{\text{untied}} = 79,708,672 + 16,777,216 = \mathbf{96,485,888}\text{ (~96.5M)}$$

---

#### For Baseline Profile ($d_{\text{ffn}} = 1,376$):
- $W_{\text{gate}} = 512 \times 1376 = 704,512$
- $W_{\text{up}} = 512 \times 1376 = 704,512$
- $W_{\text{down}} = 1376 \times 512 = 704,512$
- RMSNorm $= 512$
$$\text{Params}_{\text{FFN}} = 512 + 3 \times 704,512 = 2,114,048\text{ parameters}$$

$$\text{Params}_{\text{Total Per Layer}} = 786,944 + 2,114,048 = 2,900,992\text{ parameters}$$

#### For 12 Layers:
$$\text{Params}_{\text{Layers}} = 12 \times 2,900,992 = 34,811,904\text{ parameters}$$

#### Total Model Parameters (Baseline):
$$\text{Params}_{\text{tied}} = 16,777,216 + 34,811,904 + 512 = \mathbf{51,589,632}\text{ (~51.6M)}$$
$$\text{Params}_{\text{untied}} = 51,589,632 + 16,777,216 = \mathbf{68,366,848}\text{ (~68.4M)}$$

---

## 5. Checkpoint Format Specification

IGRIS checkpoints adhere to standard PyTorch serialization (`.pt` or `.bin`) containing a dictionary with strictly typed state tensors:

```python
{
    "model_state_dict": {
        "embed_tokens.weight": torch.Tensor(32768, 512),
        "layers.0.input_layernorm.weight": torch.Tensor(512),
        "layers.0.self_attn.q_proj.weight": torch.Tensor(512, 512),
        "layers.0.self_attn.k_proj.weight": torch.Tensor(256, 512),
        "layers.0.self_attn.v_proj.weight": torch.Tensor(256, 512),
        "layers.0.self_attn.o_proj.weight": torch.Tensor(512, 512),
        "layers.0.post_attention_layernorm.weight": torch.Tensor(512),
        "layers.0.mlp.gate_proj.weight": torch.Tensor(2048, 512),
        "layers.0.mlp.up_proj.weight": torch.Tensor(2048, 512),
        "layers.0.mlp.down_proj.weight": torch.Tensor(512, 2048),
        # ... repeated for layers 1 to 15 ...
        "norm.weight": torch.Tensor(512),
        "lm_head.weight": torch.Tensor(32768, 512)  # Optional if tied
    },
    "config": {
        "vocab_size": 32768,
        "hidden_size": 512,
        "intermediate_size": 2048,
        "num_hidden_layers": 16,
        "num_attention_heads": 8,
        "num_key_value_heads": 4,
        "max_position_embeddings": 2048,
        "rope_theta": 10000.0,
        "rms_norm_eps": 1e-05,
        "tie_word_embeddings": true
    },
    "step": 0,
    "tokenizer_sha256": "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
}
```

---

## 6. Verification and Audit Sign-Off

The test suite (`tests/test_inference_runtime.py::test_04_architecture_parameter_counts`) programmatically initializes both models and validates parameter allocations against PyTorch tensor tensors:
- Authoritative Production ($L=16, d_{\text{ffn}}=2048$): **79,708,672 parameters** (PASS).
- Baseline Profile ($L=12, d_{\text{ffn}}=1376$): **51,589,632 parameters** (PASS).

No unapproved alterations have been introduced. Both configurations are fully supported by the local inference engine.
