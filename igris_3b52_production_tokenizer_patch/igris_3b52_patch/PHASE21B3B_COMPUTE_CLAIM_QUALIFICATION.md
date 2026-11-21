# PHASE 21B3B — COMPUTE CLAIM QUALIFICATION REPORT
## Formal Literature Citation, Compute-Optimal Boundary vs Inference Efficiency, and Architecture Parameter Arithmetic

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3B  

---

## 1. Executive Summary

Phase 21B3B resolves and qualifies earlier statements regarding the "100–300 tokens per parameter" training regime. This document provides formal academic citations, draws a clear distinction between theoretical compute-optimality (Chinchilla) and empirical inference-efficiency trade-offs, and provides the exact parameter arithmetic for the IGRIS model architecture.

All token ratios and training volumes discussed herein are strictly **mathematical projections and capacity planning scenarios**. They do not constitute an authorized compute plan, training budget, or engineering mandate.

---

## 2. Qualification of the "100–300 Tokens per Parameter" Observation

### Academic Foundation: Compute-Optimal Pretraining
In foundational scaling law literature, Hoffmann et al. (2022) (*"Training Compute-Optimal Large Language Models"*, DeepMind, arXiv:2203.15556) demonstrated that given a fixed compute budget $C$, the loss-minimizing allocation scales model size $N$ and token count $D$ equally in proportion:
$$D pprox 20 	imes N$$
This establishes the **Chinchilla reference baseline** of approximately **20 tokens per parameter** for compute-optimal training. Under this regime, training past ~20 tokens/parameter yields diminishing returns in loss reduction *per training FLOP*.

### Industry Evolution: Inference-Optimal Over-Training
While Chinchilla optimality minimizes *pretraining compute*, it ignores *downstream inference cost*. In real-world deployment, inference costs scale with model parameter count $N$, not training token count $D$. Consequently, modern foundation model architectures deliberately over-train smaller parameter models far past the Chinchilla frontier to amortize inference latency and memory footprints:

1. **LLaMA-1 (Touvron et al., Meta, 2023, arXiv:2302.13971):**
   - The 6.7B parameter model was trained on 1.0 Trillion tokens:
     $$rac{1.0 	imes 10^{12}	ext{ tokens}}{6.7 	imes 10^9	ext{ params}} pprox \mathbf{149.3	ext{ tokens/parameter}}\quad (pprox 7.5	imes	ext{ Chinchilla baseline})$$
   - The 65.2B parameter model was trained on 1.4 Trillion tokens ($pprox 21.5$ tokens/parameter).

2. **LLaMA-2 (Touvron et al., Meta, 2023, arXiv:2307.09288):**
   - The 7B parameter model was trained on 2.0 Trillion tokens:
     $$rac{2.0 	imes 10^{12}	ext{ tokens}}{7.0 	imes 10^9	ext{ params}} pprox \mathbf{285.7	ext{ tokens/parameter}}\quad (pprox 14.3	imes	ext{ Chinchilla baseline})$$

3. **Gemma (Gemma Team, Google, 2024, arXiv:2403.08295):**
   - Gemma 2B was trained on 2.0 Trillion tokens ($pprox 1,000$ tokens/parameter).
   - Gemma 7B was trained on 6.0 Trillion tokens ($pprox 857$ tokens/parameter).

4. **LLaMA-3 (Dubey et al. / Meta, 2024, arXiv:2407.21783):**
   - LLaMA-3 8B was trained on 15.0 Trillion tokens ($pprox 1,868$ tokens/parameter).

### Formal Qualification:
The phrase *"100–300 tokens per parameter"* is hereby formally qualified as:

> **An empirical, non-universal industry observation reflecting an inference-optimization trade-off, exemplified by LLaMA-1 7B (~149 tokens/param) and LLaMA-2 7B (~286 tokens/param), rather than a universal theoretical rule or compute-optimal engineering mandate.**

---

