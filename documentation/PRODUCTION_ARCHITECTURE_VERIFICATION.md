# IGRIS Production Architecture Verification Report

**Engineering Role**: Senior ML Systems Engineer & Architecture Auditor  
**Model Name**: `igris-prod-16l` (Authoritative Production Architecture)  
**Baseline Profile**: `igris-50m-baseline` (Preserved Architectural Baseline)  
**Operating Model**: SOLO_DEVELOPER_OWNER_REVIEW  
**Date**: November 2026  
**Status**: **VERIFIED — 100% SPECIFICATION CONFORMANCE**

---

## 1. Production Architecture Specifications

The official production model architecture for IGRIS has been verified in code (`src/igris/model/transformer.py`) and programmatic parameter counts:

| Hyperparameter | Approved Value | Verification Status |
| :--- | :--- | :--- |
| **Model Type** | Decoder-Only Causal Transformer | Verified |
| **Layers ($L$)** | **16** | Verified |
| **Hidden Dimension ($d_{\text{model}}$)** | **512** | Verified |
| **FFN Intermediate Dimension ($d_{\text{ffn}}$)** | **2,048** ($4 \times d_{\text{model}}$) | Verified |
| **Query Attention Heads ($H_Q$)** | **8** | Verified |
| **Key/Value Heads ($H_{KV}$)** | **4** | Verified |
| **GQA Ratio** | **2:1** (8 Query : 4 KV) | Verified |
| **Head Dimension ($d_{\text{head}}$)** | **64** ($512 / 8$) | Verified |
| **Positional Embedding** | RoPE ($\theta = 10,000.0$) | Verified |
| **Activation Function** | SwiGLU ($W_{\text{gate}} \cdot \text{SiLU}(W_{\text{up}}) \cdot W_{\text{down}}$) | Verified |
| **Normalization** | Pre-LayerNorm RMSNorm (`eps=1e-5`) | Verified |
| **Embedding Tying** | `tie_word_embeddings = True` | Verified |
| **Vocabulary Size ($V$)** | **32,768** (Candidate A BPE) | Verified |
| **Context Length ($T$)** | **2,048** tokens | Verified |

---

## 2. Parameter Count Verification

### 2.1 Authoritative Production Architecture (`igris-prod-16l`)

The mathematical parameter counts for the 16-layer production model were validated against PyTorch:

$$\text{Tied Unique Parameters} = \mathbf{79,708,672}\text{ (~79.7M)}$$
$$\text{Untied Registered Parameters} = \mathbf{96,485,888}\text{ (~96.5M)}$$

```python
# Programmatic assertion in verify_inference_integration.py
cfg_prod = get_production_config()
cfg_prod.tie_word_embeddings = True
m_prod = IgrisDecoderTransformer(cfg_prod)
tied_unique_prod = sum(p.numel() for p in set(m_prod.parameters()))
assert tied_unique_prod == 79708672  # PASSED

cfg_untied = get_production_config()
cfg_untied.tie_word_embeddings = False
m_untied = IgrisDecoderTransformer(cfg_untied)
untied_registered_prod = sum(p.numel() for p in m_untied.parameters())
assert untied_registered_prod == 96485888  # PASSED
```

#### Detailed Layer-by-Layer Breakdown:
- **Token Embeddings ($W_{\text{embed}}$)**: $32,768 \times 512 = 16,777,216$
- **Per-Layer Attention**:
  - RMSNorm: $512$
  - $W_Q$ ($512 \times 512$): $262,144$
  - $W_K$ ($512 \times 256$): $131,072$
  - $W_V$ ($512 \times 256$): $131,072$
  - $W_O$ ($512 \times 512$): $262,144$
  - Attention Subtotal: $786,944$
- **Per-Layer SwiGLU FFN**:
  - RMSNorm: $512$
  - $W_{\text{gate}}$ ($512 \times 2048$): $1,048,576$
  - $W_{\text{up}}$ ($512 \times 2048$): $1,048,576$
  - $W_{\text{down}}$ ($2048 \times 512$): $1,048,576$
  - FFN Subtotal: $3,146,240$
- **Total Per Layer**: $786,944 + 3,146,240 = 3,933,184$
- **16 Layers Subtotal**: $16 \times 3,933,184 = 62,930,944$
- **Final RMSNorm**: $512$
- **Total Unique (Tied)**: $16,777,216 + 62,930,944 + 512 = \mathbf{79,708,672}$
- **Total Untied**: $79,708,672 + 16,777,216\text{ (LM Head)} = \mathbf{96,485,888}$

---

## 3. Preservation of 12-Layer Baseline Architecture

The 12-layer exploratory architecture (`igris-50m-baseline`) is maintained as a separate, distinct configuration:

| Hyperparameter | Production (`igris-prod-16l`) | Baseline (`igris-50m-baseline`) |
| :--- | :---: | :---: |
| **Number of Layers** | **16** | **12** |
| **FFN Dimension** | **2,048** | **1,376** |
| **Tied Unique Parameters** | **79,708,672** | **51,589,632** |
| **Untied Parameters** | **96,485,888** | **68,366,848** |
| **Role** | **Authoritative Production** | **Exploratory Baseline** |

```python
# Programmatic assertion in verify_inference_integration.py
cfg_base = get_baseline_50m_config()
cfg_base.tie_word_embeddings = True
m_base = IgrisDecoderTransformer(cfg_base)
tied_unique_base = sum(p.numel() for p in set(m_base.parameters()))
assert tied_unique_base == 51589632  # PASSED
```

Neither architecture has been silently mutated or overwritten. Both profiles are fully registered and independently instantiable.
