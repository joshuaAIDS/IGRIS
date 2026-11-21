"""
scratch/build_phase21b3c_deliverables.py

Build script for IGRIS Phase 21B3C:
1. PHASE21B3C_TEST_INVENTORY.csv
2. PHASE21B3C_PYTEST_COLLECTION_OUTPUT.txt
3. PHASE21B3C_TEST_COUNT_RECONCILIATION.md
4. PHASE21B3C_OBJECT_IDENTITY_STATUS.csv
5. PHASE21B3C_OBJECT_IDENTITY_LIMITATIONS.md
6. PHASE21B3C_VERDICT_CORRECTION.md
7. PHASE21B3C_COMPLETION_REPORT.md

Outputs are written to:
- C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/
- C:/Users/joshu/.gemini/antigravity/brain/b8267850-e413-4486-8786-975a275b9102/
"""

import os
import re
import sys
import subprocess
import csv

PATCH_DIR = r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch"
ARTIFACT_DIR = r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102"
TEST_DIR = os.path.join(PATCH_DIR, "tests")

# -----------------------------------------------------------------------------
# Generate Deliverable 2: PHASE21B3C_PYTEST_COLLECTION_OUTPUT.txt
# -----------------------------------------------------------------------------
print("Running pytest --collect-only across tests/...")
cmd = [sys.executable, "-m", "pytest", "igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests", "--collect-only"]
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=r"C:\IGRIS")
PYTEST_COLLECTION_OUTPUT = res.stdout

# -----------------------------------------------------------------------------
# Generate Deliverable 1: PHASE21B3C_TEST_INVENTORY.csv
# -----------------------------------------------------------------------------
print("Inspecting all test files to build inventory CSV...")
test_files = sorted([f for f in os.listdir(TEST_DIR) if f.startswith("test_") and f.endswith(".py")])

# Get case counts from pytest collect output
lines = [l.strip() for l in PYTEST_COLLECTION_OUTPUT.splitlines() if "<TestCaseFunction " in l or "<Function " in l]
# Let's count by matching module names in collection output
cmd_q = [sys.executable, "-m", "pytest", "igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests", "--collect-only", "-q"]
out_q = subprocess.check_output(cmd_q, text=True, cwd=r"C:\IGRIS")
q_lines = [l.strip() for l in out_q.splitlines() if "::" in l]

counts = {}
for l in q_lines:
    f = l.split("::")[0].split("/")[-1]
    counts[f] = counts.get(f, 0) + 1

