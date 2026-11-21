import regex
from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

def analyze_grapheme_clusters(tok, text):
    clusters = list(regex.finditer(r"\X", text))
    enc = tok.encode(text)
    offsets = enc.offsets
    tokens = enc.tokens
    
    affected_clusters = []
    total_cuts_in_clusters = 0
    
    for c in clusters:
        c_s, c_e = c.start(), c.end()
        num_cuts = 0
        
        # 1. Character-level cuts strictly inside the cluster span (c_s < cut < c_e)
        char_cuts = set(end for start, end in offsets if c_s < end < c_e)
        num_cuts += len(char_cuts)
        
        # 2. Byte-level cuts: if multiple tokens fall within the same character span
        # e.g. for a single-character cluster like 'ஆ', both tokens have offset (c_s, c_e)
        tokens_in_cluster = [i for i, (t_s, t_e) in enumerate(offsets) if t_s >= c_s and t_e <= c_e and t_s < t_e]
        if len(tokens_in_cluster) > 1 and len(char_cuts) == 0:
            num_cuts += (len(tokens_in_cluster) - 1)
            
        if num_cuts > 0:
            affected_clusters.append((c.group(), num_cuts))
            total_cuts_in_clusters += num_cuts
            
    total_cl = len(clusters)
    unique_aff = len(affected_clusters)
    pres_pct = 100.0 * (total_cl - unique_aff) / max(1, total_cl)
    
    return {
        "total_clusters": total_cl,
        "unique_affected_clusters": unique_aff,
        "total_internal_cuts": total_cuts_in_clusters,
        "affected_list": affected_clusters,
        "preservation_pct": pres_pct,
        "integrity_status": "PRESERVED" if unique_aff == 0 else "DISRUPTED"
    }

samples = [
    "server-ல்",
    "complex-ஆ",
    "deploy பண்ணினோம்",
    "memory allocation",
    "pannirukkom",
    "testing-க்கு"
]

print("=== 6 MANDATORY EXPRESSIONS ===")
for s in samples:
    res_a = analyze_grapheme_clusters(tok_a, s)
    res_exp = analyze_grapheme_clusters(tok_exp, s)
    print(f"\n--- {s} ---")
    print(f"Cand A:   status={res_a['integrity_status']} | total={res_a['total_clusters']} | affected={res_a['unique_affected_clusters']} | cuts={res_a['total_internal_cuts']} | pres={res_a['preservation_pct']:.2f}% | details={res_a['affected_list']}")
    print(f"Cand Exp: status={res_exp['integrity_status']} | total={res_exp['total_clusters']} | affected={res_exp['unique_affected_clusters']} | cuts={res_exp['total_internal_cuts']} | pres={res_exp['preservation_pct']:.2f}% | details={res_exp['affected_list']}")
