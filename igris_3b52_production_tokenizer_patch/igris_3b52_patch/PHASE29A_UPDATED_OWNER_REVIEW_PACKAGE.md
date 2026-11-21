# PHASE 29A — UPDATED OWNER REVIEW PACKAGE (EVIDENCE-CORRECTED)

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Phase:** Phase 29A (Corrected Dossiers)  
**Language Scope:** Strictly Tamil, English, and Tanglish (All other languages OUT_OF_SCOPE)  
**Current Governance Status:** Production ingress **LOCKED**; Tokenizer training **UNAUTHORIZED**; Model pretraining **LOCKED**; Cloud spending **$0.00**

---

## 1. Operating Instructions for the Project Owner

This updated review package corrects the overgeneralized legal claims, primary license misinterpretations, and privacy assumptions identified during the Phase 29A audit.

### Decision Rules:
1. **You are the sole decision-maker.** No automated agent, script, or simulated committee has rendered or will render a decision on your behalf.
2. **Approved Vocabulary:** For each candidate, you may select exactly one of the five approved decision values:
   - **`OWNER_ACCEPTS_FURTHER_REVIEW`** — Accept candidate for sandbox technical pipeline design (PII scrubbing, benchmark filtering). Does **not** authorize data downloading or ingress.
   - **`OWNER_REQUIRES_LEGAL_COUNSEL`** — Pause candidate until outside IP counsel delivers a formal written legal opinion resolving a specific statutory or contractual question.
   - **`OWNER_REQUIRES_MORE_EVIDENCE`** — Pause candidate until additional primary provenance, catalog snapshot, or license documentation is gathered. (Specifically relevant for `SRC-CV-05` data licensing).
   - **`OWNER_REJECTS_SOURCE`** — Permanently reject candidate and exclude from IGRIS.
   - **`NOT_REVIEWED`** — Current default state. Candidate remains unreviewed.
3. **No Automatic Progression:** Review each candidate independently. Accepting or pausing one candidate does not affect the others.
4. **Governance Invariant:** No candidate is authorized for acquisition, download, tokenizer training, or pretraining during this phase.

---

## 2. Evidence-Corrected Candidate Dossiers

```
================================================================================
CANDIDATE 1 OF 6: SRC-EN-01 — Project Gutenberg English Subset
================================================================================
```

### A. Dataset Description & Intended IGRIS Use
* **Description:** ~50,000 cleared English-language literary, historical, scientific, and philosophical works published prior to 1929.
* **Intended IGRIS Use:** Core foundational English pretraining corpus; provides syntactic depth, narrative structures, and long-range dependencies (~1.1 billion Candidate A tokens; ~4.2 GB text).

### B. Official Source, Version & License Evidence
* **Official Source:** Project Gutenberg Literary Archive Foundation (PGLAF), Salt Lake City, UT (`https://www.gutenberg.org/`).
* **Exact Version:** PGLAF catalog snapshot 2024-01-01 (`cache/epub/*/*.txt`).
* **Primary License Status:** **Public Domain in the United States** (17 U.S.C. § 304) for pre-1929 works; subject to PGLAF Trademark License if trademark retained.
* **Evidence Supporting Classification:** PGLAF License Section 1.C, 1.D, 1.E.8.

### C. Legal Rights, Commercial Conditions & Trademark Analysis (CORRECTED)
* **Underlying Text Copyright:** Fully expired in the United States for pre-1929 publications.
* **PGLAF Trademark & License Section 1.E.8 (CORRECTED):**
  - Section 1.E.8 does **not** universally mandate stripping.
  - If a distributor retains the trademark "Project Gutenberg" and charges a fee or distributes derivative works, it must pay **20% of net profits as a royalty to PGLAF** under § 1.E.8.
  - *Elective Disclaimer Option:* Under § 1.C and § 1.E.8, a user may remove all references to "Project Gutenberg", trademarks, and license headers. Doing so disclaims the PGLAF license entirely, allowing unrestricted commercial use of the underlying public domain text without royalty obligations.
* **Item-Level Rights Status (CORRECTED):**
  - Catalog items are **not universally unrestricted**. Some titles are modern translations or copyrighted works donated with permission.
  - Item-level copyright notice verification is required before admitting any file.
