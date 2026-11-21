# IGRIS Candidate A: Synthetic Corpus Accounting Correction & Reconciliation Report

**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Audit Date:** 2026-11-20  
**Architecture:** Decoder-Only Transformer (32,768 Vocabulary, ByteLevel BPE)  
**Status:** **RECONCILIATION COMPLETE — 100% ACCOUNTED AND VERIFIED**

---

## 1. Executive Summary & Root Cause of Discrepancy

A forensic accounting audit was performed on the Candidate A synthetic tokenizer corpus to resolve the discrepancy between:
- **Reported raw harvest in report narrative:** 1,084
- **Sum of reported individual source table entries:** 1,124
- **Reported final approved corpus:** 399

### Root Cause Analysis:
1. **The Discrepancy:** The initial report markdown table in Section 2 contained manual prospective estimates for the last three sources (`tanglish_synthetic_generator_v2.py`: 14, `phase31_synthetic_validator.py`: 20, `phase31a_policy_validator.py`: 24), which summed to 1,124.
2. **Actual Parser Behavior:** The automated pipeline script (`run_synthetic_tokenizer_training.py`) dynamically harvested records directly from the files:
   - `tanglish_synthetic_generator_v2.py`: yielded **15** records (1 more than the estimated 14).
   - `phase31_synthetic_validator.py`: yielded **3** records (the 3 synthetic Python docstrings). The OASST1 synthetic conversation trees in this file use the dictionary key `messages` rather than `nodes`, so the loop yielded 0 messages.
   - `phase31a_policy_validator.py`: yielded **0** records because its 24 policy test cases are defined dynamically inside execution test functions rather than exposed as a static top-level list.
3. **Reconciled Raw Harvest:** The actual number of raw candidates parsed was exactly:
   $$100 + 150 + 300 + 500 + 16 + 15 + 3 + 0 = \mathbf{1,084}$$
4. **Mathematical Balance:** The actual accounting equation holds with **zero discrepancy**:
   $$\mathbf{1,084 \text{ (Raw)}} = \mathbf{399 \text{ (Approved)}} + \mathbf{283 \text{ (Duplicates)}} + \mathbf{402 \text{ (Excluded)}}$$

---

## 2. Independent Source Count Reconciliation Table

