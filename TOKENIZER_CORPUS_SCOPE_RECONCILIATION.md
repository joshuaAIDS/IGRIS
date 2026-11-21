# IGRIS Tokenizer Corpus Scope & Denominator Reconciliation Report
## Forensic Reconciliation of the 833-Word Fixture Draft vs. 437-Word Curated Audit Sample

**Document Identifier:** `IGRIS-REPORT-CORPUS-SCOPE-RECONCILIATION-V1`  
**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-21  
**Status:** **RECONCILED & AUDITED**

---

## 1. Executive Summary

This report forensically investigates and resolves the numerical discrepancy observed between two different evaluation data scopes cited in tokenizer audit documentation:

1. **Earlier Draft Fixture Corpus:** 833 words, 7,258 Original Candidate A tokens, 4,017 Exp A tokens.
2. **Authoritative Curated Audit Corpus:** 437 words, 3,429 Original Candidate A tokens, 1,943 Exp A tokens.

Both datasets are legitimate artifacts of the research and audit pipeline, but they represent **two distinct evaluation stages with different sampling rules, item counts, and word denominators**. They must never be conflated.

---

## 2. Dataset Scope Comparison

| Scope Dimension | Earlier Draft Scope (Linguistic Fixture Suite) | Authoritative Curated Scope (Human Review Sample) |
|---|---|---|
| **Primary File References** | `scratch/build_linguistic_audit.py`, `scratch/build_segmentation_report.py` | [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv), [TOKENIZER_FRAGMENTATION_ANALYSIS.csv](file:///C:/IGRIS/TOKENIZER_FRAGMENTATION_ANALYSIS.csv) |
| **Associated Language Files** | Raw fixture lists (`TAMIL_FIXTURES`, `ENGLISH_FIXTURES`, `TANGLISH_FIXTURES`) | [TAMIL_SEGMENTATION_AUDIT.csv](file:///C:/IGRIS/TAMIL_SEGMENTATION_AUDIT.csv), [ENGLISH_SEGMENTATION_AUDIT.csv](file:///C:/IGRIS/ENGLISH_SEGMENTATION_AUDIT.csv), [TANGLISH_SEGMENTATION_AUDIT.csv](file:///C:/IGRIS/TANGLISH_SEGMENTATION_AUDIT.csv) |
| **Total Test Items ($N$)** | **354 raw items** (139 Tamil, 110 English, 105 Tanglish) | **Exactly 300 curated items** (100 Tamil, 100 English, 100 Tanglish) |
| **Total Words ($N_{\text{words}}$)** | **833 words** (249 Tamil, 243 English, 341 Tanglish) | **437 words** (103 Tamil, 118 English, 216 Tanglish) |
| **Total Characters ($N_{\text{chars}}$)** | **5,018 characters** | **3,412 characters** (692 Tamil, 1,180 English, 1,540 Tanglish) |
| **Original Candidate A Tokens** | **7,258 tokens** (2,724 Tamil, 2,349 English, 2,185 Tanglish) | **3,429 tokens** (898 Tamil, 1,063 English, 1,468 Tanglish) |
| **Experimental Candidate A Tokens** | **4,017 tokens** (1,999 Tamil, 1,036 English, 982 Tanglish) | **1,943 tokens** (632 Tamil, 571 English, 740 Tanglish) |
| **Candidate A Fertility** | 8.713 tokens/word | 7.8467 tokens/word |
| **Candidate Exp Fertility** | 4.823 tokens/word | 4.4462 tokens/word |
| **Sequence Length Reduction** | **-44.65%** | **-43.34%** |
| **Excessive Fragmentation ($\ge 5$)** | Cand A: 74.53% $\to$ Cand Exp: 39.41% | Cand A: 70.71% $\to$ Cand Exp: 43.94% |
| **Round-Trip Bitwise Accuracy** | **100.00%** | **100.00%** |
| **Governing Purpose** | Initial automated exploration and fixture generation | Governed owner-review audit packet (100/100/100 balance) |

---

## 3. Provenance & Filter Investigation

### 3.1 The Earlier 354-Item / 833-Word Fixture Pool
* **Origin:** During initial linguistic harness development, `scratch/build_linguistic_audit.py` assembled an expanded suite of test fixtures covering morphological inflections, technical compounds, and conversational code-switching.
* **Composition:**
  - `TAMIL_FIXTURES`: 139 items (expanded from initial 124 to include additional noun declensions and verb stems).
  - `ENGLISH_FIXTURES`: 110 items (including multi-word phrases such as `asynchronous task execution`, `memory allocation overhead`, `distributed consensus protocol`).
  - `TANGLISH_FIXTURES`: 105 items (including multi-clause sentences such as `intha feature-ah immediate-ah deploy pannidalam`).
* **Why it had 833 words:** Several fixtures contained multi-word sentences and technical descriptions. Summing whitespace words across all 354 items yielded $249 + 243 + 341 = 833$ words.
* **Why it had 7,258 tokens:** Candidate A's severe byte-level fragmentation produced 2,724 tokens on the 139 Tamil items, 2,349 on English, and 2,185 on Tanglish, totaling 7,258 tokens.

### 3.2 The Authoritative 300-Item / 437-Word Curated Audit Sample
* **Origin:** Project governance mandated a strictly balanced **300-item evaluation register** (`TOKENIZER_HUMAN_REVIEW_SAMPLE.csv`), comprising **exactly 100 Tamil, 100 English, and 100 Tanglish items**.
* **Filtering and Normalization:**
  - The 139 Tamil fixtures were pruned to exactly 100 representative items (`REV-TA-001` to `REV-TA-100`), focusing on core nominal suffixes, verb tenses, and Grantha ligatures.
  - The 110 English fixtures were pruned to exactly 100 items (`REV-EN-001` to `REV-EN-100`), removing redundant technical variations.
  - The 105 Tanglish fixtures were pruned to exactly 100 items (`REV-TG-001` to `REV-TG-100`).
* **Why it has 437 words:**
  - 100 Tamil items: primarily single inflected words and short verb phrases $\to$ **103 words**.
  - 100 English items: single vocabulary terms, compound words, and short pairs $\to$ **118 words**.
  - 100 Tanglish items: code-switched phrases and hyphenated loanwords $\to$ **216 words**.
  - Total: $103 + 118 + 216 = \mathbf{437\text{ words}}$.
* **Why it has 3,429 tokens:**
  - Candidate A produces 898 tokens on Tamil, 1,063 on English, and 1,468 on Tanglish, totaling **3,429 tokens**.
  - Experimental Candidate A produces 632 tokens on Tamil, 571 on English, and 740 on Tanglish, totaling **1,943 tokens**.

---

## 4. Denominator & Mathematical Reconciliation

To eliminate any ambiguity across documents:

1. **The Official Benchmark Denominator is $N_{\text{words}} = 437$:**
   All official audit deliverables ([TOKENIZER_FRAGMENTATION_ANALYSIS.csv](file:///C:/IGRIS/TOKENIZER_FRAGMENTATION_ANALYSIS.csv), [TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md](file:///C:/IGRIS/TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md), [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv)) strictly report on the **curated 300-item / 437-word corpus**.
2. **Consistency of Qualitative Findings:**
   The two datasets yield identical conclusions:
   - Token sequence compression: **44.65%** on the 354-item pool vs. **43.34%** on the 300-item pool.
   - Reduction in excessive fragmentation ($\ge 5$ tokens): **-35.12%** on the 354-item pool vs. **-26.77%** on the 300-item pool.
   - Exact round-trip accuracy: **100.00%** on both.
   - Grapheme cluster disruption in Tamil: Confirmed on both.

---

## 5. Summary Conclusion

There is no data corruption or contradictory calculation. The 833-word figure belongs to the preliminary 354-item fixture suite, whereas the 437-word figure belongs to the official 300-item balanced human-review register. All future reporting will reference the authoritative 300-item / 437-word corpus.
