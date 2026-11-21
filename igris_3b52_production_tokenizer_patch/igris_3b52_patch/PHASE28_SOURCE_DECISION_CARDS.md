# PHASE 28 — SOURCE DECISION CARDS: SIX OWNER-REVIEW CANDIDATES

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-20  
**Status:** DECISION PREPARATION COMPLETE (All Candidates: `NOT_REVIEWED`)

> [!CRITICAL]
> **GOVERNANCE NOTICE:** A candidate marked `VERIFIED_FOR_OWNER_REVIEW` is **NOT legally cleared** and is **NOT authorized for acquisition**. This classification signifies only that primary licensing evidence and provenance records have been audited and verified as complete for the project owner's personal review. The owner decision field for every candidate is initially set to `NOT_REVIEWED`. Production ingress remains strictly **LOCKED**.

---

## Candidate 1: `SRC-EN-01` — Project Gutenberg English Subset

```
+------------------------------------+----------------------------------------------------------+
| Specification Field                | Verified Forensic Record                                 |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-EN-01                                                |
| Dataset Name                       | Project Gutenberg English Subset                         |
| Language Category                  | ENGLISH (en)                                             |
| Official Publisher                 | Project Gutenberg Literary Archive Foundation (PGLAF)    |
| Official Source Location           | https://www.gutenberg.org/ / rsync://aleph.gutenberg.org |
| Exact Pinned Catalog Snapshot      | Snapshot 2024-01-01 (cleared English titles)             |
| Target Payload Files               | Plain text files (*-0.txt, *.txt; ~50,000 titles)        |
| Declared Primary License           | Public Domain in the United States (17 U.S.C. Section 304)|
| License Version                    | US Statutory Copyright Law (Works published pre-1929)    |
| Primary Evidence Documentation     | PGLAF Policy & Terms of Use (Section 1)                  |
| Copyright Ownership & Provenance   | Historical authors (Austen, Dickens, Melville, etc.)     |
| Current Evidence Status            | VERIFIED_FOR_OWNER_REVIEW                                |
| Current Owner Decision             | NOT_REVIEWED                                             |
+------------------------------------+----------------------------------------------------------+
```

### Forensic Audit & Risk Profile:
1. **Third-Party Content Rights:**
   - In the US, all works published before January 1, 1929 have entered the public domain. Copyright has completely expired.
   - For worldwide public domain safety (Berne Convention "Life+70" rule), authors must have died $\le 1955$ (2026 - 70 = 1956).
2. **Commercial-Use, Modification & Redistribution:**
   - Fully permitted without royalty under US copyright law.
3. **Mandatory Trademark Condition (PGLAF License § 1.E.8):**
   - If distributing or creating derivative text without paying royalties, the entity must strip all references to "Project Gutenberg", the PGLAF trademark, and the standard preamble/postamble license headers (`*** START OF THE PROJECT GUTENBERG EBOOK ... ***`).
4. **Privacy & PII Exposure:**
   - Zero living PII. All authors and historical biographical subjects deceased $>70$ years.
5. **Benchmark Contamination:**
   - Low for standard benchmarks; overlap screening recommended against BookCorpus and PG19 evaluation partitions.
6. **Technical Acquisition Prerequisites:**
   - Automated header/footer stripper verified.
   - Metadata filter enforcing `author_death_year <= 1955` verified.
7. **Outside Legal Counsel Required:** No. Permissive public domain.

---

## Candidate 2: `SRC-TD-02` — IETF RFC Repository

```
+------------------------------------+----------------------------------------------------------+
| Specification Field                | Verified Forensic Record                                 |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-TD-02                                                |
| Dataset Name                       | IETF RFC Repository (Internet Standards Specifications)  |
| Language Category                  | ENGLISH (en - Technical)                                 |
| Official Publisher                 | Internet Engineering Task Force (IETF) / RFC Editor      |
| Official Source Location           | https://www.rfc-editor.org/ / https://github.com/ietf/    |
| Exact Pinned Catalog Snapshot      | Snapshot 2024-Q3 (RFC 1 through RFC 9500+)               |
| Target Payload Files               | Plain text files (rfc*.txt; ~9,500 documents)            |
| Declared Primary License           | IETF Trust Legal Provisions (TLP 5.0 Section 3.c)        |
| License Version                    | TLP 5.0 / RFC 5378 / BCP 78                              |
| Primary Evidence Documentation     | https://trustee.ietf.org/trust-legal-provisions.html     |
| Copyright Ownership & Provenance   | IETF Trust and contributing specification authors        |
| Current Evidence Status            | VERIFIED_FOR_OWNER_REVIEW                                |
| Current Owner Decision             | NOT_REVIEWED                                             |
+------------------------------------+----------------------------------------------------------+
```

