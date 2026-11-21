# PHASE 29 — OWNER REVIEW PACKAGE: INDIVIDUAL DATASET REVIEW

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Phase:** Phase 29  
**Language Scope:** Strictly Tamil, English, and Tanglish (All other languages OUT_OF_SCOPE)  
**Current Governance Status:** Production ingress **LOCKED**; Tokenizer training **UNAUTHORIZED**; Model pretraining **LOCKED**; Cloud spending **$0.00**

---

## 1. Operating Instructions for the Project Owner

This package presents the six candidate English datasets audited as `VERIFIED_FOR_OWNER_REVIEW` in Phase 27 and Phase 28.

### Decision Rules:
1. **You are the sole decision-maker.** No automated agent, script, or simulated committee has rendered or will render a decision on your behalf.
2. **Approved Vocabulary:** For each candidate, you may select exactly one of the five approved decision values:
   - **`OWNER_ACCEPTS_FURTHER_REVIEW`** — Accept candidate for sandbox technical pipeline design (PII scrubbing, benchmark filtering). Does **not** authorize data downloading or ingress.
   - **`OWNER_REQUIRES_LEGAL_COUNSEL`** — Pause candidate until outside IP counsel delivers a formal legal opinion on a specific question.
   - **`OWNER_REQUIRES_MORE_EVIDENCE`** — Pause candidate until additional primary provenance or licensing records are gathered.
   - **`OWNER_REJECTS_SOURCE`** — Permanently reject candidate and exclude from IGRIS.
   - **`NOT_REVIEWED`** — Current default state. Candidate remains unreviewed.
3. **No Automatic Progression:** Review each candidate independently. Accepting or pausing one candidate does not affect the others.
4. **Governance Invariant:** No candidate is authorized for acquisition, download, tokenizer training, or pretraining during this phase.

---

## 2. Individual Candidate Review Packages

```
================================================================================
CANDIDATE 1 OF 6: SRC-EN-01 — Project Gutenberg English Subset
================================================================================
```

### A. Dataset Description & Intended IGRIS Use
* **Description:** ~50,000 cleared English-language literary, historical, scientific, and philosophical works published prior to 1929.
* **Intended IGRIS Use:** Core foundational English pretraining corpus; provides rich long-form syntactic coherence, complex narrative structures, extensive vocabulary, and long-range cross-sentence dependencies.
* **Estimated Volume:** ~4.2 GB raw plain text (~1.1 billion Candidate A tokens).

### B. Official Source, Version & License Evidence
* **Official Source:** Project Gutenberg Literary Archive Foundation (PGLAF), Salt Lake City, UT (`https://www.gutenberg.org/` / `rsync://aleph.gutenberg.org::gutenberg`).
* **Exact Version:** PGLAF catalog snapshot 2024-01-01 (works published pre-1929; author death year $\le 1955$).
* **Primary License:** **Public Domain in the United States** (17 U.S.C. § 304).
* **Copyright & Provenance Evidence:** All works published before January 1, 1929 have expired copyright under US law. PGLAF License Section 1 confirms free public domain status.

### C. Rights, Conditions & Commercial Usability
* **Commercial Use:** **Permitted Unrestricted** (expired copyright).
* **Modification & Redistribution:** **Permitted Unrestricted**.
* **Attribution Obligations:** None under copyright law. Author moral rights preserved in training catalog metadata.
* **Mandatory Trademark Condition (PGLAF § 1.E.8):** If distributing or modifying texts without paying royalties, the entity must strip all references to "Project Gutenberg", the PGLAF trademark, and standard preamble/postamble license headers (`*** START OF THE PROJECT GUTENBERG EBOOK ... ***`).

### D. Privacy, PII & Benchmark Contamination
* **Privacy & PII:** **Zero living PII.** All authors and biographical subjects deceased $>70$ years. GDPR and Indian DPDP Act 2023 do not apply to deceased historical persons.
* **Benchmark Contamination:** Low on standard modern LLM benchmarks; overlap screening recommended against NarrativeQA, PG19, and BookCorpus evaluation splits.

