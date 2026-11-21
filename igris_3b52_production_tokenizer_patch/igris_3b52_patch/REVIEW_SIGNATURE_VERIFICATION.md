# IGRIS Cryptographic Review Signature & Quorum Verification Specification

**Document Version:** 1.0.0  
**Milestone:** 3C.10 — Human Review Intake & Cryptographic Approval Verification  
**Governing Standard:** IGRIS Zero-Trust Cryptographic Governance & Multi-Signature Consensus  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`

---

## 1. Executive Summary & Verification Mandate

The IGRIS dataset governance framework enforces a strict zero-trust operational model: **no human approval is legally or technically recognized unless it is cryptographically signed, bound to an authentic human public key, verifiable against the audited document hash on disk, and corroborated by unanimous 4-of-4 quorum consensus**.

This document specifies the technical architecture, mathematical standards, and programmatic checks executed by [`scripts/review_intake_verifier.py`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/review_intake_verifier.py) and [`HUMAN_APPROVAL_SCHEMA_V1.json`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/HUMAN_APPROVAL_SCHEMA_V1.json).

> [!CAUTION]
> **ANTI-FABRICATION MANDATE**:
> Automated AI agents, scripts, and language models are strictly barred from inventing or generating reviewer identities, private keys, digital signatures, or approval tokens. All active catalog sources remain in the `PENDING` state until authentic human personnel execute physical/cryptographic reviews.

---

## 2. Cryptographic Verification Pipeline

Every intake submission passes through nine sequential verification gates before it can be considered for quorum evaluation:

```
+----------------------------------------------------------------------------------------------------+
|                         NINE-STAGE INTAKE VERIFICATION WORKFLOW                                    |
+----------------------------------------------------------------------------------------------------+

  [Intake Submission JSON]
            |
            v
  [Stage 1: Schema Validation against HUMAN_APPROVAL_SCHEMA_V1.json]
            |
            v
  [Stage 2: Role Legitimacy Check (Must be 1 of 4 Codified Roles)]
            |
            v
  [Stage 3: Public Key Lookup & Key Revocation List (CRL) Audit]
            |
            v
  [Stage 4: Role-to-Key Binding Verification (Key must match role)]
            |
            v
  [Stage 5: Timestamp & Expiration Date Check (current_time <= expiry_date)]
            |
            v
  [Stage 6: Document SHA-256 Verification against Disk File]
            |
            v
  [Stage 7: Canonical Serialization (RFC 8785 Sorted-Key Encoding)]
            |
            v
  [Stage 8: Cryptographic Signature Verification (Constant-Time HMAC/Sig)]
            |
            v
  [Stage 9: Quorum & Consensus Resolution Engine]
