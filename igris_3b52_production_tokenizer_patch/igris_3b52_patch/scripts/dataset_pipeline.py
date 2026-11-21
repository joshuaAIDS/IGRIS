"""
IGRIS Multilingual Dataset Integrity, Cleaning & Validation Pipeline
====================================================================
Phase 14 Dataset Integrity, Cleaning, and Validation Infrastructure

Implements the 13-Stage Modular Processing Pipeline:
1.  INPUT
2.  SOURCE VERIFICATION
3.  FILE INTEGRITY VALIDATION
4.  FORMAT VALIDATION
5.  TEXT EXTRACTION
6.  UNICODE NORMALIZATION
7.  LANGUAGE IDENTIFICATION
8.  TEXT QUALITY FILTERING
9.  DUPLICATE DETECTION
10. PII SCREENING
11. CONTAMINATION CHECKING
12. PROVENANCE RECORDING
13. VALIDATION REPORT
"""

import hashlib
import json
import os
import re
import stat
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from duplicate_detector import DuplicateDetector, DuplicateMatchResult
from language_identifier import LanguageIdentificationResult, LanguageIdentifier
from privacy_contamination_scanner import (
    BenchmarkContaminationError,
    ContaminationDetectionResult,
    PIIDetectionResult,
    PrivacyContaminationScanner,
)
from quality_filter import QualityConfig, QualityDecision, QualityFilter
from unicode_processor import (
    InvalidEncodingError,
    UnicodeAnalysisReport,
    UnicodeProcessor,
)


class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass


class SourceVerificationError(PipelineError):
    """Raised when source ID is unknown or unauthorized."""
    pass


class FileIntegrityError(PipelineError):
    """Raised when file integrity, size, or magic byte checks fail."""
    pass


class FormatValidationError(PipelineError):
    """Raised when file format is invalid or unsupported."""
    pass


class UnauthorizedDirectoryError(PipelineError):
    """Raised when input directory is outside permitted quarantine boundaries."""
    pass


@dataclass
class ProcessingConfig:
    pipeline_version: str = "IGRIS-P14-V1.0"
    config_version: str = "CONFIG-20261118"
    unicode_form: str = "NFC"
    min_confidence: float = 0.40
    strict_tier_isolation: bool = True
    intended_use: str = "VOCABULARY_TRAINING"
    quality_config: QualityConfig = field(default_factory=QualityConfig)
    allowed_input_dirs: Optional[List[str]] = None


@dataclass
class DocumentProvenanceRecord:
    document_id: str
    source_id: str
    original_file_sha256: str
    pipeline_version: str
    config_version: str
    normalization_version: str
    primary_language: str
    language_confidence: float
    quality_score: float
    quality_passed: bool
    rejection_reasons: List[str]
    duplicate_type: str
    canonical_doc_id: Optional[str]
    pii_status: str
    contamination_detected: bool
    timestamp: str
    prev_hash: str
    entry_hash: str


@dataclass
class DocumentProcessingResult:
    document_id: str
    source_id: str
    raw_sha256: str
    original_text: str
    cleaned_text: str
    unicode_report: UnicodeAnalysisReport
    language_result: LanguageIdentificationResult
    quality_decision: QualityDecision
    duplicate_result: DuplicateMatchResult
    pii_result: PIIDetectionResult
    contamination_result: ContaminationDetectionResult
    final_validation_status: str  # "VALIDATED", "REJECTED_QUALITY", "REJECTED_DUPLICATE", "REJECTED_CONTAMINATION", "QUARANTINED_PII"
    provenance: DocumentProvenanceRecord


