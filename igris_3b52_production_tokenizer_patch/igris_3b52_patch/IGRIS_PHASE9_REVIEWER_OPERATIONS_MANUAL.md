# IGRIS Phase 9: External Reviewer Operations & Onboarding Manual

**Project**: IGRIS Multilingual Decoder-Only Transformer  
**Active Patch**: `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Document ID**: `IGRIS-MANUAL-PHASE9-REV-OPS`  
**Classification**: OFFICIAL GOVERNANCE OPERATIONAL STANDARD  
**Effective Date**: 2026-11-17  
**Governance Authority**: IGRIS Steering Committee  
**Target Audience**: Designated Human Reviewers, Security Officers, Legal Counsel, and Data Engineers  

---

## 1. Executive Overview & Governance Charter

This manual defines the mandatory operational procedures, professional qualification criteria, independence safeguards, and cryptographic onboarding requirements for the four designated human governance authorities of Project IGRIS.

Under the IGRIS Architectural Charter:
- **Zero Automated Approvals**: No software agent, script, heuristic, or AI model possesses the authority to grant dataset ingress or model training approvals.
- **Strict Separation of Duties**: The four governance roles must be occupied by four separate, authenticated physical human beings. Dual-role assignment, proxy voting, or consolidated authority is strictly prohibited.
- **Fail-Closed Unanimous Quorum**: Production data ingress requires unanimous approval (4-of-4) from all designated roles. A single negative veto (`REJECT` or `REQUEST_CHANGES`) permanently halts production pipeline staging for the affected source.
- **Default-Deny Ingress Gate**: The production dataset pipeline remains **`LOCKED`** until external human onboarding and cryptographic reviews are completely finalized.

```
+-----------------------------------------------------------------------------------------+
|                                IGRIS GOVERNANCE MANDATE                                 |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|   +-----------------------+                         +-------------------------------+   |
|   |   DATA_CUSTODIAN      |                         |       LEGAL_GOVERNANCE        |   |
|   |  - Archive Checksums  |                         |  - Indian Copyright Act Sec 22|   |
|   |  - UTF-8 Losslessness |                         |  - Life+60 / Life+70 Rules    |   |
|   |  - Unicode 15.1.0 NFC |                         |  - License Class Compliance   |   |
|   +-----------+-----------+                         +---------------+---------------+   |
|               |                                                     |                   |
|               +-------------------------+---------------------------+                   |
|                                         |                                               |
|                                         v                                               |
|                      +-------------------------------------+                            |
|                      |   UNANIMOUS 4-OF-4 QUORUM CONSENSUS |                            |
|                      |      (Single Veto Blocks Pipeline)  |                            |
|                      +-------------------------------------+                            |
|                                         ^                                               |
|               +-------------------------+---------------------------+                   |
|               |                                                     |                   |
|   +-----------+-----------+                         +---------------+---------------+   |
|   |   SECURITY_PRIVACY    |                         |        CHIEF_ARCHITECT        |   |
|   |  - Direct/Indirect PII|                         |  - Vocabulary Balance (10 Cat)|   |
|   |  - Regex / Toxic Gate |                         |  - Structural Tokens (0-11)   |   |
|   |  - Key Registry / CRL |                         |  - Preference Pair Isolation  |   |
|   +-----------------------+                         +-------------------------------+   |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Reviewer Appointment Process

The appointment of governance reviewers is conducted exclusively through the IGRIS Steering Committee. The operational workflow consists of five formal stages:

```
[ Stage 1: Nomination & Candidate Vetting ]
                     |
                     v
[ Stage 2: Qualification Audit & Certification Review ]
                     |
                     v
[ Stage 3: Conflict of Interest (COI) Declaration & Independence Check ]
                     |
                     v
[ Stage 4: Formal Seat Appointment by Steering Committee ]
                     |
                     v
[ Stage 5: Reviewer Acceptance Record & Legal Attestation ]
```

### 2.1 Role-Specific Qualification Criteria

Every appointee must satisfy rigorous professional standards demonstrated through verifiable credentials and domain experience:

#### Role 1: `DATA_CUSTODIAN` (Seat ID: `APPT-2026-DC-01`)
- **Professional Background**: Minimum 8 years in large-scale data engineering, data warehousing, or machine learning data infrastructure.
- **Required Expertise**:
  - Deep technical mastery of Unicode Standard 15.1.0, canonical normalization forms (NFC/NFD), and non-Latin script encoding properties (specifically Tamil, Devanagari, Telugu, Malayalam, Bengali, Gujarati).
  - Practical expertise with binary encoding diagnostics, character set conversions, and byte-level validation (lossless UTF-8, zero `\uFFFD` tolerances).
  - Proven experience managing multi-terabyte staging environments, SHA-256 archive checksum verification, and write-once quarantine sandboxes.
  - Familiarity with automated text sanitization algorithms, including header/footer stripping and trademark boundary removal (e.g., Project Gutenberg license headers).

