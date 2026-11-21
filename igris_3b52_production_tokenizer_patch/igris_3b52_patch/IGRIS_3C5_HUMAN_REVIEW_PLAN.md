# IGRIS Milestone 3C.5 — Human Review Plan & Governance Preparation Report

**Project:** IGRIS (Decoder-Only Multilingual Transformer)  
**Patch Directory:** `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Milestone:** 3C.5 — Human Review & Dataset Gap Resolution Planning  
**Evaluation Candidates:** Candidate A (ByteLevel BPE, provisional front-runner) & Candidate B (SentencePiece Unigram)  
**Production Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

Milestone 3C.5 prepares the IGRIS project for formal human governance sign-off by:
1. Decomposing `HUMAN_REVIEW_PACKAGE.md` into **four dedicated, role-specific review documents** for each independent governance authority.
2. Formulating a **26-source decision register** that rigorously distinguishes between **technical verification** (encoding, format, throughput) and **legal approval** (commercial rights, copyleft scope).
3. Investigating and resolving the two critical dataset coverage deficits identified in Milestone 3C.4:
   - **Category 5 Gap**: Identified unencumbered `CC0-1.0` sources for **Bengali** and **Gujarati** (`IndicCorp v2`).
   - **Category 9 Deficit**: Formulated a legally cleared replacement suite for **Conversational Text** under `Apache-2.0`, `MIT`, and `Public Domain` (`OpenAssistant`, `Anthropic HH-RLHF`, `Project Gutenberg Dramatic Dialogue`).
4. Upholding all strict safety invariants: **zero downloads performed, production gate strictly locked, candidate artifacts byte-invariant, and zero fabricated approvals**.

---

## 2. Task 1: Dedicated Role Review Documents

In accordance with milestone instructions, separate review documents have been established for each of the four codified governance roles, detailing their specific responsibilities, evidentiary checklists, source-by-source recommendations, and pending sign-off blocks:

| Governance Authority | Dedicated Review Document | Core Gating Mandate |
| :--- | :--- | :--- |
| **`DATA_CUSTODIAN`** | [`REVIEW_DATA_CUSTODIAN.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_DATA_CUSTODIAN.md) | Physical data lineage, transport manifests, UTF-8 losslessness, Unicode 15.1.0 NFC normalization, and sandbox isolation. |
| **`LEGAL_GOVERNANCE`** | [`REVIEW_LEGAL_GOVERNANCE.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_LEGAL_GOVERNANCE.md) | Copyright clearance, commercial use permissions, copyleft/ShareAlike derivative analysis, and attribution inventories. |
| **`SECURITY_PRIVACY`** | [`REVIEW_SECURITY_PRIVACY.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_SECURITY_PRIVACY.md) | Statutory privacy compliance (India DPDP Act 2023, GDPR), PII scrubbers, high-entropy secret scanning, and 13-gram benchmark decontamination. |
| **`CHIEF_ARCHITECT`** | [`REVIEW_CHIEF_ARCHITECT.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_CHIEF_ARCHITECT.md) | Transformer parameter invariants (16 layers, 512 hidden, 2048 context, 32,768 vocab, IDs 0–11), sequence tier stratification, and 10-category balance. |

*All signature hashes, reviewer identities, and approval dates in these four review documents remain strictly `PENDING` awaiting genuine human action.*

---

## 3. Task 4: Source Review & Technical vs Legal Distinction

A critical principle of IGRIS governance is distinguishing **technical verification** from **legal approval**:
- **Technical Verification**: Confirms that a dataset's format, script encoding, character set, compression characteristics, and data structure can be parsed losslessly by Candidate A and Candidate B.
- **Legal Approval**: Confirms that the dataset's intellectual property terms, copyright ownership, and commercial licenses permit use in commercial AI models without copyleft taint or statutory breach.

This distinction is codified across all 26 sources in [`DATASET_REVIEW_DECISION_REGISTER.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_REVIEW_DECISION_REGISTER.csv):
- **14 Sources**: Both **Technically Verified** and **Legally Cleared** (`VERIFIED` baseline).
- **7 Sources**: **Technically Verified**, but **Legally Encumbered** by ShareAlike (`CC-BY-SA 4.0`), GPL exceptions, or Common Crawl database rights (`REQUIRES HUMAN APPROVAL`).
- **4 Sources**: May be technically parseable, but are **Legally Incompatible** due to non-commercial clauses or unauthorized media scraping (`INCOMPATIBLE` — rejected and purged).
- **1 Source**: Technical structure known, but pass-through copyright and DPDP Act compliance are unverified (`UNVERIFIED` — withheld).

---

## 4. Task 2 & 3: Gap Resolution Research Summary

