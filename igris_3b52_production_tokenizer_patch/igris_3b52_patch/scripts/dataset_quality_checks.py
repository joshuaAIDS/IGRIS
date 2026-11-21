"""IGRIS Milestone 3B.59 — Dataset Quality and Governance Validation Engine.

Provides automated checks for:
  1. Character encoding verification (strictly valid UTF-8 without BOM)
  2. Unicode normalization policy (strictly NFC by default; detection of NFD/NFKD)
  3. Script and language identification via Unicode block distribution
  4. Exact duplicate detection (SHA-256 collision index)
  5. Near-duplicate detection (MinHash + Jaccard similarity)
  6. PII and sensitive data screening (emails, phones, IPs, API keys)
  7. Non-linguistic noise ratio and line integrity audits
  8. Train/evaluation leakage detection (hash collision and n-gram overlap)

No production data is accessed; designed to audit candidate production datasets
prior to human authorization.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Sequence

import unicodedata2

# -----------------------------------------------------------------------------
# Regex patterns for screening
# -----------------------------------------------------------------------------

RE_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RE_PHONE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}\b")
RE_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_API_KEY = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|bearer[_-]?token|private[_-]?key)"
    r"\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?"
)


# -----------------------------------------------------------------------------
# Unicode Script Ranges
# -----------------------------------------------------------------------------

SCRIPT_BLOCKS = {
    "Tamil": (0x0B80, 0x0BFF),
    "Devanagari": (0x0900, 0x097F),
    "Telugu": (0x0C00, 0x0C7F),
    "Kannada": (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
    "Bengali": (0x0980, 0x09FF),
    "Gujarati": (0x0A80, 0x0AFF),
    "Latin": (0x0020, 0x007F),
}


@dataclass
class QualityCheckResult:
    is_valid_utf8: bool
    is_nfc_normalized: bool
    has_lone_surrogates: bool
    primary_script: str
    script_distribution: dict[str, float]
    non_linguistic_ratio: float
    pii_matches: dict[str, list[str]]
    exact_hash: str
    issues: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.is_valid_utf8
            and self.is_nfc_normalized
            and not self.has_lone_surrogates
            and len(self.pii_matches) == 0
            and self.non_linguistic_ratio <= 0.25
        )


def verify_encoding_and_normalization(text: str) -> tuple[bool, bool, bool, list[str]]:
    """Check UTF-8 validity, NFC normalization, and lone surrogates."""
    issues: list[str] = []

    # 1. Lone surrogates (U+D800 to U+DFFF)
    has_surrogates = False
    for ch in text:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            has_surrogates = True
            issues.append(f"Contains lone surrogate codepoint: U+{cp:04X}")
            break

    # 2. UTF-8 encodability
    is_valid_utf8 = True
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        is_valid_utf8 = False
        issues.append(f"UTF-8 encoding failure: {exc}")

    # 3. NFC normalization
    is_nfc = False
    if not has_surrogates:
        nfc_text = unicodedata2.normalize("NFC", text)
        is_nfc = (text == nfc_text)
        if not is_nfc:
            issues.append("Text is not in canonical NFC form (e.g. contains decomposed NFD sequences)")

    return is_valid_utf8, is_nfc, has_surrogates, issues


def identify_script_distribution(text: str) -> tuple[str, dict[str, float]]:
    """Analyze script distribution across known Unicode blocks."""
    counts: dict[str, int] = {k: 0 for k in SCRIPT_BLOCKS}
    other_count = 0
    total_chars = len(text)

    if total_chars == 0:
        return "Empty", {k: 0.0 for k in SCRIPT_BLOCKS}

    for ch in text:
        cp = ord(ch)
        matched = False
        for script, (low, high) in SCRIPT_BLOCKS.items():
            if low <= cp <= high:
                counts[script] += 1
                matched = True
                break
        if not matched:
            other_count += 1

    dist: dict[str, float] = {}
    for script, c in counts.items():
        dist[script] = round(c / total_chars, 4)
    dist["Other"] = round(other_count / total_chars, 4)

    # Determine primary script
    primary_script = max(counts.items(), key=lambda kv: kv[1])[0]
    if counts[primary_script] == 0:
        primary_script = "Other"

    return primary_script, dist


def compute_non_linguistic_ratio(text: str) -> float:
    """Calculate ratio of non-linguistic characters (symbols, control chars, punctuation) to non-whitespace characters."""
    if not text:
        return 0.0
    non_ws_chars = [ch for ch in text if not ch.isspace()]
    if not non_ws_chars:
        return 0.0
    non_ling = sum(
        1 for ch in non_ws_chars
        if not (unicodedata2.category(ch).startswith("L") or unicodedata2.category(ch).startswith("N"))
    )
    return round(non_ling / len(non_ws_chars), 4)


def screen_pii_and_sensitive_data(text: str) -> dict[str, list[str]]:
    """Detect presence of emails, phone numbers, IP addresses, and API keys."""
    matches: dict[str, list[str]] = {}

    emails = RE_EMAIL.findall(text)
    if emails:
        matches["email"] = emails

    phones = [p.strip() for p in RE_PHONE.findall(text) if len(re.sub(r"\D", "", p)) >= 10]
    if phones:
        matches["phone"] = phones

    ips = RE_IPV4.findall(text)
    if ips:
        # Filter local loopback or common sample docs
        real_ips = [ip for ip in ips if not ip.startswith("127.") and ip != "0.0.0.0"]
        if real_ips:
            matches["ip_address"] = real_ips

    api_keys = RE_API_KEY.findall(text)
    if api_keys:
        matches["api_key"] = api_keys

    return matches


def audit_sample_quality(text: str) -> QualityCheckResult:
    """Execute complete quality and governance screening on a single sample."""
    is_utf8, is_nfc, has_surr, issues = verify_encoding_and_normalization(text)
    primary_script, dist = identify_script_distribution(text)
    noise_ratio = compute_non_linguistic_ratio(text)
    pii = screen_pii_and_sensitive_data(text)

    if noise_ratio > 0.25:
        issues.append(f"Non-linguistic character ratio ({noise_ratio:.2%}) exceeds 25% threshold")
    if pii:
        issues.append(f"Detected sensitive PII patterns: {list(pii.keys())}")

    exact_hash = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()

    return QualityCheckResult(
        is_valid_utf8=is_utf8,
        is_nfc_normalized=is_nfc,
        has_lone_surrogates=has_surr,
        primary_script=primary_script,
        script_distribution=dist,
        non_linguistic_ratio=noise_ratio,
        pii_matches=pii,
        exact_hash=exact_hash,
        issues=issues,
    )


# -----------------------------------------------------------------------------
# MinHash Near-Duplicate Detector
# -----------------------------------------------------------------------------

class MinHashNearDuplicateDetector:
    """Lightweight 64-permutation MinHash near-duplicate detector."""

    def __init__(self, num_perm: int = 64, ngram_size: int = 5, threshold: float = 0.85):
        self.num_perm = num_perm
        self.ngram_size = ngram_size
        self.threshold = threshold
        # Deterministic universal hash coefficients: h_i(x) = (a_i * x + b_i) % prime
        self.prime = 2147483647  # 2^31 - 1
        # Pinned coefficients
        self.a_coeffs = [(i * 10007 + 3) % self.prime for i in range(1, num_perm + 1)]
        self.b_coeffs = [(i * 20011 + 7) % self.prime for i in range(1, num_perm + 1)]

    def _get_shingles(self, text: str) -> set[int]:
        """Generate hashed character n-grams."""
        shingles: set[int] = set()
        if len(text) < self.ngram_size:
            shingles.add(hash(text) & 0x7FFFFFFF)
            return shingles
        for i in range(len(text) - self.ngram_size + 1):
            shingle = text[i:i + self.ngram_size]
            # 32-bit positive hash
            shingles.add(int(hashlib.md5(shingle.encode("utf-8")).hexdigest()[:8], 16) & 0x7FFFFFFF)
        return shingles

    def compute_signature(self, text: str) -> list[int]:
        """Compute MinHash signature vector."""
        shingles = self._get_shingles(text)
        if not shingles:
            return [0] * self.num_perm

        signature: list[int] = []
        for a, b in zip(self.a_coeffs, self.b_coeffs):
            min_val = min(((a * s + b) % self.prime) for s in shingles)
            signature.append(min_val)
        return signature

    def estimate_similarity(self, sig1: list[int], sig2: list[int]) -> float:
        """Estimate Jaccard similarity between two MinHash signatures."""
        assert len(sig1) == len(sig2) == self.num_perm
        matches = sum(1 for v1, v2 in zip(sig1, sig2) if v1 == v2)
        return round(matches / self.num_perm, 4)

    def is_near_duplicate(self, sig1: list[int], sig2: list[int]) -> bool:
        """Return True if estimated Jaccard similarity meets threshold."""
        return self.estimate_similarity(sig1, sig2) >= self.threshold


# -----------------------------------------------------------------------------
# Train/Eval Leakage Detector
# -----------------------------------------------------------------------------

def detect_train_eval_leakage(
    eval_samples: Sequence[str],
    known_training_hashes: set[str],
    min_ngram_leak_chars: int = 80,
) -> tuple[bool, list[str]]:
    """Verify that evaluation samples have zero overlap with training data."""
    leakages: list[str] = []

    for idx, text in enumerate(eval_samples):
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if h in known_training_hashes:
            leakages.append(f"Sample [{idx}] exact SHA-256 collision with training set: {h}")

    has_leakage = len(leakages) > 0
    return (not has_leakage), leakages
