# IGRIS Tokenizer Final Evidence-Reconciliation Report

**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Governing Invariant:** Pretraining and Acquisition Gates are `LOCKED` ($0.00 cloud spend). Candidate A remains selected; Exp Candidate A remains quarantined.  
**Language Scope:** Strictly Tamil, English, and Tanglish.

---

## 1. Conclusive Resolution of `complex-ஆ`

The expression `complex-ஆ` (Latin adjective `complex` + hyphen `-` + Tamil independent vowel clitic `ஆ`) previously received conflicting classifications (`PRESERVED` vs `DISRUPTED`) across audit CSVs and summary tables. This section provides the definitive structural and byte-level reconciliation.

### A. Exact Input Representation
- **Original Unicode String:** `complex-ஆ`
- **Unicode Codepoints:** `U+0063 U+006F U+006D U+0070 U+006C U+0065 U+0078 U+002D U+0B86` (9 codepoints)
- **Raw UTF-8 Bytes (Hex):** `63 6F 6D 70 6C 65 78 2D E0 AE 86` (11 bytes)
- **UAX #29 Grapheme Clusters:**
  1. `c` (char span: `[0..1]`, byte span: `[0..1]`)
  2. `o` (char span: `[1..2]`, byte span: `[1..2]`)
  3. `m` (char span: `[2..3]`, byte span: `[2..3]`)
  4. `p` (char span: `[3..4]`, byte span: `[3..4]`)
  5. `l` (char span: `[4..5]`, byte span: `[4..5]`)
  6. `e` (char span: `[5..6]`, byte span: `[5..6]`)
  7. `x` (char span: `[6..7]`, byte span: `[6..7]`)
  8. `-` (char span: `[7..8]`, byte span: `[7..8]`)
  9. `ஆ` (char span: `[8..9]`, byte span: `[8..11]`)
  *Total Grapheme Clusters: 9.*

### B. Detailed Side-by-Side Tokenization Trace

| Tokenizer | Token Index | Token ID | Token String | Token Bytes (Hex) | Char Span | Cumulative Byte Span | Splits Grapheme in Char Space? | Splits Grapheme in Byte Space? |
|:---|:---:|:---:|:---|:---|:---:|:---:|:---:|:---:|
| **Candidate A** | T0 | 78 | `'c'` | `63` | `[0..1]` | `[0..1]` | False | False |
| | T1 | 90 | `'o'` | `6F` | `[1..2]` | `[1..2]` | False | False |
| | T2 | 88 | `'m'` | `6D` | `[2..3]` | `[2..3]` | False | False |
| | T3 | 91 | `'p'` | `70` | `[3..4]` | `[3..4]` | False | False |
| | T4 | 87 | `'l'` | `6C` | `[4..5]` | `[4..5]` | False | False |
| | T5 | 300 | `'ex'` | `65 78` | `[5..7]` | `[5..7]` | False | False |
| | T6 | 24 | `'-'` | `2D` | `[7..8]` | `[7..8]` | False | False |
| | T7 | 268 | `'à®'` | `E0 AE` | `[8..9]` | `[8..10]` | False | **TRUE (Cut at byte 10 inside 'ஆ')** |
| | T8 | 240 | `'Ĩ'` | `86` | `[8..9]` | `[10..11]` | False | End of string |
| **Exp Candidate A** | T0 | 472 | `'com'` | `63 6F 6D` | `[0..3]` | `[0..3]` | False | False |
| | T1 | 571 | `'ple'` | `70 6C 65` | `[3..6]` | `[3..6]` | False | False |
| | T2 | 99 | `'x'` | `78` | `[6..7]` | `[6..7]` | False | False |
| | T3 | 24 | `'-'` | `2D` | `[7..8]` | `[7..8]` | False | False |
| | T4 | 766 | `'à®Ĩ'` | `E0 AE 86` | `[8..9]` | `[8..11]` | False | False |

### C. Reconciliation of Past Contradictions
1. **Why previous scripts reported `PRESERVED`:**  
   Audits evaluating character offsets (`c_s < cut < c_e`) found that both tokens `à®` and `Ĩ` mapped to character offset `(8, 9)`. Because no integer cut exists strictly between 8 and 9, the character-level algorithm recorded `cuts_inside = 0` and marked `PRESERVED`.
2. **Why summary tables reported `DISRUPTED`:**  
   Audits inspecting byte completeness noted that `à®` (`0xE0 0xAE`) is an incomplete byte prefix that fails isolated UTF-8 decoding, thus labeling the token boundary inside `ஆ` as `DISRUPTED`.
3. **Conclusive Finding:**  
   - In **Original Candidate A**, character grapheme boundaries are preserved, but the byte sequence of `ஆ` is severed at byte offset 10 (`0xE0 0xAE | 0x86`).
   - In **Experimental Candidate A**, `ஆ` is preserved intact as a single 3-byte token `à®Ĩ` (`0xE0 0xAE 0x86`) across both character and byte dimensions.