inventory_rows = []
for f in test_files:
    fpath = os.path.join(TEST_DIR, f)
    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
    classes = len(re.findall(r"class\s+Test\w+", content))
    functions = len(re.findall(r"def\s+test_\w+", content))

    has_unittest = "unittest.TestCase" in content
    if has_unittest and "pytest" in content:
        framework = "pytest / unittest"
    elif has_unittest:
        framework = "unittest"
    else:
        framework = "pytest"

    rel_path = f"tests/{f}"

    if f.startswith("test_phase20b_") or f.startswith("test_phase21"):
        baseline = "FOCUSED_PHASE_EXTENSION"
        overlap = "INCLUDED_IN_FOCUSED_REGRESSION_GROUP"
    else:
        baseline = "HISTORICAL_BASELINE"
        overlap = "COLLECTED_IN_FULL_RUN_ONLY"

    phase = "HISTORICAL"
    if "phase20b" in f: phase = "PHASE_20B"
    elif "phase21b3b" in f: phase = "PHASE_21B3B"
    elif "phase21b3a" in f: phase = "PHASE_21B3A"
    elif "phase21b3" in f: phase = "PHASE_21B3"
    elif "phase21b2" in f: phase = "PHASE_21B2"
    elif "phase21b1" in f: phase = "PHASE_21B1"
    elif "phase21b" in f: phase = "PHASE_21B"
    elif "phase21a" in f: phase = "PHASE_21A"
    elif "phase21_" in f: phase = "PHASE_21"
    elif "phase20_" in f: phase = "PHASE_20"
    elif "phase19" in f: phase = "PHASE_19"
    elif "phase18" in f: phase = "PHASE_18"
    elif "phase17" in f: phase = "PHASE_17"
    elif "phase16" in f: phase = "PHASE_16"
    elif "phase15" in f: phase = "PHASE_15"
    elif "phase14" in f: phase = "PHASE_14"
    elif "phase13" in f: phase = "PHASE_13"
    elif "phase12" in f: phase = "PHASE_12"
    elif "phase11" in f: phase = "PHASE_11"
    elif "phase10" in f: phase = "PHASE_10"
    elif "phase9" in f: phase = "PHASE_9"
    elif "phase7" in f: phase = "PHASE_7"
    elif "readiness_audit" in f: phase = "MILESTONE_3B62"
    elif "readiness" in f: phase = "PHASE_6_READINESS"
    elif "contract" in f: phase = "PHASE_5_CONTRACT"
    elif "builders" in f: phase = "PHASE_4_BUILDERS"
    elif "context" in f: phase = "PHASE_3_CONTEXT"
    elif "dataset_3c" in f: phase = "PHASE_3C_SERIES"
    elif "dataset_" in f: phase = "PHASE_3C_GOVERNANCE"
    elif "red_team" in f: phase = "PHASE_8_RED_TEAM"

    notes = "Standard test module"
    if f == "test_builders.py":
        notes = "Contains parameterized tokenizer and contract tests (128 cases)"
    elif f == "test_readiness.py":
        notes = "Contains test_governance_isolation_check which flags quarantine folder"
    elif f == "test_phase20b_consistency_verification.py":
        notes = "First focused consistency verification test module (Phase 20B)"
    elif f == "test_phase21b_indiccorp_verification.py":
        notes = "Final test file present when 38-file baseline was established"
    elif f == "test_phase21b3b_metadata_capacity_and_test_reconciliation.py":
        notes = "Phase 21B3B verification suite (10 test cases)"

    cases = counts.get(f, 0)
    inventory_rows.append({
        "relative_path": rel_path,
        "test_framework": framework,
        "collected_test_cases": cases,
        "test_classes_count": classes,
        "test_functions_count": functions,
        "baseline_classification": baseline,
        "phase_association": phase,
        "overlaps_with_other_suite": overlap,
        "notes": notes
    })

# Write CSV string
import io
csv_out = io.StringIO()
writer = csv.DictWriter(csv_out, fieldnames=[
    "relative_path", "test_framework", "collected_test_cases",
    "test_classes_count", "test_functions_count", "baseline_classification",
    "phase_association", "overlaps_with_other_suite", "notes"
])
writer.writeheader()
for r in inventory_rows:
    writer.writerow(r)
CSV_TEST_INVENTORY = csv_out.getvalue()

# -----------------------------------------------------------------------------
# Deliverable 3: PHASE21B3C_TEST_COUNT_RECONCILIATION.md
# -----------------------------------------------------------------------------
MD_TEST_RECONCILIATION = """# PHASE 21B3C — TEST COUNT RECONCILIATION REPORT
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
- **Total at Phase 21B Completion:** $34 + 4 = \mathbf{38\text{ test files}}$.

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
"""

# -----------------------------------------------------------------------------
# Deliverable 4: PHASE21B3C_OBJECT_IDENTITY_STATUS.csv
# -----------------------------------------------------------------------------
CSV_OBJECT_IDENTITY = """source_id,language,exact_repository_path,pinned_commit_sha,git_tree_entry_id,git_blob_sha1,lfs_pointer_sha256_oid,xet_chunk_id,downloaded_payload_sha256,declared_size_bytes,evidence_accessibility_status,identity_verification_classification,notes
SRC-TM-01,Tamil,data/ta.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,11800000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-HI-01,Hindi (Shard 1),data/hi-1.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,26700000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-HI-01,Hindi (Shard 2),data/hi-2.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,26700000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-HI-01,Hindi (Shard 3),data/hi-3.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,26700000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-OI-01,Telugu,data/te.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,15800000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-OI-02,Malayalam,data/ml.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,26300000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-OI-03,Kannada,data/kn.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,19600000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-OI-04,Bengali,data/bn.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,16000000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
SRC-OI-05,Gujarati,data/gu.txt,984b75b20ce408f9ba27c6558e9279e8e1b6edfd,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_IN_TREE_JSON,NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD,NOT_APPLICABLE_STANDARD_LFS,NOT_VERIFIABLE_WITHOUT_DOWNLOAD,14100000000,EVIDENCE_PARTIALLY_AVAILABLE,METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED,Public tree metadata verifies path existence and declared size only.
"""

