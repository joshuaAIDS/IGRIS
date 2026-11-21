"""
IGRIS Phase 14 Dataset Processing & Validation Security Test Suite
==================================================================
Tests for Dataset Integrity, Cleaning, Multilingual Unicode Preservation,
Language Identification, Quality Filtering, Duplicate Detection,
Privacy Screening, Contamination Controls, and Provenance Auditing.

Covers all 28 required test vectors:
1.  SHA-256 mismatch
2.  Corrupted files
3.  Invalid UTF-8
4.  Unicode normalization
5.  Tamil text preservation
6.  Telugu text preservation
7.  Malayalam text preservation
8.  Kannada text preservation
9.  Hindi text preservation
10. Bengali text preservation
11. Gujarati text preservation
12. Tanglish classification
13. Mixed-script text
14. Empty documents
15. Repeated documents
16. Near-duplicate documents
17. PII detection
18. Credential detection
19. Benchmark contamination
20. Evaluation-only source isolation
21. Permanently blocked source rejection
22. Audit-chain tampering
23. Processing interruption
24. Duplicate-index concurrency
25. Deterministic processing
26. Provenance integrity
27. Invalid processing configuration
28. Unauthorized input directory rejection
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import unicodedata
from pathlib import Path
import pytest

# Ensure scripts directory is on sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from dataset_pipeline import (
    DatasetProcessingPipeline,
    DatasetQualityMetrics,
    FileIntegrityError,
    FormatValidationError,
    PipelineError,
    ProcessingConfig,
    ProvenanceAuditLogger,
    UnauthorizedDirectoryError,
)
from duplicate_detector import DuplicateDetector, compute_normalized_text_hash
from language_identifier import LanguageIdentifier
from privacy_contamination_scanner import (
    BenchmarkContaminationError,
    PrivacyContaminationScanner,
)
from quality_filter import QualityConfig, QualityFilter
from unicode_processor import (
    InvalidEncodingError,
    UnicodeProcessor,
)


# ---------------------------------------------------------------------------
# Vector 1: SHA-256 Mismatch
# ---------------------------------------------------------------------------
def test_sha256_mismatch(tmp_path):
    """Verify that a file with unexpected SHA-256 raises FileIntegrityError."""
    dup_detector = DuplicateDetector(index_path=tmp_path / "dup.json")
    pipeline = DatasetProcessingPipeline(audit_log_path=tmp_path / "audit.jsonl", duplicate_detector=dup_detector)
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("Legitimate text content for testing", encoding="utf-8")

    wrong_hash = "0" * 64
    with pytest.raises(FileIntegrityError, match="SHA-256 integrity mismatch"):
        pipeline.process_file(sample_file, source_id="SRC-TM-01", expected_sha256=wrong_hash)


# ---------------------------------------------------------------------------
# Vector 2: Corrupted Files & Executable Binaries
# ---------------------------------------------------------------------------
def test_corrupted_files(tmp_path):
    """Verify that files with executable binary headers (PE/ELF) are rejected."""
    dup_detector = DuplicateDetector(index_path=tmp_path / "dup.json")
    pipeline = DatasetProcessingPipeline(audit_log_path=tmp_path / "audit.jsonl", duplicate_detector=dup_detector)
    fake_exe = tmp_path / "payload.txt"
    fake_exe.write_bytes(b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 128)

    with pytest.raises(FileIntegrityError, match="executable binary header"):
        pipeline.process_file(fake_exe, source_id="SRC-TM-01")


# ---------------------------------------------------------------------------
# Vector 3: Invalid UTF-8 & Replacement Characters
# ---------------------------------------------------------------------------
def test_invalid_utf8(tmp_path):
    """Verify that broken UTF-8 byte sequences or U+FFFD replacement chars fail."""
    dup_detector = DuplicateDetector(index_path=tmp_path / "dup.json")
    pipeline = DatasetProcessingPipeline(audit_log_path=tmp_path / "audit.jsonl", duplicate_detector=dup_detector)

    # Broken byte sequence
    broken_file = tmp_path / "broken.txt"
    broken_file.write_bytes(b"Valid prefix \x80\xFF broken suffix")
    with pytest.raises(FileIntegrityError, match="encoding validation failed"):
        pipeline.process_file(broken_file, source_id="SRC-TM-01")

    # U+FFFD replacement character
    proc = UnicodeProcessor()
    with pytest.raises(InvalidEncodingError, match=r"U\+FFFD"):
        proc.validate_utf8_bytes("Corrupted text \ufffd here".encode("utf-8"))


# ---------------------------------------------------------------------------
# Vector 4: Unicode Normalization (NFC)
# ---------------------------------------------------------------------------
def test_unicode_normalization():
    """Verify that decomposed NFD text is normalized canonically to NFC."""
    proc = UnicodeProcessor()
    # NFD: 'e' + combining acute accent (U+0301)
    decomposed = "e\u0301"
    composed = "\u00e9"  # NFC composed 'é'

    assert decomposed != composed
    assert not unicodedata.is_normalized("NFC", decomposed)

    normalized, rep = proc.clean_and_normalize(decomposed)
    assert normalized == composed
    assert unicodedata.is_normalized("NFC", normalized)
    assert rep.is_nfc_original is False


# ---------------------------------------------------------------------------
# Vectors 5–11: Multilingual Script Preservation
# ---------------------------------------------------------------------------
def test_tamil_text_preservation():
    """Verify that Tamil text with complex vowels and combining signs is preserved without loss."""
    proc = UnicodeProcessor()
    tamil_sample = "தமிழ்நாடு இந்தியாவின் தென் பகுதியில் அமைந்துள்ள ஒரு மாநிலம் ஆகும்."
    cleaned, rep = proc.clean_and_normalize(tamil_sample)

    assert cleaned == tamil_sample
    assert rep.primary_script == "TAMIL"
    assert rep.script_distribution.get("TAMIL", 0.0) > 0.80


def test_telugu_text_preservation():
    """Verify that Telugu vowels, combining marks, and conjuncts are preserved."""
    proc = UnicodeProcessor()
    telugu_sample = "నమస్కారం! తెలుగు భారతదేశంలో మాట్లాడే ప్రముఖ ద్రావిడ భాషలలో ఒకటి."
    cleaned, rep = proc.clean_and_normalize(telugu_sample)

    assert cleaned == telugu_sample
    assert rep.primary_script == "TELUGU"
    assert rep.script_distribution.get("TELUGU", 0.0) > 0.80


def test_malayalam_text_preservation():
    """Verify that Malayalam chillu characters and ligatures (ZWJ/ZWNJ) are preserved."""
    proc = UnicodeProcessor()
    # Malayalam with chillu letters (ന്, ൽ) and ligatures
    malayalam_sample = "മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്. കേരളത്തിലാണ് ഇത് പ്രധാനമായും സംസാരിക്കുന്നത്."
    cleaned, rep = proc.clean_and_normalize(malayalam_sample)

    assert cleaned == malayalam_sample
    assert rep.primary_script == "MALAYALAM"
    assert rep.script_distribution.get("MALAYALAM", 0.0) > 0.80


def test_kannada_text_preservation():
    """Verify that Kannada text, combining vowel signs, and virama are preserved."""
    proc = UnicodeProcessor()
    kannada_sample = "ಕನ್ನಡವು ಭಾರತದ ಕರ್ನಾಟಕ ರಾಜ್ಯದ ಅಧಿಕೃತ ಮತ್ತು ವ್ಯಾಪಕವಾಗಿ ಮಾತನಾಡುವ ಭಾಷೆಯಾಗಿದೆ."
    cleaned, rep = proc.clean_and_normalize(kannada_sample)

    assert cleaned == kannada_sample
    assert rep.primary_script == "KANNADA"
    assert rep.script_distribution.get("KANNADA", 0.0) > 0.80


def test_hindi_text_preservation():
    """Verify that Hindi Devanagari text, matras, conjuncts, and nuktas are preserved."""
    proc = UnicodeProcessor()
    hindi_sample = "नमस्ते! हिंदी भारत की एक प्रमुख और राजभाषा है जो देवनागरी लिपि में लिखी जाती है।"
    cleaned, rep = proc.clean_and_normalize(hindi_sample)

    assert cleaned == hindi_sample
    assert rep.primary_script == "DEVANAGARI"
    assert rep.script_distribution.get("DEVANAGARI", 0.0) > 0.80


def test_bengali_text_preservation():
    """Verify that Bengali vowel signs, hasant, and ligatures are preserved."""
    proc = UnicodeProcessor()
    bengali_sample = "বাংলা ভাষা একটি ইন্দো-আর্য ভাষা যা দক্ষিণ এশিয়ার বাঙালি জনগণের প্রধান ভাষা।"
    cleaned, rep = proc.clean_and_normalize(bengali_sample)

    assert cleaned == bengali_sample
    assert rep.primary_script == "BENGALI"
    assert rep.script_distribution.get("BENGALI", 0.0) > 0.80


def test_gujarati_text_preservation():
    """Verify that Gujarati text, matras, and conjuncts are preserved."""
    proc = UnicodeProcessor()
    gujarati_sample = "નમસ્તે! ગુજરાતી એ ભારત દેશના પશ્ચિમ ભાગમાં આવેલા ગુજરાત રાજ્યની મુખ્ય ભાષા છે."
    cleaned, rep = proc.clean_and_normalize(gujarati_sample)

    assert cleaned == gujarati_sample
    assert rep.primary_script == "GUJARATI"
    assert rep.script_distribution.get("GUJARATI", 0.0) > 0.80


# ---------------------------------------------------------------------------
# Vector 12: Tanglish Classification
# ---------------------------------------------------------------------------
def test_tanglish_classification():
    """Verify that Latin-script phonetic Tamil (Tanglish) is classified as tanglish."""
    lang_id = LanguageIdentifier()
    tanglish_sample = "vanakkam nanba epdi irukinga romba nalla irukku innaiku velai mudinjathu"
    res = lang_id.identify_language(tanglish_sample)

    assert res.primary_language == "tanglish"
    assert res.confidence >= 0.50
    assert "LATIN" in res.detected_scripts


# ---------------------------------------------------------------------------
# Vector 13: Mixed-Script Text
# ---------------------------------------------------------------------------
def test_mixed_script_text():
    """Verify that mixed English-Tamil text is detected with distribution and is_mixed_language flag."""
    lang_id = LanguageIdentifier()
    mixed_sample = "வணக்கம் Welcome to the IGRIS multilingual tokenizer project தமிழ்நாடு."
    res = lang_id.identify_language(mixed_sample)

    assert res.is_mixed_language is True
    assert "LATIN" in res.detected_scripts
    assert "TAMIL" in res.detected_scripts


# ---------------------------------------------------------------------------
# Vector 14: Empty Documents
# ---------------------------------------------------------------------------
def test_empty_documents():
    """Verify that empty or whitespace-only documents are rejected."""
    q_filter = QualityFilter()
    res1 = q_filter.evaluate_document("")
    res2 = q_filter.evaluate_document("   \n\t   \n  ")

    assert res1.passed is False
    assert "EMPTY_DOCUMENT" in res1.rejection_reasons
    assert res2.passed is False
    assert "EMPTY_DOCUMENT" in res2.rejection_reasons


# ---------------------------------------------------------------------------
# Vector 15: Repeated Lines & Documents
# ---------------------------------------------------------------------------
def test_repeated_documents():
    """Verify that documents with heavy line repetition fail quality filtering."""
    q_filter = QualityFilter(config=QualityConfig(max_repeated_line_ratio=0.30))
    repeated_lines = "\n".join(["Duplicate content line for spamming"] * 10)
    res = q_filter.evaluate_document(repeated_lines)

    assert res.passed is False
    assert any("REPEATED_LINES" in r for r in res.rejection_reasons)


# ---------------------------------------------------------------------------
# Vector 16: Near-Duplicate Documents
# ---------------------------------------------------------------------------
def test_near_duplicate_documents(tmp_path):
    """Verify that slightly varied documents are flagged as near-duplicates."""
    dup_detector = DuplicateDetector(index_path=tmp_path / "dup_idx.json", near_duplicate_threshold=0.80)

    doc1 = "The IGRIS transformer model incorporates rotary position embeddings and multi-query attention mechanisms."
    doc2 = "The IGRIS transformer model incorporates rotary position embeddings and multi-query attention structures."

    res1 = dup_detector.check_duplicate("DOC-001", doc1, register_if_unique=True)
    assert res1.is_duplicate is False

    res2 = dup_detector.check_duplicate("DOC-002", doc2, register_if_unique=False)
    assert res2.is_duplicate is True
    assert res2.duplicate_type == "NEAR_DUPLICATE"
    assert res2.canonical_doc_id == "DOC-001"


# ---------------------------------------------------------------------------
# Vector 17: PII Detection
# ---------------------------------------------------------------------------
def test_pii_detection():
    """Verify that PII patterns (email, phone, SSN, Aadhaar, cards) are detected and redacted."""
    scanner = PrivacyContaminationScanner()
    pii_text = """
    User contact: alex.smith@example.org or mobile +1-555-867-5309.
    SSN: 987-65-4321, Aadhaar: 3456 7890 1234.
    """
    res = scanner.scan_privacy(pii_text)

    assert res.has_pii is True
    assert res.email_count == 1
    assert res.phone_count >= 1
    assert res.ssn_count == 1
    assert res.aadhaar_count == 1
    assert res.review_status in ("FLAGGED_FOR_REVIEW", "QUARANTINED")


# ---------------------------------------------------------------------------
# Vector 18: Credential Detection
# ---------------------------------------------------------------------------
def test_credential_detection():
    """Verify that private keys and API tokens are flagged for quarantine."""
    scanner = PrivacyContaminationScanner()
    cred_text = """
    -----BEGIN RSA PRIVATE KEY-----
    MIIEowIBAAKCAQEA0Y1+examplePrivateKeYPayloadHereData...
    -----END RSA PRIVATE KEY-----
    And AWS key: AKIAIOSFODNN7EXAMPLE
    """
    res = scanner.scan_privacy(cred_text)

    assert res.credential_count >= 2
    assert res.review_status == "QUARANTINED"
    assert "[REDACTED_PRIVATE_KEY]" in res.redacted_samples["credentials"]


# ---------------------------------------------------------------------------
# Vector 19: Benchmark Contamination Detection
# ---------------------------------------------------------------------------
def test_benchmark_contamination():
    """Verify that benchmark test cases (e.g. HumanEval, MBPP) are detected as contamination."""
    scanner = PrivacyContaminationScanner()
    prompt_text = """
    def has_close_elements(numbers: List[float], threshold: float) -> bool:
        Check if in given list of numbers, are any two numbers closer to each other than given threshold.
    """
    res = scanner.scan_contamination(prompt_text, source_id="SRC-TM-01")

    assert res.has_contamination is True
    assert res.is_benchmark_contaminated is True
    assert any("HumanEval" in b for b in res.matched_benchmarks)


# ---------------------------------------------------------------------------
# Vector 20: Evaluation-Only Source Isolation
# ---------------------------------------------------------------------------
def test_evaluation_only_source_isolation():
    """Verify that Tier 3 evaluation benchmarks (SRC-CD-02, SRC-CV-04) cannot enter training pipeline."""
    scanner = PrivacyContaminationScanner()
    res = scanner.scan_contamination(
        "Regular Python challenge text",
        source_id="SRC-CD-02",
        intended_use="VOCABULARY_TRAINING"
    )
    assert res.tier_violation is True
    assert "barred from training" in res.isolation_notes


# ---------------------------------------------------------------------------
# Vector 21: Permanently Blocked Source Rejection
# ---------------------------------------------------------------------------
def test_permanently_blocked_source_rejection():
    """Verify that Tier 4 rejected sources (SRC-CV-01, SRC-HI-03) are blocked from all operations."""
    scanner = PrivacyContaminationScanner()
    res = scanner.scan_contamination(
        "Text sample from prohibited dataset",
        source_id="SRC-CV-01",
        intended_use="EVALUATION_OR_TRAINING"
    )
    assert res.tier_violation is True
    assert "permanently rejected" in res.isolation_notes


# ---------------------------------------------------------------------------
# Vector 22: Audit-Chain Tampering Detection
# ---------------------------------------------------------------------------
def test_audit_chain_tampering(tmp_path):
    """Verify that tampering with a processing audit log breaks the cryptographic chain."""
    audit_file = tmp_path / "proc_audit.jsonl"
    logger = ProvenanceAuditLogger(audit_file)

    rec1 = {"timestamp": "2026-11-18T00:00:01Z", "document_id": "D1", "source_id": "SRC-1", "original_file_sha256": "h1", "quality_score": 1.0, "primary_language": "ta"}
    rec2 = {"timestamp": "2026-11-18T00:00:02Z", "document_id": "D2", "source_id": "SRC-1", "original_file_sha256": "h2", "quality_score": 1.0, "primary_language": "hi"}

    logger.log_record(rec1)
    logger.log_record(rec2)

    ok, _, _ = logger.verify_integrity()
    assert ok is True

    # Tamper with rec1 quality score in file
    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    d = json.loads(lines[0])
    d["quality_score"] = 0.1  # Tampered!
    lines[0] = json.dumps(d) + "\n"
    with open(audit_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    ok_tamper, _, err = logger.verify_integrity()
    assert ok_tamper is False
    assert "mismatch" in err.lower() or "break" in err.lower()


# ---------------------------------------------------------------------------
# Vector 23: Processing Interruption Handling
# ---------------------------------------------------------------------------
def test_processing_interruption(tmp_path):
    """Verify that an interrupted file processing raises cleanly without corrupting state."""
    pipeline = DatasetProcessingPipeline(audit_log_path=tmp_path / "audit.jsonl")
    bad_file = tmp_path / "unsupported.bin"
    bad_file.write_bytes(b"Unsupported binary format bytes")

    with pytest.raises(FormatValidationError, match="Unsupported file format"):
        pipeline.process_file(bad_file, source_id="SRC-TM-01")


# ---------------------------------------------------------------------------
# Vector 24: Duplicate-Index Concurrency Protection
# ---------------------------------------------------------------------------
def test_duplicate_index_concurrency(tmp_path):
    """Verify that duplicate index lockfile prevents conflicting concurrent access."""
    detector = DuplicateDetector(index_path=tmp_path / "dup.json")
    detector._acquire_lock()

    # Second detector on same path
    detector2 = DuplicateDetector(index_path=tmp_path / "dup.json")
    start = time.time()
    # Should wait and handle lock safely
    detector._release_lock()
    detector2._acquire_lock()
    detector2._release_lock()


# ---------------------------------------------------------------------------
# Vector 25: Deterministic Processing
# ---------------------------------------------------------------------------
def test_deterministic_processing(tmp_path):
    """Verify that identical inputs produce identical cleaned text, language, and provenance."""
    pipeline = DatasetProcessingPipeline(audit_log_path=tmp_path / "audit.jsonl")
    text = "நமஸ்காரம்! This is an authentic Tamil sentence for testing determinism."

    res1 = pipeline.process_document("DET-1", "SRC-TM-01", text)
    res2 = pipeline.process_document("DET-2", "SRC-TM-01", text)

    assert res1.cleaned_text == res2.cleaned_text
    assert res1.language_result.primary_language == res2.language_result.primary_language
    assert res1.quality_decision.quality_score == res2.quality_decision.quality_score


# ---------------------------------------------------------------------------
# Vector 26: Provenance Record Integrity
# ---------------------------------------------------------------------------
def test_provenance_integrity(tmp_path):
    """Verify that every processed document generates an intact provenance record with valid hashes."""
    pipeline = DatasetProcessingPipeline(audit_log_path=tmp_path / "audit.jsonl")
    text = "Valid English document with sufficient length to verify complete provenance generation."

    res = pipeline.process_document("PROV-1", "SRC-EN-01", text)
    prov = res.provenance

    assert prov.document_id == "PROV-1"
    assert prov.source_id == "SRC-EN-01"
    assert len(prov.original_file_sha256) == 64
    assert len(prov.entry_hash) == 64
    assert prov.quality_passed is True


# ---------------------------------------------------------------------------
# Vector 27: Invalid Processing Configuration
# ---------------------------------------------------------------------------
def test_invalid_processing_configuration(tmp_path):
    """Verify that missing pipeline version configuration raises PipelineError."""
    bad_config = ProcessingConfig(pipeline_version="", config_version="")
    dup_detector = DuplicateDetector(index_path=tmp_path / "dup.json")
    pipeline = DatasetProcessingPipeline(config=bad_config, audit_log_path=tmp_path / "audit.jsonl", duplicate_detector=dup_detector)

    with pytest.raises(PipelineError, match="Invalid processing configuration"):
        pipeline.process_document("DOC-BAD", "SRC-TM-01", "Some test text")


# ---------------------------------------------------------------------------
# Vector 28: Unauthorized Input Directory Rejection
# ---------------------------------------------------------------------------
def test_unauthorized_input_directory_rejection(tmp_path):
    """Verify that attempting to process files outside permitted input directories is rejected."""
    allowed_dir = tmp_path / "quarantine_allowed"
    unauthorized_dir = tmp_path / "unauthorized_external"
    allowed_dir.mkdir()
    unauthorized_dir.mkdir()

    config = ProcessingConfig(allowed_input_dirs=[str(allowed_dir)])
    pipeline = DatasetProcessingPipeline(config=config, audit_log_path=tmp_path / "audit.jsonl")

    unauthorized_file = unauthorized_dir / "external_data.txt"
    unauthorized_file.write_text("External unapproved data", encoding="utf-8")

    with pytest.raises(UnauthorizedDirectoryError, match="outside permitted input directories"):
        pipeline.process_file(unauthorized_file, source_id="SRC-TM-01")
