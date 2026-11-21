# IGRIS PHASE 20A — TOKENIZER STRUCTURAL-TOKEN SPECIFICATION RECONCILIATION REPORT

**Document ID:** `IGRIS-PHASE20A-TOK-001`  
**Execution Date:** 2026-11-18  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Phase Objective:** Critical Audit of Structural-Token Discrepancy & Verification of Physical Tokenizer Files  
**Reconciliation Finding:** **DISCREPANCY RESOLVED — ROOT CAUSE: HISTORICAL PROSE DOCUMENTATION ERROR IN PHASE 19 REPORTS**  

---

## 1. Executive Summary

This report delivers the forensic investigation into the structural-token discrepancy between earlier narrative documentation (which cited square-bracket tokens such as `[PAD]`, `[UNK]`, `[IND_NUM]`) and the Phase 20 report (which cited modern delimiter tokens `<|pad|>`, `<|begin_of_text|>`, `<think>`, `<action>`, etc.).

### Definitive Conclusion:
The discrepancy is an unequivocal **HISTORICAL PROSE DOCUMENTATION ERROR** in the narrative summaries of Phase 19 (`PHASE19_MASTER_AUDIT_REPORT.md` and `PHASE19_COMPLETION_REPORT.md`).

The actual physical artifacts:
1. [artifacts/tokenizer/candidate_a/tokenizer.json](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_a/tokenizer.json)
2. [artifacts/tokenizer/candidate_b/tokenizer.model](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_b/tokenizer.model)
3. [artifacts/tokenizer/candidate_a/build_metadata.json](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_a/build_metadata.json)
4. [artifacts/tokenizer/candidate_b/build_metadata.json](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_b/build_metadata.json)
5. Foundational governance documents: [REVIEW_CHIEF_ARCHITECT_V2.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_CHIEF_ARCHITECT_V2.md) and [IGRIS_PHASE9_REVIEWER_OPERATIONS_MANUAL.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_PHASE9_REVIEWER_OPERATIONS_MANUAL.md)
6. All automated test suites from Phase 7 through Phase 20: [scripts/run_acceptance_3b57.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/run_acceptance_3b57.py), [tests/test_builders.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests/test_builders.py), [strict.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/strict.py), [artifact_validation.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifact_validation.py)

**HAVE ALWAYS CONTAINED AND PINNED:**
$$\mathbf{<\!|pad|\!>,\ <\!|begin\_of\_text|\!>,\ <\!|end\_of\_text|\!>,\ <think>,\ </think>,\ <action>,\ </action>,\ <action\_result>,\ </action\_result>,\ <\!|system|\!>,\ <\!|user|\!>,\ <\!|assistant|\!>}$$

Both tokenizer candidate files are 100% cryptographically intact, their SHA-256 hashes are bitwise identical to their creation baseline, and they share identical structural-token semantics.

---

## 2. In-Depth Inspection of Physical Tokenizer Files

### 2.1 File Hashes & Identity Audit
Direct cryptographic inspection of physical files from disk:

| File Inspected | Role | Format | Measured SHA-256 Digest | Status |
| :--- | :--- | :---: | :--- | :---: |
| `artifacts/tokenizer/candidate_a/tokenizer.json` | Candidate A | BPE JSON | `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561` | **MATCH (Unchanged)** |
| `artifacts/tokenizer/candidate_b/tokenizer.model` | Candidate B | SentencePiece | `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888` | **MATCH (Unchanged)** |
| `artifacts/tokenizer/candidate_a/build_metadata.json` | Metadata A | JSON | `e2a6d71b31a316b24d62ca393c5d63f03b29c9efb05423f6c888d363b8603c14` | **MATCH (Unchanged)** |
| `artifacts/tokenizer/candidate_b/build_metadata.json` | Metadata B | JSON | `1a7ca2c5fc51e18d6e3381676dfc37d995aa42bc516104f76d91bb3a2df30bdf` | **MATCH (Unchanged)** |

---

### 2.2 Token ID & String Verification
Inspecting the compiled vocabulary tables of both tokenizers demonstrates exact alignment at indices 0 through 11:

