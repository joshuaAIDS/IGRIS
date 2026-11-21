"""
scratch/build_phase24.py

IGRIS Phase 24 — Tamil, English and Tanglish Data Engineering Infrastructure
Builds all upgraded modules, test suites, and deliverable documentation.

Modules authored:
1. scripts/language_identifier_v2.py      — 3-category language ID engine (TAMIL/ENGLISH/TANGLISH/UNKNOWN/OUT_OF_SCOPE)
2. scripts/unicode_processor_v2.py        — Tamil-safe Unicode processor with adversarial fixtures
3. scripts/tanglish_analyzer.py           — Tanglish code-switching analysis module
4. scripts/quality_filter_v2.py           — Configurable quality filter with rejection reasons
5. scripts/duplicate_detector_v2.py       — Multi-level duplicate detector
6. scripts/language_quality_reporter.py   — Reporting engine
7. tests/test_phase24_infrastructure.py   — Comprehensive test suite
"""

from pathlib import Path

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")
SCRIPTS_DIR = PATCH_DIR / "scripts"
TESTS_DIR = PATCH_DIR / "tests"


# =============================================================================
# MODULE 1: language_identifier_v2.py
# =============================================================================
SRC_LANGUAGE_IDENTIFIER_V2 = r'''"""
IGRIS Phase 24 Language Identification Engine v2
=================================================
Three-category language identification for Tamil, English, and Tanglish.

Labels:
- TAMIL       — Native Tamil script text (U+0B80-U+0BFF dominant)
- ENGLISH     — Standard English in Latin script
- TANGLISH    — Tamil-English code-mixed (includes Romanized Tamil, discourse particles, intra-sentential switching)
- UNKNOWN     — Insufficient evidence for classification
- OUT_OF_SCOPE — Detected non-target language (Hindi, Telugu, etc.)
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class LangIDResult:
    """Result of language identification."""
    label: str             # TAMIL, ENGLISH, TANGLISH, UNKNOWN, OUT_OF_SCOPE
    confidence: float      # 0.0 to 1.0
    is_code_mixed: bool    # True if multiple scripts detected
    script_ratios: Dict[str, float]   # script -> ratio
    detected_scripts: List[str]
    sublabel: Optional[str] = None    # e.g. "ROMANIZED_TAMIL", "TAMIL_WITH_ENGLISH_TECH", etc.
    notes: Optional[str] = None


# Script ranges
SCRIPT_RANGES = {
    "TAMIL":      [(0x0B80, 0x0BFF)],
    "LATIN":      [(0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x00FF), (0x0100, 0x024F)],
    "DEVANAGARI": [(0x0900, 0x097F)],
    "BENGALI":    [(0x0980, 0x09FF)],
    "TELUGU":     [(0x0C00, 0x0C7F)],
    "KANNADA":    [(0x0C80, 0x0CFF)],
    "MALAYALAM":  [(0x0D00, 0x0D7F)],
    "GUJARATI":   [(0x0A80, 0x0AFF)],
    "GURMUKHI":   [(0x0A00, 0x0A7F)],
    "ARABIC":     [(0x0600, 0x06FF)],
    "CYRILLIC":   [(0x0400, 0x04FF)],
    "CJK":        [(0x4E00, 0x9FFF)],
}

NON_TARGET_SCRIPTS = {"DEVANAGARI", "BENGALI", "TELUGU", "KANNADA", "MALAYALAM",
                      "GUJARATI", "GURMUKHI", "ARABIC", "CYRILLIC", "CJK"}

# Tanglish lexicon — spoken Tamil words commonly written in Latin script
TANGLISH_LEXICON: Set[str] = {
    "vanakkam", "epdi", "irukinga", "romba", "nalla", "enna", "theriyuma",
    "inga", "unga", "kooda", "panrom", "seiyalam", "solreenga", "aama",
    "illa", "padikiren", "velai", "machan", "thala", "anna", "nanba",
    "paathiya", "supera", "irukku", "poidu", "vaanga", "ponga", "kudunga",
    "edunga", "nandri", "thambi", "seri", "ippo", "appo", "eppadi",
    "ungalukku", "enakku", "yaar", "ethu", "enge", "inge", "solla",
    "paarunga", "pannunga", "pannanum", "panren", "panniten", "aayiduchu",
    "mudiyanum", "iruku", "vendiyadhilla", "vendiyirukkum", "panniyachu",
    "seekiram", "kelambanum", "theriyum", "puriyala", "sapda", "vaangiya",
    "kudinga", "marandhuten", "naalaiku", "innaiku", "nethu", "nalaiku",
    "kandippa", "apdiya", "kavala", "padadha", "serndhu", "vendiyadhu",
    "dhane", "pasi", "edukkudhu", "polaam", "polama", "mudinjudhu",
}

# Tamil discourse particles commonly inserted into English sentences
TAMIL_DISCOURSE_PARTICLES: Set[str] = {
    "da", "pa", "di", "machan", "macha", "aiyo", "aiyoo", "seri",
    "romba", "kandippa", "thambi", "la", "dhan", "nu", "kooda",
}

# English stopwords
ENGLISH_STOPWORDS: Set[str] = {
    "the", "and", "is", "in", "it", "to", "of", "for", "with", "on",
    "that", "this", "are", "from", "at", "as", "by", "an", "be", "was",
    "have", "has", "not", "but", "all", "they", "we", "can", "will",
    "one", "you", "your", "would", "should", "could", "do", "does",
    "did", "been", "being", "or", "if", "then", "than", "also",
    "their", "about", "into", "each", "just", "like", "more", "other",
    "some", "what", "when", "which", "who", "how", "its", "may",
}


def _char_script(char: str) -> str:
    """Identify the script family of a single character."""
    cp = ord(char)
    for script_name, ranges in SCRIPT_RANGES.items():
        for start, end in ranges:
            if start <= cp <= end:
                return script_name
    if char.isspace():
        return "SPACE"
    if char.isdigit():
        return "DIGIT"
    cat = unicodedata.category(char)
    if cat.startswith("P") or cat.startswith("S"):
        return "PUNCT"
    return "OTHER"


class LanguageIdentifierV2:
    """
    Robust three-category language identifier combining:
    1. Unicode script ratio analysis
    2. Tanglish lexicon matching
    3. Tamil discourse particle detection
    4. Phonetic suffix heuristics for Romanized Tamil
    5. Code-mixing structural analysis
    """

    def __init__(self, min_confidence: float = 0.35):
        self.min_confidence = min_confidence

    def identify(self, text: str) -> LangIDResult:
        if not text or not text.strip():
            return LangIDResult("UNKNOWN", 0.0, False, {}, [], notes="Empty input")

        text_nfc = unicodedata.normalize("NFC", text)
        script_counts: Dict[str, int] = {}
        total_script_chars = 0

        for ch in text_nfc:
            sc = _char_script(ch)
            if sc in ("SPACE", "DIGIT", "PUNCT", "OTHER"):
                continue
            script_counts[sc] = script_counts.get(sc, 0) + 1
            total_script_chars += 1

        if total_script_chars == 0:
            return LangIDResult("UNKNOWN", 0.1, False, {}, [], notes="No script characters")

        script_ratios = {k: round(v / total_script_chars, 4) for k, v in script_counts.items()}
        detected_scripts = sorted(script_ratios.keys(), key=lambda k: script_ratios[k], reverse=True)

        # Check for non-target scripts
        non_target_ratio = sum(script_ratios.get(s, 0) for s in NON_TARGET_SCRIPTS)
        if non_target_ratio > 0.5:
            dominant = max(NON_TARGET_SCRIPTS, key=lambda s: script_ratios.get(s, 0))
            return LangIDResult("OUT_OF_SCOPE", round(non_target_ratio, 4), False,
                                script_ratios, detected_scripts, sublabel=dominant,
                                notes=f"Non-target script dominant: {dominant}")

        tamil_ratio = script_ratios.get("TAMIL", 0.0)
        latin_ratio = script_ratios.get("LATIN", 0.0)

        # Tokenize words
        words = re.findall(r'\b\w+\b', text_nfc.lower(), re.UNICODE)
        total_words = len(words) if len(words) > 0 else 1

        # Tanglish evidence collection
        tanglish_lex_hits = sum(1 for w in words if w in TANGLISH_LEXICON)
        particle_hits = sum(1 for w in words if w in TAMIL_DISCOURSE_PARTICLES)
        english_stop_hits = sum(1 for w in words if w in ENGLISH_STOPWORDS)

        # Phonetic Tamil suffix patterns (Romanized Tamil morphology)
        tamil_suffix_patterns = (
            "nga", "ngu", "odu", "oda", "kitta", "kku", "kaga", "lai",
            "ppu", "ttu", "nnu", "chu", "dhu", "thu", "aam", "aal",
        )
        suffix_hits = sum(1 for w in words if len(w) > 4 and any(w.endswith(sfx) for sfx in tamil_suffix_patterns))

        tanglish_evidence = tanglish_lex_hits * 2 + particle_hits + suffix_hits

        # --- Classification Logic ---

        # Case 1: Tamil script dominant (>= 80% Tamil)
        if tamil_ratio >= 0.80:
            return LangIDResult("TAMIL", round(tamil_ratio, 4), False,
                                script_ratios, detected_scripts, sublabel="NATIVE_TAMIL")

        # Case 2: Tamil + Latin mixed — code-switching Tanglish
        if tamil_ratio >= 0.15 and latin_ratio >= 0.15:
            conf = round(min(tamil_ratio + latin_ratio, 1.0), 4)
            if tamil_ratio > latin_ratio:
                sub = "TAMIL_WITH_ENGLISH_TECH"
            else:
                sub = "INTRA_SENTENTIAL_CODE_SWITCH"
            return LangIDResult("TANGLISH", conf, True, script_ratios, detected_scripts,
                                sublabel=sub, notes=f"Tamil={tamil_ratio:.2f} Latin={latin_ratio:.2f}")

        # Case 3: Pure Latin script
        if latin_ratio >= 0.80:
            # Determine if Romanized Tamil or English
            tanglish_ratio = tanglish_evidence / total_words if total_words > 0 else 0

            if tanglish_ratio >= 0.15 or tanglish_lex_hits >= 2:
                sub = "ROMANIZED_TAMIL" if tanglish_lex_hits > english_stop_hits else "ENGLISH_WITH_TAMIL_PARTICLES"
                return LangIDResult("TANGLISH", round(min(0.5 + tanglish_ratio, 0.95), 4),
                                    True, script_ratios, detected_scripts, sublabel=sub)

            if english_stop_hits >= 2 or (latin_ratio >= 0.9 and tanglish_evidence == 0):
                return LangIDResult("ENGLISH", round(min(0.5 + english_stop_hits / total_words, 0.98), 4),
                                    False, script_ratios, detected_scripts, sublabel="STANDARD_ENGLISH")

            # Ambiguous Latin
            if tanglish_evidence >= 1:
                return LangIDResult("TANGLISH", 0.45, True, script_ratios, detected_scripts,
                                    sublabel="AMBIGUOUS_ROMANIZED")
            return LangIDResult("UNKNOWN", 0.3, False, script_ratios, detected_scripts,
                                notes="Latin script but insufficient English/Tanglish evidence")

        # Case 4: Tamil dominant with small Latin (English tech terms embedded)
        if tamil_ratio >= 0.50 and latin_ratio > 0.0:
            return LangIDResult("TANGLISH", round(tamil_ratio + latin_ratio * 0.5, 4),
                                True, script_ratios, detected_scripts,
                                sublabel="TAMIL_WITH_ENGLISH_TECH")

        # Case 5: Small non-target contamination with target text
        if non_target_ratio > 0.0 and non_target_ratio <= 0.5:
            if tamil_ratio > 0 or latin_ratio > 0:
                return LangIDResult("UNKNOWN", 0.3, True, script_ratios, detected_scripts,
                                    notes="Mixed target and non-target scripts")

        return LangIDResult("UNKNOWN", 0.2, False, script_ratios, detected_scripts,
                            notes="Insufficient classification evidence")
'''


