# IGRIS Dataset Authorization Test Matrix

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3B.61 — Dataset Authorization Dry Run & Security Validation  
**Document ID**: `IGRIS-DOC-ATM-3B61`  
**Test Harness**: `pytest` (Python 3.11.9)  
**Status**: VERIFIED & PASSING  

---

## 1. Overview

This matrix formalizes the comprehensive verification suite executed during the Milestone 3B.61 dry run. All tests were executed using synthetic fixtures exclusively. Zero production or private corpus files were accessed.

---

## 2. Test Execution Matrix

### 2.1 Authorization Lifecycle State Transitions

| Test ID | Initial State | Transition / Condition | Expected Gate Outcome | Enforced Error Pattern | Test Reference | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ST-01** | `LOCKED` | Initial quarantine staging | **DENIED** (`DatasetAccessDeniedError`) | `Status is 'LOCKED'` | `test_state_locked_fails_gate` | **PASS** |
| **ST-02** | `PENDING_REVIEW` | Extraction & sanitization done | **DENIED** (`DatasetAccessDeniedError`) | `Status is 'PENDING_REVIEW'` | `test_state_pending_review_fails_gate` | **PASS** |
| **ST-03** | `APPROVED` | All 4 sign-offs valid + manifest match | **ALLOWED** (Record returned) | N/A (Gate Clear) | `test_state_approved_passes_gate` | **PASS** |
| **ST-04** | `REJECTED` | One or more reviewers reject | **DENIED** (`DatasetAccessDeniedError`) | `Status is 'REJECTED'` | `test_state_rejected_fails_gate` | **PASS** |
| **ST-05** | `REVOKED` | Compliance trigger / EOL / tampering | **DENIED** (`DatasetAccessDeniedError`) | `Status is 'REVOKED'` | `test_state_revoked_fails_gate` | **PASS** |

---

### 2.2 Human Approval & Role Sign-Off Failure Modes

| Test ID | Sign-Off Scenario | Authority Roles Present | Expected Gate Outcome | Enforced Error Pattern | Test Reference | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SO-01** | Full Unanimous Approval | Custodian, Legal, Security, Architect | **ALLOWED** | Gate Clear | `test_authorization_template_parses_and_passes_gate` | **PASS** |
| **SO-02** | Missing Chief Architect | Custodian, Legal, Security | **DENIED** | `Missing required human sign-offs` | `test_missing_signatures_partial` | **PASS** |
| **SO-03** | Missing Security Lead | Custodian, Legal, Architect | **DENIED** | `Missing required human sign-offs` | `test_missing_required_role_denies_access` | **PASS** |
| **SO-04** | Role Rejection (Security) | Custodian, Legal, Architect = OK; Security = REJECTED | **DENIED** | `was 'REJECTED'` | `test_rejected_decision_denies_access` | **PASS** |
| **SO-05** | Invalid / Unknown Role | Role: `EXTERNAL_CONSULTANT` | **DENIED** | `Unrecognized sign-off role` | `test_invalid_role_in_json_fails_parse` | **PASS** |
| **SO-06** | Invalid Signature Hash | Hash string != 64 hex characters | **DENIED** | `Invalid digital signature hash` | `test_invalid_signature_hash_denies_access` | **PASS** |
| **SO-07** | Screening Unverified | `screening_verified: false` | **DENIED** | `PII screening verification is incomplete` | `test_unverified_screening_denies_access` | **PASS** |
| **SO-08** | License Unapproved | `license_approved: false` | **DENIED** | `Licensing approval is incomplete` | `test_unapproved_license_denies_access` | **PASS** |
| **SO-09** | Expired Approval Window | `expiry_date` < Reference Time | **DENIED** | `Authorization expired on` | `test_expired_approval_fails_gate` | **PASS** |

---

### 2.3 Cryptographic Integrity & Tamper Detection

| Test ID | Target Component | Modification / Tamper Scenario | Expected Gate Outcome | Enforced Error Pattern | Test Reference | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CR-01** | Manifest Content | Total line count changed in `manifest.json` | **DENIED** | `Tamper alert: Manifest computed hash` | `test_manifest_hash_tamper_detection` | **PASS** |
| **CR-02** | Data File Bytes | Single character modified in `.jsonl` file | **DENIED** | `File hash mismatch for` | `test_file_content_tamper_detection` | **PASS** |
| **CR-03** | Data File Truncation | Data file byte count altered | **DENIED** | `File byte mismatch for` | `test_file_content_tamper_detection` | **PASS** |
| **CR-04** | Manifest Generation | Deterministic repeat on identical files | **MATCH** | Exact bitwise hash equality | `test_deterministic_manifest_repeated_generation` | **PASS** |

---

### 2.4 Inventory-to-Authorization Consistency

| Test ID | Consistency Check | Inconsistency Injected | Expected Gate Outcome | Enforced Error Pattern | Test Reference | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **IC-01** | Dataset ID Match | Auth ID != Inventory ID | **DENIED** | `Dataset ID mismatch` | `test_inventory_consistency_status_mismatch` | **PASS** |
| **IC-02** | Status Concordance | Auth = `APPROVED`, Inventory = `PENDING_REVIEW` | **DENIED** | `Authorization status mismatch` | `test_inventory_consistency_status_mismatch` | **PASS** |
| **IC-03** | Screening Concordance | Auth = `verified`, Inventory = `PENDING` | **DENIED** | `Screening status mismatch` | `test_inventory_consistency_screening_mismatch` | **PASS** |
| **IC-04** | Inventory Gate Check | Accessing `LOCKED` record via `get_authorized_record` | **DENIED** | `is in 'LOCKED' state` | `test_inventory_get_authorized_record_blocks_non_approved` | **PASS** |

---

### 2.5 Attack Surface & Entry Point Protection

| Test ID | Interface Tested | Unauthorized Invocation Scenario | Expected Outcome | Enforced Behavior | Test Reference | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AS-01** | CLI: `dataset_authorization.py` | Executed against `LOCKED` authorization file | **DENIED** | Exit code != 0, prints `DENIED` | `test_cli_blocks_unauthorized_dataset` | **PASS** |
| **AS-02** | CLI: `dataset_inventory.py` | `--check-authorized` on locked dataset | **DENIED** | Exit code != 0, prints `DENIED` | `test_cli_blocks_unauthorized_dataset` | **PASS** |
| **AS-03** | Library: `get_authorized_dataset_path` | Called with unapproved / locked record | **DENIED** | Raises `DatasetAccessDeniedError` | `test_library_get_authorized_dataset_path_blocks_unauthorized` | **PASS** |
| **AS-04** | Metadata Parser | Injected malformed JSON `{ "invalid": [1, 2, }` | **DENIED** | Raises `DatasetAccessDeniedError` | `test_malformed_json_syntax_fails_gate` | **PASS** |
| **AS-05** | Metadata Parser | Missing required keys (e.g. `manifest_sha256`) | **DENIED** | Raises `DatasetAccessDeniedError` | `test_malformed_metadata_missing_keys` | **PASS** |
| **AS-06** | Immediate Revocation | Dynamic update of status to `REVOKED` | **DENIED** | Immediate gate lockout | `test_revocation_blocks_immediately` | **PASS** |

---

## 3. Test Suite Metrics Summary

- **Total Milestone 3B.61 Security Tests**: 17
- **Passed**: 17 (100.0%)
- **Failed**: 0
- **Skipped**: 0
- **Execution Time**: 0.39s
