# PHASE 21B3A — TOKEN AND COMPUTE ESTIMATE CORRECTIONS
## Chinchilla Ratio Arithmetic Correction and Model Architecture Parameter Accounting

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3A  

---

## 1. Formal Qualification of the 25–30 Billion Token Figure

In Phase 21B3, a theoretical extrapolation suggested that if the entire 183.70 GB raw corpus were tokenized under Candidate A, it would produce 25–30 billion tokens.

This figure is strictly qualified and labeled as:

**UNVALIDATED_CAPACITY_PLANNING_HYPOTHESIS**  
$$\mathbf{UNVALIDATED\_CAPACITY\_PLANNING\_HYPOTHESIS}$$

### Required Assumptions to Validate This Hypothesis:
1. **Character Encoding:** Uniform UTF-8 byte representation without binary corruption.
2. **Average Bytes Per Character:** Indic UTF-8 characters require 3 bytes per codepoint, whereas ASCII requires 1 byte.
3. **Language Distribution:** The proportion of high-resource Hindi (~80 GB) vs Dravidian languages.
4. **Unicode Normalization:** Impact of NFC normalization on Indic combining characters and diacritics.
5. **Candidate A Tokenization Behavior:** Subword fertility rate of the 32,768 ByteLevel BPE vocabulary on agglutinative Dravidian roots vs Indo-Aryan vocabulary.
6. **Deduplication Rate:** The proportion of duplicate news syndication and web crawl headers removed by MinHash LSH.
7. **Quality-Filter Rejection Rate:** The rejection volume from perplexity, line-length, and fastText language identification filtering.
8. **Source Sampling Strategy:** Whether the pipeline ingests the complete raw corpus or extracts a balanced linguistic slice.

*This estimate is an unvalidated planning hypothesis and is NOT an approved pretraining budget.*

---

## 2. Correction of Chinchilla Over-Training Arithmetic

In Phase 21B3 documentation, training on 25 billion tokens was erroneously described as a *"~340× over-training regime"*. This was a mathematical phrasing error:

### Corrected Arithmetic:
1. **Tokens Per Parameter Ratio:**  
   $$	ext{Tokens per parameter} = rac{25,000,000,000	ext{ tokens}}{73,400,000	ext{ parameters}} pprox 340.6	ext{ tokens/parameter}$$
2. **Comparison to Chinchilla Compute-Optimal Baseline:**  
   - The Chinchilla heuristic (Hoffmann et al., 2022) suggests a reference ratio of approximately **20 tokens per parameter** for compute-optimal training.
   - The ratio of 340 tokens/parameter relative to the 20 tokens/parameter reference is:
     $$	ext{Relative Multiplier} = rac{340.6}{20} pprox \mathbf{17.03	imes}$$
   - **Correction:** The scenario represents approximately **17× the reference Chinchilla ratio**, NOT 340×.
3. **The 20-Token Heuristic:** The 20-token-per-parameter heuristic is an approximate compute-optimal reference point for training loss minimization, not a universal or mandatory engineering constraint. Modern architectures (e.g., LLaMA, Gemma) routinely train at 100–300 tokens per parameter to optimize inference latency and memory footprints.

---

## 3. Reconciled IGRIS Model Parameter Count

Previous governance records documented different parameter totals depending on embedding weight-tying configuration.

In accordance with `PHASE20B_MODEL_PARAMETER_ARITHMETIC.md`, the authoritative parameter counts for the IGRIS architecture ($d_{model}=512$, $L=16$, $H=8$, $H_{kv}=4$, $d_{ff}=2048$, $V=32,768$) are:

```
+-----------------------------------+-----------------------------------+-----------------------------------+
| Architectural Metric              | Untied Configuration (Default)    | Tied Configuration                |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Embedding Matrix (Input)          | 16,777,216 parameters             | 16,777,216 parameters (Shared)    |
| 16-Layer Transformer Core         | 62,931,456 parameters             | 62,931,456 parameters             |
| LM Head Projection (Output)       | 16,777,216 parameters             | 0 unique parameters (Reused)      |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Total Unique Parameters in Memory | 96,485,888 (~96.49M)              | 79,708,672 (~79.71M)              |
+-----------------------------------+-----------------------------------+-----------------------------------+
```

### Exact Chinchilla Baseline Ratios for IGRIS:
- **Under Untied Model (96,485,888 params):**  
  - 20× Chinchilla Reference: **1.930 Billion tokens**.  
  - 25B tokens $ightarrow$ $259.1$ tokens/param $pprox \mathbf{13.0	imes}$ reference ratio.
- **Under Tied Model (79,708,672 params):**  
  - 20× Chinchilla Reference: **1.594 Billion tokens**.  
  - 25B tokens $ightarrow$ $313.6$ tokens/param $pprox \mathbf{15.7	imes}$ reference ratio.