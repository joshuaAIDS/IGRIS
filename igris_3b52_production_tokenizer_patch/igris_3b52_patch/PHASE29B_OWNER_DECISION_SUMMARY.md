# PHASE 29B — OWNER DECISION SUMMARY: FINAL CANDIDATE DOSSIERS

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Phase:** Phase 29B (Final Source Evidence and Owner Decision Readiness)  
**Status:** ALL CANDIDATES INITIALIZED AND PRESERVED AS `NOT_REVIEWED`  
**Approved Language Scope:** Strictly **Tamil**, **English**, and **Tanglish** (All other languages remain `OUT_OF_SCOPE`)  

---

## 1. Operating Model & Purpose

This document provides a concise, high-signal decision summary prepared exclusively for the sole project owner. 

Under `SOLO_DEVELOPER_OWNER_REVIEW`, no automated system, agent, or quorum may make dataset decisions or authorize acquisition. This document presents the final forensic evidence, highlights open uncertainties, and groups the six candidate sources into actionable decision readiness categories.

---

## 2. Decision Readiness Categorization

The six English candidate sources audited in Phase 29B fall into three clear readiness tiers:

```
+-----------------------------------------------------------------------------------------+
|                              DECISION READINESS MATRIX                                  |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  TIER 1: SUFFICIENT EVIDENCE FOR FURTHER REVIEW                                         |
|  -------------------------------------------------------------------------------------  |
|  Candidates with verified primary licenses, established rights scopes, and clearly      |
|  defined technical decontamination and privacy scrubbing protocols:                   |
|    - SRC-TD-03: Python Official Documentation (PSF-2.0 Section 2)                       |
|    - SRC-CV-03: OpenAssistant OASST1 English (Apache-2.0 via Contributor Agreement)      |
|    - SRC-EN-01: Project Gutenberg English Literature (PGLAF § 1.C Elective Disclaimer)  |
|    - SRC-CV-06: Project Gutenberg Theatrical Dialogue (PGLAF § 1.C Elective Disclaimer) |
|                                                                                         |
|  TIER 2: CANDIDATES REQUIRING ADDITIONAL EVIDENCE                                       |
|  -------------------------------------------------------------------------------------  |
|  Candidates with unresolved provenance, mixed licensing tiers, or data-code splits:     |
|    - SRC-CV-05: MultiWOZ 2.4 English (Code is Apache-2.0, but underlying crowd-dialogue  |
|                 data has no verified license deed; contains real Cambridge venues)     |
|                 -> Explicit candidate for OWNER_REQUIRES_MORE_EVIDENCE                  |
|    - SRC-TD-02: IETF RFC Repository (Post-5378 RFCs clear under TLP 5.0 § 3.c; Pre-5378  |
|                 RFCs & Independent Stream have unverified non-standards derivative grants)  |
|                 -> Requires owner filter to post-2008 / verified RFCs                   |
|                                                                                         |
|  TIER 3: CANDIDATES REQUIRING QUALIFIED LEGAL COUNSEL                                    |
|  -------------------------------------------------------------------------------------  |
|  Candidates with viral copyleft risks, scraping terms violations, or cross-border issues: |
|    - SRC-CV-07: WikiDialog English (CC-BY-SA 3.0/4.0 copyleft share-alike weight risk)  |
|    - SRC-TM-01: IndicCorp v2 Tamil (Crawl provenance / unverified web scraping rights)  |
|    - SRC-TM-02: Tamil Wikipedia (CC-BY-SA 3.0/4.0 copyleft share-alike weight risk)     |
|    - SRC-TM-03: OSCAR Tamil (Common Crawl scraping terms and GDPR opt-out issues)       |
|    - SRC-TG-01: DravidianCodeMix YouTube (YouTube Terms of Service § 5.B scraping ban)   |
|    - SRC-TG-02: IndicGLUE Tanglish (Twitter/YouTube social scraping provenance)          |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Candidate Source Dossiers & Decision Cards

Below are the six individual review dossiers. In strict compliance with governance rules, **every owner decision field is initialized to `[X] NOT_REVIEWED`**.

```
===========================================================================================
CANDIDATE 1: SRC-EN-01 — Project Gutenberg English Literature
===========================================================================================
Category: Public Domain Prose & Classical Literature
Upstream Repository: https://www.gutenberg.org/ (rsync://aleph.gutenberg.org::gutenberg)
Exact Release / Scope: Works published pre-1929 with author death <= 1955 (~50,000 titles)
Primary License Evidence: 17 U.S.C. § 304 / PGLAF License Section 1.C (Elective Disclaimer)
Evidence Classification: VERIFIED_PRIMARY_SOURCE (PGLAF-LIC-SEC-1C)