#### Role 2: `LEGAL_GOVERNANCE` (Seat ID: `APPT-2026-LG-01`)
- **Professional Background**: Licensed Attorney / Qualified Legal Counsel specializing in Intellectual Property, Data Law, and Artificial Intelligence Governance.
- **Required Expertise**:
  - Comprehensive knowledge of the Indian Copyright Act, 1957, with specialized emphasis on Section 22 (statutory Life+60 rule calculated from the calendar year following author decease, establishing calendar year <=1965 for 2026), Section 52 (fair dealing doctrine), and Section 57 (author moral rights).
  - Mastery of international copyright harmonizations: UK/EU Duration Directive (Life+70, establishing calendar year <=1955), US Copyright Act (Title 17, 95-year corporate/publication rule), and the Berne Convention.
  - Definitive legal understanding of open source and open data license classifications: CC0 1.0, CC-BY 4.0, CC-BY-SA 4.0, Apache-2.0, MIT, ODC-By 1.0, GPL family (copyleft boundaries), and non-commercial restrictions (`-NC` / Research-Only prohibitions).
  - Authority to rule on model training as an adaptation or derivative work under applicable jurisdictional statutes.

#### Role 3: `SECURITY_PRIVACY` (Seat ID: `APPT-2026-SP-01`)
- **Professional Background**: Certified Information Systems Security Professional (CISSP), Certified Information Privacy Professional (CIPP/E or CIPP/US), or equivalent corporate security director.
- **Required Expertise**:
  - Direct and indirect Personally Identifiable Information (PII) identification across diverse global datasets (names, government IDs, phone numbers, email addresses, physical locations, IP addresses).
  - Evaluation of cryptographic sanitization pipelines, differential privacy mechanisms, and automated regex-based PII screening filters.
  - Cryptographic key management infrastructure: FIPS 140-2 Level 3 hardware security modules, public-key infrastructure (PKI), Certificate Revocation Lists (CRL), and digital signature verification protocols.
  - Security threat modeling against dataset poisoning, backdoors, adversarial prompt injection, and red-team prompt extraction attacks.

#### Role 4: `CHIEF_ARCHITECT` (Seat ID: `APPT-2026-CA-01`)
- **Professional Background**: Principal AI Architect / Foundation Model Technical Director with at least 10 years of experience in deep learning, natural language processing, and transformer architecture engineering.
- **Required Expertise**:
  - Intimate knowledge of the IGRIS model specifications: Decoder-Only Multilingual Transformer, 2048 context length, 512 hidden dimension, 16 layers, 8 query attention heads, 4 key-value heads (Grouped-Query Attention, GQA ratio 2:1), 2048 feed-forward dimension, and exactly 32,768 vocabulary entries.
  - Tokenization mathematics and sentencepiece mechanics (BPE / Unigram), specifically the 12 pinned structural tokens at IDs 0–11:
    - ID 0: `<|pad|>`
    - ID 1: `<|begin_of_text|>`
    - ID 2: `<|end_of_text|>`
    - ID 3: `<think>`
    - ID 4: `</think>`
    - ID 5: `<action>`
    - ID 6: `</action>`
    - ID 7: `<action_result>`
    - ID 8: `</action_result>`
    - ID 9: `<|system|>`
    - ID 10: `<|user|>`
    - ID 11: `<|assistant|>`
  - Domain balance control across the 10 canonical corpus categories: Tamil, English, Tanglish, Hindi, Other Indian Languages, Conversational, Code, Mathematical/Reasoning, Emoji/Structural, and Evaluation/Red-Team.
  - Architectural policy enforcement: 0% synthetic text policy for vocabulary induction, and strict isolation of preference pairs (`SRC-CV-04` Anthropic HH-RLHF) from pre-training tokenization corpora.

---

## 3. Conflict of Interest & Independence Mandate

### 3.1 Independence Requirements
To preserve absolute integrity and prevent bias:
1. **Four Distinct Individuals**: No individual may hold more than one governance seat simultaneously. Any attempt to combine roles automatically invalidates all affected votes.
2. **Executive Non-Interference**: Neither the Project Lead, Corporate Officers, nor external investors possess the authority to overrule, compel, or reverse a governance reviewer's negative decision.
3. **Absence of Pipeline Quota Incentives**: Reviewers are evaluated exclusively on audit diligence and risk containment. No reviewer's compensation, retention, or performance rating may be tied to dataset volume, training speed, or model deployment deadlines.

