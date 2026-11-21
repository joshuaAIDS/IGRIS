"""
IGRIS Phase 24 / Phase 25 / Phase 26 Language Identification Engine v2
======================================================================
Three-category language identification for Tamil, English, and Tanglish.

Labels:
- TAMIL        — Native Tamil script text (U+0B80-U+0BFF dominant)
- ENGLISH      — Standard English in Latin script
- TANGLISH     — Tamil-English code-mixed (includes Romanized Tamil, discourse particles, intra-sentential switching)
- UNKNOWN      — Insufficient evidence for classification
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
    # Expanded colloquial, verb forms, and discourse connectives
    "aana", "piragu", "aagala", "pannitom", "aagidum", "pannina", "panninaa",
    "pannu", "panna", "mudiyum", "mudiyadhu", "varum", "varadhu",
    "konjam", "ippave", "appove", "avlo", "ivlo", "evlo", "apdi", "ipdi",
    "adhu", "idhu", "edhu", "avanga", "ivanga", "namba", "neenga", "naanga",
    "avaru", "ivaru", "sollu", "solunga", "ketka", "paaru", "therinjidhu",
    "poren", "porom", "vandhen", "vandhachu", "kelambu", "aachu",
    "paravala", "paravalai", "therla", "purila", "amaidhi", "kitta",
    "sollunga", "pesalaam", "paathutu", "vandhuten", "mudichutu",
}

# Tamil discourse particles commonly inserted into English sentences
TAMIL_DISCOURSE_PARTICLES: Set[str] = {
    "da", "pa", "di", "machan", "macha", "aiyo", "aiyoo", "seri",
    "romba", "kandippa", "thambi", "la", "dhan", "nu", "kooda",
    "dei", "dey", "daa", "paa", "dii", "ayyo", "chee", "chi",
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
    "before", "after", "during", "using", "between", "through",
}

# Specific multi-character Tamil verbal and nominal inflections in Latin script
# (Bare 'le', 'la', 'aa' are excluded to avoid collision with English words like 'reliable', 'multiple')
REFINED_TAMIL_SUFFIX_PATTERNS = (
    "nga", "ngu", "odu", "oda", "kitta", "kku", "kaga", "lai",
    "ppu", "ttu", "nnu", "chu", "dhu", "thu", "aam", "aal",
    "idudhu", "idum", "tom",
)


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
        if non_target_ratio > 0.40:
            dominant = max(NON_TARGET_SCRIPTS, key=lambda s: script_ratios.get(s, 0))
            return LangIDResult("OUT_OF_SCOPE", round(non_target_ratio, 4), False,
                                script_ratios, detected_scripts, sublabel=dominant,
                                notes=f"Non-target script dominant: {dominant}")

        tamil_ratio = script_ratios.get("TAMIL", 0.0)
        latin_ratio = script_ratios.get("LATIN", 0.0)

        # Tokenize words
        words = re.findall(r'\b\w+\b', text_nfc.lower(), re.UNICODE)
        total_words = len(words) if len(words) > 0 else 1

        # Check hyphenated clitics/suffixes (e.g., architecture-ல், server-la, lazy-aa)
        hyphen_parts = re.findall(r'(\w+)-(\w+)', text_nfc.lower(), re.UNICODE)
        hyphen_tamil_suffixes = sum(1 for _, sfx in hyphen_parts if sfx in {
            "la", "aa", "le", "ku", "uku", "oda", "kitta", "um", "ai", "dhan", "il"
        })

        # Tanglish evidence collection
        tanglish_lex_hits = sum(1 for w in words if w in TANGLISH_LEXICON)
        particle_hits = sum(1 for w in words if w in TAMIL_DISCOURSE_PARTICLES)
        english_stop_hits = sum(1 for w in words if w in ENGLISH_STOPWORDS)

        # Phonetic Tamil suffix patterns (Romanized Tamil morphology)
        suffix_hits = sum(1 for w in words if len(w) > 4 and any(w.endswith(sfx) for sfx in REFINED_TAMIL_SUFFIX_PATTERNS))

        tanglish_evidence = tanglish_lex_hits * 2 + particle_hits * 2 + suffix_hits + hyphen_tamil_suffixes * 2

        # --- Classification Logic ---

        # Case 1: Pure or overwhelmingly native Tamil script (>= 88% Tamil, Latin <= 12% isolated acronyms)
        if tamil_ratio >= 0.88 and latin_ratio <= 0.12:
            return LangIDResult("TAMIL", round(tamil_ratio, 4), False,
                                script_ratios, detected_scripts, sublabel="NATIVE_TAMIL")

        # Case 2: Meaningful script mixing
        if tamil_ratio > 0.0 and latin_ratio > 0.0:
            conf = round(min(tamil_ratio + latin_ratio, 1.0), 4)
            if tamil_ratio >= 0.50:
                sub = "TAMIL_WITH_ENGLISH_TECH"
            else:
                sub = "INTRA_SENTENTIAL_CODE_SWITCH"
            return LangIDResult("TANGLISH", conf, True, script_ratios, detected_scripts,
                                sublabel=sub, notes=f"Script mixed: Tamil={tamil_ratio:.2f} Latin={latin_ratio:.2f}")

        # Case 3: Overwhelmingly Tamil script without Latin
        if tamil_ratio >= 0.80:
            return LangIDResult("TAMIL", round(tamil_ratio, 4), False,
                                script_ratios, detected_scripts, sublabel="NATIVE_TAMIL")

        # Case 4: Latin script dominant (>= 80% Latin, 0% Tamil)
        if latin_ratio >= 0.80 and tamil_ratio == 0.0:
            tanglish_word_ratio = tanglish_evidence / total_words if total_words > 0 else 0

            # If there are explicit Tamil discourse particles or Tanglish lexicon hits or hyphenated clitics
            if particle_hits > 0 or tanglish_lex_hits > 0 or hyphen_tamil_suffixes > 0:
                if english_stop_hits > tanglish_lex_hits and particle_hits > 0:
                    sub = "ENGLISH_WITH_TAMIL_PARTICLES"
                else:
                    sub = "ROMANIZED_TAMIL"
                conf = round(min(0.60 + tanglish_word_ratio * 0.4, 0.95), 4)
                return LangIDResult("TANGLISH", conf, True, script_ratios, detected_scripts, sublabel=sub)

            # Suffix hits alone: must have multiple hits or substantial ratio
            if suffix_hits >= 2 or tanglish_word_ratio >= 0.20:
                return LangIDResult("TANGLISH", round(min(0.50 + tanglish_word_ratio, 0.90), 4),
                                    True, script_ratios, detected_scripts, sublabel="ROMANIZED_TAMIL")

            # Standard English: if english stopwords present or high Latin with 0 tanglish evidence
            if english_stop_hits >= 1 or (latin_ratio >= 0.90 and tanglish_evidence == 0):
                return LangIDResult("ENGLISH", round(min(0.60 + english_stop_hits / total_words, 0.98), 4),
                                    False, script_ratios, detected_scripts, sublabel="STANDARD_ENGLISH")

            # Single repeated character (low character entropy)
            unique_chars = len(set(text_nfc.replace(" ", "").lower()))
            if unique_chars <= 2:
                return LangIDResult("UNKNOWN", 0.2, False, script_ratios, detected_scripts, notes="Low character entropy")

            if tanglish_evidence >= 1:
                return LangIDResult("TANGLISH", 0.50, True, script_ratios, detected_scripts,
                                    sublabel="AMBIGUOUS_ROMANIZED")

            return LangIDResult("UNKNOWN", 0.3, False, script_ratios, detected_scripts,
                                notes="Latin script but insufficient English/Tanglish evidence")

        # Case 5: Small non-target contamination
        if non_target_ratio > 0.0 and non_target_ratio <= 0.40:
            return LangIDResult("UNKNOWN", 0.3, True, script_ratios, detected_scripts,
                                notes="Contaminated with non-target script")

        return LangIDResult("UNKNOWN", 0.2, False, script_ratios, detected_scripts,
                            notes="Insufficient classification evidence")
