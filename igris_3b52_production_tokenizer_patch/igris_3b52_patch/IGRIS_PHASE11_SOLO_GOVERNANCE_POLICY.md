# IGRIS Phase 11: Solo Developer Governance Policy & Migration Charter

**Project**: IGRIS Multilingual Decoder-Only Transformer  
**Active Patch**: `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Document ID**: `IGRIS-POLICY-PHASE11-SOLO-GOV`  
**Classification**: OFFICIAL ARCHITECTURAL & GOVERNANCE POLICY  
**Effective Date**: 2026-11-17  
**Governance Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Entity**: Project Owner & Sole Developer  
**Production Ingress Status**: **`LOCKED`** (Default-Deny Enforced)  

---

## 1. Executive Summary & Policy Migration Context

Project IGRIS has formally transitioned from the multi-party corporate committee framework to a **Solo Developer / Accountable Owner Governance Model** (`SOLO_DEVELOPER_OWNER_REVIEW`).

Under this project structure:
- **One Developer — One Accountable Owner**: The project is engineered and governed by a single natural person who carries sole operational, technical, and architectural responsibility.
- **Four Distinct Review Perspectives**: Rather than fabricating artificial corporate committee members or fictitious signatures, the sole owner personally executes all four required review domains:
  1. `DATA_CUSTODIAN`: Archive verification, UTF-8 losslessness, Unicode 15.1.0 NFC canonical normalization, and quarantine sandbox staging.
  2. `LEGAL_GOVERNANCE`: Copyright analysis (Indian Copyright Act 1957 Section 22 Life+60, UK/EU Life+70), open license deed compliance, and copyleft adaptation boundaries.
  3. `SECURITY_PRIVACY`: PII classification, automated regex screening, cryptographic verifier maintenance, and tamper-evident audit chaining.
  4. `CHIEF_ARCHITECT`: Vocabulary sizing (32,768), 12 structural token IDs (0–11), 0% synthetic text policy for vocabulary induction, and strict isolation of preference pairs and evaluation benchmarks.
- **Strict Anti-Fabrication Rule**: The project owner is documented as a single individual. The governance framework strictly forbids manufacturing personas, artificial titles, or simulated independent committee approvals.

```
+---------------------------------------------------------------------------------------------------------+
|                               SOLO DEVELOPER GOVERNANCE ARCHITECTURE                                    |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|                            +-----------------------------------------------+                            |
|                            |         PROJECT OWNER / SOLE DEVELOPER        |                            |
|                            |    (Single Natural Person - Sole Authority)   |                            |
|                            +-----------------------+-----------------------+                            |
|                                                    |                                                    |
|                   +--------------------------------+--------------------------------+                   |
|                   |                                |                                |                   |
|                   v                                v                                v                   |
|   +-------------------------------+ +-------------------------------+ +-------------------------------+ |
|   | PERSPECTIVE 1: DATA CUSTODIAN | | PERSPECTIVE 2: LEGAL & IP     | | PERSPECTIVE 3: SECURITY/PRIVACY | |
|   | - SHA-256 Archive Checksums   | | - Indian Copyright Sec 22/52  | | - PII Classification & Regex    | |
|   | - UTF-8 / Unicode 15.1.0 NFC  | | - License Deed Compatibility  | | - Cryptographic Intake Verifier | |
|   | - Quarantine Staging Enforcer | | - Uphold NC/Scrape Rejections | | - Immutable Audit Log Ledger    | |
|   +-------------------------------+ +-------------------------------+ +-------------------------------+ |
|                                                    |                                                    |
|                                                    v                                                    |
|                                   +-------------------------------+                                     |
|                                   | PERSPECTIVE 4: CHIEF ARCHITECT|                                     |
|                                   | - 32,768 Vocabulary Target    |                                     |
|                                   | - Structural Tokens (IDs 0-11)|                                     |
|                                   | - Benchmark Contamination Bar |                                     |
|                                   +-------------------------------+                                     |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
```

---

## 2. Definitive Boundary Distinctions

To ensure complete legal and technical transparency, the solo-developer governance model enforces strict distinctions between five categories of authority and scope:

### 2.1 Owner Self-Review vs. Independent External Review
- **Owner Self-Review**: Represents the internal due diligence, technical verification, and risk acceptance performed personally by the project developer. It confirms that code, data, and configurations satisfy internal IGRIS engineering standards.
- **Independent External Review**: Involves audits, certifications, or formal sign-offs executed by independent third parties (e.g., licensed outside legal counsel, certified penetration testers, external academic peer review).
- **Policy Rule**: Owner self-review must **never** be cited or represented as independent third-party approval. No independent approval exists for IGRIS at this stage.

### 2.2 Technical Authorization vs. Legal Authorization
- **Technical Authorization**: The project owner possesses absolute, unilateral authority to define model architectures, tokenizer vocabulary sizing (32,768), context lengths (2048), training hyperparameters, and test suites.
- **Legal Authorization**: The project owner can declare an assumption of legal risk for personal or research execution, but **cannot unilaterally alter or override statutory copyright laws, third-party license terms, or contractual covenants**.

### 2.3 Dataset-Specific Ingress Permission vs. Blanket Approval
- An owner's declared approval cannot convert an incompatible dataset into an authorized one.
- Datasets bearing non-commercial restrictions (`-NC`), unclear provenance, or unauthorized scraping (`SRC-CV-01`, `SRC-CV-02`, `SRC-HI-03`, `SRC-TG-03`) remain **strictly rejected and barred from all pipeline operations**.

---

## 3. External Legal, Regulatory & Commercial Flags

The project owner explicitly acknowledges that owner self-approval **cannot** satisfy the following external legal, contractual, and regulatory requirements:

| Risk Domain | Specific Unresolvable Constraint | Operational Impact on Deployment |
| :--- | :--- | :--- |
| **Copyleft Derivative Claims** | Datasets licensed under CC-BY-SA 4.0 (`SRC-EN-02`, `SRC-HI-02`, `SRC-TM-02`) or GPL-2.0 (`SRC-TD-01`) | Training model weights on copyleft text creates a legal risk that model weights may be deemed an adaptation/derivative work under EU/UK statutes, triggering mandatory ShareAlike release. Owner self-review cannot extinguish this upstream legal risk. |
| **Non-Commercial Prohibitions** | Datasets licensed under CC-BY-NC-SA 4.0 or Research-Only (`SRC-CV-01`, `SRC-CV-02`, `SRC-HI-03`, `SRC-TG-03`) | Commercial monetization, API deployment, or proprietary fine-tuning is legally barred. Owner approval cannot waive the licensor's non-commercial restriction. These sources remain permanently blocked. |
| **Database Sui Generis Rights** | Datasets licensed under ODC-By 1.0 (`SRC-EN-03`, `SRC-TM-03`, `SRC-ML-02`) | European Directive 96/9/EC database rights require explicit attribution notices in downstream distributions. Owner self-approval cannot bypass statutory attribution requirements. |
| **Statutory Data Privacy Laws** | India Digital Personal Data Protection Act (DPDP) 2023 & EU GDPR | Processing unconsented PII belonging to natural persons cannot be legitimized by a developer self-declaration. Formal Data Protection Impact Assessments (DPIA) and statutory data fiduciary compliance are required for commercial production. |
| **Commercial Enterprise Procurement** | Enterprise AI licensing standards (SOC 2 Type II, ISO 27001, IP Indemnification) | Commercial enterprise customers require independent third-party IP warranties and indemnities. Solo owner self-approval provides zero third-party legal indemnity. |

---

## 4. Reconciled Source Authority & Operational Decision Matrix

Under the Solo Governance Policy, the 32 candidate sources are categorized into four operational tiers:

```
+---------------------------------------------------------------------------------------------------------+
|                               SOLO OWNER SOURCE AUTHORITY TIERS                                         |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|  TIER 1: PERMISSIVE PRE-TRAINING BASELINE (18 Sources)                                                  |
|  - Scope: Eligible for Tokenizer Vocabulary Training & Fertility Evaluation pending physical staging   |
|  - Licenses: CC0 1.0, CC-BY 4.0, MIT, Apache-2.0, Public Domain, PSF-2.0, Unicode-DFS-2016            |
|  - Sources: SRC-TM-01, SRC-EN-01, SRC-TG-01, SRC-TG-02, SRC-HI-01, SRC-OI-01 through 05,               |
|             SRC-CD-01, SRC-TD-02, SRC-TD-03, SRC-CV-03, SRC-CV-05, SRC-CV-06, SRC-EM-01, SRC-EM-02    |
|                                                                                                         |
|  TIER 2: CONDITIONAL LEGAL CLEARANCE (8 Sources)                                                        |
|  - Scope: Authorized for Fertility Evaluation; Vocab Training CONDITIONAL on owner copyleft risk grant  |
|  - Licenses: CC-BY-SA 4.0, ODC-By 1.0, GPL-2.0                                                         |
|  - Sources: SRC-TM-02, SRC-TM-03, SRC-EN-02, SRC-EN-03, SRC-HI-02, SRC-ML-01, SRC-ML-02, SRC-TD-01      |
|                                                                                                         |
|  TIER 3: EVALUATION-ONLY ISOLATED BENCHMARKS (2 Sources)                                                |
|  - Scope: Strictly barred from Vocabulary Training; Authorized exclusively for Fertility Evaluation    |
|  - Sources: SRC-CD-02 (HumanEval/MBPP Benchmark) — Benchmark Contamination Prohibition                 |
|             SRC-CV-04 (Anthropic HH-RLHF) — Prompt-Isolated Subset Only (No preference pair leakage)    |
|                                                                                                         |
|  TIER 4: INCOMPATIBLE & PERMANENTLY BLOCKED (4 Sources)                                                 |
|  - Scope: Strictly BLOCKED from ALL training, evaluation, and staging pipelines                        |
|  - Licenses: CC-BY-NC 4.0, Research-Only, Unverified Scraping                                          |
|  - Sources: SRC-CV-01 (DailyDialog), SRC-CV-02 (OpenSubtitles), SRC-HI-03 (IIT Bombay), SRC-TG-03       |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
```

---

## 5. Solo Governance Operational Procedure

1. **Declared Approvals**: The owner records declared approvals in structured CSV registers ([IGRIS_PHASE11_SOLO_OWNER_APPROVAL_REGISTER.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_PHASE11_SOLO_OWNER_APPROVAL_REGISTER.csv) and [IGRIS_PHASE11_DATASET_OWNER_REVIEW_REGISTER.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_PHASE11_DATASET_OWNER_REVIEW_REGISTER.csv)).
2. **Fail-Closed Default-Deny Gate**: The production data ingress gate remains **`LOCKED`**. No automated data acquisition or model pre-training is initiated.
3. **Immutability of Tokenizer Artifacts**: Candidate A (`tokenizer.json`) and Candidate B (`tokenizer.model`) remain invariant and pinned to their verified SHA-256 hashes.

---

*End of IGRIS Phase 11 Solo Developer Governance Policy.*
