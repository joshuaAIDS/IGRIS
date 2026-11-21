# IGRIS Master Human Review Package (Version 2.0)

**Document Version:** 2.0.0  
**Milestone:** 3C.9 — Human Approval Package & Authorization Readiness Audit  
**Governing Standard:** IGRIS Dataset Governance, Security & Lineage Architecture  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary & Purpose

The **IGRIS Master Human Review Package (Version 2.0)** establishes the formal governance framework and operational instruments required to execute an authentic, auditable human review of all 32 candidate dataset sources across the 10 canonical benchmark categories.

To ensure separation of duties, prevent single-point failures, and eliminate conflicts of interest, governance authority is partitioned among **four independent human roles**:
1. [`REVIEW_DATA_CUSTODIAN_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_DATA_CUSTODIAN_V2.md) — Custody, transport, UTF-8 losslessness, NFC normalization, quarantine isolation.
2. [`REVIEW_LEGAL_GOVERNANCE_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_LEGAL_GOVERNANCE_V2.md) — License verification, commercial rights, Indian Sec 22 Life+60, UK/EU Life+70, Gutenberg 4-pillar review.
3. [`REVIEW_SECURITY_PRIVACY_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_SECURITY_PRIVACY_V2.md) — PII screening, web crawl safety, prompt injection / red-team quarantine, toxic token exclusion.
4. [`REVIEW_CHIEF_ARCHITECT_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_CHIEF_ARCHITECT_V2.md) — Model architecture, 32,768 vocabulary budget, benchmark contamination guards, artifact invariance.

---

## 2. Four-of-Four Consensus Rule (Quorum Mandate)

```
+----------------------------------------------------------------------------------------------------+
|                         FOUR-ROLE CONSENSUS GATE ARCHITECTURE                                      |
+----------------------------------------------------------------------------------------------------+

     [DATA_CUSTODIAN]       [LEGAL_GOVERNANCE]      [SECURITY_PRIVACY]      [CHIEF_ARCHITECT]
      (Custody/Lossless)     (License/Copyright)     (PII/Toxic Guard)       (Vocab/Contamination)
             |                       |                       |                       |
             +-----------------------+-----------+-----------+-----------------------+
                                                 |
                                                 v
                                  [4-of-4 CONSENSUS VERIFICATION]
                                                 |
                               +-----------------+-----------------+
                               | All 4 Signed                      | Any Role Rejects
                               v                                   v
                      [GATE UNLOCKED]                     [DEFAULT-DENY LOCK]
                  (Scoped Token Issued)                   (Access Denied)
```

> [!CAUTION]
> **GOVERNANCE DIRECTIVE**:
> 1. Unlocking any pipeline gate requires unanimous consensus (**4 out of 4 approvals**).
> 2. A rejection by any single role immediately triggers a **DEFAULT-DENY LOCK** for that source.
> 3. Zero approvals or signatures may be automated, simulated, or populated by LLM agents. All signatures must be physically or cryptographically executed by qualified human personnel.

---

## 3. Reviewer Responsibilities Matrix

| Review Role | Primary Statutory & Technical Mandate | Core Documents & Artifacts Under Review | Critical Veto Triggers |
| :--- | :--- | :--- | :--- |
| **`DATA_CUSTODIAN`** | SHA-256 pre-validation, losslessness, Unicode NFC, sandbox staging, trademark removal. | `DATASET_SOURCE_CATALOG_V3.csv`, `GUTENBERG_JURISDICTION_REVIEW_V2.md` | Hash mismatch, encoding corruption, failed de-branding. |
| **`LEGAL_GOVERNANCE`** | Commercial rights, Section 22 Life+60, Life+70, item-level review, copyleft risk. | `DATASET_LICENSE_CLASSIFICATION_V3.csv`, `INDIA_COPYRIGHT_REVIEW.md` | Non-commercial (`-NC`) clauses, author death > 1965/1955, unvetted scrapes. |
| **`SECURITY_PRIVACY`** | PII screening policy, toxic token exclusion, prompt injection quarantine, secrets audit. | `PIPELINE_GATE_AUDIT.md`, `CONVERSATIONAL_DATA_CLASSIFICATION.md` | Unredacted Aadhaar/PAN/SSN, ingestion of red-team data into training. |
| **`CHIEF_ARCHITECT`** | Architecture preservation, vocabulary budget, benchmark contamination, artifact hash invariance. | `TOKENIZER_DATA_ELIGIBILITY_MATRIX.md`, Candidate A & B artifacts | Hash alteration, structural token shift, training on HumanEval/FLORES. |