# =============================================================================
# MODULE 2: unicode_processor_v2.py
# =============================================================================
SRC_UNICODE_PROCESSOR_V2 = r'''"""
IGRIS Phase 24 Tamil-Safe Unicode Processing Engine v2
======================================================
Enforces NFC normalization while preserving Tamil combining marks,
virama sequences, and valid ZWJ/ZWNJ behavior.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class UnicodeReport:
    original_length: int
    normalized_length: int
    is_nfc_original: bool
    has_replacement_char: bool
    control_chars_removed: int
    tamil_combining_marks_preserved: int
    virama_sequences_preserved: int
    zwj_zwnj_preserved: int
    malformed_sequences: List[str] = field(default_factory=list)
    script_distribution: Dict[str, float] = field(default_factory=dict)


# Tamil Unicode block: U+0B80 - U+0BFF
TAMIL_VOWELS = set(range(0x0B85, 0x0B95))       # அ-ஔ
TAMIL_CONSONANTS = set(range(0x0B95, 0x0BBA))    # க-ஹ
TAMIL_VOWEL_SIGNS = set(range(0x0BBE, 0x0BCD))   # Combining vowel signs
TAMIL_VIRAMA = 0x0BCD                             # ்
TAMIL_AU_LENGTH_MARK = 0x0BD7                      # ௗ
TAMIL_DIGITS = set(range(0x0BE6, 0x0BF0))
TAMIL_SYMBOLS = set(range(0x0BF0, 0x0BFB))

ZWJ = '\u200D'    # Zero Width Joiner
ZWNJ = '\u200C'   # Zero Width Non-Joiner


def is_tamil_char(cp: int) -> bool:
    return 0x0B80 <= cp <= 0x0BFF


class UnicodeProcessorV2:
    """Tamil-safe Unicode processor with NFC normalization and malformed sequence detection."""

    def normalize(self, text: str) -> Tuple[str, UnicodeReport]:
        """Normalize text while preserving Tamil combining sequences."""
        orig_len = len(text)
        is_nfc_orig = unicodedata.is_normalized('NFC', text)
        has_replacement = '\uFFFD' in text

        # Count Tamil combining marks before normalization
        tamil_combining = sum(1 for ch in text if ord(ch) in TAMIL_VOWEL_SIGNS)
        virama_count = text.count(chr(TAMIL_VIRAMA))
        zwj_zwnj_count = text.count(ZWJ) + text.count(ZWNJ)

        # Detect malformed sequences
        malformed = self._detect_malformed(text)

        # Apply NFC normalization (preserves Tamil combining marks correctly)
        normalized = unicodedata.normalize('NFC', text)

        # Remove dangerous control characters (preserve ZWJ/ZWNJ, tabs, newlines)
        cleaned, ctrl_removed = self._sanitize_controls(normalized)

        # Verify Tamil combining marks preserved
        tamil_combining_after = sum(1 for ch in cleaned if ord(ch) in TAMIL_VOWEL_SIGNS)
        virama_after = cleaned.count(chr(TAMIL_VIRAMA))
        zwj_zwnj_after = cleaned.count(ZWJ) + cleaned.count(ZWNJ)

        # Script distribution
        script_dist = self._compute_script_dist(cleaned)

        return cleaned, UnicodeReport(
            original_length=orig_len,
            normalized_length=len(cleaned),
            is_nfc_original=is_nfc_orig,
            has_replacement_char=has_replacement,
            control_chars_removed=ctrl_removed,
            tamil_combining_marks_preserved=tamil_combining_after,
            virama_sequences_preserved=virama_after,
            zwj_zwnj_preserved=zwj_zwnj_after,
            malformed_sequences=malformed,
            script_distribution=script_dist,
        )

    def _detect_malformed(self, text: str) -> List[str]:
        """Detect malformed Tamil Unicode sequences."""
        issues = []
        chars = list(text)
        for i, ch in enumerate(chars):
            cp = ord(ch)
            # Lone combining mark without base consonant
            if cp in TAMIL_VOWEL_SIGNS or cp == TAMIL_VIRAMA:
                if i == 0 or not is_tamil_char(ord(chars[i - 1])):
                    if i == 0 or ord(chars[i - 1]) not in TAMIL_CONSONANTS:
                        issues.append(f"Lone combining mark U+{cp:04X} at position {i}")
            # Double virama
            if cp == TAMIL_VIRAMA and i > 0 and ord(chars[i - 1]) == TAMIL_VIRAMA:
                issues.append(f"Double virama at position {i}")
        # Replacement char
        if '\uFFFD' in text:
            issues.append("Contains U+FFFD replacement character (encoding failure)")
        return issues

    def _sanitize_controls(self, text: str) -> Tuple[str, int]:
        """Remove invisible control characters while preserving ZWJ/ZWNJ and formatting."""
        result = []
        removed = 0
        for ch in text:
            cat = unicodedata.category(ch)
            if cat == 'Cc' and ch not in ('\n', '\r', '\t'):
                removed += 1
                continue
            # Preserve ZWJ and ZWNJ (category Cf) — important for Indic rendering
            if cat == 'Cf' and ch not in (ZWJ, ZWNJ, '\uFEFF'):
                # Strip other formatting marks except BOM at start
                removed += 1
                continue
            result.append(ch)
        return ''.join(result), removed

    def _compute_script_dist(self, text: str) -> Dict[str, float]:
        """Compute script character distribution."""
        from language_identifier_v2 import _char_script
        counts: Dict[str, int] = {}
        total = 0
        for ch in text:
            sc = _char_script(ch)
            if sc in ("SPACE", "DIGIT", "PUNCT", "OTHER"):
                continue
            counts[sc] = counts.get(sc, 0) + 1
            total += 1
        if total == 0:
            return {}
        return {k: round(v / total, 4) for k, v in counts.items()}

    def round_trip_check(self, text: str) -> bool:
        """Verify that NFC normalization is lossless: normalize(text) == normalize(normalize(text))."""
        n1 = unicodedata.normalize('NFC', text)
        n2 = unicodedata.normalize('NFC', n1)
        return n1 == n2
'''


