# IGRIS Governance Audit Trail & Cryptographic Hash Chain Specification

**Document Version:** 1.0.0  
**Milestone:** 3C.10 — Human Review Intake & Cryptographic Approval Verification  
**Governing Standard:** IGRIS Append-Only Audit Logging & Cryptographic Provenance Architecture  
**Access Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Candidate Invariants:** `PRESERVED & UNCHANGED`

---

## 1. Executive Summary & Purpose

In compliance with IGRIS Milestone 3C.10 directives, this document specifies the technical architecture and cryptographic standards for the **append-only governance audit trail**.

Every state change, human review intake, gate authorization request, and access denial in the IGRIS dataset pipeline must be permanently and immutably recorded in a **cryptographic hash-chained log**. This ensures:
1. **Total State Immutability**: Historical authorization events cannot be modified, deleted, or retroactively inserted without breaking the cryptographic hash chain.
2. **Accountability & Non-Repudiation**: Every decision is cryptographically tied to the reviewer's key identity, timestamp, and audited document hash.
3. **Auditable Gate State Transitions**: Transitioning any of the seven gates from `LOCKED` or `NOT AUTHORIZED` to any other state requires a verifiable audit trail entry.

---

## 2. Cryptographic Hash Chain Architecture

The audit trail operates as an append-only JSON Lines (`.jsonl`) ledger. Each audit record contains the cryptographic SHA-256 digest of the immediately preceding record (`parent_audit_hash`), forming an unbroken tamper-evident chain:

```
+----------------------------------------------------------------------------------------------------+
|                         CRYPTOGRAPHIC AUDIT LOG HASH CHAIN                                         |
+----------------------------------------------------------------------------------------------------+

  [Genesis Entry: audit_id = 1]
  ├── parent_audit_hash: 0000000000000000000000000000000000000000000000000000000000000000 (Genesis)
  ├── source_id:         SRC-TM-01
  ├── previous_state:    LOCKED
  ├── new_state:         PENDING
  └── record_hash:       4f9a2e... (SHA-256 of Entry 1)
           |
           v
  [Entry 2: audit_id = 2]
  ├── parent_audit_hash: 4f9a2e... (Exact copy of Entry 1 record_hash)
  ├── source_id:         SRC-TM-01
  ├── previous_state:    PENDING
  ├── new_state:         APPROVED
  └── record_hash:       8b3c1d... (SHA-256 of Entry 2)
           |
           v
  [Entry 3: audit_id = 3]
  ├── parent_audit_hash: 8b3c1d... (Exact copy of Entry 2 record_hash)
  └── ...
```

---

## 3. Log Record Schema

Every entry appended to the governance ledger must conform to the following schema:

| Field Name | Type | Description |
| :--- | :---: | :--- |
| `audit_id` | `integer` | Strictly monotonic sequence counter starting at 1. |
| `timestamp` | `string` | ISO-8601 UTC timestamp recording the moment of logging. |
| `source_id` | `string` | Canonical candidate source ID (e.g. `SRC-TM-01`) or `GATE_MASTER`. |
| `gate_name` | `string` | Targeted pipeline gate (1 of 7 gates). |
| `previous_state`| `string` | State prior to event (e.g. `PENDING`, `LOCKED`). |
| `new_state` | `string` | State resulting from event (e.g. `BLOCKED_REJECTED`, `APPROVED`). |
| `reviewer_identity` | `string` | Authorized reviewer email, key ID, or `GOVERNANCE_SYSTEM`. |
| `role` | `string` | One of the four codified roles or `SYSTEM_GATE`. |
| `evidence_hash` | `string` | SHA-256 hash of the intake submission or audited document. |
| `reason_for_decision` | `string` | Explicit human findings, justification, or rejection rationale. |
| `parent_audit_hash` | `string` | SHA-256 hash of the preceding record (64 zeroes for genesis). |
| `record_hash` | `string` | SHA-256 digest computed across all record fields excluding `record_hash`. |

---

## 4. Hash Computation & Verification Algorithm

### 4.1 Record Hash Generation
For any record $R_i$:
1. Construct dictionary $D_i$ from all fields of $R_i$, excluding `record_hash`.
2. Serialize $D_i$ to canonical JSON with sorted keys:
   $$\text{canonical\_bytes} = \text{json.dumps}(D_i, \text{sort\_keys}=\text{True}).\text{encode}('utf-8')$$
3. Compute SHA-256 digest:
   $$R_i.\text{record\_hash} = \text{hashlib.sha256}(\text{canonical\_bytes}).\text{hexdigest}()$$

### 4.2 Chain Integrity Verification
The verifier scans the log sequentially from index $i = 1$ to $N$:
1. **Link Verification**: For $i = 1$, verify $R_1.\text{parent\_audit\_hash} == 0^{64}$. For $i > 1$, verify:
   $$R_i.\text{parent\_audit\_hash} == R_{i-1}.\text{record\_hash}$$
2. **Payload Verification**: Recompute the hash of $R_i$ from its fields and assert:
   $$\text{ComputedHash}(R_i) == R_i.\text{record\_hash}$$
3. Any mismatch immediately aborts pipeline operations with an `AuditTrailTamperAlert`.

---

## 5. Storage and Access Protections

1. **Storage Path**: `reports/governance_audit_trail.jsonl`.
2. **Filesystem Security**: Write-once, append-only permissions. Direct editing, rewriting, truncation, or line deletion is blocked by repository hooks and test assertions.
3. **Repository Permanence**: Audit logs are committed to version control and archived permanently with milestone sign-off records.
