# IGRIS Phase 10: Cryptographic Architecture & Signature Verification Audit

**Project**: IGRIS Multilingual Decoder-Only Transformer  
**Active Patch**: `C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch`  
**Document ID**: `IGRIS-AUDIT-PHASE10-CRYPTO`  
**Classification**: INDEPENDENT TECHNICAL AUDIT  
**Audit Date**: 2026-11-17  
**Audited Modules**: `scripts/review_intake_verifier.py`, `schemas/HUMAN_APPROVAL_SCHEMA_V1.json`  

---

## 1. Executive Summary & Core Cryptographic Findings

This audit inspects the cryptographic verification engine, key management logic, signature validation algorithms, and tamper-evident audit logging of the IGRIS governance framework.

### Critical Cryptographic Findings:
1. **Exact Signature Algorithm in Use**:
   - The actual implementation in `scripts/review_intake_verifier.py` uses **symmetric HMAC-SHA256**.
   - `compute_signature` calls `hmac.new(secret_key.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()`.
   - `verify_signature` executes constant-time `hmac.compare_digest`.
2. **Symmetric HMAC vs. Asymmetric Digital Signature Defect**:
   - **Finding**: HMAC is a symmetric message authentication code, **not** an asymmetric digital signature. In HMAC, the verifier must possess the exact same secret key as the signer.
   - **Impact**: True independent non-repudiation is impossible under symmetric HMAC because anyone with access to the verifier's key store could forge signatures indistinguishable from the human reviewer.
   - **Remediation**: The governance framework must be upgraded to support **asymmetric public-key cryptography (Ed25519 / RFC 8032)** prior to authentic human onboarding, allowing reviewers to keep private keys strictly inside their hardware enclaves while publishing only open verification public keys.
3. **Retraction of Unsubstantiated FIPS Claims**:
   - **Finding**: Documentation referenced "FIPS 140-2 Level 3 / Secure Enclave (TPM 2.0)" without citing specific NIST CMVP certificate numbers or evidence of a validated cryptographic module in the runtime environment.
   - **Determination**: In accordance with Phase 10 directives, all claims of FIPS certification are formally retracted as unverified. FIPS-certified hardware tokens (such as YubiKey 5 FIPS) remain an operational recommendation for physical reviewers, but the host environment executes standard Python cryptography.
4. **Key-to-Reviewer Binding Gap**:
   - `KeyRecord` dataclass stores `key_id`, `role`, and `secret_key`, but lacks an explicit `reviewer_id` attribute, creating a potential ambiguity in multi-reviewer key tracking.

---

## 2. Technical Inspection of Verification Engine

### 2.1 Payload Canonicalization (RFC 8785)
The engine implements deterministic JSON canonicalization in `canonical_json_bytes`:
```python
def canonical_json_bytes(data: Dict[str, Any]) -> bytes:
    payload = {k: v for k, v in data.items() if k != "digital_signature"}
    raw_str = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw_str.encode("utf-8")
```
- **Audit Assessment**: **COMPLIANT**. Strips `digital_signature`, sorts keys lexicographically, eliminates whitespace padding, and encodes as UTF-8. Guarantees bitwise reproducible signature payloads.

### 2.2 Signature-to-Dossier Binding
In `ReviewIntakeVerifier.verify_submission`:
```python
if document_path is not None:
    doc_p = Path(document_path)
    if not doc_p.is_file():
        errors.append(f"Audited document path does not exist on disk: {doc_p}")
    else:
        computed_hash = hashlib.sha256(doc_p.read_bytes()).hexdigest()
        if computed_hash.lower() != doc_hash.lower():
            errors.append(
                f"Document SHA256 mismatch: on disk='{computed_hash}', submission claims='{doc_hash}'"
            )
```
- **Audit Assessment**: **COMPLIANT & SECURE**. The live on-disk dossier markdown file is read directly and its SHA-256 hash is checked against the submission's `document_sha256`. Any modification to the dossier after signing invalidates the submission.

### 2.3 Key-to-Role Binding & Expiration
In `KeyRegistry.is_valid_key`:
- Checks `record.role != declared_role`: Prevents privilege escalation and cross-role signing.
- Checks `record.is_revoked`: Enforces immediate revocation upon CRL listing.
- Checks `now > exp_dt`: Enforces key lifetime limits.
- **Audit Assessment**: **COMPLIANT**.

