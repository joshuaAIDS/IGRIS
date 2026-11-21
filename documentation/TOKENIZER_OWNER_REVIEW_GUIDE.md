# IGRIS Tokenizer Sole Developer Owner Review Guide
## Protocol and Diagnostic Guidelines for Linguistic Review of Candidate A vs. Experimental Candidate A

**Document Identifier:** `IGRIS-GUIDE-OWNER-REVIEW-V1`  
**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-21  
**Target File:** [`TOKENIZER_HUMAN_REVIEW_SAMPLE.csv`](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv)  
**Status:** **READY FOR HUMAN INSPECTION** (300 items, all initialized to `NOT_REVIEWED`)

---

## 1. Review Objective & Governance Principle

This guide establishes the inspection protocol for the sole project owner to evaluate the 300 curated test items in [`TOKENIZER_HUMAN_REVIEW_SAMPLE.csv`](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv).

> [!IMPORTANT]
> **Governance Invariant:**  
> All 300 rows currently retain `review_status = "NOT_REVIEWED"` with blank `human_review_decision` and `reviewer_rationale`. No automated script has fabricated approval.  
> Under the `SOLO_DEVELOPER_OWNER_REVIEW` operating model, only the sole project owner has the authority to assign decisions.

---

## 2. Decision Taxonomy

When inspecting each row, the owner may assign one of the following decisions in `human_review_decision`:

| Decision Tag | Definition | Usage Criteria |
|---|---|---|
| **`APPROVED`** | Linguistically acceptable. | Token boundaries preserve stems, affixes, or natural syllables without creating destructive anomalies. |
| **`FLAGGED_CONCERN`** | Functional but sub-optimal. | Compression is achieved, but a non-morphemic subword cut or detached combining mark occurs. |
| **`REJECTED`** | Linguistically invalid. | Splits essential roots into uninterpretable fragments, creates cross-boundary chimeras, or induces illegal character sequences. |
| **`CONDITIONAL`** | Acceptable for testing only. | Tolerated in the experimental prototype, but must be tuned prior to web-scale pretraining. |

---

## 3. CSV Column Reference Guide

| Column Name | Purpose | What to Look For |
|---|---|---|
| `example_id` | Unique identifier (`REV-TA-001`..`REV-TG-100`). | Sequential tracking across Tamil, English, Tanglish. |
| `original_text` | Exact input text string. | Reference input for morphological verification. |
| `cand_a_decoded_contributions` | Original Candidate A decoded tokens. | Notice extensive byte fragmentation (`<0x..>`) and single-letter splits. |
| `cand_exp_decoded_contributions` | Exp Candidate A decoded tokens. | Inspect whether subwords align with authentic prefixes, roots, or syllables. |
| `cand_a_token_count` vs `cand_exp_token_count` | Quantitative token counts. | Check compression ratio. |
| `total_grapheme_clusters` | UAX #29 grapheme cluster count. | Number of authentic visual characters. |
| `cand_a_unique_affected_clusters` | Clusters cut in Candidate A. | In Tamil, typically $\ge 1$ due to detached pulli. |
| `cand_exp_unique_affected_clusters` | Clusters cut in Exp Candidate A. | Look for instances where Exp A preserves standalone vowels (e.g. `complex-ஆ`). |
| `morphological_status` | Automated pre-classification. | Values: `PRESERVED`, `DISRUPTED`, or `UNCERTAIN`. |
| `potential_segmentation_concern` | Automated diagnostic note. | Specific flags regarding grapheme cuts or excessive fragmentation. |
| `review_status` | Status gate. | Set to `NOT_REVIEWED` until owner signs off. |
| `human_review_decision` | Owner's final verdict. | Fill with: `APPROVED`, `FLAGGED_CONCERN`, `REJECTED`, or `CONDITIONAL`. |
| `reviewer_rationale` | Owner's technical reasoning. | Concise justification for the decision. |

---

## 4. Language-Specific Inspection Protocols

### 4.1 Tamil Script (`REV-TA-001` to `REV-TA-100`)
1. **Pulli / Virama Handling:**
   - In Tamil, pure consonants carry the virama pulli `்` (U+0BCD). Both Candidate A and Exp A split base consonants from pulli (e.g. `ல்` $\to$ `ல` | `்`).
   - *Question for Owner:* Is detached pulli representation acceptable as an intermediate representation, or does it violate tokenization quality requirements?
2. **Vowel Signs (Matras):**
   - Inspect vowel signs like `ி`, `ு`, `ை`, `ோ` (e.g. `படிக்கிறேன்`, `செய்துகொண்டிருக்கிறான்`).
   - Exp A creates frequent merges like `à®ªà®Ł` (`பட`) and `Ġà®ªà®£` (` பண`). Check if these groupings respect stem boundaries.
3. **Grantha Ligatures:**
   - Inspect items like `ஸ்ரீ`, `க்ஷ`, `ஜாதி`. Confirm that byte reconstruction remains 100% accurate without corrupting the phonetic identity.

### 4.2 English Vocabulary (`REV-EN-001` to `REV-EN-100`)
1. **Common Lexicon:**
   - Verify that high-frequency words (`the`, `model`, `system`, `function`) are atomic or cleanly partitioned.
2. **Technical Compounds & Overmerging:**
   - Inspect compound words like `microservice` (`m | icroser | vice`) and `multithreading`.
   - *Question for Owner:* Does the merge `icroser` crossing the prefix `micro-` and root `service` warrant a `FLAGGED_CONCERN` or `REJECTED`?
3. **Derivational Affixes:**
   - Verify clean isolation of prefixes (`un-`, `asynch-`, `hyper-`) and suffixes (`-tion`, `-able`, `-ment`).

### 4.3 Tanglish Language Contact (`REV-TG-001` to `REV-TG-100`)
1. **Hyphenated Loanwords with Tamil Suffixes:**
   - Inspect: `server-ல்`, `complex-ஆ`, `testing-க்கு`, `database-லிருந்து`, `table-ஐ`.
   - Confirm that the hyphen (`-`) acts as an impermeable barrier keeping the Latin stem and Tamil case suffix separate.
   - Note: In `complex-ஆ`, Exp A correctly recognizes `ஆ` as an atomic token (Token 766), whereas Cand A shreds it into `<0xE0><0xAE>` + `<0x86>`.
2. **Romanized Tamil Verbs:**
   - Inspect: `pannirukkom`, `mudikanum`, `vanthuten`, `solren`.
   - Check whether syllables group naturally (e.g. `p | ann | iru | k | k | om`).
3. **Discourse Markers:**
   - Inspect conversational clitics: `da`, `pa`, `seri`, `aiyo`, `machan`.

---

## 5. Instructions for Finalizing the Review

1. Open [`TOKENIZER_HUMAN_REVIEW_SAMPLE.csv`](file:///C:/IGRIS/TOKENIZER_HUMAN_REVIEW_SAMPLE.csv) in your spreadsheet or CSV editor.
2. For each record, enter your decision in `human_review_decision` and your notes in `reviewer_rationale`.
3. Update `review_status` from `NOT_REVIEWED` to `REVIEWED`.
4. Once completed, the final governance gate for tokenizer comparison will be unlocked.
