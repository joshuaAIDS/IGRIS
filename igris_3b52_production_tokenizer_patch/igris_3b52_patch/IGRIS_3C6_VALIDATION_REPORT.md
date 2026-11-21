# IGRIS Milestone 3C.6 — Dataset Source Validation & Governance Review Freeze Report

**Project:** IGRIS (Decoder-Only Multilingual Transformer)  
**Patch Directory:** `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Milestone:** 3C.6 — Dataset Source Validation & Governance Review Freeze  
**Evaluation Candidates:** Candidate A (ByteLevel BPE, provisional front-runner) & Candidate B (SentencePiece Unigram)  
**Production Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

Milestone 3C.6 establishes a formal, frozen baseline for genuine human governance review across all 32 reconciled dataset sources. This milestone:
1. Conducted in-depth technical and legal validation of the new sources proposed in Milestone 3C.5 (`SRC-OI-04`, `SRC-OI-05`, `SRC-CV-03`, `SRC-CV-04`, `SRC-CV-05`, `SRC-CV-06`).
2. Resolved the conversational category taxonomy by decoupling **five distinct conversational subtypes** and establishing strict pipeline boundary allocations between tokenizer training, tokenizer evaluation, and alignment evaluation.
3. Investigated and reconciled the `SRC-CV-05` identifier omission, restoring `MultiWOZ 2.4` to preserve immutable, continuous source IDs without silent renumbering.
4. Audited and confirmed 100% full coverage across all 10 canonical benchmark categories.
5. Formally enacted a **Dataset Governance Freeze**, locking the four human approval roles (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`), the 10-category taxonomy, and the 32-source catalog.
6. Maintained all strict safety boundaries: **zero dataset downloads, production gate locked, candidate artifacts byte-invariant, and zero fabricated approvals**.

---

## 2. Task 1: In-Depth Validation of New Candidate Sources

| Dimension | `SRC-OI-04`: IndicCorp Bengali | `SRC-OI-05`: IndicCorp Gujarati | `SRC-CV-03`: OpenAssistant OASST1 | `SRC-CV-04`: Anthropic HH-RLHF | `SRC-CV-05`: MultiWOZ 2.4 | `SRC-CV-06`: Project Gutenberg Theatrical |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Official Source URL** | `https://github.com/AI4Bharat/IndicCorp` | `https://github.com/AI4Bharat/IndicCorp` | `https://huggingface.co/datasets/OpenAssistant/oasst1` | `https://github.com/anthropics/hh-rlhf` | `https://github.com/budzianowski/multiwoz` | `https://www.gutenberg.org/` |
| **Exact Version** | v2.0 (Dec 2022) | v2.0 (Dec 2022) | OASST1 (Apr 2023) | v1.0 (2022) | v2.4 (2021) | Archive 2024 (Pre-1928) |
| **License Identifier** | `CC0-1.0` (Public Domain) | `CC0-1.0` (Public Domain) | `Apache-2.0` | `MIT` | `Apache-2.0` | `Public Domain` (US) |
| **Commercial Rights** | Unconditional (CC0 §2) | Unconditional (CC0 §2) | Permitted (Apache §2) | Permitted (MIT §1) | Permitted (Apache §2) | Permitted (Public Domain) |
| **Training Rights** | Unconditional | Unconditional | Explicitly granted for LLMs | Permitted under MIT | Permitted under Apache | Unconditional |
| **Dataset Provenance** | Crawled news & web portals | Crawled news & web portals | Volunteer crowd-workers (CLA) | Anthropic red-team dialogues | Cambridge task dialogue | Published stage plays |
| **Privacy / PII Risk** | LOW (Cleaned news text) | LOW (Cleaned news text) | LOW (Moderated trees) | VERY_LOW (Pre-filtered) | VERY_LOW (Simulated tasks) | ZERO (Historical drama) |
| **Volume Estimate** | 7.8 GB (~85M sentences) | 4.1 GB (~48M sentences) | 50 MB (~161k messages) | 40 MB (~160k sessions) | 15 MB (~10.4k dialogues) | 25 MB (Clean play scripts) |
| **Outstanding Legal Issues**| None | None | None | Segregate red-team split | None | Strip trademark headers |

---

## 3. Task 2: Conversational Taxonomy & Pipeline Allocation

Conversational data has been decoupled into five discrete subtypes to prevent vocabulary corruption and benchmark contamination:

```
[ Conversational Subtypes ]
├── Subtype A: Ordinary Conversational Text ----> Tokenizer Training & Evaluation (Slang, colloquial)
├── Subtype B: Multi-Turn Dialogue --------------> Tokenizer Evaluation (Turn transitions, context)
├── Subtype C: Preference Pairs -----------------> Alignment Evaluation ONLY (RLHF / DPO)
├── Subtype D: Rejected / Red-Team Responses ----> Safety Evaluation ONLY (STRICTLY BANNED from Tokenizer)
└── Subtype E: Literary Theatrical Dialogue -----> Tokenizer Training & Evaluation (Clean public domain)
```

