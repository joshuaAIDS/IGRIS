# PHASE 21B3 — IGRIS PROJECTION STATUS & RECALCULATION TRIGGERS
## Status Classification of Theoretical Yield Estimates and Acquisition Impact Analysis

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B3  
**Scope:** Theoretical Projection Auditing & Capacity Recalculation Planning  

---

## 1. Formal Classification of IGRIS Projections

All IGRIS Candidate A token counts and cleaning estimates established in Phase 21B2 are formally preserved and classified as:

$$\mathbf{PROJECTED\_UNVALIDATED\ (PRELIMINARY\ ENGINEERING\ ESTIMATES)}$$

```
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
| Source ID | Language | Verified Path         | ACL 2023 Tokens (M)   | IGRIS Projected Tokens (M)  | Classification Status |
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
| SRC-TM-01 | Tamil    | data/ta.txt           | 476 M (ACL Table 3)   | ~1,062.4 M (32k BPE)        | PROJECTED_UNVALIDATED |
| SRC-HI-01 | Hindi    | data/hi-*.txt (1,2,3) | 6,107 M (ACL Table 3) | ~3,536.8 M (Post-dedup)     | PROJECTED_UNVALIDATED |
| SRC-OI-01 | Telugu   | data/te.txt           | 731 M (ACL Table 3)   | ~1,236.7 M (32k BPE)        | PROJECTED_UNVALIDATED |
| SRC-OI-02 | Malayalam| data/ml.txt           | 931 M (ACL Table 3)   | ~822.7 M (Clean subset)     | PROJECTED_UNVALIDATED |
| SRC-OI-03 | Kannada  | data/kn.txt           | 875 M (ACL Table 3)   | ~623.5 M (Clean subset)     | PROJECTED_UNVALIDATED |
| SRC-OI-04 | Bengali  | data/bn.txt           | 926 M (ACL Table 3)   | ~2,131.9 M (32k BPE)        | PROJECTED_UNVALIDATED |
| SRC-OI-05 | Gujarati | data/gu.txt           | 901 M (ACL Table 3)   | ~1,188.3 M (32k BPE)        | PROJECTED_UNVALIDATED |
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
| TOTAL     | 7 Langs  | 9 Files               | 10,947 M (~10.95 B)   | ~10,602.3 M (~10.60 B)      | PRELIMINARY ESTIMATE  |
+-----------+----------+-----------------------+-----------------------+-----------------------------+-----------------------+
```

---

## 2. Prohibition Against Empirical Claims

Because zero production corpus files have been downloaded or ingested:
1. **Sentence Counts:** The ~472.10 million sentence figure is a modeled estimate; it has not been validated against the physical repository files.
2. **Deduplication Reductions:** The ~15–35% cleaning and MinHash deduplication reduction rates are theoretical projections derived from synthetic benchmark calibration.
3. **No Empirical Validation:** Neither the sentence counts, nor deduplication rates, nor Candidate A token yields have been empirically measured against production bytes.

---

## 3. Recalculation Triggers for Future Acquisition Planning

The discovery that physical repository files total **183.70 GB** (rather than 37.1 GB) establishes four concrete recalculation triggers if the owner authorizes full-corpus acquisition:

1. **Quarantine Storage Capacity:**  
   - *Previous Plan:* 40 GB buffer.  
   - *Recalculation Trigger:* Must allocate at least **200 GB** for quarantine intake and uncompressed staging.
2. **Raw Token Ingestion Ceiling:**  
   - If IGRIS tokenizes the entire ~183.7 GB corpus using Candidate A (32k vocabulary) rather than a pre-filtered 37 GB slice, the gross token yield before deduplication will exceed **25–30 Billion tokens**.
3. **Arrow Sharding & Memory-Mapped Footprint:**  
   - Binary dataset sharding (`uint16` token IDs) will require ~50–60 GB of memory-mapped storage instead of the planned ~21 GB.
4. **Pretraining Chinchilla Compute Budget:**  
   - For the IGRIS 512-dim, 16-layer architecture (~73.4M parameters), compute-optimal training requires ~1.47 Billion tokens ($20 	imes 	ext{parameters}$).
   - Ingesting a full 25B+ token pool represents a massive ~340× over-training regime (similar to Llama-3). A deliberate data sub-sampling and quality-filtering plan must be established before ingestion.