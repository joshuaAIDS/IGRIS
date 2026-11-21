import csv
from pathlib import Path
import regex
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"

tok_a = Tokenizer.from_file(str(WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"))
tok_exp = Tokenizer.from_file(str(PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"))

csv_p = WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv"
with open(csv_p, "r", encoding="utf-8") as f:
    records = list(csv.DictReader(f))

print(f"Loaded {len(records)} records from {csv_p.name}")

# Script classification helper
def classify_script(text: str) -> str:
    has_tamil = any("\u0B80" <= c <= "\u0BFF" for c in text)
    has_latin = any(("a" <= c <= "z") or ("A" <= c <= "Z") for c in text)
    if has_tamil and has_latin:
        return "MIXED_SCRIPT"
    elif has_tamil:
        return "TAMIL_SCRIPT"
    elif has_latin:
        return "LATIN_SCRIPT"
    else:
        return "PUNCT_OR_OTHER"

def analyze_graphemes_for_record(text: str, tok: Tokenizer):
    enc = tok.encode(text)
    offsets = enc.offsets # list of (start, end) char offsets
    
    # Internal token boundaries are cut positions strictly inside the string: (0 < cut < len(text))
    # In tokenizers with ByteLevel, tokens map to char offsets.
    # A token boundary occurs between token i and token i+1.
    token_cuts = [end for start, end in offsets[:-1]] # length len(offsets) - 1
    
    # Grapheme clusters via UAX #29 regex \X
    cluster_spans = []
    curr = 0
    for match in regex.finditer(r"\X", text):
        cluster_spans.append((match.start(), match.end(), match.group()))
    
    total_graphemes = len(cluster_spans)
    total_internal_token_boundaries = len(enc.tokens) - 1
    
    # Grapheme boundaries are the end points of each cluster (except the last one)
    grapheme_boundaries = set(end for start, end, g in cluster_spans[:-1])
    
    # Check each token cut: is it inside a grapheme cluster or between grapheme clusters?
    cuts_inside_graphemes = 0
    cuts_between_graphemes = 0
    
    for cut in token_cuts:
        # Check if cut falls strictly inside any grapheme cluster span (start < cut < end)
        inside = False
        for start, end, g in cluster_spans:
            if start < cut < end:
                inside = True
                break
        if inside:
            cuts_inside_graphemes += 1
        else:
            cuts_between_graphemes += 1
            
    return {
        "text": text,
        "total_graphemes": total_graphemes,
        "token_count": len(enc.tokens),
        "total_internal_token_boundaries": total_internal_token_boundaries,
        "cuts_inside_graphemes": cuts_inside_graphemes,
        "cuts_between_graphemes": cuts_between_graphemes,
        "cluster_spans": cluster_spans,
        "token_cuts": token_cuts
    }

# Run across all 300 records
results_a = []
results_exp = []

for r in records:
    text = r["original_text"]
    lang = r["language"]
    script = classify_script(text)
    
    res_a = analyze_graphemes_for_record(text, tok_a)
    res_exp = analyze_graphemes_for_record(text, tok_exp)
    
    res_a["language"] = lang
    res_a["script"] = script
    res_a["example_id"] = r["example_id"]
    
    res_exp["language"] = lang
    res_exp["script"] = script
    res_exp["example_id"] = r["example_id"]
    
    results_a.append(res_a)
    results_exp.append(res_exp)

print("\n--- CANDIDATE A TOTALS ---")
tot_rec = len(results_a)
tot_graph = sum(r["total_graphemes"] for r in results_a)
tot_tok_cuts_a = sum(r["total_internal_token_boundaries"] for r in results_a)
cuts_inside_a = sum(r["cuts_inside_graphemes"] for r in results_a)
cuts_between_a = sum(r["cuts_between_graphemes"] for r in results_a)

print(f"Total Records: {tot_rec}")
print(f"Total Graphemes: {tot_graph}")
print(f"Cand A Total Internal Token Boundaries: {tot_tok_cuts_a}")
print(f"Cand A Cuts INSIDE Grapheme Clusters: {cuts_inside_a}")
print(f"Cand A Cuts BETWEEN Grapheme Clusters: {cuts_between_a}")
print(f"Sum check: {cuts_inside_a + cuts_between_a} == {tot_tok_cuts_a}")

print("\n--- EXP CANDIDATE A TOTALS ---")
tot_tok_cuts_exp = sum(r["total_internal_token_boundaries"] for r in results_exp)
cuts_inside_exp = sum(r["cuts_inside_graphemes"] for r in results_exp)
cuts_between_exp = sum(r["cuts_between_graphemes"] for r in results_exp)

print(f"Exp A Total Internal Token Boundaries: {tot_tok_cuts_exp}")
print(f"Exp A Cuts INSIDE Grapheme Clusters: {cuts_inside_exp}")
print(f"Exp A Cuts BETWEEN Grapheme Clusters: {cuts_between_exp}")
print(f"Sum check: {cuts_inside_exp + cuts_between_exp} == {tot_tok_cuts_exp}")

print("\n--- PREVIOUSLY REPORTED 422 CHECK ---")
print(f"Did previous report say 422? cuts_inside_a={cuts_inside_a}, cuts_inside_exp={cuts_inside_exp}")