```

### Stage 1: Formal Schema Validation
The intake JSON is validated against [`HUMAN_APPROVAL_SCHEMA_V1.json`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/HUMAN_APPROVAL_SCHEMA_V1.json). Submissions missing required fields (`submission_id`, `reviewer_identity`, `role`, `public_key_id`, `source_ids_reviewed`, `decision`, `evidence_references`, `document_sha256`, `timestamp`, `expiry_date`, `digital_signature`) or containing unexpected extra fields are immediately rejected.

### Stage 2: Role Legitimacy Verification
The declared `role` must strictly equal one of the four codified governance roles:
- `DATA_CUSTODIAN`
- `LEGAL_GOVERNANCE`
- `SECURITY_PRIVACY`
- `CHIEF_ARCHITECT`
Submissions signed under non-codified roles (e.g. `TECHNICAL_LEAD`, `AI_ETHICS_SAFETY`, or arbitrary titles) are rejected with an `InvalidRoleError`.

### Stage 3: Public Key Registry & CRL Audit
The `public_key_id` is queried against the authoritative governance Key Registry:
1. **Key Recognition**: Unregistered key IDs fail immediately.
2. **Revocation Check**: The key must not appear on the Key Revocation List (CRL). If revoked, verification aborts with the recorded revocation reason.

### Stage 4: Role-to-Key Cryptographic Binding
A public key is cryptographically bound to a single specific role upon registration. A key registered for `DATA_CUSTODIAN` cannot sign a review on behalf of `LEGAL_GOVERNANCE`. Any attempt to cross-sign triggers an immediate `RoleBindingViolationError`.

### Stage 5: Timestamp & Expiration Enforcement
- The submission timestamp must reflect a valid UTC ISO-8601 string.
- If the current validation time exceeds `expiry_date`, the approval is marked **`EXPIRED`** and rejected. Approval validity windows are capped at 90 days for custody and security, and 180 days for legal and architecture.

### Stage 6: Audited Document SHA-256 Verification
The field `document_sha256` represents the hash of the markdown review dossier audited by the human reviewer (e.g. `REVIEW_DATA_CUSTODIAN_V2.md`). The verifier computes the live SHA-256 hash of that file on disk:
$$\text{ComputedHash}(\text{Path}) == \text{document\_sha256}$$
If even a single byte or space in the markdown document was modified after review, a `DocumentIntegrityMismatchError` is raised.

### Stage 7: Deterministic Canonical Serialization
To prevent JSON key-reordering attacks, the intake dictionary is serialized into canonical bytes:
1. The `digital_signature` field is excluded from the serialization payload.
2. Dictionary keys are sorted lexicographically (`sort_keys=True`).
3. Whitespace is stripped to compact separators (`separators=(',', ':')`).
4. Output is encoded to binary UTF-8 without ASCII escaping.

### Stage 8: Cryptographic Signature Verification
The digital signature is verified in constant time (`hmac.compare_digest`) against the canonical payload bytes using the registered key secret. Any bit-flip in the payload (such as altering `decision` from `REJECT` to `APPROVE`, or adding an extra source ID) invalidates the signature.

---

## 3. Quorum & Consensus Resolution Matrix

Once individual submissions pass Stages 1–8, they are aggregated by the [`QuorumEngine`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/scripts/review_intake_verifier.py) on a per-source basis:

| Custodian Vote | Legal Vote | Security Vote | Architect Vote | Resolved Source State | Downstream Governance Action |
| :---: | :---: | :---: | :---: | :---: | :--- |
| `APPROVE` | `APPROVE` | `APPROVE` | `APPROVE` | **`APPROVED`** | Eligible for scoped gate authorization. |
| `APPROVE` | `APPROVE` | `APPROVE` | `PENDING` | **`PENDING`** | Quorum incomplete; gate remains LOCKED. |
| `APPROVE` | `REJECT` | `APPROVE` | `APPROVE` | **`BLOCKED_REJECTED`** | **Consensus Failure**: permanently blocks acquisition. |
| `APPROVE` | `APPROVE` | `REQUEST_CHANGES` | `APPROVE` | **`BLOCKED_CHANGES_REQUESTED`** | Approval withheld pending remediation. |
| `REJECT` | `REJECT` | `REJECT` | `REJECT` | **`BLOCKED_REJECTED`** | Unanimous rejection; permanently barred. |

### Quorum Invariant Rules:
1. **Unanimous 4-of-4 Quorum**: All four roles must vote `APPROVE`.
2. **Conflicting Decision Rule**: Any single `REJECT` or `REQUEST_CHANGES` overrides all `APPROVE` votes and immediately yields a `BLOCKED` status.
3. **Duplicate Detection**: Multiple submissions for the same role on a single source ID are flagged and rejected to prevent replay attacks.
4. **Independent Source Evaluation**: Every source ID is resolved independently. Approving `SRC-TM-01` confers zero approval status on `SRC-HI-01` or any other corpus.

---

## 4. Current Operational State

1. **Production Access Gate**: **`LOCKED`**.
2. **Active Approvals**: **`NONE`** (Zero human submissions received).
3. **All 32 Sources**: Set to **`PENDING`** in [`SOURCE_APPROVAL_STATE_V2.csv`](file:///C:/IGRIS/igris_3b52_production_tokenizer_patch/igris_3b52_patch/SOURCE_APPROVAL_STATE_V2.csv).
