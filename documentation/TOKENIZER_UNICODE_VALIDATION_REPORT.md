# IGRIS Tokenizer Unicode & Adversarial Validation Report
## Forensic Testing of NFC Normalization, Complex Script Conjuncts, and Delimiter Isolation

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Test Suite Status:** **ALL 10 ADVERSARIAL SUITES PASSING (100% REVERSIBLE)**  

---

## 1. Adversarial Unicode Test Results Summary

Both tokenizers were subjected to an identical 10-point adversarial test battery exercising Tamil Unicode grapheme clusters, zero-width characters, combining signs, traditional fractions, and code-mixed boundary cases:

| Suite ID | Test Description | Input Preview | Orig A Tokens | Exp A Tokens | Round-Trip A | Round-Trip Exp | Length Reduction |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| `TC-UNI-01` | **NFC Pulli & Virama Conjuncts** | `'தமிழ்நாடு மென்பொருள் துறை'` | 28 | 22 | **PASS** | **PASS** | -21.4% |
| `TC-UNI-02` | **Grantha Ligatures (ksha, shri)** | `'க்ஷ, ஸ்ரீ, ஶ்ரீ, க்‍க, க்‌க'` | 34 | 24 | **PASS** | **PASS** | -29.4% |
| `TC-UNI-03` | **Zero-Width Joiner (ZWJ)** | `'க்‍க'` | 6 | 4 | **PASS** | **PASS** | -33.3% |
| `TC-UNI-04` | **Zero-Width Non-Joiner (ZWNJ)** | `'க்‌க'` | 6 | 3 | **PASS** | **PASS** | -50.0% |
| `TC-UNI-05` | **Tamil Vowel Signs (Matras)** | `'கி, கீ, கு, கூ, கெ, கே, கை, கொ, கோ, கௌ'` | 44 | 27 | **PASS** | **PASS** | -38.6% |
| `TC-UNI-06` | **Tamil Numerals & Fractions** | `'௧௨௩௪௫௬௭௮௯௰ ௱ ௲ ௳ ௴ ௵'` | 35 | 30 | **PASS** | **PASS** | -14.3% |
| `TC-UNI-07` | **Colloquial Romanized Tamil** | `'Innaiku nalla mazhai peyudhu pa, seekiram vaanga'` | 45 | 14 | **PASS** | **PASS** | -68.9% |
| `TC-UNI-08` | **Natural Tech Code-Switching** | `'Server restart aana udane API response latency...'` | 55 | 16 | **PASS** | **PASS** | -70.9% |
| `TC-UNI-09` | **Malformed Lone Combining Signs** | `'ா௲்'` (combining signs without base) | 4 | 4 | **PASS** | **PASS** | 0.0% |
| `TC-UNI-10` | **Structural Special Tokens** | `'<|user|> What is IGRIS? <|assistant|> <think>...'` | 28 | 23 | **PASS** | **PASS** | -17.9% |

---

## 2. Analysis of Critical Linguistic Cases

1. **Pulli Virama Reversibility:**
   - Tamil consonants with pulli (e.g. `க்`, `த்`, `ள்`) are represented in Unicode as base consonant (`U+0B95`) + virama (`U+0BCD`). Both tokenizers preserve the exact sequence without decomposing or merging with adjacent characters across word boundaries.
2. **Zero-Width Characters (`ZWJ` U+200D and `ZWNJ` U+200C):**
   - Experimental Candidate A compresses the ZWNJ sequence `'க்‌க'` from 6 bytes/tokens down to 3 tokens while maintaining 100% NFC-normalized byte reconstruction.
3. **Romanized Tamil & Code-Switching Compression:**
   - The greatest compression gains occur in Romanized Tamil (`TC-UNI-07`, **68.9% reduction**) and Tanglish technical discourse (`TC-UNI-08`, **70.9% reduction**), demonstrating that Experimental Candidate A learned frequent English/Tanglish character n-grams and subword roots.
4. **Malformed Combining Character Robustness:**
   - Feeding isolated combining vowel signs (`ா௲்`) without a base consonant does not crash either tokenizer; both handle lone combining codepoints gracefully through byte fallback.
5. **Structural Delimiter Isolation:**
   - Structural special tokens (`<|user|>`, `<|assistant|>`, `<think>`, `</think>`) are parsed as single atomic units with IDs `10`, `11`, `3`, and `4`, and are restored perfectly during detokenization with `skip_special_tokens=False`.

---

## 3. Confirmation of Zero Split Leakage

Forensic check: Zero validation records (`VAL_SPLIT`) or test records (`TEST_SPLIT`) were present in the training inputs used to build Experimental Candidate A. Merges were derived exclusively from the 320 `TRAIN_SPLIT` records.
