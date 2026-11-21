# IGRIS Pipeline Gate Audit & Authorization Decoupling Specification

**Document Version:** 2.0.0  
**Milestone:** 3C.9 — Human Approval Package & Authorization Readiness Audit  
**Governing Standard:** IGRIS Zero-Trust Data Governance & Default-Deny Security Framework  
**Current Gate Status:** `LOCKED` (Default-Deny Enforced)  
**Acquisition Status:** `NOT AUTHORIZED`  
**Human Approvals Status:** `PENDING` (Unsigned — Never Fabricate Signatures)

---

## 1. Executive Summary & The Independence Axiom

A critical systemic vulnerability in modern machine learning infrastructure is **authorization bleed**—where obtaining permission for an early-stage activity (such as crawling or tokenizer evaluation) is improperly interpreted as blanket permission for downstream activities (such as pre-training, fine-tuning, or commercial model release).

In strict compliance with IGRIS Milestone 3C.9 directives, this document formalizes the **Seven Decoupled Governance Gates** and codifies the **Independence Axiom**:

> [!CAUTION]
> **THE INDEPENDENCE AXIOM**:
> **No permission granted for one pipeline gate may automatically authorize, unlock, or imply permission for any other pipeline gate.**
> Each pipeline stage possesses an independent cryptographic access control gate, independent authorization state record, and independent four-role human sign-off requirement.

---

## 2. The Seven Decoupled Governance Gates

```
+----------------------------------------------------------------------------------------------------+
|                         IGRIS SEVEN-GATE AUTHORIZATION ARCHITECTURE                                |
+----------------------------------------------------------------------------------------------------+

  [Gate 1: DATASET ACQUISITION] ----------------> State: NOT AUTHORIZED (Default-Deny)
           |
           v
  [Gate 2: PRODUCTION DATA ACCESS] -------------> State: LOCKED (Default-Deny Access Controller)
           |
           +-----------------------+-----------------------+
           |                       |                       |
           v                       v                       v
  [Gate 3: TOKENIZER VOCAB]   [Gate 4: TOKENIZER EVAL]   [Gate 5: SUPERVISED FINE-TUNING]
   State: PENDING_APPROVAL     State: PENDING_APPROVAL    State: NOT AUTHORIZED
   (18 Eligible, 8 Cond,       (28 Eligible,              (0 / 32 Authorized,
    2 Prohibited, 4 Rej)        4 Rejected)                100% Prohibited at 3C.9)
                                                           |
                                                           +-------------------+
                                                           |                   |
                                                           v                   v
                                               [Gate 6: ALIGNMENT EVAL]  [Gate 7: SAFETY EVAL]
                                                State: NOT AUTHORIZED     State: NOT AUTHORIZED
                                                (3 Designated Benchs)     (1 Designated Bench)
```

### Detailed Gate Specifications:

### Gate 1: Dataset Acquisition Gate
- **Purpose**: Authorizes outbound network requests to download or transfer raw corpus files from upstream repositories.
- **Current State**: **`NOT AUTHORIZED`**. Zero bytes of external dataset files have been downloaded or transported.
- **Trigger Condition**: Requires an approved `DATASET_ACQUISITION_PLAN.md` signed by `DATA_CUSTODIAN` and `CHIEF_ARCHITECT`.

### Gate 2: Production Data Access Gate
- **Purpose**: Unlocks filesystem access to staging, quarantine, or production corpus folders (`production/data/`).
- **Current State**: **`LOCKED`**. Hardcoded default-deny gate in `src/authorization.py`.
- **Trigger Condition**: Requires active, unexpired, verified signatures from all four human roles (`DATA_CUSTODIAN`, `LEGAL_GOVERNANCE`, `SECURITY_PRIVACY`, `CHIEF_ARCHITECT`).

### Gate 3: Tokenizer Vocabulary Training Gate
- **Purpose**: Permits subword merge learning, Unigram EM optimization, and vocabulary construction up to the 32,768 vocabulary budget.
- **Current State**: **`PENDING_APPROVAL`** (for 18 verified baseline sources).
- **Hard Architectural Exclusions**:
  - `SRC-CD-02` (HumanEval/MBPP): `STRICTLY_PROHIBITED` (Prevents test-set contamination).
  - `SRC-CV-04` (Anthropic HH-RLHF): `STRICTLY_PROHIBITED` (Prevents toxic vocabulary piece allocation).
  - 4 Incompatible sources (`SRC-TG-03`, `SRC-HI-03`, `SRC-CV-01`, `SRC-CV-02`): `INELIGIBLE_REJECTED`.

