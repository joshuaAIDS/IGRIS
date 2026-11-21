# IGRIS Milestone 3C.6 — Dataset Governance Freeze Order

**Document Version:** 1.0.0  
**Effective Date:** 2026-11-17  
**Status:** FROZEN FOR HUMAN REVIEW  
**Governing Standard:** IGRIS Production Governance & Dataset Specification Baseline  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Freeze Order

By this governance order, the dataset source catalog, architectural invariants, evaluation categories, and authorization gate schemas for the IGRIS project are formally **FROZEN**.

This freeze establishes a stable, auditable, and immutable baseline for genuine human sign-off across the four designated governance authorities (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`).

No automated agent or script may modify, append, or renumber any frozen catalog records, schema definitions, or architectural specifications without a multi-signature Architectural Change Request (ACR).

---

## 2. Frozen Governance Dimensions

```
+---------------------------------------------------------------------------------------------------+
|                                 IGRIS GOVERNANCE FREEZE BASELINE                                  |
+---------------------------------------------------------------------------------------------------+
| 1. Four Human Approval Roles   : DATA_CUSTODIAN, LEGAL_GOVERNANCE, SECURITY_PRIVACY, CHIEF_ARCHITECT |
| 2. Ten Benchmark Categories    : Preserved strictly from DATASET_SPECIFICATION.md (Milestone 3B.59)  |
| 3. Source Catalog V2           : Exactly 32 sources locked in DATASET_SOURCE_CATALOG_V2.csv       |
| 4. Conversational Taxonomy     : 5 decoupled subtypes locked in CONVERSATIONAL_DATA_CLASSIFICATION.md |
| 5. Model Architecture          : 16L / 512H / 8Attn / 4KV / 2048Ctx / 32768Vocab / 12 Structural Tokens |
| 6. Production Access Gate      : LOCKED (Default-Deny Enforced by scripts/dataset_authorization.py)|
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Frozen Authorization Roles

The four approval roles defined in `scripts/dataset_authorization.py` are confirmed and locked:
1. **`DATA_CUSTODIAN`**: Physical ingress, cryptographic manifest verification, UTF-8 losslessness, and Unicode 15.1.0 NFC normalization.
2. **`LEGAL_GOVERNANCE`**: Copyright ownership, terms of service adherence, commercial model training permissions, and copyleft/ShareAlike waivers.
3. **`SECURITY_PRIVACY`**: Statutory data privacy compliance (India DPDP Act 2023, GDPR), automated regex PII scrubbers, credential scanning, and 13-gram benchmark decontamination.
4. **`CHIEF_ARCHITECT`**: System parameter budget, sequence tier distribution (Tiers 1–4), 10-domain balance, and structural token isolation.

**Invariance Rule**: No proposed auxiliary roles (`AI_ETHICS_SAFETY`, `TECHNICAL_LEAD`) may replace or dilute these four foundational sign-off authorities.

---

## 4. Frozen Category Taxonomy & V2 Catalog Baseline

The 10 benchmark categories are frozen with their reconciled 32-source composition in [`DATASET_SOURCE_CATALOG_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/DATASET_SOURCE_CATALOG_V2.csv):

| ID | Frozen Category | Total Sources | Cleared / Verified Sources | Encumbered / Conditional | Incompatible (Rejected) |
|:---:|:---|:---:|:---:|:---:|:---:|
| **1** | **Tamil** | 3 | `SRC-TM-01` (`CC0-1.0`) | `SRC-TM-02`, `SRC-TM-03` | None |
| **2** | **English** | 3 | `SRC-EN-01` (`Public Domain`) | `SRC-EN-02`, `SRC-EN-03` | None |
| **3** | **Tanglish** | 3 | `SRC-TG-01`, `SRC-TG-02` (`CC-BY-4.0`) | None | `SRC-TG-03` |
| **4** | **Hindi** | 3 | `SRC-HI-01` (`CC0-1.0`) | `SRC-HI-02` | `SRC-HI-03` |
| **5** | **Other Indian Languages** | 5 | `SRC-OI-01` to `05` (`CC0-1.0`) | None | None |
| **6** | **Multilingual Mixed Text** | 2 | None | `SRC-ML-01`, `SRC-ML-02` | None |
| **7** | **Programming Code** | 2 | `SRC-CD-01` (`Permissive`), `SRC-CD-02` | None | None |
| **8** | **Technical Documentation** | 3 | `SRC-TD-02` (`RFC`), `SRC-TD-03` (`PSF`) | `SRC-TD-01` | None |
| **9** | **Conversational Text** | 6 | `SRC-CV-03`, `SRC-CV-04`, `SRC-CV-05`, `SRC-CV-06` | None | `SRC-CV-01`, `SRC-CV-02` |
| **10** | **Emoji & Unicode Edge Cases**| 2 | `SRC-EM-01`, `SRC-EM-02` (`Unicode-DFS`) | None | None |
| **Total**| **Complete Master Catalog** | **32** | **18 Verified Baseline** | **7 Conditional** + **1 Unverified** | **4 Rejected (Kept for Audit)** |

---

## 5. Frozen Architectural & Security Boundaries

1. **Safety Exclusion Invariant**:
   - Conversational Subtype D (Rejected / Red-Team Responses) is permanently excluded from Tokenizer Pre-Training.
   - Preference Pairs (Subtype C) are segregated exclusively for post-training alignment evaluation.
2. **Structural Token Invariant**:
   - Structural token IDs 0–11 remain strictly isolated. Normal user text encoding can never emit these IDs.
3. **Candidate Tokenizer Invariance**:
   - Candidate A (`tokenizer.json`): SHA-256 `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
   - Candidate B (`tokenizer.model`): SHA-256 `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
4. **Acquisition Gate**:
   - All dataset acquisition, network downloads, and production PII scanning remain **`NOT AUTHORIZED`**.
   - Production dataset access gate remains strictly **`LOCKED`**.
