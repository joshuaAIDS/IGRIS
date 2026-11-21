"""
phase31a_policy_validator.py — Comprehensive Non-Production Policy Test Runner for IGRIS Phase 31A.
Validates:
1. Benchmark Contamination Policies (Thresholds 0.70 & 0.85 -> MANUAL_REVIEW_REQUIRED; zero automatic rejection).
2. Privacy Masking Policies ([EMAIL_REDACTED], [PHONE_REDACTED], Unicode preservation, uncertain PII handling).
3. OASST1 Combined Language Routing Policies (Metadata + LanguageIdentifierV2, Tanglish/Tamil routing, uncertain PII).
"""

import hashlib
import json
import os
import re
import sys
import unicodedata
from typing import Dict, List, Any, Tuple, Optional

# Ensure scripts dir is on sys.path to import LanguageIdentifierV2
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from language_identifier_v2 import LanguageIdentifierV2

# ---------------------------------------------------------------------------
# Approved Placeholders & Regular Expressions
# ---------------------------------------------------------------------------
EMAIL_PLACEHOLDER = "[EMAIL_REDACTED]"
PHONE_PLACEHOLDER = "[PHONE_REDACTED]"

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

# Sensitive narrative keywords without structured identifiers
SENSITIVE_NARRATIVE_KEYWORDS = [
    "diagnosed with", "chronic depression", "medical leave", "prescription medication",
    "bank account balance", "credit card debt", "filed for bankruptcy", "divorce proceeding"
]

UNCERTAIN_PII_PATTERNS = [
    re.compile(r'\buser_id_[0-9a-zA-Z_]+\b'),
    re.compile(r'\bauthor_handle_[0-9a-zA-Z_]+\b'),
    re.compile(r'\baccount_token_[0-9a-zA-Z_]+\b'),
]

# ---------------------------------------------------------------------------
# Benchmark Screening Module
# ---------------------------------------------------------------------------
class BenchmarkPolicyEvaluator:
    """
    Evaluates benchmark similarity scores under Phase 31A owner policies:
    - score >= 0.70: MANUAL_REVIEW_REQUIRED (concern: moderate)
    - score >= 0.85: MANUAL_REVIEW_REQUIRED (concern: high)
    - No score alone may automatically reject a record.
    """
    def evaluate(self, similarity: float, benchmark_id: Optional[str] = None, 
                 matching_span: Optional[str] = None, is_common_idiom: bool = False) -> Dict[str, Any]:
        if is_common_idiom:
            return {
                "similarity_score": similarity,
                "benchmark_id": benchmark_id,
                "review_status": "NOT_REVIEWED",
                "concern_level": "NONE",
                "automatic_rejection": False,
                "rationale": "Common programming pattern recognized by AST analyzer; false-positive suppressed."
            }
        
        if benchmark_id is None or similarity < 0.70:
            return {
                "similarity_score": similarity,
                "benchmark_id": benchmark_id,
                "review_status": "NOT_REVIEWED",
                "concern_level": "NONE",
                "automatic_rejection": False,
                "rationale": "Similarity below 0.70 threshold; clean."
            }
        
        concern = "HIGH" if similarity >= 0.85 else "MODERATE"
        return {
            "similarity_score": similarity,
            "benchmark_id": benchmark_id,
            "matching_span": matching_span,
            "detection_method": "13-gram MinHash / AST Normalizer",
            "review_status": "MANUAL_REVIEW_REQUIRED",
            "concern_level": concern,
            "automatic_rejection": False,
            "rationale": f"Similarity {similarity:.2f} >= 0.70 requires mandatory owner manual review (concern: {concern})."
        }

