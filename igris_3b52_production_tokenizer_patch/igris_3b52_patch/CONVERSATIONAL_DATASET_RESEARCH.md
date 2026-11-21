# IGRIS Milestone 3C.5 — Conversational Dataset Research Report

**Document Version:** 1.0.0  
**Status:** Human Review Proposal  
**Governing Standard:** `DATASET_SPECIFICATION.md` (Milestone 3B.59)  
**Target Category:** Category 9 (Conversational Text)  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

In Milestone 3C.4, the category coverage audit revealed a **zero compliant coverage** state for **Category 9: Conversational Text**. Both candidate sources originally listed in `DATASET_SOURCE_CATALOG.csv` were legally disqualified:
1. `SRC-CV-01` (DailyDialog): Disqualified due to an explicit **Non-Commercial (`NC`)** restriction in `CC-BY-NC-SA 4.0`.
2. `SRC-CV-02` (OpenSubtitles Multilingual): Disqualified due to **severe third-party copyright liability** resulting from unauthorized scraping of commercial film and television dialogue.

This report investigates legally unencumbered, permissively licensed conversational datasets suitable for language model evaluation and tokenizer benchmarking, enforcing strict rejection criteria.

---

## 2. Strict Rejection Criteria & Analysis of Disqualified Corpora

To safeguard the IGRIS project from regulatory, contractual, and copyright litigation, candidate conversational datasets were systematically audited against four disqualification gates:

```
[ Candidate Conversational Source ]
               |
               v
  1. Contains Non-Commercial clause (NC)? ------> [ REJECTED: Violates Commercial Policy ]
               | NO
               v
  2. Scraped without copyright authorization? -> [ REJECTED: Third-Party Copyright Liability ]
               | NO
               v
  3. Violates Platform Terms of Service? -------> [ REJECTED: Contractual Breach ]
               | NO
               v
  4. Contains unscrubbed PII / toxic data? -----> [ REJECTED: DPDP Act 2023 Non-Compliance ]
               | NO
               v
      [ CANDIDATE ACCEPTED FOR REVIEW ]
```

### 2.1 Audit of Disqualified Conversational Corpora

| Disqualified Source | Stated / Applied License | Specific Disqualification Root Cause |
| :--- | :--- | :--- |
| **DailyDialog (`SRC-CV-01`)** | `CC-BY-NC-SA 4.0` | **Non-Commercial Restriction**. Section 2.a strictly forbids commercial exploitation; derived model weights cannot be deployed commercially. |
| **OpenSubtitles (`SRC-CV-02`)** | Scraped Crowd Subtitles | **Third-Party Copyright Infringement**. Dialogues are literal transcriptions of copyrighted commercial motion pictures owned by studios. |
| **Cornell Movie-Dialogs** | Research-Only / Fair Use | **Third-Party Copyright Infringement**. Scraped directly from copyrighted screenplays. No commercial training grant exists. |
| **Reddit / Pushshift Dumps** | Reddit Terms of Service | **Terms of Service Breach & PII Liability**. Reddit's Data API terms explicitly forbid commercial AI model training without enterprise licensing; extreme PII risk. |
| **Twitter / X Conversational Scrapes** | X Terms of Service | **Contractual Breach**. X Developer Agreement strictly prohibits scraping and AI training without enterprise authorization. |
| **PersonaChat / ConvAI2** | CC-BY-NC 4.0 | **Non-Commercial Restriction**. Restricts usage strictly to non-commercial academic benchmarking. |

---

## 3. Compliant Conversational Candidate Research

The following four conversational sources have been identified as completely free of non-commercial clauses, free of unauthorized scraping, and licensed under open permissive terms:

### 3.1 Candidate Source 1: OpenAssistant Conversations (OASST1 / OASST2) — [RECOMMENDED]
- **Proposed ID**: `SRC-CV-03`
- **Dataset Name**: OpenAssistant Conversations (OASST1)
- **Dataset Owner**: LAION / OpenAssistant Community / Volunteer Contributors
- **Official Source URL**: `https://huggingface.co/datasets/OpenAssistant/oasst1`
- **Official License URL**: `https://www.apache.org/licenses/LICENSE-2.0`
- **Exact License**: `Apache-2.0`
- **Published Size Estimate**: ~161,000 message trees across 35 languages (~50 MB JSONL)
- **Language / Script**: Multilingual (English, Hindi, and Indian language conversation trees)
- **Commercial Use Allowed**: **YES** (Explicit commercial grant under Apache-2.0 §2)
- **Modification & Redistribution**: **YES** (Standard Apache-2.0 notice preservation)
- **Tokenizer / Model Training Rights**: **YES** (Created explicitly for open-source language model training and alignment)
- **Provenance**: Authentically crowdsourced human dialogue trees created by volunteer contributors under a formal Contributor License Agreement (CLA).
- **PII & Safety Assessment**: Low PII risk; volunteer contributors instructed not to submit personal data; community moderation applied.
- **Strategic Fit**: **TIER 1 (PRIMARY CANDIDATE)**. Modern multi-turn assistant-style conversational dialogue under Apache-2.0.