class ProvenanceAuditLogger:
    """
    Append-only, cryptographically chained audit logger for dataset processing events.
    """
    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._get_latest_hash()

    def _get_latest_hash(self) -> str:
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return "0" * 64
        last_entry = None
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        last_entry = json.loads(line)
                    except json.JSONDecodeError:
                        pass
        if last_entry and "entry_hash" in last_entry:
            return last_entry["entry_hash"]
        return "0" * 64

    def log_record(self, record_dict: Dict[str, Any]) -> str:
        prev_h = self._last_hash
        payload = f"{record_dict['timestamp']}|{record_dict['document_id']}|{record_dict['source_id']}|{record_dict['original_file_sha256']}|{record_dict['quality_score']}|{record_dict['primary_language']}|{prev_h}"
        entry_h = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        
        record_dict["prev_hash"] = prev_h
        record_dict["entry_hash"] = entry_h

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_dict) + "\n")
            f.flush()

        self._last_hash = entry_h
        return entry_h

    def verify_integrity(self) -> Tuple[bool, int, Optional[str]]:
        """Verify the cryptographic hash chain of the audit log."""
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return True, 0, None

        current_prev = "0" * 64
        count = 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry.get("prev_hash") != current_prev:
                    return False, count, f"Hash chain break at line {line_idx + 1}: expected prev {current_prev}, got {entry.get('prev_hash')}"

                payload = f"{entry['timestamp']}|{entry['document_id']}|{entry['source_id']}|{entry['original_file_sha256']}|{entry['quality_score']}|{entry['primary_language']}|{current_prev}"
                computed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
                if computed != entry.get("entry_hash"):
                    return False, count, f"Entry hash mismatch at line {line_idx + 1}"

                current_prev = entry["entry_hash"]
                count += 1

        return True, count, None