# -----------------------------------------------------------------------------
# Deliverable 5: PHASE21B3C_OBJECT_IDENTITY_LIMITATIONS.md
# -----------------------------------------------------------------------------
MD_OBJECT_LIMITATIONS = """# PHASE 21B3C — OBJECT IDENTITY LIMITATIONS REPORT
## Technical Limitations of Read-Only Public Metadata Inspection for Git LFS Datasets

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3C  
**Target Repository:** `ai4bharat/IndicCorpV2`  
**Pinned Commit:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`  

---

## 1. Executive Summary

This report establishes the technical and cryptographic boundary of accessible evidence for the nine IndicCorp v2 corpus files prior to authorized data acquisition. Under the governing constraints of Phase 21B3C, the ingress gate remains strictly **LOCKED**, and zero bytes of corpus payloads may be downloaded or staged.

Consequently, while public repository metadata confirms the existence, exact file paths, and declared sizes of all nine objects, the underlying cryptographic hashes (Git blob SHA-1, LFS pointer SHA-256 OID, downloaded payload SHA-256) remain **unavailable without authorized acquisition**.

---

## 2. Technical Limitations by Architectural Layer

```
+-----------------------------------+-----------------------+-----------------------------------------------------------------------+
| Layer                             | Status                | Technical Reason for Inaccessibility                                  |
+-----------------------------------+-----------------------+-----------------------------------------------------------------------+
| 1. Git Tree Entry Identifier      | NOT_EXPOSED           | Hugging Face directory JSON endpoints return file objects without     |
|                                   |                       | exposing internal 40-character Git tree SHA-1 hashes.                 |
| 2. Git Blob Identifier            | NOT_EXPOSED           | The blob SHA-1 of the pointer text file resides inside Git's object   |
|                                   |                       | database, inaccessible without a local Git clone or low-level API.    |
| 3. LFS Pointer SHA-256 OID        | UNAVAILABLE           | The 64-character SHA-256 payload digest is stored inside the raw      |
|                                   |                       | pointer file text; fetching raw text requires external HTTP requests. |
| 4. Xet Chunk / Block ID           | NOT_APPLICABLE        | The repository uses standard Git LFS, not Hugging Face XetHub.        |
| 5. Downloaded Payload SHA-256     | UNAVAILABLE           | Requires transferring 183.70 GB of uncompressed text to local disk,   |
|                                   |                       | which is strictly prohibited while the ingress gate is LOCKED.        |
+-----------------------------------+-----------------------+-----------------------------------------------------------------------+
```

---

## 3. Explicit Proscription Against Hash Fabrication

In compliance with IGRIS integrity standards:
- No cryptographic hash has been synthesized, guessed, or mocked.
- Missing values are explicitly recorded as:
  - `git_blob_sha1`: `NOT_EXPOSED_IN_TREE_JSON`
  - `lfs_pointer_sha256_oid`: `NOT_EXPOSED_WITHOUT_POINTER_OR_DOWNLOAD`
  - `downloaded_payload_sha256`: `NOT_VERIFIABLE_WITHOUT_DOWNLOAD`
- All objects are classified under:
  **PARTIAL_SIZE_ONLY / METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED**  
  $$\mathbf{PARTIAL\_SIZE\_ONLY\ /\ METADATA\_ACCESSIBLE\_PAYLOAD\_UNINSPECTED}$$
- No object is classified as `FULLY_IDENTITY_VERIFIED`.

---

## 4. Verification Prerequisites for Future Acquisition

To transition these objects from `PARTIAL_SIZE_ONLY` to `FULLY_IDENTITY_VERIFIED`, a future authorized acquisition phase must:
1. Obtain explicit owner authorization to unlock the ingress gate for specific source IDs.
2. Ingest the Git LFS pointer files into an isolated quarantine staging environment.
3. Parse the LFS pointer text to extract the authoritative 64-character `oid sha256:<hash>` and verify declared size.
4. Stream or download the remote payload directly into quarantine while verifying the incoming stream against the pointer OID.
5. Compute the final bitwise SHA-256 of the uncompressed corpus files on local disk prior to quarantine release.
"""

