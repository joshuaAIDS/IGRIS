# PHASE 31 — PYTHON DOCUMENTATION BENCHMARK CONTAMINATION PLAN

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target Source:** `SRC-TD-03` (Python Official Documentation)  
**Date:** 2026-11-20  

---

## 1. Target Evaluation Benchmarks
The following benchmarks evaluate Python code synthesis and algorithmic reasoning:
1. **OpenAI HumanEval:** 164 hand-crafted Python programming problems with unit tests.
2. **Google MBPP (Mostly Basic Python Problems):** 974 crowd-sourced Python coding problems.
3. **DS-1000:** 1,000 data science coding problems (NumPy, Pandas, SciPy, Scikit-Learn).

---

## 2. Contamination Detection Architecture

```mermaid
flowchart TD
    A["Raw Python Docstring / Code Snippet"] --> B["Whitespace & Quote Normalizer"]
    B --> C{"Exact SHA-256 Match with Benchmark Prompt?"}
    C -- "Yes" --> D["REJECT_BENCHMARK_OVERLAP (Hard Reject)"]
    C -- "No" --> E["AST Signature & Docstring Extractor"]
    E --> F{"Normalized Signature Match?"}
    F -- "Yes" --> D
    F -- "No" --> G["13-gram MinHash / Jaccard Overlap"]
    G -- "Similarity >= 0.85" --> D
    G -- "0.70 <= Similarity < 0.85" --> H["QUARANTINE_FOR_MANUAL_REVIEW"]
    G -- "Similarity < 0.70" --> I["PASS_DECONTAMINATION"]
```

### 2.1 Detection Tiers
1. **Tier 1 (Exact Match):** Cryptographic SHA-256 hash comparison of extracted docstrings against canonical benchmark prompts.
2. **Tier 2 (Normalized Match):** Stripping comments, normalizing docstring formatting, and matching normalized AST function definitions.
3. **Tier 3 (Near-Duplicate Overlap):** 13-gram Jaccard similarity. A threshold $\ge 0.70$ triggers review; $\ge 0.85$ triggers immediate rejection.

### 2.2 False-Positive Handling
Common elementary idioms (e.g. standard `fibonacci` docstring, simple list comprehensions, `import sys`) may exhibit token overlap without representing benchmark contamination. Such cases are assigned structural weights based on AST depth before triggering rejection.

### 2.3 Residual Risk Qualification
Automated decontamination significantly minimizes the hazard of pretraining memorization, but does not provide mathematical certainty against subtle algorithmic overlaps.
