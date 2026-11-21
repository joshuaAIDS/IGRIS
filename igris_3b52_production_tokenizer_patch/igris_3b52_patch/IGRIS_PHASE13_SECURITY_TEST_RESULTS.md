# IGRIS PHASE 13: COMPREHENSIVE SECURITY TEST RESULTS REPORT

**Document Identifier**: `IGRIS-P13-STR-2026-V1`  
**Execution Date**: `2026-11-18`  
**Operating Model**: `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target Invariants**:
- Candidate A SHA-256: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- Candidate B SHA-256: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
- Production Ingress Gate: `LOCKED`

---

## 1. Executive Summary

Phase 13 conducted exhaustive automated red-team security verification of the source-specific owner authorization mechanism, secure acquisition engine, and quarantine validation pipeline. All 24 mandatory security vectors specified in Section 9 were evaluated.

**Test Summary**:
- **Phase 13 Controlled Acquisition Security Tests**: **24 / 24 PASSED** (0 failures, 0 skips).
- **Phase 12 Ingress Pipeline Security Tests**: **14 / 14 PASSED**.
- **Complete Project Pytest Suite**: **379 / 379 PASSED** in 4.63 seconds.
- **Production Acceptance Runner**: **162 / 162 CHECKS PASSED**.
- **Candidate Tokenizer Invariants**: **100% PRESERVED**.

---

## 2. Granular Results Across 24 Security Vectors

| # | Security Vector / Test Name | Attack Scenario / Condition Evaluated | Defense Mechanism | Result |
| :---: | :--- | :--- | :--- | :---: |
| **01** | `test_unauthorized_acquisition_rejection` | Acquisition attempted without grant | Default-Deny access check | **PASSED** |
| **02** | `test_missing_owner_approval_default_deny` | Querying status without owner approval | Raises `UnauthorizedAcquisitionError` | **PASSED** |
| **03** | `test_revoked_authorization_rejection` | Grant marked as revoked | Immediate block via `RevokedAuthorizationError` | **PASSED** |
| **04** | `test_expired_authorization_rejection` | Authorization timestamp past expiry | Expiry detection via `ExpiredAuthorizationError` | **PASSED** |
| **05** | `test_unauthorized_source_url_rejection` | Requested URL diverges from grant URL | Exact URL prefix verification | **PASSED** |
| **06** | `test_unauthorized_domain_rejection` | Download from phishing/unapproved host | Domain whitelist check | **PASSED** |
| **07** | `test_http_downgrade_rejection` | Plain HTTP or protocol downgrade | Strict HTTPS scheme enforcement | **PASSED** |
| **08** | `test_redirect_abuse_rejection` | Redirect targeting unapproved domain | Hop-by-hop redirect inspector ($\le 3$ hops) | **PASSED** |
| **09** | `test_oversized_download_cutoff` | Byte stream exceeding configured ceiling | Streaming cutoff and `.part` unlinking | **PASSED** |
| **10** | `test_interrupted_downloads_cleanup` | Network disconnection / socket reset midway | Atomic rollback; `.part` purged | **PASSED** |
| **11** | `test_hash_mismatch_rejection` | Downloaded bytes fail SHA-256 match | Cryptographic verification; `.part` deleted | **PASSED** |
| **12** | `test_corrupted_archive_rejection` | Truncated or corrupt zip file | Archive integrity inspection | **PASSED** |
| **13** | `test_archive_traversal_zip_slip_rejection`| Malicious archive with `../../escape` | Sandbox boundary enforcement (`commonpath`) | **PASSED** |
| **14** | `test_executable_file_rejection` | Executable disguised as data (`MZ`, `ELF`) | Magic byte header inspection | **PASSED** |
| **15** | `test_invalid_utf8_rejection` | Invalid byte sequences or `\uFFFD` | Strict UTF-8 decoding & replacement check | **PASSED** |
| **16** | `test_unicode_normalization_enforced` | Non-NFC decomposed text (`e\u0301`) | Evaluated via `unicodedata.is_normalized` | **PASSED** |
| **17** | `test_pii_screening` | Text containing emails, phones, SSNs, cards | Regex screening; sample card redaction | **PASSED** |
| **18** | `test_duplicate_acquisition_rejection` | Identical content SHA-256 ingested twice | Global ledger lookup in `content_hash_ledger` | **PASSED** |
| **19** | `test_replay_attack_rejection` | Authorization nonce reused across sessions | Nonce consumption registry | **PASSED** |
| **20** | `test_audit_chain_tampering_detection` | Line modification in acquisition audit log | Chained SHA-256 verification | **PASSED** |
| **21** | `test_concurrent_acquisition_attempts` | Concurrent acquisition on same source | Concurrency lockfile (`<source_id>.lock`) | **PASSED** |
| **22** | `test_quarantine_integrity_preserved` | Quarantined raw file write permissions | Read-only permissions enforced (`0o444`) | **PASSED** |
| **23** | `test_recovery_after_process_interruption` | Residual `.part` file from previous crash | Orphan cleanup; clean restart | **PASSED** |
| **24** | `test_tier_isolation_enforcement` | Attempting training on Tier 2/3/4 sources | Tier isolation boundary check | **PASSED** |

---

## 3. Actual Command Execution Logs

### 3.1 Phase 13 Test Suite Run

```powershell
PS C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch> C:\IGRIS\.venv\Scripts\python.exe -m pytest tests/test_phase13_controlled_acquisition.py -v
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0 -- C:\IGRIS\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch
plugins: anyio-4.16.0
collecting ... collected 24 items

