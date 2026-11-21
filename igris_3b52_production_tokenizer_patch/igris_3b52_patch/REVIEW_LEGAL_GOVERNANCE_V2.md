# IGRIS Human Review Package (Version 2): Legal Governance (`LEGAL_GOVERNANCE`)

**Document Version:** 2.0.0  
**Status:** PENDING AUTHENTIC HUMAN REVIEW (Unsigned)  
**Governing Role:** `LEGAL_GOVERNANCE`  
**Governing Standard:** IGRIS Legal Governance, Licensing & Intellectual Property Policy  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`

---

## 1. Role Responsibilities & Legal Mandate

The **Legal Governance Officer** possesses sole legal authority over:
1. Verification of published dataset licenses, direct public license evidence URLs, and institutional grants.
2. Enforcement of commercial rights, ensuring no corpus with non-commercial (`-NC`) clauses enters commercial training.
3. Assessment of copyleft and ShareAlike virality risks (CC-BY-SA 4.0, GPL-2.0) regarding downstream model weights.
4. Execution of the multi-jurisdictional copyright review under **The Indian Copyright Act, 1957 (Section 22 Life + 60, Section 23, Section 24, Section 57)** and **UK/EU Life + 70** directives.
5. Item-level public domain clearance for Project Gutenberg (`SRC-EN-01`, `SRC-CV-06`), verifying author/translator vital dates and lifetime publication status.
6. Enforcement of trademark removal mandates (Project Gutenberg Literary Archive Foundation License Section 1.E).
7. Strict verification that permissive licenses (CC-BY, Apache-2.0, MIT) are **not treated as unrestricted**, requiring attribution manifests and license notice files in all release packages.

---

## 2. Evidentiary References

Before signing, the Legal Governance Officer must review:
- [x] [`DATASET_LICENSE_CLASSIFICATION_V3.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_LICENSE_CLASSIFICATION_V3.csv) — 9-class license taxonomy and restriction terms.
- [x] [`DATASET_LICENSE_EVIDENCE_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_LICENSE_EVIDENCE_V2.csv) — Primary evidence URLs and commercial rights terms.
- [x] [`INDIA_COPYRIGHT_REVIEW.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/INDIA_COPYRIGHT_REVIEW.md) — Section 22 Life+60 statutory review and 1965 threshold.
- [x] [`GUTENBERG_JURISDICTION_REVIEW_V2.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/GUTENBERG_JURISDICTION_REVIEW_V2.md) — Multi-jurisdictional review and 4-pillar clearance protocol.
- [x] [`PIPELINE_AUTHORIZATION_MATRIX_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PIPELINE_AUTHORIZATION_MATRIX_V2.csv) — Gate decoupling specifications.

---

## 3. Legal Source-by-Source Review (All 32 Sources)