---

## 2. Comprehensive 300-Item Grapheme Audit Reconciliation

All 300 records in [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv) were re-evaluated directly from tokenizer encodings, byte streams, and UAX #29 regex `\X` clusters. The detailed record-level data is published in [TOKENIZER_GRAPHEME_RECONCILIATION_300.csv](file:///C:/IGRIS/TOKENIZER_GRAPHEME_RECONCILIATION_300.csv).

### A. Master Reconciled Summary Table

| Evaluation Dimension | Total Records | Total Graphemes | Cand A Internal Cuts | Cand A Cuts Inside Graphemes | Cand A Cuts Between Graphemes | Cand A Byte Cuts Inside Graphemes | Exp A Internal Cuts | Exp A Cuts Inside Graphemes | Exp A Cuts Between Graphemes | Exp A Byte Cuts Inside Graphemes |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **TOTAL CORPUS** | **300** | **2,990** | **3,129** | **598** | **2,531** | **735** | **1,643** | **423** | **1,220** | **429** |
| **Language: TAMIL** | 100 | 404 | 798 | 407 | 391 | 497 | 532 | 289 | 243 | 293 |
| **Language: ENGLISH** | 100 | 1,180 | 963 | 0 | 963 | 0 | 471 | 0 | 471 | 0 |
| **Language: TANGLISH** | 100 | 1,406 | 1,368 | 191 | 1,177 | 238 | 640 | 134 | 506 | 136 |
| **Script: TAMIL SCRIPT** | 110 | 456 | 916 | 465 | 451 | 573 | 609 | 328 | 281 | 334 |
| **Script: LATIN SCRIPT** | 142 | 1,808 | 1,449 | 0 | 1,449 | 0 | 639 | 0 | 639 | 0 |
| **Script: MIXED SCRIPT** | 43 | 682 | 725 | 133 | 592 | 162 | 358 | 95 | 263 | 95 |
| **Script: NUMERIC/PUNCT**| 5 | 44 | 39 | 0 | 39 | 0 | 37 | 0 | 37 | 0 |

### B. Explanation of the Previously Reported "422 Cuts"
The previous report stated: *"Both Candidate A and Experimental Candidate A produce 422 internal cuts within multi-codepoint grapheme clusters across the 300 examples."*

**Forensic Explanation of Error:**
1. **Candidate A does NOT have 422 cuts:** Candidate A actually has **598** character-level internal cuts (and 735 byte-level internal cuts). The previous report erroneously assigned the exact same number (422) to both tokenizers, completely ignoring that Candidate A has 175 more character-level internal cuts than Exp Candidate A due to its severe lack of subword merges.
2. **Experimental Candidate A has 423 cuts, not 422:** The previous report undercounted by 1 cut (422 instead of the true 423 character-level cuts).
3. **Root Cause:** A placeholder value of `422` was copy-pasted across both columns in `TOKENIZER_FRAGMENTATION_ANALYSIS.csv` and propagated into `TOKENIZER_LINGUISTIC_SEGMENTATION_REPORT.md` without independent recomputation.
4. **Correct Reconciled Values:**
   - Candidate A cuts inside graphemes: **598** (char) / **735** (byte).
   - Experimental Candidate A cuts inside graphemes: **423** (char) / **429** (byte).
   - Character cuts between graphemes: **2,531** (Cand A) vs **1,220** (Exp A).

---

## 3. Conservative Morphological Reclassification of English Cases

