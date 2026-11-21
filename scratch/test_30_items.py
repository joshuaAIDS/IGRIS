import csv
import unicodedata
import regex
from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

def get_codepoints(text):
    return " ".join(f"U+{ord(c):04X}" for c in text)

def get_grapheme_clusters(text):
    clusters = regex.findall(r"\X", text)
    return " | ".join(clusters)

# Define 30 items
tamil_items = [
    ("க்", "pulli_and_virama", "TA-AUD-051",
     "Base voiceless velar stop க + virama/pulli (pure consonant k).",
     "Cand A and Exp A segment identically into base byte prefix and virama; pulli remains isolated diacritic."),
    ("கௌ", "uyirmei_combinations", "TA-AUD-061",
     "Diphthongal vowel uyirmei letter கௌ (kau) = base consonant + au-sign.",
     "Canonical vs decomposed representation; Exp A groups base consonant but separates vowel sign; check NFC consistency."),
    ("ஸ்ரீ", "grantha_and_conjuncts", "TA-AUD-071",
     "Grantha auspicious honorific ligature Sri (ஸ + ் + ர + ீ).",
     "Exp A merges ligature elements more compactly than Cand A, but still separates across grapheme components."),
    ("செய்தல்", "roots_and_suffixes", "TA-AUD-002",
     "Root verb செய் (do) + verbal noun suffix -தல் (doing/action).",
     "Exp A merges root prefix and noun suffix -தல் into distinct chunks, reducing fragmentation by 33%."),
    ("வந்தேன்", "tense_and_person", "TA-AUD-011",
     "Past tense verb: root வந் (come-past) + 1st person singular agreement -தேன் (I came).",
     "Exp A segments at morphological junction between verbal stem and person agreement suffix."),
    ("மரங்கள்", "singular_and_plural", "TA-AUD-021",
     "Root மரம் (tree) + plural inflection suffix -கள் (trees).",
     "Exp A preserves clean boundary before plural suffix -கள், avoiding arbitrary character fragmentation."),
    ("பல்கலைக்கழகம்", "compound_words", "TA-AUD-032",
     "Nominal compound: பல (many) + கலை (arts/sciences) + கழகம் (academy/university).",
     "High syllable count; Exp A preserves sub-word stems without cross-stem non-morphemic contamination."),
    ("போறேன்", "spoken_vs_formal", "TA-AUD-041",
     "Spoken colloquial contraction of formal போகிறேன் (I am going).",
     "Exp A forms compact spoken stem tokens; check whether colloquial contractions retain root recognizability."),
    ("வீட்டிற்குள்", "agglutinative_inflections", "TA-AUD-091",
     "Agglutinative postpositional phrase: வீடு (house) + இற்கு (dative/oblique) + உள் (inside).",
     "Exp A reduces token count from 17 to 12; verify inflectional case suffix boundaries."),
    ("நாடுகளிலிருந்து", "agglutinative_inflections", "TA-AUD-100",
     "Agglutinative inflection chain: நாடு (country) + கள் (plural) + இல் (locative) + இருந்து (ablative).",
     "Multi-suffix case stack; Exp A maintains 26% reduction while aligning on natural morpheme chunks.")
]

english_items = [
    ("the", "common_words", "EN-AUD-001",
     "High-frequency English definite article.",
     "Candidate A and Exp A segment identically as 't | he' due to initial vocabulary seed structure."),
    ("microservice", "technical_vocabulary", "EN-AUD-021",
     "Closed compound technical noun: micro + service.",
     "EXP A OVERMERGES into 'm | icroser | vice', creating non-morphemic subword 'icroser' spanning the boundary."),
    ("asynchronous", "programming_terminology", "EN-AUD-031",
     "Computing adjective: a- (negation prefix) + synchronous (simultaneous).",
     "Exp A collapses into 'as | ynchronous', obscuring the 'a-' + 'synchronous' morphological boundary."),
    ("middleware", "programming_terminology", "EN-AUD-037",
     "Technical compound noun: middle + ware.",
     "Exp A fragments into 5 subwords ('m | id | d | le | ware') without forming morpheme 'middle'."),
    ("internationalization", "long_words", "EN-AUD-061",
     "Multi-affix technical noun: inter- + nation + -al + -ize + -ation.",
     "Exp A segments cleanly as 'in | tern | ational | ization', aligning neatly with derivational affixes."),
    ("unavoidable", "prefixes_and_suffixes", "EN-AUD-051",
     "Prefixed/suffixed adjective: un- (prefix) + avoid (root) + -able (suffix).",
     "Exp A segments as 'un | av | o | id | able'; un- and -able are preserved, root 'avoid' is fragmented."),
    ("API", "acronyms_initialisms", "EN-AUD-071",
     "All-caps initialism: Application Programming Interface.",
     "Exp A merges 'PI' into a single token ('A | PI') rather than 3 separate single-letter tokens."),
    ("user_id", "numbers_punctuation", "EN-AUD-085",
     "Snake_case software identifier: user + _ + id.",
     "Exp A isolates underscore delimiter cleanly ('us | er | _ | id'), preventing cross-token leakage."),
    ("parseToken()", "numbers_punctuation", "EN-AUD-086",
     "CamelCase method identifier with parenthesis syntax.",
     "Exp A preserves capital 'Token' and punctuation '(' ')' distinctly ('par | se | Token | ( | )')."),
    ("returns dict[str, Any]", "code_adjacent_text", "EN-AUD-093",
     "Python type signature string with brackets, spaces, and commas.",
     "Exp A forms whitespace-prefixed tokens 'Ġdict' and 'ĠAny' cleanly while isolating delimiters.")
]

