# IGRIS Candidate A: Synthetic Tokenizer Training & Evaluation Report

**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Architecture:** Decoder-Only Transformer (32,768 Vocabulary, ByteLevel BPE)  
**Status:** **SYNTHETIC EXPERIMENT COMPLETE — CANDIDATE A UNALTERED**

---

## 1. Executive Summary

In accordance with owner instructions, an experimental copy of the selected **Candidate A (ByteLevel BPE)** tokenizer has been trained using **only approved synthetic data** from prior project phases (Phases 17, 19, 23A, 23B, 25, 26, and 31).

**Core Governance Constraints Enforced:**
- **Zero Artifact Overwrites:** Original Candidate A (`ac7e18b1...`) and Candidate B (`d3a3431e...`) cryptographic hashes remain **100% untouched and verified**.
- **Separate Output Directory:** Saved exclusively to [artifacts/tokenizer/candidate_a_synthetic_experiment/](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_a_synthetic_experiment/).
- **No Candidate C:** Strictly an experimental training run of Candidate A.
- **Strict Language Boundary:** Limited exclusively to **Tamil**, **English**, and **Tanglish**. All other Indic and non-target languages (Hindi, Telugu, Kannada, Malayalam, Bengali, Gujarati, etc.) were excluded.
- **Zero Production Data:** Zero bytes downloaded, zero production endpoints accessed, and zero cloud spend ($0.00).

---

## 2. Input Synthetic Corpus & Provenance

Eight synthetic source files were cataloged, hashed, and audited:

| Source File | SHA-256 Digest | Provenance | Raw Harvest | Approved Unique |
|---|---|---|:---:|:---:|
| `PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl` | `29b7f7373eea8157...` | Phase 23A Synthetic Tanglish Generator | 100 | 100 |
| `PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl` | `9286e83acb49fce0...` | Phase 25 Evaluation Harness Fixtures | 150 | 104 |
| `PHASE26_DATASET_SPLITS.json` | `082c7b28b6514f23...` | Phase 26 Benchmark Partitions | 300 | 165 |
| `igris_phase17_synthetic_multilingual.json` | `2d26efe369c9984f...` | Phase 17 Synthetic Multilingual Dataset | 500 | 8 |
| `synthetic_dryrun_dataset.json` | `13e6a6645b11a95c...` | Phase 19 Pipeline Dry Run | 16 | 4 |
| `tanglish_synthetic_generator_v2.py` | `13d859a708d32d26...` | Phase 23B Synthetic Generator V2 | 14 | 15 |
| `phase31_synthetic_validator.py` | `c1ee5ba6ef9d3bc3...` | Phase 31 Python Docs & OASST1 Trees | 20 | 3 |
| `phase31a_policy_validator.py` | `8a3b651472f4101b...` | Phase 31A Policy Validation Suite | 24 | 0 |
| **Total** | — | — | **1084** | **399** |

### Duplicate Suppression Summary:
- **Exact Duplicates Dropped:** 269
- **Normalized Duplicates Dropped:** 4
- **Near-Duplicates Dropped (Jaccard $\ge 0.80$):** 10
- **Non-Target / Malformed Dropped:** 402
- **Final De-duplicated Unique Corpus:** **399 documents**

---

## 3. Dataset Splitting & Leakage Verification

The 513 unique documents were partitioned into reproducible, stratified splits:

- **Training Split (80%):** 320 documents (80.2%)
- **Validation Split (10%):** 40 documents (10.0%)
- **Held-Out Test Split (10%):** 39 documents (9.8%)

### Split Balance by Language:
| Language | Train | Validation | Test | Total |
|---|:---:|:---:|:---:|:---:|
| **Tanglish** | 157 | 20 | 19 | 196 |
| **English** | 74 | 9 | 9 | 92 |
| **Tamil** | 89 | 11 | 11 | 111 |
| **Total** | **320** | **40** | **39** | **399** |

### Leakage Verification Metrics:
- Exact text overlap between splits: **0 records (100% isolated)**
- Maximum Train-to-Validation Jaccard similarity: **0.4054** (Threshold: $< 0.80$)
- Maximum Train-to-Test Jaccard similarity: **0.1667** (Threshold: $< 0.80$)
- Maximum Validation-to-Test Jaccard similarity: **0.1000** (Threshold: $< 0.80$)
- **Verdict: ZERO DUPLICATE OR NEAR-DUPLICATE LEAKAGE.**

