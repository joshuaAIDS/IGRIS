# IGRIS PHASE 21A — TOKENIZER SELECTION RECORD
## Formal Owner Decision Documentation

**Document ID:** `IGRIS-PHASE21A-TSR-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Project Owner / Reviewer:** Sole Developer  
**Status:** **OWNER DECISION RECORDED — CANDIDATE A SELECTED**  

---

## 1. Formal Owner Decision

Pursuant to the `SOLO_DEVELOPER_OWNER_REVIEW` governance framework, the Project Owner has evaluated the empirical evidence presented in Phase 15 and Phase 21 and formally recorded the following decision:

```
====================================================================================================
OFFICIAL OWNER DECISION:
SELECTED TOKENIZER:     CANDIDATE A
ARCHITECTURE:           ByteLevel BPE (HuggingFace Fast Tokenizers)
STATUS:                 SELECTED FOR INITIAL IGRIS DEVELOPMENT
DECISION BASIS:         PHASE 15 & PHASE 21 COMPARATIVE BENCHMARK RESULTS
COMPARISON CANDIDATE:   CANDIDATE B (SentencePiece Unigram) RETAINED AS UNSELECTED BASELINE
====================================================================================================
```

---

## 2. Decision Rationale & Technical Evidence Basis

The decision to select **Candidate A** is grounded in verified empirical metrics from [PHASE21_TOKENIZER_SELECTION_RECOMMENDATION.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21_TOKENIZER_SELECTION_RECOMMENDATION.md) and [candidate_comparison.json](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/reports/phase15/candidate_comparison.json):

1. **Superior Multilingual Sequence Compression:**
   * Overall fertility is **2.1% lower** in Candidate A (12.43 tokens/word) versus Candidate B (12.69 tokens/word). Across a 13-billion token pretraining corpus, this represents an effective efficiency gain of ~270 million tokens of sequence capacity.
   * In high-resource Indic target registers, Candidate A demonstrates marked superiority:
     * **Tamil (`ta`):** Candidate A fertility = 11.43 vs Candidate B = 12.56 (**Candidate B produces +9.89% more tokens**).
     * **Hindi (`hi`):** Candidate A fertility = 7.98 vs Candidate B = 8.24 (**Candidate B produces +3.26% more tokens**).
     * **Tanglish (`ta-Latn`):** Candidate A fertility = 5.95 vs Candidate B = 5.98.
     * **Code-Switching:** Candidate A fertility = 9.59 vs Candidate B = 9.74.
2. **Hardware Memory Efficiency:**
   * Candidate A operates with **54.29 KB peak RAM** during batch tokenization, consuming **46.4% less memory** than Candidate B (101.35 KB). This provides optimal scaling for multi-worker PyTorch DataLoader pipelines during distributed pretraining.
3. **Lossless Unicode & Structural Token Integrity:**
   * Candidate A maintains **100.0% exact byte round-trip fidelity** and **100.0% NFC canonical round-trip fidelity** across all 9 target registers (en, hi, ta, te, ml, kn, bn, gu, tanglish).
   * Structural tokens `<|pad|>` through `<|assistant|>` are strictly pinned at IDs 0–11.
4. **Toolchain Integration:**
   * Candidate A's `tokenizer.json` format integrates natively with HuggingFace Tokenizers and FlashAttention/PyTorch tokenized streaming loaders with zero C++ wrapper bridging.

---

## 3. Cryptographic Hash Verification & File Immutability

Both tokenizer candidates were verified directly against active physical disk storage using standard SHA-256 calculation:

| Candidate | Target File Path | Architecture | Physical SHA-256 Digest | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Candidate A** | `artifacts/tokenizer/candidate_a/tokenizer.json` | ByteLevel BPE | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | **SELECTED / INVARIANT** |
| **Candidate B** | `artifacts/tokenizer/candidate_b/tokenizer.model` | Unigram LM | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **RETAINED / INVARIANT** |

### Immutability Invariant:
* Neither file was retrained, regenerated, overwritten, or modified.
* Both hashes match their earliest recorded baselines from Phase 6.
* Candidate B is retained on disk as an immutable comparative reference artifact.

---

## 4. Governance Boundaries & Prohibitions

This selection record authorizes **strictly the designation of Candidate A as the active development tokenizer**.

The following activities remain strictly prohibited:
* **Production Dataset Ingress:** **LOCKED** (Default-Deny Enforced).
* **Dataset Acquisition:** **NOT AUTHORIZED** (Zero sources authorized).
* **Production Pretraining:** **NOT AUTHORIZED** (Gates locked).
* **Tokenizer File Modification:** **PROHIBITED** (Hashes immutable).
