import unicodedata
from tokenizers import Tokenizer
import regex

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

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
    cs = [chr(n) for n in cs]
    return dict(zip(bs, cs))

byte_to_char = bytes_to_unicode()
char_to_byte = {v: k for k, v in byte_to_char.items()}

def token_to_bytes(tok: str) -> bytes:
    b_arr = bytearray()
    for ch in tok:
        if ch in char_to_byte:
            b_arr.append(char_to_byte[ch])
        else:
            b_arr.extend(ch.encode("utf-8"))
    return bytes(b_arr)

def decode_token_safely(tok: str) -> str:
    raw_b = token_to_bytes(tok)
    try:
        return raw_b.decode("utf-8")
    except UnicodeDecodeError:
        return "".join(f"<0x{b:02X}>" for b in raw_b)

samples = [
    "க்",
    "கௌ",
    "ஸ்ரீ",
    "செய்தல்",
    "வந்தேன்",
    "மரங்கள்",
    "server-ல்",
    "complex-ஆ",
    "testing-க்கு",
    "database-லிருந்து",
    "deploy பண்ணினோம்",
    "the",
    "microservice",
    "asynchronous"
]

print("=== UNICODE NORMALIZATION INVESTIGATION ===")
for s in samples[:6]:
    nfc = unicodedata.normalize("NFC", s)
    nfd = unicodedata.normalize("NFD", s)
    print(f"Sample: {s}")
    print(f"  NFC codepoints: {[f'U+{ord(c):04X}' for c in nfc]}")
    print(f"  NFD codepoints: {[f'U+{ord(c):04X}' for c in nfd]}")
    print(f"  NFC == NFD: {nfc == nfd}")

print("\n=== BYTE MAPPING FORENSICS FOR à®¤, à¯į, Ġ ===")
for test_token in ["à®¤", "à¯į", "Ġ", "à®", "¤", "à¯", "į", "Ġà®ªà®£"]:
    raw_b = token_to_bytes(test_token)
    hex_str = " ".join(f"0x{b:02X}" for b in raw_b)
    dec_val = decode_token_safely(test_token)
    print(f"Token string: {test_token!r:12} -> Raw bytes: {hex_str:20} -> Decoded: {dec_val!r}")

print("\n=== ROUND-TRIP FIDELITY AUDIT ===")
all_pass = True
for s in samples:
    enc_a = tok_a.encode(s)
    dec_a = tok_a.decode(enc_a.ids)
    enc_exp = tok_exp.encode(s)
    dec_exp = tok_exp.decode(enc_exp.ids)
    pass_a = (dec_a == s)
    pass_exp = (dec_exp == s)
    if not (pass_a and pass_exp):
        all_pass = False
        print(f"FAILED on {s}: dec_a={dec_a!r}, dec_exp={dec_exp!r}")
print(f"Round-trip 100.0% match: {all_pass}")