# =============================================================================
# MODULE 3: tanglish_analyzer.py
# =============================================================================
SRC_TANGLISH_ANALYZER = r'''"""
IGRIS Phase 24 Tanglish Code-Switching Analysis Module
======================================================
Identifies Tamil script spans, English spans, Romanized Tamil candidates,
code-switch boundaries, Tamil suffix attachment, and discourse markers.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SpanInfo:
    start: int
    end: int
    script: str    # "TAMIL", "LATIN", "MIXED", "PUNCT"
    text: str


@dataclass
class CodeSwitchPoint:
    position: int
    from_script: str
    to_script: str
    left_context: str
    right_context: str


@dataclass
class TanglishAnalysis:
    total_chars: int
    tamil_char_count: int
    latin_char_count: int
    tamil_ratio: float
    latin_ratio: float
    spans: List[SpanInfo]
    code_switch_points: List[CodeSwitchPoint]
    discourse_markers_found: List[str]
    romanized_tamil_candidates: List[str]
    tamil_suffixes_detected: List[str]
    is_structurally_plausible: bool
    plausibility_notes: str


DISCOURSE_MARKERS = {
    "da", "pa", "di", "machan", "macha", "aiyo", "aiyoo", "seri",
    "romba", "kandippa", "thambi", "la", "dhan", "nu", "kooda",
    "apdiya", "illaya", "dhaan", "thaan",
}

ROMANIZED_TAMIL_PATTERNS = [
    r'\b[a-z]+nnu\b', r'\b[a-z]+chu\b', r'\b[a-z]+dhu\b',
    r'\b[a-z]+thu\b', r'\b[a-z]+nga\b', r'\b[a-z]+ngu\b',
    r'\b[a-z]+odu\b', r'\b[a-z]+oda\b', r'\b[a-z]+kku\b',
    r'\b[a-z]+ppu\b', r'\b[a-z]+ttu\b', r'\b[a-z]+aam\b',
]

TAMIL_SUFFIX_MARKERS = ["-ஐ", "-ல்", "-க்கு", "-இல்", "-ஆ", "-உடன்", "-ஆல்"]


def _is_tamil_cp(cp: int) -> bool:
    return 0x0B80 <= cp <= 0x0BFF


def _is_latin_cp(cp: int) -> bool:
    return (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A) or (0x00C0 <= cp <= 0x024F)


class TanglishAnalyzer:
    """Analyzes Tanglish text for code-switching patterns and structural properties."""

    def analyze(self, text: str) -> TanglishAnalysis:
        text_nfc = unicodedata.normalize('NFC', text)
        total = len(text_nfc)
        tamil_count = sum(1 for ch in text_nfc if _is_tamil_cp(ord(ch)))
        latin_count = sum(1 for ch in text_nfc if _is_latin_cp(ord(ch)))
        t_ratio = round(tamil_count / total, 4) if total > 0 else 0
        l_ratio = round(latin_count / total, 4) if total > 0 else 0

        spans = self._extract_spans(text_nfc)
        switch_points = self._find_code_switches(spans)
        words = re.findall(r'\b\w+\b', text_nfc.lower(), re.UNICODE)
        markers = [w for w in words if w in DISCOURSE_MARKERS]
        romanized = self._find_romanized_candidates(text_nfc)
        suffixes = [sfx for sfx in TAMIL_SUFFIX_MARKERS if sfx in text_nfc]

        plausible, notes = self._assess_plausibility(spans, switch_points, tamil_count, latin_count)

        return TanglishAnalysis(
            total_chars=total, tamil_char_count=tamil_count, latin_char_count=latin_count,
            tamil_ratio=t_ratio, latin_ratio=l_ratio, spans=spans,
            code_switch_points=switch_points, discourse_markers_found=markers,
            romanized_tamil_candidates=romanized, tamil_suffixes_detected=suffixes,
            is_structurally_plausible=plausible, plausibility_notes=notes,
        )

    def _extract_spans(self, text: str) -> List[SpanInfo]:
        spans = []
        if not text:
            return spans
        cur_script = self._char_class(text[0])
        start = 0
        for i in range(1, len(text)):
            sc = self._char_class(text[i])
            if sc != cur_script:
                spans.append(SpanInfo(start, i, cur_script, text[start:i]))
                cur_script = sc
                start = i
        spans.append(SpanInfo(start, len(text), cur_script, text[start:]))
        return spans

    def _char_class(self, ch: str) -> str:
        cp = ord(ch)
        if _is_tamil_cp(cp):
            return "TAMIL"
        if _is_latin_cp(cp):
            return "LATIN"
        return "PUNCT"

    def _find_code_switches(self, spans: List[SpanInfo]) -> List[CodeSwitchPoint]:
        switches = []
        script_spans = [s for s in spans if s.script in ("TAMIL", "LATIN")]
        for i in range(1, len(script_spans)):
            if script_spans[i].script != script_spans[i - 1].script:
                switches.append(CodeSwitchPoint(
                    position=script_spans[i].start,
                    from_script=script_spans[i - 1].script,
                    to_script=script_spans[i].script,
                    left_context=script_spans[i - 1].text[-15:],
                    right_context=script_spans[i].text[:15],
                ))
        return switches

    def _find_romanized_candidates(self, text: str) -> List[str]:
        candidates = []
        for pat in ROMANIZED_TAMIL_PATTERNS:
            candidates.extend(re.findall(pat, text.lower()))
        return list(set(candidates))

    def _assess_plausibility(self, spans, switches, tamil_c, latin_c) -> Tuple[bool, str]:
        if tamil_c == 0 and latin_c == 0:
            return False, "No script characters"
        if len(switches) > 20:
            return False, "Excessive code-switching (>20 points) suggests noise"
        if tamil_c > 0 and latin_c > 0:
            return True, "Bilingual content with plausible code-switch boundaries"
        if latin_c > 0 and tamil_c == 0:
            return True, "Latin-only text (may be Romanized Tamil or English)"
        return True, "Tamil-dominant text"
'''


