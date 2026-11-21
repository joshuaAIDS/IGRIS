# IGRIS Milestone 3C.5 — Dataset Gap Resolution Plan

**Document Version:** 1.0.0  
**Status:** Canonical Gap Resolution Roadmap  
**Governing Standard:** `DATASET_SPECIFICATION.md` (Milestone 3B.59)  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

This document establishes the strategic, technical, and governance roadmap for resolving the two critical dataset coverage deficits identified during Milestone 3C.4:
1. **Category 5 Gap (Other Indian Languages)**: Initial lack of candidate sources for **Bengali (`bn`)** and **Gujarati (`gu`)**.
2. **Category 9 Deficit (Conversational Text)**: Disqualification of both initial candidate sources (`SRC-CV-01` and `SRC-CV-02`) due to non-commercial restrictions and copyright liabilities.

Through the rigorous research conducted in Milestone 3C.5, viable, unencumbered replacement sources have been identified for both categories, establishing a path toward **100% compliant benchmark coverage across all 10 categories**.

---

## 2. Updated 10-Category Target Composition

The following table summarizes the updated proposed benchmark composition, integrating the research findings from `BENGALI_GUJARATI_SOURCE_RESEARCH.md` and `CONVERSATIONAL_DATASET_RESEARCH.md`:

| ID | Benchmark Category | Proposed Source IDs | Selected Source Names | Governing License | Volume Status | Compliance Verdict |
|:---:|:---|:---|:---|:---:|:---:|:---:|
| **1** | **Tamil** | `SRC-TM-01` | IndicCorp v2 (Tamil) | `CC0-1.0` | 3.8 GB | **CLEARED (VERIFIED)** |
| **2** | **English** | `SRC-EN-01` | Project Gutenberg Open Archive | `Public Domain` | 12 GB | **CLEARED (VERIFIED)** |
| **3** | **Tanglish** | `SRC-TG-01`, `SRC-TG-02` | DravidianCodeMix + IndicGLUE | `CC-BY-4.0` | 60 MB | **CLEARED (VERIFIED)** |
| **4** | **Hindi** | `SRC-HI-01` | IndicCorp v2 (Hindi) | `CC0-1.0` | 12.5 GB | **CLEARED (VERIFIED)** |
| **5** | **Other Indian Languages** | `SRC-OI-01` to `03`<br/>`SRC-OI-04`, `SRC-OI-05` *(New)* | IndicCorp v2 (Telugu, Malayalam, Kannada)<br/>IndicCorp v2 (Bengali, Gujarati) | `CC0-1.0` (All 5) | 20.8 GB | **RESOLVED (CC0 BASELINE)** |
| **6** | **Multilingual Mixed Text** | `SRC-ML-01`, `SRC-ML-02` | FLORES-200 + mC4 Sample | `CC-BY-SA` / `ODC-By` | 585 MB | **REQUIRES HUMAN APPROVAL** |
| **7** | **Programming Code** | `SRC-CD-01`, `SRC-CD-02` | The Stack v2 (Permissive) + HumanEval | `MIT/Apache/BSD` | >2 GB | **CLEARED (VERIFIED)** |
| **8** | **Technical Documentation** | `SRC-TD-02`, `SRC-TD-03` | IETF RFCs + Python Docs | `RFC Trust` / `PSF-2.0` | 430 MB | **CLEARED (VERIFIED)** |
| **9** | **Conversational Text** | `SRC-CV-03`, `SRC-CV-04`<br/>`SRC-CV-06` *(New)* | OpenAssistant (OASST1) + Anthropic HH-RLHF<br/>Project Gutenberg Theatrical Dialogue | `Apache-2.0`<br/>`MIT`<br/>`Public Domain` | ~115 MB | **RESOLVED (PERMISSIVE BASELINE)** |
| **10** | **Emoji & Unicode Edge Cases** | `SRC-EM-01`, `SRC-EM-02` | Unicode 15.1.0 UCD + Emoji Test Suites | `Unicode-DFS-2016` | 39 MB | **CLEARED (VERIFIED)** |

---

## 3. Four-Stage Gap Resolution Protocol

To transition from the current research state to authorized acquisition without violating governance boundaries, IGRIS enforces a strict **Four-Stage Resolution Protocol**:

```
[ STAGE 1: Research & Verification ]  ==> COMPLETED in Milestone 3C.5
  - Identify unencumbered public sources for Bengali, Gujarati, and Conversational Text.
  - Audit licenses (CC0-1.0, Apache-2.0, MIT, Public Domain).
  - Draft research findings (zero downloads executed).
                |
                v
[ STAGE 2: Human Governance Review ]  ==> ACTIVE (Milestone 3C.5 / 3C.6)
  - Deliver role-specific review documents to the 4 governance authorities.
  - Review questions, evidence, and risk registers.
  - Await authentic human digital signatures. Gate remains LOCKED.
                |
                v
[ STAGE 3: Controlled Sandbox Acquisition ]  ==> FUTURE (Milestone 3C.6+)
  - Authorized ONLY after all 4 human approvals transition to APPROVED.
  - Physical ingress into isolated `quarantine/datasets/<id>/` sandbox.
  - Upstream SHA-256 pre-validation prior to archive extraction.
                |
                v
[ STAGE 4: Staging, Scrubbing & Stratification ] ==> FUTURE (Milestone 3C.7+)
  - Automated UTF-8 validation and Unicode 15.1.0 NFC normalization.
  - Automated regex PII screening and secret scanning.
  - 13-gram benchmark decontamination check.
  - Stratification into Sequence Tiers 1–4 across all 10 categories.
```

---

## 4. Governance Invariants & Safety Enforcement

1. **Default-Deny Gate Preservation**:
   - The production dataset access gate (`scripts/dataset_authorization.py`) remains locked in the `LOCKED` state.
   - No script or agent is authorized to download remote data.
2. **Zero Architecture Changes**:
   - The approved Transformer architecture (16 layers, 512 hidden, 8 attention heads, 4 KV heads [GQA], 2,048 context length, 32,768 vocabulary, structural tokens 0–11) remains immutable.
3. **Candidate Invariance**:
   - Candidate A (ByteLevel BPE) and Candidate B (SentencePiece Unigram) remain unaltered and ready for comparative evaluation.
