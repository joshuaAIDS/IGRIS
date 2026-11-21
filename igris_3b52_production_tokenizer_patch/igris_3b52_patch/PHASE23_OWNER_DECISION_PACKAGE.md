# PHASE 23 — PROJECT OWNER DECISION DOSSIER
## Source Authorization Decision Package for Tamil, English, and Tanglish Pretraining

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Reviewer:** Sole Developer / Project Owner  
**Date:** 2026-11-18  
**Phase:** Phase 23  
**Status:** PRESENTED FOR OWNER DETERMINATION  

---

## 1. Scope Narrowing Formal Record

The Project Owner has formally narrowed the IGRIS pretraining language scope to:
1. **Tamil (`ta`)**
2. **English (`en`)**
3. **Tanglish (`ta-Latn` / code-mixed)**

All other languages (Hindi, Telugu, Malayalam, Kannada, Bengali, Gujarati, and multilingual mixtures) are **OUT_OF_SCOPE** and permanently barred from pretraining.

---

## 2. Decision Summary by Source Status

```
+------------------------------------+--------------------------+--------------------------------------------------------+
| Classification Status Category     | Source Count             | Source Identifiers Included                            |
+------------------------------------+--------------------------+--------------------------------------------------------+
| **ELIGIBLE_FOR_OWNER_REVIEW**      | **6 Sources**            | SRC-EN-01, SRC-TD-02, SRC-TD-03, SRC-CV-03,            |
|                                    |                          | SRC-CV-05, SRC-CV-06                                   |
+------------------------------------+--------------------------+--------------------------------------------------------+
| **PENDING_LEGAL_REVIEW**           | **8 Sources**            | SRC-TM-01, SRC-TM-02, SRC-TM-03, SRC-TG-01,            |
|                                    |                          | SRC-TG-02, SRC-EN-02, SRC-EN-03, SRC-TD-01             |
+------------------------------------+--------------------------+--------------------------------------------------------+
| **REJECTED**                       | **3 Sources**            | SRC-CV-01 (NC), SRC-CV-04 (Leakage), SRC-TG-03 (NC)    |
+------------------------------------+--------------------------+--------------------------------------------------------+
| **OUT_OF_SCOPE**                   | **15 Sources**           | SRC-HI-01, SRC-HI-02, SRC-HI-03, SRC-OI-01,            |
|                                    |                          | SRC-OI-02, SRC-OI-03, SRC-OI-04, SRC-OI-05,            |
|                                    |                          | SRC-CD-01, SRC-CD-02, SRC-EM-01, SRC-EM-02,            |
|                                    |                          | SRC-ML-01, SRC-ML-02, SRC-CV-02                        |
+------------------------------------+--------------------------+--------------------------------------------------------+
| **APPROVED_FOR_ACQUISITION**       | **0 Sources**            | Zero sources authorized; Ingress Gate remains LOCKED   |
+------------------------------------+--------------------------+--------------------------------------------------------+
| **TOTAL CATALOG SOURCES**          | **32 Sources**           | 100% Accounted with Zero Overlap                       |
+------------------------------------+--------------------------+--------------------------------------------------------+
```

---

## 3. Recommended Owner Decision Actions

### Action Item 1: Authorize English Public Domain & Permissive Sources (Phase 24 Candidates)
The following 6 English sources possess clean provenance, verified permissive licenses (Public Domain, Apache-2.0, PSF-2.0, IETF Trust), and zero underlying third-party rights conflicts:
1. `SRC-EN-01` (Project Gutenberg Open Archive)
2. `SRC-TD-02` (IETF RFC Archive Text)
3. `SRC-TD-03` (Python Official Documentation)
4. `SRC-CV-03` (OpenAssistant Conversations OASST1 - English filtered)
5. `SRC-CV-05` (MultiWOZ 2.4 Task Dialogue)
6. `SRC-CV-06` (Project Gutenberg Theatrical Dialogue)

*Recommendation:* The Project Owner may authorize these 6 sources for controlled pilot acquisition in Phase 24.

### Action Item 2: Retain Legal Hold on Tamil & Tanglish Sources
The Tamil sources (`SRC-TM-01`, `SRC-TM-02`, `SRC-TM-03`) and Tanglish sources (`SRC-TG-01`, `SRC-TG-02`) carry underlying fair dealing, ShareAlike copyleft, or platform terms risks.
*Recommendation:* Retain in **`PENDING_LEGAL_REVIEW`** status until formal legal counsel opinion is obtained. Do not unlock ingress for these sources during Phase 23.
