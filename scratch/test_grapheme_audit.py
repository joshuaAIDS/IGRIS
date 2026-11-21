import regex
from tokenizers import Tokenizer

def analyze_grapheme_boundaries(tok, text):
    encoding = tok.encode(text)
    offsets = encoding.offsets
    
    # Get character offsets of grapheme clusters using Unicode \X
    cluster_spans = []
    for match in regex.finditer(r"\X", text):
        cluster_spans.append((match.start(), match.end(), match.group()))
    
    internal_token_boundaries = 0
    boundary_violations = []
    
    # Token boundaries are the cut points between tokens
    token_cuts = set(end for start, end in offsets if 0 < end < len(text))
    
    for c_start, c_end, c_text in cluster_spans:
        # A grapheme cluster with combining marks has length > 1
        if c_end - c_start > 1:
            for cut in token_cuts:
                if c_start < cut < c_end:
                    internal_token_boundaries += 1
                    boundary_violations.append((c_text, cut - c_start))
    
    return {
        "total_graphemes": len(cluster_spans),
        "internal_cuts": internal_token_boundaries,
        "violations": boundary_violations,
        "roundtrip_pass": tok.decode(encoding.ids) == text
    }

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

for p in ["server-ல்", "complex-ஆ", "deploy பண்ணினோம்", "memory allocation", "pannirukkom", "testing-க்கு", "தமிழ்நாடு"]:
    ga = analyze_grapheme_boundaries(tok_a, p)
    gexp = analyze_grapheme_boundaries(tok_exp, p)
    print(f"=== {p} ===")
    print(f"  Total graphemes: {ga['total_graphemes']}")
    print(f"  Cand A:   internal cuts = {ga['internal_cuts']}, violations: {ga['violations']}")
    print(f"  Cand Exp: internal cuts = {gexp['internal_cuts']}, violations: {gexp['violations']}")
