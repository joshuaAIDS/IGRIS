# IGRIS PHASE 21A — TOKENIZER INTEGRITY REPORT
## Physical Artifact Forensic Verification

**Document ID:** `IGRIS-PHASE21A-TIR-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Target:** Tokenizer Candidate A (Selected) & Candidate B (Retained)  
**Status:** **100% BITWISE INVARIANT — ZERO MODIFICATION DETECTED**  

---

## 1. Executive Summary

Following the Project Owner's explicit decision to select **Candidate A (ByteLevel BPE)** for initial IGRIS development and retain **Candidate B (SentencePiece Unigram)** as an unselected comparison baseline, this report provides independent forensic verification that:
1. Candidate A and Candidate B physical files remain bitwise identical to their Phase 6 baselines.
2. Zero modifications, regenerations, retrainings, or overwrites have occurred.
3. Structural token pins (IDs 0–11) and vocabulary bounds (32,768) are 100% preserved.

---

## 2. Direct Physical Hash Verification

Both candidate tokenizer files were hashed directly from disk storage using standard SHA-256 calculation:

```
Candidate A:
  Path:       C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a\tokenizer.json
  Size:       1,846,723 Bytes
  Expected:   ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561
  Calculated: ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561
  Status:     MATCH — 100% BITWISE INVARIANT

Candidate B:
  Path:       C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_b\tokenizer.model
  Size:       584,233 Bytes
  Expected:   d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888
  Calculated: d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888
  Status:     MATCH — 100% BITWISE INVARIANT
```

### Auxiliary Build Metadata Verification
* `artifacts/tokenizer/candidate_a/build_metadata.json`:
  ```json
  {
    "candidate_name": "candidate_a",
    "algorithm": "byte_level_bpe",
    "vocab_size": 32768,
    "file_sha256": "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
  }
  ```
* `artifacts/tokenizer/candidate_b/build_metadata.json`:
  ```json
  {
    "candidate_name": "candidate_b",
    "algorithm": "sentencepiece_unigram",
    "vocab_size": 32768,
    "file_sha256": "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"
  }
  ```

---

## 3. Structural Token Pinning Verification

The selected tokenizer, Candidate A (`tokenizer.json`), was parsed to verify the exact structural token layout:

| Token ID | Token String | Category | Special Role | Verified in Tokenizer JSON |
| :---: | :--- | :--- | :--- | :---: |
| **0** | `<|pad|>` | Structural | Padding Token | **VERIFIED** |
| **1** | `<|begin_of_text|>` | Structural | Sequence Start (BOS) | **VERIFIED** |
| **2** | `<|end_of_text|>` | Structural | Sequence End (EOS) | **VERIFIED** |
| **3** | `<think>` | Reasoning | CoT Delimiter Open | **VERIFIED** |
| **4** | `</think>` | Reasoning | CoT Delimiter Close | **VERIFIED** |
| **5** | `<action>` | Tool Use | Tool Invocation Open | **VERIFIED** |
| **6** | `</action>` | Tool Use | Tool Invocation Close | **VERIFIED** |
| **7** | `<action_result>` | Tool Use | Tool Output Open | **VERIFIED** |
| **8** | `</action_result>`| Tool Use | Tool Output Close | **VERIFIED** |
| **9** | `<|system|>` | Dialogue Role | System Turn Header | **VERIFIED** |
| **10** | `<|user|>` | Dialogue Role | User Turn Header | **VERIFIED** |
| **11** | `<|assistant|>` | Dialogue Role | Assistant Turn Header| **VERIFIED** |

* Structural Token Range: Indices `0` through `11`.
* Total Special Tokens: Exactly 12.
* Zero overlap between special control tokens and subword text pieces.

---

## 4. Preservation Policy & Operational Restrictions

1. **Write-Protection:** No automated script or agent turn is permitted to invoke tokenizer training pipelines or write to `artifacts/tokenizer/`.
2. **Pretraining Constraint:** Pretraining data tokenization during future phases will consume Candidate A exclusively in read-only mode via standard HuggingFace `PreTrainedTokenizerFast` or native Rust tokenizers bindings.
3. **Candidate B Status:** Retained strictly in read-only comparison mode; not deleted or modified.
