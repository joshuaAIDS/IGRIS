# IGRIS Production Authorization Checklist

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3B.62 — Production Authorization Readiness Audit  
**Document ID**: `IGRIS-CHK-PAC-3B62`  
**Classification**: MANDATORY HUMAN GOVERNANCE GATE  
**Status**: ACTIVE PREREQUISITE (Production Access Locked)  

---

## 1. Operational Invariant

> [!CAUTION]
> **STRICT GOVERNANCE PROHIBITION**:  
> No automated script, evaluation harness, CLI tool, or background process may access, read, or process any production dataset until this checklist has been fully completed, verified, and signed off by the four designated human authority roles. All production data remains locked under default-deny access control.

---

## 2. Multi-Tier Human Sign-Off Checklist

Each check item is classified as:
- **`PASS`**: The automated technical mechanism, validation rule, or template is tested and verified.
- **`REQUIRES HUMAN APPROVAL`**: The real-world production artifact or legal review requires human review and sign-off.

---

### Phase 1: Legal, Licensing & Provenance Compliance
**Mandatory Signatory**: `LEGAL_GOVERNANCE` (Lead Legal Counsel / Compliance Officer)

| Item ID | Verification Criteria | Technical Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **L-01** | License permits evaluation, benchmark derivation, and model fine-tuning. | SPDX Identifier / Legal Agreement review | `REQUIRES HUMAN APPROVAL` |
| **L-02** | No unapproved web-scraped material or terms-of-service violations. | Source Lineage & Ingress Register | `REQUIRES HUMAN APPROVAL` |
| **L-03** | Derivative work rights and public reporting of tokenizer benchmarks permitted. | Intellectual Property Review | `REQUIRES HUMAN APPROVAL` |
| **L-04** | Commercial vs Non-Commercial usage scope explicitly documented. | Scope declaration in `authorization.md` | `REQUIRES HUMAN APPROVAL` |
| **L-05** | Legal & Governance signatory digital signature hash recorded. | 64-character SHA-256 validation | `PASS` (Schema Verified) |

**Sign-off Decision**: `[ ] APPROVED` `[ ] REJECTED`  
**Signatory Name**: __________________________  
**Timestamp**: __________________________  
**Signature Hash**: __________________________  

---

### Phase 2: Source Custody & Normalization Integrity
**Mandatory Signatory**: `DATA_CUSTODIAN` (Lead Data Engineer / Corpus Specialist)

| Item ID | Verification Criteria | Technical Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **C-01** | Corpus origin, snapshot timestamp, and ingestion method verified. | Source Ingestion Audit Log | `REQUIRES HUMAN APPROVAL` |
| **C-02** | Encoding is strictly UTF-8 with zero byte-order marks (BOM) or unmapped bytes. | `scripts/dataset_quality_checks.py` | `PASS` (Tooling Verified) |
| **C-03** | 100% Unicode NFC normalization verified (zero NFD, NFKC, or NFKD drift). | Unicode 15.1.0 NFC validator | `PASS` (Tooling Verified) |
| **C-04** | Zero lone surrogates (`U+D800`–`U+DFFF`) or bi-directional spoofing characters. | Surrogate isolation scanner | `PASS` (Tooling Verified) |
| **C-05** | Category classification aligns with the 10 approved evaluation domains. | `DatasetInventory.filter_by_category` | `PASS` (Schema Verified) |
| **C-06** | Data Custodian digital signature hash recorded. | 64-character SHA-256 validation | `PASS` (Schema Verified) |

**Sign-off Decision**: `[ ] APPROVED` `[ ] REJECTED`  
**Signatory Name**: __________________________  
**Timestamp**: __________________________  
**Signature Hash**: __________________________  

---

### Phase 3: Privacy, PII Screening & Decontamination
**Mandatory Signatory**: `SECURITY_PRIVACY` (Lead Security Engineer / CISSP)