### 3.2 Conflict of Interest (COI) Declaration
Prior to seat appointment, each prospective reviewer must complete and sign the **IGRIS Governance Conflict of Interest Declaration**:

```
+-----------------------------------------------------------------------------------------+
|                  IGRIS GOVERNANCE CONFLICT OF INTEREST DECLARATION                      |
+-----------------------------------------------------------------------------------------+
| Candidate Name        : _______________________________________________________________ |
| Candidate ID / Title  : _______________________________________________________________ |
| Nominated Seat        : [ ] DATA_CUSTODIAN          [ ] LEGAL_GOVERNANCE                |
|                         [ ] SECURITY_PRIVACY        [ ] CHIEF_ARCHITECT                 |
+-----------------------------------------------------------------------------------------+
| DECLARATION ITEMS (Check all that apply):                                               |
|                                                                                         |
| [ ] 1. AFFILIATION WITH DATASET PROVIDERS: Neither I nor any immediate family member    |
|        holds a financial, employment, or advisory relationship with any entity providing|
|        candidate datasets listed in the IGRIS Source Catalog.                           |
|                                                                                         |
| [ ] 2. THIRD-PARTY IP INTERESTS: I do not hold any proprietary, copyright, or patent   |
|        interest in the content of the candidate datasets under review.                  |
|                                                                                         |
| [ ] 3. COMMERCIAL BIAS: I have no financial interest in commercial entities whose     |
|        intellectual property or commercial software may compete with or be impacted by  |
|        the models trained from these datasets.                                          |
|                                                                                         |
| [ ] 4. RECUSAL DUTY: I agree to immediately recuse myself from reviewing any specific  |
|        source if a conflict arises during the governance review lifecycle.              |
|                                                                                         |
| Signature: ____________________________________     Date: _____________________________ |
+-----------------------------------------------------------------------------------------+
```

---

## 4. Responsibility Boundaries & Decision Authority

Each reviewer operates strictly within their jurisdictional boundary:

| Governance Role | Mandatory Scope of Authority | Out-of-Scope (Ultra Vires) Actions |
| :--- | :--- | :--- |
| **`DATA_CUSTODIAN`** | SHA-256 archive checksums, upstream repository URLs, UTF-8 losslessness, Unicode 15.1.0 normalization, quarantine isolation, Gutenberg header removal | Granting copyright clearance, approving PII exceptions, modifying model vocabulary sizing |
| **`LEGAL_GOVERNANCE`** | Indian Copyright Act Sec 22 (Life+60), UK/EU Life+70, US Title 17, 9-class license deeds, non-commercial terms, fair dealing limits | Verifying technical encoding formats, assessing token fertility metrics, managing hardware HSMs |
| **`SECURITY_PRIVACY`** | PII detection and classification, regex filter rules, red-team prompt risk, hardware key registration, Certificate Revocation List (CRL) | Redefining copyright terms, modifying architectural attention mechanisms, changing dataset URLs |
| **`CHIEF_ARCHITECT`** | Tokenizer vocabulary balance, 12 structural token IDs (0–11), 0% synthetic text rule, preference pair isolation, downstream perplexity | Overruling legal copyright determinations, overriding PII security blocks, bypassing quarantine |

---

## 5. Reviewer Onboarding & Cryptographic Key Provisioning

Once appointed, each reviewer must execute the four-step cryptographic onboarding workflow:

```
[ Step 1: In-Person / Cryptographic Identity Verification ]
                            |
                            v
[ Step 2: FIPS 140-2 Level 3 Hardware Security Token Provisioning ]
                            |
                            v
[ Step 3: Certificate Signing Request (CSR) & Public Key Registration ]
                            |
                            v
[ Step 4: Governance Key Registry Activation & CRL Validation ]
```

### 5.1 Identity Verification Requirements
Identity verification must be performed through verified enterprise multi-factor credentials:
1. Presentation of government-issued photo identification (Passport or National ID).
2. Verification against corporate identity provider (enterprise SSO / smart card).
3. Attestation by two existing members of the IGRIS Steering Committee.

### 5.2 Hardware Security Token Requirements
All cryptographic operations must be performed using dedicated hardware:
- **Approved Hardware**: FIPS 140-2 Level 3 certified USB cryptographic tokens (e.g., YubiKey 5 Series FIPS, Nitrokey Pro) or dedicated enterprise Hardware Security Modules (HSM / TPM 2.0).
- **Entropy Requirement**: Minimum 256 bits of true physical random entropy.
- **Key Algorithms**: HMAC-SHA256 with 256-bit symmetric hardware secret or Ed25519 (Edwards-curve Digital Signature Algorithm).
- **Non-Exportability**: The private key must be generated directly on the hardware token with the non-exportable flag set (`never_extractable = true`). Software file exports or plaintext disk storage are strictly prohibited.

