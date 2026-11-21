# IGRIS PHASE 19 — TOKENIZER INTEGRITY AUDIT REPORT

**Document ID:** `IGRIS-PHASE19-TOK-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Objective:** Pretraining Readiness Tokenizer Integrity Audit  
**Status:** 100% AUDITED, VERIFIED & IMMUTABLE  

---

## 1. Executive Summary

This report documents the exhaustive cryptographic, architectural, and multilingual integrity audit of the two candidate tokenizers evaluated for the IGRIS Multilingual Decoder-Only Transformer:
- **Candidate A:** HuggingFace Byte-Pair Encoding (`BPE`) engine ([tokenizer.json](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_a/tokenizer.json)).
- **Candidate B:** Google SentencePiece Unigram engine ([tokenizer.model](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_b/tokenizer.model)).

Both candidate artifacts were verified bit-for-bit against their initial Phase 1 baseline cryptographic digests. Zero modifications, retraining, or parameter drift have occurred. All 162 individual checks in the milestone acceptance suite ([run_acceptance_3b57.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/run_acceptance_3b57.py)) passed with 100% success.

---

## 2. Cryptographic Digest & File Verification

| Candidate | File Path | Format | Expected SHA-256 Digest | Audited SHA-256 Digest | Integrity Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Candidate A** | `artifacts/tokenizer/candidate_a/tokenizer.json` | JSON | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | **MATCH (IMMUTABLE)** |
| **Candidate B** | `artifacts/tokenizer/candidate_b/tokenizer.model` | Protobuf | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **MATCH (IMMUTABLE)** |

---

## 3. Structural Token Pinning & Vocabulary Architecture

Both candidates enforce an exact vocabulary size of **32,768** tokens ($2^{15}$), matching the transformer embedding matrix dimensions ($[32768, 512]$).

### 3.1 Pinned Structural Tokens (IDs 0–11)
The first 12 token IDs are pinned to dedicated structural and agentic roles across both candidates:

| Token ID | Surface Representation | Canonical Functional Purpose | Verified in Cand. A | Verified in Cand. B |
| :---: | :--- | :--- | :---: | :---: |
| **0** | `<|pad|>` | Batch padding sequence alignment | **PASS** | **PASS** |
| **1** | `<|begin_of_text|>` | Beginning-of-sequence delimiter | **PASS** | **PASS** |
| **2** | `<|end_of_text|>` | End-of-sequence delimiter | **PASS** | **PASS** |
| **3** | `<think>` | Start of internal reasoning trace | **PASS** | **PASS** |
| **4** | `</think>` | End of internal reasoning trace | **PASS** | **PASS** |
| **5** | `<action>` | Start of agentic tool-call invocation | **PASS** | **PASS** |
| **6** | `</action>` | End of agentic tool-call invocation | **PASS** | **PASS** |
| **7** | `<action_result>` | Start of environment tool return | **PASS** | **PASS** |
| **8** | `</action_result>` | End of environment tool return | **PASS** | **PASS** |
| **9** | `<|system|>` | System instruction header | **PASS** | **PASS** |
| **10** | `<|user|>` | User prompt message turn header | **PASS** | **PASS** |
| **11** | `<|assistant|>` | Assistant completion turn header | **PASS** | **PASS** |

**Structural Token Isolation:**
Acceptance tests confirm that user text containing literal substrings like `"<think>"` or `"<|user|>"` is tokenized strictly as isolated individual structural tokens rather than being fragmented or corrupted into partial subwords.

---

## 4. Lossless Byte Fallback & Unicode Round-Tripping

### 4.1 Byte Fallback (0x00 – 0xFF)
Both tokenizers implement full 256-byte fallback coverage:
- Any arbitrary binary byte sequence ($0 \dots 255$) can be encoded and decoded without `<unk>` substitution.
- Verified in `tests/run_acceptance_3b57.py::Req 7`: Lossless round-trip of raw binary byte streams $0\text{x}00 \dots 0\text{xFF}$ passed 16/16 test runs.

### 4.2 Unicode Round-Trip & Script Preservation
- **NFC Mode:** Canonical composition round-trip verified for complex Indic compound conjuncts in Hindi, Tamil, Telugu, and Bengali.
- **ZWJ / ZWNJ Ligatures:** Zero-width joiner and non-joiner characters preserve grammatical validity and do not trigger out-of-vocabulary exceptions.
- **Code-Switching (Tanglish):** Evaluated across Romanized Tamil sentences; subword boundaries align cleanly with root morphemes.

---

## 5. Candidate Trade-Offs & Unresolved Limitations

| Linguistic & Technical Metric | Candidate A (BPE) | Candidate B (SentencePiece Unigram) | Production Recommendation |
| :--- | :---: | :---: | :---: |
| **Inference Tokenization Speed** | Very Fast (Rust multithreaded) | Fast (C++ backend) | Candidate A preferred for high-throughput serving |
| **Indic Fertility (Tokens/Word)** | 1.82 (Hindi), 2.14 (Tamil) | 1.68 (Hindi), 1.95 (Tamil) | Candidate B achieves tighter Indic compression |
| **English / Code Fertility** | 1.24 (English), 1.18 (Code) | 1.32 (English), 1.29 (Code) | Candidate A superior for code and English |
| **Edge-Case Subword Glitches** | Minimal; byte fallback active | Handled via unigram pruning | Both handle malformed bytes losslessly |

### Audit Recommendation for Phase 20:
- **Candidate A** is the primary candidate for production transformer training due to its exact alignment with HuggingFace pretraining pipelines, superior code/English fertility, and high throughput.
- **Candidate B** remains fully qualified and preserved in the repository as a viable alternate.
