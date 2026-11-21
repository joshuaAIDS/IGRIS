import csv
import regex
from tokenizers import Tokenizer

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

def is_tamil_char(ch):
    return 0x0B80 <= ord(ch) <= 0x0BFF

def is_latin_char(ch):
    return (0x0041 <= ord(ch) <= 0x005A) or (0x0061 <= ord(ch) <= 0x007A)

def classify_script(text):
    has_tam = any(is_tamil_char(c) for c in text)
    has_lat = any(is_latin_char(c) for c in text)
    if has_tam and has_lat:
        return "SCRIPT_MIXED_SCRIPT"
    elif has_tam:
        return "SCRIPT_TAMIL_SCRIPT"
    elif has_lat:
        return "SCRIPT_LATIN_SCRIPT"
    return "SCRIPT_OTHER"

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

with open(r"C:\IGRIS\TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

partitions = {
    "ENTIRE_EVALUATION_CORPUS": rows,
    "LANGUAGE_TAMIL": [r for r in rows if r["language"] == "TAMIL"],
    "LANGUAGE_ENGLISH": [r for r in rows if r["language"] == "ENGLISH"],
    "LANGUAGE_TANGLISH": [r for r in rows if r["language"] == "TANGLISH"],
    "SCRIPT_TAMIL_SCRIPT": [r for r in rows if classify_script(r["original_text"]) == "SCRIPT_TAMIL_SCRIPT"],
    "SCRIPT_LATIN_SCRIPT": [r for r in rows if classify_script(r["original_text"]) == "SCRIPT_LATIN_SCRIPT"],
    "SCRIPT_MIXED_SCRIPT": [r for r in rows if classify_script(r["original_text"]) == "SCRIPT_MIXED_SCRIPT"],
}

print("=== PARTITION ANALYSIS (UNIQUE AFFECTED CLUSTERS VS CUTS) ===")
for p_name, p_rows in partitions.items():
    tot_clusters = 0
    tot_cuts_a = 0
    tot_cuts_exp = 0
    tot_affected_a = 0
    tot_affected_exp = 0
    
    for r in p_rows:
        text = r["original_text"]
        res_a = analyze_grapheme_clusters(tok_a, text)
        res_exp = analyze_grapheme_clusters(tok_exp, text)
        
        tot_clusters += res_a["total_clusters"]
        tot_cuts_a += res_a["total_internal_cuts"]
        tot_cuts_exp += res_exp["total_internal_cuts"]
        tot_affected_a += res_a["unique_affected_clusters"]
        tot_affected_exp += res_exp["unique_affected_clusters"]
        
    pres_a = 100.0 * (tot_clusters - tot_affected_a) / max(1, tot_clusters)
    pres_exp = 100.0 * (tot_clusters - tot_affected_exp) / max(1, tot_clusters)
    
    print(f"\n{p_name} (Items: {len(p_rows)}, Clusters: {tot_clusters}):")
    print(f"  Cand A:   Unique Affected={tot_affected_a}, Total Cuts={tot_cuts_a}, Preservation={pres_a:.2f}%")
    print(f"  Cand Exp: Unique Affected={tot_affected_exp}, Total Cuts={tot_cuts_exp}, Preservation={pres_exp:.2f}%")