* **Author Death Year Filter (CORRECTED):**
  - Filtering works by `author_death_year <= 1955` is a **preliminary technical screening tool**, not a definitive legal clearance. It does not account for joint authors, corporate works, or derivative translations.

### D. Privacy & PII Assessment (CORRECTED)
* **Living PII Status:** Classical literature features deceased historical authors. However, digital ebooks contain **living volunteer proofreader names, transcriber credits, and donor acknowledgments** in header blocks.
* **Control:** Elective header stripping removes volunteer transcriber notes.

### E. Benchmark Contamination & Technical Prerequisites
* **Contamination Risk:** Overlap screening required against BookCorpus, NarrativeQA, and PG19 evaluation sets.
* **Prerequisites:** Automated header/footer stripper; item-level copyright notice parser; author death date validator.

### F. Advantages, Disadvantages & Uncertainties
* **Advantages:** Massive syntactic volume (~1.1B tokens); zero third-party copyright claims if trademark disclaimed; $0 royalty cost.
* **Disadvantages:** 19th-century stylistic bias; lacks modern web jargon; item-level parsing required.
* **Uncertainties:** International copyright status of specific translated titles in Life+70 jurisdictions.

### G. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Authorizes sandbox design of header stripper and item-level copyright notice parser).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-EN-01                                             |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                             |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                             |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                             |
| [ ] OWNER_REJECTS_SOURCE                                                     |
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
* **Description:** ~9,500 Request for Comments documents (RFC 1 through RFC 9500+). Formal Internet protocol specifications, state machine descriptions, and algorithmic networking definitions (~140 million Candidate A tokens; ~550 MB text).

### B. Official Source, Version & License Evidence
* **Official Source:** RFC Editor / IETF (`https://www.rfc-editor.org/`).
* **Exact Version:** Plain-text official archive snapshot 2024-Q3 (`rfc*.txt`).
* **Primary License Status:** **IETF Trust Legal Provisions (TLP 5.0 Section 3.c)** / RFC 5378 / BCP 78.

### C. Legal Rights & Stream Variation Analysis (CORRECTED)
* **Licensing Non-Uniformity (CORRECTED):**
  - The RFC repository does **not** possess uniform licensing across all documents.
  - *The Pre-RFC 5378 Problem:* RFCs published prior to November 10, 2008 (RFC 1 through ~RFC 5377) were contributed under RFC 2026 or RFC 3978, where contributors did not grant broad derivative work rights. The IETF Trust adopted TLP Section 6.c to address legacy RFCs, but retroactive author assignments do not exist.
  - *Stream Variations:* Independent Submission Stream (ISE) and IRTF documents do not represent IETF consensus and may contain proprietary vendor legends or restricted modification terms.
* **Standards Integrity Restriction:** Derivative works cannot be published *as official IETF RFC standards*.
* **Commercial Model Pretraining:** Pretraining extracts statistical parameters and falls within broad analysis grants, but pre-5378 text carries historical ambiguity.

### D. Privacy & PII Assessment (CORRECTED)
* **Living PII Status:** RFC Author Addresses sections contain **real living networking engineers' names, business email addresses, physical office addresses, and telephone numbers**.
* **Mandatory Control:** Automated regex pipeline scrubbing all email patterns (`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`) and phone numbers prior to tokenization.

### E. Technical Prerequisites & Benchmark Contamination
* **Contamination Risk:** Negligible for modern NLP benchmarks; minor potential overlap with network certification exams.
* **Prerequisites:** Automated email and phone number scrubber; RFC stream classifier (isolating IETF Standards Track from Independent Streams).

### F. Advantages, Disadvantages & Uncertainties
* **Advantages:** Flawless formal technical English; protocol state machines; precise terminology.
* **Disadvantages:** ASCII diagrams and hex dumps require custom filtering; pre-5378 legal variations.
* **Uncertainties:** Status of pre-2008 legacy RFCs under international derivative work doctrines.

