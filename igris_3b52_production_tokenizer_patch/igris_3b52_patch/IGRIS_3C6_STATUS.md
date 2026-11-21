# IGRIS Milestone 3C.6 — Milestone Status

**Document Version:** 1.0.0  
**Status:** Completed  
**Milestone:** 3C.6 — Dataset Source Validation & Governance Review Freeze  
**Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Governance Gate Status

| Gate Dimension | Operational Status | Enforcement Mechanism |
| :--- | :---: | :--- |
| **Production Dataset Access** | **`LOCKED`** | Enforced by `scripts/dataset_authorization.py` default-deny gate |
| **Dataset Acquisition (Downloads)** | **`NOT AUTHORIZED`** | Zero download calls executed; no network ingress |
| **Production PII Scanning** | **`NOT AUTHORIZED`** | Quarantined; awaiting physical dataset staging authorization |
| **Tokenizer Model Training** | **`NOT AUTHORIZED`** | Architecture parameters and candidate vocabularies locked |
| **Candidate Artifact Invariance** | **`VERIFIED`** | Candidate A and Candidate B SHA-256 hashes byte-invariant |

---

## 2. Master Catalog V2 Summary (32 Sources)

| Consensus Classification | Source Count | Sources Included | Operational Ruling |
| :--- | :---: | :--- | :--- |
| **`VERIFIED`** | **18** | `SRC-TM-01`, `SRC-EN-01`, `SRC-TG-01`, `SRC-TG-02`, `SRC-HI-01`, `SRC-OI-01`, `SRC-OI-02`, `SRC-OI-03`, `SRC-OI-04`, `SRC-OI-05`, `SRC-CD-01`, `SRC-CD-02`, `SRC-TD-02`, `SRC-TD-03`, `SRC-CV-03`, `SRC-CV-04`, `SRC-CV-05`, `SRC-CV-06`, `SRC-EM-01`, `SRC-EM-02` | Technically verified and legally cleared. Eligible for staging upon human sign-off. |
| **`REQUIRES HUMAN APPROVAL`** | **7** | `SRC-TM-02`, `SRC-EN-02`, `SRC-EN-03`, `SRC-HI-02`, `SRC-ML-01`, `SRC-ML-02`, `SRC-TD-01` | Technically verified, but requires legal waiver (ShareAlike/GPL) or privacy sign-off (Crawl). |
| **`INCOMPATIBLE`** | **4** | `SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02` | Legally incompatible (`NC` clause or third-party copyright infringement). Purged from pipeline. |
| **`UNVERIFIED`** | **1** | `SRC-TM-03` | Pass-through web crawl rights and DPDP Act compliance unverified. Withhold acquisition. |
| **Total** | **32** | All 10 categories covered | **Master Catalog V2 Frozen for Human Review** |

---

## 3. Governance Freeze Checklist

- [x] Four original human approval roles confirmed and locked (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`).
- [x] Canonical ten benchmark categories confirmed and locked (`DATASET_SPECIFICATION.md`).
- [x] Category 5 sub-language coverage complete (Telugu, Malayalam, Kannada, Bengali, Gujarati under `CC0-1.0`).
- [x] Category 9 conversational taxonomy decoupled into 5 subtypes with red-team training exclusion.
- [x] Source ID sequence for Category 9 restored and verified (`SRC-CV-01` through `SRC-CV-06`).
- [x] Model architecture parameters locked (16L / 512H / 8Attn / 4KV / 2048Ctx / 32768Vocab / 12 Structural Tokens).
- [x] Candidate A and Candidate B synthetic artifacts verified byte-invariant.
- [x] Production access gate locked in default-deny mode.

---

## 4. Regression & Invariance Summary

- **Pytest Suite:** 244 passed in 4.85s.
- **Milestone 3B.57 Acceptance Audit:** 162 / 162 checks passed.
- **Candidate A Hash (`tokenizer.json`):** `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (Invariant)
- **Candidate B Hash (`tokenizer.model`):** `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (Invariant)
