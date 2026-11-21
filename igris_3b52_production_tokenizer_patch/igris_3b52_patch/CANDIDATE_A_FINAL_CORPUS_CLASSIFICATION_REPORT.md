# IGRIS Candidate A: Final Corpus Classification Audit & Reconciliation Report

**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Audit Date:** 2026-11-20  
**Status:** **AUDIT COMPLETE — 100% RECONCILED (ZERO DISCREPANCIES REMAINING)**  
**Target Tokenizer:** Candidate A (ByteLevel BPE, 32,768 Vocabulary)  
**Governance Invariants:** Preserved (Candidate A, Candidate B, Experimental Tokenizer untouched; $0.00 spend; zero pretraining)

---

## 1. Executive Summary & Purpose

This forensic dataset audit resolves the two remaining classification ambiguities identified in the Candidate A synthetic corpus accounting audit:
1. **Exclusion Category Discrepancy (402 Records):** Reconciled the reporting difference between the accounting table (393 Non-target, 9 Malformed/Noise) and the narrative (385 Non-target/out-of-scope, 9 Malformed, 8 Noise) into four mutually exclusive, record-verified categories.
2. **Language Label Transition Matrix (399 Accepted Records):** Formally mapped the relationship between the operational tokenizer training labels (**Tanglish: 196, Tamil: 111, English: 92**) and the primary linguistic provenance labels (**Tamil: 153, English: 131, Tanglish: 115**), identifying the exact 81 transitioned records with granular linguistic evidence.
3. **Training-Manifest Integrity:** Verified 100% single-occurrence isolation across splits (320 Train, 40 Val, 39 Test), confirmed zero validation/test leakage to BPE trainer, and re-verified all cryptographic hashes.

---

## 2. Section 1: Exclusion-Category Reconciliation (402 Records)

### Root Cause of Historical Reporting Discrepancy:
- In the initial summary table, 8 synthetic adversarial symbol noise records (`P25-SYN-0131`, `0134`, `0135`, `P26-DEV-0093`, `0095`, `P26-VAL-0095`, `P26-TEST-0093`, `0095`) and 1 Python code fixture (`IGRIS-SYNTH-DRYRUN-0015`) were grouped into the `Non-Target Dropped` column, yielding 384 + 8 + 1 = 393 records. The `Malformed / Noise` column contained only the 9 records with < 5 characters.
- In the narrative, the 1 Python code record was grouped with the 384 Indic script records under "Non-Target Indic Scripts (385 records)", leaving 8 noise records and 9 malformed records.

### Four Mutually Exclusive Reconciled Categories:
Every record in [CANDIDATE_A_EXCLUSION_CATEGORY_RECONCILIATION.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_EXCLUSION_CATEGORY_RECONCILIATION.csv) is assigned to exactly one final category:

| Reconciled Exclusion Category | Record Count | Description & Invariant Verification |
|---|:---:|---|
| `NON_TARGET_LANGUAGE_OR_SCRIPT` | **384** | Records containing non-target Indic script Unicode characters (Devanagari: 74, Telugu: 72, Malayalam: 63, Kannada: 62, Bengali: 57, Gujarati: 56). Strictly `OUT_OF_SCOPE`. |
| `MALFORMED_OR_TOO_SHORT` | **9** | Degenerate text under 5 characters (empty strings, 2-character fragments `'Hi'`, `'வா'`, `'OK'`, 4-character `'Good'`). Fails minimum length threshold. |
| `NOISE_OR_LOW_INFORMATION` | **8** | Synthetic adversarial test fixtures composed of repeated symbols (`??? !!! ....`), digit strings, or ASCII punctuation soup; lacking linguistic syntax. |
| `OTHER_OUT_OF_SCOPE` | **1** | Implementation Python source code (`IGRIS-SYNTH-DRYRUN-0015`: `def compute_attention(q, k, v, mask=None)...`). Excluded as programming syntax. |
| **TOTAL** | **402** | **100% Reconciled and Mathematically Verified.** |

