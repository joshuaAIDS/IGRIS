# IGRIS PHASE 12: SECURITY TEST RESULTS REPORT

**Document Identifier**: `IGRIS-P12-STR-2026-V1`  
**Execution Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Test Suite**: [test_phase12_acquisition_security.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_phase12_acquisition_security.py)  
**Execution Engine**: `pytest-9.2.0`, Python 3.11.9 (`win32`)

---

## 1. Executive Summary

Phase 12 conducted rigorous automated red-team security verification of the controlled dataset acquisition engine and quarantine validation pipeline. All 12 threat vectors specified in Section 6, along with default-deny gate lock enforcement and register integrity checks, were evaluated.

**Test Summary**:
- **Phase 12 Security Tests**: **14 / 14 PASSED** (0 failures, 0 warnings, 0 skips).
- **Total Project Regression Suite**: **355 / 355 PASSED** in 4.57 seconds.
- **Production Acceptance Runner**: **162 / 162 CHECKS PASSED**.
- **Candidate Tokenizer Invariants**: **100% PRESERVED**.

---

## 2. Granular Results by Security Vector

| Vector # | Security Vector / Test Name | Attack Scenario Simulated | Defense Mechanism | Result |
| :---: | :--- | :--- | :--- | :---: |
| **V01** | `test_unauthorized_domain_blocked` | Download from phishing domain or external IP | Domain whitelist check | **PASSED** |
| **V02** | `test_http_downgrade_blocked` | Insecure `http://` or `ftp://` request | Scheme strictness check | **PASSED** |
| **V03** | `test_redirect_abuse_blocked` | Redirect to unapproved domain or > 3 hops | Multi-hop redirect validator | **PASSED** |
| **V04** | `test_zip_slip_path_traversal_blocked` | Malicious zip/tar with `../../escape.sh` | Canonical sandbox path checking | **PASSED** |
| **V05** | `test_malicious_file_detection` | Executable binaries (`MZ`, `ELF`, `Mach-O`) | Magic byte header inspection | **PASSED** |
| **V06** | `test_hash_mismatch_detection` | Tampered content hash | SHA-256 check & `.part` purge | **PASSED** |
| **V07** | `test_corrupted_download_handling` | Peer disconnection / network abort midway | Partial download auto-cleanup | **PASSED** |
| **V08** | `test_oversized_file_blocked` | Byte stream exceeding `max_size_bytes` | Streaming cutoff and purge | **PASSED** |
| **V09** | `test_duplicate_archive_detected` | Ingesting duplicate archive content | Content hash deduplication ledger | **PASSED** |
| **V10** | `test_unicode_validation_failures` | Corrupted UTF-8 bytes and `\uFFFD` chars | Strict decoding & replacement check | **PASSED** |
| **V11** | `test_quarantine_isolation_and_immutability`| Staging file tampering | Read-only permissions (`0o444`) | **PASSED** |
| **V12** | `test_audit_log_integrity` | Malicious modification of audit trail | Chained SHA-256 log verification | **PASSED** |
| **Gate** | `test_default_deny_gate_lock` | Download attempt with locked gate | `AcquisitionGateLockedError` | **PASSED** |
| **Reg** | `test_phase12_registers_integrity` | Discrepancies in 32-source manifest/register | 32-source register validation | **PASSED** |

---

## 3. Actual Command Execution Logs

### 3.1 Phase 12 Security Test Suite Run

```powershell
PS C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch> C:\IGRIS\.venv\Scripts\python.exe -m pytest tests/test_phase12_acquisition_security.py -v
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0 -- C:\IGRIS\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch
plugins: anyio-4.16.0
collecting ... collected 14 items

tests/test_phase12_acquisition_security.py::test_unauthorized_domain_blocked PASSED [  7%]
tests/test_phase12_acquisition_security.py::test_http_downgrade_blocked PASSED [ 14%]
tests/test_phase12_acquisition_security.py::test_redirect_abuse_blocked PASSED [ 21%]
tests/test_phase12_acquisition_security.py::test_zip_slip_path_traversal_blocked PASSED [ 28%]
tests/test_phase12_acquisition_security.py::test_malicious_file_detection PASSED [ 35%]
tests/test_phase12_acquisition_security.py::test_hash_mismatch_detection PASSED [ 42%]
tests/test_phase12_acquisition_security.py::test_corrupted_download_handling PASSED [ 50%]
tests/test_phase12_acquisition_security.py::test_oversized_file_blocked PASSED [ 57%]
tests/test_phase12_acquisition_security.py::test_duplicate_archive_detected PASSED [ 64%]
tests/test_phase12_acquisition_security.py::test_unicode_validation_failures PASSED [ 71%]
tests/test_phase12_acquisition_security.py::test_quarantine_isolation_and_immutability PASSED [ 78%]
tests/test_phase12_acquisition_security.py::test_audit_log_integrity PASSED [ 85%]
tests/test_phase12_acquisition_security.py::test_default_deny_gate_lock PASSED [ 92%]
tests/test_phase12_acquisition_security.py::test_phase12_registers_integrity PASSED [100%]

============================= 14 passed in 0.29s ==============================
```

### 3.2 Full Project Regression Suite Run

```powershell
PS C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch> C:\IGRIS\.venv\Scripts\python.exe -m pytest tests -q
........................................................................ [ 20%]
........................................................................ [ 40%]
........................................................................ [ 60%]
........................................................................ [ 81%]
...................................................................      [100%]
355 passed in 4.57s
```

### 3.3 Final Acceptance Audit Run

```powershell
PS C:\IGRIS> C:\IGRIS\.venv\Scripts\python.exe C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts\run_acceptance_3b57.py
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

## 4. Cryptographic Artifact Integrity

Candidate A and Candidate B cryptographic hashes remain strictly identical to their initial certified baselines:
- **Candidate A SHA-256**: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- **Candidate B SHA-256**: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
