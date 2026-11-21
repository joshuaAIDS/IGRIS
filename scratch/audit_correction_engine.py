import json
import csv
import regex
from pathlib import Path
from tokenizers import Tokenizer

# 1. ByteLevel BPE Mapping
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

# 2. Grapheme Analysis
def analyze_graphemes(tok, text):
    encoding = tok.encode(text)
    offsets = encoding.offsets
    tokens = encoding.tokens
    ids = encoding.ids
    
    # Unicode UAX #29 Grapheme clusters
    clusters = []
    for m in regex.finditer(r"\X", text):
        clusters.append({
            "start": m.start(),
            "end": m.end(),
            "text": m.group(),
            "is_multicode": (m.end() - m.start() > 1)
        })
    
    token_cuts = set(end for start, end in offsets if 0 < end < len(text))
    
    internal_cuts = 0
    cut_clusters = []
    for c in clusters:
        c_cuts = [cut for cut in token_cuts if c["start"] < cut < c["end"]]
        if c_cuts:
            internal_cuts += len(c_cuts)
            cut_clusters.append(c["text"])
            
    # Round-trip verify
    reconstructed = full_reconstructed_text(tokens)
    roundtrip = (reconstructed == text)
    
    # Token decoded contributions
    decoded_contribs = [decode_token_bytes(t) for t in tokens]
    
    return {
        "ids": ids,
        "tokens": tokens,
        "decoded_contribs": decoded_contribs,
        "reconstructed": reconstructed,
        "roundtrip": roundtrip,
        "total_graphemes": len(clusters),
        "multicode_graphemes": sum(1 for c in clusters if c["is_multicode"]),
        "internal_cuts": internal_cuts,
        "cut_clusters": cut_clusters,
        "grapheme_integrity": "PRESERVED" if internal_cuts == 0 else "DISRUPTED",
        "clusters": [c["text"] for c in clusters]
    }

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

print("[*] Loaded tokenizers successfully.")

# Test mandatory examples
mandatory = [
    "server-ல்",
    "complex-ஆ",
    "deploy பண்ணினோம்",
    "memory allocation",
    "pannirukkom",
    "testing-க்கு"
]

print("=== MANDATORY EXAMPLES ===")
for m in mandatory:
    res_a = analyze_graphemes(tok_a, m)
    res_exp = analyze_graphemes(tok_exp, m)
    print(f"\n--- {m} ---")
    print(f"Cand A ({len(res_a['ids'])} tok):")
    print(f"  IDs:     {res_a['ids']}")
    print(f"  Raw:     {' | '.join(res_a['tokens'])}")
    print(f"  Decoded: {' | '.join(res_a['decoded_contribs'])}")
    print(f"  Recon:   {res_a['reconstructed']} (Match: {res_a['roundtrip']})")
    print(f"  Grapheme cuts: {res_a['internal_cuts']} violations: {res_a['cut_clusters']}")
    print(f"Cand Exp ({len(res_exp['ids'])} tok):")
    print(f"  IDs:     {res_exp['ids']}")
    print(f"  Raw:     {' | '.join(res_exp['tokens'])}")
    print(f"  Decoded: {' | '.join(res_exp['decoded_contribs'])}")
    print(f"  Recon:   {res_exp['reconstructed']} (Match: {res_exp['roundtrip']})")
    print(f"  Grapheme cuts: {res_exp['internal_cuts']} violations: {res_exp['cut_clusters']}")