---

## 3. Section 2: Language-Label Reconciliation & Transition Matrix (399 Records)

### Analysis of Classification Methodologies:
- **Operational Classification (Earlier Training Report & Split Manifest):**
  - Applied `LanguageIdentifierV2` rule: any record exhibiting intra-sentential script mixing (Tamil Unicode + Latin alphabetic characters) or Romanized Tamil phonology/particles is classified as `TANGLISH`.
  - Result: **Tanglish: 196, Tamil: 111, English: 92** (Total: 399).
- **Primary Linguistic Classification (Provenance Audit):**
  - Evaluates dominant grammatical matrix and primary script:
    - 41 code-mixed records with Tamil matrix syntax and script (e.g. *"Microservice health checks pass ஆனா மட்டும் தான்..."*) + 1 pure colloquial Romanized Tamil record (`P25-SYN-0033`: *"Innaiku kaalaila romba mazhai peyudhu, veliya poga mudiyala pa"*, 0 English words) are classified as **`TAMIL`** (111 + 42 = **153**).
    - 39 records with English matrix syntax in Latin script with conversational Tamil particles (*"Hey machan, check the build logs..."*, *"You must verify the cryptographic signatures before approving the release da."*) are classified as **`ENGLISH`** (92 + 39 = **131**).
    - 115 records from dedicated procedural Tanglish synthetic fixture generators (`PHASE23A`: 100, `tanglish_synthetic_generator_v2.py`: 15) remain classified as **`TANGLISH`** (196 - 81 = **115**).

### Complete Label-Transition Matrix:

| Original Training Label | Current TAMIL | Current ENGLISH | Current TANGLISH | Current UNKNOWN | Total Original |
|---|:---:|:---:|:---:|:---:|:---:|
| **TAMIL** | **111** | 0 | 0 | 0 | **111** |
| **ENGLISH** | 0 | **92** | 0 | 0 | **92** |
| **TANGLISH** | **42** | **39** | **115** | 0 | **196** |
| **TOTAL** | **153** | **131** | **115** | **0** | **399** |

### Transition Summary & Corpus Scope Guarantee:
- Exactly **81 records** transitioned out of the broad operational `TANGLISH` bucket:
  - **42 to TAMIL** (Tamil script/syntax dominant; 0% non-Tamil Indic script).
  - **39 to ENGLISH** (English grammatical matrix; 0% non-English/Tamil content).
  - **115 retained as TANGLISH** (dedicated procedural Tanglish fixtures).
- **Scope Confirmation:** Zero records were classified as `UNKNOWN` or out-of-scope. All 399 records remain strictly within **Tamil**, **English**, and **Tanglish**.
- All 81 transitioned records are itemized with full character metrics, script detection, and evidence in [CANDIDATE_A_LANGUAGE_LABEL_CHANGE_AUDIT.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_LANGUAGE_LABEL_CHANGE_AUDIT.csv).

---

## 4. Section 3: Training-Manifest Integrity Audit

The training split manifest [CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv) was forensically validated against the 399 unique documents:

1. **Split Distribution:**
   - **TRAIN:** 320 documents (80.2%)
   - **VALIDATION:** 40 documents (10.0%)
   - **TEST:** 39 documents (9.8%)
   - **Total:** 399 unique documents.
2. **Single-Occurrence Guarantee:**
   - Every `doc_id` from `SYN-CAND-A-0001` to `SYN-CAND-A-0399` appears **exactly once**. Zero missing or duplicate IDs.
3. **Trainer Isolation Verification:**
   - Only the 320 `TRAIN` documents were supplied to `build_candidate_a()`.
   - Zero validation or test documents were ever passed to BPE merge learning.
4. **Content Hash Verification:**
   - Every recorded `text_sha256` in the manifest matches the exact cryptographic SHA-256 of the NFC-normalized source text (399/399 verified).
