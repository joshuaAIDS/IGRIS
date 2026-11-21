# PHASE 27 — ENGLISH SOURCE LEGAL & RIGHTS AUDIT
## Comprehensive Evidence Audit for Seven English Candidates Across Public Domain, Permissive, and Copyleft Regimes

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Phase:** Phase 27  
**Language Scope:** ENGLISH (`en`)  
**Status:** AUDITED & CATEGORIZED (Zero Production Ingress Authorized)

---

## 1. Executive Summary

English provides foundational syntactic depth, technical vocabulary, and conversational fluency for IGRIS. In accordance with the historical source reconciliation (`CORR-23B-01`), seven candidate English sources were audited across primary license evidence, copyright ownership, commercial pretraining eligibility, trademark restrictions, PII exposure, and benchmark contamination.

### Classification Overview:
- **Verified for Owner Review (6 sources):**
  1. `SRC-EN-01`: Project Gutenberg English Subset (Public Domain US; Life+70 filter; trademark strip).
  2. `SRC-TD-02`: IETF RFC Repository (Permissive IETF TLP 5.0 / RFC 5378; email regex scrub).
  3. `SRC-TD-03`: Python Official Documentation (Permissive PSF-2.0; docstring benchmark screen).
  4. `SRC-CV-03`: OpenAssistant OASST1 English (Permissive Apache-2.0; PII scrub; train split only).
  5. `SRC-CV-05`: MultiWOZ 2.4 English (Permissive Apache-2.0; zero real PII; test.json quarantine).
  6. `SRC-CV-06`: Project Gutenberg Theatrical Dialogue (Public Domain dramatic plays; trademark strip).
- **Pending Legal Review (1 source):**
  7. `SRC-CV-07`: WikiDialog English Subset (CC-BY-SA 3.0/4.0 derivative of Wikipedia; ShareAlike weight risk).

---

## 2. In-Depth Audit: Public Domain Sources (`SRC-EN-01` & `SRC-CV-06`)

### A. `SRC-EN-01`: Project Gutenberg English Subset
- **Publisher:** Project Gutenberg Literary Archive Foundation (PGLAF), Salt Lake City, UT.
- **Repository:** `https://www.gutenberg.org/` / `rsync://aleph.gutenberg.org::gutenberg`
- **Pinned Catalog Snapshot:** 2024-01-01 (~50,000 cleared English titles; ~4.2 GB text).
- **Statutory Copyright Basis:**
  - Works published before January 1, 1929 have entered the public domain in the United States pursuant to 17 U.S.C. § 304.
  - Copyright has completely expired; all reproduction, derivative, and commercial pretraining rights are unencumbered.
- **International Life+70 Rule Reconciliation:**
  - In jurisdictions adhering to the Berne Convention "Life of the Author + 70 years" term (e.g. EU, UK), works by authors dying between 1929 and 1955 could theoretically retain copyright unless the "Rule of the Shorter Term" applies.
  - **Mitigation:** A strict metadata filter excluding any author with death date $> 1955$ ensures 100% worldwide public domain status (2026 - 70 = 1956).
- **Mandatory Trademark Requirement (PGLAF License § 1.E.8):**
  - Distributing modified or derivative texts without paying PGLAF royalties requires complete removal of the "Project Gutenberg" trademark and all preamble/postamble header text (`*** START OF THE PROJECT GUTENBERG EBOOK ... ***`).
- **PII & Privacy Risk:** Zero (all authors and historical subjects deceased $>70$ years).
- **Status:** **`VERIFIED_FOR_OWNER_REVIEW`**.

### B. `SRC-CV-06`: Project Gutenberg Theatrical Dialogue
- **Historical Reconciliation Note:** Reaffirmed as Project Gutenberg Theatrical Dialogue pursuant to `CORR-23B-01` (WikiDialog reassigned to `SRC-CV-07`).
- **Content:** Classical dramatic dialogue extracted from pre-1929 theatrical plays (Shakespeare, Wilde, Shaw, Synge).
- **Copyright Analysis:**
  - William Shakespeare (d. 1616), Oscar Wilde (d. 1900), J.M. Synge (d. 1909) are in the public domain globally.
  - George Bernard Shaw (d. 1950): Works published pre-1929 entered the public domain in Life+70 nations on January 1, 2021.
