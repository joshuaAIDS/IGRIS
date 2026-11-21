# PHASE 31A — OWNER POLICY DECISIONS & TECHNICAL SPECIFICATION FREEZE

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Confirmation Date:** 2026-11-20  
**Phase:** Phase 31A (Owner Policy Confirmation and Technical Specification Freeze)  
**Approved Language Scope:** Strictly **Tamil**, **English**, and **Tanglish**  

---

## 1. Executive Summary & Policy Confirmations

On 2026-11-20, the sole project owner explicitly established and frozen the operational policies governing the non-production evaluation of **`SRC-TD-03`** (Python Official Documentation) and **`SRC-CV-03`** (OpenAssistant OASST1 English).

### The Three Core Policy Confirmations:
1. **Benchmark Similarity Policy (Python Docs):**
   - Similarity $\ge 0.70$ triggers mandatory manual review (`MANUAL_REVIEW_REQUIRED`).
   - Similarity $\ge 0.85$ triggers mandatory manual review (`MANUAL_REVIEW_REQUIRED`), indicating heightened concern.
   - **Absolute Invariant:** *No similarity score alone may automatically reject a record.* Both thresholds mandate human review, preventing false-positive pruning of canonical programming constructs.
2. **Privacy Masking Policy:**
   - Approved Placeholders: `[EMAIL_REDACTED]` and `[PHONE_REDACTED]`.
   - Masking occurs strictly on identified spans without corrupting surrounding Unicode text (NFC normalization preserved).
   - Machine-readable audit logs preserve span offsets and one-way SHA-256 hashes; raw sensitive values are never logged in ordinary records.
   - Uncertain PII and sensitive unstructured narratives must be held for manual review or rejected; *they must never be silently accepted*.
3. **OASST1 Language Routing Policy:**
   - Multi-stage gate: Dataset metadata -> IGRIS `LanguageIdentifierV2` -> Confidence-based routing -> Code-switch/Tanglish detection -> Manual review for uncertain records.
   - Latin script is explicitly recognized as ambiguous; Romanized Tamil and Tamil-English code-switching are routed to Tanglish, never admitted to the English candidate set.

---

## 2. Review States Taxonomy

The following five standardized review states are approved for benchmark and privacy triage:

| State Code | Definition | Automated Assignment Permitted? |
| :--- | :--- | :---: |
| `NOT_REVIEWED` | Initial baseline state for clean records below screening thresholds | YES |
| `MANUAL_REVIEW_REQUIRED` | Triggered by threshold exceedance ($\ge 0.70$), uncertain PII, or ambiguous language | YES |
| `OWNER_ACCEPTED` | Explicitly cleared by sole project owner after manual inspection | **NO (Owner Only)** |
| `OWNER_REJECTED` | Explicitly excluded by sole project owner after manual inspection | **NO (Owner Only)** |
| `INSUFFICIENT_EVIDENCE` | Document held pending additional upstream provenance or context | YES / Owner |

---

## 3. Preserved Governance Invariants

```
+-------------------------------------------------------------------------+
|                  IGRIS HARDWARE & PIPELINE INVARIANTS                   |
+-------------------------------------------------------------------------+
|  Production Datasets Downloaded:    0                                   |
|  Production Bytes Admitted:         0 bytes                             |
|  Production Data Ingress Gate:      LOCKED                              |
|  Quarantine Ingress Gate:           LOCKED                              |
|  Acquisition Grants Created:        0 (Zero authorized)                 |
|  Tokenizer Training Gate:           UNAUTHORIZED                        |
|  Model Pretraining Gate:            LOCKED                              |
|  Cloud Infrastructure Spending:     $0.00                               |
|  Candidate A SHA-256 Hash:          ac7e18b13973450b43bfff18609a833...  |
|  Candidate B SHA-256 Hash:          d3a3431e07c87ecce863647202ddc9b...  |
|  Vocabulary Size:                   32,768 (Frozen)                     |
|  Structural Tokens:                 IDs 0–11 (Pinned)                   |
|  Approved Language Scope:           Tamil, English, Tanglish ONLY       |
|  SRC-TD-03 & SRC-CV-03 Status:      OWNER_ACCEPTS_FURTHER_REVIEW        |
|  Four Blocked Sources:              OWNER_REQUIRES_MORE_EVIDENCE        |
|  Preserved Legal Blockers:          TM-01..03, TG-01..03, CV-07         |
+-------------------------------------------------------------------------+
```