# ---------------------------------------------------------------------------
# Privacy Masking Module
# ---------------------------------------------------------------------------
class PrivacyPolicyMasker:
    """
    Applies privacy masking under Phase 31A owner policies:
    - [EMAIL_REDACTED], [PHONE_REDACTED]
    - Preserves surrounding Unicode text without corruption (NFC).
    - Preserves machine-readable record without logging sensitive values.
    - Handles uncertain PII and sensitive narratives by routing to manual review.
    """
    def mask_text(self, text: str) -> Dict[str, Any]:
        # Enforce canonical NFC before processing
        norm_text = unicodedata.normalize("NFC", text)
        records = []
        
        # 1. Check for sensitive narrative without explicit identifiers
        has_sensitive_narrative = any(kw in norm_text.lower() for kw in SENSITIVE_NARRATIVE_KEYWORDS)
        
        # 2. Check for uncertain PII identifiers
        uncertain_matches = []
        for pat in UNCERTAIN_PII_PATTERNS:
            for m in pat.finditer(norm_text):
                uncertain_matches.append((m.start(), m.end(), m.group(0)))
                
        # 3. Identify and mask Email and Phone spans
        masked_text = norm_text
        
        # Collect email spans
        email_spans = []
        for m in EMAIL_REGEX.finditer(norm_text):
            # Check false positive like matrix @ multiplication or python decorator
            val = m.group(0)
            if "@" in val and not val.startswith("@") and not val.endswith("@"):
                email_spans.append((m.start(), m.end(), val))
                
        # Collect phone spans
        phone_spans = []
        for m in PHONE_REGEX.finditer(norm_text):
            val = m.group(0).strip()
            # Must have at least 7 digits to avoid matching small numbers
            digits = sum(1 for c in val if c.isdigit())
            if digits >= 7:
                phone_spans.append((m.start(), m.end(), val))
                
        # Sort spans in reverse order to replace without invalidating earlier offsets
        all_spans = []
        for s, e, v in email_spans:
            all_spans.append((s, e, "EMAIL", EMAIL_PLACEHOLDER, v))
        for s, e, v in phone_spans:
            all_spans.append((s, e, "PHONE", PHONE_PLACEHOLDER, v))
            
        all_spans.sort(key=lambda x: x[0], reverse=True)
        
        # Apply replacement
        for s, e, etype, placeholder, raw_val in all_spans:
            val_hash = hashlib.sha256(raw_val.encode("utf-8")).hexdigest()[:16]
            records.append({
                "entity_type": etype,
                "placeholder": placeholder,
                "start_offset": s,
                "end_offset": e,
                "entity_hash": val_hash  # One-way hash; raw value NOT logged
            })
            masked_text = masked_text[:s] + placeholder + masked_text[e:]
            
        # Ensure Unicode NFC stability
        masked_text = unicodedata.normalize("NFC", masked_text)
        
        # Determine privacy status
        if has_sensitive_narrative or len(uncertain_matches) > 0:
            review_status = "MANUAL_REVIEW_REQUIRED"
            rationale = "Uncertain PII or sensitive narrative detected; held for manual review."
        elif len(all_spans) > 0:
            review_status = "MASKING_APPLIED"
            rationale = f"Masked {len(all_spans)} structured identifiers cleanly."
        else:
            review_status = "CLEAN"
            rationale = "No PII detected."
            
        return {
            "original_len": len(norm_text),
            "masked_text": masked_text,
            "masking_records": records,
            "has_sensitive_narrative": has_sensitive_narrative,
            "uncertain_pii_count": len(uncertain_matches),
            "review_status": review_status,
            "rationale": rationale
        }

