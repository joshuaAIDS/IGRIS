# IGRIS Milestone 3C.4 — Dataset Evidence & Human Review Preparation Report

**Project:** IGRIS (Decoder-Only Multilingual Transformer)  
**Patch Directory:** `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Milestone:** 3C.4 — Dataset Evidence & Human Review Preparation  
**Evaluation Candidates:** Candidate A (ByteLevel BPE, provisional front-runner) & Candidate B (SentencePiece Unigram)  
**Production Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

Milestone 3C.4 prepared an auditable evidence package for human review across all 26 candidate dataset sources proposed for IGRIS production tokenizer evaluation. All evidence was synthesized from official repository documentation, published license texts, and legal frameworks without downloading or ingesting any candidate dataset files.

In strict compliance with safety rules:
1. **Zero dataset contents were downloaded.**
2. **No private, production, quarantine, or approved dataset directories were accessed.**
3. **No production PII scanning was executed.**
4. **Neither tokenizer candidate was trained or retrained.**
5. **Candidate A and Candidate B synthetic artifacts remain byte-invariant.**
6. **Zero signatures, approvals, or legal waivers were fabricated.**
7. **Production access gate remains strictly `LOCKED`.**
8. **The four original authorization roles (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`) are preserved.**
9. **The ten canonical benchmark categories from `DATASET_SPECIFICATION.md` are strictly preserved.**
10. **No authorization schemas or Transformer architecture parameters were modified.**

---

## 2. Task 1 & 2: Source Evidence & Classification Review

All 26 sources were reassessed against official documentation, licensing terms, and intellectual property requirements:

| Classification | Count | Ratio | Description & Policy Action |
| :--- | :---: | :---: | :--- |
| **`VERIFIED`** | **14** | 53.8% | Unconditional commercial and model training rights confirmed by permissive or public domain licenses (`CC0-1.0`, `MIT`, `Apache-2.0`, `Unicode-DFS-2016`, `CC-BY-4.0`, `PSF-2.0`). |
| **`REQUIRES HUMAN APPROVAL`** | **7** | 26.9% | Requires formal human review and legal waivers due to ShareAlike copyleft clauses (`CC-BY-SA 4.0`), GPL documentation exceptions, or Common Crawl database curation (`ODC-By 1.0`). |
| **`INCOMPATIBLE`** | **4** | 15.4% | Violates commercial use requirements due to explicit Non-Commercial (`NC`) clauses or unauthorized scraping of copyrighted entertainment media. **Purged from acquisition.** |
| **`UNVERIFIED`** | **1** | 3.8% | Web crawl pass-through copyright and DPDP Act compliance unverified (`OSCAR 23.01`). |

### Deep-Dive Analysis of Critical Licensing & Provenance Nuances:

1. **Project Gutenberg Item-Level Copyright (`SRC-EN-01`)**:
   - *Evidence*: Core literary texts published before 1928 are in the US public domain. However, works may retain copyright in jurisdictions with author life+70 terms. Furthermore, raw downloads include trademarked introductory preambles and postambles under the "Project Gutenberg™ License".
   - *Technical Mitigation*: Mandate an automated preprocessing step to strip Gutenberg trademark headers/footers. Public domain text itself is completely unencumbered.
2. **The Stack v2 Per-File Licenses (`SRC-CD-01`)**:
   - *Evidence*: The BigCode/Software Heritage dataset provides a permissive subset filtered via ScanCode (MIT, Apache-2.0, BSD-2/3, ISC). However, repository-level licensing may conflict with per-file headers. Software Heritage maintains an active developer opt-out list.
   - *Technical Mitigation*: Mandate synchronization against the Software Heritage opt-out registry prior to ingestion; run automated secret scanning for API tokens and private keys.
3. **Common Crawl & Derived Web Corpora (`SRC-EN-03`, `SRC-ML-02`, `SRC-TM-03`)**:
   - *Evidence*: C4, mC4, and OSCAR are compiled under `ODC-By 1.0` covering database structure, but Common Crawl terms disclaim underlying web page copyrights. Ingestion relies on US fair use / EU DSM Article 3/4. Furthermore, uncurated web text contains significant PII risks under India's Digital Personal Data Protection (DPDP) Act 2023.
   - *Technical Mitigation*: Classify as `REQUIRES HUMAN APPROVAL` / `UNVERIFIED`; require mandatory automated regex PII scrubbing and human legal sign-off.