### Forensic Audit & Risk Profile:
1. **Third-Party Content Rights:**
   - Specifications authored by network engineers and researchers under formal copyright assignment or license grants to the IETF Trust.
2. **Commercial-Use, Modification & Redistribution:**
   - Perpetual, worldwide, non-exclusive license to copy, extract, translate, and distribute RFC text.
   - **Specific Restriction:** Derivative or modified texts cannot be published *as official IETF RFC standards* (to protect the integrity of Internet specifications). Model pretraining extracts statistical parameters and does not publish RFC specifications.
3. **Attribution Requirements:**
   - Retain RFC document numbers, titles, and author attributions in dataset provenance metadata.
4. **Privacy & PII Exposure:**
   - RFC text footers contain real business email addresses, phone numbers, and corporate affiliations of Internet engineers.
   - **Mandatory Control:** Automated regex pipeline scrubbing all email patterns (`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`) prior to tokenization.
5. **Benchmark Contamination:**
   - Negligible for general LLM benchmarks; potential overlap with specialized networking certification exams.
6. **Technical Acquisition Prerequisites:**
   - Automated regex email and phone number scrubber verified.
7. **Outside Legal Counsel Required:** No. Clear permissive terms under IETF Trust.

---

## Candidate 3: `SRC-TD-03` — Python Official Documentation

```
+------------------------------------+----------------------------------------------------------+
| Specification Field                | Verified Forensic Record                                 |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-TD-03                                                |
| Dataset Name                       | Python Official Documentation                            |
| Language Category                  | ENGLISH (en - Technical)                                 |
| Official Publisher                 | Python Software Foundation (PSF), Beaverton, OR          |
| Official Source Location           | https://github.com/python/cpython (Doc/) / docs.python.org|
| Exact Pinned Catalog Snapshot      | Python 3.12.7 documentation release (git tag v3.12.7)    |
| Target Payload Files               | Plain text (*.txt) or reStructuredText (Doc/**/*.rst)    |
| Declared Primary License           | Python Software Foundation License Version 2 (PSF-2.0)   |
| License Version                    | PSF-2.0 Section 2 (Doc/license.rst)                      |
| Primary Evidence Documentation     | https://docs.python.org/3/license.html                   |
| Copyright Ownership & Provenance   | Copyright (c) 2001-2024 Python Software Foundation       |
| Current Evidence Status            | VERIFIED_FOR_OWNER_REVIEW                                |
| Current Owner Decision             | NOT_REVIEWED                                             |
+------------------------------------+----------------------------------------------------------+
```

### Forensic Audit & Risk Profile:
1. **Third-Party Content Rights:**
   - Developed by core Python contributors under PSF contributor agreements. Permissive open-source documentation license.
2. **Commercial-Use, Modification & Redistribution:**
   - Fully permitted. Explicit grant to reproduce, analyze, modify, and distribute derivatives.
3. **Attribution Requirements:**
   - Retain brief PSF copyright notice and disclaimer in dataset provenance metadata.
4. **Privacy & PII Exposure:**
   - Minimal (public acknowledgments of core developers).
5. **Benchmark Contamination (HIGH RELEVANCE):**
   - Python docstrings and documentation tutorials contain coding problem statements and docstring doctests that overlap directly with standard Python code benchmarks (HumanEval, MBPP).
   - **Mandatory Control:** Docstring code prompt screening filter to detect and exclude test problems matching HumanEval/MBPP.
6. **Technical Acquisition Prerequisites:**
   - Benchmark prompt overlap screening filter verified.
7. **Outside Legal Counsel Required:** No. Standard permissive open-source license.

---

## Candidate 4: `SRC-CV-03` — OpenAssistant Conversations (OASST1 - English)

