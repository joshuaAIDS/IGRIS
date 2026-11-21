# IGRIS Tokenizer Byte-Level Decoding & Unicode Grapheme Audit
## Technical and Linguistic Investigation of ByteLevel BPE Representations and Akshara Boundaries

**Document Identifier:** `IGRIS-AUDIT-BYTELEVEL-DECODING-V1`  
**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-21  
**Audit Scope:** Original Candidate A (`ac7e18b1...`) vs. Experimental Candidate A (`3393acbe...`)  
**Status:** **AUDIT VERIFIED & EVIDENCE CORRECTED**

---

## 1. Executive Summary

This forensic audit investigates the byte-level token representation, decoding bijection, and Unicode grapheme integrity of **Original Candidate A** (the locked production tokenizer) and **Experimental Candidate A** (the synthetic-experiment tokenizer).

### Key Conclusions:
1. **Root Cause of Mojibake:** Raw tokenizer vocabulary strings like `à®²` and `à¯į` are ByteLevel BPE Latin-1 character representations of raw UTF-8 byte sequences (`0xE0 0xAE 0xB2` and `0xE0 0xAF 0x8D`), not readable Tamil. Presenting them as human-readable Tamil tokens was a visualization defect.
2. **Incomplete Byte Fragments:** In Candidate A, vocabulary merges often split multi-byte UTF-8 sequences into partial prefixes (e.g. `à®` = `0xE0 0xAE`). These tokens cannot decode to valid UTF-8 in isolation and must be formally represented as explicit hex byte sequences `<0xE0><0xAE>`.
3. **100.00% Round-Trip Reconstruction:** Concatenating the raw byte arrays of all tokens in an utterance and decoding the concatenated stream produces a 100.00% bitwise exact match to the original text across all 300 test items in both tokenizers.
4. **Disambiguation of Round-Trip Fidelity vs. Grapheme Integrity:**
   - **Bitwise Round-Trip Fidelity:** 100.00% (No bytes are lost).
   - **Unicode Grapheme Boundary Preservation:** **DISRUPTED** in both tokenizers. Neither tokenizer has learned BPE merges that join base consonants with pulli (`்`) or vowel signs (e.g. `ி`, `ு`). Both tokenizers segment `ல்` into `ல` (U+0BB2) and `்` (U+0BCD), cutting *inside* the UAX #29 grapheme cluster.
5. **Compression vs. Linguistic Quality:** Experimental Candidate A achieves a 43.34% reduction in sequence length and reduces excessive word fragmentation from 70.71% to 43.94%. However, this compression is driven by statistical character and byte n-gram frequencies, not by morphosyntactic awareness. Many subword splits remain linguistically `UNCERTAIN`.

---

## 2. ByteLevel BPE Bijection Mathematics

The Hugging Face / GPT-2 `ByteLevel` pre-tokenizer implements an invertible bijection between the 256 possible byte values ($0x00 \dots 0xFF$) and a subset of Unicode codepoints:

### 2.1 The 256-Byte Mapping Definition
Let $B = \{0, 1, \dots, 255\}$ be the set of byte values. The mapping function $f: B \to \mathbb{U}$ maps bytes to Unicode characters:
1. **Printable ASCII and Latin-1:**
   - $0x21 \le b \le 0x7E$ (33 to 126: `!` to `~`): mapped directly to $b$.
   - $0xA1 \le b \le 0xAC$ (161 to 172: `¡` to `¬`): mapped directly to $b$.
   - $0xAE \le b \le 0xFF$ (174 to 255: `®` to `ÿ`): mapped directly to $b$.
   These 188 bytes are preserved identically in Latin-1 representation.
2. **Non-Printable, Control, and Whitespace Bytes:**
   The remaining 68 bytes (including $0x00 \dots 0x20$, $0x7F \dots 0xA0$, and $0xAD$) are shifted into codepoint space starting at $U+0100$ ($256 + n$).
   - Space ($0x20$ = 32): mapped to $U+0120$ (`Ġ`).
   - Newline ($0x0A$ = 10): mapped to $U+010A$ (`Ċ`).

### 2.2 Reversible Inversion Algorithm
Given a raw token string $S = c_1 c_2 \dots c_k$, each character is mapped back to its exact byte via the inverse dictionary $f^{-1}(c)$:
$$\text{bytes}(S) = \big[ f^{-1}(c_1), f^{-1}(c_2), \dots, f^{-1}(c_k) \big]$$

