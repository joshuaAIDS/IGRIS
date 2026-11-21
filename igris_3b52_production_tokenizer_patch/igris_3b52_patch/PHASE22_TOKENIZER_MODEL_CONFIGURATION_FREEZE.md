# PHASE 22 — TOKENIZER & MODEL CONFIGURATION FREEZE
## Bitwise Integrity Freeze, Architectural Parameter Reconciliation, and Hardware Bounds Specification

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 22  
**Status:** CONFIGURATION FROZEN & MATHEMATICALLY RECONCILED  

---

## 1. Executive Summary

Phase 22 formally freezes the production tokenizer selection and model architecture configuration for the IGRIS project.

- **Selected Tokenizer:** Candidate A (ByteLevel BPE, $V=32,768$) remains selected for initial development.
- **Bitwise Hash Status:** Authoritative SHA-256 digest is verified bit-for-bit unchanged.
- **Reference Tokenizer:** Candidate B (Unigram SentencePiece, $V=32,768$) remains preserved unchanged as an unselected reference candidate.
- **Model Architecture:** IGRIS 3B52 decoder-only transformer parameter arithmetic is fully reconciled and locked.

---

## 2. Tokenizer Checksum Verification & Pinning

```
+-------------------+-----------------------+-------------------------------------------------------------------+-------------------+
| Candidate         | Architecture          | Authoritative SHA-256 Digest                                      | Freeze Status     |
+-------------------+-----------------------+-------------------------------------------------------------------+-------------------+
| Candidate A       | ByteLevel BPE         | ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561 | FROZEN & SELECTED |
| Candidate B       | Unigram SentencePiece | d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888 | FROZEN REFERENCE  |
+-------------------+-----------------------+-------------------------------------------------------------------+-------------------+
```

### 2.1. Structural Token Contract (Tokens 0–11)
The 12 special structural tokens are permanently pinned at indices 0 through 11 in Candidate A:
```
Index 0:  <|pad|>            Index 6:  </action>
Index 1:  <|begin_of_text|>  Index 7:  <action_result>
Index 2:  <|end_of_text|>    Index 8:  </action_result>
Index 3:  <think>            Index 9:  <|system|>
Index 4:  </think>           Index 10: <|user|>
Index 5:  <action>           Index 11: <|assistant|>
```
Total vocabulary size is strictly **32,768 tokens**.

---

## 3. IGRIS 3B52 Architecture & Parameter Reconciliation

The model configuration is strictly locked under `IgrisConfig`:

```
+-----------------------------------+-----------------------+-----------------------------------------------------------+
| Architectural Parameter           | Value                 | Technical Specification                                   |
+-----------------------------------+-----------------------+-----------------------------------------------------------+
| Hidden Dimension ($d$)            | 512                   | Model representation width                                |
| Number of Layers ($L$)            | 16                    | Number of transformer decoder blocks                      |
| Query Attention Heads ($H$)       | 8                     | Head dimension $d_k = 512 / 8 = 64$                       |
| Key/Value Attention Heads ($H_{kv}$) 4                   | Grouped Query Attention (GQA 2:1 ratio)                   |
| Intermediate Dimension ($d_{ff}$) | 2048                  | SwiGLU feed-forward hidden dimension                      |
| Maximum Sequence Length ($S$)     | 2048                  | Rotary Position Embeddings (RoPE) context window          |
| Vocabulary Size ($V$)             | 32,768                | Pinned Candidate A tokenizer vocabulary                   |
| Normalization                     | RMSNorm ($\epsilon=10^{-5}$) Root Mean Square Layer Normalization              |
| Activation Function               | SwiGLU                | Gated linear unit with SiLU activation                    |
+-----------------------------------+-----------------------+-----------------------------------------------------------+
```

### 3.1. Parameter Arithmetic Breakdown

```
+-----------------------------------+-----------------------+-----------------------------------------------------------+
| Layer Component                   | Parameter Count       | Mathematical Formula                                      |
+-----------------------------------+-----------------------+-----------------------------------------------------------+
| Token Embedding Matrix            | 16,777,216            | $V 	imes d = 32,768 	imes 512$                          |
| LM Head (Un-tied Projection)      | 16,777,216            | $d 	imes V = 512 	imes 32,768$                          |
| Attention Weights (Per Layer)     | 786,432               | $W_q (512 	imes 512) + W_k, W_v (2 	imes 512 	imes 256) + W_o (512 	imes 512)$ |
| SwiGLU MLP Weights (Per Layer)    | 3,145,728             | $W_{gate} (512 	imes 2048) + W_{up} (512 	imes 2048) + W_{down} (2048 	imes 512)$ |
| RMSNorm Weights (Per Layer)       | 1,024                 | $AttnNorm (512) + MLP_Norm (512)$                         |
| Total Per Layer                   | 3,933,184             | $786,432 + 3,145,728 + 1,024$                             |
| All 16 Transformer Layers         | 62,930,944            | $16 	imes 3,933,184$                                     |
| Final RMSNorm                     | 512                   | Pre-LM Head normalization                                 |
+-----------------------------------+-----------------------+-----------------------------------------------------------+
| TOTAL REGISTERED (Untied Weights) | 96,485,888 (~96.5M)   | Embedding + Layers + Final Norm + LM Head                 |
| TOTAL UNIQUE (Tied Weights)       | 79,708,672 (~79.7M)   | Embedding + Layers + Final Norm (LM Head tied to Embed)   |
| NON-EMBEDDING PARAMETERS          | 62,931,456 (~62.9M)   | Layers + Final Norm                                       |
+-----------------------------------+-----------------------+-----------------------------------------------------------+
```

---

## 4. Hardware Limitations & Training Profile Constraints

Based on the physical hardware probe of the NVIDIA GeForce RTX 3050 6GB Laptop GPU:
1. **Micro-Batch Size Constraint:** To prevent CUDA Out-of-Memory (OOM) errors, local micro-batch size must be limited to $B \le 4$ sequences of length $S = 1024$ or $B \le 2$ sequences of length $S = 2048$.
2. **FlashAttention / SDPA Mandatory:** Native PyTorch `F.scaled_dot_product_attention` is mandatory to avoid materializing $O(S^2)$ attention matrices in VRAM.
3. **Gradient Checkpointing:** Activation checkpointing must be enabled to cap peak activation memory at $pprox 1.2 	ext{ GiB}$.
4. **Precision Standard:** Training must execute strictly in **Bfloat16 (BF16)** mixed precision, leveraging native Ampere hardware support without dynamic loss scaling artifacts.
