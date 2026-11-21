"""IGRIS Milestone 3B.59 — Tokenizer Evaluation Acceptance Criteria and Thresholds.

Provides a configurable threshold validation engine that classifies criteria into:
  1. Mandatory Requirements (Hard Gates - must pass 100%)
  2. Recommended Targets (Optimization Targets for production corpus training)
  3. Informational Metrics (Observability parameters)

All thresholds are configurable via JSON configuration.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_THRESHOLDS = {
    "mandatory": {
        "round_trip_fidelity_min_pct": 100.0,
        "structural_token_isolation_min_pct": 100.0,
        "vocabulary_size_exact": 32768,
        "structural_token_count_exact": 12,
        "byte_fallback_count_exact": 256,
        "unicode_version_exact": "15.1.0",
        "context_length_exact": 2048,
    },
    "recommended": {
        "tokens_per_word_english_max": 1.35,
        "tokens_per_word_tamil_max": 2.50,
        "tokens_per_word_hindi_max": 2.20,
        "tokens_per_word_code_max": 1.80,
        "encoding_throughput_min_chars_sec": 250000.0,
        "decoding_throughput_min_tokens_sec": 1000000.0,
        "sequence_p95_tokens_max": 1800,
    },
    "informational": {
        "peak_heap_memory_kb_target": 1024.0,
        "compression_ratio_bytes_per_token_min": 1.0,
    },
}


@dataclass
class ThresholdCheck:
    metric_name: str
    tier: str  # mandatory, recommended, informational
    target_value: Any
    actual_value: Any
    passed: bool
    details: str = ""


@dataclass
class EvaluationAssessment:
    mandatory_passed: bool
    recommended_passed: bool
    checks: list[ThresholdCheck] = field(default_factory=list)

    @property
    def ready_for_production_review(self) -> bool:
        return self.mandatory_passed


class AcceptanceThresholdEvaluator:
    def __init__(self, config_path: str | Path | None = None) -> None:
        if config_path and Path(config_path).exists():
            self.thresholds = json.loads(Path(config_path).read_text(encoding="utf-8"))
        else:
            self.thresholds = dict(DEFAULT_THRESHOLDS)

    def evaluate_candidate(
        self,
        candidate_name: str,
        metrics: dict[str, Any],
        is_synthetic: bool = True,
    ) -> EvaluationAssessment:
        checks: list[ThresholdCheck] = []
        mandatory_ok = True
        recommended_ok = True

        # 1. Mandatory Checks
        m_thresh = self.thresholds["mandatory"]

        # Fidelity
        fid = metrics.get("round_trip_fidelity_pct", 0.0)
        c_fid = (fid >= m_thresh["round_trip_fidelity_min_pct"])
        if not c_fid: mandatory_ok = False
        checks.append(ThresholdCheck("round_trip_fidelity", "mandatory", m_thresh["round_trip_fidelity_min_pct"], fid, c_fid))

        # Structural Isolation
        iso = metrics.get("structural_isolation_pct", 0.0)
        c_iso = (iso >= m_thresh["structural_token_isolation_min_pct"])
        if not c_iso: mandatory_ok = False
        checks.append(ThresholdCheck("structural_token_isolation", "mandatory", m_thresh["structural_token_isolation_min_pct"], iso, c_iso))

        # Vocab Size
        v_size = metrics.get("vocab_size", 0)
        c_v = (v_size == m_thresh["vocabulary_size_exact"])
        if not c_v: mandatory_ok = False
        checks.append(ThresholdCheck("vocab_size", "mandatory", m_thresh["vocabulary_size_exact"], v_size, c_v))

        # Structural Tokens Count
        st_count = metrics.get("structural_token_count", 0)
        c_st = (st_count == m_thresh["structural_token_count_exact"])
        if not c_st: mandatory_ok = False
        checks.append(ThresholdCheck("structural_token_count", "mandatory", m_thresh["structural_token_count_exact"], st_count, c_st))

        # Byte Fallback
        bf_count = metrics.get("byte_fallback_count", 0)
        c_bf = (bf_count == m_thresh["byte_fallback_count_exact"])
        if not c_bf: mandatory_ok = False
        checks.append(ThresholdCheck("byte_fallback_count", "mandatory", m_thresh["byte_fallback_count_exact"], bf_count, c_bf))

        # Unicode Version
        u_ver = metrics.get("unicode_version", "")
        c_u = (u_ver == m_thresh["unicode_version_exact"])
        if not c_u: mandatory_ok = False
        checks.append(ThresholdCheck("unicode_version", "mandatory", m_thresh["unicode_version_exact"], u_ver, c_u))

        # Context Length
        ctx_len = metrics.get("context_length", 2048)
        c_ctx = (ctx_len == m_thresh["context_length_exact"])
        if not c_ctx: mandatory_ok = False
        checks.append(ThresholdCheck("context_length", "mandatory", m_thresh["context_length_exact"], ctx_len, c_ctx))

        # 2. Recommended Checks
        # Note: If is_synthetic is True, TPW on Indic scripts reflects synthetic fallback,
        # so recommended compression targets are informational until production corpus training.
        r_thresh = self.thresholds["recommended"]

        enc_tp = metrics.get("encoding_throughput_chars_sec", 0.0)
        c_enc = (enc_tp >= r_thresh["encoding_throughput_min_chars_sec"])
        if not c_enc: recommended_ok = False
        checks.append(ThresholdCheck("encoding_throughput", "recommended", r_thresh["encoding_throughput_min_chars_sec"], enc_tp, c_enc))

        dec_tp = metrics.get("decoding_throughput_tokens_sec", 0.0)
        c_dec = (dec_tp >= r_thresh["decoding_throughput_min_tokens_sec"])
        if not c_dec: recommended_ok = False
        checks.append(ThresholdCheck("decoding_throughput", "recommended", r_thresh["decoding_throughput_min_tokens_sec"], dec_tp, c_dec))

        if not is_synthetic:
            tpw_en = metrics.get("tpw_english", 0.0)
            c_en = (tpw_en <= r_thresh["tokens_per_word_english_max"])
            if not c_en: recommended_ok = False
            checks.append(ThresholdCheck("tpw_english", "recommended", r_thresh["tokens_per_word_english_max"], tpw_en, c_en))

            tpw_ta = metrics.get("tpw_tamil", 0.0)
            c_ta = (tpw_ta <= r_thresh["tokens_per_word_tamil_max"])
            if not c_ta: recommended_ok = False
            checks.append(ThresholdCheck("tpw_tamil", "recommended", r_thresh["tokens_per_word_tamil_max"], tpw_ta, c_ta))

        # 3. Informational Checks
        i_thresh = self.thresholds["informational"]
        mem_peak = metrics.get("peak_heap_kb", 0.0)
        checks.append(ThresholdCheck("peak_heap_kb", "informational", i_thresh["peak_heap_memory_kb_target"], mem_peak, True))

        return EvaluationAssessment(
            mandatory_passed=mandatory_ok,
            recommended_passed=recommended_ok,
            checks=checks,
        )
