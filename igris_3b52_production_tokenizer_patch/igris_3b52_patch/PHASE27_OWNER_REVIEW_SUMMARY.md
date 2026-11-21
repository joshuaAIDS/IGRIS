# PHASE 27 — OWNER REVIEW SUMMARY & GOVERNANCE PACKAGE

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-20  
**Phase:** Phase 27  
**Language Scope:** TAMIL, ENGLISH, TANGLISH ONLY (All other languages OUT_OF_SCOPE)  
**Governance Invariant:** All Production Gates Remain **LOCKED** ($0.00 spent, 0 bytes acquired)

---

## 1. Purpose of this Review Package

This document presents a structured, objective summary of the legal, licensing, copyright, terms of service, and privacy evidence collected across thirteen candidate datasets.

Under the `SOLO_DEVELOPER_OWNER_REVIEW` operating model, **the sole developer / project owner holds exclusive authority** to authorize dataset ingress, commission outside legal counsel, or reject candidate sources.

> [!IMPORTANT]
> **No legal opinions are fabricated.** Confirmed facts are strictly separated from legal interpretations and unresolved jurisprudential questions. No source is marked `APPROVED_FOR_ACQUISITION`.

---

## 2. Master Candidate Classification Matrix

| Source ID | Candidate Name | Language | Primary License | Evidence Status | Commercial Viability | Mandatory Controls Required if Authorized |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`SRC-EN-01`** | Project Gutenberg English | ENGLISH | Public Domain (US) | **`VERIFIED_FOR_OWNER_REVIEW`** | Unrestricted | Strip PGLAF trademark headers; filter author death $\le 1955$ |
| **`SRC-TD-02`** | IETF RFC Repository | ENGLISH | IETF TLP 5.0 | **`VERIFIED_FOR_OWNER_REVIEW`** | Permissive | Automated regex scrubbing of author emails and phone numbers |
| **`SRC-TD-03`** | Python Official Docs | ENGLISH | PSF-2.0 | **`VERIFIED_FOR_OWNER_REVIEW`** | Permissive | Screen docstring code prompts against HumanEval/MBPP benchmarks |
| **`SRC-CV-03`** | OpenAssistant OASST1 (En) | ENGLISH | Apache-2.0 | **`VERIFIED_FOR_OWNER_REVIEW`** | Permissive | Filter `lang=='en'`; automated PII scrub; quarantine validation split |
| **`SRC-CV-05`** | MultiWOZ 2.4 English | ENGLISH | Apache-2.0 | **`VERIFIED_FOR_OWNER_REVIEW`** | Permissive | Strict quarantine of `test.json` benchmark split; ingest train only |
| **`SRC-CV-06`** | Gutenberg Theatrical Dialogue | ENGLISH | Public Domain (US) | **`VERIFIED_FOR_OWNER_REVIEW`** | Unrestricted | Strip PGLAF trademark headers; author death verified $\le 1955$ |
| **`SRC-TM-01`** | IndicCorp v2 (Tamil) | TAMIL | CC0-1.0 (Compilation) | **`PENDING_LEGAL_REVIEW`** | Unsettled | Outside Indian IP counsel review on Section 52 fair dealing |
| **`SRC-TM-02`** | Tamil Wikipedia Dump | TAMIL | CC-BY-SA 4.0 | **`PENDING_LEGAL_REVIEW`** | Unsettled | Outside copyleft counsel review on foundation model weight risk |
| **`SRC-TM-03`** | OSCAR 23.01 Tamil (Filtered)| TAMIL | ODC-By 1.0 | **`PENDING_LEGAL_REVIEW`** | Unsettled | Web domain blacklist and right-to-erasure unlearning policy |
| **`SRC-TG-01`** | DravidianCodeMix (YouTube) | TANGLISH | CC-BY-4.0 (Compilation) | **`PENDING_LEGAL_REVIEW`** | High Risk | Counsel review on YouTube ToS § II.A scraping restrictions |
| **`SRC-TG-02`** | IndicGLUE Tanglish Sentiment| TANGLISH | CC-BY-4.0 (Compilation) | **`PENDING_LEGAL_REVIEW`** | Conditional | Strict quarantine of `dev.csv` and `test.csv`; train split only |
| **`SRC-CV-07`** | WikiDialog English Subset | ENGLISH | CC-BY-SA 3.0/4.0 | **`PENDING_LEGAL_REVIEW`** | Unsettled | Consolidate with Wikipedia copyleft review; quarantine QA benchmarks |
| **`SRC-TG-03`** | Spoken Tanglish Transcripts | TANGLISH | CC-BY-NC-ND | **`REJECTED`** | Prohibited | None — permanently excluded due to Non-Commercial clause |

