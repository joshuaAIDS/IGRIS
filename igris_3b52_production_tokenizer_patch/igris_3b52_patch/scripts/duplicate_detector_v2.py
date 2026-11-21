"""
IGRIS Phase 24 Multi-Level Duplicate Detector v2
=================================================
1. Exact byte-level SHA-256 duplicate detection.
2. Unicode NFC-normalized text duplicate detection.
3. Near-duplicate detection using Jaccard similarity over word 3-grams.
Deterministic, configurable thresholds, mixed Tamil-English support.
"""

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class DupResult:
    is_duplicate: bool
    dup_type: str        # NONE, EXACT, NORMALIZED, NEAR_DUPLICATE
    matched_id: Optional[str]
    similarity: float
    notes: Optional[str] = None


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _norm_hash(text: str) -> str:
    nfc = unicodedata.normalize('NFC', text)
    collapsed = re.sub(r'\s+', ' ', nfc).strip().lower()
    return hashlib.sha256(collapsed.encode('utf-8')).hexdigest()


def _word_ngrams(text: str, n: int = 3) -> Set[str]:
    words = re.findall(r'\b\w+\b', text.lower(), re.UNICODE)
    if len(words) < n:
        return {' '.join(words)} if words else set()
    return {' '.join(words[i:i + n]) for i in range(len(words) - n + 1)}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class DuplicateDetectorV2:
    """In-memory multi-level duplicate detector."""

    def __init__(self, near_dup_threshold: float = 0.80):
        self.near_dup_threshold = near_dup_threshold
        self._exact: Dict[str, str] = {}     # hash -> doc_id
        self._norm: Dict[str, str] = {}      # norm_hash -> doc_id
        self._ngrams: Dict[str, Set[str]] = {}  # doc_id -> ngrams

    def check_and_register(self, doc_id: str, text: str) -> DupResult:
        """Check for duplicates and register if unique."""
        exact_h = _sha256(text)
        if exact_h in self._exact:
            return DupResult(True, "EXACT", self._exact[exact_h], 1.0)

        norm_h = _norm_hash(text)
        if norm_h in self._norm:
            return DupResult(True, "NORMALIZED", self._norm[norm_h], 1.0,
                             notes="Identical after NFC + whitespace collapse + lowercase")

        ngrams = _word_ngrams(text)
        best_match = None
        best_sim = 0.0
        for existing_id, existing_ng in self._ngrams.items():
            sim = _jaccard(ngrams, existing_ng)
            if sim > best_sim:
                best_sim = sim
                best_match = existing_id

        if best_sim >= self.near_dup_threshold and best_match:
            return DupResult(True, "NEAR_DUPLICATE", best_match, round(best_sim, 4))

        # Register as unique
        self._exact[exact_h] = doc_id
        self._norm[norm_h] = doc_id
        self._ngrams[doc_id] = ngrams
        return DupResult(False, "NONE", None, round(best_sim, 4))

    @property
    def registered_count(self) -> int:
        return len(self._exact)
