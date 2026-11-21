# IGRIS PHASE 20B — TOKENIZER HASH HISTORY & FORENSIC RECONCILIATION

**Document ID:** `IGRIS-PHASE20B-TH-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target:** Tokenizer Candidate A & Candidate B Artifact Integrity  
**Status:** FORENSICALLY RECONCILED — 100% BITWISE INVARIANT  

---

## 1. Executive Summary

This forensic audit investigates the historical SHA-256 hashes of the physical tokenizer artifacts for **Candidate A** (HuggingFace BPE) and **Candidate B** (SentencePiece Unigram) across the complete project lifecycle (Phases 6 through 20A).

The investigation concludes that:
1. The **physical files on disk have never changed**. Their byte-level SHA-256 hashes are identical to the earliest recorded baselines from Phase 6.
2. Every technical report, metadata JSON file, and evaluation report authored in the repository across all phases records the exact canonical baseline hashes.
3. The discrepancy cited in the Phase 20B audit scope between the baseline hashes and the strings presented in the final assistant response of Phase 20A (`ac7e18b1d9bf...` and `d3a3431e3d36...`) was a **conversational presentation artifact**: the assistant expanded truncated prefix strings (`ac7e18b1...` and `d3a3431e...`) into hallucinated hex completions during chat markdown rendering. No physical file, metadata file, or repository report was ever altered.

---

## 2. Physical File Direct Hash Verification

Calculated directly from the active files on disk using Python standard library `hashlib.sha256()`:

| Artifact | Physical File Path | File Size | SHA-256 Hex Digest |
| :--- | :--- | :--- | :--- |
| **Candidate A** | `artifacts/tokenizer/candidate_a/tokenizer.json` | 1,846,723 B | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` |
| **Candidate B** | `artifacts/tokenizer/candidate_b/tokenizer.model` | 584,233 B | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` |

### Auxiliary Build Metadata Verification
- `artifacts/tokenizer/candidate_a/build_metadata.json`:
  ```json
  "file_sha256": "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
  ```
- `artifacts/tokenizer/candidate_b/build_metadata.json`:
  ```json
  "file_sha256": "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
  ```

Both build metadata records match the physical file hashes to the exact byte.

---

## 3. Chronological Hash Audit (Phases 6–20A)

Every document and metadata record across 88 repository files was forensically inspected:

| Project Phase | Primary Document / Artifact | Candidate A Recorded SHA-256 | Candidate B Recorded SHA-256 | Direct Hash Match? |
| :--- | :--- | :--- | :--- | :---: |
| **Phase 6** | `IGRIS_PHASE6_FINAL_VERDICT.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 6** | `IGRIS_PHASE6_INDEPENDENT_AUDIT.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 7** | `IGRIS_PHASE7_FINAL_STATUS.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 8** | `IGRIS_PHASE8_FINAL_STATUS.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 9** | `IGRIS_PHASE9_FINAL_STATUS.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 10** | `IGRIS_PHASE10_FINAL_READINESS_REPORT.md`| `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 11** | `IGRIS_PHASE11_FINAL_STATUS.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 12** | `IGRIS_PHASE12_FINAL_STATUS.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 13** | `IGRIS_PHASE13_FINAL_STATUS.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 14** | `IGRIS_PHASE14_FINAL_STATUS.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 15** | `IGRIS_PHASE15_TOKENIZER_CANDIDATE_COMPARISON.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 15** | `reports/phase15/candidate_comparison.json` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 16** | `PHASE_16_COMPLETION_REPORT.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 17** | `chk_step_000010_metadata.json` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 18** | `PHASE18_SCALABILITY_BENCHMARK.json` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 19** | `dry_run_audit_metrics.json` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 19** | `PHASE19_TOKENIZER_INTEGRITY_REPORT.md` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 20** | `PHASE20_TOKENIZER_FINAL_INTEGRITY_REPORT.md`| `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 20A** | `PHASE20A_MASTER_RECONCILIATION_REPORT.md`| `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |
| **Phase 20A** | `PHASE20A_TOKENIZER_SPECIFICATION_RECONCILIATION.md`| `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **YES** |

---

## 4. Origin of the Divergent Hash Strings

The Phase 20B audit identified two divergent hash strings cited in Phase 20A chat:
- String A: `ac7e18b1d9bf6c1ecfba2e95a8ffc013bc083232049cbbcfb1b9d45e5482cc23`
- String B: `d3a3431e3d36b76aa96e6761f1857c919a32c25ae99ec98711ae7faeb6ab66c7`

### Forensic Investigation:
1. **Repository Search:** A recursive scan of all 74 code files, JSON configurations, test files, and markdown documents across the entire repository revealed that **neither string appears in any file on disk**.
2. **Phase 20A Document Inspection:**
   - In `PHASE20A_MASTER_RECONCILIATION_REPORT.md`: Only `ac7e18b13973...` and `d3a3431e07c8...` appear.
   - In `PHASE20A_TOKENIZER_SPECIFICATION_RECONCILIATION.md`: Only `ac7e18b13973...` and `d3a3431e07c8...` appear.
   - In `PHASE20A_COMPLETION_REPORT.md`: The hashes were recorded with 8-character prefix and ellipsis: `ac7e18b1...` and `d3a3431e...`.
3. **Transcript Log Analysis:**
   - The strings first occurred at **Step 3548** in the conversation transcript (`transcript_full.jsonl`).
   - Step 3548 was the chat assistant's final markdown presentation message. When formatting the summary table, the assistant observed the prefix `ac7e18b1...` and `d3a3431e...` from the preceding completion report and auto-completed them as hallucinated 64-character hexadecimal values instead of querying the physical files.

### Conclusion on Discrepancy:
* The discrepancy was **100% a conversational presentation artifact** in chat prose.
* It was **not** caused by a different file, a new artifact version, or an actual file change.
* The physical files are, and have always been, identical to the baseline hashes established in Phase 6.

---

## 5. Architectural Invariance Confirmation

- Tokenizer Candidate A:
  - Format: HuggingFace Fast Tokenizer (`tokenizer.json`)
  - Algorithm: Byte-Pair Encoding (BPE)
  - Vocabulary Size: 32,768
  - Structural Tokens: 12 tokens `<|pad|>` (0) to `<|assistant|>` (11)
  - SHA-256: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
- Tokenizer Candidate B:
  - Format: Google SentencePiece Model (`tokenizer.model`)
  - Algorithm: Unigram Language Model
  - Vocabulary Size: 32,768
  - Structural Tokens: 12 tokens `<|pad|>` (0) to `<|assistant|>` (11)
  - SHA-256: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