```
+------------------------------------+----------------------------------------------------------+
| Specification Field                | Verified Forensic Record                                 |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-CV-03                                                |
| Dataset Name                       | OpenAssistant OASST1 (English Subset)                    |
| Language Category                  | ENGLISH (en - Conversational)                            |
| Official Publisher                 | LAION / OpenAssistant Project (Köpf et al., 2023)        |
| Official Source Location           | https://huggingface.co/datasets/OpenAssistant/oasst1     |
| Exact Pinned Catalog Snapshot      | Dataset release v1.0, commit 289ed0f90ff8eb4b5b7c0fdb... |
| Target Payload Files               | 2023-04-12_oasst_ready.trees.jsonl.gz (lang=='en')       |
| Declared Primary License           | Apache License 2.0                                       |
| License Version                    | Apache-2.0                                               |
| Primary Evidence Documentation     | OpenAssistant repository LICENSE and Contributor Terms   |
| Copyright Ownership & Provenance   | Volunteer crowd contributors under Apache-2.0 assignment |
| Current Evidence Status            | VERIFIED_FOR_OWNER_REVIEW                                |
| Current Owner Decision             | NOT_REVIEWED                                             |
+------------------------------------+----------------------------------------------------------+
```

### Forensic Audit & Risk Profile:
1. **Third-Party Content Rights:**
   - Volunteer crowd-workers submitted instructions and responses under terms explicitly assigning contributions under Apache-2.0.
2. **Commercial-Use, Modification & Redistribution:**
   - Fully permitted with Apache-2.0 NOTICE file and copyright attribution retention.
3. **Language Scope Isolation Invariant:**
   - OASST1 contains multiple languages (German, Spanish, French). Strict filter enforcing `lang == 'en'` is mandatory to maintain the IGRIS 3-language boundary.
4. **Privacy & PII Exposure:**
   - Medium risk. Volunteer prompters occasionally include personal anecdotes, social handles, or email references.
   - **Mandatory Control:** Automated regex and NER pipeline to scrub names, handles, and contact details.
5. **Benchmark Contamination & Split Isolation:**
   - The dataset contains `train` and `validation` splits.
   - **Mandatory Control:** Strict quarantine of the validation split. Pretraining must ingest ONLY the `train` split. Screening against MT-Bench and AlpacaEval required.
6. **Technical Acquisition Prerequisites:**
   - `lang == 'en'` filter verified.
   - Automated PII scrubber verified.
   - Validation split quarantine verified.
7. **Outside Legal Counsel Required:** No. Permissive Apache-2.0.

---

## Candidate 5: `SRC-CV-05` — MultiWOZ 2.4 (Task-Oriented Dialogue)

```
+------------------------------------+----------------------------------------------------------+
| Specification Field                | Verified Forensic Record                                 |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-CV-05                                                |
| Dataset Name                       | MultiWOZ 2.4 English Subset (Task Dialogue)              |
| Language Category                  | ENGLISH (en - Conversational)                            |
| Official Publisher                 | Dialogue Systems Group, University of Cambridge          |
| Official Source Location           | https://github.com/smartyfh/MultiWOZ2.4                  |
| Exact Pinned Catalog Snapshot      | Official release v2.4 (commit 89622d1)                   |
| Target Payload Files               | data.json / train.jsonl (~8,438 dialogues)               |
| Declared Primary License           | Apache License 2.0                                       |
| License Version                    | Apache-2.0 (Cambridge DSG LICENSE file)                  |
| Primary Evidence Documentation     | Budzianowski et al. (EMNLP 2018); Ye et al. (2021)       |
| Copyright Ownership & Provenance   | University of Cambridge Dialogue Systems Group           |
| Current Evidence Status            | VERIFIED_FOR_OWNER_REVIEW                                |
| Current Owner Decision             | NOT_REVIEWED                                             |
+------------------------------------+----------------------------------------------------------+
```

### Forensic Audit & Risk Profile:
1. **Third-Party Content Rights:**
   - Wizard-of-Oz crowd-sourced task dialogues created under Cambridge ethical research protocols. Released under Apache-2.0.
2. **Commercial-Use, Modification & Redistribution:**
   - Fully permitted with Apache attribution notice.
3. **Privacy & PII Exposure:**
   - **Zero Real PII.** All dialogue entities (hotels, restaurants, phone numbers, postcodes, reference IDs) are drawn from a synthetic mock database of Cambridge services.
