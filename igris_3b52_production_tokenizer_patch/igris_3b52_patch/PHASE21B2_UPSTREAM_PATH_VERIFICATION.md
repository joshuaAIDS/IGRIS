# PHASE 21B2 — INDICCORP UPSTREAM PATH VERIFICATION
## Independent Verification of Hugging Face Repository Structure and File Layout

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B2  
**Scope:** Read-Only Upstream Repository Tree Verification  

---

## 1. Upstream Repository and Pinned Revision

- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2` on Hugging Face Hub  
- **Canonical Web URL:** `https://huggingface.co/datasets/ai4bharat/IndicCorpV2`  
- **Pinned Immutable Commit SHA:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`  
- **Authoritative Publisher:** AI4Bharat, Department of Computer Science & Engineering, IIT Madras  
- **Primary Publication:** Doddapaneni et al., *"Towards Leaving No Indic Language Behind: Building Monolingual Corpora, Benchmark and Models for Indic Languages"*, ACL 2023  
- **Storage Architecture:** Hosted via Git LFS / Hugging Face Xet pointer backend  

---

## 2. Upstream File Mapping Corrections

During Phase 21B1, repository mappings were preliminarily described using an assumed BCP-47 / script subfolder hierarchy (`data/<lang>_<Script>/`). Direct inspection of the actual upstream repository tree at commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd` reveals that files are stored as flat text archives directly under the `data/` directory, with high-resource languages (specifically Hindi) sharded into multiple numbered chunks.

```
+-----------+----------+--------------------+-----------------------------+-------------------------------+-----------------------+
| Source ID | Language | Script (ISO 15924) | Verified Upstream Path(s)   | Approximate File Size         | Storage Architecture  |
+-----------+----------+--------------------+-----------------------------+-------------------------------+-----------------------+
| SRC-TM-01 | Tamil    | Tamil (Taml)       | data/ta.txt                 | ~11.8 GB                      | Hugging Face Git LFS  |
| SRC-HI-01 | Hindi    | Devanagari (Deva)  | data/hi-1.txt               | ~26.7 GB                      | Hugging Face Git LFS  |
|           |          |                    | data/hi-2.txt               | ~26.7 GB                      | Hugging Face Git LFS  |
|           |          |                    | data/hi-3.txt (hi-*.txt)    | ~26.7 GB (~80 GB total)       | Hugging Face Git LFS  |
| SRC-OI-01 | Telugu   | Telugu (Telu)      | data/te.txt                 | ~15.8 GB                      | Hugging Face Git LFS  |
| SRC-OI-02 | Malayalam| Malayalam (Mlym)   | data/ml.txt                 | ~26.3 GB                      | Hugging Face Git LFS  |
| SRC-OI-03 | Kannada  | Kannada (Knda)     | data/kn.txt                 | ~19.6 GB                      | Hugging Face Git LFS  |
| SRC-OI-04 | Bengali  | Bengali (Beng)     | data/bn.txt                 | ~16.0 GB                      | Hugging Face Git LFS  |
| SRC-OI-05 | Gujarati | Gujarati (Gujr)    | data/gu.txt                 | ~14.1 GB                      | Hugging Face Git LFS  |
+-----------+----------+--------------------+-----------------------------+-------------------------------+-----------------------+
```

### Detailed Path Notes:
1. **Tamil (`SRC-TM-01`):** The exact verified upstream artifact path is `data/ta.txt` (single uncompressed text archive ~11.8 GB).
2. **Hindi (`SRC-HI-01`):** Due to the massive volume of Hindi web text, the upstream corpus is partitioned into multiple chunks matching the glob `data/hi-*.txt` (specifically `data/hi-1.txt`, `data/hi-2.txt`, `data/hi-3.txt`), totaling roughly ~80 GB.
3. **Telugu (`SRC-OI-01`):** The exact verified upstream path is `data/te.txt` (~15.8 GB).
4. **Malayalam (`SRC-OI-02`):** The exact verified upstream path is `data/ml.txt` (~26.3 GB).
5. **Kannada (`SRC-OI-03`):** The exact verified upstream path is `data/kn.txt` (~19.6 GB).
6. **Bengali (`SRC-OI-04`):** The exact verified upstream path is `data/bn.txt` (~16.0 GB).
7. **Gujarati (`SRC-OI-05`):** The exact verified upstream path is `data/gu.txt` (~14.1 GB).

---

## 3. Governance Boundaries Maintained

- **Zero Production Bytes Acquired:** All file mappings and sizes were verified via read-only repository tree inspection and metadata evaluation. No corpus contents were downloaded.
- **Production Ingress Locked:** The `SecureAcquisitionEngine` ingress gate remains strictly locked under `Default-Deny`.
- **Zero Sources Authorized:** These corrections prepare accurate technical records; no sources are authorized for ingress by this document.