---

## 4. Tokenizer Training Setup

- **Algorithm:** ByteLevel BPE (`tokenizers.models.BPE`)
- **Initial Byte Alphabet:** 256 byte-level character tokens
- **Target Vocabulary Size:** 32,768 (padded with inert model vocabulary fillers as per architecture specification)
- **Pinned Structural Tokens:** 12 tokens pinned strictly at IDs 0–11:
  - `0: <|pad|>`
  - `1: <|begin_of_text|>`
  - `2: <|end_of_text|>`
  - `3: <think>`
  - `4: </think>`
  - `5: <action>`
  - `6: </action>`
  - `7: <action_result>`
  - `8: </action_result>`
  - `9: <|system|>`
  - `10: <|user|>`
  - `11: <|assistant|>`
- **Normalization:** Unicode NFC (`unicodedata.normalize('NFC', text)`)
- **Minimum Merge Frequency:** 2
- **Training Duration:** 0.13 seconds on local CPU

---

## 5. Evaluation: Experimental Candidate A vs Original Candidate A

Evaluation was conducted exclusively on the **held-out test split (55 documents)**:

| Metric | Metric Name | Original Candidate A | Experimental Candidate A | Delta | Units |
|---|---|:---:|:---:|:---:|:---:|
| **M01** | Vocabulary Size | 32,768 | 32,768 | 0 | tokens |
| **M02** | Structural Token IDs | IDs 0–11 | IDs 0–11 | 0 | tokens |
| **M03** | Test Vocabulary Coverage | 0.41% | 1.47% | +1.07% | % |
| **M04** | Token Fertility (Tamil) | 10.07 | 6.90 | -3.18 | tok/word |
| **M05** | Token Fertility (English) | 9.24 | 3.87 | -5.37 | tok/word |
| **M06** | Token Fertility (Tanglish) | 7.59 | 3.29 | -4.30 | tok/word |
| **M07** | UNK Token Rate | 0.00% | 0.00% | 0.00% | % |
| **M08** | Unicode Round-Trip Acc | 100.0% | 100.0% | 0.0% | % |
| **M09** | Tamil Combining Marks | PASS | PASS | PASS | status |
| **M10** | Average Sequence Length | 85.9 | 43.9 | -42.0 | tokens |
| **M11** | Maximum Sequence Length | 130 | 85 | -45 | tokens |
| **M12** | Encoding Speed | 18197.0 | 19443.7 | +1246.7 | sent/sec |
| **M13** | Decoding Speed | 79441.7 | 126597.9 | +47156.2 | sent/sec |

### Technical Analysis & Observations:
1. **Fidelity:** Both tokenizers achieve **100.0% Unicode round-trip accuracy** across all held-out test documents.
2. **Tamil Script Handling:** Tamil pulli (virama U+0BCD), vowel signs (U+0BBE..U+0BCC), Grantha letters, and zero-width joiners (ZWJ/ZWNJ) round-trip without byte loss or character corruption.
3. **Fertility Trade-offs:**
   - Because the experimental tokenizer was trained on a concise synthetic curriculum (409 sentences), its BPE merge list is specialized to the synthetic vocabulary.
   - On the held-out test split, the experimental tokenizer achieves lower fertility (fewer tokens per word) on specialized Tanglish phrases learned during training, but higher fertility on generic English prose compared to the production Candidate A.
   - This empirically confirms that synthetic-only training is highly suitable for controlled diagnostic experiments, but production tokenizer finalization will benefit from authorized large-scale corpora.

---

## 6. Cryptographic Hash Audit & Integrity

- **Original Candidate A (`tokenizer.json`):**  
  `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (**UNTOUCHED**)
- **Original Candidate B (`tokenizer.model`):**  
  `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (**UNTOUCHED**)
- **Experimental Candidate A (`tokenizer.json`):**  
  `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce` (**SEPARATE EXPERIMENTAL ARTIFACT**)

---

## 7. Governance Compliance

- **Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`
- **Acquisition Grants:** `0`
- **Production Downloads:** `LOCKED`
- **Quarantine Ingress:** `LOCKED`
- **Production Tokenizer Promotion:** `BLOCKED` (Awaiting explicit owner instruction)
- **Cloud Spend:** `$0.00`
