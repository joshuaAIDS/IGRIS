# IGRIS Candidate A: Synthetic Tokenizer Results & Metric Audit

**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Audit Date:** 2026-11-20  
**Architecture:** Decoder-Only Transformer (32,768 Vocabulary, ByteLevel BPE)  
**Status:** **AUDIT COMPLETE — ALL METRICS VERIFIED & RECONCILED**

---

## 1. Executive Summary

This audit thoroughly investigates the Candidate A synthetic tokenizer training experiment across five designated audit areas:
1. **Vocabulary Structure & Reachability:** Exact count of learned BPE merges, initial byte tokens, structural tokens, and inert fillers.
2. **Vocabulary Coverage Disambiguation:** Precision audit of the reported `0.41%` and `1.47%` coverage figures.
3. **Training Data Strictness:** Proof that validation and test sets were strictly held out from BPE merge training.
4. **Evaluation Recalculation:** Exact mathematical verification of token fertilities, sequence lengths, and speed benchmarks.
5. **Cryptographic Integrity:** Re-verification of all original and experimental tokenizer hashes.

---

## 2. Vocabulary Structure & Reachability Audit

Both tokenizers were decoded and mapped into full 32,768-entry inventories:

| Vocabulary Segment | Original Candidate A | Experimental Candidate A | Token IDs | Reachable in Inference? | Description |
|---|:---:|:---:|:---:|:---:|---|
| **Structural Tokens** | 12 | 12 | 0–11 | **Yes** | `<|pad|>`, `<|begin_of_text|>`, etc. Special added tokens. |
| **Initial Byte Alphabet** | 256 | 256 | 12–267 | **Yes** | 256 single-byte character tokens (GPT-2 ByteLevel mapping). |
| **Learned BPE Merges** | 63 | 1,755 | 268–330 (Orig)<br>268–2022 (Exp) | **Yes** | Subwords learned from frequency co-occurrence in training text. |
| **Inert Vocabulary Fillers** | 32,437 | 30,745 | 331–32767 (Orig)<br>2023–32767 (Exp) | **No** | `<|filler_00000|>`.. Padding slots to fulfill 32,768 requirement. |
| **Total Vocabulary** | **32,768** | **32,768** | **0–32,767** | — | **Contiguous, exactly 32,768 slots, zero duplicates.** |

### Key Vocabulary Findings:
1. **Unreachable Entries Identified:**
   - In Original Candidate A, **32,437 entries** are inert fillers (`<|filler_00000|>` to `<|filler_32436|>`).
   - In Experimental Candidate A, **30,745 entries** are inert fillers (`<|filler_00000|>` to `<|filler_30744|>`).
   - **Reason for Unreachability:** These filler tokens reside exclusively in `model.vocab` (not in `added_tokens`) and possess **zero corresponding merge rules** in `model.merges`. Consequently, the ByteLevel BPE tokenizer algorithm can **never emit** any filler token for any input byte sequence. They serve solely as fixed-width matrix alignment placeholders.
2. **Structural Token Integrity:**
   - Structural token IDs 0–11 remain strictly preserved, ordered, and identical across both artifacts.
3. **Duplicate Check:**
   - Both tokenizers possess strictly 32,768 unique values with 0 collisions.

---

## 3. Vocabulary Coverage Disambiguation Audit

The reported values of **0.41%** (Original) and **1.47%** (Experimental) have been investigated and reconciled:

### Derivation of Reported Values:
- **Test Set Unique Tokens Emitted:**
  - Original Candidate A emitted **133 distinct token IDs** across the 39 test sentences.
  - Experimental Candidate A emitted **482 distinct token IDs** across the 39 test sentences.
- **Reported Calculation (Padded Vocabulary Utilization):**
  $$\text{Reported Coverage (Original)} = \frac{133}{32,768} \times 100\% = 0.4059\% \approx 0.41\%$$
  $$\text{Reported Coverage (Experimental)} = \frac{482}{32,768} \times 100\% = 1.4709\% \approx 1.47\%$$

### Linguistic Metric Reconciliation:
The metric reported as "Vocabulary Coverage" is more accurately termed **"Padded Vocabulary Utilization on Test Set"** because the denominator includes 30,000+ unreachable filler slots.

When evaluated against the **Active (Reachable) Subword Vocabulary**:
- **Original Candidate A:**
  $$\text{Active Utilization} = \frac{133}{331} \times 100\% = \mathbf{40.18\%}$$
- **Experimental Candidate A:**
  $$\text{Active Utilization} = \frac{482}{2,023} \times 100\% = \mathbf{23.83\%}$$

When evaluated as **Corpus Character Coverage (Text UNK Rate)**:
- Both tokenizers achieve **100.00% Coverage (0.00% UNK)** due to complete byte-level fallback.

---

## 4. Training Data & Leakage Audit

1. **Training Split Isolation:**
   - Only the 320 documents of the `TRAIN` split were supplied to `build_candidate_a()`.
   - The 40 `VALIDATION` documents and 39 `TEST` documents were completely withheld during BPE merge learning.
2. **Language Category Representation:**
   - **Tanglish:** 196 documents (Train: 157, Val: 20, Test: 19)
   - **Tamil:** 111 documents (Train: 89, Val: 11, Test: 11)
   - **English:** 92 documents (Train: 74, Val: 9, Test: 9)
3. **Leakage Verification:**
   - Exact text matches between splits: **0**
   - Maximum pairwise word 3-gram Jaccard similarity across splits: **0.4054** (Strictly $< 0.70$)
   - Prefix matches ($\ge 50$ characters): **0**
4. **Synthetic Provenance:**
   - All 8 input sources trace directly to authorized synthetic generators and validators created in Phases 17–31A.

---

## 5. Evaluation Recalculation Audit

All metrics were recomputed directly from the held-out test split (39 documents):

| Language | Test Documents | Word Count | Char Count | Original Tokens | Exp Tokens | Orig Fertility (tok/w) | Exp Fertility (tok/w) | Delta |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Tamil** | 11 | 107 | 942 | 1,078 | 738 | **10.07** | **6.90** | -3.17 |
| **English** | 9 | 89 | 912 | 822 | 344 | **9.24** | **3.87** | -5.37 |
| **Tanglish** | 19 | 191 | 1,542 | 1,450 | 629 | **7.59** | **3.29** | -4.30 |
| **Total** | **39** | **387** | **3,396** | **3,350** | **1,711** | **8.66** | **4.42** | -4.24 |

### Speed Measurement Methodology Verification:
- **Inputs Evaluated:** Both tokenizers were evaluated on the **exact identical corpus** (repeated 50x to 100x for stable benchmarking).
- **Encoding Speed:** Original: ~18,200 sent/sec; Experimental: ~19,400–20,000 sent/sec.
- **Decoding Speed:** Original: ~83,000 sent/sec; Experimental: ~126,000–130,000 sent/sec.
- **Explanation:** The experimental tokenizer achieves higher sentence-level decoding throughput because it emits significantly fewer tokens per sentence (43.9 vs 85.9), requiring fewer subword stitch operations per text.

---

## 6. Integrity & Governance Audit

- **Original Candidate A:** `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (**UNTOUCHED**)
- **Original Candidate B:** `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (**UNTOUCHED**)
- **Experimental Candidate A:** `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce` (**ISOLATED EXPERIMENTAL ARTIFACT**)
- **Production Files:** Zero production code, configs, or gates modified.
- **Acquisition Status:** Zero production data acquired; downloads remain LOCKED.