class DatasetProcessingPipeline:
    """
    Modular 13-stage dataset integrity, cleaning, and validation pipeline.
    """
    def __init__(
        self,
        config: Optional[ProcessingConfig] = None,
        duplicate_detector: Optional[DuplicateDetector] = None,
        audit_log_path: Optional[Path] = None
    ):
        self.config = config if config is not None else ProcessingConfig()
        self.unicode_proc = UnicodeProcessor(target_form=self.config.unicode_form)
        self.lang_id = LanguageIdentifier(min_confidence=self.config.min_confidence)
        self.quality_filter = QualityFilter(config=self.config.quality_config)
        self.dup_detector = duplicate_detector if duplicate_detector is not None else DuplicateDetector()
        self.privacy_scanner = PrivacyContaminationScanner()

        if audit_log_path is None:
            audit_log_path = Path(__file__).resolve().parents[2] / "quarantine" / "logs" / "dataset_processing_audit.jsonl"
        self.audit_logger = ProvenanceAuditLogger(audit_log_path)

    def validate_input_directory(self, file_path: Path):
        """Enforce that file is within configured allowed input directories."""
        if self.config.allowed_input_dirs is not None:
            resolved_file = Path(file_path).resolve()
            is_allowed = False
            for allowed in self.config.allowed_input_dirs:
                resolved_allowed = Path(allowed).resolve()
                try:
                    if os.path.commonpath([str(resolved_allowed), str(resolved_file)]) == str(resolved_allowed):
                        is_allowed = True
                        break
                except ValueError:
                    pass
            if not is_allowed:
                raise UnauthorizedDirectoryError(
                    f"File '{file_path}' is outside permitted input directories: {self.config.allowed_input_dirs}"
                )

    def process_document(
        self,
        document_id: str,
        source_id: str,
        text_content: str,
        raw_sha256: Optional[str] = None
    ) -> DocumentProcessingResult:
        """
        Execute full 13-stage processing on a single text document.
        """
        # Validate configuration integrity
        if not self.config.pipeline_version or not self.config.config_version:
            raise PipelineError("Invalid processing configuration: missing version specifiers")

        if raw_sha256 is None:
            raw_sha256 = hashlib.sha256(text_content.encode("utf-8")).hexdigest()

        # Stage 6: Unicode Normalization
        cleaned_text, unicode_rep = self.unicode_proc.clean_and_normalize(text_content)

        # Stage 7: Language Identification
        lang_res = self.lang_id.identify_language(cleaned_text)

        # Stage 8: Quality Filtering
        quality_dec = self.quality_filter.evaluate_document(cleaned_text)

        # Stage 9: Duplicate Detection
        dup_res = self.dup_detector.check_duplicate(
            doc_id=document_id,
            text=cleaned_text,
            raw_sha256=raw_sha256,
            register_if_unique=quality_dec.passed
        )

        # Stage 10: PII Screening
        pii_res = self.privacy_scanner.scan_privacy(cleaned_text)

        # Stage 11: Contamination Checking
        contam_res = self.privacy_scanner.scan_contamination(
            text=cleaned_text,
            source_id=source_id,
            intended_use=self.config.intended_use
        )

        # Determine Final Status
        if contam_res.has_contamination:
            final_status = "REJECTED_CONTAMINATION"
        elif dup_res.is_duplicate:
            final_status = "REJECTED_DUPLICATE"
        elif not quality_dec.passed:
            final_status = "REJECTED_QUALITY"
        elif pii_res.review_status == "QUARANTINED":
            final_status = "QUARANTINED_PII"
        elif pii_res.review_status == "FLAGGED_FOR_REVIEW":
            final_status = "FLAGGED_PII_REVIEW"
        else:
            final_status = "VALIDATED"

        # Stage 12: Provenance Recording
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        prov_dict = {
            "document_id": document_id,
            "source_id": source_id,
            "original_file_sha256": raw_sha256,
            "pipeline_version": self.config.pipeline_version,
            "config_version": self.config.config_version,
            "normalization_version": f"Unicode-15.1.0-{self.config.unicode_form}",
            "primary_language": lang_res.primary_language,
            "language_confidence": lang_res.confidence,
            "quality_score": quality_dec.quality_score,
            "quality_passed": quality_dec.passed,
            "rejection_reasons": quality_dec.rejection_reasons,
            "duplicate_type": dup_res.duplicate_type,
            "canonical_doc_id": dup_res.canonical_doc_id,
            "pii_status": pii_res.review_status,
            "contamination_detected": contam_res.has_contamination,
            "timestamp": now_iso
        }

        entry_h = self.audit_logger.log_record(prov_dict)

        provenance = DocumentProvenanceRecord(
            document_id=document_id,
            source_id=source_id,
            original_file_sha256=raw_sha256,
            pipeline_version=self.config.pipeline_version,
            config_version=self.config.config_version,
            normalization_version=f"Unicode-15.1.0-{self.config.unicode_form}",
            primary_language=lang_res.primary_language,
            language_confidence=lang_res.confidence,
            quality_score=quality_dec.quality_score,
            quality_passed=quality_dec.passed,
            rejection_reasons=quality_dec.rejection_reasons,
            duplicate_type=dup_res.duplicate_type,
            canonical_doc_id=dup_res.canonical_doc_id,
            pii_status=pii_res.review_status,
            contamination_detected=contam_res.has_contamination,
            timestamp=now_iso,
            prev_hash=prov_dict["prev_hash"],
            entry_hash=entry_h
        )

        return DocumentProcessingResult(
            document_id=document_id,
            source_id=source_id,
            raw_sha256=raw_sha256,
            original_text=text_content,
            cleaned_text=cleaned_text,
            unicode_report=unicode_rep,
            language_result=lang_res,
            quality_decision=quality_dec,
            duplicate_result=dup_res,
            pii_result=pii_res,
            contamination_result=contam_res,
            final_validation_status=final_status,
            provenance=provenance
        )

    def process_file(
        self,
        file_path: Path,
        source_id: str,
        expected_sha256: Optional[str] = None
    ) -> List[DocumentProcessingResult]:
        """
        Execute file integrity validation, text extraction, and batch document processing.
        """
        p = Path(file_path)
        self.validate_input_directory(p)

        if not p.exists():
            raise FileIntegrityError(f"Input file does not exist: {p}")

        # Stage 3: File Integrity Validation
        raw_bytes = p.read_bytes()
        file_sha256 = hashlib.sha256(raw_bytes).hexdigest()

        if expected_sha256 and expected_sha256.lower() != file_sha256.lower():
            raise FileIntegrityError(
                f"SHA-256 integrity mismatch: expected {expected_sha256}, got {file_sha256}"
            )

        # Check for executable binary headers
        if raw_bytes.startswith(b"MZ") or raw_bytes.startswith(b"\x7fELF") or raw_bytes.startswith(b"\xca\xfe\xba\xbe"):
            raise FileIntegrityError("Prohibited executable binary header detected in dataset file")

        # Stage 4: Format Validation
        ext = p.suffix.lower()
        if ext not in (".txt", ".json", ".jsonl", ".csv", ".tsv", ".md"):
            raise FormatValidationError(f"Unsupported file format extension: {ext}")

        # Stage 5: Text Extraction
        try:
            text = self.unicode_proc.validate_utf8_bytes(raw_bytes)
        except InvalidEncodingError as e:
            raise FileIntegrityError(f"File encoding validation failed: {e}") from e

        # Extract documents (by line or JSON or full text)
        results = []
        if ext == ".jsonl":
            lines = text.splitlines()
            for line_idx, line in enumerate(lines):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                    doc_text = obj.get("text", obj.get("content", str(obj)))
                    doc_id = f"{p.stem}_{line_idx}"
                except json.JSONDecodeError:
                    doc_text = line
                    doc_id = f"{p.stem}_{line_idx}"
                res = self.process_document(doc_id, source_id, doc_text)
                results.append(res)
        else:
            # Whole document or separated by blank lines
            doc_id = p.stem
            res = self.process_document(doc_id, source_id, text, raw_sha256=file_sha256)
            results.append(res)

        return results