When a single token represents a complete valid UTF-8 sequence, it decodes directly:
$$\text{Decoded}(S) = \text{UTF8Decode}(\text{bytes}(S))$$
When a token represents an incomplete byte sequence (e.g. `à®` = `0xE0 0xAE`), `UTF8Decode` raises a `UnicodeDecodeError`. In such cases, the token's isolated contribution is rendered as:
$$\text{Decoded}(S) = \langle 0x\text{HEX}_1 \rangle \langle 0x\text{HEX}_2 \rangle \dots$$

---

## 3. Mandatory Linguistic Expressions Evaluation

Six mandatory test cases were re-evaluated side-by-side using exact token IDs, raw strings, byte-level decoded contributions, reconstructed text, and UAX #29 grapheme cluster analysis.

### Summary Comparison Table

| Expression | Total Graphemes | Cand A Tokens | Cand Exp Tokens | Cand A Grapheme Status | Cand Exp Grapheme Status | Cand A Morph Status | Cand Exp Morph Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`server-ல்`** | 8 | 7 | 5 | DISRUPTED | DISRUPTED | DISRUPTED | UNCERTAIN |
| **`complex-ஆ`** | 9 | 9 | 5 | DISRUPTED | PRESERVED | DISRUPTED | UNCERTAIN |
| **`deploy பண்ணினோம்`** | 12 | 18 | 11 | DISRUPTED | DISRUPTED | DISRUPTED | UNCERTAIN |
| **`memory allocation`** | 17 | 15 | 3 | PRESERVED | PRESERVED | DISRUPTED | PRESERVED |
| **`pannirukkom`** | 11 | 10 | 6 | PRESERVED | PRESERVED | DISRUPTED | UNCERTAIN |
| **`testing-க்கு`** | 10 | 10 | 8 | DISRUPTED | DISRUPTED | DISRUPTED | UNCERTAIN |

---

### Detailed Expression Breakdown

#### 1. `server-ல்` (Latin Stem + Hyphen + Tamil Locative Case Suffix)
* **Grapheme Clusters (8):** `s`, `e`, `r`, `v`, `e`, `r`, `-`, `ல்` (`\X` binds U+0BB2 and U+0BCD).
* **Original Candidate A:**
  - Token IDs: `[94, 284, 97, 284, 24, 294, 271]`
  - Raw BPE: `s | er | v | er | - | à®² | à¯į`
  - Decoded: `s | er | v | er | - | ல | ்`
  - Reconstructed: `server-ல்` (Match: 100%)
  - Grapheme Cuts: **1 cut inside `ல்`** (`ல` | `்`). Status: **DISRUPTED**.
  - Morphological Assessment: **DISRUPTED**. Root `server` fragmented into 4 pieces; suffix `ல்` cut at pulli.
* **Experimental Candidate A:**
  - Token IDs: `[643, 453, 24, 288, 270]`
  - Raw BPE: `ser | ver | - | à®² | à¯į`
  - Decoded: `ser | ver | - | ல | ்`
  - Reconstructed: `server-ல்` (Match: 100%)
  - Grapheme Cuts: **1 cut inside `ல்`** (`ல` | `்`). Status: **DISRUPTED**.
  - Morphological Assessment: **UNCERTAIN**. Syllables `ser` + `ver` are cleaner, and the hyphen isolates the stem from the suffix, but the suffix `ல்` remains detached from its pulli.

#### 2. `complex-ஆ` (Latin Adjective + Hyphen + Tamil Adverbial Suffix)
* **Grapheme Clusters (9):** `c`, `o`, `m`, `p`, `l`, `e`, `x`, `-`, `ஆ` (U+0B86).
* **Original Candidate A:**
  - Token IDs: `[78, 90, 88, 91, 87, 300, 24, 268, 240]`
  - Raw BPE: `c | o | m | p | l | ex | - | à® | Ĩ`
  - Decoded: `c | o | m | p | l | ex | - | <0xE0><0xAE> | <0x86>`
  - Reconstructed: `complex-ஆ` (Match: 100%)
  - Grapheme Cuts: **1 cut inside `ஆ`** (byte-level shredding: `<0xE0><0xAE>` + `<0x86>`). Status: **DISRUPTED**.
  - Unique Affected Clusters: 1 (`ஆ`). Preservation Rate: 88.89%.
  - Morphological Assessment: **DISRUPTED**. Extreme Latin character fragmentation and byte-level vowel shredding.
* **Experimental Candidate A:**
  - Token IDs: `[472, 571, 99, 24, 766]`
  - Raw BPE: `com | ple | x | - | à®Ĩ`
  - Decoded: `com | ple | x | - | ஆ`
  - Reconstructed: `complex-ஆ` (Match: 100%)
  - Grapheme Cuts: **0 cuts**. Status: **PRESERVED**. `ஆ` is atomic (Token 766).
  - Unique Affected Clusters: 0. Preservation Rate: 100.00%.
  - Morphological Assessment: **UNCERTAIN**. Latin stem split into syllables `com` + `ple` + `x`; suffix `ஆ` is cleanly recognized as an atomic token.

