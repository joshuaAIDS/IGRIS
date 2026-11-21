# IGRIS Milestone 3C.9 — Human Approval Package & Authorization Readiness Audit Report

**Project:** IGRIS (Decoder-Only Multilingual Transformer)  
**Active Patch:** `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Milestone:** 3C.9 — Human Approval Package & Authorization Readiness Audit  
**Date:** 2026-11-17  
**Access Control Gate:** `LOCKED` (Default-Deny Enforced)  
**Dataset Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary

Milestone 3C.9 establishes the finalized, tamper-evident dataset governance package and executes an authorization readiness audit for the IGRIS multilingual tokenizer evaluation project.

In strict compliance with all milestone constraints and safety protocols:
1. **Zero Acquisition & Zero Production Access**: No external datasets were downloaded, opened, read, staged, or ingested. No PII scans or model training routines were executed.
2. **Candidate Invariants Preserved**: Candidate A (`tokenizer.json`) and Candidate B (`tokenizer.model`) SHA-256 hashes remain perfectly identical to baselines.
3. **Legal Correction Freeze**:
   - Reaffirmed Section 22 of the Indian Copyright Act, 1957 (**Life + 60**, author death $\le 1965$ in 2026).
   - Reaffirmed European/UK **Life + 70** directives (author death $\le 1955$ in 2026).
   - Corrected Section 57 moral rights language to avoid unsupported blanket claims of perpetual rights post-copyright expiry, while preserving attribution integrity as an essential governance mandate.
   - Enforced 4-pillar item-level public domain review for Project Gutenberg and rejected claims of zero global copyright risk.
4. **Four Human Review Packages**: Authored separate, comprehensive review documents for `DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, and `CHIEF_ARCHITECT`, as well as the master dossier `HUMAN_REVIEW_PACKAGE_V2.md`. All reviewer fields and signature lines remain authentic, explicit, and blank (`PENDING`).
5. **32-Source Review Matrix**: Created `SOURCE_HUMAN_REVIEW_MATRIX.csv` indexing all 32 sources with their primary status, license class, commercial evidence, pipeline eligibilities, privacy risk, and approval state (`PENDING`).
6. **Seven Decoupled Governance Gates & Independence Axiom**: Codified `PIPELINE_GATE_AUDIT.md`, enforcing that permission for one pipeline gate confers zero rights on any other gate. Supervised Fine-Tuning (SFT), alignment evaluation, and safety evaluation remain **`NOT AUTHORIZED` (100% locked)**.
7. **Comprehensive Governance Security Testing**: Implemented and executed automated security tests covering missing signatures, invalid roles, expired approvals, revoked approvals, record tampering, conflicting decisions, unauthorized access, and default-deny behavior.

---

## 2. Task 1: Legal Correction Freeze & Section 57 Refinement

### 2.1 Indian Statutory Framework (Section 22 Life+60)
The canonical calculation under Section 22 of The Copyright Act, 1957 is frozen:
$$\text{Indian Public Domain Entry Date} = \text{January 1, } (Y_{\text{death}} + 61)$$
For calendar year 2026, the threshold is **author death on or before December 31, 1965 ($\le 1965$)**. Authors dying in 1966 or later remain protected under Indian copyright throughout 2026. The 1955 threshold applies strictly to jurisdictions with **Life + 70** rules (United Kingdom and European Union).

