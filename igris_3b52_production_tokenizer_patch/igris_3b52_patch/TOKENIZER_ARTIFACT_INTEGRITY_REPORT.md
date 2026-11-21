# IGRIS Tokenizer Artifact Integrity Report
## Pre-Evaluation Forensic Verification of Candidate A and Experimental Candidate A

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Accountable Decision-Maker:** Sole Project Owner  
**Date:** 2026-11-20  
**Verification Status:** **ALL ARTIFACTS VERIFIED AND CRYPTOGRAPHICALLY INTACT**  

---

## 1. Cryptographic Hash Invariants

Prior to initiating any benchmark comparisons, the physical artifacts on disk were inspected and verified against project baseline digests:

| Tokenizer Artifact | Target Path | File Size | Authoritative Expected SHA-256 | Actual Measured SHA-256 | Integrity Status |
|---|---|:---:|---|---|:---:|
| **Original Candidate A** | `artifacts/tokenizer/candidate_a/tokenizer.json` | 891,955 B | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | **MATCH** |
| **Candidate B Reference** | `artifacts/tokenizer/candidate_b/tokenizer.model` | 504,500 B | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **MATCH** |
| **Experimental Candidate A** | `artifacts/tokenizer/candidate_a_synthetic_experiment/tokenizer.json` | 913,541 B | `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce` | `3393acbee2214ce09b9e03eaaf1a367a324b29032c61a1e4d0408e991c35c3ce` | **MATCH** |

---

## 2. Structural Special Token Slot Allocation (IDs 0–11)

Both `tokenizer.json` files were parsed at the JSON AST level to verify that all 12 structural special tokens occupy their exact assigned IDs without silent remapping or displacement:

| Token ID | Authoritative Token String | Candidate A Actual Token | Exp Candidate A Actual Token | Frontend Test Status | Runtime Adapter Status |
|:---:|---|---|---|:---:|:---:|
| **0** | `<|pad|>` | `<|pad|>` | `<|pad|>` | PASS | PASS |
| **1** | `<|begin_of_text|>` | `<|begin_of_text|>` | `<|begin_of_text|>` | PASS | PASS |
| **2** | `<|end_of_text|>` | `<|end_of_text|>` | `<|end_of_text|>` | PASS | PASS |
| **3** | `<think>` | `<think>` | `<think>` | PASS | PASS |
| **4** | `</think>` | `</think>` | `</think>` | PASS | PASS |
| **5** | `<action>` | `<action>` | `<action>` | PASS | PASS |
| **6** | `</action>` | `</action>` | `</action>` | PASS | PASS |
| **7** | `<action_result>` | `<action_result>` | `<action_result>` | PASS | PASS |
| **8** | `</action_result>` | `</action_result>` | `</action_result>` | PASS | PASS |
| **9** | `<|system|>` | `<|system|>` | `<|system|>` | PASS | PASS |
| **10** | `<|user|>` | `<|user|>` | `<|user|>` | PASS | PASS |
| **11** | `<|assistant|>` | `<|assistant|>` | `<|assistant|>` | PASS | PASS |

---

## 3. Architecture & Backend Configuration Consistency

Inspection of `build_metadata.json` across both candidate builds confirms identical runtime parameters:
- **Backend Core:** Hugging Face Tokenizers (Rust-based `tokenizers==0.23.3`)
- **Model Type:** ByteLevel BPE
- **Pre-Tokenizer:** ByteLevel (`add_prefix_space=False`, `use_regex=True`)
- **Decoder:** ByteLevel
- **Post-Processor:** `None`
- **Total Vocabulary Size:** Exactly 32,768 entries
- **Byte Fallback:** Full coverage of all 256 initial byte values (IDs 12–267)
- **Learned Merges Count:**
  - Original Candidate A: **63 merges** (trained on Phase 15 dry run)
  - Experimental Candidate A: **1,755 merges** (trained on Phase 31B synthetic training split)

---

## 4. Verification of Dependent Subsystems

1. **Inference Runtime Adapter (`src/igris/tokenizer/strict.py`):**
   - Verified that `StrictTokenizer` enforces `VOCAB_SIZE = 32768`, checks lone surrogates, and validates IDs without remapping.
2. **Frontend Serialization (`frontend/src/services/tokenizer/candidateA.ts`):**
   - Verified that TypeScript bindings and unit tests (`frontend/src/__tests__/tokenizer_candidate_a.test.ts`) assert the exact 12 structural special tokens and vocabulary limit.
3. **Artifact Isolation:**
   - The original Candidate A production directory (`artifacts/tokenizer/candidate_a/`) is untouched. The experimental build resides exclusively in `artifacts/tokenizer/candidate_a_synthetic_experiment/`.
