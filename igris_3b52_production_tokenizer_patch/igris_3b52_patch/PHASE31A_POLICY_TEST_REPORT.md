# PHASE 31A — POLICY TEST REPORT

**Project:** IGRIS — Multilingual Decoder-Only Transformer  
**Operating Model:** `SOLO_DEVELOPER_OWNER_REVIEW`  
**Test Harness:** `scripts/phase31a_policy_validator.py`  
**Execution Date:** 2026-11-20  
**Test Mode:** STRICTLY SYNTHETIC FIXTURES (Zero Production Ingress)  

---

## 1. Executive Summary

The Phase 31A policy test harness was executed to validate the owner's policy specifications across benchmark contamination, privacy masking, and language routing.

* **Benchmark Policy Tests:** 7/7 PASSED (**100%**).
* **Privacy Masking Tests:** 9/9 PASSED (**100%**).
* **Language Routing Tests:** 8/8 PASSED (**100%**).
* **Overall Policy Test Suite:** 24/24 PASSED (**100%**).

---

## 2. Detailed Test Results

### 2.1 Benchmark Similarity Policy Tests
| Test ID | Scenario | Input Similarity | Expected Status | Actual Result | Auto-Reject? | Status |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| `BM-TEST-01` | Similarity below 0.70 | 0.45 | `NOT_REVIEWED` | `NOT_REVIEWED` | False | **PASS** |
| `BM-TEST-02` | Similarity exactly 0.70 | 0.70 | `MANUAL_REVIEW_REQUIRED` | `MANUAL_REVIEW_REQUIRED` (MODERATE) | False | **PASS** |
| `BM-TEST-03` | Similarity between 0.70 and 0.85 | 0.78 | `MANUAL_REVIEW_REQUIRED` | `MANUAL_REVIEW_REQUIRED` (MODERATE) | False | **PASS** |
| `BM-TEST-04` | Similarity exactly 0.85 | 0.85 | `MANUAL_REVIEW_REQUIRED` | `MANUAL_REVIEW_REQUIRED` (HIGH) | False | **PASS** |
| `BM-TEST-05` | Similarity above 0.85 | 0.94 | `MANUAL_REVIEW_REQUIRED` | `MANUAL_REVIEW_REQUIRED` (HIGH) | False | **PASS** |
| `BM-TEST-06` | Common programming idiom | 0.88 | `NOT_REVIEWED` | `NOT_REVIEWED` (AST Suppressed) | False | **PASS** |
| `BM-TEST-07` | Missing benchmark reference | 0.00 | `NOT_REVIEWED` | `NOT_REVIEWED` | False | **PASS** |

*Verification Finding:* Neither the 0.70 nor the 0.85 threshold triggered automated rejection. All flagged items routed to manual review.

---

### 2.2 Privacy Masking Policy Tests
| Test ID | Scenario | Target Entity | Expected Behavior | Actual Behavior | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `PRIV-TEST-01` | Single email | `alex.smith@python.org` | Masked to `[EMAIL_REDACTED]` | Clean replacement; raw email unlogged | **PASS** |
| `PRIV-TEST-02` | Multiple emails | 2 emails | Both masked to `[EMAIL_REDACTED]` | 2 replacements in reverse offset order | **PASS** |
| `PRIV-TEST-03` | Phone number | `+1-206-555-0199` | Masked to `[PHONE_REDACTED]` | Clean replacement; entity hashed | **PASS** |
| `PRIV-TEST-04` | Email & phone in same text | 1 email, 1 phone | Both masked | Both placeholders present | **PASS** |
| `PRIV-TEST-05` | False-positive code syntax | `A @ B`, `@classmethod` | Preserved untouched | 0 replacements; syntax intact | **PASS** |
| `PRIV-TEST-06` | Unicode text surrounding PII | Tamil characters + email | NFC preserved; combining marks intact | Tamil text uncorrupted; email masked | **PASS** |
| `PRIV-TEST-07` | Overlapping matches | Adjacent emails | Replaced without offset drift | 2 clean replacements | **PASS** |
| `PRIV-TEST-08` | Uncertain PII | `author_handle_9942a` | Held for manual review | `MANUAL_REVIEW_REQUIRED` | **PASS** |
| `PRIV-TEST-09` | Sensitive health narrative | Unstructured depression disclosure | Held for manual review | `MANUAL_REVIEW_REQUIRED` | **PASS** |

---

### 2.3 OASST1 Language Routing Policy Tests
| Test ID | Scenario | Text Excerpt | Metadata Lang | Routing Decision | Status |
| :--- | :--- | :--- | :---: | :--- | :---: |
| `LANG-TEST-01` | Standard English | Gaussian quadrature... | `en` | `ADMIT_ENGLISH_CANDIDATE` | **PASS** |
| `LANG-TEST-02` | Native Tamil script | தமிழ் மொழி... | `ta` | `ROUTE_TAMIL` | **PASS** |
| `LANG-TEST-03` | Romanized Tamil | enna bro romba late... | `ta` | `ROUTE_TANGLISH` | **PASS** |
| `LANG-TEST-04` | Code-switching | very complex algorithm bro... | `en` | `REJECT_LANG_MISMATCH` | **PASS** |
| `LANG-TEST-05` | Discourse marker (*da*) | loss is dropping very rapidly da | `en` | `REJECT_LANG_MISMATCH` | **PASS** |
| `LANG-TEST-06` | Mixed-language turn | seri namba adutha function... | `en` | `REJECT_LANG_MISMATCH` | **PASS** |
| `LANG-TEST-07` | Incorrect metadata | idhu romba mukkiyamaana... | `en` | `REJECT_LANG_MISMATCH` | **PASS** |
| `LANG-TEST-08` | Low confidence string | zzz qqq xxx | `en` | `HOLD_FOR_MANUAL_REVIEW` | **PASS** |