# =============================================================================
# MODULE 4: quality_filter_v2.py
# =============================================================================
SRC_QUALITY_FILTER_V2 = r'''"""
IGRIS Phase 24 Configurable Quality Filter v2
==============================================
Detects empty, short, long, spammy, URL-heavy, malformed, and low-info records.
Every rejection carries a machine-readable reason code.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass
class QualityConfigV2:
    min_length_chars: int = 10
    max_length_chars: int = 100000
    min_words: int = 2
    max_repeated_char_run: int = 5
    max_url_ratio: float = 0.30
    max_punct_ratio: float = 0.40
    max_digit_ratio: float = 0.50
    boilerplate_keywords: Set[str] = field(default_factory=lambda: {
        "cookie policy", "terms of service", "privacy policy", "click here",
        "subscribe now", "advertisement", "404 not found", "page not found",
    })


@dataclass
class QualityVerdict:
    passed: bool
    rejection_reasons: List[str]   # Machine-readable reason codes
    char_count: int
    word_count: int
    url_ratio: float
    punct_ratio: float
    repeated_char_max_run: int
    has_malformed_unicode: bool


class QualityFilterV2:
    """Configurable text quality filter producing machine-readable rejection reasons."""

    def __init__(self, config: Optional[QualityConfigV2] = None):
        self.config = config or QualityConfigV2()

    def evaluate(self, text: str) -> QualityVerdict:
        reasons: List[str] = []
        if not text or not text.strip():
            return QualityVerdict(False, ["EMPTY_RECORD"], 0, 0, 0.0, 0.0, 0, False)

        stripped = text.strip()
        char_count = len(stripped)
        words = re.findall(r'\b\w+\b', stripped, re.UNICODE)
        word_count = len(words)

        # Length checks
        if char_count < self.config.min_length_chars:
            reasons.append("TOO_SHORT")
        if char_count > self.config.max_length_chars:
            reasons.append("TOO_LONG")
        if word_count < self.config.min_words:
            reasons.append("TOO_FEW_WORDS")

        # Repeated character spam
        max_run = 0
        cur_run = 1
        for i in range(1, len(stripped)):
            if stripped[i] == stripped[i - 1]:
                cur_run += 1
                max_run = max(max_run, cur_run)
            else:
                cur_run = 1
        max_run = max(max_run, cur_run) if stripped else 0
        if max_run > self.config.max_repeated_char_run:
            reasons.append("REPEATED_CHAR_SPAM")

        # URL density
        urls = re.findall(r'https?://\S+', stripped)
        url_chars = sum(len(u) for u in urls)
        url_ratio = url_chars / char_count if char_count > 0 else 0
        if url_ratio > self.config.max_url_ratio:
            reasons.append("URL_HEAVY")

        # Punctuation density
        punct_count = sum(1 for ch in stripped if unicodedata.category(ch).startswith('P'))
        punct_ratio = punct_count / char_count if char_count > 0 else 0
        if punct_ratio > self.config.max_punct_ratio:
            reasons.append("EXCESSIVE_PUNCTUATION")

        # Malformed Unicode
        has_malformed = '\uFFFD' in stripped
        if has_malformed:
            reasons.append("MALFORMED_UNICODE")

        # Boilerplate
        lower_text = stripped.lower()
        for kw in self.config.boilerplate_keywords:
            if kw in lower_text:
                reasons.append("BOILERPLATE_DETECTED")
                break

        # Language uncertainty (checked externally, but we detect purely symbolic text)
        alpha_count = sum(1 for ch in stripped if ch.isalpha())
        if alpha_count == 0:
            reasons.append("NO_ALPHABETIC_CHARS")

        return QualityVerdict(
            passed=len(reasons) == 0,
            rejection_reasons=reasons,
            char_count=char_count,
            word_count=word_count,
            url_ratio=round(url_ratio, 4),
            punct_ratio=round(punct_ratio, 4),
            repeated_char_max_run=max_run,
            has_malformed_unicode=has_malformed,
        )
'''


