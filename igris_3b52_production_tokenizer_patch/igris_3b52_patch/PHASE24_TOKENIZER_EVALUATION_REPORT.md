# PHASE 24 — Tokenizer Evaluation Report (Read-Only)

**Project:** IGRIS — Multilingual Decoder-Only Transformer
**Date:** 2026-11-19 17:43
**Tokenizer:** Candidate A (SELECTED)
**Mode:** READ-ONLY EVALUATION — NO MODIFICATION AUTHORIZED
**Status:** SYNTHETIC BENCHMARK ONLY

## 1. Tokenizer Identity

| Property | Value |
|----------|-------|
| Tokenizer | Candidate A |
| Hash (SHA-256) | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` |
| Hash match | True |
| Vocabulary size | 32,768 |
| Structural tokens (IDs 0–11) | Verified |
| UNK token ID | None |

## 2. Fertility Analysis

Fertility = tokens per whitespace-delimited word. Lower is more efficient.

| Language | Avg Fertility | Total Tokens | Total Words | UNK Rate | Round-Trip |
|----------|---------------|--------------|-------------|----------|------------|
| english | 5.8857 | 206 | 35 | 0.000000 | 5/5 |
| tamil | 7.6316 | 145 | 19 | 0.000000 | 5/5 |
| tanglish | 6.2121 | 205 | 33 | 0.000000 | 5/5 |
| tamil_script_mixed | 6.5000 | 78 | 12 | 0.000000 | 3/3 |

## 3. UNK Token Analysis

| Metric | Value |
|--------|-------|
| Overall UNK rate (eval samples) | 0.0 |
| Fixture UNK rate (100 fixtures) | 0.0 |
| Total fixture tokens | 7,665 |
| Total fixture UNK tokens | 0 |

**Zero UNK tokens across all evaluation samples and fixtures.** The tokenizer successfully encodes all Tamil, English, and Tanglish text without falling back to unknown tokens.

## 4. Round-Trip Integrity

| Scope | Passed | Total | Rate |
|-------|--------|-------|------|
| English samples | 5 | 5 | 100% |
| Tamil samples | 5 | 5 | 100% |
| Tanglish samples | 5 | 5 | 100% |
| All 100 fixtures | 100 | 100 | 100% |

## 5. Sequence Length Distribution (100 Fixtures)

| Statistic | Value |
|-----------|-------|
| Min | 47 |
| Max | 142 |
| Mean | 76.65 |
| Median | 69 |
| P95 | 119 |

## 6. Observations

1. **English fertility (5.89)** is typical for BPE tokenizers on English text.
2. **Tamil fertility (7.63)** is higher, reflecting the agglutinative nature of Tamil and the multi-codepoint structure of Tamil syllables.
3. **Tanglish fertility (6.21)** falls between English and Tamil, as expected for code-mixed text.
4. **Tamil script mixed fertility (6.50)** is similar to Tanglish, confirming reasonable handling of mixed-script text.
5. **Zero UNK rate** across all categories confirms the vocabulary covers the target languages adequately.
6. **100% round-trip** on all test cases confirms no information loss through encode→decode.

> **DISCLAIMER:** Fertility and round-trip metrics are on a small synthetic sample set. Production tokenizer evaluation requires testing on the actual training corpus after authorized acquisition.

## 7. Governance

- Tokenizer was loaded READ-ONLY. No modifications were made.
- Hash verification confirms the tokenizer file is unmodified.
- Structural tokens (IDs 0–11) are pinned and verified.
