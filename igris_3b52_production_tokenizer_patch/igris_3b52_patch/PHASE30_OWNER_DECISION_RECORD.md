# PHASE 30 — OWNER DATASET DECISION RECORD

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Confirmation Date:** 2026-11-20  
**Phase:** Phase 30 (Record Approved Owner Dataset Decisions)  
**Approved Language Scope:** Strictly **Tamil**, **English**, and **Tanglish** (All other languages remain `OUT_OF_SCOPE`)  

---

## 1. Official Owner Decisions

On 2026-11-20, the sole project owner explicitly confirmed and approved the following source-level decisions for the six candidate English datasets audited in Phase 29/29B:

| Source ID | Dataset Name | Approved Owner Decision | Approval Date | Operational Status |
| :--- | :--- | :--- | :---: | :--- |
| **`SRC-EN-01`** | Project Gutenberg English Subset | `OWNER_REQUIRES_MORE_EVIDENCE` | 2026-11-20 | BLOCKED (Pending Item-Level Rights Audit) |
| **`SRC-TD-02`** | IETF RFC Repository | `OWNER_REQUIRES_MORE_EVIDENCE` | 2026-11-20 | BLOCKED (Pending Post-5378 Stream Filter) |
| **`SRC-TD-03`** | Python Official Documentation | `OWNER_ACCEPTS_FURTHER_REVIEW` | 2026-11-20 | NON-PRODUCTION PLANNING PERMITTED |
| **`SRC-CV-03`** | OpenAssistant OASST1 English | `OWNER_ACCEPTS_FURTHER_REVIEW` | 2026-11-20 | NON-PRODUCTION PLANNING PERMITTED |
| **`SRC-CV-05`** | MultiWOZ 2.4 English Subset | `OWNER_REQUIRES_MORE_EVIDENCE` | 2026-11-20 | BLOCKED (Pending Data License Deed & Entity Review) |
| **`SRC-CV-06`** | Gutenberg Theatrical Dialogue | `OWNER_REQUIRES_MORE_EVIDENCE` | 2026-11-20 | BLOCKED (Pending Item-Level Play Rights Audit) |

---

## 2. Rigorous Decision Interpretation

### 2.1 Interpretation of `OWNER_ACCEPTS_FURTHER_REVIEW`
Applies exclusively to:
- **`SRC-TD-03`** (Python Official Documentation)
- **`SRC-CV-03`** (OpenAssistant OASST1 English)

#### Permitted Actions:
- Non-production technical evaluation of data structures, token fragmentation, and formatting.
- Additional evidence collection from authoritative upstream repositories and primary license files.
- Refinement of license scope and provenance verification ledgers.
- Design of privacy, PII-scrubbing, and regex/NER masking specifications.
- Specification and design of isolated sandbox data pipelines.
- Synthetic-only test fixture generation and validation scripts.
- Non-production planning and prerequisite documentation.

#### Strictly Prohibited Actions:
- **NO production dataset downloads.**
- **NO production ingestion or quarantine ingress.**
- **NO model pretraining or tokenizer training on these datasets.**
- **DO NOT treat this decision as legal clearance or a blanket indemnity.**
- **DO NOT treat this decision as an acquisition grant or spend authorization.**

---

### 2.2 Interpretation of `OWNER_REQUIRES_MORE_EVIDENCE`
Applies exclusively to:
- **`SRC-EN-01`** (Project Gutenberg English Literature)
- **`SRC-TD-02`** (IETF RFC Repository)
- **`SRC-CV-05`** (MultiWOZ 2.4 English Subset)
- **`SRC-CV-06`** (Project Gutenberg Theatrical Dialogue)