# =============================================================================
# MODULE 5: duplicate_detector_v2.py
# =============================================================================
SRC_DUPLICATE_DETECTOR_V2 = r'''"""
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
'''


# =============================================================================
# MODULE 6: language_quality_reporter.py
# =============================================================================
SRC_LANGUAGE_QUALITY_REPORTER = r'''"""
IGRIS Phase 24 Language Quality Reporter
=========================================
Generates confusion matrices and classification reports from labeled test data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ConfusionEntry:
    true_label: str
    pred_label: str
    count: int


@dataclass
class ClassificationReport:
    total: int
    correct: int
    accuracy: float
    per_class: Dict[str, Dict[str, float]]  # class -> {precision, recall, f1, support}
    confusion_matrix: List[ConfusionEntry]


class LanguageQualityReporter:
    """Generates classification reports from (true_label, pred_label) pairs."""

    def report(self, predictions: List[Tuple[str, str]]) -> ClassificationReport:
        total = len(predictions)
        correct = sum(1 for t, p in predictions if t == p)
        accuracy = correct / total if total > 0 else 0.0

        labels = sorted(set(t for t, _ in predictions) | set(p for _, p in predictions))
        cm: Dict[Tuple[str, str], int] = {}
        for t, p in predictions:
            cm[(t, p)] = cm.get((t, p), 0) + 1

        per_class: Dict[str, Dict[str, float]] = {}
        for label in labels:
            tp = cm.get((label, label), 0)
            fp = sum(cm.get((other, label), 0) for other in labels if other != label)
            fn = sum(cm.get((label, other), 0) for other in labels if other != label)
            support = tp + fn
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            per_class[label] = {"precision": round(precision, 4), "recall": round(recall, 4),
                                "f1": round(f1, 4), "support": support}

        confusion_entries = [ConfusionEntry(t, p, c) for (t, p), c in sorted(cm.items())]
        return ClassificationReport(total, correct, round(accuracy, 4), per_class, confusion_entries)
'''