tanglish_items = [
    ("server-ல்", "english_with_tamil_suffixes", "TG-AUD-001",
     "Latin technical root 'server' + hyphen + Tamil locative case suffix '-ல்'.",
     "Hyphen serves as script transition anchor; Tamil locative '-ல்' is isolated without corrupting Latin stem."),
    ("complex-ஆ", "english_with_tamil_suffixes", "TG-AUD-002",
     "Latin adjective 'complex' + hyphen + Tamil adverbial clitic '-ஆ'.",
     "Clean separation across Latin stem and Tamil clitic; Exp A reduces total tokens from 9 to 5."),
    ("testing-க்கு", "english_with_tamil_suffixes", "TG-AUD-003",
     "Latin gerund 'testing' + hyphen + Tamil dative suffix '-க்கு'.",
     "Tamil dative suffix '-க்கு' decomposed into base + pulli + base + u-sign; stem 'testing' preserved."),
    ("database-லிருந்து", "english_with_tamil_suffixes", "TG-AUD-004",
     "Latin noun 'database' + hyphen + Tamil ablative suffix '-லிருந்து'.",
     "Multi-morpheme ablative suffix cleanly partitioned from Latin database stem."),
    ("deploy பண்ணினோம்", "intra_sentential_code_switch", "TG-AUD-031",
     "Latin verb 'deploy' + space + Tamil inflected light verb 'பண்ணினோம்' (we deployed).",
     "Whitespace + script change boundary; Exp A merges 'Ġபண' at onset of Tamil verb."),
    ("sprint planning முடிஞ்சிருச்சு", "intra_sentential_code_switch", "TG-AUD-034",
     "English noun phrase 'sprint planning' + colloquial Tamil completive verb 'முடிஞ்சிருச்சு'.",
     "Major multi-word code-switch boundary; both English terms and Tamil verb stems segmented cleanly."),
    ("algorithm romba slow-ஆ இருக்கு", "intra_sentential_code_switch", "TG-AUD-035",
     "Mixed script: English technical + Romanized Tamil adverb + Latin-Tamil hyphenated clitic + Tamil verb.",
     "Multi-script sentence; Exp A merges Romanized 'romba' as single token ('Ġromba')."),
    ("Please check the logs da", "english_with_tamil_discourse_markers", "TG-AUD-061",
     "Standard English imperative sentence + Tamil colloquial discourse marker 'da'.",
     "Discourse marker 'da' isolated as single token 'Ġda'; English words achieve 1-token-per-word efficiency."),
    ("pannirukkom", "spoken_informal_tanglish_verbs", "TG-AUD-076",
     "Romanized Tamil informal verb inflection: pann- (do) + irukk- (perfect) + -om (1st plural).",
     "Romanized Tamil verbal morphology; Exp A segments as 'p | ann | iru | k | k | om'."),
    ("கம்ப்யூட்டர்", "tamil_script_loanwords", "TG-AUD-091",
     "Tamil script phonetic transliteration of English noun 'computer'.",
     "Exp A merges 'கம்' into 'à®ķà®®' and 'டர்' into 'à®Łà®°', reducing token count from 16 to 10.")
]

print("Checking all 30 items...")
all_30 = []
for i, (text, cat, ref_id, interp, concern) in enumerate(tamil_items, 1):
    all_30.append((f"OWN-REV-{i:02d}", "TAMIL", cat, text, ref_id, interp, concern))
for i, (text, cat, ref_id, interp, concern) in enumerate(english_items, 11):
    all_30.append((f"OWN-REV-{i:02d}", "ENGLISH", cat, text, ref_id, interp, concern))
for i, (text, cat, ref_id, interp, concern) in enumerate(tanglish_items, 21):
    all_30.append((f"OWN-REV-{i:02d}", "TANGLISH", cat, text, ref_id, interp, concern))

for r in all_30:
    rev_id, lang, cat, text, ref_id, interp, concern = r
    enc_a = tok_a.encode(text)
    enc_exp = tok_exp.encode(text)
    toks_a = " | ".join(enc_a.tokens)
    toks_exp = " | ".join(enc_exp.tokens)
    print(f"{rev_id} [{lang}] {text} -> A: {len(enc_a.tokens)} toks, Exp: {len(enc_exp.tokens)} toks")