#### 3. `deploy பண்ணினோம்` (Code-Switched Technical Verb + Auxiliary)
* **Grapheme Clusters (12):** `d`, `e`, `p`, `l`, `o`, `y`, ` `, `ப`, `ண்`, `ணி`, `னோ`, `ம்`.
* **Original Candidate A:**
  - Token IDs: `[79, 80, 91, 302, 100, 273, 115, 268, 108, 271, 268, 108, 272, 285, 270, 245, 278, 271]`
  - Raw BPE: `d | e | p | lo | y | Ġà® | ª | à® | £ | à¯į | à® | £ | à®¿ | à®© | à¯ | ĭ | à®® | à¯į`
  - Decoded: `d | e | p | lo | y | <0x20><0xE0><0xAE> | <0xAA> | <0xE0><0xAE> | <0xA3> | ் | <0xE0><0xAE> | <0xA3> | ி | ன | <0xE0><0xAF> | <0x8B> | ம | ்`
  - Reconstructed: `deploy பண்ணினோம்` (Match: 100%)
  - Grapheme Cuts: **4 cuts** (`ண்`, `ணி`, `னோ`, `ம்`). Status: **DISRUPTED**.
  - Morphological Assessment: **DISRUPTED**. Pathological byte decomposition.
* **Experimental Candidate A:**
  - Token IDs: `[79, 80, 628, 336, 270, 294, 274, 279, 356, 282, 270]`
  - Raw BPE: `d | e | ploy | Ġà®ªà®£ | à¯į | à®£ | à®¿ | à®© | à¯ĭ | à®® | à¯į`
  - Decoded: `d | e | ploy |  பண | ் | ண | ி | ன | ோ | ம | ்`
  - Reconstructed: `deploy பண்ணினோம்` (Match: 100%)
  - Grapheme Cuts: **4 cuts** (`ண்`, `ணி`, `னோ`, `ம்`). Status: **DISRUPTED**.
  - Morphological Assessment: **UNCERTAIN**. Fuses `ploy` and ` பண`, but decomposes verb-final morphology into individual characters and diacritics.

#### 4. `memory allocation` (Technical English Compound)
* **Grapheme Clusters (17):** `m`, `e`, `m`, `o`, `r`, `y`, ` `, `a`, `l`, `l`, `o`, `c`, `a`, `t`, `i`, `o`, `n`.
* **Original Candidate A:**
  - Token IDs: `[88, 80, 88, 90, 93, 100, 232, 297, 302, 78, 76, 95, 84, 90, 89]`
  - Raw BPE: `m | e | m | o | r | y | Ġ | al | lo | c | a | t | i | o | n`
  - Decoded: `m | e | m | o | r | y |   | al | lo | c | a | t | i | o | n`
  - Reconstructed: `memory allocation` (Match: 100%)
  - Grapheme Cuts: 0 cuts.
  - Morphological Assessment: **DISRUPTED**. Decomposed into 15 individual letter tokens.
* **Experimental Candidate A:**
  - Token IDs: `[1463, 1330, 331]`
  - Raw BPE: `memory | Ġalloc | ation`
  - Decoded: `memory |  alloc | ation`
  - Reconstructed: `memory allocation` (Match: 100%)
  - Grapheme Cuts: 0 cuts.
  - Morphological Assessment: **PRESERVED**. Perfectly segmented into genuine morphemes: `memory` + root `alloc` + suffix `ation`.

#### 5. `pannirukkom` (Colloquial Romanized Tamil Inflected Verb)
* **Grapheme Clusters (11):** `p`, `a`, `n`, `n`, `i`, `r`, `u`, `k`, `k`, `o`, `m`.
* **Original Candidate A:**
  - Token IDs: `[91, 280, 89, 84, 93, 96, 86, 86, 90, 88]`
  - Raw BPE: `p | an | n | i | r | u | k | k | o | m`
  - Decoded: `p | an | n | i | r | u | k | k | o | m`
  - Reconstructed: `pannirukkom` (Match: 100%)
  - Grapheme Cuts: 0 cuts.
  - Morphological Assessment: **DISRUPTED**.
* **Experimental Candidate A:**
  - Token IDs: `[91, 388, 424, 86, 86, 334]`
  - Raw BPE: `p | ann | iru | k | k | om`
  - Decoded: `p | ann | iru | k | k | om`
  - Reconstructed: `pannirukkom` (Match: 100%)
  - Grapheme Cuts: 0 cuts.
  - Morphological Assessment: **UNCERTAIN**. Subwords `ann`, `iru`, `om` are clean phonetic units, but geminate `k`+`k` is split.

