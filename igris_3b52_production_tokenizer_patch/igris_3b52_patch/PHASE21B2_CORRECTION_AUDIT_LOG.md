# PHASE 21B2 — CORRECTION AUDIT LOG
## Detailed Audit Trail of Upstream Paths, ACL 2023 Statistics, and Projection Labeling

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B2  

---

## 1. Audit Scope & Rationale

During the Phase 21B1 review, three categories of factual discrepancies were identified:
1. **Upstream Path Structure:** An assumed BCP-47 directory pattern (`data/<lang>_<Script>/`) was described instead of the actual flat text repository layout (`data/<lang>.txt` and `data/hi-*.txt`).
2. **ACL 2023 Published Statistics:** Several language token counts in Phase 21B1 were derived from secondary web scrape columns rather than Table 3 of the authoritative ACL 2023 publication (Doddapaneni et al.).
3. **Projection Labeling:** IGRIS token yield estimates were insufficiently distinguished from empirically verified corpus statistics.

This audit log records the exact corrections applied. Historical Phase 21B and Phase 21B1 reports are preserved intact for governance auditability.

---

## 2. Itemized Corrections

### Correction 1: Upstream File Layout
- **Historical Description (Phase 21B1):** `data/tam_Taml/`, `data/hin_Deva/`, `data/tel_Telu/`, `data/mal_Mlym/`, `data/kan_Knda/`, `data/ben_Beng/`, `data/guj_Gujr/`.
- **Corrected Upstream Mapping (Phase 21B2):**
  - Tamil: `data/ta.txt` (~11.8 GB)
  - Hindi: `data/hi-1.txt`, `data/hi-2.txt`, `data/hi-3.txt` (`data/hi-*.txt`, ~80 GB total)
  - Telugu: `data/te.txt` (~15.8 GB)
  - Malayalam: `data/ml.txt` (~26.3 GB)
  - Kannada: `data/kn.txt` (~19.6 GB)
  - Bengali: `data/bn.txt` (~16.0 GB)
  - Gujarati: `data/gu.txt` (~14.1 GB)
- **Repository Verification:** Pinned at commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`.

### Correction 2: ACL 2023 Table 3 Token Statistics
- **Tamil:** 476 M tokens (Confirmed aligned).
- **Hindi:** 6,107 M tokens (Confirmed aligned).
- **Telugu:** 731 M tokens (Confirmed aligned).
- **Malayalam:** Corrected from 2,205 M to **931 M** tokens (Variance: -1,274 M tokens).
- **Kannada:** Corrected from 1,751 M to **875 M** tokens (Variance: -876 M tokens).
- **Bengali:** 926 M tokens (Confirmed aligned).
- **Gujarati:** Corrected from 1,410 M to **901 M** tokens (Variance: -509 M tokens).
- **Selected Seven-Language Pool Total:** Corrected from 13,606 M to **10,947 M tokens** (Exact sum: $476 + 6107 + 731 + 931 + 875 + 926 + 901 = 10,947$ million tokens).

### Correction 3: Strict Labeling of IGRIS Estimates
- **Rule Enforced:** All IGRIS Candidate A token counts (~10.60 B aggregate) are formally classified as:
  `PRELIMINARY_ENGINEERING_ESTIMATES (PROJECTED_UNVALIDATED)`
- **Restriction:** Because zero production bytes have been acquired, no claim of empirical validation of sentence counts, cleaning yields, or deduplication reductions is permitted.

---

## 3. Governance Invariant Audit

- Historical files (`PHASE21B_COMPLETION_REPORT.md`, `PHASE21B1_COMPLETION_REPORT.md`) are preserved unedited.
- Tokenizer hashes verified invariant:
  - Candidate A: `ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561`
  - Candidate B: `d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888`
- Production ingress remains **LOCKED**.
- 0 production datasets acquired (0 bytes).
- 0 sources authorized.