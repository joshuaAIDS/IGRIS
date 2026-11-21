# IGRIS Dataset Acquisition Risk Register & Quality Safeguards

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3C.2 — Dataset Acquisition Planning  
**Document ID**: `IGRIS-RSK-DAR-3C2`  
**Classification**: TECHNICAL RISK REGISTER & SAFEGUARDS  
**Status**: APPROVED  
**Date**: 2026-11-17  

---

## 1. Overview & Risk Assessment Methodology

This risk register identifies, assesses, and provides mitigation controls for potential hazards associated with acquiring multilingual text datasets for the IGRIS language model evaluation suite.

Risks are evaluated across five critical dimensions:
- **Legal & Intellectual Property**
- **Data Privacy & Statutory Compliance (DPDP / GDPR)**
- **Benchmark Contamination & Decontamination**
- **Data Quality, Normalization & Encoding Integrity**
- **Supply Chain, Provenance & Link Rot**

---

## 2. Comprehensive Acquisition Risk Register

| Risk ID | Domain | Risk Description | Likelihood | Impact | Severity | Primary Mitigation Control | Sign-Off Authority | Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| **RSK-LEG-01** | Legal | Copyleft taint from `CC-BY-SA` or `GPL` text infecting downstream model weights. | Medium | High | **HIGH** | Restrict acquisition to CC0, MIT, Apache-2.0, and CC-BY for models; evaluate SA strictly in isolated read-only benchmark runs. | `LEGAL_GOVERNANCE` | `REQUIRES HUMAN APPROVAL` |
| **RSK-LEG-02** | Legal | Terms-of-service violations from third-party web scrapers (e.g. YouTube comments, Reddit). | Medium | High | **HIGH** | Prohibit raw web scraper ingestion; require verified upstream academic/institutional data releases with published rights. | `LEGAL_GOVERNANCE` | `REQUIRES HUMAN APPROVAL` |
| **RSK-PRI-01** | Privacy | Inadvertent ingestion of Personally Identifiable Information (PII) under India DPDP Act 2023 / GDPR. | High | High | **CRITICAL** | Automated regex PII screening for Indian mobile numbers, Aadhaar, PAN, emails, and payment cards; quarantine flagged rows. | `SECURITY_PRIVACY` | `REQUIRES HUMAN APPROVAL` |
| **RSK-PRI-02** | Privacy | Leaked credentials, API tokens, cryptographic private keys, or internal infrastructure hostnames. | Medium | Critical | **CRITICAL** | Automated secret scanning using entropy detectors and token regex; immediate sample isolation upon detection. | `SECURITY_PRIVACY` | `REQUIRES HUMAN APPROVAL` |
| **RSK-CON-01** | Contamination | 13-gram overlap between candidate evaluation sets and future pre-training corpora (benchmark leakage). | High | High | **HIGH** | Run automated 13-gram overlap detector (`detect_train_eval_leakage`); enforce 0.0% overlap requirement. | `CHIEF_ARCHITECT` | `VERIFIED` |
| **RSK-CON-02** | Contamination | Internal sample duplication skewing tokenizer compression ratios and vocabulary statistics. | High | Medium | **MEDIUM** | MinHash LSH deduplication ($J \ge 0.85$) and exact line hashing; deduplication drop rate logged in manifest. | `DATA_CUSTODIAN` | `VERIFIED` |
| **RSK-ENC-01** | Quality | Ingress files containing non-UTF-8 bytes or Byte Order Marks (BOM, `U+FEFF`). | Medium | High | **HIGH** | Strict UTF-8 validation rejecting unmapped byte sequences; automated BOM stripping at file boundaries. | `DATA_CUSTODIAN` | `VERIFIED` |
| **RSK-ENC-02** | Quality | Decomposed Unicode characters (NFD/NFKD) causing artificial vocabulary explosion. | High | High | **HIGH** | Mandatory Unicode 15.1.0 NFC normalization filter; zero tolerance for unnormalized text. | `DATA_CUSTODIAN` | `VERIFIED` |
| **RSK-ENC-03** | Quality | Lone surrogate code points (`U+D800`–`U+DFFF`) or bi-directional text overrides causing parser crashes. | Low | Critical | **HIGH** | Strict surrogate rejection filter (`test_lone_surrogates_flagged`); rejection of uncertified control codes. | `DATA_CUSTODIAN` | `VERIFIED` |
| **RSK-SUP-01** | Supply Chain | Upstream link rot, repository deletion, or silent upstream data mutation altering benchmark reproducibility. | Medium | High | **HIGH** | Upstream mirror snapshots frozen in quarantine storage; dual-layer SHA-256 manifests stamped immediately upon receipt. | `DATA_CUSTODIAN` | `VERIFIED` |
| **RSK-SUP-02** | Supply Chain | Ingestion of corrupted or truncated archive files during transit. | Low | High | **MEDIUM** | SHA-256 checksum verification against upstream published hash prior to extraction in sandbox environments. | `SECURITY_PRIVACY` | `VERIFIED` |

---

## 3. Mandatory Human Sign-Off Gate Safeguard

To guarantee that no risk item goes unmitigated:

1. **Pre-Ingestion Clearance**:
   Every prospective dataset must be reviewed against this register by the four authority roles prior to issuing any acquisition command.
2. **Quarantine Isolation**:
   Any data that fails automated quality, PII, or encoding checks is immediately quarantined into `quarantine/pii_flagged/` or `quarantine/rejected/`.
3. **Default-Deny Invariant**:
   The programmatic access gate (`AuthorizationValidator.enforce_access_gate`) remains locked. If any risk item remains unmitigated or unapproved, execution halts with `DatasetAccessDeniedError`.
