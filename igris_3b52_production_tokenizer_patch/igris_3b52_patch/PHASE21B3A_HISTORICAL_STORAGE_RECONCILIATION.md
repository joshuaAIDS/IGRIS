# PHASE 21B3A — HISTORICAL STORAGE RECONCILIATION
## Forensic Audit of the Early 37.1 GB Baseline and Provenance Tracking

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3A  

---

## 1. Investigation of Historical Phase 21 Artifacts

Inspection of the original repository records in Phase 21 (`PHASE21_MULTILINGUAL_STATISTICS.csv`) reveals how the 37.1 GB figure was originally recorded:

```
+-----------+----------------------+----------+-----------------------------+-------------------------------+-----------------------+
| Source ID | Source Name          | Language | Statistic Basis             | Raw Bytes Estimate            | Raw Display String    |
+-----------+----------------------+----------+-----------------------------+-------------------------------+-----------------------+
| SRC-TM-01 | IndicCorp v2 (Tamil) | ta       | PUBLISHED_CATALOG_ESTIMATE  | 4,080,218,931                 | 3.8 GB                |
| SRC-HI-01 | IndicCorp v2 (Hindi) | hi       | PUBLISHED_CATALOG_ESTIMATE  | 13,421,772,800                | 12.5 GB               |
| SRC-OI-01 | IndicCorp v2 (Telugu)| te       | PUBLISHED_CATALOG_ESTIMATE  | 4,509,715,660                 | 4.2 GB                |
| SRC-OI-02 | IndicCorp v2 (Mal)   | ml       | PUBLISHED_CATALOG_ESTIMATE  | 2,791,728,742                 | 2.6 GB                |
| SRC-OI-03 | IndicCorp v2 (Kan)   | kn       | PUBLISHED_CATALOG_ESTIMATE  | 2,254,857,830                 | 2.1 GB                |
| SRC-OI-04 | IndicCorp v2 (Ben)   | bn       | PUBLISHED_CATALOG_ESTIMATE  | 8,375,186,227                 | 7.8 GB                |
| SRC-OI-05 | IndicCorp v2 (Guj)   | gu       | PUBLISHED_CATALOG_ESTIMATE  | 4,402,341,478                 | 4.1 GB                |
+-----------+----------------------+----------+-----------------------------+-------------------------------+-----------------------+
| TOTAL     | 7 IndicCorp Corpora  | 7 Langs  | PUBLISHED_CATALOG_ESTIMATE  | 39,835,821,668                | 37.1 GB (Sum of disp) |
+-----------+----------------------+----------+-----------------------------+-------------------------------+-----------------------+
```

---

## 2. Root Cause Determination

The audit investigated whether the historical 37.1 GB figure originated as:
1. A sampled subset.
2. A projected filtered corpus.
3. A deduplicated corpus estimate.
4. A compressed archive estimate.
5. An undocumented preliminary catalog assumption.

### Findings:
- The metadata in Phase 21 labeled the figure as `PUBLISHED_CATALOG_ESTIMATE`.
- However, the underlying mathematical model or external catalog table from which those specific byte numbers (`4,080,218,931` for Tamil, `13,421,772,800` for Hindi, etc.) were generated was not accompanied by an archival calculation script.
- The actual upstream repository at Hugging Face contains **183.70 GB** across the 9 files.
- In accordance with the Phase 21B3A mandate: Because the specific derivation logic cannot be conclusively confirmed from committed source code or academic paper tables, the origin is formally classified as:

**HISTORICAL_CAUSE_UNCONFIRMED**  
$$\mathbf{HISTORICAL\_CAUSE\_UNCONFIRMED}$$

- Historical reports are preserved unedited to maintain complete transparency and provenance auditability.