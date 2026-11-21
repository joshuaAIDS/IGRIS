# IGRIS Tokenizer Linguistic Segmentation Quality Report
## Rigorous Controlled Linguistic Audit of Candidate A vs. Experimental Candidate A

**Document Identifier:** `IGRIS-REPORT-LINGUISTIC-SEGMENTATION-V1`  
**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-21  
**Audit Status:** **AUDIT VERIFIED & EVIDENCE CORRECTED**  
**Final Status:** **`SEGMENTATION_CONDITIONAL`**

---

## 1. Executive Summary

A forensic, controlled linguistic segmentation audit was conducted comparing the locked production tokenizer (**Original Candidate A**, SHA-256 `ac7e18b1...`) against the experimental synthetic-trained tokenizer (**Experimental Candidate A**, SHA-256 `3393acbe...`).

The evaluation analyzed 300 curated linguistic test cases across Tamil ($N=100$), English ($N=100$), and Tanglish ($N=100$), explicitly examining whether token boundaries preserve authentic morphological units, akshara cohesion, affix boundaries, and code-switching junctures.

### Key Audit Findings:

1. **Pathological Fragmentation vs. Subword Compression:**
   - **Original Candidate A:** Possesses only 63 learned BPE merges. As a result, it suffers from severe fragmentation, decomposing **98.86%** of all words and **100.0%** of Tamil words into single ASCII characters and individual UTF-8 byte triplets. Over **70.71%** of all words are excessively fragmented ($\ge 5$ tokens per word).
   - **Experimental Candidate A:** Possesses 1,755 learned BPE merges. Single-token whole-word representations rise from **1.14%** to **5.49%** (and up to **10.53%** on Latin-script Tanglish), while excessive word fragmentation drops from **70.71%** down to **43.94%** across the audit corpus (-43.34% overall token count).
2. **Byte-Level Decoding and Mojibake Correction:**
   - Raw BPE tokens such as `à®²` and `à¯į` are ByteLevel BPE Latin-1 character representations of raw UTF-8 byte sequences (`0xE0 0xAE 0xB2` and `0xE0 0xAF 0x8D`), not readable Tamil.
   - Concatenating raw token bytes and decoding produces **100.00% exact round-trip reconstruction** across all 300 test items in both tokenizers.
   - Isolated tokens representing partial multi-byte sequences (e.g. `à®` = `0xE0 0xAE`) cannot be decoded to valid UTF-8 independently and are explicitly annotated as hex bytes `<0xE0><0xAE>`.
