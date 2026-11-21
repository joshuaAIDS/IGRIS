# IGRIS Milestone 3C.3 — Approval Role Reconciliation

**Document Version:** 1.0.0  
**Status:** Canonical Governance Baseline  
**Governing Standard:** IGRIS Production Authorization Specification  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)

---

## 1. Executive Summary

This document performs a formal reconciliation between the **original four approval roles** established and codified in Milestones 3B.60 through 3B.62 and the **newly proposed roles** introduced in Milestone 3C.1.

In accordance with strict IGRIS governance principles:
1. **Existing approval roles are not silently replaced, merged, or deprecated.**
2. The four original roles remain the immutable, cryptographically enforced gate in `scripts/dataset_authorization.py`.
3. The newly proposed roles (`AI_ETHICS_SAFETY`, `TECHNICAL_LEAD`) are analyzed, mapped, and reconciled to eliminate ambiguity and prevent governance dilution.

---

## 2. Role Comparison & Discrepancy Matrix

| Dimension | Codified Role 1: `DATA_CUSTODIAN` | Codified Role 2: `LEGAL_GOVERNANCE` | Codified Role 3: `SECURITY_PRIVACY` | Codified Role 4: `CHIEF_ARCHITECT` | Proposed Role A: `AI_ETHICS_SAFETY` | Proposed Role B: `TECHNICAL_LEAD` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Origin Milestone** | Milestone 3B.60 | Milestone 3B.60 | Milestone 3B.60 | Milestone 3B.60 | Milestone 3C.1 | Milestone 3C.1 |
| **Enforced in Code** | Yes (`SignOffRole.DATA_CUSTODIAN`) | Yes (`SignOffRole.LEGAL_GOVERNANCE`) | Yes (`SignOffRole.SECURITY_PRIVACY`) | Yes (`SignOffRole.CHIEF_ARCHITECT`) | No (Informational prompt proposal) | No (Informational prompt proposal) |
| **Primary Mandate** | Data origin, custodial transfer, SHA-256 integrity, UTF-8 losslessness, NFC normalization. | Intellectual property, licensing, terms of service, commercial rights, copyleft/ShareAlike analysis. | PII screening (India DPDP Act 2023, GDPR), secret/credential isolation, 13-gram leakage prevention. | Model architecture fidelity, context window budget (2048), 10-domain stratification, vocabulary allocation (32,768). | Algorithmic fairness, societal bias, toxic content mitigation, harmful output guardrails. | Ingress pipeline execution, tooling stability, performance benchmarking, test suite execution. |
| **Statutory / Legal Basis** | Data chain of custody & supply chain security. | Copyright law, open-source contract law, IP indemnification. | Statutory privacy compliance (DPDP 2023 §8, GDPR Art. 6), cybersecurity standards. | Engineering architecture specification & parameter budget. | AI safety frameworks, voluntary ethical guidelines. | Operational engineering management. |
| **Veto Power** | Complete (Blocks corrupted or untracked data) | Complete (Blocks copyright-infringing or viral copyleft data) | Complete (Blocks data containing PII or leaking benchmarks) | Complete (Blocks data violating architectural budget or context length) | Advisory / Evaluative unless formally codified | Operational unless formally codified |

---

## 3. Discrepancy Analysis

### 3.1 Discrepancy 1: `SECURITY_PRIVACY` vs `AI_ETHICS_SAFETY`
- **Scope Divergence**: 
  - `SECURITY_PRIVACY` addresses **statutory, legal compliance** and **hard cryptographic security**. Its mandate covers deterministic PII scrubbing (Aadhaar numbers, PAN cards, phone numbers, email addresses, credit cards), secret scanning (AWS tokens, private keys, API keys), and 13-gram pre-training/evaluation leakage isolation.
  - `AI_ETHICS_SAFETY` addresses **probabilistic alignment and qualitative risk**, including societal bias, hate speech, representation across underrepresented dialects, and toxic discourse.
- **Risk of Silent Replacement**:
  - If `AI_ETHICS_SAFETY` silently replaces `SECURITY_PRIVACY`, strict PII scrubbing and credential isolation could be subordinated to subjective safety filtering, creating severe regulatory exposure under India's Digital Personal Data Protection (DPDP) Act 2023 and GDPR.
  - If `AI_ETHICS_SAFETY` is omitted entirely, harmful or toxic training material could bypass review even if completely free of PII and properly licensed.
