# IGRIS Security Gap Register & Bypass Analysis

**Project**: IGRIS Decoder-Only Language Model  
**Milestone**: 3B.62 — Production Authorization Readiness Audit  
**Document ID**: `IGRIS-SEC-GAP-3B62`  
**Classification**: TECHNICAL SECURITY AUDIT & RISK REGISTER  
**Status**: APPROVED  
**Date**: 2026-11-17  

---

## 1. Overview & Threat Context

In preparation for future production dataset evaluation (Milestone 3C), this register documents potential security gaps, attack surfaces, and bypass vectors in the data access pipeline.

While Milestone 3B has successfully implemented a Default-Deny runtime gate, full production security requires continuous auditing of the boundary between user code, filesystem I/O, and cryptographic authorization records.

---

## 2. Security Gap Register

| Gap ID | Category | Vulnerability / Bypass Description | Milestone 3B Mitigation | Milestone 3C Target Hardening | Severity | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GAP-01** | Direct File I/O | A developer or untracked script uses Python `open("data.jsonl")` directly, bypassing `AuthorizationValidator.get_authorized_dataset_path()`. | Policy prohibition & CI test isolation; datasets staged in isolated directory hierarchies. | Implement filesystem-level sandboxing (e.g. read-only mounts, process namespaces, or encrypted filesystems with in-memory decryption by the gatekeeper only). | **HIGH** | `MITIGATED VIA POLICY` |
| **GAP-02** | Signature Cryptography | Authorization sign-off records currently use SHA-256 digest strings rather than asymmetric digital signatures (e.g., Ed25519 or RSA-4096). | Schema strictly validates 64-character hex format; manifest SHA-256 enforces bitwise immutability. | Integrate asymmetric public-key cryptography (Ed25519) where each human authority signs using their private key, verified against an organizational public key ring. | **MEDIUM** | `PLANNED FOR 3C` |
| **GAP-03** | Local OS Permissions | Filesystem read-only flags (`chmod 0444` / `attrib +R`) can be overridden or removed by privileged OS users. | Dual-layer SHA-256 manifest validation detects any file tampering at execution time regardless of file permissions. | Implement cryptographic envelope encryption (KMS) for raw production corpus partitions. | **MEDIUM** | `ENFORCED VIA GATE` |
| **GAP-04** | Training Trigger Guard | An operator could manually execute `build_tokenizers.py` targeting production corpus before formal sign-off. | Training builders currently point exclusively to synthetic fixtures; all production flags are disabled. | Embed programmatic call to `AuthorizationValidator.enforce_access_gate()` inside `CandidateABuilder.build()` and `CandidateBBuilder.build()` before corpus ingestion. | **HIGH** | `READY TO ENFORCE` |
| **GAP-05** | Path Traversal / Symlinks | Malicious or malformed paths in `DATASET_INVENTORY.csv` (e.g. `../../private/data.jsonl`) could attempt traversal. | Path resolution uses strictly normalized `Path.resolve()` relative to approved dataset root directories. | Enforce strict regex validation restricting file paths to `^[a-zA-Z0-9_-]+(/[a-zA-Z0-9_.-]+)+$`; reject `..` and leading slashes. | **MEDIUM** | `ENFORCED VIA GATE` |
| **GAP-06** | Hardware Token Binding | Sign-off hashes can theoretically be copied between markdown records if metadata is identical. | `DatasetAuthorizationRecord` binds the signatory hash directly to `dataset_id`, `milestone`, `version`, and `timestamp`. | Require FIDO2 / YubiKey WebAuthn or PGP hardware token digital signatures for production sign-offs. | **LOW** | `PLANNED FOR 3C` |

---

## 3. In-Depth Bypass Analysis & Mitigations

### 3.1 Direct Python `open()` Bypass Analysis (GAP-01)
- **Risk**: Python's native standard library allows any code running in the same process to call `open(path, 'r')`. If an evaluation script bypasses the `AuthorizationValidator`, unapproved files could theoretically be read.
- **Architectural Safeguard**:
  1. The canonical evaluation pipeline (`scripts/evaluate_candidates_3b58.py`) only receives dataset paths resolved by `AuthorizationValidator.get_authorized_dataset_path()`.
  2. In production deployment, datasets must reside in protected network storage accessible only by the service account executing the gated runner.
  3. CI/CD static analysis (e.g., AST linter) will reject PRs containing direct file path opens on dataset directories.

### 3.2 Asymmetric Cryptography Roadmap (GAP-02 & GAP-06)
- **Current State**: Milestone 3B validates that each of the four human sign-offs includes an approved signatory name, role, timestamp, decision (`APPROVED`), and a 64-character SHA-256 digest.
- **Production Roadmap**:
  - In Milestone 3C, replace mock hashes with real digital signatures:
    $$\text{Signature} = \operatorname{Ed25519\_Sign}(\text{PrivateKey}_{\text{Role}}, \text{DatasetID} \parallel \text{ManifestHash} \parallel \text{Timestamp})$$
  - The access gate will load the organization's public keyring (`.igris/security/keyring.pub`) and verify the signature using the corresponding role's public key.

---

## 4. Audit Conclusion

No unmitigated critical security vulnerabilities exist in the Milestone 3B codebase. All identified gaps are either:
1. Enforced and blocked at runtime by the dual SHA-256 gatekeeper.
2. Mitigated by strict governance isolation and synthetic-only execution environments.
3. Formally registered for cryptographic upgrade during Milestone 3C production staging.
