import csv
import regex
from tokenizers import Tokenizer
from test_byte_exact_graphemes import analyze_graphemes_bytes

tok_a = Tokenizer.from_file(r'C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json')
tok_exp = Tokenizer.from_file(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json')

with open(r'C:\IGRIS\TOKENIZER_HUMAN_REVIEW_SAMPLE.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

def is_tamil_char(ch):
    return 0x0B80 <= ord(ch) <= 0x0BFF

def is_latin_char(ch):
    return (0x0041 <= ord(ch) <= 0x005A) or (0x0061 <= ord(ch) <= 0x007A)

def classify_script(text):
    has_tam = any(is_tamil_char(c) for c in text)
    has_lat = any(is_latin_char(c) for c in text)
    if has_tam and has_lat:
        return 'SCRIPT_MIXED_SCRIPT'
    elif has_tam:
        return 'SCRIPT_TAMIL_SCRIPT'
    elif has_lat:
        return 'SCRIPT_LATIN_SCRIPT'
    return 'SCRIPT_OTHER'

partitions = {
    'ENTIRE_EVALUATION_CORPUS': rows,
    'LANGUAGE_TAMIL': [r for r in rows if r['language'] == 'TAMIL'],
    'LANGUAGE_ENGLISH': [r for r in rows if r['language'] == 'ENGLISH'],
    'LANGUAGE_TANGLISH': [r for r in rows if r['language'] == 'TANGLISH'],
    'SCRIPT_TAMIL_SCRIPT': [r for r in rows if classify_script(r['original_text']) == 'SCRIPT_TAMIL_SCRIPT'],
    'SCRIPT_LATIN_SCRIPT': [r for r in rows if classify_script(r['original_text']) == 'SCRIPT_LATIN_SCRIPT'],
    'SCRIPT_MIXED_SCRIPT': [r for r in rows if classify_script(r['original_text']) == 'SCRIPT_MIXED_SCRIPT'],
}

print("=== EXACT BYTE-LEVEL UTF-8 GRAPHEME ANALYSIS ACROSS PARTITIONS ===")
for p_name, p_rows in partitions.items():
    tot_clusters = 0
    tot_cuts_a = 0
    tot_cuts_exp = 0
    tot_aff_a = 0
    tot_aff_exp = 0
    
    for r in p_rows:
        text = r['original_text']
        res_a = analyze_graphemes_bytes(tok_a, text)
        res_exp = analyze_graphemes_bytes(tok_exp, text)
        
        tot_clusters += res_a['total_clusters']
        tot_cuts_a += res_a['total_cuts']
        tot_cuts_exp += res_exp['total_cuts']
        tot_aff_a += res_a['unique_affected']
        tot_aff_exp += res_exp['unique_affected']
        
    pres_a = round(100.0 * (tot_clusters - tot_aff_a) / max(1, tot_clusters), 2)
    pres_exp = round(100.0 * (tot_clusters - tot_aff_exp) / max(1, tot_clusters), 2)
    
    print(f"\n{p_name} (Items: {len(p_rows)}, Clusters: {tot_clusters}):")
    print(f"  Cand A:   Total Cuts={tot_cuts_a}, Unique Affected={tot_aff_a}, Preservation={pres_a:.2f}%")
    print(f"  Cand Exp: Total Cuts={tot_cuts_exp}, Unique Affected={tot_aff_exp}, Preservation={pres_exp:.2f}%")