- **Resolution**:
  - `SECURITY_PRIVACY` remains the **primary gating authority** for dataset authorization.
  - `AI_ETHICS_SAFETY` is integrated as an essential **review dimension within the Security & Privacy sign-off package**, requiring an explicit Ethics & Bias assessment section in the sign-off record before `SECURITY_PRIVACY` approves.

---

### 3.2 Discrepancy 2: `CHIEF_ARCHITECT` vs `TECHNICAL_LEAD`
- **Scope Divergence**:
  - `CHIEF_ARCHITECT` has authority over **global architectural invariants**: the 16-layer decoder-only Transformer, 512 hidden dimension, 8 attention heads, 4 KV heads (GQA), 2,048 context length, exactly 32,768 vocabulary, and strict reservation of IDs 0–11 for structural tokens.
  - `TECHNICAL_LEAD` is responsible for **tactical execution**: pipeline automation, CI/CD runtimes, test coverage, memory profiling, and throughput benchmarking.
- **Risk of Silent Replacement**:
  - A `TECHNICAL_LEAD` may approve a dataset based on operational convenience (e.g., fast download speeds, small disk footprint) that compromises the architectural integrity or benchmark representation (e.g., inadequate sequence length tiers or distorted Tamil-to-English ratio).
  - Silently replacing `CHIEF_ARCHITECT` removes systemic architectural accountability from the governance gate.
- **Resolution**:
  - `CHIEF_ARCHITECT` remains the **exclusive sign-off role** in the programmatic authorization gate.
  - `TECHNICAL_LEAD` signs off on the technical readiness report as a prerequisite technical audit submitted to the `CHIEF_ARCHITECT`.

---

## 4. Governance Harmonization Model

To preserve backward compatibility, security enforcement, and operational clarity, IGRIS establishes the following **Harmonized 4-Authority Framework**:

```
+-----------------------------------------------------------------------------------+
|                           IGRIS AUTHORIZATION GATE                                 |
|                                (DEFAULT: LOCKED)                                   |
+-----------------------------------------------------------------------------------+
          |                           |                         |                |
          v                           v                         v                v
+-------------------+       +-------------------+     +-------------------+   +--------------------+
| 1. DATA_CUSTODIAN |       | 2. LEGAL_GOVERNANCE|    | 3. SECURITY_PRIVACY|   | 4. CHIEF_ARCHITECT |
|                   |       |                   |     | (incl. AI Ethics) |   | (incl. Tech Lead)  |
+-------------------+       +-------------------+     +-------------------+   +--------------------+
| * Provenance      |       | * License terms   |     | * Statutory PII   |   | * Model invariants |
| * SHA-256 Hash    |       | * Commercial use  |     | * Secret leakage  |   | * Context budget   |
| * Ingress storage |       | * Copyleft risk   |     | * 13-gram overlap |   | * 10-domain balance|
| * NFC / UTF-8     |       | * Attribution     |     | * Safety / Bias   |   | * Tokenizer scope  |
+-------------------+       +-------------------+     +-------------------+   +--------------------+
          |                           |                         |                |
          +---------------------------+-------------------------+----------------+
                                      |
                                      v
                        [ ALL 4 ROLES APPROVED? ]
                               /         \
                             YES          NO
                             /              \
                [ GATE: APPROVED ]      [ GATE: LOCKED ]
```

### Programmatic Enforcement
In `scripts/dataset_authorization.py`, the required roles remain strictly defined as:
```python
class SignOffRole(str, Enum):
    DATA_CUSTODIAN = "DATA_CUSTODIAN"
    LEGAL_GOVERNANCE = "LEGAL_GOVERNANCE"
    SECURITY_PRIVACY = "SECURITY_PRIVACY"
    CHIEF_ARCHITECT = "CHIEF_ARCHITECT"

REQUIRED_ROLES: Set[SignOffRole] = {
    SignOffRole.DATA_CUSTODIAN,
    SignOffRole.LEGAL_GOVERNANCE,
    SignOffRole.SECURITY_PRIVACY,
    SignOffRole.CHIEF_ARCHITECT,
}
```

No modification to the Python verification code is permitted without a formally recorded, multi-signatory Architectural Change Request (ACR).
