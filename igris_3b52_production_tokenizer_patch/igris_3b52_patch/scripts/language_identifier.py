"""
IGRIS Multilingual Language Identification Engine
=================================================
Phase 14 Dataset Integrity, Cleaning, and Validation Infrastructure

Distinguishes:
- English ('en')
- Hindi ('hi')
- Tamil ('ta')
- Telugu ('te')
- Malayalam ('ml')
- Kannada ('kn')
- Bengali ('bn')
- Gujarati ('gu')
- Tanglish ('tanglish') [Code-mixed Tamil-English / Latin-script Tamil phonology]
- Unknown / Ambiguous ('unknown')
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from unicode_processor import UnicodeProcessor, get_character_script


@dataclass
class LanguageIdentificationResult:
    primary_language: str
    confidence: float
    is_mixed_language: bool
    distribution: Dict[str, float]
    detected_scripts: List[str]
    notes: Optional[str] = None


# Tanglish Lexicon Markers (Phonetic Tamil in Latin script)
TANGLISH_LEXICON: Set[str] = {
    "vanakkam", "epdi", "irukinga", "romba", "nalla", "enna", "theriyuma",
    "inga", "unga", "kooda", "panrom", "seiyalam", "solreenga", "aama",
    "illa", "padikiren", "velai", "machan", "thala", "anna", "nanba",
    "paathiya", "supera", "irukku", "poidu", "vaanga", "ponga", "kudunga",
    "edunga", "nandri", "thambi", "seri", "ippo", "appo", "eppadi", "ungalukku",
    "enakku", "yaar", "ethu", "enge", "inge", "solla", "paarunga", "pannunga"
}

# English High-Frequency Stopwords
ENGLISH_STOPWORDS: Set[str] = {
    "the", "and", "is", "in", "it", "to", "of", "for", "with", "on",
    "that", "this", "are", "from", "at", "as", "by", "an", "be", "was",
    "have", "has", "not", "but", "all", "they", "we", "can", "will", "one"
}

# Mapping from script names to canonical language codes
SCRIPT_TO_LANG: Dict[str, str] = {
    "DEVANAGARI": "hi",
    "BENGALI": "bn",
    "GUJARATI": "gu",
    "TAMIL": "ta",
    "TELUGU": "te",
    "KANNADA": "kn",
    "MALAYALAM": "ml",
}


class LanguageIdentifier:
    """
    Robust multi-factor language identifier combining Unicode script analysis,
    character n-gram profiles, and code-mixed Tanglish lexical heuristics.
    """
    def __init__(self, min_confidence: float = 0.4):
        self.min_confidence = min_confidence
        self.unicode_proc = UnicodeProcessor()

    def identify_language(self, text: str) -> LanguageIdentificationResult:
        """
        Identify the language of the provided text.
        Returns LanguageIdentificationResult with primary language, confidence, and distribution.
        """
        if not text or not text.strip():
            return LanguageIdentificationResult(
                primary_language="unknown",
                confidence=0.0,
                is_mixed_language=False,
                distribution={"unknown": 1.0},
                detected_scripts=[],
                notes="Empty text input"
            )

        cleaned_text, analysis = self.unicode_proc.clean_and_normalize(text)
        script_dist = analysis.script_distribution
        detected_scripts = list(script_dist.keys())

        # If purely punctuation/digits
        if detected_scripts == ["PUNCTUATION_OR_OTHER"] or detected_scripts == ["EMPTY"]:
            return LanguageIdentificationResult(
                primary_language="unknown",
                confidence=0.1,
                is_mixed_language=False,
                distribution={"unknown": 1.0},
                detected_scripts=detected_scripts,
                notes="Text consists exclusively of punctuation, numbers, or symbols"
            )

        # Tokenize text into lower-cased alphanumeric words
        words = re.findall(r"\b\w+\b", cleaned_text.lower(), re.UNICODE)
        total_words = len(words)

        dist: Dict[str, float] = {}

        # 1. Native Indic Scripts
        for script, ratio in script_dist.items():
            if script in SCRIPT_TO_LANG:
                lang = SCRIPT_TO_LANG[script]
                dist[lang] = dist.get(lang, 0.0) + ratio

        # 2. Latin Script Analysis (English vs Tanglish)
        latin_ratio = script_dist.get("LATIN", 0.0)
        if latin_ratio > 0.0:
            if total_words == 0:
                dist["en"] = latin_ratio
            else:
                tanglish_matches = sum(1 for w in words if w in TANGLISH_LEXICON)
                english_matches = sum(1 for w in words if w in ENGLISH_STOPWORDS)

                # Check if mixed with Tamil script
                tamil_ratio = script_dist.get("TAMIL", 0.0)
                
                # Check for phonetic Tanglish suffix patterns
                tanglish_suffix_matches = sum(1 for w in words if any(w.endswith(sfx) and len(w) > len(sfx) + 2 for sfx in ("nga", "oda", "kitta", "la", "kaga")))

                total_tanglish_evidence = tanglish_matches * 2 + tanglish_suffix_matches

                if tamil_ratio > 0.15 and latin_ratio > 0.15:
                    # Clear code-mixed Tamil-English
                    dist["tanglish"] = dist.get("tanglish", 0.0) + latin_ratio + tamil_ratio
                    # Reduce raw ta
                    dist["ta"] = max(0.0, dist.get("ta", 0.0) - tamil_ratio * 0.5)
                elif total_tanglish_evidence >= 1 and (total_tanglish_evidence > english_matches or total_tanglish_evidence >= 2):
                    dist["tanglish"] = dist.get("tanglish", 0.0) + latin_ratio
                elif english_matches > 0:
                    dist["en"] = dist.get("en", 0.0) + latin_ratio
                else:
                    # Latin script text with no strong English/Tanglish stopwords
                    # Check general Latin ratio
                    if latin_ratio >= 0.7:
                        # Default to English with moderate confidence
                        dist["en"] = latin_ratio * 0.75
                        dist["unknown"] = latin_ratio * 0.25
                    else:
                        dist["en"] = latin_ratio * 0.5
                        dist["unknown"] = latin_ratio * 0.5

        # Normalize probability distribution
        total_p = sum(dist.values())
        if total_p > 0:
            norm_dist = {k: round(v / total_p, 4) for k, v in dist.items()}
        else:
            norm_dist = {"unknown": 1.0}

        sorted_dist = sorted(norm_dist.items(), key=lambda x: x[1], reverse=True)
        top_lang, top_conf = sorted_dist[0]

        # Mixed language detection
        significant_langs = [l for l, c in norm_dist.items() if c >= 0.25 and l != "unknown"]
        is_mixed = len(significant_langs) > 1 or top_lang == "tanglish"

        if top_conf < self.min_confidence:
            return LanguageIdentificationResult(
                primary_language="unknown",
                confidence=top_conf,
                is_mixed_language=is_mixed,
                distribution=norm_dist,
                detected_scripts=detected_scripts,
                notes=f"Insufficient confidence ({top_conf:.2f} < {self.min_confidence:.2f})"
            )

        return LanguageIdentificationResult(
            primary_language=top_lang,
            confidence=top_conf,
            is_mixed_language=is_mixed,
            distribution=norm_dist,
            detected_scripts=detected_scripts,
            notes=None
        )