### 2.2 Refinement of Section 57 Moral Rights Language
Milestone 3C.9 explicitly refines the analysis of Section 57 (Author's Special Rights) to eliminate unsupported blanket claims:
- **Statutory Scope**: Section 57(1) guarantees that moral rights (paternity and integrity) survive the assignment or licensing of copyright during the author's life. Under Section 57(2) (as amended by Act 27 of 2012), legal representatives may exercise these rights post-mortem.
- **Duration Boundary**: The landmark ruling in *Amar Nath Sehgal v. Union of India* (2005) established the pre-eminence of moral rights over economic transfer, but the litigation occurred during active copyright subsistence. The Indian statute does not provide for perpetual moral rights extending indefinitely into eternity post-copyright expiry (unlike French *droit moral perpétuel*).
- **Governance Mandate**: While blanket perpetual claims post-expiry lack statutory or appellate consensus in India, IGRIS governance mandates attribution preservation and protection against derogatory distortion as an ethical best practice.

---

## 3. Task 2: Four Human Review Packages (Version 2.0)

Governance authority is distributed across four independent human review packages covering all 32 candidate sources:

1. **[`REVIEW_DATA_CUSTODIAN_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_DATA_CUSTODIAN_V2.md)**:
   - Focus: Cryptographic pre-validation, SHA-256 manifests, UTF-8 losslessness, Unicode 15.1.0 NFC normalization, sandbox isolation (`quarantine/`), Project Gutenberg header/trademark de-branding, and prompt-only staging of `SRC-CV-04`.
   - Decision State: **`PENDING HUMAN REVIEW`** (Unsigned).
2. **[`REVIEW_LEGAL_GOVERNANCE_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_LEGAL_GOVERNANCE_V2.md)**:
   - Focus: Published licenses, public evidence URLs, commercial rights, CC-BY-SA 4.0 copyleft risks, Section 22 Life+60 compliance, 4-pillar Gutenberg item clearances, and enforcement that CC-BY/Apache-2.0 are not treated as unrestricted.
   - Decision State: **`PENDING HUMAN REVIEW`** (Unsigned).
3. **[`REVIEW_SECURITY_PRIVACY_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_SECURITY_PRIVACY_V2.md)**:
   - Focus: PII screening (Aadhaar, PAN, SSN, emails), web crawl safety (OSCAR, C4, mC4), secrets filtering in code (`SRC-CD-01`), and mandatory quarantine of adversarial red-team datasets (`SRC-CV-04`).
   - Decision State: **`PENDING HUMAN REVIEW`** (Unsigned).
4. **[`REVIEW_CHIEF_ARCHITECT_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_CHIEF_ARCHITECT_V2.md)**:
   - Focus: Model architecture (2048 context, 512 hidden, 16 layers, 8 Q-heads, 4 KV-heads, 32,768 vocabulary, 12 pinned structural tokens at IDs 0–11), Candidate A & B hash invariance, benchmark contamination guards (`SRC-CD-02`, `SRC-ML-01`), and vocabulary poisoning guards.
   - Decision State: **`PENDING HUMAN REVIEW`** (Unsigned).

Master Dossier: [`HUMAN_REVIEW_PACKAGE_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/HUMAN_REVIEW_PACKAGE_V2.md).

---

## 4. Task 3: 32-Source Human Review Matrix

[`SOURCE_HUMAN_REVIEW_MATRIX.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/SOURCE_HUMAN_REVIEW_MATRIX.csv) tabulates the review status across all 32 sources:
- **Primary Status Breakdown**: 20 Verified | 7 Conditional | 1 Unverified (`SRC-TM-03`) | 4 Incompatible (`SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02`).
- **License Class Breakdown**: 7 CC0 | 2 CC-BY | 2 Apache-2.0 | 1 MIT | 2 Public Domain | 4 ShareAlike | 1 GPL | 3 ODC-By | 10 Other/Unknown.
- **Commercial Evidence**: 20 Confirmed Allowed | 7 Requires Legal Review | 3 Prohibited NC | 2 Unverified.
- **Required Reviewers**: All 4 roles (`DATA_CUSTODIAN; LEGAL_GOVERNANCE; SECURITY_PRIVACY; CHIEF_ARCHITECT`).
- **Final Approval State**: **`PENDING` across all 32 sources (100%)**.

---

## 5. Task 4: Pipeline Gate Separation & The Independence Axiom

In [`PIPELINE_GATE_AUDIT.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PIPELINE_GATE_AUDIT.md), the Independence Axiom is enforced across all seven gates:

```
+----------------------------------------------------------------------------------------------------+
|                         THE SEVEN DECOUPLED GOVERNANCE GATES                                       |
+----------------------------------------------------------------------------------------------------+
Gate 1: Dataset Acquisition --------> State: NOT AUTHORIZED (No downloads permitted)
Gate 2: Production Data Access -----> State: LOCKED (Default-deny filesystem barrier)
Gate 3: Tokenizer Vocab Training ---> State: PENDING REVIEW (18 Eligible, 8 Cond, 2 Prohib, 4 Rej)
Gate 4: Tokenizer Evaluation -------> State: PENDING REVIEW (28 Eligible, 4 Rej; Isolated CV-04)
Gate 5: Supervised Fine-Tuning -----> State: NOT AUTHORIZED (0 / 32 Allowed; 100% Locked)
Gate 6: Alignment Evaluation -------> State: NOT AUTHORIZED (0 / 32 Allowed; 100% Locked)
Gate 7: Safety Evaluation ----------> State: NOT AUTHORIZED (0 / 32 Allowed; 100% Locked)
```

**Boundary Rule**: Authorizing tokenizer evaluation confers zero permission for vocabulary training, pre-training, or fine-tuning. Downstream SFT and alignment require separate, future governance authorizations.

---

## 6. Task 5: Governance Security Validation

In [`tests/test_dataset_3c9_governance.py`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_dataset_3c9_governance.py), eight rigorous security scenarios were tested:

1. **Missing Signatures**: Verifies that when fewer than 4 roles have signed, the access gate remains `LOCKED` and state transitions to `APPROVED` are refused.
2. **Invalid Reviewer Roles**: Verifies that approval records signed by un-codified roles (e.g. `AI_ETHICS_SAFETY`, `TECHNICAL_LEAD`, or arbitrary strings) fail validation.
3. **Expired Approvals**: Verifies that signatures exceeding the validity window (90 days for custody/security, 180 days for legal/architecture) automatically trigger an expired state and deny access.
4. **Revoked Approvals**: Verifies that a record marked `REVOKED` immediately terminates access regardless of previous approvals.
5. **Tampered Records**: Verifies that altering any metadata field (such as changing a checksum, license name, or approval status) after cryptographic hashing results in an immediate integrity violation.
6. **Conflicting Decisions**: Verifies that if 3 roles vote `APPROVED` and 1 role votes `REJECTED`, the consensus engine resolves to `REJECTED` under the 4-of-4 quorum rule.
7. **Unauthorized Access Attempts**: Verifies that attempting to read or stage an unapproved dataset raises `DatasetAccessDeniedError`.
8. **Default-Deny Behavior**: Verifies that any query without explicit, active, four-signature approval returns `DENIED`.

---

## 7. Task 7: Technical Regression & Candidate Invariants

1. **Pytest Regression**:
   - `tests/test_dataset_3c9_governance.py`: **9/9 passed**.
   - Full test suite: **266/266 passed** in 6.18s.
2. **Acceptance Runner**:
   - `scripts/run_acceptance_3b57.py`: **162/162 checks passed**.
3. **Candidate Tokenizer Invariants (100% Unchanged)**:
   - Candidate A (`tokenizer.json`): `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
   - Candidate B (`tokenizer.model`): `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`

---

## 8. Unresolved Governance Issues for Human Sign-Off

The following items are formally surfaced for human determination:
1. **ShareAlike Risk Clearance**: `LEGAL_GOVERNANCE` must evaluate whether the release of model weights trained on CC-BY-SA 4.0 corpora (Wikipedia, FLORES-200) constitutes a derivative work requiring ShareAlike weight distribution.
2. **Web Crawl Provenance Audits**: `DATA_CUSTODIAN` and `SECURITY_PRIVACY` must audit the extraction and filtering scripts for OSCAR Tamil (`SRC-TM-03`) and Common Crawl extracts (`SRC-EN-03`, `SRC-ML-02`) before any download.
3. **Project Gutenberg EBook Lists**: Data Custodian and Legal Officer must execute the item-level checklist on the specific EBook IDs proposed for `SRC-EN-01` and `SRC-CV-06`.
4. **Linux Kernel GPL Exemption**: Legal Officer must confirm that using Linux kernel documentation solely for vocabulary learning falls within permitted documentation fair use without triggering reciprocal GPL licensing.

---

## 9. Final Governance Gate Record

```
+====================================================================================================+
|                                  IGRIS FINAL GOVERNANCE GATE STATE                                 |
+====================================================================================================+
Production Data Access:             LOCKED (Default-Deny Enforced)
Dataset Acquisition:                NOT AUTHORIZED (Zero Network Ingestion)
Human Approvals:                    PENDING (All 4 Packages Unsigned & Prepared)
Supervised Fine-Tuning (SFT):       NOT AUTHORIZED (0 / 32 Sources)
Alignment Evaluation:               NOT AUTHORIZED (0 / 32 Sources)
Safety Evaluation:                  NOT AUTHORIZED (0 / 32 Sources)
Candidate A Hash:                   ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561 (INVARIANT)
Candidate B Hash:                   d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888 (INVARIANT)
====================================================================================================+
```