### G. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Authorizes sandbox design of email scrubber and stream filter isolating IETF Standards Track).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-TD-02                                             |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                             |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                             |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                             |
| [ ] OWNER_REJECTS_SOURCE                                                     |
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
* **Description:** Official Python 3.12 documentation: Language Reference, Library Reference, Tutorials, and HOWTOs (~22 million Candidate A tokens; ~85 MB text).

### B. Official Source, Version & License Evidence
* **Official Source:** Python Software Foundation (PSF), Beaverton, OR (`https://github.com/python/cpython` Doc/ / `https://docs.python.org/3/`).
* **Exact Version:** Python 3.12.7 documentation release (git tag `v3.12.7`).
* **Primary License:** **Python Software Foundation License Version 2 (PSF-2.0)**.
* **Operative Grant:** PSF-2.0 Section 2 explicitly grants rights to "reproduce, analyze, test... prepare derivative works, distribute, and otherwise use Python".

### C. Rights, Commercial Use & Attribution
* **Commercial Usability:** Permitted permissive (OSI/FSF approved).
* **Attribution:** Brief PSF copyright notice and disclaimer retained in dataset metadata ledger.

### D. Privacy & PII Assessment (CORRECTED)
* **Living PII Status:** Contains public acknowledgments, core developer names, and bug tracker contributor handles. Does not contain private addresses or sensitive personal data.
* **Control:** Retain developer names as public author credits.

### E. Benchmark Contamination (HIGH RELEVANCE)
* **Contamination Risk:** Python docstrings and tutorial examples contain coding problem statements and doctests that overlap directly with HumanEval and MBPP evaluation benchmarks.
* **Mandatory Control:** Docstring code prompt exclusion filter to screen against HumanEval and MBPP problem statements.

### F. Advantages, Disadvantages & Uncertainties
* **Advantages:** Clean permissive open-source license; structured software engineering prose; zero copyleft risk.
* **Disadvantages:** Modest corpus volume (~85 MB); benchmark leakage requires rigorous filtering.
* **Uncertainties:** None. Clean, established legal terms.

### G. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Authorizes sandbox design of RST text parser and HumanEval/MBPP screening filter).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-TD-03                                             |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                             |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                             |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                             |
| [ ] OWNER_REJECTS_SOURCE                                                     |
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
* **Description:** Crowd-sourced multi-turn conversational trees: human instructions paired with volunteer assistant responses (~55 million Candidate A tokens across ~161,000 English messages; ~210 MB text).
* **Intended IGRIS Use:** Instruction-tuning and conversational pretraining; teaches role tokens (`<user>=10`, `<assistant>=11`) and conversational turn-taking.

### B. Official Source, Version & License Evidence
* **Official Source:** LAION / OpenAssistant (`https://huggingface.co/datasets/OpenAssistant/oasst1`).
* **Exact Version:** Release v1.0, commit `289ed0f90ff8eb4b5b7c0fdbab26a29d5b0d02ea` (`2023-04-12_oasst_ready.trees.jsonl.gz`).
* **Primary License:** **Apache License 2.0**.
* **Provenance Evidence:** Contributor agreement explicitly assigning contributions under Apache-2.0.

### C. Legal Rights & Third-Party Content Risks (CORRECTED)
* **Commercial Usability:** Permitted permissive under Apache-2.0.
* **Third-Party Content Uncertainty (CORRECTED):** Volunteer crowd-workers may have pasted excerpts of third-party copyrighted text into prompts. Apache-2.0 § 7 disclaims warranties; long-form prompts require deduplication against web text to eliminate verbatim copyrighted excerpts.

### D. Privacy & PII Assessment (CORRECTED)
* **Living PII Status:** Volunteer prompters occasionally shared personal anecdotes, first names, or social media handles. Automated NER models have documented false negatives on informal or transliterated names.
* **Mandatory Control:** Automated regex and NER scrubber combined with random manual sample inspection.

### E. Language Scope & Benchmark Quarantine Invariants
* **Language Scope Filter:** OASST1 is multilingual. **Strict filtering `lang == 'en'` is mandatory.**
* **Validation Split Quarantine:** **The validation split must be strictly quarantined.** Ingestion restricted exclusively to `train` split.

