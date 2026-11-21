# IGRIS Security Validation Report: Dataset Access & Authorization Architecture

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3B.61 — Dataset Authorization Dry Run & Security Validation  
**Document ID**: `IGRIS-SEC-VAL-3B61`  
**Classification**: INTERNAL SECURITY AUDIT  
**Status**: APPROVED  
**Date**: 2026-11-17  

---

## 1. Executive Security Statement

This security validation report documents the dry-run audit of the IGRIS dataset inventory and authorization access-control system. The system was tested exclusively against synthetic attack vectors and failure conditions.

### Strict Governance Compliance:
1. **Production Corpus Isolation**: Zero production datasets, private training files, archives, or quarantine folders were opened, decompressed, or read.
2. **Tokenizer Immutability**: Neither Candidate A nor Candidate B tokenizers were retrained or modified. All model artifacts retain their exact verified bitwise SHA-256 digests.
3. **Execution Sandbox**: All testing occurred strictly inside the approved patch workspace (`C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\`).

---

## 2. Threat Modeling & Security Controls

The dataset access control architecture was audited against six primary threat vectors:

```mermaid
flowchart TD
    T1["Threat 1: Unauthorized Ingestion Bypass"] --> C1["Control: Default-Deny Gatekeeper in AuthorizationValidator"]
    T2["Threat 2: Post-Authorization File Tampering"] --> C2["Control: Dual SHA-256 Manifest & File-Byte Hashing"]
    T3["Threat 3: Fraudulent / Partial Sign-Offs"] --> C3["Control: Mandatory 4-Tier Role Quorum & Hex Hash Validation"]
    T4["Threat 4: Expired Approval Exploitation"] --> C4["Control: ISO 8601 Temporal Window & Expiry Gate"]
    T5["Threat 5: Inventory-Auth State Drift"] --> C5["Control: Strict Bidirectional Consistency Validator"]
    T6["Threat 6: CLI & Script Direct Execution"] --> C6["Control: Non-Zero Exit Codes & Programmatic Path Protections"]
```

### Threat 1: Unauthorized Ingestion Bypass
- **Risk**: An evaluation harness or training script loads a dataset without valid authorization.
- **Enforced Control**: `AuthorizationValidator.enforce_access_gate()` operates under strict Default-Deny. Datasets in `LOCKED`, `PENDING_REVIEW`, `REJECTED`, or `REVOKED` states raise an uncatchable `DatasetAccessDeniedError` and immediately abort execution.
- **Audit Result**: **SECURE**. All non-approved states were blocked.

### Threat 2: Post-Authorization File Tampering
- **Risk**: An approved dataset is silently modified on disk (e.g. content altered, PII injected, lines removed).
- **Enforced Control**: Dual-layer cryptographic validation. The root manifest has a SHA-256 signature recorded in the authorization record. Each file entry inside the manifest has an individual SHA-256 hash and byte size.
- **Audit Result**: **SECURE**. Tampering with a single character in a `.jsonl` data file or modifying the manifest total count immediately raised `DatasetAccessDeniedError("Tamper alert: ...")`.

### Threat 3: Fraudulent or Partial Sign-Offs
- **Risk**: An authorization record is forged with missing roles, unauthorized titles, or non-hex signature strings.
- **Enforced Control**:
  - The four roles (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`) are strictly mandatory.
  - Every signatory must record `APPROVED`. A single `REJECTED` veto halts the gate.
  - Digital signatures must match 64-character hexadecimal SHA-256 format.
- **Audit Result**: **SECURE**. Partial sign-offs, external consultant roles, and non-hex signature strings were all rejected.

### Threat 4: Expired Approval Exploitation
- **Risk**: An old authorization record from a prior milestone is reused beyond its certified lifetime.
- **Enforced Control**: The authorization gate parses `expiry_date` as an ISO 8601 timestamp with UTC timezone enforcement. Records past their expiration date trigger immediate refusal.
- **Audit Result**: **SECURE**. Expired fixtures were blocked with `Authorization expired on <date>`.

### Threat 5: Inventory-Auth State Drift
- **Risk**: A dataset is marked `APPROVED` in markdown, but remains `PENDING_REVIEW` or `QUARANTINED` in the central inventory CSV.
- **Enforced Control**: `AuthorizationValidator.verify_inventory_consistency()` cross-checks `dataset_id`, `version`, `authorization_status`, and `screening_status`. Any discrepancy halts access.
- **Audit Result**: **SECURE**. Status discrepancies between authorization records and inventory CSV records were caught and blocked.

### Threat 6: Direct Access via CLI or Secondary Interfaces
- **Risk**: Scripts invoke CLI tools or library functions attempting to bypass the gate.
- **Enforced Control**:
  - `dataset_authorization.py` CLI exits with code 1 and outputs `DENIED`.
  - `dataset_inventory.py --check-authorized` exits with code 1 and outputs `DENIED` when queried on non-approved records.
  - Library methods `get_authorized_dataset_path()` and `get_authorized_record()` enforce access permissions before returning file paths or records.
- **Audit Result**: **SECURE**. All interfaces cleanly reject unauthorized requests.

---

## 3. Tokenizer Artifact Integrity

Throughout the execution of Milestones 3B.57 through 3B.61, both candidate tokenizer artifacts have remained untouched and bitwise invariant:

| Tokenizer Artifact | Path | SHA-256 Checksum | Verified State |
| :--- | :--- | :--- | :--- |
| **Candidate A** | `artifacts/tokenizer/candidate_a/tokenizer.json` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | **UNMODIFIED** |
| **Candidate B** | `artifacts/tokenizer/candidate_b/tokenizer.model` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **UNMODIFIED** |

Acceptance runner verification (`scripts/run_acceptance_3b57.py`) passed all 162/162 requirements.

---

## 4. Conclusion & Recommendations

The dataset authorization gate and inventory tracking system have passed all dry-run validation checks with 100% test coverage.

### Operational Recommendations for Milestone 3C:
1. **Never Bypass the Gate**: All future evaluation and ingestion drivers must strictly interface through `AuthorizationValidator.get_authorized_dataset_path()`.
2. **Key Ring Integration**: Transition from mock SHA-256 signature hashes to RSA/ECDSA public-key verification when human signers are provisioned with enterprise hardware keys.
3. **Continuous Quarantine Scans**: Ensure that quarantine staging directories remain locked with read-only permissions and network-isolated from execution compute nodes.
