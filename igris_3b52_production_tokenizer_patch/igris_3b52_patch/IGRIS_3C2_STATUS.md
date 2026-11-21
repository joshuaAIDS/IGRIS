# IGRIS Milestone 3C.2 Status: Dataset Acquisition Planning

**Project**: IGRIS Decoder-Only Language Model  
**Patch Directory**: `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Milestone**: 3C.2 — Dataset Acquisition Planning  
**Date**: 2026-11-17  
**Gate Status**: **PRODUCTION ACCESS LOCKED — AWAITING HUMAN GOVERNANCE SIGN-OFF**  

---

## 1. Executive Summary

Milestone 3C.2 formalizes the dataset acquisition plan, public source catalog, license compatibility analysis, and risk register across all 10 approved evaluation categories.

In strict compliance with project governance directives:
- **Zero production datasets were downloaded, opened, or decompressed.**
- **Zero private training files or quarantine folders were accessed.**
- **Zero corpus ingestion or production PII scanning was executed.**
- **Zero tokenizer retraining or parameter adjustments were performed.**
- **Candidate A and Candidate B artifacts remain 100% bitwise unmodified.**
- **Production access remains strictly locked under the Default-Deny gate.**

---

## 2. Four-Tier Status Classification Ledger

In accordance with milestone instructions, every data source, license category, risk mitigation, and operational component is formally classified under one of the four mandated statuses:
- **`VERIFIED`**: Source documentation, official URLs, owners, and published licenses verified against upstream public releases.
- **`UNVERIFIED`**: Third-party scraped sources or secondary mirrors requiring primary provenance validation.
- **`REQUIRES HUMAN APPROVAL`**: Legal terms of service, commercial usage boundaries, PII thresholds, or architectural quotas requiring explicit human sign-off.
- **`NOT AVAILABLE`**: Proprietary, non-public, or unreleased datasets inaccessible without institutional agreements.

### 2.1 Category Source Verification Classifications

| Source ID | Dataset Name | Category | Primary License | Source Verification Status | Governance Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **`SRC-TM-01`** | IndicCorp v2 (Tamil) | Tamil | `CC0-1.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TM-02`** | Tamil Wikipedia Dump | Tamil | `CC-BY-SA-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TM-03`** | OSCAR 23.01 Tamil (Filtered) | Tamil | `ODC-By 1.0` | **`UNVERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-EN-01`** | Project Gutenberg Archive | English | Public Domain | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-EN-02`** | English Wikipedia Dump | English | `CC-BY-SA-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-EN-03`** | C4 (Clean Crawled Corpus) | English | `ODC-By 1.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TG-01`** | DravidianCodeMix (Ta-En) | Tanglish | `CC-BY-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TG-02`** | IndicGLUE Tanglish Sentiment | Tanglish | `CC-BY-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TG-03`** | Social Dravidian Tanglish (FIRE) | Tanglish | Research-Only | **`UNVERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-HI-01`** | IndicCorp v2 (Hindi) | Hindi | `CC0-1.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-HI-02`** | Hindi Wikipedia Dump | Hindi | `CC-BY-SA-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-HI-03`** | IIT Bombay En-Hi Parallel | Hindi | `CC-BY-NC-SA-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-OI-01`** | IndicCorp v2 (Telugu) | Other Indian | `CC0-1.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-OI-02`** | IndicCorp v2 (Malayalam) | Other Indian | `CC0-1.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-OI-03`** | IndicCorp v2 (Kannada) | Other Indian | `CC0-1.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-ML-01`** | FLORES-200 Multilingual | Multilingual mixed | `CC-BY-SA-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-ML-02`** | mC4 Multilingual Slice | Multilingual mixed | `ODC-By 1.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-CD-01`** | The Stack v2 (Permissive) | Code | `MIT` / `Apache` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-CD-02`** | HumanEval & MBPP | Code | `MIT` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TD-01`** | Linux Kernel Documentation | Technical docs | `GPL-2.0-with-exc` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TD-02`** | IETF RFC Archive | Technical docs | `IETF-Trust` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-TD-03`** | Python Official Docs | Technical docs | `PSF-2.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-CV-01`** | DailyDialog Dataset | Conversational | `CC-BY-NC-SA-4.0` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-CV-02`** | OpenSubtitles OPUS | Conversational | Non-Standard | **`UNVERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-EM-01`** | Unicode 15.1.0 UCD Tests | Unicode / Emoji | `Unicode-DFS-2016` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-EM-02`** | Unicode 15.1.0 Emoji Data | Unicode / Emoji | `Unicode-DFS-2016` | **`VERIFIED`** | **`REQUIRES HUMAN APPROVAL`** |
| **`SRC-PR-01`** | Private Unredacted Datasets | All Domains | Proprietary / NDA | **`NOT AVAILABLE`** | **`NOT AVAILABLE` (Excluded)** |

---

### 2.2 Operational and Governance Invariants

| Governance / Technical Invariant | Verification Status | Gate State |
| :--- | :---: | :---: |
| **10-Category Coverage Mapping** | **`VERIFIED`** | Ready for Review |
| **Public Source Catalog (`DATASET_SOURCE_CATALOG.csv`)** | **`VERIFIED`** | 26 sources cataloged |
| **License Comparison (`DATASET_LICENSE_COMPARISON.md`)** | **`VERIFIED`** | Legal tiers established |
| **Risk Register (`DATASET_ACQUISITION_RISK_REGISTER.md`)** | **`VERIFIED`** | 11 risks assessed & mitigated |
| **Pre-Ingestion Human Approval Requirement** | **`REQUIRES HUMAN APPROVAL`** | **`LOCKED`** |
| **Candidate A Artifact Checksum** | **`VERIFIED` (Unchanged)** | Bitwise Invariant |
| **Candidate B Artifact Checksum** | **`VERIFIED` (Unchanged)** | Bitwise Invariant |
| **Pytest Full Regression Suite** | **`VERIFIED` (214/214 passing)** | 100% Pass Rate |
| **3B.57 Acceptance Runner Audit** | **`VERIFIED` (162/162 passing)** | 100% Pass Rate |

---

## 3. Mandatory Governance Directive

**Production access remains strictly LOCKED.**  
No download commands, web scraping processes, or corpus extractions may occur until all four human authorities (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, and `CHIEF_ARCHITECT`) complete and execute the approval process detailed in `PRODUCTION_AUTHORIZATION_CHECKLIST.md`.
