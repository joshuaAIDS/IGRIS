"""IGRIS Phase 15 — Standardized Tokenizer Evaluation Engine.

Provides reproducible, read-only evaluation of tokenizer candidates across:
  1. Multilingual Coverage (English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Gujarati, Tanglish)
  2. Tokenization Quality (Fertility, compression, character coverage, byte-fallback rate, UNK rate)
  3. Indic Script Integrity (Matras, viramas, conjuncts, ZWJ/ZWNJ ligatures, NFC round-trip)
  4. Code-Switching & Tanglish (Transitions, spelling variation, mixed-script vocabulary)
  5. Robustness & Adversarial Edge Cases (Empty strings, whitespace, repetitions, emoji, foreign scripts)
  6. Operational Performance (Throughput, latency, memory consumption via tracemalloc)

Guarantees 100% read-only access: never writes or modifies evaluated tokenizer artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import statistics
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Sequence

# Setup paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from igris.tokenizer.strict import (
    STRUCTURAL_COUNT,
    STRUCTURAL_TOKENS,
    VOCAB_SIZE,
    StrictTokenizer,
    load_candidate_a,
    load_candidate_b,
)
from tokenizer_metrics import (
    AggregateCategoryMetrics,
    SampleTokenizationMetrics,
    aggregate_sample_metrics,
    compute_sample_metrics,
)
from tokenizer_multilingual_benchmark import (
    BENCHMARK_SAMPLES,
    BenchmarkSample,
    get_benchmark_categories,
    get_samples_for_category,
)
from tokenizer_unicode_tests import (
    UnicodeIntegrityReport,
    run_unicode_integrity_suite,
)


@dataclass
class PerformanceMetrics:
    encoding_throughput_chars_sec: float
    encoding_throughput_tokens_sec: float
    decoding_throughput_tokens_sec: float
    encoding_latency_ms_per_kb: float
    peak_memory_bytes: int
    peak_memory_kb: float
    short_doc_latency_ms: float
    long_doc_latency_ms: float
    repeat_runs: int


@dataclass
class TokenizerEvaluationSummary:
    candidate_name: str
    artifact_path: str
    sha256_hash: str
    vocab_size: int
    structural_tokens_count: int
    byte_fallback_count: int
    category_metrics: dict[str, AggregateCategoryMetrics]
    overall_metrics: AggregateCategoryMetrics
    unicode_integrity: UnicodeIntegrityReport
    performance: PerformanceMetrics
    environment: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_name": self.candidate_name,
            "artifact_path": self.artifact_path,
            "sha256_hash": self.sha256_hash,
            "vocab_size": self.vocab_size,
            "structural_tokens_count": self.structural_tokens_count,
            "byte_fallback_count": self.byte_fallback_count,
            "category_metrics": {k: asdict(v) for k, v in self.category_metrics.items()},
            "overall_metrics": asdict(self.overall_metrics),
            "unicode_integrity": {
                "total_tests": self.unicode_integrity.total_tests,
                "passed_tests": self.unicode_integrity.passed_tests,
                "failed_tests": self.unicode_integrity.failed_tests,
                "exact_match_pct": self.unicode_integrity.exact_match_pct,
                "nfc_match_pct": self.unicode_integrity.nfc_match_pct,
            },
            "performance": asdict(self.performance),
            "environment": self.environment,
        }


class TokenizerEvaluator:
    """Evaluates a StrictTokenizer candidate in strict read-only mode."""

    def __init__(self, repeat_runs: int = 5):
        self.repeat_runs = repeat_runs

    def evaluate(
        self,
        tokenizer: StrictTokenizer,
        candidate_name: str,
        artifact_path: str | Path,
    ) -> TokenizerEvaluationSummary:
        path = Path(artifact_path)
        raw_bytes = path.read_bytes()
        file_hash = hashlib.sha256(raw_bytes).hexdigest()

        codec = tokenizer.raw_binary_codec()
        byte_fallback_ids = set(codec.id_to_byte.keys())

        # Collect sample metrics across all benchmark samples
        sample_metrics_list: list[SampleTokenizationMetrics] = []
        for sample in BENCHMARK_SAMPLES:
            token_ids = tokenizer.encode_content(sample.text)
            decoded = tokenizer.decode_content(token_ids)

            sm = compute_sample_metrics(
                sample_id=sample.sample_id,
                category=sample.category,
                text=sample.text,
                token_ids=token_ids,
                decoded_text=decoded,
                byte_fallback_ids=byte_fallback_ids,
            )
            sample_metrics_list.append(sm)

        # Aggregate per category
        category_metrics_map: dict[str, AggregateCategoryMetrics] = {}
        for cat in get_benchmark_categories():
            cat_samples = [s for s in sample_metrics_list if s.category == cat]
            category_metrics_map[cat] = aggregate_sample_metrics(cat, cat_samples)

        # Overall aggregate
        overall = aggregate_sample_metrics("Overall", sample_metrics_list)

        # Unicode integrity suite
        unicode_report = run_unicode_integrity_suite(tokenizer)

        # Performance measurements
        perf = self._measure_performance(tokenizer)

        # Environment metadata
        env_info = {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "date": "2026-11-18",
        }

        return TokenizerEvaluationSummary(
            candidate_name=candidate_name,
            artifact_path=str(path),
            sha256_hash=file_hash,
            vocab_size=tokenizer.vocab_size,
            structural_tokens_count=len(STRUCTURAL_TOKENS),
            byte_fallback_count=len(byte_fallback_ids),
            category_metrics=category_metrics_map,
            overall_metrics=overall,
            unicode_integrity=unicode_report,
            performance=perf,
            environment=env_info,
        )

    def _measure_performance(self, tokenizer: StrictTokenizer) -> PerformanceMetrics:
        """Measure throughput, latency, and memory overhead."""
        all_texts = [s.text for s in BENCHMARK_SAMPLES if s.text]
        total_chars = sum(len(t) for t in all_texts)
        total_bytes = sum(len(t.encode("utf-8")) for t in all_texts)

        # Warmup
        warmup_token_lists = []
        for t in all_texts:
            toks = tokenizer.encode_content(t)
            warmup_token_lists.append(toks)
            _ = tokenizer.decode_content(toks)

        total_tokens = sum(len(toks) for toks in warmup_token_lists)

        # Measure encoding throughput
        encode_durations = []
        for _ in range(self.repeat_runs):
            t0 = time.perf_counter()
            for t in all_texts:
                _ = tokenizer.encode_content(t)
            t1 = time.perf_counter()
            encode_durations.append(t1 - t0)

        # Measure decoding throughput
        decode_durations = []
        for _ in range(self.repeat_runs):
            t0 = time.perf_counter()
            for toks in warmup_token_lists:
                _ = tokenizer.decode_content(toks)
            t1 = time.perf_counter()
            decode_durations.append(t1 - t0)

        mean_enc_dur = statistics.mean(encode_durations) if encode_durations else 1e-6
        mean_dec_dur = statistics.mean(decode_durations) if decode_durations else 1e-6

        chars_per_sec = total_chars / mean_enc_dur if mean_enc_dur > 0 else 0.0
        tokens_per_sec = total_tokens / mean_enc_dur if mean_enc_dur > 0 else 0.0
        dec_tokens_per_sec = total_tokens / mean_dec_dur if mean_dec_dur > 0 else 0.0

        kb_total = total_bytes / 1024.0
        latency_ms_per_kb = ((mean_enc_dur * 1000.0) / kb_total) if kb_total > 0 else 0.0

        # Short doc latency (single sentence ~50 chars)
        short_text = "The quick brown fox jumps over the lazy dog."
        t0 = time.perf_counter()
        for _ in range(100):
            _ = tokenizer.encode_content(short_text)
        short_latency_ms = ((time.perf_counter() - t0) / 100.0) * 1000.0

        # Long doc latency (document ~2000 chars)
        long_text = short_text * 40
        t0 = time.perf_counter()
        for _ in range(20):
            _ = tokenizer.encode_content(long_text)
        long_latency_ms = ((time.perf_counter() - t0) / 20.0) * 1000.0

        # Peak memory measurement via tracemalloc
        tracemalloc.start()
        tracemalloc.reset_peak()
        for t in all_texts:
            toks = tokenizer.encode_content(t)
            _ = tokenizer.decode_content(toks)
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return PerformanceMetrics(
            encoding_throughput_chars_sec=round(chars_per_sec, 2),
            encoding_throughput_tokens_sec=round(tokens_per_sec, 2),
            decoding_throughput_tokens_sec=round(dec_tokens_per_sec, 2),
            encoding_latency_ms_per_kb=round(latency_ms_per_kb, 4),
            peak_memory_bytes=peak_bytes,
            peak_memory_kb=round(peak_bytes / 1024.0, 2),
            short_doc_latency_ms=round(short_latency_ms, 4),
            long_doc_latency_ms=round(long_latency_ms, 4),
            repeat_runs=self.repeat_runs,
        )


def evaluate_candidates(
    path_a: str | Path | None = None,
    path_b: str | Path | None = None,
) -> tuple[TokenizerEvaluationSummary, TokenizerEvaluationSummary]:
    """Convenience helper to evaluate Candidate A and Candidate B together."""
    artifacts_dir = _PATCH_ROOT / "artifacts" / "tokenizer"
    actual_path_a = Path(path_a or (artifacts_dir / "candidate_a" / "tokenizer.json"))
    actual_path_b = Path(path_b or (artifacts_dir / "candidate_b" / "tokenizer.model"))

    tok_a = load_candidate_a(str(actual_path_a))
    tok_b = load_candidate_b(str(actual_path_b))

    evaluator = TokenizerEvaluator()
    summary_a = evaluator.evaluate(tok_a, "Candidate A (ByteLevel BPE)", actual_path_a)
    summary_b = evaluator.evaluate(tok_b, "Candidate B (SentencePiece Unigram)", actual_path_b)

    return summary_a, summary_b


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IGRIS Phase 15 Tokenizer Evaluation")
    parser.add_argument("--candidate", choices=["a", "b", "both"], default="both")
    args = parser.parse_args()

    artifacts_dir = _PATCH_ROOT / "artifacts" / "tokenizer"
    path_a = artifacts_dir / "candidate_a" / "tokenizer.json"
    path_b = artifacts_dir / "candidate_b" / "tokenizer.model"

    evaluator = TokenizerEvaluator()

    if args.candidate in ["a", "both"]:
        tok_a = load_candidate_a(str(path_a))
        res_a = evaluator.evaluate(tok_a, "Candidate A", path_a)
        print("=== Candidate A Summary ===")
        print(f"SHA-256: {res_a.sha256_hash}")
        print(f"Overall Fertility (tokens/word): {res_a.overall_metrics.avg_tokens_per_word}")
        print(f"Overall Compression (chars/tok): {res_a.overall_metrics.avg_chars_per_token}")
        print(f"Encoding Throughput (chars/s): {res_a.performance.encoding_throughput_chars_sec}")

    if args.candidate in ["b", "both"]:
        tok_b = load_candidate_b(str(path_b))
        res_b = evaluator.evaluate(tok_b, "Candidate B", path_b)
        print("=== Candidate B Summary ===")
        print(f"SHA-256: {res_b.sha256_hash}")
        print(f"Overall Fertility (tokens/word): {res_b.overall_metrics.avg_tokens_per_word}")
        print(f"Overall Compression (chars/tok): {res_b.overall_metrics.avg_chars_per_token}")
        print(f"Encoding Throughput (chars/s): {res_b.performance.encoding_throughput_chars_sec}")