| Source ID | Dataset Name | License Class | Commercial Terms | Primary Legal Issue & Obligations | Legal Officer Decision |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | CC0 | CONFIRMED | Unencumbered public domain dedication by AI4Bharat; clear for commercial training. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-02** | Tamil Wikipedia Dump | ShareAlike | CONDITIONAL | CC-BY-SA 4.0 viral copyleft: model weights derivative risk requires formal legal clearance. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TM-03** | OSCAR 23.01 Tamil (Filtered) | ODC-By | UNCONFIRMED | Common Crawl web crawl; domain copyright unvetted; ODC-By database notice required. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-01** | Project Gutenberg Open Archive | Public Domain | CONFIRMED | Public domain in US/India for authors dying <= 1965; mandatory PGLAF trademark removal. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-02** | English Wikipedia Dump | ShareAlike | CONDITIONAL | CC-BY-SA 4.0: requires ShareAlike downstream licensing review; author credits mandatory. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EN-03** | C4 English Corpus | ODC-By | CONDITIONAL | ODC-By 1.0: mandatory database credit; underlying web domain fair use assessment required. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | CC-BY | CONFIRMED | CC-BY 4.0: **NOT unrestricted**; mandatory author credit (Chakravarthi et al.) and URI link. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | CC-BY | CONFIRMED | CC-BY 4.0: **NOT unrestricted**; attribution to AI4Bharat consortium mandatory. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TG-03** | Social Dravidian Sentiment Tanglish | Other / Unknown | **PROHIBITED** | Research-only clause: commercial use strictly barred; **MUST REJECT**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | CC0 | CONFIRMED | CC0-1.0 public domain dedication; clean commercial baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-02** | Hindi Wikipedia Dump | ShareAlike | CONDITIONAL | CC-BY-SA 4.0: ShareAlike viral copyleft review required before training. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-HI-03** | IIT Bombay Hindi-English | Other / Unknown | **PROHIBITED** | CC-BY-NC-SA 4.0: non-commercial restriction bars commercial deployment; **MUST REJECT**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | CC0 | CONFIRMED | CC0-1.0 public domain dedication; clean commercial baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | CC0 | CONFIRMED | CC0-1.0 public domain dedication; clean commercial baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | CC0 | CONFIRMED | CC0-1.0 public domain dedication; clean commercial baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-04** | IndicCorp v2 (Bengali) | CC0 | CONFIRMED | CC0-1.0 public domain dedication; clean commercial baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-OI-05** | IndicCorp v2 (Gujarati) | CC0 | CONFIRMED | CC0-1.0 public domain dedication; clean commercial baseline. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-01** | FLORES-200 Benchmark | ShareAlike | CONDITIONAL | CC-BY-SA 4.0: benchmark test split; ShareAlike applies to derivative models if trained. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | ODC-By | CONDITIONAL | ODC-By 1.0: database notice required; web crawl underlying content risks. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-01** | The Stack v2 (Permissive) | Other / Unknown | CONFIRMED | Permissive mix (MIT/Apache/BSD): requires automated license notice attribution file. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | Other / Unknown | CONFIRMED | MIT / Apache-2.0: clear for eval; prohibited from training (benchmark contamination). | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-01** | Linux Kernel Documentation | GPL | CONDITIONAL | GPL-2.0: syscall documentation exemption applies, but reciprocal copyleft requires sign-off. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-02** | IETF RFC Archive (Text) | Other / Unknown | CONFIRMED | RFC 5378 / IETF Trust: verbatim text reproduction permitted; derivatives restricted. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-TD-03** | Python Official Documentation | Other / Unknown | CONFIRMED | PSF-2.0: mandatory license notice retention; clear for commercial training/eval. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-01** | DailyDialog Dataset | Other / Unknown | **PROHIBITED** | CC-BY-NC-SA 4.0: non-commercial clause prohibits commercial exploitation; **MUST REJECT**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-02** | OpenSubtitles Multilingual | Other / Unknown | **PROHIBITED** | Unauthorized commercial subtitle scrape; severe copyright liability; **MUST REJECT**. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-03** | OpenAssistant OASST1 | Apache-2.0 | CONFIRMED | Apache-2.0: **NOT unrestricted**; must retain NOTICE file and state modified files. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-04** | Anthropic HH-RLHF | MIT | CONFIRMED | MIT: permissive, but prohibited from tokenizer training (vocabulary safety guard). | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-05** | MultiWOZ 2.4 | Apache-2.0 | CONFIRMED | Apache-2.0: **NOT unrestricted**; retain copyright notices and Apache license text. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-CV-06** | Project Gutenberg Theatrical | Public Domain | CONFIRMED | Public domain dramatic scripts; author death <= 1965 (India) and <= 1955 (UK/EU). Strip TM. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-01** | Unicode Standard 15.1.0 Suite | Other / Unknown | CONFIRMED | Unicode-DFS-2016: unencumbered commercial license with Unicode copyright notice. | `[ ] APPROVE  [ ] REJECT` |
| **SRC-EM-02** | Unicode 15.1 Emoji Data Files | Other / Unknown | CONFIRMED | Unicode-DFS-2016: unencumbered commercial license with Unicode copyright notice. | `[ ] APPROVE  [ ] REJECT` |

---

## 4. Legal Reviewer Sign-Off Field (Authentic Human Review)

> [!IMPORTANT]
> **INSTRUCTION TO HUMAN REVIEWER**: Do not execute or authorize dataset acquisition until this form is physically or digitally signed by the authorized Legal Governance Officer. No automated system may populate this signature.

- **Designated Role**: `LEGAL_GOVERNANCE`
- **Reviewer Full Name**: `__________________________________________________`
- **Bar Admission / Legal Credentials**: `__________________________________________________`
- **Organizational Title**: `__________________________________________________`
- **Reviewer Corporate Email**: `__________________________________________________`
- **Legal Clearance Decision**: `[ ] APPROVED FOR AUTHORIZATION STAGING    [ ] REJECTED / WITHHELD`
- **Digital / Physical Signature**: `__________________________________________________`
- **Date of Review (YYYY-MM-DD)**: `____________________`
- **Cryptographic PGP Key ID / Hash**: `__________________________________________________`

---

## 5. Expiry and Revocation Conditions

1. **Validity Period**: This legal approval shall remain valid for **180 calendar days** from the signature date, after which legal re-certification is mandatory.
2. **Immediate Revocation Triggers**:
   - Receipt of formal DMCA / Section 51 notice or copyright infringement complaint.
   - Any judicial ruling altering the interpretation of CC-BY-SA derivative status for model weights.
   - Any inclusion of an unverified Gutenberg EBook with an author who died after 1965 (India) or 1955 (UK/EU).
   - Any deployment of model weights trained on rejected non-commercial corpora (`-NC`).