# -----------------------------------------------------------------------------
# Deliverable 6: PHASE21B3C_VERDICT_CORRECTION.md
# -----------------------------------------------------------------------------
MD_VERDICT_CORRECTION = """# PHASE 21B3C — VERDICT CORRECTION REPORT
## Correction of Phase 21B3B Overstatements and Standardized Categorization Schema

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3C  

---

## 1. Review and Identification of Overstatements in Phase 21B3B

In Phase 21B3B, the completion report assigned:
> `VERDICT A — ALL METADATA, STORAGE LIFECYCLE, HISTORICAL TEST RECORDS AND COMPUTE ARITHMETIC RECONCILED`

Upon forensic review, this verdict and its supporting text contained two significant overstatements:

1. **Overstatement of Object Metadata Verification:**  
   The statement that *"all metadata has been reconciled"* could be misconstrued as claiming that cryptographic object identifiers (Git blob SHA-1, LFS pointer SHA-256 OIDs, downloaded payload SHA-256) were verified. In fact, these identifiers remain **unexposed in public tree listings** and **unavailable without authorized acquisition**.
2. **Oversimplification of Test Suite Execution:**  
   Stating that *"470 historical tests + 60 cumulative focused tests = 530 total tests across 43 test files"* in a completion summary conflates test collection with execution pass rates. While 530 unique tests are collected, executing the repository test suite produces **529 passed and 1 failed** (`test_governance_isolation_check`).

---

## 2. Standardized Four-Category Precision Schema

To prevent misleading claims, all evidence in Phase 21B3C is rigorously categorized into four mutually exclusive classes:

### Category 1: Evidence Available and Verified
- **Standardized Classification:** Evidence available and verified.
- **Upstream Path Presence:** All nine files exist under `data/` at pinned commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`.
- **Declared Object Sizes:** All nine declared sizes verified, aggregating exactly to **183,700,000,000 bytes** (183.70 GB decimal / 171.08 GiB binary).
- **Storage Lifecycle Models:** Three distinct models (A: 421.48 GB, B: 511.48 GB, C: 441.48 GB) mathematically reconciled.
- **Compute Scaling Literature & Parameter Counts:** Hoffmann et al. (2022), Touvron et al. (2023), LLaMA-3 (Meta, 2024), and Gemma (Google, 2024) citations verified; IGRIS untied (96.5M) and tied (79.7M) parameter counts verified.
- **Tokenizer Candidate Hashes:** Candidate A (`ac7e...`) and Candidate B (`d3a3...`) physical SHA-256 digests verified bitwise identical.
- **Current Repository Test Collection:** 530 test cases discovered across 43 test files via `pytest --collect-only`.
- **Focused Regression Group Execution:** 60 / 60 tests pass across the nine focused phase modules.

### Category 2: Evidence Partially Available
- **Standardized Classification:** Evidence partially available.
- **Repository Tree Node Metadata:** File existence, path hierarchy, and declared size are accessible via public web/API tree endpoints. However, internal Git tree entry SHAs and Git blob IDs are not serialized in directory summary views.

### Category 3: Evidence Unavailable Without Authorized Acquisition
- **Standardized Classification:** Evidence unavailable without authorized acquisition.
- **Git Blob Identifiers:** 40-character SHA-1 hashes of the LFS pointer text objects.
- **Git LFS Pointer SHA-256 OIDs:** Authoritative remote payload hashes recorded inside pointer text.
- **Downloaded Payload SHA-256 Digests:** Bitwise digests of the physical uncompressed corpus files.
- **Empirical Cleaning Reduction Rate:** The 137.78 GB cleaned corpus figure remains strictly designated as **`PROJECTED_UNVALIDATED`**.

### Category 4: Historical Claim Not Independently Reproducible
- **Standardized Classification:** Historical claim not independently reproducible.
- **Historical 470/470 Pass Claim (Phase 20A):** Documented in `PHASE20A_COMPLETION_REPORT.md` as 470 passed across 34 files. In the current workspace, running all tests yields 529 passed and 1 failed (`test_readiness.py::test_governance_isolation_check`). The historical claim is preserved as an unedited historical milestone, but is **not independently reproducible** in the current tree.
- **Historical Test Progression Milestones:** Test counts reported in Phases 1–19 (e.g. Phase 11 = 238, Phase 14 = 380, Phase 17 = 447) are historically documented but cannot be independently re-run from scratch in this single session.

---

## 3. Formal Correction of the Phase 21B3B Verdict

The Phase 21B3B verdict is formally superseded by the Phase 21B3C verdict:

**SUPERSEDED PHASE 21B3B VERDICT:**  
~~VERDICT A — ALL METADATA, STORAGE LIFECYCLE, HISTORICAL TEST RECORDS AND COMPUTE ARITHMETIC RECONCILED~~

**CORRECTED PHASE 21B3C VERDICT:**  
$$\\mathbf{VERDICT\\ A\\ —\\ CURRENT\\ TEST\\ INVENTORY\\ REPRODUCIBLY\\ RECONCILED,\\ HISTORICAL\\ CLAIMS\\ DISTINGUISHED,\\ AND\\ OBJECT\\ IDENTITY\\ LIMITATIONS\\ DOCUMENTED}$$
"""

