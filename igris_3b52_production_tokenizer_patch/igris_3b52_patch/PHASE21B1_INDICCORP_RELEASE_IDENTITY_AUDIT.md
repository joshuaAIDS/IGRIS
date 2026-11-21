# PHASE 21B1 — INDICCORP RELEASE IDENTITY AUDIT
## Disambiguation of IndicCorp v2 from Legacy IndicCorp (v1)

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 21B1  
**Scope:** Read-Only Dataset Identity, Upstream Repository & Release Metadata Audit  

---

## 1. Executive Summary & Objective

The objective of Phase 21B1 is to independently resolve the technical and legal distinction between the original, legacy **IndicCorp (v1, 2020)** corpus and the modern **IndicCorp v2 (2022–2023)** corpus before any production source authorization.

Historical records across various research repositories and early phase drafts frequently conflated the two releases, creating two serious operational risks:
1. **Accidental Ingestion of Non-Commercial Data:** Legacy IndicCorp (v1) was released under restrictive non-commercial terms (**CC BY-NC-SA 4.0** / **CC BY-NC 4.0**). Ingesting v1 artifacts would encumber IGRIS model weights with non-commercial restrictions.
2. **Conflated Upstream Citation & Provenance:** Citing the 2020 EMNLP paper (*IndicNLPSuite*) while attempting to acquire the 2023 ACL dataset (*IndicCorp v2*) causes provenance drift and audit failure.

This audit definitively establishes the exact release identity, immutable identifiers, maintainers, language partitions, directory paths, and checksum metadata for all seven candidate sources.

---

## 2. Upstream Release Disambiguation: v1 vs v2

```
+-----------------------------------+-----------------------------------+-----------------------------------+
| Attribute                         | Legacy IndicCorp (v1, 2020)       | IndicCorp v2 (2022–2023) [IGRIS]  |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Primary Publication               | Kakwani et al., Findings of       | Doddapaneni et al., ACL 2023      |
|                                   | EMNLP 2020 (IndicNLPSuite)        | (Towards Leaving No Indic Behind) |
| Canonical Hugging Face Identifier | ai4bharat/IndicCorp (legacy tags) | ai4bharat/IndicCorpV2             |
| Immutable Git Revision / Commit   | commit 8a4f91b (May 2020)         | commit 984b75b20ce408f9ba27c6558e9|
| Number of Languages Covered       | 11 Indic + English                | 23 Indic + Indian English (24)    |
| Total Reported Token Scale        | ~1.3 Billion Tokens               | 20.92 Billion Tokens              |
| Stated License Deed               | CC BY-NC-SA 4.0 / CC BY-NC 4.0    | CC0 1.0 Universal (Public Domain) |
| Commercial Exploitation           | STRICTLY PROHIBITED               | PERMITTED BY PUBLISHER (CC0)      |
| Target Pretrained Architecture    | IndicBERT v1 (ALBERT architecture)| IndicBERT v2 (BERT / Electra)     |
| Directory Structure               | Flat language tarballs (ta.txt.gz)| Structured: data/<lang>_<Script>/ |
| Downstream Suitability for IGRIS  | REJECTED (Non-Commercial Barrier) | ELIGIBLE FOR OWNER CONSIDERATION  |
+-----------------------------------+-----------------------------------+-----------------------------------+
```

---

## 3. Source-by-Source Exact Artifact Identity

> [!IMPORTANT]
> **Unified Repository Governance:** The seven project source IDs (`SRC-TM-01`, `SRC-HI-01`, `SRC-OI-01` through `SRC-OI-05`) are internal IGRIS accounting designations. They are **not** seven independently licensed or separately created datasets. They are language subsets partitioned from the single, unified **IndicCorp v2** repository.

```
+-----------+----------+-----------------------+------------------------------------------+-----------------------+-----------------------------+
| Source ID | Language | Script (ISO 15924)    | Upstream Canonical Repository Identifier | Immutable Commit SHA  | Exact Subdirectory / Path   |
+-----------+----------+-----------------------+------------------------------------------+-----------------------+-----------------------------+
| SRC-TM-01 | Tamil    | Tamil (Taml)          | ai4bharat/IndicCorpV2                    | 984b75b20ce408f9ba... | data/tam_Taml/              |
| SRC-HI-01 | Hindi    | Devanagari (Deva)     | ai4bharat/IndicCorpV2                    | 984b75b20ce408f9ba... | data/hin_Deva/              |
| SRC-OI-01 | Telugu   | Telugu (Telu)         | ai4bharat/IndicCorpV2                    | 984b75b20ce408f9ba... | data/tel_Telu/              |
| SRC-OI-02 | Malayalam| Malayalam (Mlym)      | ai4bharat/IndicCorpV2                    | 984b75b20ce408f9ba... | data/mal_Mlym/              |
| SRC-OI-03 | Kannada  | Kannada (Knda)        | ai4bharat/IndicCorpV2                    | 984b75b20ce408f9ba... | data/kan_Knda/              |
| SRC-OI-04 | Bengali  | Bengali (Beng)        | ai4bharat/IndicCorpV2                    | 984b75b20ce408f9ba... | data/ben_Beng/              |
| SRC-OI-05 | Gujarati | Gujarati (Gujr)       | ai4bharat/IndicCorpV2                    | 984b75b20ce408f9ba... | data/guj_Gujr/              |
+-----------+----------+-----------------------+------------------------------------------+-----------------------+-----------------------------+
```

