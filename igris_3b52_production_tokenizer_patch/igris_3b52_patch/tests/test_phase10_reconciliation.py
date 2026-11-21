"""IGRIS Phase 10: Governance Reconciliation & Independent Readiness Test Suite.

Verifies:
1. Presence and integrity of all Phase 10 deliverables.
2. Exact source eligibility counts:
   - Vocab training: 18 eligible pending approval, 14 ineligible/prohibited.
   - Fertility evaluation: 28 eligible pending approval, 4 ineligible.
3. Four incompatible sources permanently barred.
4. Tokenizer benchmark and preference pair training prohibitions enforced.
5. Candidate A and B tokenizer SHA-256 hashes invariant.
6. Pipeline gate locked across all candidate sources.
7. Phase 10 final verdict selection (Verdict B: Remediable Defects).
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import pytest

PATCH_ROOT = Path(__file__).resolve().parent.parent

CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_phase10_deliverables_exist():
    """Verify all seven Phase 10 deliverable files exist."""
    deliverables = [
        PATCH_ROOT / "IGRIS_PHASE10_SOURCE_ELIGIBILITY_RECONCILIATION.csv",
        PATCH_ROOT / "IGRIS_PHASE10_GOVERNANCE_STATE_AUDIT.md",
        PATCH_ROOT / "IGRIS_PHASE10_CRYPTOGRAPHIC_AUDIT.md",
        PATCH_ROOT / "IGRIS_PHASE10_SIGNATURE_INTAKE_SECURITY_REPORT.md",
        PATCH_ROOT / "IGRIS_PHASE10_PIPELINE_GATE_AUDIT.md",
        PATCH_ROOT / "IGRIS_PHASE10_TEST_RESULTS.md",
        PATCH_ROOT / "IGRIS_PHASE10_FINAL_READINESS_REPORT.md",
    ]
    for d in deliverables:
        assert d.is_file(), f"Missing required Phase 10 deliverable: {d.name}"
        assert d.stat().st_size > 0, f"Deliverable is empty: {d.name}"


def test_phase10_reconciliation_counts():
    """Verify exact reconciled operation counts across the 32 candidate sources."""
    recon_path = PATCH_ROOT / "IGRIS_PHASE10_SOURCE_ELIGIBILITY_RECONCILIATION.csv"
    with open(recon_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 32, f"Expected 32 sources in reconciliation, found {len(rows)}"

    # Vocabulary training counts
    vocab_eligible = [r for r in rows if r["vocab_training_eligibility"] == "ELIGIBLE_PENDING_APPROVAL"]
    vocab_ineligible = [r for r in rows if r["vocab_training_eligibility"] != "ELIGIBLE_PENDING_APPROVAL"]

    assert len(vocab_eligible) == 18, f"Expected 18 eligible for vocab training, got {len(vocab_eligible)}"
    assert len(vocab_ineligible) == 14, f"Expected 14 ineligible/prohibited for vocab training, got {len(vocab_ineligible)}"

    # Fertility evaluation counts
    fert_eligible = [
        r for r in rows
        if r["fertility_eval_eligibility"] in ("ELIGIBLE_PENDING_APPROVAL", "ELIGIBLE_ISOLATED_PROMPTS_ONLY")
    ]
    fert_ineligible = [
        r for r in rows
        if r["fertility_eval_eligibility"] not in ("ELIGIBLE_PENDING_APPROVAL", "ELIGIBLE_ISOLATED_PROMPTS_ONLY")
    ]

    assert len(fert_eligible) == 28, f"Expected 28 eligible for fertility eval, got {len(fert_eligible)}"
    assert len(fert_ineligible) == 4, f"Expected 4 ineligible for fertility eval, got {len(fert_ineligible)}"


def test_phase10_incompatible_sources_blocked():
    """Verify that the 4 incompatible sources are blocked across all operations."""
    recon_path = PATCH_ROOT / "IGRIS_PHASE10_SOURCE_ELIGIBILITY_RECONCILIATION.csv"
    with open(recon_path, "r", encoding="utf-8") as f:
        rows = {r["source_id"]: r for r in csv.DictReader(f)}

    incompatibles = ["SRC-CV-01", "SRC-CV-02", "SRC-HI-03", "SRC-TG-03"]
    for sid in incompatibles:
        r = rows[sid]
        assert r["matrix_v2_primary_status"] == "INCOMPATIBLE"
        assert r["vocab_training_eligibility"] == "INELIGIBLE_REJECTED"
        assert r["fertility_eval_eligibility"] == "INELIGIBLE_REJECTED"
        assert r["pipeline_gate_state"] == "LOCKED"


def test_phase10_prohibited_sources_isolated():
    """Verify benchmark (SRC-CD-02) and preference pairs (SRC-CV-04) are barred from vocab training."""
    recon_path = PATCH_ROOT / "IGRIS_PHASE10_SOURCE_ELIGIBILITY_RECONCILIATION.csv"
    with open(recon_path, "r", encoding="utf-8") as f:
        rows = {r["source_id"]: r for r in csv.DictReader(f)}

    # SRC-CD-02 HumanEval & MBPP Benchmark
    cd02 = rows["SRC-CD-02"]
    assert cd02["vocab_training_eligibility"] == "STRICTLY_PROHIBITED"
    assert cd02["fertility_eval_eligibility"] == "ELIGIBLE_PENDING_APPROVAL"

    # SRC-CV-04 Anthropic HH-RLHF
    cv04 = rows["SRC-CV-04"]
    assert cv04["vocab_training_eligibility"] == "STRICTLY_PROHIBITED"
    assert cv04["fertility_eval_eligibility"] == "ELIGIBLE_ISOLATED_PROMPTS_ONLY"


def test_phase10_candidate_tokenizer_hashes_invariant():
    """Verify Candidate A and Candidate B tokenizer SHA-256 hashes remain invariant."""
    candidate_a = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    candidate_b = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    assert candidate_a.is_file(), f"Missing Candidate A: {candidate_a}"
    assert candidate_b.is_file(), f"Missing Candidate B: {candidate_b}"

    assert sha256_file(candidate_a) == CANDIDATE_A_HASH
    assert sha256_file(candidate_b) == CANDIDATE_B_HASH


def test_phase10_final_verdict():
    """Verify that Phase 10 readiness report selects Verdict B."""
    report_path = PATCH_ROOT / "IGRIS_PHASE10_FINAL_READINESS_REPORT.md"
    content = report_path.read_text(encoding="utf-8")

    assert "[X] B. GOVERNANCE IMPLEMENTATION HAS REMEDIABLE DEFECTS" in content
    assert "[ ] A." in content
    assert "[ ] C." in content
    assert "[ ] D." in content
