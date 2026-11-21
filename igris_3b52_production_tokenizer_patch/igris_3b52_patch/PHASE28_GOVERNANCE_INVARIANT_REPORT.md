# PHASE 28 — GOVERNANCE INVARIANT REPORT

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-20  
**Phase:** Phase 28

---

## 1. Executive Invariant Declaration

Throughout Phase 28, all immutable project governance constraints were continuously monitored, cryptographically verified, and strictly enforced.

Zero bytes of production data were downloaded, zero cloud resources were provisioned, and zero funds were expended.

```
+-------------------------------------------------------------------------+
|                  IGRIS GOVERNANCE CONTROL GATES (PHASE 28)              |
+-------------------------------------------------------------------------+
|  Production Dataset Downloads:      NOT AUTHORIZED                      |
|  Production Ingress Gate:           LOCKED                              |
|  Dataset Quarantine Ingress:        LOCKED                              |
|  Source-Specific Acquisition Grants: NONE                               |
|  Tokenizer Training Gate:          UNAUTHORIZED                        |
|  Model Pretraining Gate:           LOCKED                              |
|  Cloud Infrastructure Provisioning: NOT AUTHORIZED                      |
|  Cloud Infrastructure Spending:     $0.00                               |
|  Active Disk Ingress Bytes:         0 bytes                             |
+-------------------------------------------------------------------------+
```

---

## 2. Tokenizer Cryptographic & Architectural Invariants

Both tokenizer candidates were verified on disk prior to Phase 28 execution:

```
+------------------------------------+----------------------------------------------------------+
| Architectural Property             | Verified Value & Cryptographic SHA-256 Hash              |
+------------------------------------+----------------------------------------------------------+
| Selected Candidate                 | Candidate A (ByteLevel BPE, Hugging Face Tokenizers)     |
| Candidate A Artifact Path          | artifacts/tokenizer/candidate_a/tokenizer.json           |
| Candidate A SHA-256 Hash           | ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab... |
| Candidate B Artifact Path          | artifacts/tokenizer/candidate_b/tokenizer.model          |
| Candidate B SHA-256 Hash           | d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2... |
| Total Vocabulary Size (V)          | 32,768 (Frozen, Immutable)                               |
| Structural Tokens (Pinned IDs 0–11)| <pad>=0, <s>=1, </s>=2, <unk>=3, <mask>=4,               |
|                                    | <sep>=5, <cls>=6, <eod>=7, <bos>=8, <eos>=9,             |
|                                    | <user>=10, <assistant>=11                                |
+------------------------------------+----------------------------------------------------------+
```

Hash verification exit code: **0 (100% Match)**. Zero modifications made to tokenizer artifacts or architecture.

---

## 3. Project Language Scope Invariant

The project language boundary remains strictly restricted to:
1. **Tamil** (`ta` / U+0B80–U+0BFF)
2. **English** (`en` / Latin script)
3. **Tanglish** (`ta-Latn` / Tamil-English code-mixed, Romanized Tamil)

All other languages (Hindi, Telugu, Kannada, Malayalam, Bengali, Gujarati) remain classified as `OUT_OF_SCOPE` in the master inventory (`PHASE28_SOURCE_RECONCILIATION.csv`).

---

## 4. Phase 26 Metric Addendum Invariant

The Phase 26 evaluation metrics and addendum are preserved:
- File present: [PHASE26_METRIC_CORRECTION_ADDENDUM.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/PHASE26_METRIC_CORRECTION_ADDENDUM.md)
- Held-out test set accuracy: **0.9800** (98 / 100 correct)
- Held-out test set Macro F1: **0.9493**
- Historical reports preserved without modification.

---

## 5. Storage & Directory Cleanliness Audit

```
Directory Check:
  C:\IGRIS\production:   DOES NOT EXIST / CLEAN (0 files)
  C:\IGRIS\raw:          DOES NOT EXIST / CLEAN (0 files)
  C:\IGRIS\acquired:     DOES NOT EXIST / CLEAN (0 files)
  C:\IGRIS\quarantine:   DOES NOT EXIST / CLEAN (0 files)
```

No external network requests were made to Hugging Face, Wikimedia, Project Gutenberg, IETF, or GitHub for dataset payloads.