# ---------------------------------------------------------------------------
# OASST1 Combined Language Routing Module
# ---------------------------------------------------------------------------
class LanguageRoutingEvaluator:
    """
    Combined language routing using:
    1. Dataset language metadata (initial gate).
    2. IGRIS LanguageIdentifierV2 (independent check).
    3. Confidence-based routing.
    4. Code-switch and Tanglish detection.
    5. Manual review routing for uncertain records.
    """
    def __init__(self):
        self.lang_id = LanguageIdentifierV2()

    def route_record(self, text: str, metadata_lang: str) -> Dict[str, Any]:
        result = self.lang_id.identify(text)
        
        # 1. Metadata mismatch check
        if metadata_lang.lower() == "en" and result.label != "ENGLISH":
            if result.label in ("TANGLISH", "TAMIL"):
                return {
                    "routing_decision": "REJECT_LANG_MISMATCH",
                    "classified_label": result.label,
                    "confidence": result.confidence,
                    "sublabel": result.sublabel,
                    "action": "EXCLUDE_FROM_ENGLISH_CANDIDATE_SET",
                    "requires_review": False,
                    "rationale": f"Metadata asserted 'en' but text detected as {result.label} ({result.sublabel})."
                }
            elif result.label == "OUT_OF_SCOPE":
                return {
                    "routing_decision": "REJECT_OUT_OF_SCOPE",
                    "classified_label": "OUT_OF_SCOPE",
                    "confidence": result.confidence,
                    "action": "PERMANENT_EXCLUSION",
                    "requires_review": False,
                    "rationale": "Non-target script detected."
                }
            else: # UNKNOWN
                return {
                    "routing_decision": "HOLD_FOR_MANUAL_REVIEW",
                    "classified_label": "UNKNOWN",
                    "confidence": result.confidence,
                    "action": "MANUAL_REVIEW_REQUIRED",
                    "requires_review": True,
                    "rationale": "Low confidence classification; uncertain record held for manual review."
                }
                
        # 2. Confirmed English
        if metadata_lang.lower() == "en" and result.label == "ENGLISH":
            if result.confidence < 0.70:
                return {
                    "routing_decision": "HOLD_FOR_MANUAL_REVIEW",
                    "classified_label": "UNKNOWN",
                    "confidence": result.confidence,
                    "action": "MANUAL_REVIEW_REQUIRED",
                    "requires_review": True,
                    "rationale": f"English detected but confidence ({result.confidence:.2f}) < 0.70 threshold; Latin script not assumed English without lexical proof; held for manual review."
                }
            return {
                "routing_decision": "ADMIT_ENGLISH_CANDIDATE",
                "classified_label": "ENGLISH",
                "confidence": result.confidence,
                "sublabel": result.sublabel,
                "action": "PROCEED_TO_DECONTAMINATION",
                "requires_review": False,
                "rationale": "Verified English with sufficient confidence."
            }
            
        # 3. Direct Tamil or Tanglish
        return {
            "routing_decision": f"ROUTE_{result.label}",
            "classified_label": result.label,
            "confidence": result.confidence,
            "sublabel": result.sublabel,
            "action": f"PRESERVE_FOR_{result.label}_PIPELINE",
            "requires_review": False,
            "rationale": f"Directly classified as {result.label}."
        }

