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

text = "complex-ஆ"
clusters = list(regex.finditer(r"\X", text))

# Byte spans of grapheme clusters
g_byte_spans = []
b_curr = 0
for c in clusters:
    b_len = len(text[c.start():c.end()].encode("utf-8"))
    g_byte_spans.append((b_curr, b_curr + b_len, c.group()))
    b_curr += b_len

print("=== GRAPHEME CLUSTERS ===")
for i, ((cs, ce), (bs, be, g)) in enumerate(zip([(c.start(), c.end()) for c in clusters], g_byte_spans)):
    print(f"G{i}: {g!r:4} | CharSpan=[{cs}..{ce}] | ByteSpan=[{bs:2}..{be:2}]")

for name, tok in [("Original Candidate A", tok_a), ("Experimental Candidate A", tok_exp)]:
    enc = tok.encode(text)
    tok_bytes = [token_to_bytes(t) for t in enc.tokens]
    
    # Cumulative byte offsets
    cum = 0
    spans = []
    for b in tok_bytes:
        spans.append((cum, cum + len(b)))
        cum += len(b)
        
    print(f"\n=== {name} ===")
    print(f"Token count: {len(enc.tokens)}")
    for i, (tid, tstr, (cs, ce), (bs, be), tb) in enumerate(zip(enc.ids, enc.tokens, enc.offsets, spans, tok_bytes)):
        hex_str = tb.hex(" ").upper()
        print(f"  Token {i}: ID={tid:5} | String={tstr!r:8} | Bytes={hex_str:10} | CharSpan=[{cs}..{ce}] | ByteSpan=[{bs:2}..{be:2}]")
        
    print("  Internal Boundaries:")
    for i in range(len(enc.tokens) - 1):
        cut_char = enc.offsets[i][1]
        cut_byte = spans[i][1]
        
        splits_char_g = any(c.start() < cut_char < c.end() for c in clusters)
        splits_byte_g = any(bs < cut_byte < be for bs, be, g in g_byte_spans)
        
        print(f"    Boundary {i} (between T{i} & T{i+1}): CutCharOffset={cut_char}, CutByteOffset={cut_byte:2} | Splits Char Grapheme={splits_char_g} | Splits Byte Grapheme={splits_byte_g}")