- **Trademark Compliance:** Same mandatory PGLAF header stripping applies.
- **Status:** **`VERIFIED_FOR_OWNER_REVIEW`**.

---

## 3. In-Depth Audit: Permissive Technical Documentation (`SRC-TD-02` & `SRC-TD-03`)

### A. `SRC-TD-02`: IETF RFC Repository
- **Publisher:** Internet Engineering Task Force (IETF) / RFC Editor.
- **Repository:** `https://www.rfc-editor.org/` / `https://github.com/ietf/rfc-editor`
- **Pinned Snapshot:** RFC 1 through RFC 9500+ (Snapshot 2024-Q3, `rfc*.txt`).
- **License Framework:** IETF Trust Legal Provisions (TLP 5.0 Section 3.c) / RFC 5378 / BCP 78.
- **Rights & Permissions:**
  - Perpetual, worldwide, non-exclusive license to copy, publish, extract, and distribute RFC specifications.
  - Commercial model pretraining is fully unencumbered.
  - **Restriction:** Derived texts cannot be published *as official IETF RFC standards* (to protect the integrity of Internet specifications). Model training extracts statistical parameters and does not publish RFC specifications.
- **PII Exposure & Sanitization:**
  - RFC footers contain real business email addresses and corporate affiliations of Internet engineers.
  - **Mandatory Control:** Automated regex pipeline scrubbing all email patterns (`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`) prior to tokenization.
- **Status:** **`VERIFIED_FOR_OWNER_REVIEW`**.

### B. `SRC-TD-03`: Python Official Documentation
- **Publisher:** Python Software Foundation (PSF), Beaverton, OR.
- **Repository:** `https://github.com/python/cpython` (Doc/) / `https://docs.python.org/3/`
- **Pinned Version:** Python 3.12.7 documentation release (`v3.12.7`).
- **License:** Python Software Foundation License Version 2 (`PSF-2.0`).
- **Permissive Rights:**
  - Standard OSI-approved permissive license granting unrestricted rights to reproduce, make derivative works, and distribute.
  - Attribution: Retain brief PSF copyright notice in training metadata.
- **Benchmark Contamination Mitigation:**
  - Python docstrings contain coding examples that could overlap with HumanEval or MBPP prompts.
  - **Mandatory Control:** Docstring code prompts screened against standard coding evaluation benchmarks.
- **Status:** **`VERIFIED_FOR_OWNER_REVIEW`**.

---

## 4. In-Depth Audit: Permissive Conversational Corpora (`SRC-CV-03` & `SRC-CV-05`)

### A. `SRC-CV-03`: OpenAssistant Conversations (OASST1 - English Subset)
- **Publisher:** LAION / OpenAssistant Project (Köpf et al., 2023).
- **Repository:** `https://huggingface.co/datasets/OpenAssistant/oasst1`
- **Pinned Revision:** Commit `289ed0f90ff8eb4b5b7c0fdbab26a29d5b0d02ea` (`2023-04-12_oasst_ready.trees.jsonl.gz`).
- **License:** Apache License 2.0.
- **Contributor Governance:**
  - Crowd-workers accepted contributor agreements assigning Apache-2.0 rights.
  - Clean provenance; commercial pretraining permitted with Apache attribution notice.
- **Mandatory Pipeline Invariants:**
  1. *Language Filtering:* Filter strictly for `lang == 'en'` to respect the IGRIS 3-language boundary.
  2. *Split Isolation:* Ingest ONLY `split == 'train'`. Permanently quarantine the validation split.
  3. *PII Scrubbing:* Automated regex and NER pipeline to redact personal names, usernames, and contact info.
- **Status:** **`VERIFIED_FOR_OWNER_REVIEW`**.

