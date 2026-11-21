# IGRIS Production Dataset Governance & Authorization Checklist

**Document Version**: 1.0.0  
**Milestone**: 3B.59 — Production Evaluation Readiness  
**Target Corpus**: IGRIS Multilingual Production Evaluation & Training Datasets  
**Governance Policy**: **STRICT CLEAN-ROOM ISOLATION**. Production datasets remain strictly inaccessible until this checklist is fully executed, verified, and signed off by authorized personnel.

---

## 1. Governance Isolation Invariants

Prior to granting read access or initiating any processing of production datasets, the following absolute invariants must be verified:
1. **Zero Unauthorized Access**: Automated systems and AI agents must not probe, inspect, read, or copy files from production training roots, approved inventories, or quarantine repositories without an active authorization ticket.
2. **Clean-Room Verification**: All pipeline code, quality filters, and benchmark suites must be tested solely against approved synthetic fixtures.
3. **No Retraining Without Authorization**: Neither Candidate A nor Candidate B may be trained on external data until explicit written sign-off is logged in Section 4.

---

## 2. Dataset Authorization Checklist

Every candidate production dataset must be audited against each check below prior to ingestion into the evaluation pipeline.

### Category A: Provenance, Ownership & Licensing
- [ ] **A.1 Dataset Lineage & Custodianship**: Complete provenance record identifying the dataset author, collecting organization, original acquisition source URL, and internal IGRIS data custodian.
- [ ] **A.2 Usage Permission & Terms of Service**: Written verification that data acquisition strictly complies with the terms of service, robots.txt directives, and scraping policies of the source domains.
- [ ] **A.3 Intellectual Property & Licensing Compatibility**: Complete legal review confirming the dataset is released under an open/permissive license (e.g. CC0, CC-BY, MIT, Apache 2.0, or verified Public Domain) permitting commercial model training and derivative evaluation without viral copyleft constraints.
- [ ] **A.4 Redistribution & Derivative Rights**: Clear documentation of rights to store, preprocess, derive subwords, and publish evaluation aggregates.

### Category B: Privacy, Security & Sensitivity Screening
- [ ] **B.1 Personally Identifiable Information (PII) Scrubbing**: Automated regex and heuristic audit verifying zero exposed personal emails, personal telephone numbers, home addresses, government IDs (e.g. Aadhaar, SSN, PAN), and financial identifiers.
- [ ] **B.2 Sensitive Credentials & API Keys Screening**: Automated screening verifying zero exposed passwords, cryptographic private keys, OAuth tokens, AWS/GCP service account keys, and database connection strings.
- [ ] **B.3 Toxic & Offensive Content Filtering**: Screening against standardized toxicity blocklists and harmful content taxonomies to prevent harmful generation bias.

### Category C: Data Quality, Integrity & Leakage Prevention
- [ ] **C.1 Character Encoding & BOM Validation**: Verification that all text files are strictly encoded in valid UTF-8 without Byte Order Marks (`\uFEFF`) and zero lone surrogates (`U+D800`–`U+DFFF`).
- [ ] **C.2 Canonical Unicode Normalization (NFC)**: Automated pass confirming all text conforms to canonical NFC normalization per Unicode 15.1.0 (`unicodedata2==15.1.0`).
- [ ] **C.3 Exact Deduplication Audit**: Verification that all records are unique; duplicate records matching on normalized SHA-256 hash are purged.
- [ ] **C.4 Near-Duplicate Decontamination (MinHash LSH)**: MinHash 64-permutation screening verifying zero sample pairs with Jaccard similarity $\ge 0.85$ within the evaluation set.
- [ ] **C.5 Train/Evaluation Leakage Gate**: Cryptographic SHA-256 hash cross-check confirming zero overlap between evaluation benchmarks and any pre-training corpora.

### Category D: Versioning, Integrity & Cryptographic Manifests
- [ ] **D.1 Semantic Versioning**: Dataset assigned a formal semantic version string (e.g. `igris-eval-corpus-v1.0.0`).
- [ ] **D.2 Cryptographic SHA-256 Manifest**: Complete CSV/JSON manifest recording every individual file name, line count, byte length, and SHA-256 checksum.
- [ ] **D.3 Read-Only Storage Lock**: Production dataset stored on an immutable, read-only filesystem volume with access control restricted to authorized pipeline runner accounts.

---

## 3. Human Authorization Workflow

Access to production evaluation data requires a three-tier sign-off workflow:

```
+----------------------------+     +----------------------------+     +----------------------------+
| 1. Data Governance Officer | --> | 2. Lead Security Officer   | --> | 3. Chief ML Architect      |
| (Licensing & Lineage Check)|     | (PII & Sensitivity Check)  |     | (Final Access Permission)  |
+----------------------------+     +----------------------------+     +----------------------------+
```

---

## 4. Formal Sign-Off Record

*This section must be completed and cryptographically signed prior to unlocking production dataset read permissions.*

| Role | Approver Name | Signature / Verification ID | Date | Authorization Status |
|:---|:---|:---|:---|:---:|
| **Data Custodian** | *Pending Assignment* | `UNAUTHORIZED` | *Pending* | **LOCKED** |
| **Governance Officer** | *Pending Assignment* | `UNAUTHORIZED` | *Pending* | **LOCKED** |
| **Lead Tokenizer Architect**| *Pending Assignment* | `UNAUTHORIZED` | *Pending* | **LOCKED** |

> [!CAUTION]
> Production datasets remain completely locked and inaccessible. Any unauthorized attempt by automated tooling or background jobs to circumvent read permissions constitutes a governance violation.