5. **Cryptographic Invariants:**
   - Candidate A Production Hash: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (**UNTOUCHED**)
   - Candidate B Production Hash: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (**UNTOUCHED**)
   - Experimental Tokenizer Hash: `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce` (**UNTOUCHED**)

---

## 5. Section 4: Confirmed Facts vs. Corrections vs. Decisions Required

### A. Confirmed Facts:
- Total raw candidate records harvested: **1,084**.
- Total approved unique documents: **399**.
- Total duplicates suppressed: **283** (269 exact, 4 normalized, 10 near).
- Total excluded records: **402** (384 non-target Indic, 9 malformed, 8 noise, 1 python code).
- Mathematical balance: 1,084 = 399 + 283 + 402 holds to the exact single record.
- Split distribution: **320 Train, 40 Val, 39 Test**.
- Zero code contamination in 399 natural language documents (0% code leaks).
- Zero production data downloaded ($0.00 spend).

### B. Corrected Historical Counts:
- **Exclusion Table Breakdown:**
  - Historical report table merged 8 noise records and 1 code record into the Non-target column (384 + 8 + 1 = 393).
  - Corrected mutual exclusivity: **384 Non-Target Script**, **9 Malformed/Too Short**, **8 Noise/Low Information**, **1 Other Out-of-Scope (Code)**.
- **Language Distribution Interpretation:**
  - The difference between `196 / 111 / 92` and `115 / 153 / 131` is a difference of classification granularity (Operational Code-Mix First vs. Dominant Matrix Grammar/Script First), not missing or corrupt data.
  - Both distributions account for all 399 records with 100% traceability.

### C. Unresolved Classifications:
- **Zero records require `UNKNOWN_REQUIRES_OWNER_REVIEW` for language scope.** All 399 records are confirmed to belong strictly to Tamil, English, or Tanglish.

### D. Owner Decisions Still Required:
1. **Corpus Label Nomenclature Freeze:**
   - *Option 1 (Operational Tagging):* Retain `TANGLISH: 196, TAMIL: 111, ENGLISH: 92` as the primary dataset catalog labels (prioritizing code-mixed benchmark tagging).
   - *Option 2 (Linguistic Matrix Tagging):* Formally adopt `TAMIL: 153, ENGLISH: 131, TANGLISH: 115` as the primary dataset catalog labels (prioritizing script and grammatical matrix dominance).
2. **Phase Completion Approval:** Acknowledge completion of the Candidate A synthetic corpus classification audit and grant authorization to proceed to subsequent owner review workflows.

---

## 6. Deliverable Index

All 5 required audit deliverables have been generated and mirrored:

1. [CANDIDATE_A_EXCLUSION_CATEGORY_RECONCILIATION.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_EXCLUSION_CATEGORY_RECONCILIATION.csv)
2. [CANDIDATE_A_LANGUAGE_LABEL_TRANSITION_MATRIX.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_LANGUAGE_LABEL_TRANSITION_MATRIX.csv)
3. [CANDIDATE_A_LANGUAGE_LABEL_CHANGE_AUDIT.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_LANGUAGE_LABEL_CHANGE_AUDIT.csv)
4. [CANDIDATE_A_FINAL_CORPUS_CLASSIFICATION_REPORT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CANDIDATE_A_FINAL_CORPUS_CLASSIFICATION_REPORT.md)
5. [verify_candidate_a_final_classification.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/verify_candidate_a_final_classification.py)

---

## 7. Governance Certification & Stopping Condition

- **Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`
- **Sole Project Owner:** Accountable decision-maker
- **Candidate A:** Unchanged (`ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`)
- **Candidate B:** Unchanged (`d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`)
- **Experimental Tokenizer:** Unchanged (`3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce`)
- **Acquisition Grants:** `0`
- **Cloud Spending:** `$0.00`
- **Production Pretraining:** `LOCKED`

Audit is complete. Awaiting review and policy decision from the project owner.