Key Legal & Technical Facts:
- Section 1.C allows copying, distribution, and derivative works without contractual royalties,
  provided all references to Project Gutenberg and PGLAF trademarks are completely removed.
- Section 1.E.8 is the commercial fee royalty clause (20% gross profit under trademark),
  NOT the elective disclaimer mechanism.
- Catalog inclusion does not guarantee public domain (item-level notice check required).
- Author death filter (<= 1955) is a preliminary screening heuristic, not global legal clearance.
- Transcriber and proofreader names in header lines require automated stripping.
- Mandatory decontamination: screen against NarrativeQA and PG19 evaluation sets.

Readiness Assessment: SUFFICIENT_FOR_FURTHER_REVIEW (Pending Item-Level Screening)

+-----------------------------------------------------------------------------------------+
| OWNER DECISION FIELD: SRC-EN-01                                                         |
|                                                                                         |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                                        |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                                        |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                                        |
| [ ] OWNER_REJECTS_SOURCE                                                                |
| [X] NOT_REVIEWED                                                                        |
+-----------------------------------------------------------------------------------------+
```

```
===========================================================================================
CANDIDATE 2: SRC-TD-02 — IETF RFC Repository
===========================================================================================
Category: Technical Standards Specifications & Protocol Descriptions
Upstream Repository: https://www.rfc-editor.org/ / https://github.com/ietf/rfc-editor
Exact Release / Scope: Official RFC tarball RFC 1 through RFC 9500+ (snapshot 2024-Q3)
Primary License Evidence: IETF Trust Legal Provisions (TLP 5.0 § 3.c) / RFC 5378 / BCP 78
Evidence Classification: CONFLICTING_EVIDENCE / UNVERIFIED for Pre-5378 outside Standards

Key Legal & Technical Facts:
- Post-5378 Standards Track RFCs grant clear worldwide royalty-free derivative rights (TLP 5.0 § 3.c).
- Pre-5378 RFCs (pre-Nov 10, 2008) were contributed under RFC 2026/3978, where contributors
  did not grant broad derivative rights outside the IETF Standards Process.
- Pre-5378 RFCs are NOT automatically rejected; reproduction is permitted, but machine-learning
  derivative rights outside standards remain UNVERIFIED.
- Independent Submission Stream RFCs contain proprietary vendor MIBs and non-standard disclaimers.
- Real network engineer email addresses, corporate affiliations, and phone numbers in footers
  require automated regex scrubbing.

Readiness Assessment: REQUIRES_MORE_EVIDENCE (To filter to Post-5378 Standards Track)

+-----------------------------------------------------------------------------------------+
| OWNER DECISION FIELD: SRC-TD-02                                                         |
|                                                                                         |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                                        |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                                        |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                                        |
| [ ] OWNER_REJECTS_SOURCE                                                                |
| [X] NOT_REVIEWED                                                                        |
+-----------------------------------------------------------------------------------------+
```

```
===========================================================================================
CANDIDATE 3: SRC-TD-03 — Python Official Documentation
===========================================================================================
Category: Programming Documentation, Language Specifications, & Tutorials
Upstream Repository: https://github.com/python/cpython / https://docs.python.org/3/
Exact Release / Scope: Python 3.12.7 documentation release tarball (git tag v3.12.7)
Primary License Evidence: Python Software Foundation License Version 2 (PSF-2.0 Section 2)
Evidence Classification: VERIFIED_PRIMARY_SOURCE (PSF-2.0-DOC-LICENSE)