## 3. Reconciled IGRIS Model Parameter Arithmetic

The IGRIS architecture is specified with the following hyperparameters:
- Hidden Dimension ($d_{model}$): $512$
- Layers ($L$): $16$
- Attention Heads ($H$): $8$
- Key/Value Heads ($H_{kv}$): $4$ (Grouped-Query Attention 2:1)
- Feed-Forward Dimension ($d_{ff}$): $2048$
- Vocabulary Size ($V$): $32,768$ (Candidate A ByteLevel BPE)
- Structural Tokens: 12 pinned IDs (0–11)

### Parameter Accounting Table:
```
+-----------------------------------+-----------------------------------+-----------------------------------+
| Component                         | Untied Configuration (Default)    | Tied Configuration (Shared)       |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Input Embedding Matrix            | 16,777,216 parameters             | 16,777,216 parameters (Shared)    |
| Transformer Core (16 Layers)      | 62,931,456 parameters             | 62,931,456 parameters             |
| LM Head Projection Matrix         | 16,777,216 parameters             | 0 unique parameters (Reused)      |
| Output LayerNorm                  | 512 parameters                    | 512 parameters                    |
| Embedding LayerNorm / Scalars     | 512 parameters                    | 512 parameters                    |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Total Unique Model Parameters     | 96,485,888 (~96.49M)              | 79,708,672 (~79.71M)              |
+-----------------------------------+-----------------------------------+-----------------------------------+
```

---

## 4. Scenario Analysis: 25-Billion-Token Planning Hypothesis

Under the capacity planning hypothesis of processing the entire cleaned IndicCorp v2 corpus (~25 Billion tokens), the resulting token-to-parameter ratios and Chinchilla multipliers are reconciled as follows:

```
+-------------------------------+-------------------+-----------------------+-------------------+-------------------+
| Model Configuration           | Total Parameters  | Chinchilla 20x Target | 25B Scenario Ratio| Chinchilla Mult.  |
+-------------------------------+-------------------+-----------------------+-------------------+-------------------+
| Untied Architecture (Default) | 96,485,888        | 1,929,717,760 tokens  | 259.10 tokens/p   | 12.96x (~13.0x)   |
| Tied Architecture             | 79,708,672        | 1,594,173,440 tokens  | 313.64 tokens/p   | 15.68x (~15.7x)   |
| Historical Placeholder (73.4M)| 73,400,000        | 1,468,000,000 tokens  | 340.60 tokens/p   | 17.03x (~17.0x)   |
+-------------------------------+-------------------+-----------------------+-------------------+-------------------+
```

### Exact Mathematical Reconciliation:
1. **Untied Configuration (96,485,888 params):**
   $$	ext{Tokens/Param} = rac{25,000,000,000}{96,485,888} pprox 259.105\quad\Longrightarrow\quad rac{259.105}{20} pprox \mathbf{12.955	imes}\ (\mathbf{pprox 13.0	imes})$$
2. **Tied Configuration (79,708,672 params):**
   $$	ext{Tokens/Param} = rac{25,000,000,000}{79,708,672} pprox 313.642\quad\Longrightarrow\quad rac{313.642}{20} pprox \mathbf{15.682	imes}\ (\mathbf{pprox 15.7	imes})$$
3. **Early 73.4M Parameter Placeholder:**
   $$	ext{Tokens/Param} = rac{25,000,000,000}{73,400,000} pprox 340.599\quad\Longrightarrow\quad rac{340.599}{20} pprox \mathbf{17.030	imes}\ (\mathbf{pprox 17.0	imes})$$

---

## 5. Governance Separation of Arithmetic vs Pretraining Authorization

The calculations above represent purely theoretical capacity modeling. Under the `SOLO_DEVELOPER_OWNER_REVIEW` operating model:
- Zero pretraining tokens are approved for training.
- Ingress gate remains strictly `LOCKED`.
- Ingested corpus payload remains `0 bytes`.