4. **Wikipedia CC-BY-SA Obligations (`SRC-TM-02`, `SRC-EN-02`, `SRC-HI-02`)**:
   - *Evidence*: Text is licensed under `CC-BY-SA 4.0`. While benchmark evaluation (calculating fertility and compression ratios) is non-derivative fair use, training a neural network or tokenizer vocabulary on CC-BY-SA text creates legal debate over whether model weights are "Adapted Material" requiring viral ShareAlike release.
   - *Technical Mitigation*: Classify as `REQUIRES HUMAN APPROVAL`. Legal Governance must sign off on whether model weights are encumbered.
5. **FLORES-200 Multilingual Benchmark (`SRC-ML-01`)**:
   - *Evidence*: Released by Meta under `CC-BY-SA 4.0`. Highly curated parallel sentences across 200 languages.
   - *Technical Mitigation*: Safe for benchmark evaluation; must be quarantined from pre-training sets to prevent ShareAlike contamination and benchmark leakage.
6. **HumanEval & MBPP Component Licenses (`SRC-CD-02`)**:
   - *Evidence*: HumanEval is `MIT`; MBPP is `Apache-2.0`. Commercial evaluation use is fully authorized.
   - *Technical Mitigation*: Must be held out from pre-training sets. Enforce 13-gram overlap filter (`test_detect_train_eval_leakage`) to guarantee zero benchmark contamination.
7. **Linux Kernel Documentation Licensing Exceptions (`SRC-TD-01`)**:
   - *Evidence*: Licensed under `GPL-2.0-only` with Linux Documentation Exception and dual GFDL tags in `Documentation/`. Copyleft terms require legal review for derivative model weights.
   - *Technical Mitigation*: Classify as `REQUIRES HUMAN APPROVAL`. Technical Documentation is alternatively supported by verified sources `SRC-TD-02` (IETF RFCs) and `SRC-TD-03` (Python PSF-2.0).

---

## 3. Task 3: Category Coverage Audit & Gap Analysis

The 10 approved benchmark categories defined in `DATASET_SPECIFICATION.md` were audited:

| ID | Approved Specification Category | Evaluated Coverage Status | Verified Sources Available | Critical Gaps Identified |
|:---:|:---|:---:|:---:|:---|
| 1 | **Tamil** | **FULL COVERAGE** | `SRC-TM-01` (`CC0-1.0`) | None. 3.8 GB unencumbered text. |
| 2 | **English** | **FULL COVERAGE** | `SRC-EN-01` (`Public Domain`) | None. 12 GB unencumbered literature. |
| 3 | **Tanglish** | **FULL COVERAGE** | `SRC-TG-01`, `SRC-TG-02` (`CC-BY-4.0`) | None. 60 MB peer-reviewed code-mixed text. |
| 4 | **Hindi** | **FULL COVERAGE** | `SRC-HI-01` (`CC0-1.0`) | None. 12.5 GB unencumbered prose. |
| 5 | **Other Indian Languages** | **PARTIAL COVERAGE** | `SRC-OI-01`, `SRC-OI-02`, `SRC-OI-03` | **CRITICAL GAP**: Telugu, Malayalam, and Kannada covered; **Bengali (`bn`) and Gujarati (`gu`) have ZERO candidate sources.** |
| 6 | **Multilingual Mixed Text** | **CONDITIONAL COVERAGE** | None (Both pending legal approval) | `SRC-ML-01` (CC-BY-SA) and `SRC-ML-02` (Crawl) require human sign-off. |
| 7 | **Programming Code** | **FULL COVERAGE** | `SRC-CD-01` (`Permissive`), `SRC-CD-02` | None. Full language and schema coverage. |
| 8 | **Technical Documentation** | **FULL COVERAGE** | `SRC-TD-02` (`RFC Trust`), `SRC-TD-03` (`PSF-2.0`) | None. Over 430 MB verified specs and manuals. |
| 9 | **Conversational Text** | **ZERO COMPLIANT COVERAGE** | **NONE** (Both rejected) | **CRITICAL DEFICIT**: `SRC-CV-01` has `NC` clause; `SRC-CV-02` has copyright liability. **0 compliant sources exist.** |
| 10 | **Emoji & Unicode Edge Cases** | **FULL COVERAGE** | `SRC-EM-01`, `SRC-EM-02` (`Unicode-DFS`) | None. Official Unicode 15.1.0 test suites. |

