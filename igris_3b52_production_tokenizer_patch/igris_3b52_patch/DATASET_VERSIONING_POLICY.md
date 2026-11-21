# IGRIS Dataset Versioning Policy

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3B.60 — Dataset Authorization & Inventory Preparation  
**Document ID**: `IGRIS-POL-VER-2026-V1`  
**Status**: APPROVED  
**Applies To**: Multilingual Evaluation Suites & Tokenizer Benchmarks  

---

## 1. Principles of Dataset Versioning

Scientific comparability and reproducible tokenizer evaluation require that datasets remain strictly deterministic across evaluation runs. Once a dataset version is registered, audited, and authorized:

1. **Strict Immutability**: No file belonging to a released version may ever be modified, overwritten, appended, or truncated in place.
2. **Deterministic Identifiers**: Every evaluation benchmark report must explicitly record the exact dataset ID, version number, and manifest SHA-256 hash.
3. **Traceability of Evolution**: Every revision must document what changed, why it changed, who requested it, and who approved it.

---

## 2. Semantic Versioning Specification (`vMAJOR.MINOR.PATCH`)

Dataset version numbers follow the semantic format:
$$\text{Version} = \text{v}\langle\text{MAJOR}\rangle.\langle\text{MINOR}\rangle.\langle\text{PATCH}\rangle$$

### 2.1 Major Version Increment (`v(X+1).0.0`)
A Major increment indicates **breaking benchmark changes**. Previous benchmark scores and baseline measurements are **not directly comparable** with the new version.

Triggers for Major version increment:
- Replacement or overhaul of >5% of the underlying sample text.
- Re-stratification of length tiers (e.g., changing context distribution between 512, 1024, 2048 tokens).
- Category re-allocations (e.g., splitting a general category into distinct language partitions).
- Fundamental changes in formatting, schema, or structural token delimiters.
- Deprecation or complete purging of a core benchmark domain.

*Governance Requirement*: Requires full re-authorization with all four sign-off roles (Custodian, Legal, Security, Architect).

---

### 2.2 Minor Version Increment (`vX.(Y+1).0`)
A Minor increment indicates **additive or non-breaking refinements**. The overall category distribution and comparative integrity are preserved.

Triggers for Minor version increment:
- Inclusion of additional non-breaking validation samples within existing categories.
- Removal of newly discovered anomalous strings or accidental duplicates (<1% of total volume).
- Decontamination corrections (e.g., pruning newly identified leakage against an updated pre-training split).
- Normalization corrections (e.g., converting legacy escaped sequences to standard NFC text).

*Governance Requirement*: Requires Custodian, Security, and Architect approvals.

---

### 2.3 Patch Version Increment (`vX.Y.(Z+1)`)
A Patch increment represents **purely metadata, packaging, or documentation fixes** without altering the underlying content tokens or text bytes.

Triggers for Patch version increment:
- Corrections to dataset inventory metadata (e.g., license link correction, custodian contact update).
- Formatting fixes in documentation or markdown headers.
- Re-packaging of identical data files into revised directory hierarchies with updated manifest checksums.
- Typographical corrections in test harness fixtures referencing the dataset.

*Governance Requirement*: Requires Custodian sign-off and automated cryptographic verification.

---

## 3. Directory Layout and File Naming Conventions

All datasets must reside in standardized, self-describing directory trees:

```
datasets/
└── evaluation/
    └── <category_slug>/
        └── <dataset_id>/
            └── v<MAJOR>.<MINOR>.<PATCH>/
                ├── manifest.json
                ├── authorization.md
                ├── data.jsonl
                └── README.md
```

### Examples:
- `datasets/evaluation/tamil/DS-SYNTH-TM-001/v1.0.0/manifest.json`
- `datasets/evaluation/technical_documentation/DS-SYNTH-EN-002/v1.1.0/data.jsonl`

File naming must use lowercase alphanumeric characters with underscores (`_`) or hyphens (`-`). Spaces and special characters are prohibited.

---

## 4. Immutability Enforcement Workflow

To prevent accidental drift or silent corruption:

1. **Filesystem Write Protection**:
   - Immediately following manifest stamping, the entire directory is set to read-only (`chmod -R 0555` / `attrib +R /S /D`).
2. **Checksum Verification**:
   - Every execution run verifies the SHA-256 hash of each file against `manifest.json`.
   - If any file hash does not match, the authorization gate halts execution immediately with `DatasetAccessDeniedError`.
3. **No In-Place Edits**:
   - Attempting to overwrite an existing version directory is a policy violation. Any new build must target a new version folder (`v1.0.1` or `v1.1.0`).

---

## 5. Deprecation and Sunsetting Policy

When a dataset version is superseded or retired:

1. **Deprecation Notice**:
   - The dataset record status in `DATASET_INVENTORY.csv` is updated to `DEPRECATED`.
   - The authorization record is updated with an end-of-life timestamp.
   - Evaluations using deprecated datasets will emit prominent warning logs.
2. **Archival & Quarantine**:
   - When retired, the dataset directory is moved to `datasets/archive/` and marked `LOCKED`.
   - No production evaluations or training runs may bind to an archived or locked dataset.
3. **Revocation**:
   - If a security or licensing defect is discovered, status transitions immediately to `REVOKED`. Access gates reject revoked datasets with immediate fatal exceptions.
