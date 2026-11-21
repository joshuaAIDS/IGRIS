# PHASE 27 — COMPLETION REPORT: DATASET SOURCE LEGAL, LICENSING & RIGHTS REVIEW

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase:** Phase 27 — Dataset Source Legal, Licensing & Rights Review  
**Date:** 2026-11-20  
**Status:** COMPLETE — ALL REQUIREMENTS SATISFIED (`VERDICT A`)  
**Current Governance Status:** Production ingress **LOCKED**; Tokenizer training **UNAUTHORIZED**; Model pretraining **LOCKED**; Cloud spending **$0.00**.

---

## 1. Executive Summary

Phase 27 conducted an exhaustive, source-specific legal, copyright, licensing, terms of service, and privacy evidence audit across thirteen candidate datasets for the IGRIS multilingual transformer.

The approved language scope was strictly enforced: **Tamil**, **English**, and **Tanglish** only. All other languages were confirmed as `OUT_OF_SCOPE`.

### Key Achievements:
1. **Phase 26 Metric Resolution:** Executed independent recalculation of Phase 26 held-out test predictions; confirmed zero discrepancies in saved data files; identified and documented narrative discrepancies; issued [PHASE26_METRIC_CORRECTION_ADDENDUM.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE26_METRIC_CORRECTION_ADDENDUM.md).
2. **Source ID Reconciliation Codified:** Preserved historical mapping under `CORR-23B-01`: `SRC-CV-06` is permanently Project Gutenberg Theatrical Dialogue; `SRC-CV-07` is permanently WikiDialog English.
3. **Thirteen Candidates Audited Across 20 Parameters:** Completed deep forensic reviews across repository provenance, primary license evidence, compilation vs. underlying rights, statutory fair dealing (Indian Copyright Act § 52), platform scraping terms (YouTube ToS § II.A), and privacy regimes (GDPR / DPDP Act 2023).
4. **Zero Production Ingress Maintained:** No datasets were acquired, downloaded, or tokenized. Production gates remain 100% locked.

---

## 2. Source Audit Telemetry & Category Breakdown

```
+-------------------------------------------------------------------------+
|                  IGRIS PHASE 27 SOURCE AUDIT TELEMETRY                  |
+-------------------------------------------------------------------------+
|  Total Candidate Sources Audited:                           13          |
|  Historical Out-of-Scope Sources Accounted For:              8          |
|  Total Source Entries in Master Inventory:                  21          |
+-------------------------------------------------------------------------+
|  CLASSIFICATION BREAKDOWN (13 IN-SCOPE CANDIDATES):                     |
|  * VERIFIED_FOR_OWNER_REVIEW:                                6 (46.2%)  |
|      - SRC-EN-01 (Project Gutenberg English)                            |
|      - SRC-TD-02 (IETF RFC Repository)                                  |
|      - SRC-TD-03 (Python Official Documentation)                        |
|      - SRC-CV-03 (OpenAssistant OASST1 English)                         |
|      - SRC-CV-05 (MultiWOZ 2.4 English)                                 |
|      - SRC-CV-06 (Project Gutenberg Theatrical Dialogue)                |
|                                                                         |
|  * PENDING_LEGAL_REVIEW:                                     6 (46.2%)  |
|      - SRC-TM-01 (IndicCorp v2 Tamil)                                   |
|      - SRC-TM-02 (Tamil Wikipedia Dump)                                 |
|      - SRC-TM-03 (OSCAR 23.01 Tamil)                                    |
|      - SRC-TG-01 (DravidianCodeMix YouTube Comments)                    |
|      - SRC-TG-02 (IndicGLUE Tanglish Sentiment)                         |
|      - SRC-CV-07 (WikiDialog English Subset)                            |
|                                                                         |
|  * REJECTED:                                                 1 (7.7%)   |
|      - SRC-TG-03 (Spoken Tanglish Transcripts - NC/ND Clause)           |
|                                                                         |
|  * OUT_OF_SCOPE (Confirmed in Inventory):                    8          |
|      - SRC-HI-01, SRC-OI-01, SRC-OI-02, SRC-OI-03,                     |
|        SRC-OI-04, SRC-OI-05, SRC-CV-01, SRC-CV-04                       |
+-------------------------------------------------------------------------+
```

---

## 3. Primary Evidence and Legal Findings

### A. Tamil Sources (`SRC-TM-01`, `SRC-TM-02`, `SRC-TM-03`)
- **IndicCorp v2 Tamil (`SRC-TM-01`):** AI4Bharat dedicated the compilation under CC0-1.0. However, underlying articles scraped from Dinamalar, Dinamani, and Daily Thanthi remain copyrighted by news publishers. Indian Copyright Act Section 52(1)(a) has no explicit TDM exception. Outside Indian IP counsel opinion is mandatory prior to ingress.
- **Tamil Wikipedia (`SRC-TM-02`):** Crowdsourced under CC-BY-SA 4.0. The unresolved legal question is whether trained neural network weights constitute an "Adapted Material" (derivative work), potentially compelling the release of model weights under CC-BY-SA.
- **OSCAR 23.01 Tamil (`SRC-TM-03`):** ODC-By 1.0 covers only database rights; underlying web text is unreleased. Right to erasure under GDPR and DPDP Act 2023 presents unlearning compliance risks.