### F. Advantages, Disadvantages & Uncertainties
* **Advantages:** High conversational quality; clean Apache-2.0 provenance; instruction-following alignment.
* **Disadvantages:** Incidental volunteer PII requires automated scrubbing; multilingual filtering required.
* **Uncertainties:** Potential third-party text in crowd prompts.

### G. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Authorizes sandbox design of `lang=='en'` filter, validation split quarantine, and PII scrubber).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-CV-03                                             |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                             |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                             |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                             |
| [ ] OWNER_REJECTS_SOURCE                                                     |
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
* **Description:** 8,438 task-oriented dialogues between tourists and informational clerks across 7 Cambridge domains (hotels, restaurants, attractions, trains, taxis, hospitals, police) (~12 million Candidate A tokens; ~45 MB text).
* **Intended IGRIS Use:** Slot-filling, multi-turn state tracking, structured entity extraction, and conversational goal resolution.

### B. Official Source, Version & License Evidence
* **Official Source:** Dialogue Systems Group, University of Cambridge (`https://github.com/smartyfh/MultiWOZ2.4`).
* **Exact Version:** Release v2.4, commit `89622d1` (`data.json` / `train.jsonl`).
* **Primary License Status:** **Apache License 2.0** (Repository LICENSE file).

### C. Data License vs. Code License Audit (CORRECTED)
* **The Repository vs. Data Split (CORRECTED):**
  - The GitHub repository root contains an Apache-2.0 license file.
  - However, MultiWOZ 2.4 is an error-corrected re-annotation of MultiWOZ 2.0 / 2.1.
  - Original dialogue utterances were collected via Amazon Mechanical Turk under academic research protocols.
  - **Audit Finding:** Whether the underlying dialogue utterances themselves are legally covered by Apache-2.0 or remain subject to academic research consent constraints is **UNVERIFIED**.
  - **Viable Decision Option:** The owner may reasonably select **`OWNER_REQUIRES_MORE_EVIDENCE`** to investigate the original Cambridge data release terms before accepting.

### D. Entity Reality & Privacy Assessment (CORRECTED)
* **Entity Reality Audit (CORRECTED — PREVIOUS CLAIM REFUTED):**
  - Previous claim of "zero real PII / all entities synthetic" is **factually false**.
  - The corpus database contains **real Cambridge commercial venue names** ("The Gonville Hotel", "Lensfield Hotel", "Pizza Hut City Centre"), **real physical street addresses** ("Gonville Place", "Lensfield Road"), **real UK postcodes** (`CB2 1SJ`, `CB1 2ER`), and **real landline telephone numbers** (`01223 ...`).
  - Synthetic elements are restricted to booking reference IDs (e.g. `7DFG987A`) and simulated tourist scenarios.
* **Privacy Implication:** Business directory data is public commercial information, but telephone numbers and addresses must be treated as real-world entity data, not synthetic fiction.

### E. Benchmark Contamination Invariant (CRITICAL)
* MultiWOZ `test.json` is the universal international benchmark for Dialogue State Tracking (DST).
* **Mandatory Control:** Strict quarantine of `test.json`. Ingestion restricted exclusively to `train.jsonl`.

### F. Advantages, Disadvantages & Uncertainties
* **Advantages:** Superb structured multi-turn goal resolution; excellent state tracking.
* **Disadvantages:** Contains real business contact info; small volume (~45 MB); data license vs. code license ambiguity.
* **Uncertainties:** Commercial licensing status of underlying crowd-worker utterances.

### G. Suggested Next Action
* **`OWNER_REQUIRES_MORE_EVIDENCE`** (Recommended to verify original Cambridge MultiWOZ 2.0 Mechanical Turk consent terms and data licensing) OR **`OWNER_ACCEPTS_FURTHER_REVIEW`** (conditional on test split quarantine).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-CV-05                                             |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                             |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                             |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                             |
| [ ] OWNER_REJECTS_SOURCE                                                     |
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
* **Description:** Classical dramatic dialogue extracted from pre-1929 theatrical plays (William Shakespeare, Oscar Wilde, George Bernard Shaw, J.M. Synge) (~6.5 million Candidate A tokens across ~120 plays; ~25 MB text).
* **Intended IGRIS Use:** Dramatic dialogue cadence, character turn-taking, conflict, and repartee.

