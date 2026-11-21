# PHASE 31 — OASST1 PRIVACY FILTERING AND SPLIT ISOLATION PLAN

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target Source:** `SRC-CV-03` (OpenAssistant OASST1 English)  
**Date:** 2026-11-20  

---

## 1. Dialogue Tree Rejection Taxonomy

```
+--------------------------------+-------------------------------------------------------------+
| Rejection Reason Code          | Technical Condition                                         |
+--------------------------------+-------------------------------------------------------------+
| REJECT_ORPHAN_MESSAGE          | Message parent_id is missing from tree index                |
| REJECT_CYCLE_DETECTED          | Graph traversal detects cyclical reference                  |
| REJECT_DUPLICATE_NODE          | Duplicate message_id or identical text at sibling node      |
| REJECT_LANG_MISMATCH_TANGLISH  | Contains >= 2 Romanized Tamil particles despite 'en' tag    |
| REJECT_LANG_OUT_OF_SCOPE       | Language tag is not 'en' or detected as out-of-scope        |
| REJECT_EVAL_BENCHMARK_OVERLAP  | Prompt overlaps with MT-Bench / AlpacaEval benchmark        |
| REJECT_UNRESOLVED_PII          | Contains unmasked sensitive personal narrative or contact   |
+--------------------------------+-------------------------------------------------------------+
```

---

## 2. Privacy & PII Scrubbing Protocol

### 2.1 Structured Identifiers (Automated Masking)
* **Email Regex:** Masked to `[EMAIL_REDACTED]`.
* **Phone Regex:** Masked to `[PHONE_REDACTED]`.
* **Social Media Handles (`@user`):** Masked to `[USER_HANDLE]`.

### 2.2 Unstructured Personal Narratives
Volunteer crowd-workers occasionally disclosed personal medical, financial, or relationship anecdotes. High-sensitivity first-person disclosures flagged by keyword heuristics are routed to quarantine rather than admitted to pretraining candidate shards.

---

## 3. Split Isolation Architecture

1. **Candidate Training Pool:** Sourced exclusively from `train.jsonl` dialogue trees.
2. **Permanent Validation Quarantine:** `val.jsonl` dialogue trees are locked and segregated from training to preserve general conversational evaluation integrity.
3. **Evaluation Decontamination:** Ingestion candidate prompts must be screened against MT-Bench multi-turn prompts.
