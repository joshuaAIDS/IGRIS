"""
IGRIS Privacy & Contamination Scanner
=====================================
Phase 14 Dataset Integrity, Cleaning, and Validation Infrastructure

Enforces:
1. PII detection (emails, phones, SSNs, Aadhaar, credit cards with Luhn check, PIN/ZIP codes).
2. Credential and secret detection (private keys, API tokens, bearer tokens).
3. Benchmark contamination detection (HumanEval, MBPP signatures).
4. Preference-pair leakage detection (RLHF prompt/chosen/rejected patterns).
5. Operational tier isolation enforcement (Tier 2, 3, 4 barred from training ingress).
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


class ContaminationError(Exception):
    """Base exception for dataset contamination or leakage errors."""
    pass


class BenchmarkContaminationError(ContaminationError):
    """Raised when evaluation benchmark prompts or fixtures leak into training candidate data."""
    pass


class PreferenceLeakageError(ContaminationError):
    """Raised when RLHF preference pairs or evaluation alignment sets leak into training data."""
    pass


@dataclass
class PIIDetectionResult:
    has_pii: bool
    email_count: int
    phone_count: int
    ssn_count: int
    aadhaar_count: int
    credit_card_count: int
    postal_code_count: int
    credential_count: int
    redacted_samples: Dict[str, List[str]]
    review_status: str  # "CLEAN", "FLAGGED_FOR_REVIEW", "QUARANTINED"


@dataclass
class ContaminationDetectionResult:
    has_contamination: bool
    is_benchmark_contaminated: bool
    is_preference_leaked: bool
    matched_benchmarks: List[str]
    matched_leakage_types: List[str]
    tier_violation: bool
    isolation_notes: Optional[str] = None


# Regex Patterns
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b")
PHONE_US_REGEX = re.compile(r"\b(?:\+?1[-.]?)?\(?[2-9]\d{2}\)?[-.]?\d{3}[-.]?\d{4}\b")
PHONE_IN_REGEX = re.compile(r"\b(?:\+?91|0)?[6-9]\d{9}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
AADHAAR_REGEX = re.compile(r"(?<!\d)\b[2-9]\d{3}\s\d{4}\s\d{4}\b(?!\s*\d)")
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
PIN_CODE_IN_REGEX = re.compile(r"\b[1-9][0-9]{5}\b")
ZIP_CODE_US_REGEX = re.compile(r"\b\d{5}(?:-\d{4})?\b")

# Credentials & API Keys
PRIVATE_KEY_REGEX = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
AWS_KEY_REGEX = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
GITHUB_TOKEN_REGEX = re.compile(r"\bghp_[A-Za-z0-9_]{36}\b")
BEARER_TOKEN_REGEX = re.compile(r"\bBearer\s+[A-Za-z0-9_\-\.]{30,}\b")

# Benchmark Signatures
HUMANEVAL_SIGNATURES = [
    "def has_close_elements", "def separate_paren_groups", "def truncate_number",
    "def flip_case", "def find_zero", "def factorize", "def parse_nested_parens",
    "def filter_by_prefix", "def rolling_max", "def make_palindrome"
]

MBPP_SIGNATURES = [
    "write a python function to find the minimum sum of a path in a triangle",
    "write a python function to identify non-prime numbers",
    "write a function to find the similar elements from the given two tuple lists",
    "write a python function to find the sum of all odd length subarrays"
]

# Preference Pair Signatures
RLHF_SIGNATURES = [
    "\n\nhuman:", "\n\nassistant:",
    "chosen:", "rejected:",
    "<|prompter|>", "<|assistant|>"
]


def luhn_checksum_valid(card_str: str) -> bool:
    """Validate credit card number using the Luhn algorithm."""
    digits = [int(d) for d in card_str if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += d
    return checksum % 10 == 0


class PrivacyContaminationScanner:
    """
    Comprehensive scanner detecting PII, credentials, benchmark contamination,
    and preference pair leakage in training candidate data.
    """
    def __init__(self):
        pass

    def scan_privacy(self, text: str, max_samples: int = 5) -> PIIDetectionResult:
        """Scan text for PII and credentials, returning redacted samples."""
        if not text:
            return PIIDetectionResult(
                has_pii=False, email_count=0, phone_count=0, ssn_count=0,
                aadhaar_count=0, credit_card_count=0, postal_code_count=0,
                credential_count=0, redacted_samples={}, review_status="CLEAN"
            )

        redacted: Dict[str, List[str]] = {}

        # 1. Emails
        emails = EMAIL_REGEX.findall(text)
        if emails:
            redacted["emails"] = [f"{e.split('@')[0][:2]}***@{e.split('@')[1]}" for e in emails[:max_samples]]

        # 2. Phones
        phones_us = PHONE_US_REGEX.findall(text)
        phones_in = PHONE_IN_REGEX.findall(text)
        all_phones = phones_us + phones_in
        if all_phones:
            redacted["phones"] = [f"***-***-{p[-4:]}" for p in all_phones[:max_samples]]

        # 3. SSN
        ssns = SSN_REGEX.findall(text)
        if ssns:
            redacted["ssns"] = ["***-**-" + s[-4:] for s in ssns[:max_samples]]

        # 4. Aadhaar
        aadhaars = AADHAAR_REGEX.findall(text)
        if aadhaars:
            redacted["aadhaars"] = ["**** **** " + a[-4:] for a in aadhaars[:max_samples]]

        # 5. Credit Cards with Luhn verification
        raw_cards = CREDIT_CARD_REGEX.findall(text)
        valid_cards = [c for c in raw_cards if luhn_checksum_valid(c)]
        if valid_cards:
            redacted["credit_cards"] = ["XXXX-XXXX-XXXX-" + c[-4:] for c in valid_cards[:max_samples]]

        # 6. Postal Codes
        pin_codes = PIN_CODE_IN_REGEX.findall(text)
        if pin_codes and (emails or all_phones):  # Only count if context suggests PII
            redacted["postal_codes"] = [p[:3] + "***" for p in pin_codes[:max_samples]]

        # 7. Credentials & Private Keys
        cred_count = 0
        creds_found = []
        if PRIVATE_KEY_REGEX.search(text):
            cred_count += 1
            creds_found.append("[REDACTED_PRIVATE_KEY]")
        if AWS_KEY_REGEX.search(text):
            cred_count += 1
            creds_found.append("[REDACTED_AWS_KEY]")
        if GITHUB_TOKEN_REGEX.search(text):
            cred_count += 1
            creds_found.append("[REDACTED_GITHUB_TOKEN]")
        if BEARER_TOKEN_REGEX.search(text):
            cred_count += 1
            creds_found.append("[REDACTED_BEARER_TOKEN]")
        if creds_found:
            redacted["credentials"] = creds_found

        total_pii = (
            len(emails) + len(all_phones) + len(ssns) + len(aadhaars)
            + len(valid_cards) + cred_count
        )

        has_pii = total_pii > 0
        if cred_count > 0 or len(valid_cards) > 0 or len(ssns) > 0:
            status = "QUARANTINED"
        elif has_pii:
            status = "FLAGGED_FOR_REVIEW"
        else:
            status = "CLEAN"

        return PIIDetectionResult(
            has_pii=has_pii,
            email_count=len(emails),
            phone_count=len(all_phones),
            ssn_count=len(ssns),
            aadhaar_count=len(aadhaars),
            credit_card_count=len(valid_cards),
            postal_code_count=len(pin_codes) if (emails or all_phones) else 0,
            credential_count=cred_count,
            redacted_samples=redacted,
            review_status=status
        )

    def scan_contamination(
        self,
        text: str,
        source_id: str,
        intended_use: str = "VOCABULARY_TRAINING"
    ) -> ContaminationDetectionResult:
        """
        Check for benchmark contamination, RLHF preference leakage,
        and operational tier violations.
        """
        lower_text = text.lower() if text else ""
        matched_benchmarks: List[str] = []
        matched_leakage: List[str] = []
        tier_violation = False
        notes = []

        # 1. Tier Boundary Check
        if source_id in ("SRC-CD-02", "SRC-CV-04"):
            if "TRAINING" in intended_use.upper():
                tier_violation = True
                notes.append(f"Tier 3 source {source_id} is evaluation-only and barred from training")

        if source_id in ("SRC-EN-02", "SRC-EN-03", "SRC-HI-02", "SRC-ML-01", "SRC-ML-02", "SRC-TD-01", "SRC-TM-02", "SRC-TM-03"):
            if "TRAINING" in intended_use.upper():
                tier_violation = True
                notes.append(f"Tier 2 source {source_id} is conditional and barred from training pending legal clearance")

        if source_id in ("SRC-CV-01", "SRC-CV-02", "SRC-HI-03", "SRC-TG-03"):
            tier_violation = True
            notes.append(f"Tier 4 source {source_id} is permanently rejected from all operations")

        # 2. Benchmark Contamination
        for sig in HUMANEVAL_SIGNATURES:
            if sig.lower() in lower_text:
                matched_benchmarks.append(f"HumanEval ({sig})")

        for sig in MBPP_SIGNATURES:
            if sig.lower() in lower_text:
                matched_benchmarks.append(f"MBPP ({sig[:30]}...)")

        # 3. Preference Pair Leakage
        for sig in RLHF_SIGNATURES:
            if sig.lower() in lower_text:
                matched_leakage.append(f"RLHF Preference Marker ({sig.strip()})")

        has_bench = len(matched_benchmarks) > 0
        has_pref = len(matched_leakage) > 0
        has_contam = has_bench or has_pref or tier_violation

        return ContaminationDetectionResult(
            has_contamination=has_contam,
            is_benchmark_contaminated=has_bench,
            is_preference_leaked=has_pref,
            matched_benchmarks=matched_benchmarks,
            matched_leakage_types=matched_leakage,
            tier_violation=tier_violation,
            isolation_notes="; ".join(notes) if notes else None
        )