| Item ID | Verification Criteria | Technical Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **S-01** | Zero direct PII identifiers (emails, phone numbers, government IDs, credit cards). | Regex scanner & entity audit | `REQUIRES HUMAN APPROVAL` |
| **S-02** | Zero leaked credentials, API tokens, cryptographic keys, or internal hostnames. | Secret scanning engine | `REQUIRES HUMAN APPROVAL` |
| **S-03** | 13-gram overlap test confirms 0.0% contamination against pre-training corpora. | `detect_train_eval_leakage` | `PASS` (Tooling Verified) |
| **S-04** | MinHash LSH near-duplicate rate is within certified limits ($J < 0.85$). | `MinHashNearDuplicateDetector` | `PASS` (Tooling Verified) |
| **S-05** | Flagged or quarantined records permanently purged or isolated in quarantine. | Quarantine isolation policy | `REQUIRES HUMAN APPROVAL` |
| **S-06** | Security & Privacy signatory digital signature hash recorded. | 64-character SHA-256 validation | `PASS` (Schema Verified) |

**Sign-off Decision**: `[ ] APPROVED` `[ ] REJECTED`  
**Signatory Name**: __________________________  
**Timestamp**: __________________________  
**Signature Hash**: __________________________  

---

### Phase 4: Model Architecture & Milestone Scope Alignment
**Mandatory Signatory**: `CHIEF_ARCHITECT` (Principal Architect / Project Lead)

| Item ID | Verification Criteria | Technical Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **A-01** | Context window budget aligns with 2,048 tokens ($2\times$ safety margin). | `context_window_evaluation.py` | `PASS` (Contract Verified) |
| **A-02** | Target milestone scope is explicitly set to `TOKENIZER_EVALUATION_ONLY`. | Authorization metadata gate | `PASS` (Schema Verified) |
| **A-03** | Direct model training and fine-tuning are strictly prohibited in scope. | Default-deny training gate | `PASS` (Enforced) |
| **A-04** | Balanced stratification across short (<512), medium (512–1024), long (1024–2048). | Context length tier classifier | `PASS` (Tooling Verified) |
| **A-05** | Chief Architect digital signature hash recorded. | 64-character SHA-256 validation | `PASS` (Schema Verified) |

**Sign-off Decision**: `[ ] APPROVED` `[ ] REJECTED`  
**Signatory Name**: __________________________  
**Timestamp**: __________________________  
**Signature Hash**: __________________________  

---

### Phase 5: Cryptographic Integrity & Packaging
**Mandatory Signatory**: `DATA_CUSTODIAN` & `SECURITY_PRIVACY`

| Item ID | Verification Criteria | Technical Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **P-01** | Deterministic `manifest.json` generated for all dataset files. | `scripts/dataset_inventory.py::generate_manifest` | `PASS` (Tooling Verified) |
| **P-02** | Individual file SHA-256 hashes, line counts, character counts, byte sizes stamped. | `compute_file_metrics` | `PASS` (Tooling Verified) |
| **P-03** | Root manifest SHA-256 computed and cross-referenced in `authorization.md`. | Dual-layer hash validation | `PASS` (Tooling Verified) |
| **P-04** | Filesystem permissions set to immutable read-only (`chmod 0444` / `attrib +R`). | OS-level file locking | `REQUIRES HUMAN APPROVAL` |

---

### Phase 6: Final Authorization Gate Clearance
**Mandatory Condition**: Unanimous `APPROVED` from all four roles.

| Role | Signatory Title | Required Decision | Execution Status |
| :--- | :--- | :--- | :--- |
| **Data Custodian** | Lead Data Engineer | `APPROVED` | `REQUIRES HUMAN APPROVAL` |
| **Legal & Governance** | Lead Legal Counsel | `APPROVED` | `REQUIRES HUMAN APPROVAL` |
| **Security & Privacy Lead** | Principal Security Engineer | `APPROVED` | `REQUIRES HUMAN APPROVAL` |
| **Chief Architect** | Project Lead | `APPROVED` | `REQUIRES HUMAN APPROVAL` |

> **EXECUTION GATE RULE**:  
> If all four roles record `APPROVED`, the status in `authorization.md` and `DATASET_INVENTORY.csv` transitions from `PENDING_REVIEW` to `APPROVED`.  
> If ANY role records `REJECTED`, status transitions to `REJECTED` and the dataset is quarantined.