### 5.3 Public-Key Registration Procedure
1. Reviewer generates key pair within the hardware enclave.
2. Reviewer extracts public key certificate and submits Certificate Signing Request (CSR) to the Security Officer.
3. Security Officer verifies fingerprint out-of-band and registers the key in `KeyRegistry`:
   ```python
   record = KeyRecord(
       key_id="KEY-DATA_CUSTODIAN-XXXX",
       role=SignOffRole.DATA_CUSTODIAN,
       secret_key=hardware_attested_public_key,
       is_revoked=False,
       created_at="2026-11-17T00:00:00Z",
       expires_at="2027-11-17T00:00:00Z",
   )
   key_registry.register_key(record)
   ```
4. The key record is bound exclusively to the designated role. Any attempt to use the key for another role results in instant cryptographic rejection.

### 5.4 Key Revocation & Certificate Revocation List (CRL) Protocol
- **Revocation Triggers**:
  - Loss, theft, or suspected compromise of hardware security token.
  - Reviewer departure, reassignment, or recusal.
  - Cryptographic anomaly or unauthorized signing attempt.
- **Revocation SLA**: Revocation must be committed to the `KeyRegistry` within **60 minutes** of notification.
- **Revocation Effect**: All subsequent submission attempts using a revoked key fail automatically with `KeyRevokedError`.

---

## 6. Reviewer Package Distribution Architecture

Every reviewer receives a structured, role-specific distribution package consisting of:
1. **Role-Specific Human Review Dossier** (`REVIEW_<ROLE>_V2.md`).
2. **Complete Dataset Source Catalog** (`DATASET_SOURCE_CATALOG_V3.csv`).
3. **License Evidence Dossier** (`DATASET_LICENSE_EVIDENCE_V2.csv`).
4. **Source Human Review Matrix** (`SOURCE_HUMAN_REVIEW_MATRIX.csv`).
5. **Technical Data Eligibility Matrix** (`TOKENIZER_DATA_ELIGIBILITY_MATRIX.md`).
6. **Pipeline Authorization Matrix** (`PIPELINE_AUTHORIZATION_MATRIX_V2.csv`).
7. **Security Gap Register & PII Assessment** (`SECURITY_GAP_REGISTER.md`).
8. **India Copyright Law Legal Review** (`INDIA_COPYRIGHT_REVIEW.md`).

Reviewers review their assigned candidate sources, record line-item decisions, and prepare their cryptographic submission.

---

## 7. Appointment Acceptance Form Template

Below is the formal acceptance record required for every newly appointed governance reviewer:

```
================================================================================
IGRIS GOVERNANCE REVIEWER APPOINTMENT ACCEPTANCE RECORD
================================================================================
Appointment Reference ID    : APPT-2026-[ROLE]-01
Governing Entity            : IGRIS Steering Committee
Effective Date              : 2026-11-17
Expiration Date             : 2027-11-17 (Subject to annual re-affirmation)

1. APPOINTEE INFORMATION:
   Full Legal Name          : __________________________________________________
   Corporate Email Address  : __________________________________________________
   Assigned Seat            : [ ] DATA_CUSTODIAN        [ ] LEGAL_GOVERNANCE
                              [ ] SECURITY_PRIVACY      [ ] CHIEF_ARCHITECT
   Designation / Title      : __________________________________________________

2. HARDWARE KEY DETAILS:
   Hardware Token Serial    : __________________________________________________
   Assigned Key ID          : KEY-[ROLE]-[SERIAL]
   Public Key Fingerprint   : __________________________________________________
   Key Expiry (UTC)         : __________________________________________________

3. MANDATORY LEGAL AND TECHNICAL ATTESTATIONS:
   [X] I have read and agree to comply with the IGRIS Reviewer Operations Manual.
   [X] I satisfy all qualification criteria for my designated governance role.
   [X] I have disclosed all potential conflicts of interest and signed the COI Form.
   [X] I understand that my authority is strictly bound to my defined scope.
   [X] I acknowledge that my negative decision (REJECT or REQUEST_CHANGES) constitutes
       an absolute veto over dataset staging into production.
   [X] I attest that my hardware signing key will remain in my exclusive personal
       custody and will never be shared, automated, or exported.

Appointee Signature         : __________________________________________________
Date Signed (UTC)           : __________________________________________________
Attesting Committee Officer : __________________________________________________
Officer Signature           : __________________________________________________
Date Attested (UTC)         : __________________________________________________
================================================================================
```

---

*End of IGRIS Reviewer Operations & Onboarding Manual. Approved by IGRIS Steering Committee.*
