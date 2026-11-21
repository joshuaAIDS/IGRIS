# IGRIS Governance Review: Security & Privacy (`SECURITY_PRIVACY`)

**Document Version:** 1.0.0  
**Status:** PENDING HUMAN REVIEW (Unsigned)  
**Governing Role:** `SECURITY_PRIVACY`  
**Governing Standard:** IGRIS Data Privacy, Secret Protection & AI Safety Policy  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Role Responsibilities & Mandate

The **Security & Privacy Lead** possesses sole authority over:
1. Statutory privacy compliance with India's **Digital Personal Data Protection (DPDP) Act 2023** and **GDPR**.
2. Automated Personally Identifiable Information (PII) screening and quarantine (Aadhaar numbers, PAN cards, phone numbers, email addresses, payment cards).
3. Automated cryptographic secret scanning (AWS keys, GitHub personal access tokens, RSA private keys, corporate infrastructure hostnames).
4. Decontamination and benchmark isolation (enforcing zero 13-gram overlap between evaluation benchmarks and training corpora).
5. Societal AI ethics and safety filtering (mitigation of abusive, defamatory, and toxic discourse).

---

## 2. Evidentiary Checklist

Before signing, the Security & Privacy Lead must verify the following artifacts:
- [ ] Automated regex PII test suites in `tests/test_dataset_quality.py` have passed synthetic verification.
- [ ] High-entropy secret scanner configuration targeting Category 7 (Programming Code) is active.
- [ ] 13-gram overlap detection script (`detect_train_eval_leakage`) is verified against HumanEval/MBPP.
- [ ] Social media username pseudonymization filter is operational for Tanglish corpora (`SRC-TG-01`).
- [ ] Mandatory quarantine protocol for flagged PII rows is established in sandbox storage.

---

## 3. Source-by-Source Security & Privacy Evaluation (All 26 Sources)

| Source ID | Dataset Name | PII Risk Level | Security Verdict | Mandatory Security & Privacy Controls |
| :--- | :--- | :---: | :---: | :--- |
| **SRC-TM-01** | IndicCorp v2 (Tamil) | LOW | **CLEARED** | Standard PII regex scan; AI4Bharat adult content filter verified. |
| **SRC-TM-02** | Tamil Wikipedia Dump | LOW | **CLEARED** | Encyclopedic biographies of public figures; standard PII regex scan. |
| **SRC-TM-03** | OSCAR 23.01 Tamil (Filtered) | MEDIUM-HIGH | **QUARANTINE** | Web crawl text carries high risk of personal contact information under DPDP Act. |
| **SRC-EN-01** | Project Gutenberg Open Archive | ZERO | **CLEARED** | Pre-1928 literature contains zero living individuals. Zero PII risk. |
| **SRC-EN-02** | English Wikipedia Dump | LOW | **CLEARED** | Encyclopedic text; standard PII regex scan. |
| **SRC-EN-03** | C4 (Clean Crawled Corpus) | MEDIUM-HIGH | **QUARANTINE** | Web crawl contains personal email and phone numbers; strict scrub mandatory. |
| **SRC-TG-01** | DravidianCodeMix (Tamil-English) | MEDIUM | **CONDITIONAL** | YouTube comments; mandatory pseudonymization of `@username` handles. |
| **SRC-TG-02** | IndicGLUE Tanglish Sentiment | LOW-MEDIUM | **CLEARED** | Curated product/movie reviews; low PII exposure. |
| **SRC-TG-03** | Social Dravidian Sentiment | HIGH | **REJECTED** | Uncurated social media comments; rejected on legal and privacy grounds. |
| **SRC-HI-01** | IndicCorp v2 (Hindi) | LOW | **CLEARED** | Curated news text; standard PII regex scan. |
| **SRC-HI-02** | Hindi Wikipedia Dump | LOW | **CLEARED** | Encyclopedic text; standard PII regex scan. |
| **SRC-HI-03** | IIT Bombay Parallel Corpus | LOW | **REJECTED** | Judicial text has low PII, but rejected on legal non-commercial grounds. |
| **SRC-OI-01** | IndicCorp v2 (Telugu) | LOW | **CLEARED** | Curated news text; standard PII regex scan. |
| **SRC-OI-02** | IndicCorp v2 (Malayalam) | LOW | **CLEARED** | Curated news text; standard PII regex scan. |
| **SRC-OI-03** | IndicCorp v2 (Kannada) | LOW | **CLEARED** | Curated news text; standard PII regex scan. |
| **SRC-ML-01** | FLORES-200 Multilingual | VERY_LOW | **CLEARED** | Professional translations; zero personal data. |
| **SRC-ML-02** | mC4 Multilingual Web Corpus | MEDIUM-HIGH | **QUARANTINE** | Massive uncurated web crawl across 108 languages; requires high-throughput PII scrub. |
| **SRC-CD-01** | The Stack v2 (Permissive Subset) | LOW-MEDIUM | **CONDITIONAL** | Mandatory high-entropy secret scanning to detect hardcoded API keys and tokens. |
| **SRC-CD-02** | HumanEval & MBPP Benchmark | VERY_LOW | **CLEARED (EVAL)** | Zero PII; 13-gram overlap gate must prevent leakage into pre-training corpora. |
| **SRC-TD-01** | Linux Kernel Documentation | LOW | **CLEARED** | Technical maintainer contact information; standard PII scrub. |
| **SRC-TD-02** | IETF RFC Archive (Text) | VERY_LOW | **CLEARED** | Public protocol specifications; author business addresses are public records. |
| **SRC-TD-03** | Python Official Documentation | VERY_LOW | **CLEARED** | Technical documentation; zero personal data. |
| **SRC-CV-01** | DailyDialog Dataset | LOW | **REJECTED** | Low PII, but rejected on legal non-commercial grounds. |
| **SRC-CV-02** | OpenSubtitles Multilingual | MEDIUM | **REJECTED** | Rejected on third-party copyright grounds. |
| **SRC-EM-01** | Unicode 15.1.0 Test Suite | ZERO | **CLEARED** | Character code tables; zero personal data. |
| **SRC-EM-02** | Unicode 15.1.0 Emoji Data Files | ZERO | **CLEARED** | Emoji sequences; zero personal data. |

---

## 4. Security & Privacy Determination & Sign-Off Record

```
[ ] APPROVED — Privacy compliance, secret isolation, and decontamination controls verified.
[ ] REJECTED — Severe unmitigated PII, credential leakage, or benchmark contamination risks.
[ ] CONDITIONAL — Approved subject to automated PII scrubbing and secret scanning quarantine.

Reviewer Name:          __________________________________________________
Reviewer Title:         Security & Privacy Lead
Reviewer Organization:  __________________________________________________
Signature SHA-256:      [PENDING HUMAN REVIEW - DO NOT POPULATE]
Review Date (UTC):      [PENDING HUMAN REVIEW]
Expiration Date (UTC):  [PENDING HUMAN REVIEW]
Security Conditions:    __________________________________________________
```