### B. Official Source, Version & License Evidence
* **Official Source:** Project Gutenberg Literary Archive Foundation (`https://www.gutenberg.org/`).
* **Exact Version:** Pre-1929 dramatic plays catalog snapshot; permanent ID affirmed under `CORR-23B-01`.
* **Primary License Status:** **Public Domain in the United States** (17 U.S.C. § 304).

### C. Legal Rights & Edition Analysis (CORRECTED)
* **Playwright Copyright Status:**
  - Shakespeare (d. 1616), Wilde (d. 1900), Synge (d. 1909) are in public domain worldwide.
  - George Bernard Shaw (d. 1950): Works published pre-1929 entered public domain in Life+70 nations on January 1, 2021.
* **Edition Copyright Uncertainty (CORRECTED):**
  - Modern critical editions, translations, or scholarly annotations published after 1928 hold separate copyright.
  - Candidate texts must be verified as original English plays published pre-1929 without modern copyrighted apparatus.
* **Trademark Disclaimer:** Elective removal of "Project Gutenberg" trademark headers disclaims PGLAF license.

### D. Privacy & PII Assessment (CORRECTED)
* **Living PII Status:** Dramatic characters are fictional or historical. Incidental modern volunteer transcriber credits exist in PGLAF headers and are removed via header stripping.

### E. Advantages, Disadvantages & Uncertainties
* **Advantages:** High literary drama; rapid turn-taking; clean public domain status.
* **Disadvantages:** Archaic syntactic register; small corpus size (~25 MB).
* **Uncertainties:** None for original English classical texts published pre-1929.

### F. Suggested Next Action
* **`OWNER_ACCEPTS_FURTHER_REVIEW`** (Authorizes sandbox design of dramatic dialogue script parser and PGLAF header stripper).

```
+------------------------------------------------------------------------------+
| OWNER DECISION FIELD — SRC-CV-06                                             |
| Current Status: [X] NOT_REVIEWED                                             |
|                                                                              |
| [ ] OWNER_ACCEPTS_FURTHER_REVIEW                                             |
| [ ] OWNER_REQUIRES_LEGAL_COUNSEL                                             |
| [ ] OWNER_REQUIRES_MORE_EVIDENCE                                             |
| [ ] OWNER_REJECTS_SOURCE                                                     |
|                                                                              |
| Owner Notes: _______________________________________________________________ |
+------------------------------------------------------------------------------+
```

---

## 3. Preserved Status of Pending & Rejected Sources

In accordance with Phase 29A governance rules, all other candidate sources remain locked in their existing legal classifications:

### A. Tamil Corpora (Pending Legal Review)
* **`SRC-TM-01` (IndicCorp v2 Tamil):** `PENDING_LEGAL_REVIEW`. Blocker: Indian Copyright Act § 52(1)(a) TDM fair dealing gap for news publisher content.
* **`SRC-TM-02` (Tamil Wikipedia Dump):** `PENDING_LEGAL_REVIEW`. Blocker: CC-BY-SA 4.0 § 3(b) viral ShareAlike copyleft risk to model weights.
* **`SRC-TM-03` (OSCAR 23.01 Tamil):** `PENDING_LEGAL_REVIEW`. Blocker: ODC-By database license only; GDPR/DPDP right to erasure unlearning infeasibility.

### B. Tanglish Corpora (Two Pending, One Rejected)
* **`SRC-TG-01` (DravidianCodeMix):** `PENDING_LEGAL_REVIEW`. Blocker: YouTube Terms of Service § II.A automated scraping prohibition.
* **`SRC-TG-02` (IndicGLUE Tanglish Sentiment):** `PENDING_LEGAL_REVIEW`. Blocker: Social media scraping terms and evaluation benchmark contamination.
* **`SRC-TG-03` (Spoken Tanglish Transcripts):** **`REJECTED`**. Blocker: Non-commercial (NC/ND) clause permanently bars commercial model deployment.

### C. English Copyleft Corpus (Pending Legal Review)
* **`SRC-CV-07` (WikiDialog English):** `PENDING_LEGAL_REVIEW`. Blocker: Inpainted dialogue inherits CC-BY-SA copyleft from Wikipedia; QA evaluation overlap.