---

## 3. Key Findings by Language Category

### A. English Corpora: High Permissibility and Low Legal Risk
Six English sources (`SRC-EN-01`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-03`, `SRC-CV-05`, `SRC-CV-06`) are fully cleared from a licensing standpoint:
- Public domain literature (Gutenberg) carries expired copyright under 17 U.S.C. § 304.
- Technical documentation (IETF, Python) carries permissive open licenses (TLP 5.0, PSF-2.0).
- Conversational dialogue (OASST1, MultiWOZ) carries permissive Apache-2.0 licenses with clean contributor agreements.
- All six are classified as **`VERIFIED_FOR_OWNER_REVIEW`**. The owner may authorize preparation pipelines for these sources once technical sanitization filters (PII regex, benchmark quarantines) are approved.

### B. Tamil Corpora: Substantial Legal Ambiguity Under Indian Law
All three Tamil candidates (`SRC-TM-01`, `SRC-TM-02`, `SRC-TM-03`) are categorized as **`PENDING_LEGAL_REVIEW`**:
- `SRC-TM-01` (IndicCorp v2) carries a CC0 compilation license from IIT Madras, but the underlying news articles were crawled from commercial publishers whose copyright is unreleased. Indian copyright law lacks an explicit Text and Data Mining exception.
- `SRC-TM-02` (Tamil Wikipedia) is licensed under CC-BY-SA 4.0. The unresolved international legal question is whether trained neural network weights constitute an "Adapted Material" (derivative work) compelling open weights under ShareAlike.
- Neither source should be admitted to production ingress without outside legal counsel evaluation.

### C. Tanglish Corpora: Platform Restrictions & Rejections
- `SRC-TG-01` (DravidianCodeMix) contains genuine Tanglish comments, but scraping YouTube comments breaches YouTube Terms of Service § II.A. Categorized as **`PENDING_LEGAL_REVIEW`**.
- `SRC-TG-02` (IndicGLUE) is an evaluation benchmark; ingesting it into pretraining would contaminate evaluations unless `dev` and `test` splits are strictly quarantined.
- `SRC-TG-03` is published under a Non-Commercial research license and is permanently **`REJECTED`**.

---

## 4. Actionable Decisions for Sole Developer / Project Owner

The project owner is presented with the following decision points:

1. **Decision Point 1 (English Permissive Authorization):**
   - Authorize technical pipeline preparation for the six `VERIFIED_FOR_OWNER_REVIEW` English sources (`SRC-EN-01`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-03`, `SRC-CV-05`, `SRC-CV-06`), contingent on automated PII scrubbing and benchmark evaluation quarantine.
2. **Decision Point 2 (Tamil IP Counsel Review):**
   - Authorize engaging outside Indian IP counsel to evaluate Section 52(1)(a) fair dealing for `SRC-TM-01` (IndicCorp v2) and CC-BY-SA copyleft weight risk for `SRC-TM-02` (Tamil Wikipedia).
3. **Decision Point 3 (Tanglish Strategy):**
   - Decide whether to seek platform clearance for social media Tanglish (`SRC-TG-01`, `SRC-TG-02`) or rely primarily on Phase 25/26 validated **synthetic Tanglish generators** combined with licensed conversational English-Tamil parallel structures.
4. **Decision Point 4 (Rejection Confirmation):**
   - Confirm permanent rejection of `SRC-TG-03` (Non-commercial), `SRC-CV-01` (DailyDialog NC), and `SRC-CV-04` (Anthropic HH-RLHF alignment leakage).
