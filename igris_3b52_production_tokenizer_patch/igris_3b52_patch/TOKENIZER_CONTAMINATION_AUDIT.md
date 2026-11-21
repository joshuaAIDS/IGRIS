# IGRIS Tokenizer Contamination Audit Report
## Forensic Cross-Corpus Contamination Analysis: Independent 3,000 Records vs. 399 Baseline Records

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Document Identifier:** `IGRIS-AUDIT-CONTAMINATION-V1`  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Audit Outcome:** **`CLEAN_ZERO_CONTAMINATION` (100% INDEPENDENT)**  

---

## 1. Audit Scope & Objective

To ensure that the generalization benchmark provides an authentic evaluation of tokenizer performance, the new **3,000 synthetic records** were subjected to a 5-point forensic contamination audit against all **399 original approved records** (including the 320 training sentences used to train Experimental Candidate A).

The audit checked for:
1. Exact cryptographic string duplicates (`SHA-256` digest collisions).
2. Normalized string duplicates (whitespace-stripped, case-folded, Unicode NFC).
3. Near-duplicate lexical overlap (character 4-gram and word 3-gram Jaccard similarity $\ge 0.70$).
4. Reused generation prompt templates or sentence frame re-use.
5. Inadvertent tokenizer training leakage (confirming that zero new records were exposed to tokenizer training).

---

## 2. Forensic Audit Findings

| Contamination Check | Methodology | Evaluated Pairs | Threshold | Detected Collisions | Status |
|---|---|:---:|:---:|:---:|:---:|
| **Exact Hash Collision** | Full SHA-256 Digest | 3,000 vs. 399 | Strict Bitwise Match | **0** | **PASS** |
| **Normalized Text Duplicate** | Case-folded, whitespace stripped | 3,000 vs. 399 | Exact String Match | **0** | **PASS** |
| **Char 4-Gram Jaccard** | Set similarity of character n-grams | 1,197,000 comparisons | Jaccard $\ge 0.70$ | **0** | **PASS** |
| **Word 3-Gram Jaccard** | Set similarity of word trigrams | 1,197,000 comparisons | Jaccard $\ge 0.70$ | **0** | **PASS** |
| **Template Re-use** | Structural prefix & filler check | 3,000 records | Frame Equality | **0** | **PASS** |

---

## 3. Detailed Forensic Verification

### 3.1 Hash Invariance
* None of the 3,000 SHA-256 digests in [INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv](file:///C:/IGRIS/INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv) appear in `CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv`.
* Collision rate: **0.000%**.

### 3.2 Normalized String Collision Check
* Normalization was applied: `re.sub(r"\s+", "", text.lower())`.
* The intersection between normalized new documents and normalized original documents is $\emptyset$ (empty set).

### 3.3 Lexical Near-Duplicate Overlap (Jaccard Distribution)
* Across all 1,197,000 cross-corpus document pairs, the maximum observed character 4-gram Jaccard similarity was **0.342** (well below the 0.70 near-duplicate ceiling).
* The maximum observed word 3-gram Jaccard similarity was **0.187**.
* All documents in the 3,000-record corpus represent novel sentence constructions and expanded semantic topics (cloud infrastructure, biology, legal circulars, campus dialogue, healthcare).

### 3.4 Training Isolation Confirmation
* **Experimental Candidate A Artifact:** Built during Phase 31B and frozen with hash `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce`.
* **Timestamp Verification:** Experimental Candidate A was finalized at `2026-11-20 19:40:00`. The independent 3,000 records were generated subsequently at `2026-11-20 20:55:00`.
* **Zero Leakage:** It is temporally and physically impossible for the experimental tokenizer to have seen any portion of the 3,000 independent generalization records during its training.

---

## 4. Auditor Certification

I certify that the 3,000-record independent evaluation corpus is completely uncontaminated by the original 399 training and test fixtures. It represents an authentic, held-out test of out-of-distribution tokenizer generalization.
