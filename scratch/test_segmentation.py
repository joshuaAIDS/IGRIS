from pathlib import Path
from tokenizers import Tokenizer

cand_a = Path(r'C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json')
exp_a = Path(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json')

tok_a = Tokenizer.from_file(str(cand_a))
tok_exp = Tokenizer.from_file(str(exp_a))

test_cases = [
    'தமிழ்',
    'செய்தல்',
    'வந்தேன்',
    'மரங்கள்',
    'பல்கலைக்கழகம்',
    'போறேன்',
    'க்',
    'கௌ',
    'ஸ்ரீ',
    'வீட்டிற்குள்',
    'explain',
    'microservice',
    'asynchronous',
    'middleware',
    'internationalization',
    'API',
    'server-ல்',
    'complex-ஆ',
    'deploy பண்ணினோம்',
    'memory allocation',
    'pannirukkom',
    'testing-க்கு'
]

print(f"{'TEXT':25s} | {'CANDIDATE A (COUNT)':45s} | {'EXP A (COUNT)':45s}")
print('-' * 125)
for t in test_cases:
    enc_a = tok_a.encode(t)
    enc_exp = tok_exp.encode(t)
    toks_a = f"{' | '.join(enc_a.tokens)} ({len(enc_a.tokens)})"
    toks_exp = f"{' | '.join(enc_exp.tokens)} ({len(enc_exp.tokens)})"
    print(f"{t:25s} | {toks_a:45s} | {toks_exp:45s}")
