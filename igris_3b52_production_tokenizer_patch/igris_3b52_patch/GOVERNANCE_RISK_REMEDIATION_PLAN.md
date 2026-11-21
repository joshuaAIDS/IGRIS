# IGRIS Governance Risk Register & Remediation Plan

**Project**: IGRIS Multilingual Decoder-Only Transformer  
**Active Patch**: `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Classification**: RISK GOVERNANCE & REMEDIATION  
**Status**: ACTIVE & ACTIONABLE  
**Audit Date**: 2026-11-17  
**Gatekeeper Status**: LOCKED (Default-Deny Active)  

---

## 1. Executive Summary

This document presents the Phase 3 governance risk analysis and comprehensive remediation plan for the IGRIS dataset acquisition and training pipeline.

While the technical framework enforces fail-closed cryptographic gatekeeping, several high-impact legal, ethical, and architectural risks remain inherent to the candidate data sources. Under the IGRIS governance charter, these risks must be formally remediated or accepted by the designated human roles prior to unlocking the dataset acquisition gate.

---

## 2. Governance Risk Matrix

```mermaid
quadrantChart
    title Risk Severity vs. Remediation Complexity
    x-axis Low Remediation Complexity --> High Remediation Complexity
    y-axis Low Severity --> High Severity
    quadrant-1 High Impact / Difficult (Prioritize & Isolate)
    quadrant-2 High Impact / Actionable (Enforce Immediately)
    quadrant-3 Low Impact / Manageable (Standard SOP)
    quadrant-4 Low Impact / Nuanced (Monitor Closely)
    "R1: Copyleft Viral Risk (CC-BY-SA 4.0)": [0.85, 0.90]
    "R2: Non-US Jurisdiction Copyright (Section 52)": [0.75, 0.82]
    "R3: Public Domain Vital Dates (Life+60)": [0.35, 0.70]
    "R4: Non-Commercial Contamination (NC Clause)": [0.20, 0.95]
    "R5: Synthetic Data Loops & Model Collapse": [0.65, 0.60]
    "R6: Evaluation-Only Scope Leakage (HH-RLHF)": [0.25, 0.78]
    "R7: Reviewer Key Compromise & Stale Creds": [0.30, 0.50]
