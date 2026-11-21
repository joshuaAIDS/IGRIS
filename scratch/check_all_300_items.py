import csv
import regex
from pathlib import Path
from tokenizers import Tokenizer

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

byte_to_char_map = bytes_to_unicode()
char_to_byte_map = {v: k for k, v in byte_to_char_map.items()}

def raw_token_to_bytes(tok_str: str) -> bytes:
    b_arr = bytearray()
    for ch in tok_str:
        if ch in char_to_byte_map:
            b_arr.append(char_to_byte_map[ch])
        else:
            b_arr.extend(ch.encode("utf-8"))
    return bytes(b_arr)

def decode_token_bytes(tok_str: str) -> str:
    raw_b = raw_token_to_bytes(tok_str)
    try:
        return raw_b.decode("utf-8")
    except UnicodeDecodeError:
        return "".join(f"<0x{b:02X}>" for b in raw_b)

def full_reconstructed_text(raw_tokens: list[str]) -> str:
    all_bytes = b"".join(raw_token_to_bytes(t) for t in raw_tokens)
    return all_bytes.decode("utf-8", errors="replace")

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

# Read the 300 items from TOKENIZER_HUMAN_REVIEW_SAMPLE.csv
with open(r"C:\IGRIS\TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows read: {len(rows)}")

# Check roundtrip accuracy and grapheme integrity across all 300
roundtrip_failures_a = 0
roundtrip_failures_exp = 0
total_graphemes_all = 0
total_internal_cuts_a = 0
total_internal_cuts_exp = 0

for r in rows:
    text = r["original_text"]
    
    enc_a = tok_a.encode(text)
    enc_exp = tok_exp.encode(text)
    
    recon_a = full_reconstructed_text(enc_a.tokens)
    recon_exp = full_reconstructed_text(enc_exp.tokens)
    
    if recon_a != text:
        roundtrip_failures_a += 1
    if recon_exp != text:
        roundtrip_failures_exp += 1
        
    # Graphemes
    clusters = list(regex.finditer(r"\X", text))
    total_graphemes_all += len(clusters)
    
    cuts_a = set(end for start, end in enc_a.offsets if 0 < end < len(text))
    cuts_exp = set(end for start, end in enc_exp.offsets if 0 < end < len(text))
    
    for c in clusters:
        c_cuts_a = [cut for cut in cuts_a if c.start() < cut < c.end()]
        c_cuts_exp = [cut for cut in cuts_exp if c.start() < cut < c.end()]
        total_internal_cuts_a += len(c_cuts_a)
        total_internal_cuts_exp += len(c_cuts_exp)

print(f"Cand A Roundtrip Failures: {roundtrip_failures_a} / {len(rows)}")
print(f"Cand Exp Roundtrip Failures: {roundtrip_failures_exp} / {len(rows)}")
print(f"Total Graphemes: {total_graphemes_all}")
print(f"Cand A Total Internal Cuts: {total_internal_cuts_a}")
print(f"Cand Exp Total Internal Cuts: {total_internal_cuts_exp}")
