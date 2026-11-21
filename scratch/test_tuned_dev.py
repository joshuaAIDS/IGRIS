import json, sys, re, unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

sys.path.insert(0, r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts')
from language_identifier_v2 import SCRIPT_RANGES, NON_TARGET_SCRIPTS, TANGLISH_LEXICON, TAMIL_DISCOURSE_PARTICLES, ENGLISH_STOPWORDS, _char_script, LangIDResult

# Refined suffix patterns: removed bare 'le', 'la', 'aa' (handled by hyphen_parts and particles)
REFINED_TAMIL_SUFFIX_PATTERNS = (
    "nga", "ngu", "odu", "oda", "kitta", "kku", "kaga", "lai",
    "ppu", "ttu", "nnu", "chu", "dhu", "thu", "aam", "aal",
    "idudhu", "idum", "tom",
)

class TunedLanguageIdentifier:
    def __init__(self, min_confidence: float = 0.35):
        self.min_confidence = min_confidence

    def identify(self, text: str) -> LangIDResult:
        if not text or not text.strip():
            return LangIDResult("UNKNOWN", 0.0, False, {}, [], notes="Empty input")

        text_nfc = unicodedata.normalize("NFC", text)
        script_counts = {}
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
        total_words = len(words) if words else 1

        # Check hyphenated clitics/suffixes (e.g., architecture-ல், server-la, lazy-aa)
        hyphen_parts = re.findall(r'(\w+)-(\w+)', text_nfc.lower(), re.UNICODE)
        hyphen_tamil_suffixes = sum(1 for _, sfx in hyphen_parts if sfx in {
            "la", "aa", "le", "ku", "uku", "oda", "kitta", "um", "ai", "dhan", "il"
        })

        # Tanglish evidence collection
        tanglish_lex_hits = sum(1 for w in words if w in TANGLISH_LEXICON)
        particle_hits = sum(1 for w in words if w in TAMIL_DISCOURSE_PARTICLES)
        english_stop_hits = sum(1 for w in words if w in ENGLISH_STOPWORDS)

        suffix_hits = sum(1 for w in words if len(w) > 4 and any(w.endswith(sfx) for sfx in REFINED_TAMIL_SUFFIX_PATTERNS))

        tanglish_evidence = tanglish_lex_hits * 2 + particle_hits * 2 + suffix_hits + hyphen_tamil_suffixes * 2

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

            # If repeated chars or unknown
            if len(set(text_nfc.replace(" ", "").lower())) <= 2:
                return LangIDResult("UNKNOWN", 0.2, False, script_ratios, detected_scripts, notes="Low character entropy")

            if tanglish_evidence >= 1:
                return LangIDResult("TANGLISH", 0.50, True, script_ratios, detected_scripts, sublabel="AMBIGUOUS_ROMANIZED")

            return LangIDResult("UNKNOWN", 0.3, False, script_ratios, detected_scripts,
                                notes="Latin script but insufficient English/Tanglish evidence")

        # Case 5: Small non-target contamination
        if non_target_ratio > 0.0 and non_target_ratio <= 0.40:
            return LangIDResult("UNKNOWN", 0.3, True, script_ratios, detected_scripts,
                                notes="Contaminated with non-target script")

        return LangIDResult("UNKNOWN", 0.2, False, script_ratios, detected_scripts,
                            notes="Insufficient classification evidence")

with open(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE26_DATASET_SPLITS.json', 'r', encoding='utf-8') as f:
    pkg = json.load(f)

dev_records = pkg['splits']['dev']
tuned_lid = TunedLanguageIdentifier()

correct = 0
total = len(dev_records)
mismatches = []

for r in dev_records:
    res = tuned_lid.identify(r['text'])
    gt = r['ground_truth_language']
    if res.label == gt:
        correct += 1
    else:
        mismatches.append({
            'id': r['id'],
            'gt': gt,
            'pred': res.label,
            'sub': res.sublabel,
            'diff': r['difficulty'],
            'cat': r['category'],
            'text': r['text'][:60]
        })

print(f"Tuned Dev accuracy: {correct}/{total} ({correct/total:.2%})")
print(f"Total mismatches: {len(mismatches)}")
for m in mismatches:
    print(f"  {m['id']} [{m['gt']} -> {m['pred']}] ({m['diff']}) {m['cat']}: {m['text']}")
