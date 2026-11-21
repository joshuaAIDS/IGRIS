# IGRIS PHASE 20B — MODEL PARAMETER ARITHMETIC RECONCILIATION

**Document ID:** `IGRIS-PHASE20B-MP-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target:** `IgrisDecoderTransformer` Architecture  
**Status:** FULLY RECONCILED — ZERO ARITHMETIC RESIDUAL  

---

## 1. Executive Summary

This document presents the definitive mathematical and empirical parameter reconciliation of the `IgrisDecoderTransformer` architecture instantiated from `src/igris/model/transformer.py`.

The specific question addressed by Phase 20B is:
```
Reported SwiGLU:         50,331,648
Reported GQA Attention:  12,582,912
-----------------------------------
Sum:                     62,914,560
Reported Non-Embedding:  62,931,456
-----------------------------------
Difference:                  16,896
```

**Finding:** The difference of exactly **16,896 parameters** is completely and rigorously accounted for by the **Root Mean Square Normalization (RMSNorm) layers** across the 16 transformer blocks and the final pre-head normalization layer. There are zero unmapped or unaccounted parameters.

---

## 2. Global Parameter Totals

Direct PyTorch parameter enumeration on the instantiated module:

| Metric | Untied Configuration (Default) | Tied Configuration (`tie_word_embeddings=True`) | Description |
| :--- | :--- | :--- | :--- |
| **Total Registered Parameters** | **96,485,888** | 96,485,888 | Sum of `.numel()` across all `model.parameters()` |
| **Unique Physical Parameters** | **96,485,888** | **79,708,672** | Deduplicated by underlying memory pointer (`data_ptr()`) |
| **Token Embeddings** | **16,777,216** | 16,777,216 | `embed_tokens.weight` ($32,768 \times 512$) |
| **LM Head Output Matrix** | **16,777,216** | 0 (Shared) | `lm_head.weight` ($32,768 \times 512$, shared when tied) |
| **Non-Embedding Parameters** | **62,931,456** | **62,931,456** | Layers 0–15 + Final RMSNorm |

---

## 3. Component Parameter Breakdown

### 3.1 SwiGLU Feed-Forward Network (FFN)
The feed-forward network uses the SwiGLU activation scheme with 3 weight matrices per layer (`gate_proj`, `up_proj`, `down_proj`):
* `gate_proj.weight`: Shape `[2048, 512]` $\rightarrow 1,048,576$ parameters
* `up_proj.weight`: Shape `[2048, 512]` $\rightarrow 1,048,576$ parameters
* `down_proj.weight`: Shape `[512, 2048]` $\rightarrow 1,048,576$ parameters
* **Total per block:** $1,048,576 \times 3 = 3,145,728$ parameters
* **Across 16 blocks:**
  $$16 \times 3,145,728 = \mathbf{50,331,648}\text{ parameters}$$

### 3.2 Grouped Query Attention (GQA 2:1)
The attention mechanism operates with 8 query heads and 4 key-value heads (`num_attention_heads=8, num_key_value_heads=4`), with `head_dim=64`:
* `q_proj.weight`: Shape `[512, 512]` $\rightarrow 262,144$ parameters
* `k_proj.weight`: Shape `[256, 512]` $\rightarrow 131,072$ parameters (4 heads $\times$ 64 dim)
* `v_proj.weight`: Shape `[256, 512]` $\rightarrow 131,072$ parameters (4 heads $\times$ 64 dim)
* `o_proj.weight`: Shape `[512, 512]` $\rightarrow 262,144$ parameters
* **Total per block:** $262,144 + 131,072 + 131,072 + 262,144 = 786,432$ parameters
* **Across 16 blocks:**
  $$16 \times 786,432 = \mathbf{12,582,912}\text{ parameters}$$

### 3.3 Normalization (RMSNorm)
Each of the 16 transformer blocks contains 2 RMSNorm layers (pre-attention and pre-FFN), followed by a final root RMSNorm before the LM head:
* Per-block `input_layernorm.weight`: Shape `[512]` $\rightarrow 512$ parameters
* Per-block `post_attention_layernorm.weight`: Shape `[512]` $\rightarrow 512$ parameters
* **Total RMSNorm per block:** $512 + 512 = 1,024$ parameters
* **16 Blocks Subtotal:** $16 \times 1,024 = 16,384$ parameters
* **Final Pre-Head `norm.weight`:** Shape `[512]` $\rightarrow 512$ parameters
* **Total Normalization Parameters:**
  $$16,384 + 512 = \mathbf{16,896}\text{ parameters}$$

### 3.4 Other Parameters
* **Biases:** All linear projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`, `lm_head`) have `bias=False`.
* **Positional Embeddings:** Rotary Position Embeddings (`IgrisRotaryEmbedding`) use fixed mathematical frequency formulations precomputed as non-trainable buffers (`inv_freq`), contributing **0 trainable parameters**.

---

## 4. Exact Mathematical Reconciliation

$$\begin{aligned}
\text{Non-Embedding Total} &= \text{SwiGLU FFN} + \text{GQA Attention} + \text{RMSNorm} \\
62,931,456 &= 50,331,648 + 12,582,912 + 16,896 \\
62,931,456 &= 62,914,560 + 16,896 \\
62,931,456 &= 62,931,456 \quad (\text{Residual} = 0)
\end{aligned}$$

$$\begin{aligned}
\text{Total Registered (Untied)} &= \text{Token Embeddings} + \text{LM Head} + \text{Non-Embedding} \\
96,485,888 &= 16,777,216 + 16,777,216 + 62,931,456 \\
96,485,888 &= 96,485,888 \quad (\text{Residual} = 0)
\end{aligned}$$

$$\begin{aligned}
\text{Total Unique (Tied)} &= \text{Shared Token Embeddings/LM Head} + \text{Non-Embedding} \\
79,708,672 &= 16,777,216 + 62,931,456 \\
79,708,672 &= 79,708,672 \quad (\text{Residual} = 0)
\end{aligned}$$

---

## 5. Parameter Distribution Summary Table

| Architectural Module | Layer Count | Tensor Names | Tensors per Layer | Parameters per Layer | Module Total | % of Non-Embedding | % of Total Untied |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **SwiGLU FFN** | 16 | `gate_proj`, `up_proj`, `down_proj` | 3 | 3,145,728 | 50,331,648 | 79.98% | 52.17% |
| **GQA Attention** | 16 | `q_proj`, `k_proj`, `v_proj`, `o_proj` | 4 | 786,432 | 12,582,912 | 19.99% | 13.04% |
| **RMSNorm** | 16 (+1) | `input_layernorm`, `post_attention_layernorm`, `norm` | 2 (+1 final) | 1,024 (+512) | 16,896 | 0.03% | 0.02% |
| **Non-Embedding Total** | **16** | — | **7 (+1 final)** | **3,933,184 (+512)** | **62,931,456** | **100.00%** | **65.22%** |
| **Token Embeddings** | — | `embed_tokens` | 1 | — | 16,777,216 | — | 17.39% |
| **LM Head (Untied)** | — | `lm_head` | 1 | — | 16,777,216 | — | 17.39% |
| **Total Model (Untied)**| — | — | **114** | — | **96,485,888** | — | **100.00%** |
| **Total Model (Tied)** | — | — | **113 (unique)** | — | **79,708,672** | — | — |