### E. Technical Preparation Requirements
1. Implement and unit-test automated regex header/footer stripper to remove all PGLAF trademark notices.
2. Implement metadata validator enforcing `author_death_year <= 1955` for worldwide Life+70 safety.

### F. Advantages & Disadvantages for IGRIS
* **Advantages:** Clean legal posture; zero third-party copyright risk; massive high-craft literary vocabulary; zero living PII exposure; $0 royalty cost.
* **Disadvantages:** Skew toward 19th-century and early 20th-century syntax; lacks modern colloquialisms, web jargon, and contemporary technical vocabulary.

### G. Remaining Uncertainties
* Whether specific translated works from non-US authors have extended copyright in non-US jurisdictions (fully mitigated by the `death_year <= 1955` filter).

### H. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Permits engineering to design the PGLAF trademark stripping and author death date filtering pipeline in the local sandbox).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-EN-01                                             |
|                                                                              |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| Owner Selection:                                                             |
|   [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                           |
|   [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                           |
|   [ ] OWNER_REQUIRES_MORE_EVIDENCE                                           |
|   [ ] OWNER_REJECTS_SOURCE                                                   |
|                                                                              |
| Owner Notes: _______________________________________________________________ |
+------------------------------------------------------------------------------+
```

---

```
================================================================================
CANDIDATE 2 OF 6: SRC-TD-02 — IETF RFC Repository
================================================================================
```

### A. Dataset Description & Intended IGRIS Use
* **Description:** Complete archive of ~9,500 Request for Comments (RFCs) from RFC 1 through RFC 9500+. Official technical specifications of Internet protocols (TCP/IP, HTTP/1-3, TLS 1.3, DNS, BGP, QUIC, OAuth, JSON).
* **Intended IGRIS Use:** Technical English pretraining corpus; provides rigorous technical definitions, protocol specifications, precise formal prose, networking terminology, and mathematical/RFC 2119 requirement keyword structures (MUST, SHALL, SHOULD, MAY).
* **Estimated Volume:** ~550 MB plain text (~140 million Candidate A tokens).

### B. Official Source, Version & License Evidence
* **Official Source:** RFC Editor / Internet Engineering Task Force (IETF) (`https://www.rfc-editor.org/` / `https://github.com/ietf/rfc-editor`).
* **Exact Version:** Complete official plain text archive snapshot 2024-Q3 (`rfc*.txt`).
* **Primary License:** **IETF Trust Legal Provisions (TLP 5.0 Section 3.c)** / RFC 5378 / BCP 78.
* **Copyright & Provenance Evidence:** Specifications authored by contributing engineers under formal copyright license grants to the IETF Trust. IETF TLP 5.0 § 3.c grants perpetual, worldwide rights to copy, extract, translate, and distribute.

### C. Rights, Conditions & Commercial Usability
* **Commercial Use:** **Permitted Permissive** (unrestricted for research and derivative works).
* **Modification & Redistribution:** **Permitted with Specific Restriction:** Derived texts cannot be published *as official IETF RFC standards* (to protect the integrity of Internet specifications). Model pretraining extracts statistical parameters and does not publish RFC standards.
* **Attribution Obligations:** Retain RFC document numbers, titles, and author attributions in dataset metadata ledger.

### D. Privacy, PII & Benchmark Contamination
* **Privacy & PII:** **Low Risk (Action Required).** RFC text footers contain real business email addresses, corporate affiliations, and phone numbers of Internet engineers (e.g. `postel@isi.edu`).
* **Mandatory PII Control:** Automated regex pipeline scrubbing all email patterns (`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`) and phone numbers prior to tokenization.
* **Benchmark Contamination:** Negligible for general NLP benchmarks; minor potential overlap with specialized networking certification exams.

### E. Technical Preparation Requirements
1. Implement and unit-test automated email address regex mask (`[EMAIL_REDACTED]`).
2. Implement ASCII table formatter to normalize technical ASCII diagrams.

### F. Advantages & Disadvantages for IGRIS
* **Advantages:** Unmatched technical English precision; formal protocol specifications; clean authoritative provenance; explicit perpetual license grant.
* **Disadvantages:** Contains dense ASCII tables, packet diagrams, and hex dumps requiring custom normalization.

### G. Remaining Uncertainties
* Pre-2008 RFCs (pre-RFC 5378) operated under older contributor agreements; however, the IETF Trust has confirmed liberal extraction policies for all historical RFCs.

### H. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Permits engineering to design the automated email masking regex and technical text normalizer in sandbox).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-TD-02                                             |
|                                                                              |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| Owner Selection:                                                             |
|   [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                           |
|   [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                           |
|   [ ] OWNER_REQUIRES_MORE_EVIDENCE                                           |
|   [ ] OWNER_REJECTS_SOURCE                                                   |
|                                                                              |
| Owner Notes: _______________________________________________________________ |
+------------------------------------------------------------------------------+
```

---

```
================================================================================
CANDIDATE 3 OF 6: SRC-TD-03 — Python Official Documentation
================================================================================
```

### A. Dataset Description & Intended IGRIS Use
* **Description:** Official documentation of the Python programming language: Language Reference, Library Reference, Tutorial, Setup & Usage guides, and HOWTOs.
* **Intended IGRIS Use:** High-quality expository software engineering prose, programming tutorials, API specifications, and structured technical explanations.
* **Estimated Volume:** ~85 MB plain text (~22 million Candidate A tokens).

### B. Official Source, Version & License Evidence
* **Official Source:** Python Software Foundation (PSF), Beaverton, OR (`https://github.com/python/cpython` Doc/ / `https://docs.python.org/3/`).
* **Exact Version:** Python 3.12.7 documentation release tarball (git tag `v3.12.7`).
* **Primary License:** **Python Software Foundation License Version 2 (PSF-2.0)**.
* **Copyright & Provenance Evidence:** Copyright © 2001-2024 Python Software Foundation. PSF-2.0 Section 2 explicitly grants licensees the right to reproduce, analyze, modify, and distribute derivatives.

### C. Rights, Conditions & Commercial Usability
* **Commercial Use:** **Permitted Permissive** (OSI-approved and FSF-approved permissive open-source license).
* **Modification & Redistribution:** **Permitted with Notice:** Retain brief PSF copyright notice and disclaimer in documentation metadata.
* **Attribution Obligations:** Standard PSF attribution statement retained in dataset metadata ledger.

### D. Privacy, PII & Benchmark Contamination
* **Privacy & PII:** **Zero PII Risk.** Contains public acknowledgments of core Python developers; no private personal data.
* **Benchmark Contamination (HIGH RELEVANCE):** Python docstrings and documentation tutorials contain coding problem statements and doctests that overlap directly with standard Python coding benchmarks (HumanEval, MBPP).
* **Mandatory Control:** Docstring code prompt screening filter to detect and exclude test problems matching HumanEval/MBPP.

### E. Technical Preparation Requirements
1. Implement reStructuredText (RST) to plain-text parser stripping directive markup while preserving code blocks and prose.
2. Implement HumanEval/MBPP code prompt exclusion filter.

### F. Advantages & Disadvantages for IGRIS
* **Advantages:** Extremely clear pedagogical technical English; clean permissive license; zero copyleft risk; zero privacy risk.
* **Disadvantages:** Modest volume (~85 MB); benchmark leakage risk requires strict prompt exclusion.

### G. Remaining Uncertainties
* None. PSF-2.0 is an internationally recognized permissive license with extensive corporate adoption.

### H. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Permits engineering to design the RST text extraction and HumanEval/MBPP screening filter).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-TD-03                                             |
|                                                                              |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| Owner Selection:                                                             |
|   [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                           |
|   [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                           |
|   [ ] OWNER_REQUIRES_MORE_EVIDENCE                                           |
|   [ ] OWNER_REJECTS_SOURCE                                                   |
|                                                                              |
| Owner Notes: _______________________________________________________________ |
+------------------------------------------------------------------------------+
```

---

```
================================================================================
CANDIDATE 4 OF 6: SRC-CV-03 — OpenAssistant OASST1 English Subset
================================================================================
```

### A. Dataset Description & Intended IGRIS Use
* **Description:** Crowd-sourced multi-turn conversational trees: human user instructions paired with volunteer assistant responses, spanning technical queries, creative writing, explanations, and dialogue.
* **Intended IGRIS Use:** Instruction-tuning and conversational pretraining corpus; teaches decoder-only transformer conversational turn-taking, role tokens (`<user>`, `<assistant>`), and prompt-following behavior.
* **Estimated Volume:** ~210 MB plain text (~55 million Candidate A tokens across ~161,000 messages in English).

### B. Official Source, Version & License Evidence
* **Official Source:** LAION / OpenAssistant Project (`https://huggingface.co/datasets/OpenAssistant/oasst1`).
* **Exact Version:** Release v1.0, commit `289ed0f90ff8eb4b5b7c0fdbab26a29d5b0d02ea` (`2023-04-12_oasst_ready.trees.jsonl.gz`).
* **Primary License:** **Apache License 2.0**.
* **Copyright & Provenance Evidence:** Volunteer contributors accepted OpenAssistant Contributor Terms assigning contributions under Apache-2.0. Clean repository LICENSE file.

### C. Rights, Conditions & Commercial Usability
* **Commercial Use:** **Permitted Permissive** (standard Apache-2.0 terms).
* **Modification & Redistribution:** **Permitted** with Apache-2.0 NOTICE retention.
* **Attribution Obligations:** Retain Apache-2.0 NOTICE file and copyright notice in dataset provenance ledger.

### D. Privacy, PII & Benchmark Contamination
* **Privacy & PII (MEDIUM RISK):** Volunteer crowd-workers occasionally included personal anecdotes, first names, or social media handles.
* **Mandatory PII Control:** Automated regex and Named Entity Recognition (NER) scrubber to redact personal names, handles, and contact info.
* **Language Scope Filter (MANDATORY INVARIANT):** OASST1 contains multiple languages (German, Spanish, French). Strict filter enforcing `lang == 'en'` is required.
* **Benchmark Contamination & Split Quarantine (CRITICAL):**
  * The dataset contains `train` and `validation` splits.
  * **Mandatory Control:** Strict quarantine of the validation split. Pretraining must ingest ONLY the `train` split. Screening against MT-Bench and AlpacaEval prompt sets required.

### E. Technical Preparation Requirements
1. Implement `lang == 'en'` language partition filter.
2. Implement validation split quarantine isolating `split == 'train'`.
3. Implement automated PII regex and NER scrubber.

### F. Advantages & Disadvantages for IGRIS
* **Advantages:** High conversational quality; clean Apache-2.0 provenance; instruction-following alignment; natural turn-taking structure.
* **Disadvantages:** Contains incidental volunteer PII requiring automated scrubbing; requires multilingual filtering to remove non-English trees.

### G. Remaining Uncertainties
* Potential for crowd-workers to have pasted short excerpts of third-party copyrighted text into prompts (shielded by Apache-2.0 § 7 disclaimer of warranty).

### H. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Permits engineering to design the `lang=='en'` filter, validation split quarantine, and PII scrubbing pipeline).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-CV-03                                             |
|                                                                              |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| Owner Selection:                                                             |
|   [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                           |
|   [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                           |
|   [ ] OWNER_REQUIRES_MORE_EVIDENCE                                           |
|   [ ] OWNER_REJECTS_SOURCE                                                   |
|                                                                              |
| Owner Notes: _______________________________________________________________ |
+------------------------------------------------------------------------------+
```

---

```
================================================================================
CANDIDATE 5 OF 6: SRC-CV-05 — MultiWOZ 2.4 English Subset
================================================================================
```

### A. Dataset Description & Intended IGRIS Use
* **Description:** 8,438 human-human goal-oriented task dialogues between tourists and informational clerks across 7 Cambridge domains (hotels, restaurants, attractions, trains, taxis, hospitals, police).
* **Intended IGRIS Use:** Task-oriented conversational pretraining corpus; teaches the model slot-filling, multi-turn state tracking, structured entity extraction, and conversational goal resolution.
* **Estimated Volume:** ~45 MB plain text (~12 million Candidate A tokens).

### B. Official Source, Version & License Evidence
* **Official Source:** Dialogue Systems Group, University of Cambridge (`https://github.com/smartyfh/MultiWOZ2.4`).
* **Exact Version:** Official release v2.4, commit `89622d1` (`data.json` / `train.jsonl`).
* **Primary License:** **Apache License 2.0**.
* **Copyright & Provenance Evidence:** Copyright © University of Cambridge Dialogue Systems Group (Budzianowski et al., EMNLP 2018; Ye et al., 2021). Clean repository LICENSE file.

### C. Rights, Conditions & Commercial Usability
* **Commercial Use:** **Permitted Permissive** (standard Apache-2.0 terms).
* **Modification & Redistribution:** **Permitted** with Apache attribution notice.
* **Attribution Obligations:** Cambridge Dialogue Systems Group Apache-2.0 attribution statement retained in metadata.

### D. Privacy, PII & Benchmark Contamination
* **Privacy & PII:** **ZERO REAL PII.** All dialogue entities (hotel names, restaurant addresses, telephone numbers, postcodes, booking reference IDs) are drawn from a synthetic mock database of Cambridge services.
* **Benchmark Contamination (CRITICAL INVARIANT):**
  * MultiWOZ `test.json` is the standard international benchmark for Dialogue State Tracking (DST).
  * Ingesting `test.json` into pretraining would contaminate evaluation and invalidate scientific benchmark scores.
  * **Mandatory Control:** Strict quarantine of `test.json`. Ingestion strictly restricted to `train.jsonl` only.

### E. Technical Preparation Requirements
1. Implement split partition verifier ensuring zero leakage from `test.json`.
2. Implement dialogue flattener converting nested JSON turns into standardized `<user>` / `<assistant>` training sequences.

### F. Advantages & Disadvantages for IGRIS
* **Advantages:** Absolute zero privacy risk (synthetic entities); permissive Cambridge Apache-2.0 license; excellent goal-oriented multi-turn structure.
* **Disadvantages:** Narrow domain focus (Cambridge tourism/booking); small corpus volume (~45 MB).

### G. Remaining Uncertainties
* None. Clean academic dataset released under permissive Apache-2.0.

### H. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Permits engineering to design the dialogue flattener and `test.json` quarantine verification in sandbox).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-CV-05                                             |
|                                                                              |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| Owner Selection:                                                             |
|   [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                           |
|   [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                           |
|   [ ] OWNER_REQUIRES_MORE_EVIDENCE                                           |
|   [ ] OWNER_REJECTS_SOURCE                                                   |
|                                                                              |
| Owner Notes: _______________________________________________________________ |
+------------------------------------------------------------------------------+
```

---

```
================================================================================
CANDIDATE 6 OF 6: SRC-CV-06 — Project Gutenberg Theatrical Dialogue
================================================================================
```

### A. Dataset Description & Intended IGRIS Use
* **Description:** Extracted theatrical dramatic scripts from classical plays published pre-1929 (William Shakespeare, Oscar Wilde, George Bernard Shaw, J.M. Synge).
* **Intended IGRIS Use:** Conversational dramatic dialogue pretraining corpus; teaches natural dialogue cadence, character turn-taking, dramatic conflict, repartee, and conversational subtext.
* **Estimated Volume:** ~25 MB plain text (~6.5 million Candidate A tokens across ~120 plays).

### B. Official Source, Version & License Evidence
* **Official Source:** Project Gutenberg Literary Archive Foundation (PGLAF) (`https://www.gutenberg.org/`).
* **Exact Version:** Pre-1929 dramatic plays catalog snapshot; permanent source ID reaffirmed under `CORR-23B-01`.
* **Primary License:** **Public Domain in the United States** (17 U.S.C. § 304).
* **Copyright & Provenance Evidence:** Classical dramatic plays published before January 1, 1929 have expired copyright in the US.
  * Shakespeare (d. 1616), Wilde (d. 1900), Synge (d. 1909) are in the public domain globally.
  * George Bernard Shaw (d. 1950): Works published pre-1929 entered the public domain in Life+70 nations on January 1, 2021.

### C. Rights, Conditions & Commercial Usability
* **Commercial Use:** **Permitted Unrestricted** (expired copyright).
* **Modification & Redistribution:** **Permitted Unrestricted**.
* **Attribution Obligations:** None under copyright law.
* **Mandatory Trademark Condition (PGLAF § 1.E.8):** Same mandatory removal of "Project Gutenberg" trademark headers and footers as `SRC-EN-01`.

### D. Privacy, PII & Benchmark Contamination
* **Privacy & PII:** **Zero living PII.** All playwrights and dramatic characters deceased $>70$ years.
* **Benchmark Contamination:** Negligible for modern conversational and QA benchmarks.

### E. Technical Preparation Requirements
1. Implement PGLAF trademark header/footer stripper.
2. Implement script dialogue normalizer to parse character name prefixes (`HAMLET:`, `LADY BRACKNELL:`) into conversational role tokens.

### F. Advantages & Disadvantages for IGRIS
* **Advantages:** Free public domain status; zero copyleft risk; zero privacy risk; superb dramatic dialogue and conversational turn-taking.
* **Disadvantages:** Archaic syntactic register (Early Modern English in Shakespeare; Victorian/Edwardian English in Wilde and Shaw); small corpus size (~25 MB).

### G. Remaining Uncertainties
* None. Reconciled under `CORR-23B-01`; copyright status fully confirmed.

### H. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Permits engineering to design the dramatic character dialogue normalizer and PGLAF header stripper).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-CV-06                                             |
|                                                                              |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| Owner Selection:                                                             |
|   [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                           |
|   [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                           |
|   [ ] OWNER_REQUIRES_MORE_EVIDENCE                                           |
|   [ ] OWNER_REJECTS_SOURCE                                                   |
|                                                                              |
| Owner Notes: _______________________________________________________________ |
+------------------------------------------------------------------------------+
```

---

## 3. Preservation of Pending Tamil, Tanglish & WikiDialog Sources

In accordance with Phase 29 requirements, all other candidate sources remain preserved in their existing legal classifications. **No status changes have been made:**

### A. Tamil Corpora (All Pending Legal Review)
* **`SRC-TM-01` (IndicCorp v2 Tamil):** `PENDING_LEGAL_REVIEW`. Blocker: Indian Copyright Act § 52(1)(a) TDM fair dealing gap for news publisher content.
* **`SRC-TM-02` (Tamil Wikipedia Dump):** `PENDING_LEGAL_REVIEW`. Blocker: CC-BY-SA 4.0 § 3(b) viral ShareAlike copyleft risk to model weights.
* **`SRC-TM-03` (OSCAR 23.01 Tamil):** `PENDING_LEGAL_REVIEW`. Blocker: ODC-By database license only; underlying web copyright; GDPR/DPDP right to erasure.

### B. Tanglish Corpora (Two Pending, One Rejected)
* **`SRC-TG-01` (DravidianCodeMix):** `PENDING_LEGAL_REVIEW`. Blocker: YouTube Terms of Service § II.A automated scraping prohibition.
* **`SRC-TG-02` (IndicGLUE Tanglish Sentiment):** `PENDING_LEGAL_REVIEW`. Blocker: Social media scraping terms and evaluation benchmark contamination.
* **`SRC-TG-03` (Spoken Tanglish Transcripts):** **`REJECTED`**. Blocker: Non-commercial (NC/ND) clause permanently bars commercial model deployment.

### C. English Copyleft Corpus (Pending Legal Review)
* **`SRC-CV-07` (WikiDialog English):** `PENDING_LEGAL_REVIEW`. Blocker: Inpainted dialogue inherits CC-BY-SA copyleft from Wikipedia; QA evaluation overlap.