# ---------------------------------------------------------------------------
# Synthetic Test Suite Execution
# ---------------------------------------------------------------------------
def run_all_phase31a_tests() -> Dict[str, Any]:
    bm_eval = BenchmarkPolicyEvaluator()
    masker = PrivacyPolicyMasker()
    router = LanguageRoutingEvaluator()
    
    test_results = {
        "benchmark_passed": 0,
        "benchmark_total": 7,
        "privacy_passed": 0,
        "privacy_total": 9,
        "language_passed": 0,
        "language_total": 8,
        "details": []
    }
    
    # -----------------------------------------------------------------------
    # 1. Benchmark Tests (7 test cases)
    # -----------------------------------------------------------------------
    bm_cases = [
        {"id": "BM-TEST-01", "name": "Similarity below 0.70", "sim": 0.45, "bm_id": "HumanEval/4", "exp_status": "NOT_REVIEWED", "exp_auto_rej": False},
        {"id": "BM-TEST-02", "name": "Similarity exactly 0.70", "sim": 0.70, "bm_id": "HumanEval/12", "exp_status": "MANUAL_REVIEW_REQUIRED", "exp_auto_rej": False},
        {"id": "BM-TEST-03", "name": "Similarity between 0.70 and 0.85", "sim": 0.78, "bm_id": "MBPP/105", "exp_status": "MANUAL_REVIEW_REQUIRED", "exp_auto_rej": False},
        {"id": "BM-TEST-04", "name": "Similarity exactly 0.85", "sim": 0.85, "bm_id": "HumanEval/64", "exp_status": "MANUAL_REVIEW_REQUIRED", "exp_auto_rej": False},
        {"id": "BM-TEST-05", "name": "Similarity above 0.85", "sim": 0.94, "bm_id": "HumanEval/0", "exp_status": "MANUAL_REVIEW_REQUIRED", "exp_auto_rej": False},
        {"id": "BM-TEST-06", "name": "False-positive common programming pattern", "sim": 0.88, "bm_id": "HumanEval/1", "is_idiom": True, "exp_status": "NOT_REVIEWED", "exp_auto_rej": False},
        {"id": "BM-TEST-07", "name": "Missing benchmark reference", "sim": 0.0, "bm_id": None, "exp_status": "NOT_REVIEWED", "exp_auto_rej": False},
    ]
    
    for case in bm_cases:
        res = bm_eval.evaluate(case["sim"], case["bm_id"], is_common_idiom=case.get("is_idiom", False))
        passed = (res["review_status"] == case["exp_status"] and res["automatic_rejection"] == case["exp_auto_rej"])
        if passed:
            test_results["benchmark_passed"] += 1
        test_results["details"].append({"test_id": case["id"], "name": case["name"], "passed": passed, "result": res})
        
    # -----------------------------------------------------------------------
    # 2. Privacy Tests (9 test cases)
    # -----------------------------------------------------------------------
    priv_cases = [
        {"id": "PRIV-TEST-01", "name": "Single email", "text": "Contact lead at alex.smith@python.org for info.", 
         "check": lambda r: EMAIL_PLACEHOLDER in r["masked_text"] and len(r["masking_records"]) == 1 and "alex.smith@python.org" not in str(r["masking_records"])},
        {"id": "PRIV-TEST-02", "name": "Multiple emails", "text": "Maintainers: alex@python.org, jane@example.com.",
         "check": lambda r: r["masked_text"].count(EMAIL_PLACEHOLDER) == 2 and len(r["masking_records"]) == 2},
        {"id": "PRIV-TEST-03", "name": "Phone number", "text": "Call telephone +1-206-555-0199 directly.",
         "check": lambda r: PHONE_PLACEHOLDER in r["masked_text"] and len(r["masking_records"]) == 1},
        {"id": "PRIV-TEST-04", "name": "Email and phone in same text", "text": "Reach out to support@domain.org or 415-555-2671.",
         "check": lambda r: EMAIL_PLACEHOLDER in r["masked_text"] and PHONE_PLACEHOLDER in r["masked_text"]},
        {"id": "PRIV-TEST-05", "name": "False-positive email-like text", "text": "Matrix operation uses A @ B, and class uses @classmethod decorator.",
         "check": lambda r: EMAIL_PLACEHOLDER not in r["masked_text"] and len(r["masking_records"]) == 0},
        {"id": "PRIV-TEST-06", "name": "Unicode text surrounding masked spans", "text": "ஆசிரியர் தொடர்பு: dev@tamil-nlp.org நன்றி வணக்கம்",
         "check": lambda r: EMAIL_PLACEHOLDER in r["masked_text"] and "ஆசிரியர் தொடர்பு:" in r["masked_text"] and unicodedata.is_normalized("NFC", r["masked_text"])},
        {"id": "PRIV-TEST-07", "name": "Overlapping detections", "text": "contact:dev@python.org;dev@python.org",
         "check": lambda r: r["masked_text"].count(EMAIL_PLACEHOLDER) == 2 and "@@" not in r["masked_text"]},
        {"id": "PRIV-TEST-08", "name": "Uncertain PII", "text": "Internal user record assigned author_handle_9942a for audit.",
         "check": lambda r: r["review_status"] == "MANUAL_REVIEW_REQUIRED" and r["uncertain_pii_count"] > 0},
        {"id": "PRIV-TEST-09", "name": "Sensitive narrative without recognizable identifiers", "text": "I was diagnosed with chronic depression during the project.",
         "check": lambda r: r["review_status"] == "MANUAL_REVIEW_REQUIRED" and r["has_sensitive_narrative"] is True},
    ]
    
    for case in priv_cases:
        res = masker.mask_text(case["text"])
        passed = case["check"](res)
        if passed:
            test_results["privacy_passed"] += 1
        test_results["details"].append({"test_id": case["id"], "name": case["name"], "passed": passed, "review_status": res["review_status"]})

    # -----------------------------------------------------------------------
    # 3. Language Tests (8 test cases)
    # -----------------------------------------------------------------------
    lang_cases = [
        {"id": "LANG-TEST-01", "name": "Standard English", "text": "This module implements numerical integration using Gaussian quadrature.", "meta": "en", "exp_dec": "ADMIT_ENGLISH_CANDIDATE"},
        {"id": "LANG-TEST-02", "name": "Native Tamil script", "text": "தமிழ் மொழி உலகின் மிகத் தொன்மையான செம்மொழிகளில் ஒன்றாகும்.", "meta": "ta", "exp_dec": "ROUTE_TAMIL"},
        {"id": "LANG-TEST-03", "name": "Romanized Tamil", "text": "enna bro romba late ah reply varudhu, eppo solve pannuveenga sollunga", "meta": "ta", "exp_dec": "ROUTE_TANGLISH"},
        {"id": "LANG-TEST-04", "name": "Tamil-English code-switching", "text": "This is a very complex algorithm bro, but namba easy ah solve pannalam.", "meta": "en", "exp_dec": "REJECT_LANG_MISMATCH"},
        {"id": "LANG-TEST-05", "name": "English with Tamil discourse markers", "text": "The neural network loss is dropping very rapidly da.", "meta": "en", "exp_dec": "REJECT_LANG_MISMATCH"},
        {"id": "LANG-TEST-06", "name": "Mixed-language conversation turn", "text": "seri namba adutha function define pannuvom", "meta": "en", "exp_dec": "REJECT_LANG_MISMATCH"},
        {"id": "LANG-TEST-07", "name": "Incorrect metadata (asserted en, text is Tanglish)", "text": "idhu romba mukkiyamaana vishayam bro kandippa paarunga", "meta": "en", "exp_dec": "REJECT_LANG_MISMATCH"},
        {"id": "LANG-TEST-08", "name": "Low-confidence identification", "text": "zzz qqq xxx", "meta": "en", "exp_dec": "HOLD_FOR_MANUAL_REVIEW"},
    ]
    
    for case in lang_cases:
        res = router.route_record(case["text"], case["meta"])
        passed = (res["routing_decision"] == case["exp_dec"])
        if passed:
            test_results["language_passed"] += 1
        test_results["details"].append({"test_id": case["id"], "name": case["name"], "passed": passed, "routing": res["routing_decision"]})

    return test_results

if __name__ == "__main__":
    res = run_all_phase31a_tests()
    print("=" * 70)
    print("PHASE 31A POLICY VALIDATION TEST RUNNER")
    print("=" * 70)
    print(f"  Benchmark Policy Tests: {res['benchmark_passed']}/{res['benchmark_total']} PASSED")
    print(f"  Privacy Masking Tests:  {res['privacy_passed']}/{res['privacy_total']} PASSED")
    print(f"  Language Routing Tests: {res['language_passed']}/{res['language_total']} PASSED")
    print("-" * 70)
    all_passed = (res['benchmark_passed'] == res['benchmark_total'] and
                  res['privacy_passed'] == res['privacy_total'] and
                  res['language_passed'] == res['language_total'])
    for d in res["details"]:
        print(f"    - {d['test_id']}: {d['name']} -> Passed={d['passed']}")
    print("=" * 70)
    if all_passed:
        print("ALL 24 POLICY TESTS PASSED (100%)")
        sys.exit(0)
    else:
        print("SOME POLICY TESTS FAILED")
        sys.exit(1)