#### 6. `testing-க்கு` (Latin Noun + Hyphen + Tamil Dative Case Suffix)
* **Grapheme Clusters (10):** `t`, `e`, `s`, `t`, `i`, `n`, `g`, `-`, `க்`, `கு`.
* **Original Candidate A:**
  - Token IDs: `[95, 281, 95, 301, 82, 24, 277, 271, 277, 288]`
  - Raw BPE: `t | es | t | in | g | - | à®ķ | à¯į | à®ķ | à¯ģ`
  - Decoded: `t | es | t | in | g | - | க | ் | க | ு`
  - Reconstructed: `testing-க்கு` (Match: 100%)
  - Grapheme Cuts: **2 cuts** (`க்` and `கு`). Status: **DISRUPTED**.
  - Morphological Assessment: **DISRUPTED**.
* **Experimental Candidate A:**
  - Token IDs: `[95, 398, 307, 24, 272, 270, 272, 273]`
  - Raw BPE: `t | est | ing | - | à®ķ | à¯į | à®ķ | à¯ģ`
  - Decoded: `t | est | ing | - | க | ் | க | ு`
  - Reconstructed: `testing-க்கு` (Match: 100%)
  - Grapheme Cuts: **2 cuts** (`க்` and `கு`). Status: **DISRUPTED**.
  - Morphological Assessment: **UNCERTAIN**. English stem is cleanly partitioned into morphemes `t` + `est` + `ing`, and the hyphen cleanly separates the stem from the suffix. However, the Tamil suffix `-க்கு` is split across 4 individual tokens.

---

## 4. Overall 300-Item Forensic Audit Results

Across all 300 curated audit examples (100 Tamil, 100 English, 100 Tanglish):

| Metric | Original Candidate A | Experimental Candidate A | Reconciliation Note |
|---|:---:|:---:|---|
| **Round-Trip Bitwise Accuracy** | **100.00%** (300/300) | **100.00%** (300/300) | Zero bitwise byte loss or corruption. |
| **Total Extended Grapheme Clusters** | 2,990 | 2,990 | Determined via Unicode UAX #29 `regex \X`. |
| **Internal Grapheme Cuts** | 492 | 428 | Includes byte-level and character-level slices. |
| **Unique Affected Clusters** | 492 | 428 | Measured independently for each tokenizer. |
| **Grapheme Preservation Rate** | **83.55%** | **85.69%** | Formula: $100 \times (\text{total} - \text{affected}) / \text{total}$. |
| **Tamil Grapheme Preservation Rate** | **17.33%** (70/404) | **27.72%** (112/404) | Disrupted by detached pulli and vowel signs. |
| **English Grapheme Preservation Rate** | **100.00%** (1,180/1,180) | **100.00%** (1,180/1,180) | 0 grapheme cuts in English vocabulary. |
| **Tanglish Grapheme Preservation Rate** | **88.76%** (1,248/1,406) | **90.33%** (1,270/1,406) | Cuts occur strictly in Tamil-script suffixes. |
| **Total Words ($N_{\text{words}}$)** | 437 | 437 | Exact whitespace-delimited word denominator. |
| **Total Characters ($N_{\text{chars}}$)** | 3,412 | 3,412 | Exact input character count. |
| **Tokens per Word (Fertility)** | 7.8467 | 4.4462 | **-43.34%** sequence length reduction. |
| **Excessive Fragmentation ($\ge 5$)** | 70.71% | 43.94% | Reduced by 26.77 percentage points. |
| **Single-Token Word Rate** | 1.14% | 5.49% | Increased 4.8x. |
| **Human Review Sample Status** | `NOT_REVIEWED` (300/300) | `NOT_REVIEWED` (300/300) | Decisions and rationales strictly blank. |

---

## 5. Architectural Recommendations

1. **Retain Candidate A as Production Tokenizer:** In accordance with project governance, Original Candidate A (`ac7e18b1...`) remains the active production tokenizer for architecture initialization.
2. **Tamil Grapheme Merge Tuning:** During future vocabulary scaling on real web-scale corpora, BPE merge rules must be constrained or initialized with atomic Tamil akshara (consonant + pulli, consonant + vowel signs) to eliminate the 422 internal grapheme cuts.
3. **Owner Review Sign-Off:** The 300 curated examples in `TOKENIZER_HUMAN_REVIEW_SAMPLE.csv` are formatted with complete decoded Unicode contributions and grapheme diagnostics, ready for independent human review.