Key Legal & Technical Facts:
- PSF-2.0 Section 2 expressly grants licensees the right to "reproduce, analyze, test,
  prepare derivative works, distribute, and otherwise use Python... in machine or paper media."
- Permissive open-source license covering computational analysis and model pretraining.
- Third-party notices (Expat, OpenSSL, libffi) in Doc/license.rst are fully permissive.
- Benchmark leakage risk: HumanEval and MBPP prompts frequently mirror Python docstrings.
  Mandatory docstring exclusion filter required prior to tokenization.
- Contributor names and emails in Doc/acks.rst require automated email masking.

Readiness Assessment: SUFFICIENT_FOR_FURTHER_REVIEW

+-----------------------------------------------------------------------------------------+
| OWNER DECISION FIELD: SRC-TD-03                                                         |
|                                                                                         |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                                        |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                                        |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                                        |
| [ ] OWNER_REJECTS_SOURCE                                                                |
| [X] NOT_REVIEWED                                                                        |
+-----------------------------------------------------------------------------------------+
```

```
===========================================================================================
CANDIDATE 4: SRC-CV-03 — OpenAssistant OASST1 English
===========================================================================================
Category: Conversational Dialogue, Instruction Following, & Multi-Turn Trees
Upstream Repository: https://huggingface.co/datasets/OpenAssistant/oasst1
Exact Release / Scope: Release v1.0, commit 289ed0f90ff8eb4b5b7c0fdbab26a29d5b0d02ea
Primary License Evidence: Apache License 2.0 / Contributor Terms of Service
Evidence Classification: VERIFIED_PRIMARY_SOURCE (OASST1-APACHE2-LICENSE)

Key Legal & Technical Facts:
- Contributors agreed to Contributor Terms assigning Apache-2.0 rights to LAION/OpenAssistant.
- Grants broad commercial and model training rights with standard Section 7 warranty disclaimers.
- Requires strict English-only filtering (`lang == 'en'`).
- Validation dialogue trees must be quarantined to prevent leakage into MT-Bench / AlpacaEval.
- Volunteer prompts contain incidental personal information (usernames, self-disclosed anecdotes);
  requires automated regex and spaCy NER scrubbing pipeline.
- Risk of residual third-party copyrighted text submitted by crowd-workers in prompts.

Readiness Assessment: SUFFICIENT_FOR_FURTHER_REVIEW

+-----------------------------------------------------------------------------------------+
| OWNER DECISION FIELD: SRC-CV-03                                                         |
|                                                                                         |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                                        |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                                        |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                                        |
| [ ] OWNER_REJECTS_SOURCE                                                                |
| [X] NOT_REVIEWED                                                                        |
+-----------------------------------------------------------------------------------------+
```

```
===========================================================================================
CANDIDATE 5: SRC-CV-05 — MultiWOZ 2.4 English Subset
===========================================================================================
Category: Task-Oriented Dialogue (Hotels, Restaurants, Transport)
Upstream Repository: https://github.com/smartyfh/MultiWOZ2.4 (Ye et al., 2021)
Exact Release / Scope: Official release v2.4, commit 89622d1 (~8,438 dialogues)
Primary License Evidence: Apache License 2.0 (Repo Code) / Data license UNVERIFIED
Evidence Classification: CONFLICTING_EVIDENCE (MULTIWOZ-REPO-LICENSE)

Key Legal & Technical Facts:
- Code is licensed under Apache-2.0, but there is no explicit data deed or licensing agreement
  governing the crowd-sourced dialogue turns collected across MultiWOZ versions.
- Primary evidence does NOT support blanket Apache-2.0 coverage of the dataset itself.
- Entities are NOT synthetic: contains authentic Cambridge commercial establishments
  ("The Gonville Hotel", "Lensfield Hotel", postcodes CB1 1LY / CB2 1EN, phone numbers 01223...).
