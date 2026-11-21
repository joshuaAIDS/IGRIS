"""
IGRIS Phase 25 — End-to-End Synthetic Dataset Processing Pipeline v2
=====================================================================
Integrates all Phase 24 / Phase 25 data-engineering components:
1. Input validation
2. Unicode normalization (UnicodeProcessorV2)
3. Language identification (LanguageIdentifierV2)
4. Tanglish code-switch analysis (TanglishAnalyzer)
5. Text quality filtering (QualityFilterV2)
6. Multi-level duplicate detection (DuplicateDetectorV2)
7. Record classification & decisioning
8. Dataset manifest generation
9. Quality reporting (LanguageQualityReporter)

Preserves full audit trail: original inputs, transformations, rejection reasons.
No silent record deletion.
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from duplicate_detector_v2 import DuplicateDetectorV2, DupResult
from language_identifier_v2 import LanguageIdentifierV2, LangIDResult
from quality_filter_v2 import QualityConfigV2, QualityFilterV2, QualityVerdict
from tanglish_analyzer import TanglishAnalysis, TanglishAnalyzer
from unicode_processor_v2 import UnicodeProcessorV2, UnicodeReport


@dataclass
class RawRecord:
    """Incoming unvalidated record."""
    id: str
    text: str
    source_id: str = "SYNTHETIC_BENCHMARK"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedRecord:
    """Fully processed record with full transformation provenance."""
    id: str
    original_text: str
    normalized_text: str
    source_id: str
    
    # Stage 1: Input Validation
    input_valid: bool
    input_validation_notes: Optional[str]

    # Stage 2: Unicode Normalization
    original_char_count: int
    normalized_char_count: int
    is_nfc_original: bool
    has_replacement_char: bool
    control_chars_removed: int
    tamil_combining_preserved: int
    virama_preserved: int
    zwj_zwnj_preserved: int
    unicode_malformed_sequences: List[str]
    script_distribution: Dict[str, float]

    # Stage 3: Language Identification
    language_label: str
    language_confidence: float
    is_code_mixed: bool
    language_sublabel: Optional[str]

    # Stage 4: Tanglish Analysis
    is_tanglish_plausible: Optional[bool]
    code_switch_points_count: int
    discourse_markers: List[str]
    romanized_candidates: List[str]
    tamil_suffixes: List[str]

    # Stage 5: Quality Filtering
    quality_passed: bool
    quality_reasons: List[str]
    word_count: int
    url_ratio: float
    punct_ratio: float

    # Stage 6: Duplicate Detection
    is_duplicate: bool
    duplicate_type: str
    duplicate_matched_id: Optional[str]
    duplicate_similarity: float

    # Stage 7: Record Classification
    final_action: str  # ACCEPTED, REJECTED, DUPLICATE_FLAGGED
    rejection_reasons: List[str]

    # Provenance and Timestamps
    sha256_original: str
    sha256_normalized: str
    timestamp_utc: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DatasetPipelineV2:
    """
    Orchestrates the 9-stage Phase 25 data-engineering pipeline.
    Deterministic, reproducible, non-destructive.
    """

    def __init__(
        self,
        quality_config: Optional[QualityConfigV2] = None,
        near_dup_threshold: float = 0.80,
        min_lang_confidence: float = 0.35,
    ):
        self.quality_config = quality_config or QualityConfigV2()
        self.near_dup_threshold = near_dup_threshold
        self.min_lang_confidence = min_lang_confidence

        self.unicode_proc = UnicodeProcessorV2()
        self.lang_id = LanguageIdentifierV2(min_confidence=min_lang_confidence)
        self.tanglish_analyzer = TanglishAnalyzer()
        self.quality_filter = QualityFilterV2(self.quality_config)
        self.dup_detector = DuplicateDetectorV2(near_dup_threshold=near_dup_threshold)

    def reset_state(self):
        """Reset internal state (e.g. duplicate index) for reproducible re-runs."""
        self.dup_detector = DuplicateDetectorV2(near_dup_threshold=self.near_dup_threshold)

    def process_record(self, record: RawRecord) -> ProcessedRecord:
        now_utc = datetime.now(timezone.utc).isoformat()
        orig_text = record.text if record.text is not None else ""
        sha256_orig = hashlib.sha256(orig_text.encode("utf-8")).hexdigest()

        # Stage 1: Input Validation
        input_valid = True
        input_notes = None
        if not record.id or not isinstance(record.id, str):
            input_valid = False
            input_notes = "Invalid or missing record ID"
        elif not isinstance(orig_text, str):
            input_valid = False
            input_notes = "Text is not a string instance"

        # Stage 2: Unicode Normalization
        normalized_text, u_report = self.unicode_proc.normalize(orig_text)
        sha256_norm = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

        # Stage 3: Language Identification
        lang_res = self.lang_id.identify(normalized_text)

        # Stage 4: Tanglish Analysis (if applicable)
        is_tanglish_or_mixed = (
            lang_res.label == "TANGLISH"
            or lang_res.is_code_mixed
            or ("TAMIL" in lang_res.detected_scripts and "LATIN" in lang_res.detected_scripts)
        )
        if is_tanglish_or_mixed and len(normalized_text.strip()) > 0:
            t_analysis = self.tanglish_analyzer.analyze(normalized_text)
            t_plausible = t_analysis.is_structurally_plausible
            sw_count = len(t_analysis.code_switch_points)
            d_markers = t_analysis.discourse_markers_found
            r_cands = t_analysis.romanized_tamil_candidates
            t_sfx = t_analysis.tamil_suffixes_detected
        else:
            t_plausible = None
            sw_count = 0
            d_markers = []
            r_cands = []
            t_sfx = []

        # Stage 5: Quality Filtering
        q_verdict = self.quality_filter.evaluate(normalized_text)

        # Stage 6: Duplicate Detection
        # Only check duplicate if input was valid and not empty
        if input_valid and len(normalized_text.strip()) > 0:
            dup_res = self.dup_detector.check_and_register(record.id, normalized_text)
        else:
            dup_res = DupResult(False, "NONE", None, 0.0, notes="Skipped duplicate check")

        # Stage 7: Record Classification / Decision
        rejection_reasons = []
        if not input_valid:
            final_action = "REJECTED"
            rejection_reasons.append(f"INPUT_VALIDATION_FAILURE: {input_notes}")
        elif lang_res.label == "OUT_OF_SCOPE":
            final_action = "REJECTED"
            rejection_reasons.append(f"OUT_OF_SCOPE_LANGUAGE: {lang_res.sublabel or 'NON_TARGET'}")
        elif not q_verdict.passed:
            final_action = "REJECTED"
            rejection_reasons.extend(q_verdict.rejection_reasons)
        elif dup_res.is_duplicate:
            final_action = "DUPLICATE_FLAGGED"
            rejection_reasons.append(f"DUPLICATE_{dup_res.dup_type}: matches {dup_res.matched_id}")
        elif lang_res.label == "UNKNOWN":
            final_action = "REJECTED"
            rejection_reasons.append("UNRESOLVED_LANGUAGE_UNKNOWN")
        else:
            # Must be valid target language: TAMIL, ENGLISH, TANGLISH
            final_action = "ACCEPTED"

        return ProcessedRecord(
            id=record.id,
            original_text=orig_text,
            normalized_text=normalized_text,
            source_id=record.source_id,
            input_valid=input_valid,
            input_validation_notes=input_notes,
            original_char_count=u_report.original_length,
            normalized_char_count=u_report.normalized_length,
            is_nfc_original=u_report.is_nfc_original,
            has_replacement_char=u_report.has_replacement_char,
            control_chars_removed=u_report.control_chars_removed,
            tamil_combining_preserved=u_report.tamil_combining_marks_preserved,
            virama_preserved=u_report.virama_sequences_preserved,
            zwj_zwnj_preserved=u_report.zwj_zwnj_preserved,
            unicode_malformed_sequences=u_report.malformed_sequences,
            script_distribution=u_report.script_distribution,
            language_label=lang_res.label,
            language_confidence=lang_res.confidence,
            is_code_mixed=lang_res.is_code_mixed,
            language_sublabel=lang_res.sublabel,
            is_tanglish_plausible=t_plausible,
            code_switch_points_count=sw_count,
            discourse_markers=d_markers,
            romanized_candidates=r_cands,
            tamil_suffixes=t_sfx,
            quality_passed=q_verdict.passed,
            quality_reasons=q_verdict.rejection_reasons,
            word_count=q_verdict.word_count,
            url_ratio=q_verdict.url_ratio,
            punct_ratio=q_verdict.punct_ratio,
            is_duplicate=dup_res.is_duplicate,
            duplicate_type=dup_res.dup_type,
            duplicate_matched_id=dup_res.matched_id,
            duplicate_similarity=dup_res.similarity,
            final_action=final_action,
            rejection_reasons=rejection_reasons,
            sha256_original=sha256_orig,
            sha256_normalized=sha256_norm,
            timestamp_utc=now_utc,
            metadata=record.metadata,
        )

    def process_dataset(
        self, records: List[RawRecord]
    ) -> Tuple[List[ProcessedRecord], Dict[str, Any]]:
        """Process full dataset and compile summary telemetry."""
        start_time = time.time()
        processed: List[ProcessedRecord] = []
        action_counts = {"ACCEPTED": 0, "REJECTED": 0, "DUPLICATE_FLAGGED": 0}
        lang_counts = {"TAMIL": 0, "ENGLISH": 0, "TANGLISH": 0, "UNKNOWN": 0, "OUT_OF_SCOPE": 0}
        rejection_reasons_dist: Dict[str, int] = {}

        for rec in records:
            p_rec = self.process_record(rec)
            processed.append(p_rec)
            action_counts[p_rec.final_action] = action_counts.get(p_rec.final_action, 0) + 1
            lang_counts[p_rec.language_label] = lang_counts.get(p_rec.language_label, 0) + 1
            for r in p_rec.rejection_reasons:
                rejection_reasons_dist[r] = rejection_reasons_dist.get(r, 0) + 1

        elapsed = time.time() - start_time

        telemetry = {
            "total_records": len(records),
            "processed_records": len(processed),
            "action_counts": action_counts,
            "acceptance_rate": round(action_counts["ACCEPTED"] / len(records), 4) if records else 0.0,
            "rejection_rate": round(action_counts["REJECTED"] / len(records), 4) if records else 0.0,
            "duplicate_rate": round(action_counts["DUPLICATE_FLAGGED"] / len(records), 4) if records else 0.0,
            "language_distribution": lang_counts,
            "rejection_reasons_distribution": rejection_reasons_dist,
            "unique_registered_hashes": self.dup_detector.registered_count,
            "pipeline_elapsed_sec": round(elapsed, 4),
        }
        return processed, telemetry