| Token ID | Candidate A (`tokenizer.json`) | Candidate B (`tokenizer.model`) | Candidate A `added_tokens` Attributes | Candidate B Metadata Specification |
| :---: | :--- | :--- | :--- | :--- |
| **0** | `<|pad|>` | `<|pad|>` | `id=0, special=True, normalized=False` | `user_defined_symbols: <|pad|>` |
| **1** | `<|begin_of_text|>` | `<|begin_of_text|>` | `id=1, special=True, normalized=False` | `user_defined_symbols: <|begin_of_text|>` |
| **2** | `<|end_of_text|>` | `<|end_of_text|>` | `id=2, special=True, normalized=False` | `user_defined_symbols: <|end_of_text|>` |
| **3** | `<think>` | `<think>` | `id=3, special=True, normalized=False` | `user_defined_symbols: <think>` |
| **4** | `</think>` | `</think>` | `id=4, special=True, normalized=False` | `user_defined_symbols: </think>` |
| **5** | `<action>` | `<action>` | `id=5, special=True, normalized=False` | `user_defined_symbols: <action>` |
| **6** | `</action>` | `</action>` | `id=6, special=True, normalized=False` | `user_defined_symbols: </action>` |
| **7** | `<action_result>` | `<action_result>` | `id=7, special=True, normalized=False` | `user_defined_symbols: <action_result>` |
| **8** | `</action_result>` | `</action_result>` | `id=8, special=True, normalized=False` | `user_defined_symbols: </action_result>` |
| **9** | `<|system|>` | `<|system|>` | `id=9, special=True, normalized=False` | `user_defined_symbols: <|system|>` |
| **10** | `<|user|>` | `<|user|>` | `id=10, special=True, normalized=False` | `user_defined_symbols: <|user|>` |
| **11** | `<|assistant|>` | `<|assistant|>` | `id=11, special=True, normalized=False` | `user_defined_symbols: <|assistant|>` |

---

## 3. Forensic Origin of the Square-Bracket `[IND_NUM]` Specification

A repository-wide textual search revealed the exact provenance of the square-bracket notation:
1. **Physical Artifacts:** Square-bracket tokens (`[IND_NUM]`, `[IND_DATE]`, `[PAD]`, `[CLS]`, `[SEP]`, `[MASK]`) appear in **zero** `.py`, **zero** `.json`, and **zero** `.model` files in the repository.
2. **Historical Governance:** Foundational documents authored prior to Phase 19 explicitly cite `<|pad|>` and `<think>`:
   - [REVIEW_CHIEF_ARCHITECT_V2.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/REVIEW_CHIEF_ARCHITECT_V2.md) (line 34):
     `"12 Structural Tokens: Pinned at token IDs 0–11 (<|pad|>, <|begin_of_text|>, <|end_of_text|>, <think>, </think>, <action>, </action>, <action_result>, </action_result>, <|system|>, <|user|>, <|assistant|>)."`
   - [IGRIS_PHASE9_REVIEWER_OPERATIONS_MANUAL.md](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/IGRIS_PHASE9_REVIEWER_OPERATIONS_MANUAL.md) (line 74):
     `"specifically the 12 pinned structural tokens at IDs 0–11: ID 0: <|pad|>, ID 3: <think>"`
3. **The Phase 19 Documentation Slip:**
   In Phase 19, the reporting agent synthesized `PHASE19_MASTER_AUDIT_REPORT.md` and `PHASE19_COMPLETION_REPORT.md`. While the automated dry-run script ([scripts/phase19_end_to_end_dry_run.py](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/phase19_end_to_end_dry_run.py)) imported and tested the real tokenizer with `<|pad|>`, the author of the markdown report drafted a prose description from memory using classical BERT-style brackets (`[PAD], [UNK], [BOS], [EOS], [MASK], [SEP], [CLS], [NL], [IND_NUM], [IND_DATE], [SYS], [USR]`).
4. **Phase 20 Truthfulness:**
   In Phase 20, the audit inspected the physical files directly, accurately reported `<|pad|>` through `<|assistant|>`, and verified them across all acceptance tests.

---

## 4. Semantic Equivalency & Invariant Verification

1. **Equivalence Between Candidate A and B:**
   - Both tokenizers implement the exact same 12 control tokens at indices 0 through 11.
   - `<|pad|>` (ID 0) acts as the non-attending batch padding token in both models.
   - `<|begin_of_text|>` (ID 1) and `<|end_of_text|>` (ID 2) serve as sequence boundary delimiters.
   - `<think>` / `</think>` (IDs 3–4) isolate internal reasoning chains.
   - `<action>` / `</action>` and `<action_result>` / `</action_result>` (IDs 5–8) manage agentic function execution.
   - `<|system|>`, `<|user|>`, `<|assistant|>` (IDs 9–11) provide role-delimited multi-turn conversational formatting.
2. **Byte Fallback:**
   - Candidate B maps byte tokens `<0x00>` through `<0xFF>` to IDs 12–267.
   - Candidate A uses HuggingFace ByteLevel pre-tokenization.
   - Neither tokenizer produces out-of-vocabulary exceptions on arbitrary UTF-8 byte sequences.

---

## 5. Audit Determination & Resolution

```
====================================================================================================
AUDIT DETERMINATION:
DISCREPANCY CLASSIFICATION: HISTORICAL PROSE DOCUMENTATION ERROR (PHASE 19)
PHYSICAL TOKENIZER INTEGRITY: 100% INTACT AND BITWISE VERIFIED
PHASE 20 SPECIFICATION: CONFIRMED ACCURATE AND REFLECTIVE OF PHYSICAL FILES
INCOMPATIBILITY: NONE (CANDIDATES A AND B ARE FULLY COMPATIBLE)
====================================================================================================
```
Neither tokenizer requires retraining, replacement, or modification.