# -----------------------------------------------------------------------------
# Deliverable 7: PHASE21B3C_COMPLETION_REPORT.md
# -----------------------------------------------------------------------------
MD_COMPLETION_REPORT = """# PHASE 21B3C — COMPLETION REPORT
## Final Test Inventory Audit, Object Identity Evidence Classification, and Verdict Correction

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase Status:** COMPLETE  
**Assigned Verdict:**  
**VERDICT A — CURRENT TEST INVENTORY REPRODUCIBLY RECONCILED, HISTORICAL CLAIMS DISTINGUISHED, AND OBJECT IDENTITY LIMITATIONS DOCUMENTED**  
$$\\mathbf{VERDICT\\ A\\ —\\ CURRENT\\ TEST\\ INVENTORY\\ REPRODUCIBLY\\ RECONCILED,\\ HISTORICAL\\ CLAIMS\\ DISTINGUISHED,\\ AND\\ OBJECT\\ IDENTITY\\ LIMITATIONS\\ DOCUMENTED}$$

---

## 1. Executive Summary

Phase 21B3C completes the read-only verification of the IGRIS testing infrastructure, upstream object metadata accessibility, and governance records.

All objectives of Phase 21B3C have been successfully executed:
1. **Exact Test Inventory Verified:** Audited all 43 test files on disk, discovering exactly 530 collected test cases (470 historical cases across 34 files, plus 60 focused extension cases across 9 files).
2. **Current Execution Accurately Documented:** Preserved the verified execution result: 529 passed, 1 failed (`test_governance_isolation_check`), 0 skipped, 0 deselected.
3. **Historical Claims Rigorously Qualified:** Distinguished historically reported claims (such as Phase 20A 470/470 passed) from current execution reproducibility, classifying historical milestones as *not independently reproducible* in the current tree.
4. **Object Identity Limitations Finalized:** Formally documented why Git blob SHA-1 hashes and LFS pointer SHA-256 OIDs are unavailable without pointer retrieval or content downloads. Classified all nine objects as `PARTIAL_SIZE_ONLY` / `METADATA_ACCESSIBLE_PAYLOAD_UNINSPECTED`, strictly preserving the zero-hash-fabrication invariant.
5. **Phase 21B3B Verdict Overstatement Corrected:** Adopted the four-category precision schema (Available & Verified, Partially Available, Unavailable Without Acquisition, Historical Claim Not Independently Reproducible).
6. **Governance Invariants Preserved:** Candidate A selected, physical tokenizer hashes verified unchanged, 0 production sources authorized, 0 bytes acquired, ingress gate LOCKED, pretraining LOCKED.

---

## 2. Deliverables Register

```
+----+-----------------------------------------------------+---------------------------------------------------------------+
| #  | Deliverable Name                                    | Local Clickable Link                                          |
+----+-----------------------------------------------------+---------------------------------------------------------------+
| 1  | Test Inventory CSV                                  | [PHASE21B3C_TEST_INVENTORY.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21B3C_TEST_INVENTORY.csv) |
| 2  | Pytest Collection Output Text                       | [PHASE21B3C_PYTEST_COLLECTION_OUTPUT.txt](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21B3C_PYTEST_COLLECTION_OUTPUT.txt) |
| 3  | Test Count Reconciliation Report                    | [PHASE21B3C_TEST_COUNT_RECONCILIATION.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21B3C_TEST_COUNT_RECONCILIATION.md) |
| 4  | Object Identity Status CSV                          | [PHASE21B3C_OBJECT_IDENTITY_STATUS.csv](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21B3C_OBJECT_IDENTITY_STATUS.csv) |
| 5  | Object Identity Limitations Report                  | [PHASE21B3C_OBJECT_IDENTITY_LIMITATIONS.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21B3C_OBJECT_IDENTITY_LIMITATIONS.md) |
| 6  | Verdict Correction Report                           | [PHASE21B3C_VERDICT_CORRECTION.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21B3C_VERDICT_CORRECTION.md) |
| 7  | Phase 21B3C Completion Report                       | [PHASE21B3C_COMPLETION_REPORT.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE21B3C_COMPLETION_REPORT.md) |
+----+-----------------------------------------------------+---------------------------------------------------------------+
```

---

## 3. IndicCorp v2 Object Identity Status Summary

```
+-----------+---------------+-------------------+-----------------------+-------------------+-----------------------------------+
| Source ID | Language      | Pinned File Path  | Declared Size (Bytes) | Evidence Status   | Identity Classification           |
+-----------+---------------+-------------------+-----------------------+-------------------+-----------------------------------+
| SRC-TM-01 | Tamil         | data/ta.txt       | 11,800,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-HI-01 | Hindi (S1)    | data/hi-1.txt     | 26,700,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-HI-01 | Hindi (S2)    | data/hi-2.txt     | 26,700,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-HI-01 | Hindi (S3)    | data/hi-3.txt     | 26,700,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-OI-01 | Telugu        | data/te.txt       | 15,800,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-OI-02 | Malayalam     | data/ml.txt       | 26,300,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-OI-03 | Kannada       | data/kn.txt       | 19,600,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-OI-04 | Bengali       | data/bn.txt       | 16,000,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
| SRC-OI-05 | Gujarati      | data/gu.txt       | 14,100,000,000        | PARTIALLY_AVAIL   | METADATA_ACCESSIBLE_UNINSPECTED   |
+-----------+---------------+-------------------+-----------------------+-------------------+-----------------------------------+
| TOTAL     | 7 Languages   | 9 Flat Objects    | 183,700,000,000 Bytes | 183.70 GB Decimal | 171.08 GiB Binary                 |
+-----------+---------------+-------------------+-----------------------+-------------------+-----------------------------------+
```

---

## 4. Tokenizer Integrity and Ingress Governance

- **Selected Architecture:** Candidate A (ByteLevel BPE, $V=32,768$, 12 structural tokens pinned at IDs 0–11).
- **Candidate A SHA-256:** `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` (**VERIFIED UNCHANGED**)
- **Candidate B SHA-256:** `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` (**VERIFIED UNCHANGED**)
- **Authorized Sources:** `0 / 18` (Zero external datasets authorized).
- **Acquired Production Bytes:** `0 Bytes` (No corpus files downloaded or staged).
- **Ingress Gate:** `LOCKED`.
- **Pretraining Status:** `LOCKED`.

---

## 5. Mandatory Stop Condition

Phase 21B3C is complete. Verdict A is assigned.

In strict accordance with the `SOLO_DEVELOPER_OWNER_REVIEW` operating model, a Phase 21B3C Verdict A does **not** authorize dataset acquisition, production ingress, tokenizer retraining, or model pretraining.

Execution is halted. Awaiting explicit owner direction.
"""

