import unicodedata
from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

test_samples = [
    "க்",
    "கௌ",
    "ஸ்ரீ",
    "செய்தல்",
    "வந்தேன்",
    "மரங்கள்",
    "பல்கலைக்கழகம்",
    "café",
    "naïve",
    "server-ல்",
    "complex-ஆ",
    "testing-க்கு"
]

print("=== NFC vs NFD AUDIT ===")
for s in test_samples:
    nfc = unicodedata.normalize("NFC", s)
    nfd = unicodedata.normalize("NFD", s)
    diff = (nfc != nfd)
    
    enc_a_nfc = tok_a.encode(nfc)
    enc_a_nfd = tok_a.encode(nfd)
    enc_exp_nfc = tok_exp.encode(nfc)
    enc_exp_nfd = tok_exp.encode(nfd)
    
    dec_a_nfc = tok_a.decode(enc_a_nfc.ids)
    dec_a_nfd = tok_a.decode(enc_a_nfd.ids)
    dec_exp_nfc = tok_exp.decode(enc_exp_nfc.ids)
    dec_exp_nfd = tok_exp.decode(enc_exp_nfd.ids)
    
    nfc_cps = " ".join(f"U+{ord(c):04X}" for c in nfc)
    nfd_cps = " ".join(f"U+{ord(c):04X}" for c in nfd)
    
    print(f"\nSample: {s} | Diff: {diff}")
    print(f"  NFC Codepoints: {nfc_cps}")
    print(f"  NFD Codepoints: {nfd_cps}")
    print(f"  Cand A: NFC count={len(enc_a_nfc.ids)}, NFD count={len(enc_a_nfd.ids)} | tokens NFC={enc_a_nfc.tokens} vs NFD={enc_a_nfd.tokens}")
    print(f"  Exp A : NFC count={len(enc_exp_nfc.ids)}, NFD count={len(enc_exp_nfd.ids)} | tokens NFC={enc_exp_nfc.tokens} vs NFD={enc_exp_nfd.tokens}")
    print(f"  Cand A exact reconstruction: NFC={dec_a_nfc == nfc}, NFD={dec_a_nfd == nfd}")
    print(f"  Exp A  exact reconstruction: NFC={dec_exp_nfc == nfc}, NFD={dec_exp_nfd == nfd}")
