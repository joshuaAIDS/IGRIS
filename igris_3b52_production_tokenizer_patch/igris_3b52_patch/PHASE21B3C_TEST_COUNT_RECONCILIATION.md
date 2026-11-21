# PHASE 21B3C — TEST COUNT RECONCILIATION REPORT
## Comprehensive Reconciliation of Current Inventory, Historical Baselines, and Focused Test Suites

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3C  

---

## 1. Executive Summary

Phase 21B3C resolves all outstanding ambiguities regarding repository test inventory counts, distinguishing between **collected unique test cases** and **execution results**, and explicitly qualifying **historical claims** that cannot be independently reproduced in the current single-session environment.

```
+-----------------------------------+---------------+-----------------------------------------------------------------------+
| Metric                            | Quantity      | Exact Classification & Status                                         |
+-----------------------------------+---------------+-----------------------------------------------------------------------+
| Total Test Files on Disk          | 43 files      | Complete unique test modules in `tests/` directory                    |
| Historical Baseline Test Files    | 34 files      | Modules established through Phase 20A                                 |
| Phase 21B Baseline Test Files     | 38 files      | Test files on disk upon completion of Phase 21B (34 hist + 4 focused) |
| Focused Extension Test Files      | 9 files       | Modules added from Phase 20B through Phase 21B3B                      |
| Total Collected Test Cases        | 530 items     | Unique tests discovered by `pytest --collect-only`                    |
| Current Execution Passed          | 529 passed    | Tests passing in full repository execution                            |
| Current Execution Failed          | 1 failed      | `test_readiness.py::TestReadiness::test_governance_isolation_check`   |
| Current Execution Skipped         | 0 skipped     | Zero tests skipped                                                    |
| Current Execution Deselected      | 0 deselected  | Zero tests deselected                                                 |
| Cumulative Focused Executions     | 60 passed     | 60 / 60 tests pass across the 9 focused phase suites (100%)           |
+-----------------------------------+---------------+-----------------------------------------------------------------------+
```

---

## 2. Historical Baseline vs Current Reproducibility

### The Phase 20A Claim (470 Passed Across 34 Files)
- **Historical Record:** In `PHASE20A_COMPLETION_REPORT.md` (and cited in Phase 20B), it was reported that executing full repository regression yielded **470 / 470 passed** across **34 test files** in 44.5 seconds.
- **Current Verification:**
  - The exact 34 historical test files exist in `tests/` today.
  - When collected via pytest, these 34 files define exactly **470 unique test cases**.
- **Crucial Qualification (Historical Claim Not Independently Reproducible):**
  - When the full test suite is executed in the current workspace, **529 tests pass and 1 test fails**.
  - The failing test is `test_readiness.py::TestReadiness::test_governance_isolation_check` (one of the 34 historical files).
  - Therefore, the historical claim that all 470 historical tests pass cleanly simultaneously is **historically reported but not independently reproducible** in the current workspace state without modifying the filesystem or resolving the quarantine folder.

---

## 3. Disambiguation of the "Phase 21B Baseline: 38 Test Files"

In Phase 21B3A documentation, a reference was made to the complete codebase containing "38 test files". This caused confusion when Phase 21B3B reported 43 test files.

### Exact Explanation of the 38-File Milestone:
The figure **38 test files** represents a historical baseline frozen at the conclusion of **Phase 21B**:
- **34 Historical Files:** From Phases 1 through 20A.
- **Plus 4 Focused Modules Added Sequentially:**
  1. `test_phase20b_consistency_verification.py` (Phase 20B)
  2. `test_phase21_controlled_dataset_preparation.py` (Phase 21)
  3. `test_phase21a_tokenizer_selection_and_dataset_review.py` (Phase 21A)
  4. `test_phase21b_indiccorp_verification.py` (Phase 21B)
- **Total at Phase 21B Completion:** $34 + 4 = \mathbf{38	ext{ test files}}$.

Subsequent subphases added 5 additional test files:
- Phase 21B1: `test_phase21b1_release_identity_and_license_reconciliation.py` (39 files)
- Phase 21B2: `test_phase21b2_path_statistics_and_projection_correction.py` (40 files)
- Phase 21B3: `test_phase21b3_immutable_metadata_verification.py` (41 files)
- Phase 21B3A: `test_phase21b3a_planning_and_evidence_corrections.py` (42 files)
- Phase 21B3B: `test_phase21b3b_metadata_capacity_and_test_reconciliation.py` (43 files)

Thus, the current unique inventory is exactly **43 test files**. The 38-file citation was an unrefreshed historical snapshot from Phase 21B.

---

## 4. Disambiguation of the "470 + 60" Arithmetic

In Phase 21B3B, it was observed that $470 + 60 = 530$. Under Phase 21B3C governance, this must **not** be assumed to imply that 530 tests passed:

1. **Collection vs Execution Distinction:**
   - **Collected Items:** Exactly 530 unique test cases are collected (470 from historical files + 60 from focused phase extensions).
   - **Executed Tests:** Running `pytest` across all 43 files yields **529 PASSED**, **1 FAILED**, **0 SKIPPED**, **0 DESELECTED**.
2. **Focused Regression Scope:**
   - The 9 focused regression suites define exactly 60 test cases:
     - `test_phase20b`: 4
     - `test_phase21`: 6
     - `test_phase21a`: 4
     - `test_phase21b`: 7
     - `test_phase21b1`: 7
     - `test_phase21b2`: 7
     - `test_phase21b3`: 7
     - `test_phase21b3a`: 8
     - `test_phase21b3b`: 10
     - Total: **60 tests**.
   - When these 9 focused modules are run in isolation, they achieve **60 / 60 passed (100%)**.
3. **The Danger of Arithmetic Assumption:**
   - Stating "470 passed + 60 passed = 530 passed" falsely implies 100% full-suite pass rate.
   - The verified reality is: **529 passed, 1 failed**.

---

## 5. Root Cause Analysis of the Single Test Failure

- **Failing Test:** `tests/test_readiness.py::TestReadiness::test_governance_isolation_check`
- **Failure Message:** `AssertionError: 'quarantine' unexpectedly found in 'quarantine'`
- **Mechanism:**
  - `test_readiness.py` inspects all files and directories in `_PATCH_ROOT.rglob("*")` that do not end in `.md` or `.markdown`, asserting `self.assertNotIn("quarantine", p.name.lower())`.
  - In `scripts/secure_acquisition_engine.py:312`, the engine logs audit events to `Path("quarantine/logs/acquisition_audit.jsonl")`.
  - During negative security and acquisition tests (where the engine correctly rejects unauthorized downloads with `BLOCKED_GATE_LOCKED`), the engine instantiated the directory `quarantine/logs/` within `_PATCH_ROOT`.
  - The directory name `quarantine` violates the string check in `test_readiness.py`.
- **Security Assessment:**
  - No production corpus or unapproved data exists in that folder.
  - The folder contains solely 5,135 bytes of JSONL audit logs confirming that unauthorized access attempts were blocked.
  - In this read-only verification phase, the directory is documented as a forensic finding rather than silently altered.