4. **Evaluation Benchmark Contamination (CRITICAL INVARIANT):**
   - MultiWOZ `test.json` is the universal international benchmark for Dialogue State Tracking (DST).
   - Ingesting `test.json` would contaminate evaluation and invalidate scientific results.
   - **Mandatory Control:** Strict quarantine of `test.json`. Ingestion restricted to `train.jsonl` only.
5. **Technical Acquisition Prerequisites:**
   - Split partition verifier ensuring zero leakage from `test.json`.
6. **Outside Legal Counsel Required:** No. Clean academic Apache-2.0 release.

---

## Candidate 6: `SRC-CV-06` — Project Gutenberg Theatrical Dialogue

```
+------------------------------------+----------------------------------------------------------+
| Specification Field                | Verified Forensic Record                                 |
+------------------------------------+----------------------------------------------------------+
| Source Identifier                  | SRC-CV-06                                                |
| Dataset Name                       | Project Gutenberg Theatrical Dialogue                    |
| Language Category                  | ENGLISH (en - Conversational Dramatic)                   |
| Official Publisher                 | Project Gutenberg Literary Archive Foundation (PGLAF)    |
| Official Source Location           | https://www.gutenberg.org/                               |
| Exact Pinned Catalog Snapshot      | Pre-1929 theatrical dramatic plays catalog snapshot      |
| Target Payload Files               | theatrical_dialogue/*.txt (~120 plays; ~25 MB text)      |
| Declared Primary License           | Public Domain in the United States (17 U.S.C. Section 304)|
| License Version                    | US Statutory Copyright Law (Pre-1929 classical plays)    |
| Primary Evidence Documentation     | PGLAF Policy & CORR-23B-01 Permanent ID Reconciliation   |
| Copyright Ownership & Provenance   | Shakespeare (d.1616), Wilde (d.1900), Shaw (d.1950)      |
| Current Evidence Status            | VERIFIED_FOR_OWNER_REVIEW                                |
| Current Owner Decision             | NOT_REVIEWED                                             |
+------------------------------------+----------------------------------------------------------+
```

### Forensic Audit & Risk Profile:
1. **Historical Source ID Reconciliation (CORR-23B-01):**
   - Reaffirmed permanently as Project Gutenberg Theatrical Dialogue. WikiDialog English reassigned to `SRC-CV-07`.
2. **Third-Party Content Rights:**
   - Classical plays published pre-1929 have expired copyright in the US.
   - Worldwide copyright status: Shakespeare (d. 1616), Wilde (d. 1900), Synge (d. 1909) are in public domain globally. George Bernard Shaw (d. 1950) entered public domain in Life+70 nations on January 1, 2021.
3. **Mandatory Trademark Condition (PGLAF License § 1.E.8):**
   - Same mandatory stripping of "Project Gutenberg" trademark headers and footers as `SRC-EN-01`.
4. **Privacy & PII Exposure:**
   - Zero living PII. All playwrights and dramatic characters deceased $>70$ years.
5. **Benchmark Contamination:**
   - Negligible for modern NLP benchmarks.
6. **Technical Acquisition Prerequisites:**
   - Automated PGLAF header/footer stripper verified.
7. **Outside Legal Counsel Required:** No. Classical public domain literature.

---

## Summary of Decision Fields for Owner

| Source ID | Candidate Name | Primary License | Evidence Status | Current Owner Decision |
| :--- | :--- | :---: | :---: | :---: |
| **`SRC-EN-01`** | Project Gutenberg English | Public Domain | VERIFIED_FOR_OWNER_REVIEW | `NOT_REVIEWED` |
| **`SRC-TD-02`** | IETF RFC Repository | IETF TLP 5.0 | VERIFIED_FOR_OWNER_REVIEW | `NOT_REVIEWED` |
| **`SRC-TD-03`** | Python Official Docs | PSF-2.0 | VERIFIED_FOR_OWNER_REVIEW | `NOT_REVIEWED` |
| **`SRC-CV-03`** | OpenAssistant OASST1 (En) | Apache-2.0 | VERIFIED_FOR_OWNER_REVIEW | `NOT_REVIEWED` |
| **`SRC-CV-05`** | MultiWOZ 2.4 English | Apache-2.0 | VERIFIED_FOR_OWNER_REVIEW | `NOT_REVIEWED` |
| **`SRC-CV-06`** | Gutenberg Theatrical Dialogue | Public Domain | VERIFIED_FOR_OWNER_REVIEW | `NOT_REVIEWED` |