The 15 English overmerging examples in [TOKENIZER_MORPHOLOGY_REVIEW_V2.csv](file:///C:/IGRIS/TOKENIZER_MORPHOLOGY_REVIEW_V2.csv) have been audited against strictly defined morphological categories:

```
+───────────────────────────────────────────────────────────────────────────────────────────────+
|                               CONSERVATIVE MORPHOLOGY CLASSIFICATIONS                         |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
| Category                      | Definition                                                    |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
| CLEAR_MORPHEME_BOUNDARY       | Token boundary strictly isolates an authentic prefix/suffix/stem|
| CROSSES_MORPHEME_BOUNDARY     | Subword spans across a known compound or derivational boundary|
| POTENTIAL_OVERMERGE           | Merge combines base coda with suffix, creating homograph risk |
| LINGUISTICALLY_AMBIGUOUS      | Monomorphemic root split sub-syllabically; no active boundary |
| NOT_ASSESSED                  | Case not evaluated under morphological criteria               |
+───────────────────────────────+───────────────────────────────────────────────────────────────+
```

### Audited Case Results:

| Audit ID | Word | Exp A Tokens | Classification | Violating Token | Conservative Linguistic Rationale |
|:---|:---|:---|:---:|:---:|:---|
| **OVM-REV-01** | `microservice` | `m \| icroser \| vice` | **`CROSSES_MORPHEME_BOUNDARY`** | `icroser` | Compound boundary between prefix `micro-` and base `service` is severed; `icroser` spans both constituents. |
| **OVM-REV-02** | `microservices` | `m \| icroser \| vices` | **`CROSSES_MORPHEME_BOUNDARY`** | `icroser` | Overmerge recurs across inflected plural, crossing prefix-root boundary. |
| **OVM-REV-03** | `service` | `ser \| vice` | **`LINGUISTICALLY_AMBIGUOUS`** | `NONE` | Synchronically monomorphemic root; division is sub-lexical rather than morphological. |
| **OVM-REV-04** | `services` | `ser \| vices` | **`POTENTIAL_OVERMERGE`** | `vices` | Combines base coda with plural suffix `-s`, forming an orthographic homograph with the noun `vices`. |
| **OVM-REV-05** | `asynchronous` | `as \| ynchronous` | **`CROSSES_MORPHEME_BOUNDARY`** | `as` | Merges privative prefix `a-` with root onset `s-`, obscuring the negation morpheme. |
| **OVM-REV-06** | `synchronous` | `s \| ynchronous` | **`LINGUISTICALLY_AMBIGUOUS`** | `NONE` | Splitting initial onset `s` from `ynchronous` does not isolate Greek prefix `syn-`. |
| **OVM-REV-07** | `middleware` | `m \| id \| d \| le \| ware` | **`CLEAR_MORPHEME_BOUNDARY`** | `NONE` | Compound boundary between `middle` and `ware` is strictly preserved; suffix `ware` is an intact token. |
| **OVM-REV-08** | `middle` | `m \| id \| d \| le` | **`LINGUISTICALLY_AMBIGUOUS`** | `NONE` | Monomorphemic root; sub-syllabic fragmentation without morphological division. |
| **OVM-REV-09** | `ware` | `ware` | **`CLEAR_MORPHEME_BOUNDARY`** | `NONE` | Lexical root and productive compounding morpheme preserved as intact single token. |
| **OVM-REV-10** | `internationalization` | `in \| tern \| ational \| ization` | **`POTENTIAL_OVERMERGE`** | `tern` | Suffixes `-ational` and `-ization` align well, but `tern` straddles prefix `inter-` and stem `nation`. |
| **OVM-REV-11** | `international` | `in \| tern \| ational` | **`POTENTIAL_OVERMERGE`** | `tern` | Subword `tern` spans across boundary between `inter-` and `nation`. |
| **OVM-REV-12** | `unavoidable` | `un \| av \| o \| id \| able` | **`CLEAR_MORPHEME_BOUNDARY`** | `NONE` | Prefix `un-` and suffix `-able` strictly preserved as independent morpheme tokens. |
| **OVM-REV-13** | `avoidable` | `av \| o \| id \| able` | **`CLEAR_MORPHEME_BOUNDARY`** | `NONE` | Suffix `-able` cleanly isolated as an atomic morpheme token. |
| **OVM-REV-14** | `avoid` | `av \| o \| id` | **`LINGUISTICALLY_AMBIGUOUS`** | `NONE` | Monomorphemic root; arbitrary character fragmentation. |
| **OVM-REV-15** | `multiprocessing` | `multi \| pro \| ces \| sing` | **`CLEAR_MORPHEME_BOUNDARY`** | `NONE` | Productive prefix `multi-` preserved as an exact atomic token. |

---

## 4. Preservation of Owner-Review Governance

In strict adherence to the `SOLO_DEVELOPER_OWNER_REVIEW` operating model:
- All **30 records** in [TOKENIZER_OWNER_REVIEW_30.csv](file:///C:/IGRIS/TOKENIZER_OWNER_REVIEW_30.csv) remain strictly **`NOT_REVIEWED`** with empty rationales (`""`).
- All **300 records** in [TOKENIZER_HUMAN_REVIEW_SAMPLE.csv](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv) remain strictly **`NOT_REVIEWED`** with empty rationales (`""`).
- Zero decisions have been fabricated, simulated, or pre-approved.

---

## 5. Automated Verification Summary

The complete test suite in `verify_final_reconciliation.py` passed all assertions:
1. **Cryptographic Hashes:**
   - Candidate A: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
   - Exp Candidate A: `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce`
   - Candidate B: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
2. **Structural Tokens:** Pinned IDs 0–11 intact in both tokenizers.
3. **300-Item Reconciliation Totals:** 300 records, 2,990 graphemes, 598 Cand A cuts inside, 423 Exp A cuts inside.
4. **`complex-ஆ` Integrity:** Character cut = 0; byte cut at 10 verified for Candidate A; Exp A verified 0 cuts in both.
5. **Morphology Classifications:** All 15 rows mapped to conservative categories.
6. **Governance Invariants:** Pretraining and data acquisition gates verified **`LOCKED`** (\$0.00 cloud spend).
