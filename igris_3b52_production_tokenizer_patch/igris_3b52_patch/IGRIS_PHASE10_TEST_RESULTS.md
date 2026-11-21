# IGRIS Phase 10: Comprehensive Test Execution Results

**Project**: IGRIS Multilingual Decoder-Only Transformer  
**Active Patch**: `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Document ID**: `IGRIS-REPORT-PHASE10-TEST-RESULTS`  
**Classification**: OFFICIAL INDEPENDENT VERIFICATION RECORD  
**Execution Date**: 2026-11-17  
**Python Runtime**: `C:\IGRIS\.venv\Scripts\python.exe` (Python 3.11.9)  
**Pytest Version**: 9.2.0  
**Overall Status**: **`ALL TEST SUITES PASSED (333/333 Unit Tests, 162/162 Acceptance Checks)`**  

---

## 1. Executive Test Execution Summary

In accordance with Section 7 of the Phase 10 directives, the complete testing suite was executed across the full codebase, governance-specific verifiers, signature intake engines, red-team security attack vectors, and clean-process tokenizer acceptance runners.

```
================================================================================
IGRIS PHASE 10 TEST EXECUTION SUMMARY
================================================================================
1. Full Pytest Regression Suite      : 333 / 333 PASSED (Exit Code: 0, 7.55s)
2. Governance Authorization Tests    :  11 /  11 PASSED (Exit Code: 0, 0.19s)
3. Signature Intake Security Tests   :  22 /  22 PASSED (Exit Code: 0, 0.13s)
4. Red-Team Security Adversarial     :  10 /  10 PASSED (Exit Code: 0, 0.13s)
5. Phase 9 Reviewer Operations Suite :   8 /   8 PASSED (Exit Code: 0, 0.06s)
6. Phase 10 Reconciliation Suite     :   6 /   6 PASSED (Exit Code: 0, 0.12s)
7. Clean-Process Acceptance Suite    : 162 / 162 PASSED (Exit Code: 0, 1.52s)
--------------------------------------------------------------------------------
TOTAL TEST CHECKS EXECUTED: 495
TOTAL PASSED              : 495
TOTAL FAILED              : 0
TOTAL SKIPPED             : 0
================================================================================
```

---

## 2. Detailed Test Suite Execution Logs

### Suite 1: Full Pytest Regression Suite
- **Command**: `& "C:\IGRIS\.venv\Scripts\python.exe" -m pytest tests -q`
- **Working Directory**: `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`
- **Exit Code**: `0`
- **Output**:
  ```
  ........................................................................ [ 21%]
  ........................................................................ [ 43%]
  ........................................................................ [ 64%]
  ........................................................................ [ 86%]
  ..............................................                           [100%]
  333 passed in 7.55s
  ```
- **Evaluation**: Zero failures, zero warnings, zero regressions.

### Suite 2: Governance-Specific Authorization Tests
- **Command**: `& "C:\IGRIS\.venv\Scripts\python.exe" -m pytest tests/test_dataset_authorization.py -v`
- **Exit Code**: `0`
- **Output**:
  ```
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_authorization_template_parses_and_passes_gate PASSED [  9%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_missing_auth_file_denies_access PASSED [ 18%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_dataset_id_mismatch_denies_access PASSED [ 27%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_status_not_approved_denies_access PASSED [ 36%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_missing_required_role_denies_access PASSED [ 45%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_rejected_decision_denies_access PASSED [ 54%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_unverified_screening_denies_access PASSED [ 63%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_unapproved_license_denies_access PASSED [ 72%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_invalid_signature_hash_denies_access PASSED [ 81%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_manifest_hash_tamper_detection PASSED [ 90%]
  tests/test_dataset_authorization.py::TestDatasetAuthorization::test_file_content_tamper_detection PASSED [100%]
  11 passed in 0.19s
  ```

### Suite 3: Signature Intake & Cryptographic Verification Tests
- **Command**: `& "C:\IGRIS\.venv\Scripts\python.exe" -m pytest tests/test_dataset_3c10_review_intake.py tests/test_phase7_approval_intake.py -v`
- **Exit Code**: `0`
- **Output**:
  ```
  tests/test_dataset_3c10_review_intake.py::test_3c10_deliverables_exist PASSED [  4%]
  tests/test_dataset_3c10_review_intake.py::test_human_approval_schema_v1_valid PASSED [  9%]
  tests/test_dataset_3c10_review_intake.py::test_source_approval_state_v2_schema_and_counts PASSED [ 13%]
  tests/test_dataset_3c10_review_intake.py::test_cryptographic_verification_valid_signature PASSED [ 18%]
  tests/test_dataset_3c10_review_intake.py::test_cryptographic_verification_invalid_and_missing_signature PASSED [ 22%]
  tests/test_dataset_3c10_review_intake.py::test_cryptographic_verification_expired_approval_and_revoked_key PASSED [ 27%]
  tests/test_dataset_3c10_review_intake.py::test_document_tamper_and_sha256_mismatch PASSED [ 31%]
  tests/test_dataset_3c10_review_intake.py::test_quorum_consensus_and_conflicts PASSED [ 36%]
  tests/test_dataset_3c10_review_intake.py::test_audit_trail_hash_chain PASSED [ 40%]
  tests/test_dataset_3c10_review_intake.py::test_candidate_invariants_preserved PASSED [ 45%]
  tests/test_phase7_approval_intake.py::test_valid_authentic_intake_submission PASSED [ 50%]
  tests/test_phase7_approval_intake.py::test_invalid_signature_fails_closed PASSED [ 54%]
  tests/test_phase7_approval_intake.py::test_missing_signature_fails_closed PASSED [ 59%]
  tests/test_phase7_approval_intake.py::test_expired_signature_fails_closed PASSED [ 63%]
  tests/test_phase7_approval_intake.py::test_revoked_key_fails_closed PASSED [ 68%]
  tests/test_phase7_approval_intake.py::test_role_mismatch_fails_closed PASSED [ 72%]
  tests/test_phase7_approval_intake.py::test_source_id_mismatch_and_malformed_fails_closed PASSED [ 77%]
  tests/test_phase7_approval_intake.py::test_approval_scope_independence_axiom PASSED [ 81%]
  tests/test_phase7_approval_intake.py::test_replayed_approval_submission_fails_closed PASSED [ 86%]
  tests/test_phase7_approval_intake.py::test_modified_review_document_fails_closed PASSED [ 90%]
  tests/test_phase7_approval_intake.py::test_unanimous_consensus_required_for_quarantine_staging PASSED [ 95%]
  tests/test_phase7_approval_intake.py::test_single_rejection_overrides_all_approvals PASSED [100%]
  22 passed in 0.13s
  ```

### Suite 4: Red-Team Security Adversarial Tests
- **Command**: `& "C:\IGRIS\.venv\Scripts\python.exe" -m pytest tests/test_red_team_security.py -v`
- **Exit Code**: `0`
- **Output**:
  ```
  tests/test_red_team_security.py::test_redteam_attack_01_unauthorized_dataset_ingestion PASSED [ 10%]
  tests/test_red_team_security.py::test_redteam_attack_02_approval_signature_forgery PASSED [ 20%]
  tests/test_red_team_security.py::test_redteam_attack_03_signature_replay PASSED [ 30%]
  tests/test_red_team_security.py::test_redteam_attack_04_revoked_key_rejection PASSED [ 40%]
  tests/test_red_team_security.py::test_redteam_attack_05_expired_approval_rejection PASSED [ 50%]
  tests/test_red_team_security.py::test_redteam_attack_06_role_impersonation PASSED [ 60%]
  tests/test_red_team_security.py::test_redteam_attack_07_audit_log_tampering PASSED [ 70%]
  tests/test_red_team_security.py::test_redteam_attack_08_unauthorized_pipeline_transitions PASSED [ 80%]
  tests/test_red_team_security.py::test_redteam_attack_09_approval_state_manipulation PASSED [ 90%]
  tests/test_red_team_security.py::test_redteam_attack_10_candidate_substitution_detection PASSED [100%]
  10 passed in 0.13s
  ```

### Suite 5: Clean-Process Tokenizer Acceptance Suite
- **Command**: `& "C:\IGRIS\.venv\Scripts\python.exe" scripts/run_acceptance_3b57.py`
- **Exit Code**: `0`
- **Output Summary**:
  ```
  ================================================================================
  REQUIREMENT SUMMARY
  ================================================================================
  Req  1 | [PASS] Clean-process artifact loading                                         (1/1 tests)
  Req  2 | [PASS] Verify exact vocabulary size: 32,768                                   (6/6 tests)
  Req  3 | [PASS] Verify exactly 12 structural tokens at IDs 0–11                        (5/5 tests)
  Req  4 | [PASS] Verify Candidate A has no unintended special added tokens              (5/5 tests)
  Req  5 | [PASS] Verify Candidate B PAD=0 and BOS/EOS/UNK=-1 at runtime                 (9/9 tests)
  Req  6 | [PASS] Verify all 256 byte fallback mappings                                  (6/6 tests)
  Req  7 | [PASS] Test raw binary round-trip for bytes 0x00–0xFF                         (16/16 tests)
  Req  8 | [PASS] Test text round-trip in NFC and exact modes                            (32/32 tests)
  Req  9 | [PASS] Test structural-token isolation                                        (68/68 tests)
  Req 10 | [PASS] Test save/reload consistency                                           (4/4 tests)
  Req 11 | [PASS] Verify SHA-256 hashes against metadata                                 (6/6 tests)
  Req 12 | [PASS] Verify Unicode database version is actually 15.1.0                     (2/2 tests)
  Req 13 | [PASS] Build twice from identical synthetic inputs and compare artifacts for deterministic output (2/2 tests)
  --------------------------------------------------------------------------------
  Total Individual Tests Executed: 162
  Passed: 162
  Failed: 0
  Skipped: 0
  --------------------------------------------------------------------------------
  ARTIFACT HASHES:
    Candidate A (tokenizer.json):  ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561
    Candidate B (tokenizer.model): d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888
  ================================================================================
  ```

---

## 3. Test Invariants Sign-Off

All tests passed with zero suppressions or modifications to expected security outcomes. Candidate tokenizer artifacts remain bitwise invariant.
