# PHASE 23 — ENGLISH SOURCE LEGAL & TECHNICAL READINESS AUDIT
## Review of Public Domain, Permissive, Copyleft, and Prohibited English Datasets

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 23  
**Language Scope:** ENGLISH (`en`)  
**Status:** AUDITED & CATEGORIZED  

---

## 1. Executive Summary

Eleven candidate English datasets were reviewed across public domain literature, technical RFC standards, open-source programming documentation, permissive conversational AI datasets, and copyleft/prohibited corpora.

### Category Breakdown:
- **Eligible for Owner Review (6 sources):** `SRC-EN-01`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-03`, `SRC-CV-05`, `SRC-CV-06`.
- **Pending Legal Review (3 sources):** `SRC-EN-02`, `SRC-EN-03`, `SRC-TD-01`.
- **Rejected (2 sources):** `SRC-CV-01` (Non-commercial), `SRC-CV-04` (Prohibited alignment leakage).

---

## 2. In-Depth Review: Six Sources Eligible for Owner Review

### 1. `SRC-EN-01`: Project Gutenberg Open Archive
- **Content:** ~60,000 public domain books in English (literature, history, philosophy, sciences).
- **License:** Public Domain in the United States (all published before January 1, 1929).
- **Rights Clearance:** Copyright has completely expired. Free for commercial pretraining, derivation, and distribution.
- **Trademark Notice:** Stripping standard Project Gutenberg headers/footers (`*** START OF THE PROJECT GUTENBERG EBOOK ... ***`) is required if distributing derivative text without PG trademark agreement.
- **Status:** **`ELIGIBLE_FOR_OWNER_REVIEW`**.

### 2. `SRC-TD-02`: IETF RFC Archive (Text)
- **Content:** RFC 1 through RFC 9500+ (complete technical specifications of Internet protocols: TCP/IP, HTTP, TLS, DNS, BGP).
- **License:** IETF Trust Legal Provisions (TLP 5.0) / RFC 5378.
- **Rights Clearance:** Freely available for reproduction, implementation, and research. High-craft technical English prose with rigorous formal definitions.
- **Status:** **`ELIGIBLE_FOR_OWNER_REVIEW`**.

### 3. `SRC-TD-03`: Python Official Documentation
- **Content:** Python 3 standard documentation, tutorial, library reference, language reference, and HOWTO guides.
- **License:** Python Software Foundation License Version 2 (PSF-2.0).
- **Rights Clearance:** Permissive open-source documentation license. Allows commercial use, modification, and model training.
- **Status:** **`ELIGIBLE_FOR_OWNER_REVIEW`**.

### 4. `SRC-CV-03`: OpenAssistant Conversations (OASST1 - English Subset)
- **Content:** 161,443 human-generated assistant messages across 66,497 conversation trees.
- **License:** Apache License 2.0.
- **Rights Clearance:** Contributed by volunteer crowd-workers under explicit Apache-2.0 contributor agreement. Clean provenance; allows commercial pretraining.
- **Condition:** Must be filtered for `lang == 'en'` to adhere strictly to project language scope.
- **Status:** **`ELIGIBLE_FOR_OWNER_REVIEW`**.

### 5. `SRC-CV-05`: MultiWOZ 2.4 (Task Dialogue)
- **Content:** Over 10,000 human-human goal-oriented task dialogues in English across 7 domains.
- **License:** Apache License 2.0 (University of Cambridge).
- **Rights Clearance:** High-quality annotated dialogue created with paid crowd-workers under ethical research protocol.
- **Status:** **`ELIGIBLE_FOR_OWNER_REVIEW`**.

### 6. `SRC-CV-06`: Project Gutenberg Theatrical Dialogue
- **Content:** Extracted conversational dramatic dialogues from public domain plays (Shakespeare, Shaw, Wilde).
- **License:** Public Domain.
- **Rights Clearance:** Expired copyright; excellent conversational syntax.
- **Status:** **`ELIGIBLE_FOR_OWNER_REVIEW`**.

---

## 3. Review of Conditional and Rejected English Sources

- **`SRC-EN-02` (English Wikipedia Dump):** CC-BY-SA 4.0. Copyleft ShareAlike risk regarding trained weights. Status: **`PENDING_LEGAL_REVIEW`**.
- **`SRC-EN-03` (C4 Colossal Clean Crawled Corpus):** ODC-By 1.0. Common Crawl web crawl. Contains potential copyrighted web articles and ToS risks. Status: **`PENDING_LEGAL_REVIEW`**.
- **`SRC-TD-01` (Linux Kernel Documentation):** GPL-2.0-only. GPL copyleft contamination boundary must be verified by legal counsel. Status: **`PENDING_LEGAL_REVIEW`**.
- **`SRC-CV-01` (DailyDialog):** CC-BY-NC-SA 4.0. Non-commercial restriction prohibits production model use. Status: **`REJECTED`**.
- **`SRC-CV-04` (Anthropic HH-RLHF):** MIT License, but prohibited from pretraining to prevent evaluation alignment leakage and data contamination. Status: **`REJECTED`**.
