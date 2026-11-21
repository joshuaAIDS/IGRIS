import regex
from tokenizers import Tokenizer

def bytes_to_unicode():
    bs = list(range(ord('!'), ord('~') + 1)) + list(range(ord('¡'), ord('¬') + 1)) + list(range(ord('®'), ord('ÿ') + 1))
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
            b_arr.extend(ch.encode('utf-8'))
    return bytes(b_arr)

def analyze_graphemes_bytes(tok, text):
    text_bytes = text.encode('utf-8')
    enc = tok.encode(text)
    
    # Calculate byte cut positions from tokens
    token_bytes = [raw_token_to_bytes(t) for t in enc.tokens]
    assert b''.join(token_bytes) == text_bytes, 'Concatenated token bytes must equal text bytes'
    
    byte_cuts = []
    curr = 0
    for tb in token_bytes[:-1]:
        curr += len(tb)
        byte_cuts.append(curr)
    byte_cuts_set = set(byte_cuts)
    
    # Find grapheme clusters and their byte ranges
    clusters = list(regex.finditer(r'\X', text))
    affected_clusters = []
    total_cuts = 0
    
    for c in clusters:
        c_text = c.group()
        b_start = len(text[:c.start()].encode('utf-8'))
        b_end = len(text[:c.end()].encode('utf-8'))
        
        # Check cuts strictly inside [b_start, b_end]
        c_cuts = [cut for cut in byte_cuts_set if b_start < cut < b_end]
        if c_cuts:
            affected_clusters.append((c_text, len(c_cuts), c_cuts))
            total_cuts += len(c_cuts)
            
    total_clusters = len(clusters)
    unique_affected = len(affected_clusters)
    pres_pct = round(100.0 * (total_clusters - unique_affected) / max(1, total_clusters), 2)
    
    return {
        'total_clusters': total_clusters,
        'unique_affected': unique_affected,
        'total_cuts': total_cuts,
        'affected': affected_clusters,
        'pres_pct': pres_pct
    }

tok_a = Tokenizer.from_file(r'C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json')
tok_exp = Tokenizer.from_file(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json')

for s in ['server-ல்', 'complex-ஆ', 'deploy பண்ணினோம்', 'memory allocation', 'pannirukkom', 'testing-க்கு']:
    res_a = analyze_graphemes_bytes(tok_a, s)
    res_exp = analyze_graphemes_bytes(tok_exp, s)
    print(f"=== {s} ===")
    aff_a = [(x[0], x[1]) for x in res_a['affected']]
    aff_exp = [(x[0], x[1]) for x in res_exp['affected']]
    print(f"  Cand A:   total={res_a['total_clusters']}, affected={res_a['unique_affected']}, cuts={res_a['total_cuts']}, pres={res_a['pres_pct']}%, affected={aff_a}")
    print(f"  Cand Exp: total={res_exp['total_clusters']}, affected={res_exp['unique_affected']}, cuts={res_exp['total_cuts']}, pres={res_exp['pres_pct']}%, affected={aff_exp}")