### Invariance & Gap Handling:
- **No Replacement Sources Invented**: In strict adherence to instructions, no unverified sources were fabricated to fill the gaps in Category 5 or Category 9.
- **Human Escalation**: The deficits in Bengali, Gujarati, and Conversational Text are formally submitted to the human review panel.

---

## 4. Task 4: Human Review Package Summary

A complete, un-signed human review package has been constructed in [`HUMAN_REVIEW_PACKAGE.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/HUMAN_REVIEW_PACKAGE.md) with dedicated sections for all four governance authorities:
1. **`DATA_CUSTODIAN`**: Transport integrity, SHA-256 pre-validation, UTF-8 losslessness, NFC normalization, and sandbox isolation.
2. **`LEGAL_GOVERNANCE`**: Copyright verification, commercial model training rights, ShareAlike/copyleft review, and attribution tracking.
3. **`SECURITY_PRIVACY`**: DPDP Act 2023 compliance, PII scrubbers, secret scanning, AI safety/toxicity, and 13-gram benchmark decontamination.
4. **`CHIEF_ARCHITECT`**: Transformer parameter budget, sequence tier stratification (Tiers 1–4), 10-category balance, and structural token isolation.

All approval fields, signature hashes, and review dates remain strictly **`PENDING`**.

---

## 5. Deliverables Register

| Deliverable | Description | File Link |
| :--- | :--- | :--- |
| **Evidence Report** | Master synthesis of evidence, coverage, and governance status | [IGRIS_3C4_EVIDENCE_REPORT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_3C4_EVIDENCE_REPORT.md) |
| **Source Evidence Register** | 19-column CSV cataloging provenance, URLs, training evidence, and PII risks | [DATASET_SOURCE_EVIDENCE_REGISTER.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_EVIDENCE_REGISTER.csv) |
| **License Evidence Matrix** | 12-column CSV auditing legal jurisdictions, commercial rights, copyleft, and verdicts | [DATASET_LICENSE_EVIDENCE_MATRIX.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_LICENSE_EVIDENCE_MATRIX.csv) |
| **Category Coverage Audit** | Detailed analysis of the 10 benchmark categories, Category 5 sub-languages, and deficits | [DATASET_CATEGORY_COVERAGE_AUDIT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_CATEGORY_COVERAGE_AUDIT.md) |
| **Human Review Package** | 4-role independent review templates with questions, evidence, and pending sign-offs | [HUMAN_REVIEW_PACKAGE.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/HUMAN_REVIEW_PACKAGE.md) |
| **Milestone Status Document** | Status tracking document summarizing gate locks and compliance states | [IGRIS_3C4_STATUS.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_3C4_STATUS.md) |
| **Evidence Unit Tests** | Automated test suite verifying 3C.4 deliverables, schemas, counts, and invariants | [tests/test_dataset_3c4_evidence.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_dataset_3c4_evidence.py) |

---

## 6. Task 6: Regression & Acceptance Verification

All test suites were executed within the active patch environment:

1. **Pytest Suite:** **229 passed** (including 6 new tests in `test_dataset_3c4_evidence.py`).
2. **Milestone 3B.57 Acceptance Audit:** **162 / 162 checks passed** (`run_acceptance_3b57.py`).
3. **Artifact Cryptographic Checksum Invariance:**
   - **Candidate A (`tokenizer.json`)**:
     `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (Exact match)
   - **Candidate B (`tokenizer.model`)**:
     `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (Exact match)

---

## 7. Final Governance State

- **Production Dataset Access:** `LOCKED`
- **Dataset Acquisition:** `NOT AUTHORIZED`
- **Production PII Scanning:** `NOT AUTHORIZED`
- **Tokenizer Training:** `NOT AUTHORIZED`
- **Approved Human Signatures Present:** `0 / 4` (Awaiting human review)
