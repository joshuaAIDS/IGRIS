"""IGRIS Phase 15 — Candidate Comparison Engine.

Executes side-by-side comparative evaluation of Candidate A (ByteLevel BPE)
and Candidate B (SentencePiece Unigram) on identical standardized corpora.
Generates structured comparative telemetry and outputs:
  - reports/phase15/candidate_comparison.json
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Ensure patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
import sys
if _PATCH_SCRIPTS not in sys.path:
    sys.path.insert(0, _PATCH_SCRIPTS)

from tokenizer_evaluation import (
    TokenizerEvaluationSummary,
    evaluate_candidates,
)

REPORTS_DIR = _PATCH_ROOT / "reports" / "phase15"


@dataclass
class ComparativeCategoryRow:
    category: str
    cand_a_tokens: int
    cand_b_tokens: int
    cand_a_fertility: float
    cand_b_fertility: float
    fertility_diff_pct: float  # (B - A) / A * 100
    cand_a_chars_per_tok: float
    cand_b_chars_per_tok: float
    cand_a_exact_rt_pct: float
    cand_b_exact_rt_pct: float


@dataclass
class CandidateComparisonSummary:
    timestamp: str
    candidate_a: dict[str, Any]
    candidate_b: dict[str, Any]
    category_comparison: list[ComparativeCategoryRow]
    overall_comparison: dict[str, Any]
    performance_comparison: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "candidate_a": self.candidate_a,
            "candidate_b": self.candidate_b,
            "category_comparison": [asdict(r) for r in self.category_comparison],
            "overall_comparison": self.overall_comparison,
            "performance_comparison": self.performance_comparison,
        }


def run_candidate_comparison(
    path_a: Path | str | None = None,
    path_b: Path | str | None = None,
    output_dir: Path | str | None = None,
) -> CandidateComparisonSummary:
    """Run full comparative evaluation and persist structured comparison JSON."""
    out_dir = Path(output_dir or REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_a, summary_b = evaluate_candidates(path_a, path_b)

    # Per-category comparison
    rows: list[ComparativeCategoryRow] = []
    all_categories = list(summary_a.category_metrics.keys())

    for cat in all_categories:
        ma = summary_a.category_metrics[cat]
        mb = summary_b.category_metrics.get(cat)
        if not mb:
            continue

        fert_diff = ((mb.avg_tokens_per_word - ma.avg_tokens_per_word) / ma.avg_tokens_per_word * 100.0) if ma.avg_tokens_per_word > 0 else 0.0

        rows.append(
            ComparativeCategoryRow(
                category=cat,
                cand_a_tokens=ma.total_tokens,
                cand_b_tokens=mb.total_tokens,
                cand_a_fertility=ma.avg_tokens_per_word,
                cand_b_fertility=mb.avg_tokens_per_word,
                fertility_diff_pct=round(fert_diff, 2),
                cand_a_chars_per_tok=ma.avg_chars_per_token,
                cand_b_chars_per_tok=mb.avg_chars_per_token,
                cand_a_exact_rt_pct=ma.round_trip_exact_pct,
                cand_b_exact_rt_pct=mb.round_trip_exact_pct,
            )
        )

    # Overall comparison
    oa = summary_a.overall_metrics
    ob = summary_b.overall_metrics
    overall_fert_diff = ((ob.avg_tokens_per_word - oa.avg_tokens_per_word) / oa.avg_tokens_per_word * 100.0) if oa.avg_tokens_per_word > 0 else 0.0

    overall_comp = {
        "cand_a_total_tokens": oa.total_tokens,
        "cand_b_total_tokens": ob.total_tokens,
        "cand_a_overall_fertility": oa.avg_tokens_per_word,
        "cand_b_overall_fertility": ob.avg_tokens_per_word,
        "fertility_diff_pct": round(overall_fert_diff, 2),
        "cand_a_compression_chars_per_token": oa.avg_chars_per_token,
        "cand_b_compression_chars_per_token": ob.avg_chars_per_token,
        "cand_a_exact_round_trip_pct": oa.round_trip_exact_pct,
        "cand_b_exact_round_trip_pct": ob.round_trip_exact_pct,
        "cand_a_unknown_token_rate": oa.unknown_token_rate,
        "cand_b_unknown_token_rate": ob.unknown_token_rate,
        "cand_a_byte_fallback_rate": oa.byte_fallback_rate,
        "cand_b_byte_fallback_rate": ob.byte_fallback_rate,
    }

    # Performance comparison
    pa = summary_a.performance
    pb = summary_b.performance

    enc_speedup = (pb.encoding_throughput_chars_sec / pa.encoding_throughput_chars_sec) if pa.encoding_throughput_chars_sec > 0 else 1.0
    dec_speedup = (pb.decoding_throughput_tokens_sec / pa.decoding_throughput_tokens_sec) if pa.decoding_throughput_tokens_sec > 0 else 1.0

    perf_comp = {
        "cand_a_enc_throughput_chars_sec": pa.encoding_throughput_chars_sec,
        "cand_b_enc_throughput_chars_sec": pb.encoding_throughput_chars_sec,
        "encoding_throughput_ratio_b_over_a": round(enc_speedup, 2),
        "cand_a_dec_throughput_tokens_sec": pa.decoding_throughput_tokens_sec,
        "cand_b_dec_throughput_tokens_sec": pb.decoding_throughput_tokens_sec,
        "decoding_throughput_ratio_b_over_a": round(dec_speedup, 2),
        "cand_a_peak_memory_kb": pa.peak_memory_kb,
        "cand_b_peak_memory_kb": pb.peak_memory_kb,
        "cand_a_short_doc_latency_ms": pa.short_doc_latency_ms,
        "cand_b_short_doc_latency_ms": pb.short_doc_latency_ms,
        "cand_a_long_doc_latency_ms": pa.long_doc_latency_ms,
        "cand_b_long_doc_latency_ms": pb.long_doc_latency_ms,
    }

    comparison = CandidateComparisonSummary(
        timestamp="2026-11-18T12:00:00Z",
        candidate_a=summary_a.to_dict(),
        candidate_b=summary_b.to_dict(),
        category_comparison=rows,
        overall_comparison=overall_comp,
        performance_comparison=perf_comp,
    )

    # Save to disk
    json_path = out_dir / "candidate_comparison.json"
    json_path.write_text(json.dumps(comparison.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    return comparison


if __name__ == "__main__":
    comp = run_candidate_comparison()
    print("Comparative evaluation complete.")
    print("Saved JSON to:", REPORTS_DIR / "candidate_comparison.json")
    print(f"Overall Fertility: Candidate A={comp.overall_comparison['cand_a_overall_fertility']}, Candidate B={comp.overall_comparison['cand_b_overall_fertility']}")
    print(f"Encoding Throughput (chars/s): Candidate A={comp.performance_comparison['cand_a_enc_throughput_chars_sec']}, Candidate B={comp.performance_comparison['cand_b_enc_throughput_chars_sec']}")
