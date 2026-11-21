# PHASE 21B3A — TEST SCOPE RECONCILIATION
## Scope Clarification of the 42-Test Suite vs Project-Wide Regression Inventory

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3A  

---

## 1. Test Suite Disambiguation

In Phase 21B3, test execution reported a passing score of **42/42 tests**.

To prevent any misunderstanding regarding the verification boundary, this document formally records that the 42 tests represent the:

**FOCUSED_PHASE_20B_21B3_REGRESSION_GROUP**  
$$\mathbf{FOCUSED\_PHASE\_20B\_21B3\_REGRESSION\_GROUP}$$

It does **not** represent the complete, exhaustive test suite of the IGRIS repository across all historical phases (Phases 1–19).

---

## 2. Detailed Breakdown of the 42-Test Regression Group

```
+---------------------------------------------------------------+---------------+---------------------------------------+
| Test Module Path                                              | Tests Passed  | Target Verification Scope             |
+---------------------------------------------------------------+---------------+---------------------------------------+
| tests/test_phase20b_consistency_verification.py               | 4 / 4         | Physical hashes, parameters, ledger   |
| tests/test_phase21_controlled_dataset_preparation.py          | 6 / 6         | Source license review, 0 authorized   |
| tests/test_phase21a_tokenizer_selection_and_dataset_review.py | 4 / 4         | Tokenizer selection record, gate lock |
| tests/test_phase21b_indiccorp_verification.py                 | 7 / 7         | IndicCorp 7 sources, CC0 evidence     |
| tests/test_phase21b1_release_identity_and_license_reconcil.   | 7 / 7         | IndicCorp v2 disambiguation, ACL stats|
| tests/test_phase21b2_path_statistics_and_projection_correct.  | 7 / 7         | Path correction, 10,947M Table 3      |
| tests/test_phase21b3_immutable_metadata_verification.py       | 7 / 7         | 9 LFS files, 183.7GB storage arithmetic|
+---------------------------------------------------------------+---------------+---------------------------------------+
| TOTAL FOCUSED REGRESSION GROUP                                | 42 / 42       | Phases 20B through 21B3 Invariants    |
+---------------------------------------------------------------+---------------+---------------------------------------+
```

---

## 3. Project-Wide Test Inventory

The complete IGRIS codebase contains **38 test files** comprising over 150 individual test cases covering architecture construction, distributed sharding, checkpoint rollback, PII sanitization regexes, and contract verifications.

Historical test reports are preserved unedited.