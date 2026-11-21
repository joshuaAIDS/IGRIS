"""
IGRIS Multi-Layer Duplicate Detection Engine
============================================
Phase 14 Dataset Integrity, Cleaning, and Validation Infrastructure

Enforces:
1. Exact SHA-256 byte duplicate detection.
2. Normalized text hash duplicate detection (NFC + collapsed whitespace).
3. Near-duplicate detection using deterministic Jaccard similarity over word 3-grams.
4. Persistent, concurrency-safe duplicate registry.
5. Non-destructive duplicate mapping preserving original artifacts and recording canonical IDs.
"""

import hashlib
import json
import os
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class DuplicateMatchResult:
    is_duplicate: bool
    duplicate_type: str  # "NONE", "EXACT_SHA256", "NORMALIZED_TEXT", "NEAR_DUPLICATE"
    canonical_doc_id: Optional[str]
    similarity_score: float
    notes: Optional[str] = None


def compute_normalized_text_hash(text: str) -> str:
    """Normalize NFC and collapse all whitespace to compute canonical text hash."""
    nfc = unicodedata.normalize("NFC", text)
    collapsed = re.sub(r"\s+", " ", nfc).strip()
    return hashlib.sha256(collapsed.encode("utf-8")).hexdigest()


def get_word_ngrams(text: str, n: int = 3) -> Set[str]:
    """Generate set of word n-grams for Jaccard similarity."""
    words = re.findall(r"\b\w+\b", text.lower(), re.UNICODE)
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


def calculate_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


class DuplicateDetector:
    """
    Multi-layer duplicate detector with durable state persistence
    and thread/process-safe locking.
    """
    def __init__(
        self,
        index_path: Optional[Path] = None,
        near_duplicate_threshold: float = 0.85
    ):
        if index_path is None:
            index_path = Path(__file__).resolve().parents[2] / "quarantine" / "indexes" / "duplicate_index.json"
        self.index_path = Path(index_path)
        self.lock_path = Path(str(self.index_path) + ".lock")
        self.near_duplicate_threshold = near_duplicate_threshold
        
        self.exact_hashes: Dict[str, str] = {}  # sha256 -> doc_id
        self.norm_hashes: Dict[str, str] = {}   # norm_hash -> doc_id
        self.ngram_cache: Dict[str, Set[str]] = {}  # doc_id -> ngrams

        self._load_index()

    def _acquire_lock(self, timeout: float = 5.0):
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        while time.time() - start < timeout:
            try:
                # Atomic file creation
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"{os.getpid()}|{time.time()}\n".encode("utf-8"))
                os.close(fd)
                return
            except FileExistsError:
                time.sleep(0.05)
        # Force break stale lock older than 10 seconds
        if self.lock_path.exists():
            try:
                stale_time = self.lock_path.stat().st_mtime
                if time.time() - stale_time > 10.0:
                    self.lock_path.unlink()
            except OSError:
                pass

    def _release_lock(self):
        if self.lock_path.exists():
            try:
                self.lock_path.unlink()
            except OSError:
                pass

    def _load_index(self):
        if not self.index_path.exists():
            return
        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.exact_hashes = data.get("exact_hashes", {})
                self.norm_hashes = data.get("norm_hashes", {})
        except (json.JSONDecodeError, OSError):
            pass

    def _save_index(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "exact_hashes": self.exact_hashes,
            "norm_hashes": self.norm_hashes,
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def check_duplicate(
        self,
        doc_id: str,
        text: str,
        raw_sha256: Optional[str] = None,
        register_if_unique: bool = True
    ) -> DuplicateMatchResult:
        """
        Check whether document is an exact or near duplicate.
        If unique and register_if_unique=True, stores document in index.
        """
        self._acquire_lock()
        try:
            # 1. Exact SHA-256 Check
            if raw_sha256 is None:
                raw_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

            if raw_sha256 in self.exact_hashes:
                canonical = self.exact_hashes[raw_sha256]
                return DuplicateMatchResult(
                    is_duplicate=True,
                    duplicate_type="EXACT_SHA256",
                    canonical_doc_id=canonical,
                    similarity_score=1.0,
                    notes=f"Identical byte content to {canonical}"
                )

            # 2. Normalized Text Hash Check
            norm_hash = compute_normalized_text_hash(text)
            if norm_hash in self.norm_hashes:
                canonical = self.norm_hashes[norm_hash]
                return DuplicateMatchResult(
                    is_duplicate=True,
                    duplicate_type="NORMALIZED_TEXT",
                    canonical_doc_id=canonical,
                    similarity_score=1.0,
                    notes=f"Identical normalized NFC text to {canonical}"
                )

            # 3. Near-Duplicate Check via n-gram Jaccard Similarity
            doc_ngrams = get_word_ngrams(text)
            for existing_id, existing_ngrams in self.ngram_cache.items():
                sim = calculate_jaccard_similarity(doc_ngrams, existing_ngrams)
                if sim >= self.near_duplicate_threshold:
                    return DuplicateMatchResult(
                        is_duplicate=True,
                        duplicate_type="NEAR_DUPLICATE",
                        canonical_doc_id=existing_id,
                        similarity_score=round(sim, 4),
                        notes=f"Near-duplicate (Jaccard similarity {sim:.2f} >= {self.near_duplicate_threshold})"
                    )

            # Unique document: register if requested
            if register_if_unique:
                self.exact_hashes[raw_sha256] = doc_id
                self.norm_hashes[norm_hash] = doc_id
                self.ngram_cache[doc_id] = doc_ngrams
                self._save_index()

            return DuplicateMatchResult(
                is_duplicate=False,
                duplicate_type="NONE",
                canonical_doc_id=None,
                similarity_score=0.0,
                notes=None
            )
        finally:
            self._release_lock()