### 4.1 Category 5: Bengali & Gujarati Resolution
- **Deficit**: Category 5 (`DATASET_SPECIFICATION.md`) required Telugu, Kannada, Malayalam, Bengali, and Gujarati, but Bengali and Gujarati had 0 proposed candidate sources.
- **Resolution**: Researched and proposed `IndicCorp v2 (Bengali)` (~7.8 GB) and `IndicCorp v2 (Gujarati)` (~4.1 GB) under `CC0-1.0`.
- **Outcome**: Restores Category 5 to 100% full coverage across all 5 languages under a uniform, unencumbered public domain license.
- *Detailed Report*: [`BENGALI_GUJARATI_SOURCE_RESEARCH.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/BENGALI_GUJARATI_SOURCE_RESEARCH.md).

### 4.2 Category 9: Conversational Text Resolution
- **Deficit**: Both proposed sources (`DailyDialog` and `OpenSubtitles`) were disqualified due to Non-Commercial clauses and copyright infringement liabilities.
- **Resolution**: Researched and proposed a compliant three-source replacement suite:
  1. `OpenAssistant Conversations (OASST1)` (`Apache-2.0`)
  2. `Anthropic HH-RLHF` (`MIT`)
  3. `Project Gutenberg Theatrical Dramatic Dialogue` (`Public Domain`)
- **Outcome**: Eliminates copyright toxicity and non-commercial contamination, restoring Category 9 to full compliance.
- *Detailed Report*: [`CONVERSATIONAL_DATASET_RESEARCH.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CONVERSATIONAL_DATASET_RESEARCH.md).

---

## 5. Deliverables Summary

| Deliverable | Description | File Link |
| :--- | :--- | :--- |
| **Human Review Plan** | Master report detailing the governance framework, role separation, and gap resolutions | [IGRIS_3C5_HUMAN_REVIEW_PLAN.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_3C5_HUMAN_REVIEW_PLAN.md) |
| **Decision Register** | 26-source matrix distinguishing technical verification from legal approvals | [DATASET_REVIEW_DECISION_REGISTER.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_REVIEW_DECISION_REGISTER.csv) |
| **Bengali & Gujarati Research** | Deep-dive research resolving Category 5 sub-language representation under CC0 | [BENGALI_GUJARATI_SOURCE_RESEARCH.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/BENGALI_GUJARATI_SOURCE_RESEARCH.md) |
| **Conversational Research** | Deep-dive research resolving Category 9 deficit under Apache-2.0, MIT, and Public Domain | [CONVERSATIONAL_DATASET_RESEARCH.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CONVERSATIONAL_DATASET_RESEARCH.md) |
| **Gap Resolution Plan** | Strategic 4-stage protocol for transitioning research into authorized acquisition | [DATASET_GAP_RESOLUTION_PLAN.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_GAP_RESOLUTION_PLAN.md) |
| **Milestone Status Document** | Status tracking document summarizing gate locks and compliance states | [IGRIS_3C5_STATUS.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_3C5_STATUS.md) |
| **Data Custodian Review** | Dedicated review document for Data Custodian with checklists and source decisions | [REVIEW_DATA_CUSTODIAN.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_DATA_CUSTODIAN.md) |
| **Legal Governance Review** | Dedicated review document for Legal Governance with checklists and source decisions | [REVIEW_LEGAL_GOVERNANCE.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_LEGAL_GOVERNANCE.md) |
| **Security & Privacy Review** | Dedicated review document for Security & Privacy with checklists and source decisions | [REVIEW_SECURITY_PRIVACY.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_SECURITY_PRIVACY.md) |
| **Chief Architect Review** | Dedicated review document for Chief Architect with checklists and source decisions | [REVIEW_CHIEF_ARCHITECT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_CHIEF_ARCHITECT.md) |
| **Review Test Suite** | Automated unit tests covering all 3C.5 deliverables, schemas, and invariants | [tests/test_dataset_3c5_review.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_dataset_3c5_review.py) |

---

## 6. Task 6: Regression & Acceptance Verification

All test suites were executed within the active patch environment:

1. **Pytest Suite:** **236 passed** (including 7 new tests in `test_dataset_3c5_review.py`).
2. **Milestone 3B.57 Acceptance Audit:** **162 / 162 checks passed** (`run_acceptance_3b57.py`).
3. **Artifact Cryptographic Checksum Invariance:**
   - **Candidate A (`tokenizer.json`)**:
     `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (Exact match)
   - **Candidate B (`tokenizer.model`)**:
     `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (Exact match)

---

## 7. Final Governance State

- **Production Dataset Access:** `LOCKED` (Default-Deny Enforced)
- **Dataset Acquisition:** `NOT AUTHORIZED`
- **Tokenizer Training:** `NOT AUTHORIZED`
- **Approved Human Signatures Present:** `0 / 4` (Awaiting genuine human review)