### B. `SRC-CV-05`: MultiWOZ 2.4 English Subset
- **Publisher:** Dialogue Systems Group, University of Cambridge (Budzianowski et al., EMNLP 2018; Ye et al., 2021).
- **Repository:** `https://github.com/smartyfh/MultiWOZ2.4`
- **Pinned Revision:** Commit `89622d1` (`data.json` / `train.jsonl`).
- **License:** Apache License 2.0 (University of Cambridge).
- **Privacy Assessment:** **Zero Real PII.** All dialogue entities (hotels, restaurants, phone numbers, postcodes) are drawn from a synthetic mock database of Cambridge services.
- **Evaluation Benchmark Isolation:**
  - MultiWOZ `test.json` is the standard international benchmark for Dialogue State Tracking (DST).
  - **Mandatory Control:** Strict quarantine of `test.json`. Ingestion restricted to `train.jsonl` (8,438 dialogues).
- **Status:** **`VERIFIED_FOR_OWNER_REVIEW`**.

---

## 5. In-Depth Audit: Copyleft Conversational Corpus (`SRC-CV-07`: WikiDialog)

- **Dataset Identity:** WikiDialog English Subset (Google Research, Dai et al., ACL 2022).
- **Repository:** `https://github.com/google-research-datasets/wiki-dialog` / `google/wikidialog-100k`
- **Permanent Source ID:** `SRC-CV-07` (Codified under `CORR-23B-01`).
- **Declared License:** Creative Commons Attribution-ShareAlike 3.0 / 4.0 (`CC-BY-SA 3.0/4.0`).
- **The Derivative Work Copyleft Chain:**
  - WikiDialog dialogs were synthetically generated by inpainting Wikipedia passages using neural dialog models.
  - Legally, WikiDialog is an **Adapted Material (derivative work)** of English Wikipedia articles.
  - It directly inherits the viral ShareAlike obligation of Wikipedia under CC-BY-SA.
- **Model Weight Risk:**
  - Pretraining on WikiDialog exposes IGRIS to the same unresolved ShareAlike risk as `SRC-TM-02` (Tamil Wikipedia): whether foundation model weights constitute Adapted Material subject to mandatory CC-BY-SA release.
- **Benchmark Contamination:** Severe overlap with Wikipedia-derived QA benchmarks (Natural Questions, TriviaQA, SQuAD 2.0).
- **Status:** **`PENDING_LEGAL_REVIEW`**.

---

## 6. English Source Audit Summary Matrix

| Source ID | Source Name | Primary License | Permissive Commercial | PII Risk | Eval Leakage Risk | Final Evidence Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`SRC-EN-01`** | Project Gutenberg English | Public Domain | YES | None | None | **`VERIFIED_FOR_OWNER_REVIEW`** |
| **`SRC-TD-02`** | IETF RFC Repository | IETF TLP 5.0 | YES | Low (Scrubbed) | None | **`VERIFIED_FOR_OWNER_REVIEW`** |
| **`SRC-TD-03`** | Python Official Docs | PSF-2.0 | YES | None | Coding Benchmark | **`VERIFIED_FOR_OWNER_REVIEW`** |
| **`SRC-CV-03`** | OpenAssistant OASST1 (En) | Apache-2.0 | YES | Medium (Scrubbed) | Val Split | **`VERIFIED_FOR_OWNER_REVIEW`** |
| **`SRC-CV-05`** | MultiWOZ 2.4 (En) | Apache-2.0 | YES | None (Synthetic) | Test Split | **`VERIFIED_FOR_OWNER_REVIEW`** |
| **`SRC-CV-06`** | Gutenberg Theatrical Dialogue | Public Domain | YES | None | None | **`VERIFIED_FOR_OWNER_REVIEW`** |
| **`SRC-CV-07`** | WikiDialog English Subset | CC-BY-SA 4.0 | Conditional | Low | High (QA Evals) | **`PENDING_LEGAL_REVIEW`** |
