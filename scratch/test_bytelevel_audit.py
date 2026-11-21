import csv
import json
import unicodedata
from pathlib import Path
import regex
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"

tok_a = Tokenizer.from_file(str(WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"))
tok_exp = Tokenizer.from_file(str(PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"))

def bytes_to_unicode():
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for b in range(2**8):
        if b not in bs:
            bs.append(b)
            cs.append(2**8 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))

b2u = bytes_to_unicode()
u2b = {v: k for k, v in b2u.items()}

def token_to_bytes(tok: str) -> bytes:
    b_arr = bytearray()
    for ch in tok:
        if ch in u2b:
            b_arr.append(u2b[ch])
        else:
            b_arr.extend(ch.encode("utf-8"))
    return bytes(b_arr)

def is_valid_utf8(b: bytes) -> bool:
    try:
        b.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False

# Test sample Tamil items for ByteLevel audit
tamil_bytelevel_samples = [
    ("க்", "TAMIL", "pure_consonant_velar_stop", "Single voiceless stop with virama"),
    ("கௌ", "TAMIL", "uyirmei_au_diphthong", "Base consonant + diphthongal au-vowel sign"),
    ("தமிழ்", "TAMIL", "language_noun", "Three-syllable proper noun"),
    ("செய்தல்", "TAMIL", "root_and_verbal_noun_suffix", "Root செய் + nominalizing suffix தல்"),
    ("வந்தேன்", "TAMIL", "past_finite_verb", "Past stem வந் + 1st person singular agreement தேன்"),
    ("மரங்கள்", "TAMIL", "nominal_plural", "Stem மரம் with sandhi mutation + plural suffix கள்"),
    ("ஸ்ரீ", "TAMIL", "grantha_honorific_ligature", "Grantha conjunct sa + virama + ra + long i"),
    ("பல்கலைக்கழகம்", "TAMIL", "nominal_compound", "Compound: பல + கலை + கழகம்"),
    ("வீட்டிற்குள்", "TAMIL", "agglutinative_postposition", "Stem வீடு + oblique/dative இற்கு + locative உள்"),
    ("நாடுகளிலிருந்து", "TAMIL", "agglutinative_case_stack", "Stem நாடு + plural கள் + locative இல் + ablative இருந்து"),
    ("server-ல்", "TANGLISH", "latin_root_tamil_locative", "Latin technical stem + hyphen + Tamil locative suffix"),
    ("testing-க்கு", "TANGLISH", "latin_root_tamil_dative", "Latin gerund stem + hyphen + Tamil dative suffix")
]

print("Verifying ByteLevel Mapping extraction...")
for text, lang, cat, note in tamil_bytelevel_samples:
    raw_b = text.encode("utf-8")
    enc_a = tok_a.encode(text)
    enc_exp = tok_exp.encode(text)
    
    bytes_a = [token_to_bytes(t) for t in enc_a.tokens]
    bytes_exp = [token_to_bytes(t) for t in enc_exp.tokens]
    
    rec_a_b = b"".join(bytes_a)
    rec_exp_b = b"".join(bytes_exp)
    
    match_a = (rec_a_b == raw_b)
    match_exp = (rec_exp_b == raw_b)
    
    valid_toks_a = all(is_valid_utf8(b) for b in bytes_a)
    valid_toks_exp = all(is_valid_utf8(b) for b in bytes_exp)
    
    print(f"{text}: RawLen={len(raw_b)} | Cand A: cnt={len(enc_a.ids)}, all_valid_utf8={valid_toks_a}, match={match_a} | Exp A: cnt={len(enc_exp.ids)}, all_valid_utf8={valid_toks_exp}, match={match_exp}")
