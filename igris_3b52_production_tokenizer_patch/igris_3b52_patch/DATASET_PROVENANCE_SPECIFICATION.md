# IGRIS Dataset Provenance Specification

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3B.60 — Dataset Authorization & Inventory Preparation  
**Document ID**: `IGRIS-SPEC-PROV-2026-V1`  
**Status**: APPROVED  
**Applies To**: All Multilingual Evaluation and Training Datasets  

---

## 1. Overview and Core Philosophy

In the IGRIS tokenizer and language model development lifecycle, **data provenance** is treated as a first-class security and quality discipline. Every dataset incorporated into the project must possess an unbroken, cryptographically verifiable chain of custody from origin acquisition through staging, cleaning, sanitization, and immutable packaging.

No evaluation run or tokenizer analysis may proceed on datasets whose provenance cannot be verified against an approved authorization record.

---

## 2. Five-Stage Provenance Lifecycle Chain

The lifecycle of any dataset entering the IGRIS evaluation or training pipeline comprises five non-skippable stages:

```
[ Stage 1: Origin Acquisition ]
         │
         ▼
[ Stage 2: Content Extraction & Lossless Normalization ]
         │
         ▼
[ Stage 3: PII Screening & Decontamination ]
         │
         ▼
[ Stage 4: Duplicate & Near-Duplicate Filtering ]
         │
         ▼
[ Stage 5: Immutable Packaging & Manifest Stamping ]
```

### Stage 1: Origin Acquisition & Ingestion Isolation
1. **Source Registry**: Every corpus source must be logged in the global source registry with its origin URL, repository, archival snapshot ID, or synthetic generator seed configuration.
2. **Quarantine Staging**: Raw ingress data is placed into an isolated quarantine zone (`quarantine/staging/`). Direct execution engines and training pipelines have zero read access to the quarantine zone.
3. **MIME & Container Validation**: Incoming files are validated against allowed formats (`application/x-ndjson`, `text/plain`, `text/csv`). Archive files (`.zip`, `.tar.gz`) are strictly inspected and scanned in sandbox environments before extraction.

### Stage 2: Content Extraction & Lossless Normalization
1. **Character Encoding**:
   - Every file must be strictly encoded as **UTF-8**.
   - Byte Order Marks (BOM, `U+FEFF`) must be stripped at the file boundary.
   - Non-UTF-8 bytes or invalid UTF-8 byte sequences cause immediate stage rejection.
2. **Unicode Normalization**:
   - Normalization Form C (**NFC**) is the mandatory standard across all text.
   - Decomposed sequences (NFD), compatibility decompositions (NFKD), or compatibility compositions (NFKC) are normalized to NFC.
   - Conformance to **Unicode Standard Version 15.1.0** is enforced.
3. **Surrogate & Control Character Isolation**:
   - Lone surrogate code points (`U+D800` through `U+DFFF`) are strictly prohibited and must be rejected or removed.
   - Bi-directional formatting overrides (`U+202A`–`U+202E`, `U+2066`–`U+2069`) and zero-width stealth overrides are stripped unless explicitly certified for bidirectional test fixtures.
   - Whitespace (including spaces, newlines `\n`, tabs `\t`) must be preserved losslessly without aggressive truncation or synthetic collapse.

### Stage 3: PII Screening & Sensitive Data Sanitization
1. **Automated Regular Expression Screening**:
   - Email addresses (`[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+`)
   - International & Domestic Phone Numbers (E.164, Indian 10-digit mobile `[6-9]\d{9}`, US formats)
   - Government Identifiers (Aadhaar 12-digit patterns, PAN card alphanumeric `[A-Z]{5}[0-9]{4}[A-Z]`, US SSN)
   - Payment Card Numbers (Luhn-compliant 13–19 digit patterns)
   - Cryptographic Secrets, API Keys, Private Keys (`BEGIN PRIVATE KEY`, AWS/GCP/Bearer token patterns)
2. **Contextual & Named Entity Scrubbing**:
   - High-confidence personal names associated with sensitive attributes.
   - Addresses and physical geo-locations linked to identifiable private individuals.
3. **Quarantine Action**:
   - If PII is detected, the entire sample block is segregated into `quarantine/pii_flagged/`.
   - The dataset status transitions to `FLAGGED` or `QUARANTINED` pending human review.

### Stage 4: Duplicate & Near-Duplicate Filtering
1. **Exact Duplicate Removal**:
   - SHA-256 fingerprinting of normalized lines or JSONL text records.
   - Exact duplicates within the dataset are identified and deduplicated, recording the drop percentage.
2. **MinHash LSH Near-Duplicate Detection**:
   - 5-gram word or character shingling.
   - MinHash signature generation (minimum 128 hash permutations).
   - Locality-Sensitive Hashing (LSH) with Jaccard similarity threshold $J \ge 0.85$.
   - Near-duplicates are clustered, preserving the representative canonical sample.
3. **Train/Eval Contamination Screening**:
   - 13-gram exact matching against training corpora to prevent benchmark leakage.
   - Overlap must remain strictly $0.0\%$ for approved evaluation splits.

### Stage 5: Immutable Packaging & Manifest Stamping
1. **File System Immutability**:
   - Output datasets are written to versioned directories (`eval_corpus_<dataset_id>_v<version>/`).
   - Permissions are locked to read-only (`chmod 0444` / Windows read-only attribute).
2. **Cryptographic Manifest Generation**:
   - A deterministic manifest (`manifest.json`) is generated by computing:
     - Exact byte size (`byte_size`)
     - Total line count (`line_count`)
     - Total character count (`character_count`)
     - SHA-256 checksum (`sha256`) for every packaged data file.
   - The root SHA-256 checksum of the manifest file itself is calculated and recorded into the Dataset Authorization Record.

---

## 3. Cryptographic Manifest Workflow

The SHA-256 manifest serves as the unforgeable contract between the physical file system and the authorization state.

### Manifest Schema (`manifest.json`)
```json
{
  "manifest_version": "1.0.0",
  "dataset_id": "DS-SYNTH-TM-001",
  "generated_at": "2026-11-17T09:00:00Z",
  "generator_tool": "scripts/dataset_inventory.py::generate_manifest",
  "root_directory": "synthetic/eval/tamil",
  "files": [
    {
      "relative_path": "sample_news.jsonl",
      "format": "jsonl",
      "encoding": "UTF-8",
      "byte_size": 210450,
      "line_count": 500,
      "character_count": 75240,
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ],
  "total_files": 1,
  "total_bytes": 210450,
  "total_lines": 500,
  "total_characters": 75240,
  "manifest_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a"
}
```

### Determinism Rules
- File entries must be sorted lexicographically by `relative_path` in ascending POSIX order.
- Keys within JSON objects must be sorted.
- JSON output must use standard 2-space indentation with a trailing newline.
- The `manifest_sha256` is the SHA-256 hash of the entire JSON string excluding the `manifest_sha256` key itself.

---

## 4. Audit Trail and Chain of Custody Logging

Each provenance transition emits an append-only JSONL event into the dataset audit log:

```json
{
  "event_id": "EVT-20261117-0901-001",
  "dataset_id": "DS-SYNTH-TM-001",
  "timestamp": "2026-11-17T09:01:00Z",
  "stage": "STAGE_5_IMMUTABLE_PACKAGING",
  "operator": "custodian_tamil@igris.internal",
  "action": "MANIFEST_STAMPED",
  "target_manifest_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
  "result": "SUCCESS"
}
```

Any modification to packaged files breaks the manifest hash check, invalidating all associated authorization records and triggering immediate execution termination.