### 3.2 Candidate Source 2: Anthropic HH-RLHF (Helpful & Harmless Dialogue) — [RECOMMENDED]
- **Proposed ID**: `SRC-CV-04`
- **Dataset Name**: Anthropic Human Evaluation & Feedback Conversations (HH-RLHF)
- **Dataset Owner**: Anthropic (Bai et al.)
- **Official Source URL**: `https://github.com/anthropics/hh-rlhf`
- **Official License URL**: `https://github.com/anthropics/hh-rlhf/blob/master/LICENSE`
- **Exact License**: `MIT`
- **Published Size Estimate**: ~160,000 multi-turn human-model conversational sessions (~40 MB)
- **Commercial Use Allowed**: **YES** (Permissive MIT license)
- **Modification & Redistribution**: **YES**
- **Tokenizer / Model Training Rights**: **YES** (Permitted under MIT)
- **Provenance**: Synthetic and human-curated conversational dialogues developed by Anthropic for safety and helpfulness evaluations.
- **PII & Safety Assessment**: Very Low PII risk; pre-screened for harmfulness and red-teamed.
- **Strategic Fit**: **TIER 1 (PRIMARY CANDIDATE)**. Permissive MIT license with zero copyleft risk.

### 3.3 Candidate Source 3: MultiWOZ 2.4 (Multi-Domain Task Dialogue)
- **Proposed ID**: `SRC-CV-05`
- **Dataset Name**: MultiWOZ 2.4 (Multi-Domain Wizard-of-Oz)
- **Dataset Owner**: University of Cambridge Dialogue Systems Group (Budzianowski et al.)
- **Official Source URL**: `https://github.com/budzianowski/multiwoz`
- **Official License URL**: `https://www.apache.org/licenses/LICENSE-2.0`
- **Exact License**: `Apache-2.0`
- **Published Size Estimate**: ~10,400 dialogues (~143,000 turns, ~15 MB)
- **Commercial Use Allowed**: **YES**
- **Provenance**: Crowd-sourced simulated goal-oriented conversational dialogue (booking, customer service, scheduling).
- **Strategic Fit**: **TIER 1 (TASK DIALOGUE SUPPLEMENT)**. Excellent representation of structured goal-oriented conversation.

### 3.4 Candidate Source 4: Project Gutenberg Theatrical Dramatic Dialogue
- **Proposed ID**: `SRC-CV-06`
- **Dataset Name**: Project Gutenberg Public Domain Dramatic Plays & Theatrical Dialogues
- **Dataset Owner**: Project Gutenberg Literary Archive Foundation
- **Official Source URL**: `https://www.gutenberg.org/`
- **Official License URL**: `https://www.gutenberg.org/policy/license.html`
- **Exact License**: `Public Domain` (US)
- **Published Size Estimate**: Thousands of dramatic scenes (~25 MB clean conversational text)
- **Commercial Use Allowed**: **YES** (Public Domain)
- **Provenance**: Published stage plays (multi-party turn-taking conversation) published before 1928 (e.g. Oscar Wilde, George Bernard Shaw, Shakespeare, classic dramatic adaptations).
- **Strategic Fit**: **TIER 1 (ZERO-RISK BASELINE)**. Zero copyright encumbrance, zero PII, and natural turn-taking structure.

---

## 4. Proposed Category 9 Remediation Plan

To resolve the Category 9 deficit without introducing legal risk, the following three-source blend is proposed for human review:

| Proposed ID | Dataset Name | License | Format | Primary Role |
| :--- | :--- | :---: | :--- | :--- |
| **`SRC-CV-03`** | OpenAssistant Conversations (OASST1) | `Apache-2.0` | JSONL multi-turn trees | Modern interactive dialogue |
| **`SRC-CV-04`** | Anthropic HH-RLHF | `MIT` | Text conversational turns | Multi-turn user-assistant queries |
| **`SRC-CV-06`** | Project Gutenberg Theatrical Dialogue | `Public Domain` | Formatted multi-party dialogue | Pure unencumbered dialogue |

### Compliance Verification:
- **Commercial Rights**: 100% permitted under Apache-2.0, MIT, and Public Domain.
- **Copyleft Taint**: Zero copyleft clauses (no ShareAlike, no GPL).
- **Non-Commercial Restrictions**: Zero `NC` clauses.
- **PII Exposure**: Minimal; pre-screened and historical.

---

## 5. Governance Action & Next Steps

1. **Submit to Human Review Panel**: This proposal is submitted to `LEGAL_GOVERNANCE`, `DATA_CUSTODIAN`, `SECURITY_PRIVACY`, and `CHIEF_ARCHITECT` as part of `DATASET_GAP_RESOLUTION_PLAN.md`.
2. **Lock Enforced**: Zero downloads or staging will take place until all four human approvals are cryptographically executed.