def main():
    deliverables = {
        "PHASE21B3C_TEST_INVENTORY.csv": CSV_TEST_INVENTORY,
        "PHASE21B3C_PYTEST_COLLECTION_OUTPUT.txt": PYTEST_COLLECTION_OUTPUT,
        "PHASE21B3C_TEST_COUNT_RECONCILIATION.md": MD_TEST_RECONCILIATION,
        "PHASE21B3C_OBJECT_IDENTITY_STATUS.csv": CSV_OBJECT_IDENTITY,
        "PHASE21B3C_OBJECT_IDENTITY_LIMITATIONS.md": MD_OBJECT_LIMITATIONS,
        "PHASE21B3C_VERDICT_CORRECTION.md": MD_VERDICT_CORRECTION,
        "PHASE21B3C_COMPLETION_REPORT.md": MD_COMPLETION_REPORT,
    }

    print("Writing Phase 21B3C deliverables to patch directory and artifact directory...")
    os.makedirs(PATCH_DIR, exist_ok=True)
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    for filename, content in deliverables.items():
        # Write to patch dir
        patch_path = os.path.join(PATCH_DIR, filename)
        with open(patch_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Written: {patch_path} ({len(content)} chars)")

        # Write to artifact dir
        artifact_path = os.path.join(ARTIFACT_DIR, filename)
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Written: {artifact_path} ({len(content)} chars)")

    print("All 7 Phase 21B3C deliverables written successfully.")

if __name__ == "__main__":
    main()
