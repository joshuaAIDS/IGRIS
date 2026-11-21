"""IGRIS tokenizer acceptance runner (stdlib only; no training/install)."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from .acceptance_config import (
    ACCEPTANCE_SPEC_VERSION, CANDIDATES, PROJECT_VERSION, STATUSES,
    TEST_GROUPS, VOCAB_SIZE, STRUCTURAL_TOKENS, STRUCTURAL_TOKEN_IDS,
)
from .candidate_adapters import CandidateAdapter


@dataclass
class TestResult:
    test_id: str
    name: str
    status: str
    detail: str = ""


def validate_static_contract() -> list[TestResult]:
    checks = [
        ("TS-API-STATIC-01", "12 structural tokens", len(STRUCTURAL_TOKENS) == 12),
        ("TS-API-STATIC-02", "Structural tokens unique",
         len(set(STRUCTURAL_TOKENS)) == 12),
        ("TS-API-STATIC-03", "Structural IDs fixed at 0..11",
         tuple(STRUCTURAL_TOKEN_IDS.values()) == tuple(range(12))),
        ("TS-API-STATIC-04", "Vocabulary size fixed at 32768",
         VOCAB_SIZE == 32768),
    ]
    return [
        TestResult(test_id, name, "PASS" if ok else "FAIL",
                   "Static contract assertion")
        for test_id, name, ok in checks
    ]


def build_candidate_results(candidate: str, artifact_path: Optional[str]) -> list[TestResult]:
    adapter_result = CandidateAdapter(candidate, artifact_path).load()
    # All artifact-dependent groups remain explicitly blocked until a real
    # trained artifact and production adapter are available.
    groups = {
        "TS-VAL": "Strict content-ID and input validation",
        "TS-UNI": "Unicode NFC and exact-mode behavior",
        "TS-SEC": "Structural-token escaping and malformed escapes",
        "TS-BAT": "Batch API behavior and ordering",
        "TS-REN": "Trusted sequence rendering",
        "TS-BIN": "Candidate-specific arbitrary-byte round trips",
        "TS-META": "Artifact metadata and save/reload validation",
        "TS-API": "Common public API compatibility",
        "TS-DET": "Deterministic encoding and reload behavior",
        "TS-ERR": "Runtime error behavior",
    }
    results = []
    for group, name in groups.items():
        results.append(TestResult(
            f"{group}-{candidate}-ARTIFACT",
            name,
            "BLOCKED",
            adapter_result.reason
        ))
    return results


def summarize(results: list[TestResult]) -> dict:
    counts = {status: sum(r.status == status for r in results) for status in STATUSES}
    mandatory_failure = counts["FAIL"] > 0 or counts["BLOCKED"] > 0 or counts["NOT TESTED"] > 0
    return {
        "total": len(results),
        "counts": counts,
        "overall": "NOT APPROVED" if mandatory_failure else "ACCEPTED",
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="IGRIS v2.2.28 tokenizer acceptance runner"
    )
    parser.add_argument("--candidate", choices=("A", "B", "all"), default="all")
    parser.add_argument("--candidate-a-artifact")
    parser.add_argument("--candidate-b-artifact")
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args(argv)

    results = validate_static_contract()
    selected = CANDIDATES if args.candidate == "all" else (args.candidate,)

    for candidate in selected:
        artifact = (
            args.candidate_a_artifact if candidate == "A"
            else args.candidate_b_artifact
        )
        results.extend(build_candidate_results(candidate, artifact))

    report = {
        "project": "IGRIS",
        "project_version": PROJECT_VERSION,
        "acceptance_spec_version": ACCEPTANCE_SPEC_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "selected_candidates": list(selected),
        "results": [asdict(r) for r in results],
        "summary": summarize(results),
        "production_acceptance": "NOT APPROVED",
        "note": "Scaffold mode: artifact-dependent tests are blocked; no training is performed.",
    }

    print("IGRIS v2.2.28 TOKENIZER ACCEPTANCE REPORT")
    print("=" * 62)
    for result in results:
        print(f"{result.test_id:28} {result.status:12} {result.name}")
        if result.detail:
            print(f"    {result.detail}")
    print("-" * 62)
    print(json.dumps(report["summary"], indent=2))
    print("Production acceptance:", report["production_acceptance"])

    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print("JSON report written:", args.json_report)

    return 1 if report["summary"]["overall"] != "ACCEPTED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
