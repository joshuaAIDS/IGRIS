# IGRIS Dataset License Comparison & Legal Compatibility Analysis

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3C.2 — Dataset Acquisition Planning  
**Document ID**: `IGRIS-LEG-DLC-3C2`  
**Classification**: LEGAL & GOVERNANCE COMPLIANCE MATRIX  
**Status**: DRAFT (Awaiting Legal Officer Sign-Off)  
**Date**: 2026-11-17  

---

## 1. Executive Summary

This document presents a comprehensive comparative analysis of public dataset licenses identified during Milestone 3C.2 planning.

The primary objective is to categorize candidate data sources by their legal risk profile and evaluate whether their licensing terms are compatible with:
1. **Phase 1**: Tokenizer vocabulary evaluation, compression benchmarking, and sequence length audits (`TOKENIZER_EVALUATION_ONLY`).
2. **Phase 2**: Future potential language model pre-training, fine-tuning, and weights deployment.

> [!IMPORTANT]
> **GOVERNANCE MANDATE**:  
> No dataset may be downloaded or ingested based solely on this comparative review. Every target dataset must receive formal human sign-off from `LEGAL_GOVERNANCE` on [PRODUCTION_AUTHORIZATION_CHECKLIST.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PRODUCTION_AUTHORIZATION_CHECKLIST.md).

---

## 2. Comprehensive License Compatibility Matrix

| License Type | Representative Sources | Commercial Rights | Evaluation Scope | Training Scope | Attribution Required | Copyleft Taint Risk | Legal Classification |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`CC0-1.0`** (Public Domain) | IndicCorp v2 (Tamil, Hindi, Telugu, Malayalam, Kannada), Project Gutenberg | **YES** | **YES** | **YES** | NO (Recommended) | **NONE** | **`VERIFIED` (Tier 1: Preferred)** |
| **`MIT` / `Apache-2.0` / `BSD`** | The Stack v2 (Permissive subset), HumanEval, Python Docs | **YES** | **YES** | **YES** | YES | **NONE** | **`VERIFIED` (Tier 1: Preferred)** |
| **`Unicode-DFS-2016`** | Unicode 15.1.0 UCD, Emoji 15.1 Data Files | **YES** | **YES** | **YES** | YES | **NONE** | **`VERIFIED` (Tier 1: Preferred)** |
| **`CC-BY-4.0`** | DravidianCodeMix, IndicGLUE, FLORES-200 (part), Tamil News | **YES** | **YES** | **YES** | YES | **NONE** | **`VERIFIED` (Tier 1: Preferred)** |
| **`ODC-By 1.0`** | OSCAR 23.01, C4, mC4 | **YES** | **YES** | **YES** | YES | **NONE** | **`VERIFIED` (Tier 2: Acceptable)** |
| **`CC-BY-SA-4.0`** | Wikipedia Dumps (ta, en, hi), FLORES-200 (devtest) | **YES** | **YES** | **UNCERTAIN** | YES | **MEDIUM** | **`REQUIRES HUMAN APPROVAL`** |
| **`GPL-2.0-with-exception`** | Linux Kernel Documentation | **YES** | **YES** | **YES** | YES | **LOW** | **`VERIFIED` (Tier 2: Acceptable)** |
| **`CC-BY-NC-4.0` / `NC-SA`** | DailyDialog, IIT Bombay Parallel Corpus | **NO** | **YES (Research)** | **NO** | YES | **HIGH** | **`REQUIRES HUMAN APPROVAL`** |
| **Non-Standard / Web Scrape** | OpenSubtitles OPUS, Social Dravidian FIRE | **UNVERIFIED** | **UNCERTAIN** | **NO** | UNKNOWN | **HIGH** | **`UNVERIFIED` (Tier 4: Prohibited)** |

---

## 3. In-Depth Legal Risk Analysis by Tier

### 3.1 Tier 1: Completely Permissive & Public Domain (Zero Copyleft Taint)
- **Licenses**: `CC0-1.0`, `MIT`, `Apache-2.0`, `Unicode-DFS-2016`, `CC-BY-4.0`.
- **Legal Assessment**:
  - Grants unrestricted rights to evaluate, transform, index, extract tokens, and benchmark.
  - Zero risk of viral copyleft requiring downstream language model weights or source code to be open-sourced.
  - Attribution notices must be maintained in the project's third-party notice ledger (`documentation/THIRD_PARTY_NOTICES.md`).
- **Recommendation**: Prioritize sources in Tier 1 for primary benchmark evaluation.

### 3.2 Tier 2: Attribution with Database Rights (`ODC-By 1.0`, `PSF-2.0`)
- **Licenses**: Open Data Commons Attribution License (`ODC-By 1.0`).
- **Legal Assessment**:
  - Distinguishes between "Database" rights and "Produced Works".
  - Derived tokenizer vocabularies and statistical metrics constitute "Produced Works" that do not require relicensing of the underlying database.
  - Explicit attribution credit must be embedded in published evaluation reports.
- **Recommendation**: Approved for evaluation; requires legal verification of crawl consent.

### 3.3 Tier 3: ShareAlike Copyleft Risks (`CC-BY-SA-4.0`)
- **Licenses**: Creative Commons Attribution-ShareAlike 4.0.
- **Legal Assessment**:
  - If text from CC-BY-SA sources is modified, the resulting adaptation must be licensed under CC-BY-SA.
  - While reading text to evaluate tokenizer compression ratios does not constitute an "Adaptation" under standard copyright doctrine, utilizing CC-BY-SA text for model pre-training poses legal debate regarding whether model weights inherit ShareAlike obligations.
- **Recommendation**: Permitted for evaluation-only read access; prohibited from pre-training without formal legal counsel clearance.

### 3.4 Tier 4: Non-Commercial (`NC`) and Unverified Scraping (High Risk)
- **Licenses**: `CC-BY-NC-4.0`, `CC-BY-NC-SA-4.0`, Unverified Terms of Service.
- **Legal Assessment**:
  - "Non-Commercial" restrictions conflict with production language model deployment.
  - Web scraping without verifiable robots.txt or terms of service compliance creates potential CFAA / tort liabilities.
- **Recommendation**: Strictly prohibited from production ingestion pipelines. Any research evaluation requires an explicit waiver from `LEGAL_GOVERNANCE`.

---

## 4. Legal Sign-Off Requirements for Milestone 3C

Before any dataset download or ingestion can be initiated, `LEGAL_GOVERNANCE` must sign off on:
1. Exact upstream source URL and git commit / snapshot ID.
2. Verified SPDX license identifier matching the repository's `LICENSE` file.
3. Confirmation that the evaluation scope (`TOKENIZER_EVALUATION_ONLY`) is documented.
4. Attribution wording registered in the project's legal attribution manifest.