---

## 4. The 32-Source Review Dossier Index

Every source in the catalog is indexed in [`SOURCE_HUMAN_REVIEW_MATRIX.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/SOURCE_HUMAN_REVIEW_MATRIX.csv):
1. **Tamil (3 sources)**: `SRC-TM-01` (IndicCorp v2), `SRC-TM-02` (Wikipedia Dump), `SRC-TM-03` (OSCAR Tamil).
2. **English (3 sources)**: `SRC-EN-01` (Project Gutenberg), `SRC-EN-02` (Wikipedia Dump), `SRC-EN-03` (C4).
3. **Tanglish (3 sources)**: `SRC-TG-01` (DravidianCodeMix), `SRC-TG-02` (IndicGLUE), `SRC-TG-03` (Social Sentiment - REJECTED).
4. **Hindi (3 sources)**: `SRC-HI-01` (IndicCorp v2), `SRC-HI-02` (Wikipedia Dump), `SRC-HI-03` (IIT Bombay - REJECTED).
5. **Other Indian Languages (5 sources)**: `SRC-OI-01` (Telugu), `SRC-OI-02` (Malayalam), `SRC-OI-03` (Kannada), `SRC-OI-04` (Bengali), `SRC-OI-05` (Gujarati).
6. **Multilingual Mixed (2 sources)**: `SRC-ML-01` (FLORES-200), `SRC-ML-02` (mC4).
7. **Programming Code (2 sources)**: `SRC-CD-01` (The Stack v2 Permissive), `SRC-CD-02` (HumanEval & MBPP).
8. **Technical Documentation (3 sources)**: `SRC-TD-01` (Linux Kernel), `SRC-TD-02` (IETF RFCs), `SRC-TD-03` (Python Docs).
9. **Conversational Text (6 sources)**: `SRC-CV-01` (DailyDialog - REJECTED), `SRC-CV-02` (OpenSubtitles - REJECTED), `SRC-CV-03` (OASST1), `SRC-CV-04` (Anthropic HH-RLHF), `SRC-CV-05` (MultiWOZ 2.4), `SRC-CV-06` (Gutenberg Theatrical).
10. **Emoji & Unicode Edge Cases (2 sources)**: `SRC-EM-01` (Unicode 15.1 Suite), `SRC-EM-02` (Unicode 15.1 Emoji Files).

---

## 5. Master Package Sign-Off Summary Record

This master summary record is populated upon the completion of all four independent review documents:

```
+====================================================================================================+
|                                MASTER HUMAN APPROVAL SUMMARY RECORD                                |
+====================================================================================================+
1. DATA_CUSTODIAN Approval:      [ ] PENDING    [ ] APPROVED    [ ] REJECTED   Date: _______________
   Reviewer Name: _____________________________________   Signature: _______________________________

2. LEGAL_GOVERNANCE Approval:    [ ] PENDING    [ ] APPROVED    [ ] REJECTED   Date: _______________
   Reviewer Name: _____________________________________   Signature: _______________________________

3. SECURITY_PRIVACY Approval:    [ ] PENDING    [ ] APPROVED    [ ] REJECTED   Date: _______________
   Reviewer Name: _____________________________________   Signature: _______________________________

4. CHIEF_ARCHITECT Approval:     [ ] PENDING    [ ] APPROVED    [ ] REJECTED   Date: _______________
   Reviewer Name: _____________________________________   Signature: _______________________________
+====================================================================================================+
OVERALL GOVERNANCE DECISION:     [ ] ALL APPROVED (UNLOCKED)    [X] PENDING REVIEW (LOCKED)
+====================================================================================================+
```
