import sys, re
sys.path.insert(0, r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\scripts')
from language_identifier_v2 import LanguageIdentifierV2, TANGLISH_LEXICON, TAMIL_DISCOURSE_PARTICLES, ENGLISH_STOPWORDS

lid = LanguageIdentifierV2()
text = 'Network transport layers establish reliable end-to-end connections using transmission control protocols.'
words = re.findall(r'\b\w+\b', text.lower(), re.UNICODE)
print('words:', words)

tamil_suffix_patterns = (
    'nga', 'ngu', 'odu', 'oda', 'kitta', 'kku', 'kaga', 'lai',
    'ppu', 'ttu', 'nnu', 'chu', 'dhu', 'thu', 'aam', 'aal',
    'la', 'le', 'aa', 'idudhu', 'idum', 'tom',
)
for w in words:
    matches = [sfx for sfx in tamil_suffix_patterns if len(w) > 4 and w.endswith(sfx)]
    if matches:
        print(f'word "{w}" matched suffix: {matches}')

print('tanglish_lex_hits:', [w for w in words if w in TANGLISH_LEXICON])
print('particle_hits:', [w for w in words if w in TAMIL_DISCOURSE_PARTICLES])
print('english_stop_hits:', [w for w in words if w in ENGLISH_STOPWORDS])

res = lid.identify(text)
print('Result label:', res.label, 'sublabel:', res.sublabel, 'notes:', res.notes)