### Safety Policy Enforcement:
- **Red-Team Exclusion**: `SRC-CV-04` red-team/rejected prompts are **strictly prohibited** from tokenizer vocabulary training to prevent the emergence of dedicated slur tokens or exploit representations.
- **Contamination Prevention**: Preference pairs (`chosen` vs `rejected`) are held strictly in reserve for downstream post-training alignment auditing.

*Detailed Specification*: [`CONVERSATIONAL_DATA_CLASSIFICATION.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/CONVERSATIONAL_DATA_CLASSIFICATION.md).

---

## 4. Task 3: Source Identifier Integrity

An audit of the numerical sequence for Category 9 resolved the omission of `SRC-CV-05`:
- **Investigation Finding**: In Milestone 3C.5, `MultiWOZ 2.4` was evaluated in Section 3.3 under identifier `SRC-CV-05`, but was omitted from the subsequent 3-source remediation summary table, leaving an apparent gap between `04` and `06`.
- **Integrity Invariant**: In accordance with the prohibition against silent renumbering, `SRC-CV-06` was preserved as Project Gutenberg Theatrical Dialogue, and `SRC-CV-05` was restored as MultiWOZ 2.4.
- **Outcome**: The conversational category sequence `SRC-CV-01` through `SRC-CV-06` is continuous, stable, and immutable.

*Detailed Investigation Report*: [`SOURCE_ID_INTEGRITY_REPORT.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/SOURCE_ID_INTEGRITY_REPORT.md).

---

## 5. Task 4 & 5: Category Coverage & Governance Freeze

The updated master catalog [`DATASET_SOURCE_CATALOG_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_CATALOG_V2.csv) incorporates exactly **32 reconciled sources**:

| Category ID | Benchmark Category | Total Sources | Cleared Baseline Sources | Encumbered / Conditional | Incompatible (Rejected) |
|:---:|:---|:---:|:---|:---|:---|
| **1** | **Tamil** | 3 | `SRC-TM-01` (`CC0-1.0`) | `SRC-TM-02`, `SRC-TM-03` | None |
| **2** | **English** | 3 | `SRC-EN-01` (`Public Domain`) | `SRC-EN-02`, `SRC-EN-03` | None |
| **3** | **Tanglish** | 3 | `SRC-TG-01`, `SRC-TG-02` (`CC-BY-4.0`) | None | `SRC-TG-03` |
| **4** | **Hindi** | 3 | `SRC-HI-01` (`CC0-1.0`) | `SRC-HI-02` | `SRC-HI-03` |
| **5** | **Other Indian Languages** | 5 | `SRC-OI-01` to `05` (`CC0-1.0`) | None | None |
| **6** | **Multilingual Mixed Text** | 2 | None | `SRC-ML-01`, `SRC-ML-02` | None |
| **7** | **Programming Code** | 2 | `SRC-CD-01`, `SRC-CD-02` (`Permissive`) | None | None |
| **8** | **Technical Documentation** | 3 | `SRC-TD-02` (`RFC`), `SRC-TD-03` (`PSF`) | `SRC-TD-01` | None |
| **9** | **Conversational Text** | 6 | `SRC-CV-03`, `SRC-CV-04`, `SRC-CV-05`, `SRC-CV-06` | None | `SRC-CV-01`, `SRC-CV-02` |
| **10** | **Emoji & Unicode Edge Cases**| 2 | `SRC-EM-01`, `SRC-EM-02` (`Unicode-DFS`) | None | None |
| **Total**| **Master Frozen Catalog** | **32** | **18 Verified Baseline** | **7 Conditional + 1 Unverified** | **4 Rejected (Audit)** |

*Governance Freeze Document*: [`DATASET_GOVERNANCE_FREEZE.md`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_GOVERNANCE_FREEZE.md).

---

## 6. Task 6: Regression & Acceptance Verification

All test suites were executed within the active patch environment:

1. **Pytest Suite:** **244 passed** (including 8 new unit tests in `test_dataset_3c6_validation.py`).
2. **Milestone 3B.57 Acceptance Audit:** **162 / 162 checks passed** (`run_acceptance_3b57.py`).
3. **Artifact Cryptographic Checksum Invariance:**
   - **Candidate A (`tokenizer.json`)**:
     `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (Exact match)
   - **Candidate B (`tokenizer.model`)**:
     `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (Exact match)

---

## 7. Final Governance State

- **Production Dataset Access:** `LOCKED` (Default-Deny Enforced)
- **Dataset Acquisition:** `NOT AUTHORIZED`
- **Tokenizer Training:** `NOT AUTHORIZED`
- **Human Approvals:** `PENDING` (Ready for authentic human governance review)