tests/test_phase13_controlled_acquisition.py::test_unauthorized_acquisition_rejection PASSED [  4%]
tests/test_phase13_controlled_acquisition.py::test_missing_owner_approval_default_deny PASSED [  8%]
tests/test_phase13_controlled_acquisition.py::test_revoked_authorization_rejection PASSED [ 12%]
tests/test_phase13_controlled_acquisition.py::test_expired_authorization_rejection PASSED [ 16%]
tests/test_phase13_controlled_acquisition.py::test_unauthorized_source_url_rejection PASSED [ 20%]
tests/test_phase13_controlled_acquisition.py::test_unauthorized_domain_rejection PASSED [ 25%]
tests/test_phase13_controlled_acquisition.py::test_http_downgrade_rejection PASSED [ 29%]
tests/test_phase13_controlled_acquisition.py::test_redirect_abuse_rejection PASSED [ 33%]
tests/test_phase13_controlled_acquisition.py::test_oversized_download_cutoff PASSED [ 37%]
tests/test_phase13_controlled_acquisition.py::test_interrupted_downloads_cleanup PASSED [ 41%]
tests/test_phase13_controlled_acquisition.py::test_hash_mismatch_rejection PASSED [ 45%]
tests/test_phase13_controlled_acquisition.py::test_corrupted_archive_rejection PASSED [ 50%]
tests/test_phase13_controlled_acquisition.py::test_archive_traversal_zip_slip_rejection PASSED [ 54%]
tests/test_phase13_controlled_acquisition.py::test_executable_file_rejection PASSED [ 58%]
tests/test_phase13_controlled_acquisition.py::test_invalid_utf8_rejection PASSED [ 62%]
tests/test_phase13_controlled_acquisition.py::test_unicode_normalization_enforced PASSED [ 66%]
tests/test_phase13_controlled_acquisition.py::test_pii_screening PASSED  [ 70%]
tests/test_phase13_controlled_acquisition.py::test_duplicate_acquisition_rejection PASSED [ 75%]
tests/test_phase13_controlled_acquisition.py::test_replay_attack_rejection PASSED [ 79%]
tests/test_phase13_controlled_acquisition.py::test_audit_chain_tampering_detection PASSED [ 83%]
tests/test_phase13_controlled_acquisition.py::test_concurrent_acquisition_attempts_serialized PASSED [ 87%]
tests/test_phase13_controlled_acquisition.py::test_quarantine_integrity_preserved PASSED [ 91%]
tests/test_phase13_controlled_acquisition.py::test_recovery_after_process_interruption PASSED [ 95%]
tests/test_phase13_controlled_acquisition.py::test_tier_isolation_enforcement PASSED [100%]

============================= 24 passed in 0.27s ==============================
```

### 3.2 Full Project Regression Suite Run

```powershell
PS C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch> C:\IGRIS\.venv\Scripts\python.exe -m pytest tests -q
........................................................................ [ 18%]
........................................................................ [ 37%]
........................................................................ [ 56%]
........................................................................ [ 75%]
........................................................................ [ 94%]
...................                                                      [100%]
379 passed in 4.63s
```

### 3.3 Acceptance Runner Run

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

## 4. Cryptographic Artifact Integrity Verification

Candidate A and Candidate B cryptographic hashes remain strictly identical to their initial certified baselines:
- **Candidate A SHA-256**: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- **Candidate B SHA-256**: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