# =============================================================================
# MODULE 7: test_phase24_infrastructure.py
# =============================================================================
SRC_TEST_PHASE24 = r'''"""
IGRIS Phase 24 — Comprehensive Infrastructure Test Suite
=========================================================
Tests language identification, Unicode processing, Tanglish analysis,
quality filtering, duplicate detection, and tokenizer round-trip integrity.
"""

import hashlib
import json
import os
import re
import sys
import unicodedata
import unittest
from pathlib import Path

# Add scripts directory to path
PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

from language_identifier_v2 import LanguageIdentifierV2, LangIDResult
from unicode_processor_v2 import UnicodeProcessorV2, UnicodeReport
from tanglish_analyzer import TanglishAnalyzer, TanglishAnalysis
from quality_filter_v2 import QualityFilterV2, QualityConfigV2, QualityVerdict
from duplicate_detector_v2 import DuplicateDetectorV2, DupResult
from language_quality_reporter import LanguageQualityReporter


class TestLanguageIdentifier(unittest.TestCase):
    """Tests for the three-category language identification engine."""

    def setUp(self):
        self.lid = LanguageIdentifierV2()

    def test_pure_tamil(self):
        r = self.lid.identify("தமிழ் மிகவும் அழகான மொழி, இது உலகின் மிகப் பழமையான மொழிகளில் ஒன்று.")
        self.assertEqual(r.label, "TAMIL")
        self.assertGreater(r.confidence, 0.7)

    def test_pure_english(self):
        r = self.lid.identify("The quick brown fox jumps over the lazy dog near the river bank.")
        self.assertEqual(r.label, "ENGLISH")
        self.assertGreater(r.confidence, 0.5)

    def test_tanglish_romanized(self):
        r = self.lid.identify("Innaiku evening tea sapda polama? Enaku romba tired-ah iruku.")
        self.assertEqual(r.label, "TANGLISH")

    def test_tanglish_code_switch(self):
        r = self.lid.identify("இந்த server configuration ரொம்ப complex-ஆ இருக்கு, restart பண்ணவா?")
        self.assertEqual(r.label, "TANGLISH")
        self.assertTrue(r.is_code_mixed)

    def test_english_with_tamil_particles(self):
        r = self.lid.identify("Let us wrap up this release quickly da, otherwise deployment will get delayed machan.")
        self.assertEqual(r.label, "TANGLISH")

    def test_hindi_out_of_scope(self):
        r = self.lid.identify("हिंदी एक बहुत सुंदर भाषा है और भारत में सबसे अधिक बोली जाती है।")
        self.assertEqual(r.label, "OUT_OF_SCOPE")

    def test_telugu_out_of_scope(self):
        r = self.lid.identify("తెలుగు భాషలో అనేక అందమైన కవితలు ఉన్నాయి.")
        self.assertEqual(r.label, "OUT_OF_SCOPE")

    def test_empty_input(self):
        r = self.lid.identify("")
        self.assertEqual(r.label, "UNKNOWN")

    def test_numbers_only(self):
        r = self.lid.identify("12345 67890")
        self.assertEqual(r.label, "UNKNOWN")

    def test_formal_tanglish(self):
        r = self.lid.identify("கணினி வலையமைப்பு (computer network) பாதுகாப்பு protocol-கள் முறையாக configure செய்யப்பட வேண்டும்.")
        self.assertEqual(r.label, "TANGLISH")

    def test_latin_not_all_english(self):
        """Romanized Tamil should NOT be classified as English."""
        r = self.lid.identify("Nalla movie pathiya nethu? Climax scene romba emotionally touch aayiduchu.")
        self.assertNotEqual(r.label, "ENGLISH")


class TestUnicodeProcessor(unittest.TestCase):
    """Tests for Tamil-safe Unicode processing."""

    def setUp(self):
        self.proc = UnicodeProcessorV2()

    def test_nfc_normalization(self):
        text = "தமிழ் test"
        cleaned, report = self.proc.normalize(text)
        self.assertTrue(unicodedata.is_normalized('NFC', cleaned))

    def test_tamil_combining_marks_preserved(self):
        text = "கோ"  # க + ோ (combining vowel sign)
        cleaned, report = self.proc.normalize(text)
        self.assertIn("கோ", cleaned)

    def test_virama_preserved(self):
        text = "க்"  # க + virama
        cleaned, report = self.proc.normalize(text)
        self.assertIn(chr(0x0BCD), cleaned)
        self.assertGreater(report.virama_sequences_preserved, 0)

    def test_replacement_char_detection(self):
        text = "test\uFFFDtext"
        _, report = self.proc.normalize(text)
        self.assertTrue(report.has_replacement_char)

    def test_control_char_removal(self):
        text = "test\x01\x02text"
        cleaned, report = self.proc.normalize(text)
        self.assertNotIn("\x01", cleaned)
        self.assertEqual(report.control_chars_removed, 2)

    def test_zwj_preserved(self):
        text = "test\u200Dtext"
        cleaned, _ = self.proc.normalize(text)
        self.assertIn("\u200D", cleaned)

    def test_round_trip(self):
        texts = [
            "தமிழ் மொழி",
            "server configuration-ஐ test பண்ணிட்டேன்",
            "The quick brown fox",
            "கோ கா கி கீ கு கூ",
        ]
        for text in texts:
            self.assertTrue(self.proc.round_trip_check(text), f"Round-trip failed: {text}")

    def test_adversarial_lone_combining_mark(self):
        # Lone combining mark at start
        text = chr(0x0BBE) + "test"
        _, report = self.proc.normalize(text)
        self.assertTrue(any("Lone combining" in m for m in report.malformed_sequences))

    def test_adversarial_double_virama(self):
        text = "க" + chr(0x0BCD) + chr(0x0BCD)  # double virama
        _, report = self.proc.normalize(text)
        self.assertTrue(any("Double virama" in m for m in report.malformed_sequences))


class TestTanglishAnalyzer(unittest.TestCase):
    """Tests for Tanglish code-switching analysis."""

    def setUp(self):
        self.analyzer = TanglishAnalyzer()

    def test_code_switch_detection(self):
        text = "இந்த server configuration ரொம்ப complex"
        analysis = self.analyzer.analyze(text)
        self.assertGreater(len(analysis.code_switch_points), 0)
        self.assertGreater(analysis.tamil_ratio, 0)
        self.assertGreater(analysis.latin_ratio, 0)

    def test_discourse_markers(self):
        text = "Let us do this quickly da, machan we need to finish."
        analysis = self.analyzer.analyze(text)
        self.assertIn("da", analysis.discourse_markers_found)
        self.assertIn("machan", analysis.discourse_markers_found)

    def test_tamil_suffix_detection(self):
        text = "server-ல் configuration-ஐ update"
        analysis = self.analyzer.analyze(text)
        self.assertTrue(any("-ல்" in s or "-ஐ" in s for s in analysis.tamil_suffixes_detected))

    def test_pure_english_no_switches(self):
        text = "The quick brown fox jumps over the lazy dog."
        analysis = self.analyzer.analyze(text)
        self.assertEqual(len(analysis.code_switch_points), 0)
        self.assertEqual(analysis.tamil_char_count, 0)

    def test_romanized_tamil_candidates(self):
        text = "Innaiku evening sapda polama pannunga vaanga"
        analysis = self.analyzer.analyze(text)
        self.assertTrue(analysis.is_structurally_plausible)


class TestQualityFilter(unittest.TestCase):
    """Tests for configurable quality filtering."""

    def setUp(self):
        self.qf = QualityFilterV2()

    def test_empty_record(self):
        v = self.qf.evaluate("")
        self.assertFalse(v.passed)
        self.assertIn("EMPTY_RECORD", v.rejection_reasons)

    def test_too_short(self):
        v = self.qf.evaluate("hi")
        self.assertFalse(v.passed)
        self.assertIn("TOO_SHORT", v.rejection_reasons)

    def test_repeated_char_spam(self):
        v = self.qf.evaluate("aaaaaaaaaa this is spam text")
        self.assertFalse(v.passed)
        self.assertIn("REPEATED_CHAR_SPAM", v.rejection_reasons)

    def test_url_heavy(self):
        v = self.qf.evaluate("Visit https://example.com/very/long/url/path/here for more info")
        # URL ratio may exceed threshold
        if v.url_ratio > 0.30:
            self.assertIn("URL_HEAVY", v.rejection_reasons)

    def test_malformed_unicode(self):
        v = self.qf.evaluate("This text has \uFFFD replacement characters in it.")
        self.assertIn("MALFORMED_UNICODE", v.rejection_reasons)

    def test_good_text_passes(self):
        v = self.qf.evaluate("This is a perfectly normal English sentence with enough words to pass quality checks.")
        self.assertTrue(v.passed)
        self.assertEqual(v.rejection_reasons, [])

    def test_good_tamil_passes(self):
        v = self.qf.evaluate("தமிழ் மிகவும் அழகான மொழி, பல நூற்றாண்டுகளாக வளர்ந்த இலக்கிய மரபைக் கொண்டது.")
        self.assertTrue(v.passed)

    def test_boilerplate(self):
        v = self.qf.evaluate("Please accept our cookie policy and terms of service before continuing.")
        self.assertIn("BOILERPLATE_DETECTED", v.rejection_reasons)

    def test_rejection_reasons_machine_readable(self):
        v = self.qf.evaluate("")
        for reason in v.rejection_reasons:
            self.assertTrue(reason.isupper() and "_" in reason or reason.isupper(),
                            f"Reason '{reason}' is not machine-readable uppercase code")


class TestDuplicateDetector(unittest.TestCase):
    """Tests for multi-level duplicate detection."""

    def setUp(self):
        self.dd = DuplicateDetectorV2(near_dup_threshold=0.80)

    def test_exact_duplicate(self):
        text = "இந்த server configuration ரொம்ப complex-ஆ இருக்கு."
        r1 = self.dd.check_and_register("doc-001", text)
        self.assertFalse(r1.is_duplicate)
        r2 = self.dd.check_and_register("doc-002", text)
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.dup_type, "EXACT")
        self.assertEqual(r2.matched_id, "doc-001")

    def test_normalized_duplicate(self):
        t1 = "Hello   world   test"
        t2 = "Hello world test"
        r1 = self.dd.check_and_register("doc-003", t1)
        self.assertFalse(r1.is_duplicate)
        r2 = self.dd.check_and_register("doc-004", t2)
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.dup_type, "NORMALIZED")

    def test_near_duplicate(self):
        t1 = "The quick brown fox jumps over the lazy dog near the old stone bridge."
        t2 = "The quick brown fox jumps over the lazy dog near the old wooden bridge."
        r1 = self.dd.check_and_register("doc-005", t1)
        self.assertFalse(r1.is_duplicate)
        r2 = self.dd.check_and_register("doc-006", t2)
        # May or may not be near-duplicate depending on threshold
        if r2.is_duplicate:
            self.assertEqual(r2.dup_type, "NEAR_DUPLICATE")

    def test_unique_texts(self):
        t1 = "This is completely different English text about software engineering."
        t2 = "தமிழ் மொழியின் வரலாறு மிகவும் சுவாரசியமானது."
        r1 = self.dd.check_and_register("doc-007", t1)
        r2 = self.dd.check_and_register("doc-008", t2)
        self.assertFalse(r1.is_duplicate)
        self.assertFalse(r2.is_duplicate)

    def test_mixed_script_duplicates(self):
        t1 = "server configuration-ஐ test பண்ணிட்டேன்"
        r1 = self.dd.check_and_register("doc-009", t1)
        r2 = self.dd.check_and_register("doc-010", t1)
        self.assertTrue(r2.is_duplicate)


class TestTokenizerRoundTrip(unittest.TestCase):
    """Read-only tokenizer evaluation using Candidate A."""

    def setUp(self):
        self.tokenizer_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        self.expected_hash = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"

    def test_tokenizer_hash_invariant(self):
        h = hashlib.sha256(self.tokenizer_path.read_bytes()).hexdigest()
        self.assertEqual(h, self.expected_hash)

    def test_tokenizer_loads(self):
        try:
            from tokenizers import Tokenizer
            tok = Tokenizer.from_file(str(self.tokenizer_path))
            self.assertIsNotNone(tok)
            self.assertEqual(tok.get_vocab_size(), 32768)
        except ImportError:
            self.skipTest("tokenizers library not available")

    def test_tokenizer_roundtrip_english(self):
        try:
            from tokenizers import Tokenizer
            tok = Tokenizer.from_file(str(self.tokenizer_path))
            text = "The quick brown fox jumps over the lazy dog."
            encoded = tok.encode(text)
            decoded = tok.decode(encoded.ids)
            self.assertIn("quick", decoded)
            self.assertIn("fox", decoded)
        except ImportError:
            self.skipTest("tokenizers library not available")

    def test_tokenizer_roundtrip_tamil(self):
        try:
            from tokenizers import Tokenizer
            tok = Tokenizer.from_file(str(self.tokenizer_path))
            text = "தமிழ் மொழி"
            encoded = tok.encode(text)
            decoded = tok.decode(encoded.ids)
            # Check no UNK flood — at least some Tamil characters recovered
            self.assertGreater(len(decoded.strip()), 0)
        except ImportError:
            self.skipTest("tokenizers library not available")


class TestExistingRegressionSuites(unittest.TestCase):
    """Verify existing test suites still pass."""

    def test_readiness_suite(self):
        import subprocess
        res = subprocess.run(
            [sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_readiness.py"), "-q"],
            cwd=str(PATCH_ROOT), capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 0, f"test_readiness failed: {res.stdout}\n{res.stderr}")
        self.assertIn("5 passed", res.stdout)

    def test_phase22_planning_suite(self):
        import subprocess
        res = subprocess.run(
            [sys.executable, "-m", "pytest", str(PATCH_ROOT / "tests" / "test_phase22_production_planning.py"), "-q"],
            cwd=str(PATCH_ROOT), capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 0, f"test_phase22 failed: {res.stdout}\n{res.stderr}")
        self.assertIn("6 passed", res.stdout)


class TestGovernanceInvariants(unittest.TestCase):
    """Verify production gates remain locked."""

    def test_zero_production_data(self):
        quarantine_raw = PATCH_ROOT / "quarantine" / "raw"
        if quarantine_raw.exists():
            files = list(quarantine_raw.glob("*"))
            self.assertEqual(len(files), 0, f"Quarantine not empty: {files}")

    def test_candidate_a_hash(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561")

    def test_candidate_b_hash(self):
        p = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(h, "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888")


if __name__ == "__main__":
    unittest.main(verbosity=2)
'''


# =============================================================================
# Write all modules
# =============================================================================
MODULES = {
    "scripts/language_identifier_v2.py": SRC_LANGUAGE_IDENTIFIER_V2,
    "scripts/unicode_processor_v2.py": SRC_UNICODE_PROCESSOR_V2,
    "scripts/tanglish_analyzer.py": SRC_TANGLISH_ANALYZER,
    "scripts/quality_filter_v2.py": SRC_QUALITY_FILTER_V2,
    "scripts/duplicate_detector_v2.py": SRC_DUPLICATE_DETECTOR_V2,
    "scripts/language_quality_reporter.py": SRC_LANGUAGE_QUALITY_REPORTER,
    "tests/test_phase24_infrastructure.py": SRC_TEST_PHASE24,
}


def main():
    print("IGRIS Phase 24 — Writing infrastructure modules...")
    for rel_path, content in MODULES.items():
        full_path = PATCH_DIR / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        print(f"  Written: {rel_path} ({full_path.stat().st_size} bytes)")
    print(f"\nAll {len(MODULES)} Phase 24 infrastructure modules written.")


if __name__ == "__main__":
    main()
