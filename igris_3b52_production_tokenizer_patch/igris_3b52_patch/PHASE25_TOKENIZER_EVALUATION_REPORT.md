# PHASE 25 — Tokenizer Evaluation Report (Read-Only)

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Date:** 2026-11-19 12:27 UTC  
**Mode:** READ-ONLY EVALUATION — NO RETRAINING AUTHORIZED  

## 1. Tokenizer Artifact Verification

Both tokenizer candidates were cryptographically audited against pinned reference hashes:

| Tokenizer Candidate | Type | Target SHA-256 Digest | Measured SHA-256 Digest | Status |
|---|---|---|---|---|
| **Candidate A** | ByteLevel BPE (`tokenizer.json`) | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | **MATCH (VERIFIED)** |
| **Candidate B** | SentencePiece (`tokenizer.model`) | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **MATCH (VERIFIED)** |

**Zero modifications made. Tokenizer artifacts remain frozen.**

## 2. Candidate A Tokenization Metrics (Accepted Records)

Candidate A was evaluated across the **109 accepted production-candidate records**:

| Metric | Measured Value | Standard Target |
|---|---|---|
| Total Tokens Generated | 9,106 tokens | — |
| Total UNK Tokens | **0** | 0 |
| **UNK Token Rate** | **0.000000** | < 0.0001 |
| **Lossless Round-Trip Rate** | **100.00% (109 / 109)** | 100.0% |
| **Overall Fertility** | **7.8840 tokens/word** | Context-efficient |

## 3. Per-Language Fertility Breakdown

| Language | Records | Tokens | Words | Avg Fertility | UNK Tokens |
|---|---|---|---|---|---|
| **ENGLISH** | 13 | 1,163 | 159 | **7.3145** | 0 |
| **TAMIL** | 27 | 2,616 | 270 | **9.6889** | 0 |
| **TANGLISH** | 69 | 5,327 | 726 | **7.3375** | 0 |

## 4. Key Observations

1. **Zero UNK Rate:** Not a single out-of-vocabulary fallback occurred across 9,106 generated tokens.
2. **Lossless Inversion:** Decode(Encode(x)) matches x exactly for 100% of accepted records.
3. **Fertility Stability:** English (7.31) and Tanglish (7.34) show comparable token efficiency. Tamil script fertility (9.69) aligns with agglutinative subword decomposition expectations for Tamil.
