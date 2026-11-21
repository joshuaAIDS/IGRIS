import json, sys, re, unicodedata
from collections import Counter, defaultdict

# Import existing ranges and data
sys.path.insert(0, r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts')
from language_identifier_v2 import SCRIPT_RANGES, NON_TARGET_SCRIPTS, _char_script, LangIDResult

# Expanded lexicon
ENHANCED_TANGLISH_LEXICON = {
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
    # Additional common verbs and markers
    "aana", "piragu", "aagala", "pannitom", "aagidum", "pannina", "panninaa",
    "pannu", "panna", "mudiyum", "mudiyadhu", "varum", "varadhu",
    "konjam", "ippave", "appove", "avlo", "ivlo", "evlo", "apdi", "ipdi",
    "adhu", "idhu", "edhu", "avanga", "ivanga", "namba", "neenga", "naanga",
    "avaru", "ivaru", "sollu", "solunga", "ketka", "paaru", "therinjidhu",
    "poren", "porom", "vandhen", "vandhachu", "kelambu", "aachu", "aachu",
    "paravala", "paravalai", "therla", "purila", "amaidhi",
}

ENHANCED_TAMIL_DISCOURSE_PARTICLES = {
    "da", "pa", "di", "machan", "macha", "aiyo", "aiyoo", "seri",
    "romba", "kandippa", "thambi", "la", "dhan", "nu", "kooda",
    "dei", "dey", "daa", "paa", "dii", "ayyo", "chee", "chi",
}

ENGLISH_STOPWORDS = {
    "the", "and", "is", "in", "it", "to", "of", "for", "with", "on",
    "that", "this", "are", "from", "at", "as", "by", "an", "be", "was",
    "have", "has", "not", "but", "all", "they", "we", "can", "will",
    "one", "you", "your", "would", "should", "could", "do", "does",
    "did", "been", "being", "or", "if", "then", "than", "also",
    "their", "about", "into", "each", "just", "like", "more", "other",
    "some", "what", "when", "which", "who", "how", "its", "may",
}

class EnhancedLanguageIdentifier:
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
        if non_target_ratio > 0.4:
            dominant = max(NON_TARGET_SCRIPTS, key=lambda s: script_ratios.get(s, 0))
            return LangIDResult("OUT_OF_SCOPE", round(non_target_ratio, 4), False,
                                script_ratios, detected_scripts, sublabel=dominant,
                                notes=f"Non-target script dominant: {dominant}")

        tamil_ratio = script_ratios.get("TAMIL", 0.0)
        latin_ratio = script_ratios.get("LATIN", 0.0)

        words = re.findall(r'\b\w+\b', text_nfc.lower(), re.UNICODE)
        total_words = len(words) if words else 1

        # Check hyphenated suffixes (e.g. "server-la", "lazy-aa", "architecture-ல்")
        hyphen_parts = re.findall(r'(\w+)-(\w+)', text_nfc.lower(), re.UNICODE)
        hyphen_tamil_suffixes = sum(1 for _, sfx in hyphen_parts if sfx in {"la", "aa", "le", "ku", "uku", "oda", "kitta", "um", "ai", "dhan"})

        tanglish_lex_hits = sum(1 for w in words if w in ENHANCED_TANGLISH_LEXICON)
        particle_hits = sum(1 for w in words if w in ENHANCED_TAMIL_DISCOURSE_PARTICLES)
        english_stop_hits = sum(1 for w in words if w in ENGLISH_STOPWORDS)

        tamil_suffix_patterns = (
            "nga", "ngu", "odu", "oda", "kitta", "kku", "kaga", "lai",
            "ppu", "ttu", "nnu", "chu", "dhu", "thu", "aam", "aal",
            "la", "le", "aa", "idudhu", "idum", "tom",
        )
        suffix_hits = sum(1 for w in words if len(w) > 4 and any(w.endswith(sfx) for sfx in tamil_suffix_patterns))

        tanglish_evidence = tanglish_lex_hits * 2 + particle_hits * 2 + suffix_hits + hyphen_tamil_suffixes * 2

        # Case 1: Pure or overwhelmingly native Tamil script (>= 85% Tamil, no Latin, or Latin < 5%)
        if tamil_ratio >= 0.85 and latin_ratio < 0.05:
            return LangIDResult("TAMIL", round(tamil_ratio, 4), False,
                                script_ratios, detected_scripts, sublabel="NATIVE_TAMIL")

        # Case 2: Both Tamil and Latin scripts present in meaningful amounts
        # Even 1-2% Tamil script with Latin script is code-mixed Tanglish!
        if tamil_ratio > 0.0 and latin_ratio > 0.0:
            conf = round(min(tamil_ratio + latin_ratio, 1.0), 4)
            if tamil_ratio >= 0.50:
                sub = "TAMIL_WITH_ENGLISH_TECH"
            else:
                sub = "INTRA_SENTENTIAL_CODE_SWITCH"
            return LangIDResult("TANGLISH", conf, True, script_ratios, detected_scripts,
                                sublabel=sub, notes=f"Script mixed: Tamil={tamil_ratio:.2f} Latin={latin_ratio:.2f}")

        # Case 3: Overwhelmingly Tamil script with no Latin
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

            # Suffix hits alone
            if suffix_hits >= 2 or tanglish_word_ratio >= 0.15:
                return LangIDResult("TANGLISH", round(min(0.50 + tanglish_word_ratio, 0.90), 4),
                                    True, script_ratios, detected_scripts, sublabel="ROMANIZED_TAMIL")

            # Standard English
            if english_stop_hits >= 2 or (latin_ratio >= 0.95 and tanglish_evidence == 0):
                return LangIDResult("ENGLISH", round(min(0.55 + english_stop_hits / total_words, 0.98), 4),
                                    False, script_ratios, detected_scripts, sublabel="STANDARD_ENGLISH")

            if tanglish_evidence >= 1:
                return LangIDResult("TANGLISH", 0.50, True, script_ratios, detected_scripts, sublabel="AMBIGUOUS_ROMANIZED")

            return LangIDResult("UNKNOWN", 0.3, False, script_ratios, detected_scripts,
                                notes="Latin script but insufficient English/Tanglish evidence")

        # Case 5: Small non-target contamination
        if non_target_ratio > 0.0 and non_target_ratio <= 0.4:
            return LangIDResult("UNKNOWN", 0.3, True, script_ratios, detected_scripts,
                                notes="Contaminated with non-target script")

        return LangIDResult("UNKNOWN", 0.2, False, script_ratios, detected_scripts,
                            notes="Insufficient classification evidence")


# Test against the 100 fixtures
fixtures = []
with open(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            fixtures.append(json.loads(line))

CAT_MAP = {
    'TAMIL_SCRIPT_ENGLISH_TECH': 'TANGLISH',
    'ROMANIZED_TAMIL_INFORMAL': 'TANGLISH',
    'ENGLISH_TAMIL_COLLOQUIAL': 'TANGLISH',
    'INTRA_SENTENTIAL_CODE_SWITCH': 'TANGLISH',
    'FORMAL_TECHNICAL_TANGLISH': 'TANGLISH',
    'DISCOURSE_PARTICLE_MIX': 'TANGLISH',
}

lid = EnhancedLanguageIdentifier()
y_true = []
y_pred = []
per_cat = defaultdict(lambda: {'total':0,'correct':0,'preds':Counter()})

for fix in fixtures:
    text = fix.get('text','')
    cat = fix.get('category','')
    expected = CAT_MAP.get(cat, 'UNKNOWN')
    r = lid.identify(text)
    pred = r.label
    y_true.append(expected)
    y_pred.append(pred)
    per_cat[cat]['total'] += 1
    per_cat[cat]['preds'][pred] += 1
    if pred == expected:
        per_cat[cat]['correct'] += 1

correct = sum(1 for a,b in zip(y_true,y_pred) if a==b)
acc = correct / len(y_true)
print(f"ENHANCED Overall accuracy: {acc:.2%} ({correct}/{len(y_true)})")
for cat in sorted(per_cat):
    d = per_cat[cat]
    a = d['correct']/d['total']
    print(f"  {cat}: {a:.2%} ({d['correct']}/{d['total']}) -> {dict(d['preds'])}")

# Check pure Tamil and English sanity
pure_tests = [
    ("தமிழ் மிகவும் அழகான மொழி, இது உலகின் மிகப் பழமையான மொழிகளில் ஒன்று.", "TAMIL"),
    ("The quick brown fox jumps over the lazy dog near the river bank.", "ENGLISH"),
    ("Python is an interpreted, high-level, general-purpose programming language.", "ENGLISH"),
    ("சென்னை தமிழ்நாட்டின் தலைநகரம் ஆகும்.", "TAMIL"),
    ("हिंदी भारत की राजभाषा है।", "OUT_OF_SCOPE"),
    ("తెలుగు ప్రాచీన భాష.", "OUT_OF_SCOPE"),
    ("", "UNKNOWN"),
    ("12345 67890", "UNKNOWN"),
]
print("\nSanity tests:")
for t, exp in pure_tests:
    r = lid.identify(t)
    print(f"  [{'PASS' if r.label == exp else 'FAIL'}] expected={exp} got={r.label} conf={r.confidence} text={t[:40]}")