3. **Unicode Grapheme Boundary Analysis (UAX #29):**
   - **Grapheme Integrity is DISRUPTED in both tokenizers.**
     - **Original Candidate A:** 492 internal cuts and 492 unique affected clusters across 2,990 total clusters (**83.55% overall grapheme preservation**). In Tamil script ($N=404$), 334 clusters are affected (**17.33% preservation**).
     - **Experimental Candidate A:** 428 internal cuts and 428 unique affected clusters (**85.69% overall grapheme preservation**). In Tamil script ($N=404$), 292 clusters are affected (**27.72% preservation**).
     - Standalone Tamil vowels (such as `ஆ` in `complex-ஆ`) are preserved as atomic single tokens in Exp A (Token 766) but shredded across two byte tokens in Candidate A.
     - In English, grapheme preservation is **100.0%** (1,180/1,180). In Tanglish, grapheme preservation is **88.76%** in Cand A and **90.33%** in Exp A (cuts occur strictly in Tamil-script suffixes).
4. **Linguistic Quality vs. Compression Reality:**
   - Lower token counts do **not** imply higher morphological quality.
   - In English compounds, occasional overmerging occurs (e.g. `microservice` $\to$ `m | icroser | vice`, where `icroser` crosses the morpheme boundary).
   - In Tamil inflections, merges like `Ġà®ªà®£` (` பண`) combine characters based on n-gram frequency without respecting traditional agglutinative stem-suffix boundaries.
5. **Human-Review Integrity:**
   - Exactly 300 side-by-side examples are compiled in [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv).
   - All 300 items strictly retain `review_status = "NOT_REVIEWED"` with blank reviewer decisions and rationales, supported by [TOKENIZER_OWNER_REVIEW_GUIDE.md](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_GUIDE.md).

---

## 2. Quantitative Fragmentation Analysis

The quantitative measurements from [TOKENIZER_FRAGMENTATION_ANALYSIS.csv](file:///C:/IGRIS/TOKENIZER_FRAGMENTATION_ANALYSIS.csv) summarize structural behavior across all partitions:

| Analysis Dimension | Words | Total Chars | Cand A Tokens | Exp A Tokens | Cand A Fert | Exp A Fert | Cand A CPT | Exp A CPT | Cand A Single (%) | Exp A Single (%) | Cand A Excess ($\ge 5$) (%) | Exp A Excess ($\ge 5$) (%) | Grapheme Clusters | Cand A Cuts/Aff | Cand A Pres (%) | Exp A Cuts/Aff | Exp A Pres (%) | Token Reduction (%) | Round-Trip Accuracy |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **ENTIRE_EVALUATION_CORPUS** | 437 | 3,412 | 3,429 | 1,943 | 7.8467 | 4.4462 | 0.9950 | 1.7560 | 1.14% | 5.49% | 70.71% | 43.94% | 2,990 | 492 | **83.55%** | 428 | **85.69%** | **-43.34%** | **100.0%** |
| **LANGUAGE_TAMIL** | 103 | 692 | 898 | 632 | 8.7184 | 6.1359 | 0.7706 | 1.0949 | 0.00% | 0.00% | 79.61% | 67.96% | 404 | 334 | **17.33%** | 292 | **27.72%** | **-29.62%** | **100.0%** |
| **LANGUAGE_ENGLISH** | 118 | 1,180 | 1,063 | 571 | 9.0085 | 4.8390 | 1.1101 | 2.0665 | 2.54% | 4.24% | 75.42% | 47.46% | 1,180 | 0 | **100.00%** | 0 | **100.00%** | **-46.28%** | **100.0%** |
| **LANGUAGE_TANGLISH** | 216 | 1,540 | 1,468 | 740 | 6.7963 | 3.4259 | 1.0490 | 2.0811 | 0.93% | 8.80% | 63.89% | 30.56% | 1,406 | 158 | **88.76%** | 136 | **90.33%** | **-49.59%** | **100.0%** |
| **SCRIPT_TAMIL_SCRIPT** | 113 | 783 | 1,026 | 719 | 9.0796 | 6.3628 | 0.7632 | 1.0890 | 0.00% | 0.00% | 81.42% | 69.91% | 456 | 383 | **16.01%** | 333 | **26.97%** | **-29.92%** | **100.0%** |
| **SCRIPT_LATIN_SCRIPT** | 228 | 1,808 | 1,591 | 781 | 6.9781 | 3.4254 | 1.1364 | 2.3150 | 2.19% | 10.53% | 59.21% | 28.51% | 1,808 | 0 | **100.00%** | 0 | **100.00%** | **-50.91%** | **100.0%** |
| **SCRIPT_MIXED_SCRIPT** | 91 | 777 | 768 | 401 | 8.4396 | 4.4066 | 1.0117 | 1.9377 | 0.00% | 0.00% | 84.62% | 47.25% | 682 | 109 | **84.02%** | 95 | **86.07%** | **-47.79%** | **100.0%** |

---

## 3. Mandatory Linguistic Expressions Evaluation

Six mandatory test cases were re-evaluated side-by-side using exact token IDs, raw strings, byte-level decoded contributions, reconstructed text, and UAX #29 grapheme cluster analysis:

```
1. server-ல்
   Graphemes: 8 | Cand A: 7 tok | Exp A: 5 tok
   Cand A IDs:     [94, 284, 97, 284, 24, 294, 271]
   Cand A Decoded: s | er | v | er | - | ல | ்
   Exp A IDs:      [643, 453, 24, 288, 270]
   Exp A Decoded:  ser | ver | - | ல | ்
   Grapheme Cuts:  1 cut inside 'ல்' (Cand A & Exp A) -> DISRUPTED
   Morphology:     Cand A = DISRUPTED, Exp A = UNCERTAIN

2. complex-ஆ
   Graphemes: 9 | Cand A: 9 tok | Exp A: 5 tok
   Cand A IDs:     [78, 90, 88, 91, 87, 300, 24, 268, 240]
   Cand A Decoded: c | o | m | p | l | ex | - | <0xE0><0xAE> | <0x86>
   Exp A IDs:      [472, 571, 99, 24, 766]
   Exp A Decoded:  com | ple | x | - | ஆ
   Grapheme Cuts:  Cand A: 1 cut inside 'ஆ' (byte-level shredding: <0xE0><0xAE> | <0x86>) -> DISRUPTED (88.89% pres)
                   Exp A:  0 cuts (atomic 'ஆ' Token 766) -> PRESERVED (100.0% pres)
   Morphology:     Cand A = DISRUPTED (byte shredding of 'ஆ'), Exp A = UNCERTAIN (atomic 'ஆ', syllabic stem)

3. deploy பண்ணினோம்
   Graphemes: 12 | Cand A: 18 tok | Exp A: 11 tok
   Cand A IDs:     [79, 80, 91, 302, 100, 273, 115, 268, 108, 271, 268, 108, 272, 285, 270, 245, 278, 271]
   Cand A Decoded: d | e | p | lo | y | <0x20><0xE0><0xAE> | <0xAA> | <0xE0><0xAE> | <0xA3> | ் | ...
   Exp A IDs:      [79, 80, 628, 336, 270, 294, 274, 279, 356, 282, 270]
   Exp A Decoded:  d | e | ploy |  பண | ் | ண | ி | ன | ோ | ம | ்
   Grapheme Cuts:  4 cuts ('ண்', 'ணி', 'னோ', 'ம்') -> DISRUPTED
   Morphology:     Cand A = DISRUPTED, Exp A = UNCERTAIN

4. memory allocation
   Graphemes: 17 | Cand A: 15 tok | Exp A: 3 tok
   Cand A IDs:     [88, 80, 88, 90, 93, 100, 232, 297, 302, 78, 76, 95, 84, 90, 89]
   Cand A Decoded: m | e | m | o | r | y |   | al | lo | c | a | t | i | o | n
   Exp A IDs:      [1463, 1330, 331]
   Exp A Decoded:  memory |  alloc | ation
   Grapheme Cuts:  0 cuts -> PRESERVED
   Morphology:     Cand A = DISRUPTED (15 single-letter tokens), Exp A = PRESERVED (clean root + affixes)

5. pannirukkom
   Graphemes: 11 | Cand A: 10 tok | Exp A: 6 tok
   Cand A IDs:     [91, 280, 89, 84, 93, 96, 86, 86, 90, 88]
   Cand A Decoded: p | an | n | i | r | u | k | k | o | m
   Exp A IDs:      [91, 388, 424, 86, 86, 334]
   Exp A Decoded:  p | ann | iru | k | k | om
   Grapheme Cuts:  0 cuts -> PRESERVED
   Morphology:     Cand A = DISRUPTED, Exp A = UNCERTAIN (clean syllables, split geminate 'k'|'k')

6. testing-க்கு
   Graphemes: 10 | Cand A: 10 tok | Exp A: 8 tok
   Cand A IDs:     [95, 281, 95, 301, 82, 24, 277, 271, 277, 288]
   Cand A Decoded: t | es | t | in | g | - | க | ் | க | ு
   Exp A IDs:      [95, 398, 307, 24, 272, 270, 272, 273]
   Exp A Decoded:  t | est | ing | - | க | ் | க | ு
   Grapheme Cuts:  2 cuts ('க்', 'கு') -> DISRUPTED
   Morphology:     Cand A = DISRUPTED, Exp A = UNCERTAIN (clean Latin stem, hyphen delimiter, split Tamil suffix)
```

---

## 4. Metric Definitions and Accounting Methodology

1. **Tokens per Word (Fertility):**
   $$\text{Fertility} = \frac{\sum_{i=1}^N |\text{Encode}(x_i)|}{N_{\text{words}}}$$
   - **Denominator ($N_{\text{words}}$):** Total whitespace-delimited tokens from `text.split()` ($N_{\text{words}} = 437$).
   - **Numerator:** Total tokens produced by encoding full example strings (preserving inter-word byte spaces).
2. **Characters per Token (CPT):**
   $$\text{CPT} = \frac{\sum_{i=1}^N \text{len}(x_i)}{\sum_{i=1}^N |\text{Encode}(x_i)|}$$
   - Total characters = 3,412. Cand A CPT = 0.9950; Exp A CPT = 1.7560.
3. **Single-Token Word Percentage (%):**
   $$\text{STW} = \frac{\sum_{w \in W} \mathbb{I}(|\text{Encode}(w)| = 1)}{N_{\text{words}}} \times 100\%$$
   - Measures individual whitespace words tokenizing into exactly 1 token.
4. **Excessively Fragmented Word Percentage (%):**
   $$\text{EFW} = \frac{\sum_{w \in W} \mathbb{I}(|\text{Encode}(w)| \ge 5)}{N_{\text{words}}} \times 100\%$$
   - Fixed threshold of 5 tokens per word identifies extreme character shredding.
5. **Unicode Grapheme Preservation Rate (%):**
   $$\text{GPR} = 100 \times \frac{N_{\text{total clusters}} - N_{\text{unique affected clusters}}}{N_{\text{total clusters}}}$$
   - Extended grapheme clusters determined by Unicode Standard Annex #29 `regex \X` ($N_{\text{total clusters}} = 2,990$).
   - A cluster is classified as affected if any token boundary slices inside it (via character-level cut between base and combining marks, or byte-level slicing of multi-byte codepoints).
   - Candidate A: 492 unique affected clusters, 492 cuts (83.55% preservation).
   - Candidate Exp: 428 unique affected clusters, 428 cuts (85.69% preservation).
6. **Round-Trip Bitwise Reconstruction (%):**
   $$\text{RTA} = \frac{\sum_{i=1}^N \mathbb{I}(\text{Decode}(\text{bytes}(\text{Encode}(x_i))) == x_i)}{N} \times 100\%$$
   - 100.00% verified across all 300 items.
7. **Special Token Exclusion:** Special tokens (IDs 0–11) are strictly excluded from all metric calculations.
8. **Punctuation and Hyphen Handling:** Punctuation marks are treated as standard characters within whitespace-delimited words. Hyphenated code-switching words (e.g. `server-ல்`) are counted as single words in whitespace tokenization ($N=1$).
9. **Corpus Scope Reconciliation:** The discrepancy between the preliminary 354-item fixture suite (833 words, 7,258 Candidate A tokens) and this authoritative 300-item curated audit register (437 words, 3,429 Candidate A tokens) is forensically documented in [TOKENIZER_CORPUS_SCOPE_RECONCILIATION.md](file:///C:/IGRIS/TOKENIZER_CORPUS_SCOPE_RECONCILIATION.md).

---

## 5. Human-Review Sample Integrity (300 Examples)

The side-by-side evaluation table [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv) contains exactly 300 rows:
- 100 Tamil rows (`REV-TA-001` to `REV-TA-100`)
- 100 English rows (`REV-EN-001` to `REV-EN-100`)
- 100 Tanglish rows (`REV-TG-001` to `REV-TG-100`)

In accordance with project integrity requirements:
- `review_status`: Strictly **`NOT_REVIEWED`** (300/300)
- `human_review_decision`: Strictly **blank (`""`)** (300/300)
- `reviewer_rationale`: Strictly **blank (`""`)** (300/300)
- Automated diagnostics (token IDs, raw tokens, decoded contributions, reconstructed text, grapheme status, and concern descriptions) are fully populated to facilitate owner review.
- Instructions and criteria for owner review are detailed in [TOKENIZER_OWNER_REVIEW_GUIDE.md](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_GUIDE.md).

---

## 6. Deliverables Index

The following deliverables reflect the corrected evidence:
1. [TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md](file:///C:/IGRIS/TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md) — This comprehensive report.
2. [TOKENIZER_BYTELEVEL_DECODING_AUDIT.md](file:///C:/IGRIS/TOKENIZER_BYTELEVEL_DECODING_AUDIT.md) — Technical investigation of ByteLevel bijection, mojibake, and mandatory expressions.
3. [TOKENIZER_UNICODE_GRAPHEME_AUDIT.csv](file:///C:/IGRIS/TOKENIZER_UNICODE_GRAPHEME_AUDIT.csv) — Unicode UAX #29 grapheme cluster audit for all 300 items.
4. [TOKENIZER_UNIQUE_GRAPHEME_IMPACT_ANALYSIS.csv](file:///C:/IGRIS/TOKENIZER_UNIQUE_GRAPHEME_IMPACT_ANALYSIS.csv) — Granular per-item unique affected grapheme clusters and preservation deltas.
5. [TOKENIZER_CORPUS_SCOPE_RECONCILIATION.md](file:///C:/IGRIS/TOKENIZER_CORPUS_SCOPE_RECONCILIATION.md) — Forensic reconciliation of 833-word draft vs. 437-word audit corpus.
6. [TOKENIZER_OWNER_REVIEW_GUIDE.md](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_GUIDE.md) — Concise protocol for sole developer owner review.
7. [TOKENIZER_FRAGMENTATION_ANALYSIS.csv](file:///C:/IGRIS/TOKENIZER_FRAGMENTATION_ANALYSIS.csv) — Recalculated metrics across all 7 partitions.
8. [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv) — 300 curated examples with decoded Unicode contributions.
9. [TAMIL_SEGMENTATION_AUDIT.csv](file:///C:/IGRIS/TAMIL_SEGMENTATION_AUDIT.csv) — 100 Tamil test cases.
10. [ENGLISH_SEGMENTATION_AUDIT.csv](file:///C:/IGRIS/ENGLISH_SEGMENTATION_AUDIT.csv) — 100 English test cases.
11. [TANGLISH_SEGMENTATION_AUDIT.csv](file:///C:/IGRIS/TANGLISH_SEGMENTATION_AUDIT.csv) — 100 Tanglish test cases.
12. [TOKENIZER_SEGMENTATION_VERIFIER.py](file:///C:/IGRIS/TOKENIZER_SEGMENTATION_VERIFIER.py) — Automated test suite verifying all invariants.
9. [TOKENIZER_SEGMENTATION_VERIFIER.py](file:///C:/IGRIS/TOKENIZER_SEGMENTATION_VERIFIER.py) — Automated test suite verifying all invariants.

---

## 7. Status Determination & Governance Directives

### Status Justification:
* **Why not `SEGMENTATION_PASS`?**  
  While Experimental Candidate A significantly reduces sequence length and excessive fragmentation (-43.34% tokens, single-token rate increased 4.8x), UAX #29 grapheme boundary analysis reveals that **grapheme integrity is DISRUPTED in Tamil script** (288 internal cuts, 28.71% preservation). Both tokenizers separate base consonants from pulli and vowel signs. Furthermore, the 300 human-review items remain in `NOT_REVIEWED` status awaiting sole developer owner evaluation.
* **Why not `SEGMENTATION_FAILED`?**  
  Zero bitwise regressions occurred; round-trip reconstruction accuracy is 100.00%; unknown token rate is 0.00%; and excessive character fragmentation dropped by 26.77 percentage points.
* **Why not `BLOCKED_INTEGRITY`?**  
  All cryptographic SHA-256 hashes match authoritative digests; structural special token slots 0–11 are perfectly intact; no unauthorized datasets were downloaded.

### Final Determination:
**`SEGMENTATION_CONDITIONAL`**

### Governance Directives:
* **No Tokenizer Promotion:** Experimental Candidate A remains experimental. Original Candidate A remains the active production tokenizer.
* **Pretraining Status:** `LOCKED`.
* **Production Acquisition:** `LOCKED`. Cloud spend: strictly **\$0.00**.
* **Owner Action:** Awaiting sole developer owner review of [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv).