```

---

## 3. Detailed Risk Assessment & Actionable Remediation Plans

### Risk R1: ShareAlike / Copyleft Contamination (CC-BY-SA 4.0)
- **Sources Affected**: `SRC-TM-02` (Tamil Wikipedia), `SRC-HI-02` (Hindi Wikipedia), `SRC-OI-04` (IndicCorp v2 Bengali), `SRC-OI-05` (IndicCorp v2 Gujarati).
- **Description**: Creative Commons ShareAlike 4.0 requires any "Adaptation" to be distributed under the same license terms. While tokenizing or training on text is often treated as non-infringing functional ingestion, aggressive copyright theories claim model weights could be construed as derivative works, potentially compelling the open-sourcing or relicensing of proprietary model weights.
- **Severity**: HIGH | **Likelihood**: MEDIUM | **Risk Owner**: `LEGAL_GOVERNANCE`
- **Remediation Plan**:
  1. *Isolated Evaluation*: Restrict CC-BY-SA 4.0 sources strictly to runtime evaluation (fertility and perplexity calculation), avoiding all gradient updates or tokenizer vocabulary inclusion.
  2. *Legal Opinion*: Legal Governance must issue an explicit jurisdiction-specific ruling on whether unweighted tokenization constitutes an "Adaptation" under Section 14 of the Indian Copyright Act and EU Directive 2019/790.
  3. *Dual Licensing or Alternate Sources*: Where possible, acquire data under CC0 or permissive academic licenses (e.g. AI4Bharat IndicCorp permissive research terms).

---

### Risk R2: Scraping & Fair Dealing in Non-US Jurisdictions (Section 52)
- **Sources Affected**: `SRC-TD-01` (Common Crawl Indic subsets), `SRC-EN-02` (Common Crawl English).
- **Description**: Common Crawl contains unvetted web-scraped material that includes proprietary, copyrighted, and paywalled articles. Unlike the US fair use doctrine (17 U.S.C. § 107), India's Section 52(1)(a) provides an enumerated list of "fair dealing" exceptions (research, private study, criticism, news reporting) that does not explicitly include commercial AI model training.
- **Severity**: HIGH | **Likelihood**: HIGH | **Risk Owner**: `LEGAL_GOVERNANCE` & `DATA_CUSTODIAN`
- **Remediation Plan**:
  1. *Domain Exclusion Filtering*: Apply automated blocklists for news publications, proprietary blogs, and opt-out domains (`robots.txt`, CC-crawl exclusions).
  2. *Heuristic Content Filtering*: Filter out full-length literary or artistic works scraped from web mirrors.
  3. *Strict Screening*: Legal Governance sign-off must mandate that only open-access web documentation is retained.

---

### Risk R3: Public Domain Vital Date Calculation (India Life+60 vs EU Life+70)
- **Sources Affected**: `SRC-EN-01` (Project Gutenberg English Literature), `SRC-CV-06` (Project Gutenberg Theatrical Dialogue).
- **Description**: Project Gutenberg US public domain clearance relies on US pre-1929 publication rules. However, under Section 22 of the Indian Copyright Act, 1957, copyright expires 60 years after the calendar year of the author's death (Life + 60; authors dying $\le 1965$ entered PD in 2026). In the UK/EU, copyright lasts Life + 70 (authors dying $\le 1955$ entered PD in 2026). A blanket pre-1929 rule causes international copyright infringement for authors who died after 1965 or 1955.
- **Severity**: HIGH | **Likelihood**: MEDIUM | **Risk Owner**: `LEGAL_GOVERNANCE`
- **Remediation Plan**:
  1. *Item-Level Vital Date Ledger*: Mandatory metadata catalog recording author death year, translator death year, and publication edition date for every text acquired from Project Gutenberg.
  2. *Automated Rule Filter*: Reject any text whose author or translator died after 1965 (for Indian operations) or after 1955 (for international operations).
  3. *Trademark Scrubbing*: Strip all Project Gutenberg trademarks, headers, and boilerplate before corpus assembly.

---

### Risk R4: Non-Commercial (NC) Clause Infiltration
- **Sources Affected**: `SRC-TG-03` (Social Dravidian Sentiment), `SRC-HI-03` (IIT Bombay Parallel Corpus), `SRC-CV-01` (DailyDialog Dataset).
- **Description**: Ingestion of NC-restricted datasets into commercial enterprise foundation model pipelines creates severe breach-of-contract and copyright infringement liabilities.
- **Severity**: CRITICAL | **Likelihood**: LOW (Currently Blocked) | **Risk Owner**: `CHIEF_ARCHITECT` & `LEGAL_GOVERNANCE`
- **Remediation Plan**:
  1. *Permanent Pipeline Purge*: `SRC-TG-03`, `SRC-HI-03`, and `SRC-CV-01` have been codified as `INELIGIBLE_REJECTED` in `DATASET_SOURCE_CATALOG_V3.csv` and `PIPELINE_AUTHORIZATION_MATRIX_V2.csv`.
  2. *Automated Gate Block*: The `dataset_authorization.py` gatekeeper rejects any record containing `NC` or `Non-Commercial` in its license string.
  3. *Quorum Consensus*: Ensure all 4 review packages uphold the `REJECT` recommendation for these sources.

---

### Risk R5: Synthetic Data Provenance & Model Collapse
- **Sources Affected**: `SRC-CV-03` (OpenAssistant OASST1), `SRC-CV-05` (UltraChat Curated Dialogue).
- **Description**: High ratios of synthetic or AI-generated text in training datasets can lead to linguistic degeneration, repetitive hallucination loops, and severe model collapse. Furthermore, synthetic data terms of service (e.g. OpenAI ToS prohibiting competing model training) create IP risks.
- **Severity**: MEDIUM | **Likelihood**: HIGH | **Risk Owner**: `CHIEF_ARCHITECT` & `SECURITY_PRIVACY`
- **Remediation Plan**:
  1. *Synthetic Proportion Cap*: Tokenizer vocabulary training is restricted to 0% synthetic data (100% human-authored text).
  2. *Provenance Tracking*: Retain lineage metadata identifying exact teacher models used in synthetic corpora.
  3. *N-Gram & Diversity Filtering*: Run automatic diversity checks to remove low-entropy repetitive conversational patterns.

---

### Risk R6: Scope Leakage of Alignment Pairs (HH-RLHF)
- **Sources Affected**: `SRC-CV-04` (Anthropic HH-RLHF).
- **Description**: Anthropic HH-RLHF contains preference pairs (chosen/rejected turns) specifically designed for safety and preference tuning. Inadvertently training tokenizer vocabularies or language model pre-training on rejected (harmful/toxic) responses would contaminate the base model with harmful tokens and sequences.
- **Severity**: HIGH | **Likelihood**: LOW (Enforced) | **Risk Owner**: `CHIEF_ARCHITECT` & `SECURITY_PRIVACY`
- **Remediation Plan**:
  1. *Strict Evaluation Isolation*: `SRC-CV-04` is designated exclusively as `ELIGIBLE_PRIMARY` for alignment and safety evaluation.
  2. *Token Vocab Ineligibility*: Pinned as `INELIGIBLE_REJECTED` for tokenizer vocab training in `DATASET_SOURCE_CATALOG_V3.csv`.
  3. *Isolated Prompts Only*: Fertility evaluation is restricted strictly to the user prompts (`ELIGIBLE_ISOLATED_PROMPTS_ONLY`), stripping all toxic rejected completions.

---

### Risk R7: Reviewer Key Compromise & Stale Approvals
- **Sources Affected**: All governance review submissions.
- **Description**: A human reviewer's private signing key is leaked, or an approval granted years ago remains indefinitely valid despite dataset updates.
- **Severity**: MEDIUM | **Likelihood**: LOW | **Risk Owner**: `SECURITY_PRIVACY`
- **Remediation Plan**:
  1. *Key Revocation List (CRL)*: Implemented in `KeyRegistry.revoke_key()`, tested in `test_revoked_key_rejected()`.
  2. *Mandatory Annual Expiry*: All approvals must enforce an ISO-8601 `expiry_date` not exceeding 365 days from issuance.
  3. *Audit Trail Traceability*: Any key revocation event is appended to the tamper-evident hash chain.

---

## 4. Remediation Responsibilities & Sign-Off Checklist

| Risk ID | Description | Responsible Authority Role | Mandatory Pre-Condition for Unlocking Gate | Status |
| :---: | :--- | :--- | :--- | :---: |
| **R1** | Copyleft Viral Risk | `LEGAL_GOVERNANCE` | Formal legal ruling on adaptation boundary under Section 14 | **PENDING** |
| **R2** | Non-US Fair Dealing | `LEGAL_GOVERNANCE` | Web scrape domain filtering protocol approved | **PENDING** |
| **R3** | Public Domain Vital Dates | `LEGAL_GOVERNANCE` & `DATA_CUSTODIAN` | Item-level vital date ledger (1965/1955 thresholds) populated | **PENDING** |
| **R4** | Non-Commercial Infiltration | `CHIEF_ARCHITECT` | Permanent exclusion of `SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01` | **ENFORCED** |
| **R5** | Synthetic Model Collapse | `CHIEF_ARCHITECT` | 0% synthetic ratio enforced for vocab training | **ENFORCED** |
| **R6** | Alignment Scope Leakage | `SECURITY_PRIVACY` | Isolated prompt stripping enforced for `SRC-CV-04` | **ENFORCED** |
| **R7** | Stale Creds & Revocation | `SECURITY_PRIVACY` | CRL engine and 365-day expiry verification active | **ENFORCED** |

---

## 5. Summary Verdict

All technical mitigations are active in code and verified by automated tests. Legal and custodial pre-conditions remain **PENDING AUTHENTIC HUMAN REVIEW**. The production access gate must remain **LOCKED** until all items on the sign-off checklist are formally executed.
