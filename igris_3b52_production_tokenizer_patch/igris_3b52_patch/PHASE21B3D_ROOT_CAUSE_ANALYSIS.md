# PHASE 21B3D — ROOT CAUSE ANALYSIS REPORT
## Forensic Investigation of the Governance Test Isolation Failure in `test_readiness.py`

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3D  
**Target Failure:** `tests/test_readiness.py::TestReadiness::test_governance_isolation_check`  

---

## 1. Executive Summary

During the Phase 21B3C repository-wide test execution across all 43 test files (530 collected tests), exactly one test failed:
```text
FAILED igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_readiness.py::TestReadiness::test_governance_isolation_check
AssertionError: 'quarantine' unexpectedly found in 'quarantine'
1 failed, 529 passed in 39.46s
```

Phase 21B3D isolates, reproduces, and documents the exact architectural root cause of this failure before implementing the remediation.

---

## 2. Code Inspection & Triggering Mechanism

### The Assertion in `test_readiness.py`
In `tests/test_readiness.py:86-97`:
```python
    def test_governance_isolation_check(self) -> None:
        """Verifies zero access to private training data or production corpus."""
        patch_files = list(_PATCH_ROOT.rglob("*"))
        for p in patch_files:
            if p.suffix.lower() in [".md", ".markdown"]:
                continue
            name_lower = p.name.lower()
            # Ensure no production corpus or quarantine files exist in the patch
            self.assertNotIn("quarantine", name_lower)
            self.assertNotIn("approved_line_inventory.csv", name_lower)
            self.assertNotIn("tamil_nfc_deduplicated.txt", name_lower)
```
- `_PATCH_ROOT.rglob("*")` recursively enumerates all filesystem nodes (both **files** and **directories**) within `igris_3b52_patch`.
- If any directory or file name contains `"quarantine"`, the check raises `AssertionError`.

### The Default Audit Logging Path in `secure_acquisition_engine.py`
In `scripts/secure_acquisition_engine.py:301-313`:
```python
    def __init__(
        self,
        gate_unlocked: bool = False,
        audit_log_path: Optional[Path] = None,
        custom_whitelist: Optional[Set[str]] = None,
        authorizer: Any = None
    ):
        self.gate_unlocked = gate_unlocked
        self.custom_whitelist = custom_whitelist
        self.authorizer = authorizer
        if audit_log_path is None:
            audit_log_path = Path("quarantine/logs/acquisition_audit.jsonl")
        self.audit_logger = AcquisitionAuditLogger(audit_log_path)
```
And in `AcquisitionAuditLogger.__init__` (`scripts/secure_acquisition_engine.py:211-214`):
```python
    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._get_latest_hash()
```
- When `SecureAcquisitionEngine` is instantiated without an explicit `audit_log_path`, it defaults to the relative path `Path("quarantine/logs/acquisition_audit.jsonl")`.
- `AcquisitionAuditLogger.__init__` immediately executes `self.log_path.parent.mkdir(parents=True, exist_ok=True)`.
- Because this path is **relative to the current working directory** (`os.getcwd()`), instantiating `SecureAcquisitionEngine()` inside `_PATCH_ROOT` immediately creates the directory `quarantine/logs/` within `_PATCH_ROOT`.

---

## 3. Identification of Triggering Tests

Inspection of all 43 test modules revealed that while Phase 12 and Phase 13 tests properly passed `audit_log_path=tmp_path / "audit.jsonl"`, four later test suites called `SecureAcquisitionEngine()` with default parameters:

1. **`tests/test_phase20_final_readiness.py:241`:**
   Called `engine = SecureAcquisitionEngine()` inside a `tempfile.TemporaryDirectory()`, but omitted passing `audit_log_path`, thereby creating `quarantine/logs/` in the working directory and logging a blocked acquisition event.
2. **`tests/test_phase20b_consistency_verification.py:176`:**
   Called `engine = SecureAcquisitionEngine()` with `audit_log_path=None` and called `download_source()` with `destination_path=Path(PATCH_ROOT) / "tmp_test.bin"`, writing directly to `quarantine/logs/acquisition_audit.jsonl`.
3. **`tests/test_phase21_controlled_dataset_preparation.py:120`:**
   Called `engine = SecureAcquisitionEngine()`, creating the directory structure upon instantiation.
4. **`tests/test_phase21a_tokenizer_selection_and_dataset_review.py:95`:**
   Called `engine = SecureAcquisitionEngine()`, creating the directory structure upon instantiation.

---

## 4. Working Directory (`cwd`) Dependency Analysis

When pytest was invoked with working directory `_PATCH_ROOT`:
$$	ext{cwd} = 	ext{C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch}$$
The relative path `quarantine/logs/acquisition_audit.jsonl` resolved to:
$$	ext{C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\quarantine\logscquisition_audit.jsonl}$$

When `test_readiness.py` subsequently scanned `_PATCH_ROOT`, it encountered the newly created directory `quarantine`, triggering the assertion failure.

---

## 5. Security & Provenance Assessment

Forensic inspection of the created file `quarantine/logs/acquisition_audit.jsonl` (5,135 bytes) confirmed:
- Zero bytes of production corpus or private training data were stored.
- All 9 entries were authentic audit log records documenting that unauthorized acquisition requests (e.g. `SRC-UNAUTH-01`, `SRC-TM-01`) were **correctly rejected with `BLOCKED_GATE_LOCKED`**.
- The failure was strictly an **environmental test artifact isolation defect**, not a data leak, unauthorized download, or security bypass.