#### Governing Principles:
- These four sources remain **strictly BLOCKED** from any acquisition, staging, or ingestion.
- The outstanding evidence requirements identified in Phase 29B must be satisfied before any reconsideration:
  1. **`SRC-EN-01` & `SRC-CV-06` (Project Gutenberg):** Comprehensive item-level copyright notice audits for each proposed ebook ID. Catalog inclusion does not equal public domain (some works are donated under active copyright, e.g. Ebook #10007). Author death $\le 1955$ filter is a preliminary screening heuristic that requires confirmation against authoritative death registers. Complete removal of PGLAF trademark headers under Section 1.C must be programmatically verified to avoid the Section 1.E.8 20% commercial gross-profit royalty.
  2. **`SRC-TD-02` (IETF RFC):** Filtering to isolate post-November 10, 2008 Standards Track RFCs (governed by TLP 5.0 § 3.c). Pre-RFC 5378 legacy contributions have unverified machine-learning derivative rights outside the standards process. Independent Submission Stream (ISE) vendor disclosures must be screened out.
  3. **`SRC-CV-05` (MultiWOZ 2.4):** Primary data licensing deed must be verified. Repository Apache-2.0 applies to code, not underlying Mechanical Turk crowd dialogues. Review and clearance of authentic Cambridge commercial entities (hotels, postcodes, phone numbers). Mandatory quarantine protocol for `test.json` Dialogue State Tracking benchmark.
- Unresolved risks are preserved without downgrade or removal.

---

## 3. Preservation of Legal Blockers and Out-of-Scope Languages

All other source statuses remain entirely unmodified:

```
+-----------------------------------------------------------------------------------------+
| PRESERVED SOURCE STATUSES (UNCHANGED)                                                   |
+-----------------------------------------------------------------------------------------+
|  English Candidates:                                                                    |
|    - SRC-CV-07 (WikiDialog English):            PENDING_LEGAL_REVIEW (CC-BY-SA 3.0/4.0) |
|    - SRC-CV-01 (DailyDialog):                   REJECTED (Non-Commercial Clause)        |
|    - SRC-CV-04 (Anthropic HH-RLHF):             REJECTED (Alignment Leakage Hazard)     |
|                                                                                         |
|  Tamil Candidates:                                                                      |
|    - SRC-TM-01 (IndicCorp v2 Tamil):            PENDING_LEGAL_REVIEW (TDM Scraping Gap) |
|    - SRC-TM-02 (Tamil Wikipedia Dump):          PENDING_LEGAL_REVIEW (ShareAlike Risk)  |
|    - SRC-TM-03 (OSCAR 23.01 Tamil):             PENDING_LEGAL_REVIEW (Database Rights)  |
|                                                                                         |
|  Tanglish Candidates:                                                                   |
|    - SRC-TG-01 (DravidianCodeMix YouTube):      PENDING_LEGAL_REVIEW (YouTube ToS Ban)  |
|    - SRC-TG-02 (IndicGLUE Tanglish Sentiment):  PENDING_LEGAL_REVIEW (Platform Terms)   |
|    - SRC-TG-03 (Spoken Tanglish Transcripts):   REJECTED (Non-Commercial Clause)        |
|                                                                                         |
|  Excluded Language Scope (OUT_OF_SCOPE):                                                |
|    - SRC-HI-01 (Hindi IndicCorp v2):            OUT_OF_SCOPE                            |
|    - SRC-OI-01 (Telugu IndicCorp v2):           OUT_OF_SCOPE                            |
|    - SRC-OI-02 (Malayalam IndicCorp v2):        OUT_OF_SCOPE                            |
|    - SRC-OI-03 (Kannada IndicCorp v2):          OUT_OF_SCOPE                            |
|    - SRC-OI-04 (Bengali IndicCorp v2):          OUT_OF_SCOPE                            |
|    - SRC-OI-05 (Gujarati IndicCorp v2):         OUT_OF_SCOPE                            |
+-----------------------------------------------------------------------------------------+
```

**Scope Invariant:** The approved project languages remain strictly:
1. **Tamil**
2. **English**
3. **Tanglish**

No other languages are permitted or added to the project.

---

## 4. Mandatory Governance Locks

```
+-------------------------------------------------------------------------+
|                  IGRIS HARDWARE & PIPELINE INVARIANTS                   |
+-------------------------------------------------------------------------+
|  Production Data Ingress Gate:      LOCKED (0 bytes admitted)           |
|  Quarantine Ingress Gate:           LOCKED (0 bytes admitted)           |
|  Acquisition Grants:                NONE AUTHORIZED (Count = 0)         |
|  Tokenizer Training Gate:           UNAUTHORIZED                        |
|  Model Pretraining Gate:            LOCKED                              |
|  Cloud Infrastructure Spending:     $0.00                               |
|  Candidate A SHA-256 Hash:          ac7e18b13973450b43bfff18609a833...  |
|  Candidate B SHA-256 Hash:          d3a3431e07c87ecce863647202ddc9b...  |
|  Vocabulary Size:                   32,768 (Frozen)                     |
|  Structural Tokens:                 IDs 0–11 (Pinned)                   |
|  Language Scope:                    Tamil, English, Tanglish ONLY       |
+-------------------------------------------------------------------------+
```