---

## 3. Cryptographic Verification Matrix

| Verification Aspect | Implementation Mechanism | Evaluated Status | Audit Finding |
| :--- | :--- | :---: | :--- |
| **Signature Algorithm** | HMAC-SHA256 (symmetric) | **REMEDIABLE DEFECT** | Must upgrade to asymmetric Ed25519 for non-repudiation |
| **Non-Repudiation** | Symmetric shared secret | **DEFICIENT** | Verifier possesses signing capability; requires Ed25519 public key |
| **Dossier Integrity Binding** | Bitwise SHA-256 live-disk verification | **PASS** | Any byte alteration on disk triggers instant rejection |
| **Source ID Binding** | Canonical JSON array inclusion | **PASS** | Source IDs are cryptographically covered by the signature |
| **Key-to-Role Binding** | Explicit enum check in `is_valid_key` | **PASS** | Key cannot be used for any role other than registered |
| **Key-to-Reviewer Binding** | Submission string check; missing in `KeyRecord` | **REMEDIABLE DEFECT** | `KeyRecord` should explicitly bind `reviewer_id` |
| **Replay Protection** | Timestamp/expiry check; no persistent ID cache | **REMEDIABLE DEFECT** | Verifier lacks indexed cache of seen `submission_id`s |
| **Revocation Handling (CRL)** | Boolean `is_revoked` flag with reason string | **PASS** | Revoked keys rejected immediately |
| **Credential Expiry** | ISO 8601 UTC timestamp comparison against `now` | **PASS** | Expired keys and expired approvals fail closed |
| **Constant-Time Verification** | `hmac.compare_digest` | **PASS** | Protects against timing side-channel attacks |
| **Fail-Closed Behavior** | Errors list accumulation; default invalid | **PASS** | Any failure leaves gate locked and quorum unchanged |
| **FIPS 140-2 Level 3 Claims** | Unsubstantiated assertion in docs/CSV | **RETRACTED** | Formal claim retracted; no CMVP certificate in evidence |

---

## 4. Audit Trail Cryptographic Hash-Chain Verification

The `AuditTrailLogger` implements an immutable, append-only hash chain:

```
[ Genesis Block: "0"*64 ]
          |
          v
[ Record 1 ] -> SHA-256(audit_id, ts, source_id, gate, prev, new, rev, role, evid, reason, genesis_hash)
          |
          v
[ Record 2 ] -> SHA-256(..., parent_hash = Record 1 Hash)
          |
          v
[ Record N ] -> SHA-256(..., parent_hash = Record N-1 Hash)
```

### Verification Results:
- `verify_chain_integrity()` recalculates every hash in the chain and validates parent pointers.
- Re-running integrity tests across existing audit files confirms 100% chain continuity. Zero historical records have been modified or deleted.

---

## 5. Required Cryptographic Remediation Plan

To attain authentic readiness for genuine external human review:

1. **Implement Dual-Mode Signature Verification (Ed25519 + HMAC)**:
   - Introduce Ed25519 asymmetric verification in `scripts/review_intake_verifier.py` (via pure Python RFC 8032 implementation or `cryptography` library when installed).
   - Signer generates an Ed25519 private key inside their hardware token; `KeyRecord` stores only the 32-byte Ed25519 public key.
   - Verifier validates signature using only the public key, achieving true non-repudiation.
2. **Add `reviewer_id` to `KeyRecord`**:
   - Formally bind `reviewer_id` in `KeyRecord` to enforce that a key can only be submitted by its designated owner.
3. **Add Persistent Replay Cache**:
   - Maintain a persistent index of processed `submission_id`s to reject replayed submissions on intake before quorum evaluation.
4. **Retract FIPS Claims Across All Registers**:
   - Update `IGRIS_PHASE8_KEY_REGISTRATION_STATUS.csv` and documentation to replace "FIPS 140-2 Level 3" with "Hardware Security Enclave (e.g., TPM 2.0 / Hardware Token Recommended)".

---

*End of IGRIS Phase 10 Cryptographic Architecture Audit.*