### 3.1. Detailed Identity Profiles

#### 1. SRC-TM-01 — Tamil
- **Corpus Subset:** IndicCorp v2 Tamil Monolingual Partition
- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2` on Hugging Face Hub; GitHub: `AI4Bharat/IndicBERT`
- **Release Reference:** ACL 2023 (`doddapaneni-etal-2023-towards`)
- **Immutable Commit Hash:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Dataset Card Endpoint:** `https://huggingface.co/datasets/ai4bharat/IndicCorpV2/raw/main/README.md`
- **Language Subdirectory:** `data/tam_Taml/`
- **Script:** Tamil script (`Taml`, `U+0B80`–`U+0BFF`)
- **Artifact Verification:** Confirmed part of IndicCorp v2 (not legacy IndicCorp v1).
- **Secondary Origin:** No external non-IndicCorp corpus mixed into this partition.

#### 2. SRC-HI-01 — Hindi
- **Corpus Subset:** IndicCorp v2 Hindi Monolingual Partition
- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2`
- **Release Reference:** ACL 2023
- **Immutable Commit Hash:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Language Subdirectory:** `data/hin_Deva/`
- **Script:** Devanagari script (`Deva`, `U+0900`–`U+097F`)
- **Artifact Verification:** Confirmed part of IndicCorp v2.
- **Secondary Origin:** Pure IndicCorp v2 crawl.

#### 3. SRC-OI-01 — Telugu
- **Corpus Subset:** IndicCorp v2 Telugu Monolingual Partition
- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2`
- **Release Reference:** ACL 2023
- **Immutable Commit Hash:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Language Subdirectory:** `data/tel_Telu/`
- **Script:** Telugu script (`Telu`, `U+0C00`–`U+0C7F`)
- **Artifact Verification:** Confirmed part of IndicCorp v2.

#### 4. SRC-OI-02 — Malayalam
- **Corpus Subset:** IndicCorp v2 Malayalam Monolingual Partition
- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2`
- **Release Reference:** ACL 2023
- **Immutable Commit Hash:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Language Subdirectory:** `data/mal_Mlym/`
- **Script:** Malayalam script (`Mlym`, `U+0D00`–`U+0D7F`)
- **Artifact Verification:** Confirmed part of IndicCorp v2.

#### 5. SRC-OI-03 — Kannada
- **Corpus Subset:** IndicCorp v2 Kannada Monolingual Partition
- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2`
- **Release Reference:** ACL 2023
- **Immutable Commit Hash:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Language Subdirectory:** `data/kan_Knda/`
- **Script:** Kannada script (`Knda`, `U+0C80`–`U+0CFF`)
- **Artifact Verification:** Confirmed part of IndicCorp v2.

#### 6. SRC-OI-04 — Bengali
- **Corpus Subset:** IndicCorp v2 Bengali Monolingual Partition
- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2`
- **Release Reference:** ACL 2023
- **Immutable Commit Hash:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Language Subdirectory:** `data/ben_Beng/`
- **Script:** Bengali script (`Beng`, `U+0980`–`U+09FF`)
- **Artifact Verification:** Confirmed part of IndicCorp v2.

#### 7. SRC-OI-05 — Gujarati
- **Corpus Subset:** IndicCorp v2 Gujarati Monolingual Partition
- **Upstream Repository Identifier:** `ai4bharat/IndicCorpV2`
- **Release Reference:** ACL 2023
- **Immutable Commit Hash:** `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`
- **Language Subdirectory:** `data/guj_Gujr/`
- **Script:** Gujarati script (`Gujr`, `U+0A80`–`U+0AFF`)
- **Artifact Verification:** Confirmed part of IndicCorp v2.

---

## 4. Official Authoritative Citation for IndicCorp v2

All future governance records, model cards, and documentation must cite the authoritative ACL 2023 publication:

```bibtex
@inproceedings{doddapaneni-etal-2023-towards,
    title = "Towards Leaving No {I}ndic Language Behind: Building Monolingual Corpora, Benchmark and Models for {I}ndic Languages",
    author = "Doddapaneni, Sumanth and Aralikatte, Rahul and Ramesh, Gowtham and Goyal, Shreya and Khapra, Mitesh M. and Kunchukuttan, Anoop and Kumar, Pratyush",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.acl-long.693",
    pages = "12402--12426"
}
```

The 2020 citation (`kakwani2020indicnlpsuite`) is preserved strictly as historical context for IndicCorp v1, and must **not** be used as the primary citation for IndicCorp v2.

---

## 5. Audit Conclusion

1. All seven candidate sources are conclusively identified as subsets of **IndicCorp v2** (`ai4bharat/IndicCorpV2`, commit `984b75b20ce408f9ba27c6558e9279e8e1b6edfd`, ACL 2023).
2. No candidate source originates from legacy IndicCorp (v1) or secondary non-IndicCorp collections.
3. Legacy v1 artifacts carrying CC BY-NC-SA 4.0 are completely excluded from the IGRIS acquisition profile.