@dataclass
class DatasetQualityMetrics:
    total_documents: int = 0
    successfully_validated: int = 0
    rejected_quality: int = 0
    rejected_duplicate: int = 0
    rejected_contamination: int = 0
    quarantined_pii: int = 0
    empty_documents: int = 0
    language_distribution: Dict[str, int] = field(default_factory=dict)
    script_distribution: Dict[str, int] = field(default_factory=dict)
    duplicate_count: int = 0
    near_duplicate_count: int = 0
    average_document_length_chars: float = 0.0
    median_document_length_chars: float = 0.0
    unicode_validation_failures: int = 0

    @classmethod
    def aggregate(cls, results: List[DocumentProcessingResult]) -> "DatasetQualityMetrics":
        m = cls()
        m.total_documents = len(results)
        if not results:
            return m

        lengths: List[int] = []
        for r in results:
            lengths.append(len(r.cleaned_text))
            status = r.final_validation_status
            if status == "VALIDATED":
                m.successfully_validated += 1
            elif status == "REJECTED_QUALITY":
                m.rejected_quality += 1
            elif status == "REJECTED_DUPLICATE":
                m.rejected_duplicate += 1
            elif status == "REJECTED_CONTAMINATION":
                m.rejected_contamination += 1
            elif "PII" in status:
                m.quarantined_pii += 1

            if "EMPTY_DOCUMENT" in r.quality_decision.rejection_reasons:
                m.empty_documents += 1

            lang = r.language_result.primary_language
            m.language_distribution[lang] = m.language_distribution.get(lang, 0) + 1

            script = r.unicode_report.primary_script
            m.script_distribution[script] = m.script_distribution.get(script, 0) + 1

            if r.duplicate_result.is_duplicate:
                m.duplicate_count += 1
                if r.duplicate_result.duplicate_type == "NEAR_DUPLICATE":
                    m.near_duplicate_count += 1

        lengths.sort()
        m.average_document_length_chars = round(sum(lengths) / len(lengths), 2)
        mid = len(lengths) // 2
        m.median_document_length_chars = float(lengths[mid] if len(lengths) % 2 == 1 else (lengths[mid - 1] + lengths[mid]) / 2)

        return m