### Gate 4: Tokenizer Evaluation Gate
- **Purpose**: Permits running inference-only compression ratio tests, fertility score analysis ($r_{\text{char/tok}}$), and Tier 1–4 sequence length stress testing on candidate tokenizers.
- **Current State**: **`PENDING_APPROVAL`** (28 sources eligible pending sign-off; 4 incompatible sources rejected).
- **Special Quarantine Rule**: `SRC-CV-04` is restricted strictly to `SRC-CV-04-CHOSEN-PROMPTS-ISOLATED` (extracting prompt prefixes only; excluding completions and red-team attacks).

### Gate 5: Supervised Fine-Tuning (SFT) Gate
- **Purpose**: Authorizes training decoder-only Transformer weights on instruction or conversational dialogue pairs.
- **Current State**: **`NOT AUTHORIZED` across all 32 sources (100%)**.
- **Governance Mandate**: Tokenizer evaluation clearance confers **zero** rights to fine-tune or pre-train model weights on the corpus. SFT authorization requires a separate legal and architectural governance milestone.

### Gate 6: Alignment Evaluation Gate
- **Purpose**: Authorizes evaluating trained model checkpoints against preference pairs (e.g., DPO/RLHF reward modeling).
- **Current State**: **`NOT AUTHORIZED` across all 32 sources (100%)**.
- **Designated Benchmark**: `SRC-CV-04` (Anthropic HH-RLHF) and `SRC-CV-03` are architectural candidates for downstream alignment evaluation, but remain completely blocked from execution at Milestone 3C.9.

### Gate 7: Safety Evaluation Gate
- **Purpose**: Authorizes running adversarial red-team queries and harmfulness refusal probes against trained checkpoints.
- **Current State**: **`NOT AUTHORIZED` across all 32 sources (100%)**.
- **Designated Benchmark**: `SRC-CV-04` harmlessness red-team splits are designated for this gate, but execution is strictly withheld.

---

## 3. The 32-Source Gate Mapping Summary

| Pipeline Gate | Authorized | Pending Review | Strictly Prohibited | Rejected | Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gate 1: Dataset Acquisition** | 0 | 0 | 0 | 32 (`NOT AUTHORIZED`) | 32 |
| **Gate 2: Production Data Access** | 0 | 0 | 0 | 32 (`LOCKED`) | 32 |
| **Gate 3: Tokenizer Vocab Training** | 0 | 18 (`ELIGIBLE_PENDING`) | 2 (`SRC-CD-02`, `SRC-CV-04`) | 12 (8 Cond + 4 Rej) | 32 |
| **Gate 4: Tokenizer Fertility / Reg Eval** | 0 | 28 (`ELIGIBLE_PENDING`) | 0 | 4 (`INCOMPATIBLE`) | 32 |
| **Gate 5: Supervised Fine-Tuning (SFT)** | **0** | **0** | **0** | **32 (`NOT AUTHORIZED`)** | **32** |
| **Gate 6: Alignment Evaluation** | **0** | **0** | **0** | **32 (`NOT AUTHORIZED`)** | **32** |
| **Gate 7: Safety Evaluation** | **0** | **0** | **0** | **32 (`NOT AUTHORIZED`)** | **32** |

---

## 4. Technical Enforcement Mechanisms

1. **State Machine Separation**:
   In `src/authorization.py`, every authorization request must supply both `dataset_id` AND `pipeline_gate`. The state machine verifies that:
   $$\text{GatePermission}(\text{Dataset}, \text{Gate}) \implies \text{ActiveApprovedState}(\text{Dataset}, \text{Gate})$$
   Evaluating Gate 3 checks Gate 3 permissions only; passing Gate 3 returns a scope-limited cryptographic token that cannot be used by Gate 5 (SFT) or Gate 2 (Production Access).

2. **Tamper-Evident Records**:
   Approval decisions are serialized as JSON records hashed with SHA-256. Any modification to a field invalidates the manifest signature.

3. **Multi-Role Consensus**:
   No single role can unlock any gate. Unlocking requires a 4-of-4 quorum:
   `DATA_CUSTODIAN` $\land$ `LEGAL_GOVERNANCE` $\land$ `SECURITY_PRIVACY` $\land$ `CHIEF_ARCHITECT`.

---

## 5. Audit Conclusion

All seven gates have been audited and verified:
- Acquisition: `NOT AUTHORIZED`
- Production Access: `LOCKED`
- SFT / Alignment / Safety: `NOT AUTHORIZED`
- Vocab Training & Eval: `PENDING HUMAN REVIEW`