### B. English Sources (`SRC-EN-01`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-03`, `SRC-CV-05`, `SRC-CV-06`, `SRC-CV-07`)
- Six sources (`SRC-EN-01`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-03`, `SRC-CV-05`, `SRC-CV-06`) are verified with clean permissive or public domain licensing.
- Mandatory operational controls identified:
  - Project Gutenberg: Strip trademark headers and footers (§ 1.E.8); filter author death $\le 1955$.
  - IETF RFCs: Redact author business email addresses and phone numbers.
  - Python Docs: Screen code prompts against HumanEval/MBPP coding benchmarks.
  - OASST1: Filter `lang == 'en'`; scrub PII; quarantine validation split.
  - MultiWOZ 2.4: Quarantine `test.json` benchmark split; zero real PII verified.
- `SRC-CV-07` (WikiDialog) is classified as `PENDING_LEGAL_REVIEW` due to CC-BY-SA copyleft inheritance from Wikipedia.

### C. Tanglish Sources (`SRC-TG-01`, `SRC-TG-02`, `SRC-TG-03`)
- `SRC-TG-01` (DravidianCodeMix) contains genuine code-mixed comments, but scraping YouTube comments breaches YouTube Terms of Service § II.A. Classified as `PENDING_LEGAL_REVIEW`.
- `SRC-TG-02` (IndicGLUE) carries CC-BY-4.0 compilation, but test splits must be permanently quarantined.
- `SRC-TG-03` is published under non-commercial terms and is permanently `REJECTED`.

---

## 4. Deliverables Register (12 Files)

| # | Deliverable File | Format | Status | Description |
|---|---|:---:|:---:|---|
| 1 | `PHASE26_METRIC_CORRECTION_ADDENDUM.md` | Markdown | ✓ Completed | Forensic reconciliation of Phase 26 held-out test metrics and narrative error analysis |
| 2 | `PHASE27_SOURCE_INVENTORY.csv` | CSV | ✓ Completed | Master catalog of 21 sources (13 candidate + 8 out-of-scope/rejected) |
| 3 | `PHASE27_LICENSE_EVIDENCE_REGISTER.csv` | CSV | ✓ Completed | 20-point license evidence matrix across SPDX, versions, and permissions |
| 4 | `PHASE27_COPYRIGHT_RISK_REGISTER.csv` | CSV | ✓ Completed | Underlying provenance, third-party risk, fair dealing, and weight risk |
| 5 | `PHASE27_PRIVACY_RISK_REGISTER.csv` | CSV | ✓ Completed | PII categories, GDPR/DPDP compliance, right to erasure, sanitization needs |
| 6 | `PHASE27_TAMIL_SOURCE_AUDIT.md` | Markdown | ✓ Completed | Deep forensic audit of IndicCorp v2, Tamil Wikipedia, and OSCAR |
| 7 | `PHASE27_ENGLISH_SOURCE_AUDIT.md` | Markdown | ✓ Completed | Deep forensic audit of Gutenberg, IETF, Python, OASST1, MultiWOZ, WikiDialog |
| 8 | `PHASE27_TANGLISH_SOURCE_AUDIT.md` | Markdown | ✓ Completed | Deep forensic audit of DravidianCodeMix, IndicGLUE, and academic corpora |
| 9 | `PHASE27_LEGAL_REVIEW_REQUIRED.csv` | CSV | ✓ Completed | 6 specific statutory and contractual questions for outside legal counsel |
| 10 | `PHASE27_OWNER_REVIEW_SUMMARY.md` | Markdown | ✓ Completed | Structured owner decision package with confirmed facts vs. legal interpretations |
| 11 | `PHASE27_COMPLETION_REPORT.md` | Markdown | ✓ Completed | Master completion report and audit declaration |
| 12 | `verify_phase27.py` | Python | ✓ Completed | Automated 30-check deterministic verification script |

---

## 5. Governance & Invariant Verification

```
+-------------------------------------------------------------------------+
|                  IGRIS GOVERNANCE CONTROL GATES (PHASE 27)              |
+-------------------------------------------------------------------------+
|  Production Dataset Downloads:      NOT AUTHORIZED                      |
|  Production Ingress Gate:           LOCKED                              |
|  Dataset Quarantine Ingress:        LOCKED                              |
|  Tokenizer Training:               NOT AUTHORIZED                      |
|  Model Pretraining:                LOCKED                              |
|  Cloud Provisioning:                NOT AUTHORIZED                      |
|  Cloud Spending:                    $0.00                               |
|  Candidate A Hash:                  ac7e18b13973450b43bfff18609a...     |
|  Candidate B Hash:                  d3a3431e07c87ecce863647202dd...     |
|  Vocabulary Size:                   32,768 (Frozen)                     |
|  Structural Tokens:                 IDs 0–11 (Pinned)                   |
+-------------------------------------------------------------------------+
```

---

## 6. Verdict

```
+-------------------------------------------------------------------------+
|                     IGRIS PHASE 27 FINAL VERDICT                        |
|                                                                         |
|  VERDICT A: PHASE 27 LEGAL & RIGHTS AUDIT COMPLETE AND SIGNED OFF       |
|                                                                         |
|  - 12/12 Deliverables Generated and Synchronized                        |
|  - Phase 26 Metric Addendum Formally Recorded                           |
|  - All 13 Candidate Datasets Audited Across 20 Legal Parameters         |
|  - Confirmed Facts Strictly Separated from Legal Interpretations        |
|  - Zero Sources Marked APPROVED_FOR_ACQUISITION                         |
|  - All Production Ingress and Pretraining Gates Remain LOCKED           |
|                                                                         |
|  STOPPING CONDITION SATISFIED: AWAITING SOLO_DEVELOPER_OWNER_REVIEW.    |
|  PHASE 28 WILL NOT COMMENCE WITHOUT EXPLICIT OWNER AUTHORIZATION.       |
+-------------------------------------------------------------------------+
```

> **LEGAL NOTICE:** This audit constitutes technical, factual, and risk-analytical documentation prepared for internal project governance under the `SOLO_DEVELOPER_OWNER_REVIEW` operating model. It does not constitute formal legal advice, an attorney-client communication, or an official legal opinion. No dataset acquisition, download, or training authorization is granted.