- These entries represent public commercial directory data rather than private PII.
- MultiWOZ is the primary benchmark for Dialogue State Tracking (DST).
  Test split (test.json) must be quarantined; ingest train.jsonl only.

Readiness Assessment: REQUIRES_MORE_EVIDENCE (Explicit Candidate for OWNER_REQUIRES_MORE_EVIDENCE)

+-----------------------------------------------------------------------------------------+
| OWNER DECISION FIELD: SRC-CV-05                                                         |
|                                                                                         |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                                        |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                                        |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                                        |
| [ ] OWNER_REJECTS_SOURCE                                                                |
| [X] NOT_REVIEWED                                                                        |
+-----------------------------------------------------------------------------------------+
```

```
===========================================================================================
CANDIDATE 6: SRC-CV-06 — Project Gutenberg Theatrical Dialogue
===========================================================================================
Category: Classical Theatrical Dialogue & Dramatic Play Scripts
Upstream Repository: https://www.gutenberg.org/
Exact Release / Scope: Pre-1929 theatrical plays with author death <= 1955 (~120 plays)
Primary License Evidence: 17 U.S.C. § 304 / PGLAF License Section 1.C (Elective Disclaimer)
Evidence Classification: VERIFIED_PRIMARY_SOURCE (PGLAF-THEATRICAL-SEC-1C)

Key Legal & Technical Facts:
- Governed by PGLAF Section 1.C: removing Project Gutenberg headers and trademarks waives
  contractual restrictions and avoids Section 1.E.8 20% commercial gross-profit royalties.
- Features classical playwrights (Shakespeare, Wilde, Shaw, Synge).
- George Bernard Shaw (died 1950) entered the public domain under Life+70 on January 1, 2021.
- Author death filter (<= 1955) is an effective preliminary heuristic for Life+70 nations.
- Transcriber credits in play headers require automated stripping.
- Dialogue format preserves theatrical character turn-taking.

Readiness Assessment: SUFFICIENT_FOR_FURTHER_REVIEW

+-----------------------------------------------------------------------------------------+
| OWNER DECISION FIELD: SRC-CV-06                                                         |
|                                                                                         |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                                        |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                                        |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                                        |
| [ ] OWNER_REJECTS_SOURCE                                                                |
| [X] NOT_REVIEWED                                                                        |
+-----------------------------------------------------------------------------------------+
```

---

## 4. Preserved Legal Blockers

```
+-----------------------------------------------------------------------------------------+
| PRESERVED CANDIDATE STATUSES                                                            |
+-----------------------------------------------------------------------------------------+
|  Tamil Candidates:                                                                      |
|    - SRC-TM-01 (IndicCorp v2 Tamil):            PENDING_LEGAL_REVIEW                    |
|    - SRC-TM-02 (Tamil Wikipedia):               PENDING_LEGAL_REVIEW                    |
|    - SRC-TM-03 (OSCAR Tamil):                   PENDING_LEGAL_REVIEW                    |
|                                                                                         |
|  Tanglish Candidates:                                                                   |
|    - SRC-TG-01 (DravidianCodeMix YouTube):      PENDING_LEGAL_REVIEW                    |
|    - SRC-TG-02 (IndicGLUE Tanglish Sentiment):  PENDING_LEGAL_REVIEW                    |
|    - SRC-TG-03 (Spoken Tanglish LDC):           REJECTED (Commercial Prohib.)           |
|                                                                                         |
|  English Candidates:                                                                    |
|    - SRC-CV-07 (WikiDialog English):            PENDING_LEGAL_REVIEW                    |
+-----------------------------------------------------------------------------------------+
```

---

## 5. Next Steps for the Sole Project Owner

Execution is paused. To proceed, please review the dossiers and indicate your choice for each candidate from the approved vocabulary:
1. `OWNER_ACCEPTS_FURTHER_REVIEW`
2. `OWNER_REQUIRES_LEGAL_COUNSEL`
3. `OWNER_REQUIRES_MORE_EVIDENCE`
4. `OWNER_REJECTS_SOURCE`

No acquisition will be initiated, and Phase 30 will not start, until your explicit decisions are recorded.
