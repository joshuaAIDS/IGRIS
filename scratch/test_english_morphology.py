from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

test_words = [
    ("microservice", ["micro", "service"]),
    ("microservices", ["micro", "services"]),
    ("service", ["service"]),
    ("asynchronous", ["a", "synchronous"]),
    ("synchronous", ["synchronous"]),
    ("middleware", ["middle", "ware"]),
    ("middle", ["middle"]),
    ("ware", ["ware"]),
    ("internationalization", ["inter", "nation", "al", "iz", "ation"]),
    ("international", ["inter", "nation", "al"]),
    ("unavoidable", ["un", "avoid", "able"]),
    ("avoidable", ["avoid", "able"]),
    ("avoid", ["avoid"])
]

print("=== ENGLISH MORPHOLOGICAL MERGE AUDIT ===")
for word, morphemes in test_words:
    enc_a = tok_a.encode(word)
    enc_exp = tok_exp.encode(word)
    print(f"\nWord: {word!r}")
    print(f"  Morphemes: {' + '.join(morphemes)}")
    print(f"  Cand A tokens: {enc_a.tokens} (count: {len(enc_a.tokens)})")
    print(f"  Exp A  tokens: {enc_exp.tokens} (count: {len(enc_exp.tokens)})")