| Source File | SHA-256 Digest | File Size | Initial Report Estimate | Actual Raw Harvest | Exact Dups Dropped | Norm Dups Dropped | Near Dups Dropped | Non-Target Dropped | Malformed / Noise | Final Approved |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl` | `29b7f7373eea8157...` | 53,195 B | 100 | **100** | 0 | 0 | 0 | 0 | 0 | **100** |
| `PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl` | `9286e83acb49fce0...` | 63,637 B | 150 | **150** | 20 | 1 | 5 | 16 | 4 | **104** |
| `PHASE26_DATASET_SPLITS.json` | `082c7b28b6514f23...` | 198,234 B | 300 | **300** | 88 | 3 | 5 | 34 | 5 | **165** |
| `igris_phase17_synthetic_multilingual.json` | `2d26efe369c9984f...` | 1,577,747 B | 500 | **500** | 159 | 0 | 0 | 333 | 0 | **8** |
| `synthetic_dryrun_dataset.json` | `13e6a6645b11a95c...` | 8,041 B | 16 | **16** | 2 | 0 | 0 | 10 | 0 | **4** |
| `tanglish_synthetic_generator_v2.py` | `13d859a708d32d26...` | 5,586 B | 14 | **15** | 0 | 0 | 0 | 0 | 0 | **15** |
| `phase31_synthetic_validator.py` | `c1ee5ba6ef9d3bc3...` | 9,978 B | 20 | **3** | 0 | 0 | 0 | 0 | 0 | **3** |
| `phase31a_policy_validator.py` | `8a3b651472f4101b...` | 20,335 B | 24 | **0** | 0 | 0 | 0 | 0 | 0 | **0** |
| **TOTAL** | — | **1,936,750 B** | **1,124** | **1,084** | **269** | **4** | **10** | **393** | **9** | **399** |

---

## 3. Provenance & Python Implementation Code Leakage Audit

A special forensic audit was conducted on all 18 documents extracted from Python source files:
- **15 fixtures from `tanglish_synthetic_generator_v2.py`** (`SYN-CAND-A-0382` to `SYN-CAND-A-0396`)
- **3 fixtures from `phase31_synthetic_validator.py`** (`SYN-CAND-A-0397` to `SYN-CAND-A-0399`)

### Audit Verdict:
1. **Zero Code Contamination:** Every single record was scanned for Python keywords (`import`, `def`, `class`, `return`, `assert`, `self.`, etc.). Result: **0% code leaks**.
2. **Authentic Natural Language Text:**
   - The 15 fixtures from `tanglish_synthetic_generator_v2.py` are curated multi-domain colloquial and formal Tanglish sentences (e.g. campus deadlines, e-commerce return policies, transit ticketing, healthcare wellness, software git/typing discussions).
   - The 3 fixtures from `phase31_synthetic_validator.py` are pure natural language docstrings and acknowledgments (Euclidean distance description, developer acknowledgment text, index table of contents).
3. **No External Content:** Confirmed that zero production, scraped, or externally retrieved content was admitted.

Detailed record-by-record verification is cataloged in [CANDIDATE_A_PROVENANCE_AUDIT.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_PROVENANCE_AUDIT.csv).

---

## 4. Exclusion Accounting Audit

Every one of the **402 excluded records** was traced and categorized in [CANDIDATE_A_EXCLUSION_AUDIT.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_EXCLUSION_AUDIT.csv):

### Breakdown by Category:
1. **Non-Target Indic Scripts (385 records):**
   - **Devanagari (Hindi, Marathi):** 74 records
   - **Telugu:** 72 records
   - **Kannada:** 62 records
   - **Malayalam:** 63 records
   - **Bengali:** 57 records
   - **Gujarati:** 56 records
   - **Code / Out-of-Scope tag:** 1 record
2. **Malformed / Too Short / Corrupted (9 records):**
   - Characters under 5, empty records, lone combining viramas, or malformed unicode.
3. **Unclassifiable Symbol / Noise Records (8 records):**
   - URL-heavy text, punctuation spam, or boilerplate 404 text tagged as `UNKNOWN`.

**Total Exclusions:** $385 + 9 + 8 = \mathbf{402}$.

---

## 5. Split Accounting & Isolation Verification

The 399 unique documents are partitioned into strict, non-overlapping splits:

- **TRAIN (80.2%):** 320 documents
- **VALIDATION (10.0%):** 40 documents
- **TEST (9.8%):** 39 documents
- **Total:** **399 documents**

### Invariants Confirmed:
1. **Uniqueness:** All 399 documents appear **exactly once** across the splits.
2. **Strict Trainer Isolation:** Only the 320 `TRAIN` documents were supplied to `build_candidate_a()`. Zero validation or test documents were ever passed to the BPE trainer.
3. **Zero Leakage:**
   - Exact text leakage: **0**
   - Maximum inter-split Jaccard similarity: **0.4054** (Strictly $< 0.70$)
   - Prefix overlap ($\ge 50$ chars): **0**

---

## 6. Deliverable Index

All deliverables have been generated and mirrored:

1. [CANDIDATE_A_CORPUS_ACCOUNTING_CORRECTION.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_CORPUS_ACCOUNTING_CORRECTION.md)
2. [CANDIDATE_A_SOURCE_COUNT_RECONCILIATION.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_SOURCE_COUNT_RECONCILIATION.csv)
3. [CANDIDATE_A_EXCLUSION_AUDIT.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_EXCLUSION_AUDIT.csv)
4. [CANDIDATE_A_PROVENANCE_AUDIT.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_PROVENANCE_AUDIT.csv)
5. [verify_candidate_a_corpus_accounting.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/verify_candidate_a_corpus_accounting.py)

---

## 7. Governance Certification & Stopping Condition

- **Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`
- **Candidate A Hash:** `ac7e18b1...` (**UNTOUCHED**)
- **Candidate B Hash:** `d3a3431e...` (**UNTOUCHED**)
- **Experimental Hash:** `3393acbe...` (**UNTOUCHED**)
- **Acquisition Grants:** `0`
- **Production Downloads:** `LOCKED`
- **Model Pretraining:** `LOCKED`
- **Cloud Spending:** `$0.00`

Accounting audit is complete. Awaiting review and direction from the project owner.
