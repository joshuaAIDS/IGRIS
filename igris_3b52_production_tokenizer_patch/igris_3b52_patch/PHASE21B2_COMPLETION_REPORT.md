# PHASE 21B2 — COMPLETION REPORT
## INDICCORP UPSTREAM PATH, STATISTICS AND EVIDENCE CORRECTION

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase Status:** **COMPLETE**  
**Assigned Verdict:**  
**VERDICT A — ALL UPSTREAM PATHS, PUBLISHED STATISTICS AND PROJECT ESTIMATES RECONCILED**  
$$\mathbf{VERDICT\ A\ —\ ALL\ UPSTREAM\ PATHS,\ PUBLISHED\ STATISTICS\ AND\ PROJECT\ ESTIMATES\ RECONCILED}$$

---

## 1. Executive Summary

Phase 21B2 executed a read-only verification and documentation phase to resolve factual discrepancies identified during Phase 21B1.

All tasks mandated by the project charter have been successfully completed:
1. **Upstream Paths Corrected:** Established exact file mappings for `ai4bharat/IndicCorpV2` at commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd` (`data/ta.txt`, `data/hi-*.txt`, `data/te.txt`, `data/ml.txt`, `data/kn.txt`, `data/bn.txt`, `data/gu.txt`).
2. **ACL 2023 Table 3 Statistics Corrected:** Restored authoritative token counts for Malayalam (931 M), Kannada (875 M), and Gujarati (901 M), confirming the official 7-language total of **10,947 million tokens**.
3. **IGRIS Projections Reconciled:** Fully isolated IGRIS Candidate A projections (~10.60 B tokens) in separate tables, clearly labeled as theoretical engineering estimates, with zero empirical validation claims.
4. **Legal Scope Preserved:** Delineated publisher CC0 waiver from third-party news copyright (CC0 4(c) disclaimer), reaffirming that qualified legal review is an outstanding requirement before commercialization.
5. **Technical Suitability Separated:** Strictly separated verified tokenizer behavior from unverified assumptions regarding raw corpus quality.
6. **Governance Invariants Enforced:** Zero production bytes acquired, ingress gate locked, zero sources authorized, and tokenizer hashes preserved invariant.

---

## 2. Invariant & Governance Compliance Matrix

```
+-------------------------------------------------+----------------------------------------------------+----------+
| Governance Invariant                            | Verified Operational State                         | Result   |
+-------------------------------------------------+----------------------------------------------------+----------+
| 1. Operating Model                              | SOLO_DEVELOPER_OWNER_REVIEW (Sole Human Authority) | PASS     |
| 2. Production Dataset Ingress                   | LOCKED (Default-Deny Enforced)                     | PASS     |
| 3. Production Bytes Acquired                    | 0 Bytes Downloaded (Read-Only Inspection)          | PASS     |
| 4. Production Source Authorizations             | 0 Sources Authorized (Deferred to Owner Review)    | PASS     |
| 5. Selected Tokenizer (Candidate A) Hash        | ac7e18b13973450b43bfff18609a833e4ef0e642b8dc...    | PASS     |
| 6. Unselected Tokenizer (Candidate B) Hash      | d3a3431e07c87ecce863647202ddc9b47b964718adba...    | PASS     |
| 7. Quarantine Sandbox State                     | EMPTY of Production Files                          | PASS     |
| 8. Filename Isolation Invariant                 | No non-markdown file contains 'quarantine' in name | PASS     |
| 9. Model Training State                         | Pretraining Prohibited; Model Weights Untained     | PASS     |
+-------------------------------------------------+----------------------------------------------------+----------+
```

---

## 3. Inventory of Phase 21B2 Deliverables

All required deliverables have been authored, verified, and mirrored:

1. **`PHASE21B2_UPSTREAM_PATH_VERIFICATION.md`**  
   - Independent verification of repository structure at commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`, flat text mappings, and file size measurements.
2. **`PHASE21B2_ACL_STATISTICS_CORRECTION.csv`**  
   - Formal 10-column CSV correcting all language token counts against Doddapaneni et al. (ACL 2023 Table 3), showing the verified total of 10,947 M tokens.
3. **`PHASE21B2_IGRIS_PROJECTION_RECONCILIATION.csv`**  
   - Formal 12-column CSV isolating IGRIS Candidate A projections, tokenizer method, cleaning estimates, and explicit labeling as unvalidated estimates.
4. **`PHASE21B2_LICENSE_SCOPE_STATUS.md`**  
   - Rigorous delineation of publisher CC0 waiver, Section 4(c) third-party copyright exclusion, TDM doctrine, and mandatory qualified legal review.
5. **`PHASE21B2_CORRECTION_AUDIT_LOG.md`**  
   - Complete itemized audit trail recording path corrections, statistics corrections, and governance preservation without silent overwrites.
6. **`PHASE21B2_COMPLETION_REPORT.md`**  
   - This document, establishing phase completion, governance compliance, and assigning Verdict A.
7. **`tests/test_phase21b2_path_statistics_and_projection_correction.py`**  
   - Automated pytest suite asserting the integrity of all Phase 21B2 deliverables and governance invariants.

---

## 4. Reconciled Statistics & Projection Summary

```
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
| Source ID | Language | Verified Path         | ACL 2023 Tokens (M)   | IGRIS Projected Tokens (M)  | Projection Status     |
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
| SRC-TM-01 | Tamil    | data/ta.txt           | 476 M (ACL Table 3)   | ~1,062.4 M (32k BPE)        | PROJECTED_UNVALIDATED |
| SRC-HI-01 | Hindi    | data/hi-*.txt (1,2,3) | 6,107 M (ACL Table 3) | ~3,536.8 M (Post-dedup)     | PROJECTED_UNVALIDATED |
| SRC-OI-01 | Telugu   | data/te.txt           | 731 M (ACL Table 3)   | ~1,236.7 M (32k BPE)        | PROJECTED_UNVALIDATED |
| SRC-OI-02 | Malayalam| data/ml.txt           | 931 M (ACL Table 3)   | ~822.7 M (Clean subset)     | PROJECTED_UNVALIDATED |
| SRC-OI-03 | Kannada  | data/kn.txt           | 875 M (ACL Table 3)   | ~623.5 M (Clean subset)     | PROJECTED_UNVALIDATED |
| SRC-OI-04 | Bengali  | data/bn.txt           | 926 M (ACL Table 3)   | ~2,131.9 M (32k BPE)        | PROJECTED_UNVALIDATED |
| SRC-OI-05 | Gujarati | data/gu.txt           | 901 M (ACL Table 3)   | ~1,188.3 M (32k BPE)        | PROJECTED_UNVALIDATED |
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
| TOTAL     | 7 Langs  | Flat text / sharded   | 10,947 M (~10.95 B)   | ~10,602.3 M (~10.60 B)      | PRELIMINARY ESTIMATE  |
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
```

---

## 5. Mandatory Stop Condition & Next Steps

Phase 21B2 is formally **COMPLETE**.

In strict accordance with the IGRIS governance charter and `SOLO_DEVELOPER_OWNER_REVIEW` operating model:
- Execution is **HALTED**.
- Ingress remains **LOCKED**; 0 production datasets downloaded; 0 sources authorized.
- Even with Verdict A, acquisition remains unauthorized.
- Awaiting the explicit decision and directive of the Project Owner.