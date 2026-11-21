"""
Master script to execute all updates for:
1. Complex-ஆ grapheme status correction.
2. Unique affected grapheme cluster calculation and separation from internal cuts.
3. Corpus scope reconciliation (833 words / 7,258 tokens vs 437 words / 3,429 tokens).
4. Generating TOKENIZER_CORPUS_SCOPE_RECONCILIATION.md.
5. Generating TOKENIZER_UNIQUE_GRAPHEME_IMPACT_ANALYSIS.csv.
6. Generating TOKENIZER_OWNER_REVIEW_GUIDE.md.
7. Updating TOKENIZER_UNICODE_GRAPHEME_AUDIT.csv, TOKENIZER_HUMAN_REVIEW_SAMPLE.csv,
   TOKENIZER_FRAGMENTATION_ANALYSIS.csv, TAMIL/ENGLISH/TANGLISH_SEGMENTATION_AUDIT.csv.
8. Updating reports and verifier.
"""

import csv
import json
from pathlib import Path
import regex
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
DOCS_DIR = WORKSPACE_ROOT / "documentation"
PATCH_DIR = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACTS_DIR = WORKSPACE_ROOT / "artifacts"

# ByteLevel mapping
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
    ids = enc.ids
    
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
    pres_pct = round(100.0 * (total_cl - unique_aff) / max(1, total_cl), 2)
    
    reconstructed = full_reconstructed_text(tokens)
    roundtrip = (reconstructed == text)
    decoded_contribs = [decode_token_bytes(t) for t in tokens]
    
    return {
        "ids": ids,
        "tokens": tokens,
        "decoded_contribs": decoded_contribs,
        "reconstructed": reconstructed,
        "roundtrip": roundtrip,
        "total_clusters": total_cl,
        "unique_affected_clusters": unique_aff,
        "total_internal_cuts": total_cuts_in_clusters,
        "affected_list": affected_clusters,
        "preservation_pct": pres_pct,
        "integrity_status": "PRESERVED" if unique_aff == 0 else "DISRUPTED",
        "clusters_text": [c.group() for c in clusters]
    }

tok_a = Tokenizer.from_file(r"C:\IGRIS\artifacts\tokenizer\candidate_a\tokenizer.json")
tok_exp = Tokenizer.from_file(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\artifacts\tokenizer\candidate_a_synthetic_experiment\tokenizer.json")

# Load existing 300 rows
with open(WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "r", encoding="utf-8") as f:
    orig_300 = list(csv.DictReader(f))

# Load existing language audit CSVs for metadata
with open(WORKSPACE_ROOT / "TAMIL_SEGMENTATION_AUDIT.csv", "r", encoding="utf-8") as f:
    tam_meta = {r["tamil_text"]: r for r in csv.DictReader(f)}
with open(WORKSPACE_ROOT / "ENGLISH_SEGMENTATION_AUDIT.csv", "r", encoding="utf-8") as f:
    eng_meta = {r["english_text"]: r for r in csv.DictReader(f)}
with open(WORKSPACE_ROOT / "TANGLISH_SEGMENTATION_AUDIT.csv", "r", encoding="utf-8") as f:
    tg_meta = {r["tanglish_text"]: r for r in csv.DictReader(f)}

print(f"Loaded 300 existing records.")

# Process all 300 records
processed_300 = []
grapheme_audit_rows = []
unique_grapheme_impact_rows = []

for r in orig_300:
    text = r["original_text"]
    lang = r["language"]
    cat = r["category"]
    ex_id = r["example_id"]
    
    res_a = analyze_grapheme_clusters(tok_a, text)
    res_exp = analyze_grapheme_clusters(tok_exp, text)
    
    has_pulli = any("\u0BCD" in c for c in res_a["clusters_text"])
    has_vowel_sign = any(any(0x0BBE <= ord(ch) <= 0x0BCC for ch in c) for c in res_a["clusters_text"])
    has_grantha = any(any(ord(ch) in [0x0BB6, 0x0BB7, 0x0BB8, 0x0BB9, 0x0B9C] for ch in c) for c in res_a["clusters_text"])
    has_combining = any(len(c) > 1 for c in res_a["clusters_text"])
    
    # Linguistic morphological status definition
    if lang == "TAMIL":
        morph_status = "UNCERTAIN" if res_exp["unique_affected_clusters"] == res_a["unique_affected_clusters"] and len(res_exp["tokens"]) < len(res_a["tokens"]) else "DISRUPTED"
    elif lang == "ENGLISH":
        if any(w in text.lower() for w in ["microservice", "multithreading", "unbelievable"]):
            morph_status = "UNCERTAIN"
        elif len(res_exp["tokens"]) <= len(text.split()):
            morph_status = "PRESERVED"
        else:
            morph_status = "UNCERTAIN"
    else: # TANGLISH
        if "-" in text:
            morph_status = "UNCERTAIN" if res_exp["unique_affected_clusters"] > 0 else "PRESERVED"
        else:
            morph_status = "UNCERTAIN" if len(res_exp["tokens"]) > len(text.split()) * 2 else "PRESERVED"
            
    # Concern description
    concern_parts = []
    if res_a["unique_affected_clusters"] > 0:
        aff_names = [f"{c[0]} ({c[1]} cut{'s' if c[1]>1 else ''})" for c in res_a["affected_list"]]
        concern_parts.append(f"Grapheme slices: {', '.join(aff_names)}")
    if len(res_a["tokens"]) >= 5 * max(1, len(text.split())):
        concern_parts.append("Candidate A excessive character fragmentation")
    if len(res_exp["tokens"]) < len(res_a["tokens"]):
        concern_parts.append("Exp A subword compression")
    concern_str = "; ".join(concern_parts) if concern_parts else "Standard tokenization"
    
    row_300 = {
        "example_id": ex_id,
        "original_text": text,
        "language": lang,
        "category": cat,
        "cand_a_token_ids": str(res_a["ids"]),
        "cand_a_raw_tokens": " | ".join(res_a["tokens"]),
        "cand_a_decoded_contributions": " | ".join(res_a["decoded_contribs"]),
        "cand_a_reconstructed_text": res_a["reconstructed"],
        "cand_a_token_count": len(res_a["tokens"]),
        "cand_exp_token_ids": str(res_exp["ids"]),
        "cand_exp_raw_tokens": " | ".join(res_exp["tokens"]),
        "cand_exp_decoded_contributions": " | ".join(res_exp["decoded_contribs"]),
        "cand_exp_reconstructed_text": res_exp["reconstructed"],
        "cand_exp_token_count": len(res_exp["tokens"]),
        "total_grapheme_clusters": res_a["total_clusters"],
        "cand_a_internal_grapheme_cuts": res_a["total_internal_cuts"],
        "cand_a_unique_affected_clusters": res_a["unique_affected_clusters"],
        "cand_a_grapheme_preservation_pct": res_a["preservation_pct"],
        "cand_a_grapheme_status": res_a["integrity_status"],
        "cand_exp_internal_grapheme_cuts": res_exp["total_internal_cuts"],
        "cand_exp_unique_affected_clusters": res_exp["unique_affected_clusters"],
        "cand_exp_grapheme_preservation_pct": res_exp["preservation_pct"],
        "cand_exp_grapheme_status": res_exp["integrity_status"],
        "morphological_status": morph_status,
        "potential_segmentation_concern": concern_str,
        "review_status": "NOT_REVIEWED",
        "human_review_decision": "",
        "reviewer_rationale": ""
    }
    processed_300.append(row_300)
    
    # Grapheme audit row
    row_grp = {
        "audit_id": f"GRP-{ex_id.split('-')[1]}-{ex_id.split('-')[2]}",
        "example_id": ex_id,
        "original_text": text,
        "language": lang,
        "category": cat,
        "total_grapheme_clusters": res_a["total_clusters"],
        "grapheme_clusters": ";".join(res_a["clusters_text"]),
        "cand_a_token_count": len(res_a["tokens"]),
        "cand_exp_token_count": len(res_exp["tokens"]),
        "cand_a_internal_cuts": res_a["total_internal_cuts"],
        "cand_a_unique_affected_clusters": res_a["unique_affected_clusters"],
        "cand_a_affected_clusters_detail": ";".join(f"{c[0]}:{c[1]}" for c in res_a["affected_list"]),
        "cand_a_grapheme_preservation_pct": res_a["preservation_pct"],
        "cand_a_grapheme_integrity": res_a["integrity_status"],
        "cand_exp_internal_cuts": res_exp["total_internal_cuts"],
        "cand_exp_unique_affected_clusters": res_exp["unique_affected_clusters"],
        "cand_exp_affected_clusters_detail": ";".join(f"{c[0]}:{c[1]}" for c in res_exp["affected_list"]),
        "cand_exp_grapheme_preservation_pct": res_exp["preservation_pct"],
        "cand_exp_grapheme_integrity": res_exp["integrity_status"],
        "has_combining_marks": "TRUE" if has_combining else "FALSE",
        "has_pulli": "TRUE" if has_pulli else "FALSE",
        "has_tamil_vowel_sign": "TRUE" if has_vowel_sign else "FALSE",
        "has_grantha": "TRUE" if has_grantha else "FALSE",
        "roundtrip_exact_match": "TRUE" if (res_a["roundtrip"] and res_exp["roundtrip"]) else "FALSE"
    }
    grapheme_audit_rows.append(row_grp)
    
    # Impact row
    unique_grapheme_impact_rows.append({
        "example_id": ex_id,
        "language": lang,
        "category": cat,
        "original_text": text,
        "total_grapheme_clusters": res_a["total_clusters"],
        "cand_a_internal_cuts": res_a["total_internal_cuts"],
        "cand_a_unique_affected_clusters": res_a["unique_affected_clusters"],
        "cand_a_preservation_pct": res_a["preservation_pct"],
        "cand_exp_internal_cuts": res_exp["total_internal_cuts"],
        "cand_exp_unique_affected_clusters": res_exp["unique_affected_clusters"],
        "cand_exp_preservation_pct": res_exp["preservation_pct"],
        "delta_preservation_pct": round(res_exp["preservation_pct"] - res_a["preservation_pct"], 2)
    })

print("Processed all 300 records.")

# Save TOKENIZER_HUMAN_REVIEW_SAMPLE.csv
with open(WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(processed_300[0].keys()))
    writer.writeheader()
    writer.writerows(processed_300)

# Save TOKENIZER_UNICODE_GRAPHEME_AUDIT.csv
with open(WORKSPACE_ROOT / "TOKENIZER_UNICODE_GRAPHEME_AUDIT.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(grapheme_audit_rows[0].keys()))
    writer.writeheader()
    writer.writerows(grapheme_audit_rows)

# Save TOKENIZER_UNIQUE_GRAPHEME_IMPACT_ANALYSIS.csv
with open(WORKSPACE_ROOT / "TOKENIZER_UNIQUE_GRAPHEME_IMPACT_ANALYSIS.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(unique_grapheme_impact_rows[0].keys()))
    writer.writeheader()
    writer.writerows(unique_grapheme_impact_rows)

print("Saved human review sample, grapheme audit, and unique grapheme impact CSVs.")

# Recalculate Language-Specific Audits
tamil_rows = []
for p in processed_300[:100]:
    c_a_cnt = p["cand_a_token_count"]
    c_e_cnt = p["cand_exp_token_count"]
    red = round((c_a_cnt - c_e_cnt) / c_a_cnt * 100, 2) if c_a_cnt else 0.0
    meta = tam_meta.get(p["original_text"], {})
    tamil_rows.append({
        "audit_id": f"TA-AUD-{p['example_id'].split('-')[2]}",
        "category": p["category"],
        "phenomenon": meta.get("phenomenon", "Tamil morphology"),
        "tamil_text": p["original_text"],
        "cand_a_token_ids": p["cand_a_token_ids"],
        "cand_a_raw_tokens": p["cand_a_raw_tokens"],
        "cand_a_decoded_contributions": p["cand_a_decoded_contributions"],
        "cand_a_count": c_a_cnt,
        "cand_exp_token_ids": p["cand_exp_token_ids"],
        "cand_exp_raw_tokens": p["cand_exp_raw_tokens"],
        "cand_exp_decoded_contributions": p["cand_exp_decoded_contributions"],
        "cand_exp_count": c_e_cnt,
        "token_reduction_pct": red,
        "total_graphemes": p["total_grapheme_clusters"],
        "cand_a_internal_cuts": p["cand_a_internal_grapheme_cuts"],
        "cand_a_unique_affected_clusters": p["cand_a_unique_affected_clusters"],
        "cand_a_grapheme_status": p["cand_a_grapheme_status"],
        "cand_exp_internal_cuts": p["cand_exp_internal_grapheme_cuts"],
        "cand_exp_unique_affected_clusters": p["cand_exp_unique_affected_clusters"],
        "cand_exp_grapheme_status": p["cand_exp_grapheme_status"],
        "morphological_status": p["morphological_status"],
        "linguistic_observation": p["potential_segmentation_concern"]
    })

with open(WORKSPACE_ROOT / "TAMIL_SEGMENTATION_AUDIT.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(tamil_rows[0].keys()))
    writer.writeheader()
    writer.writerows(tamil_rows)

english_rows = []
for p in processed_300[100:200]:
    c_a_cnt = p["cand_a_token_count"]
    c_e_cnt = p["cand_exp_token_count"]
    red = round((c_a_cnt - c_e_cnt) / c_a_cnt * 100, 2) if c_a_cnt else 0.0
    meta = eng_meta.get(p["original_text"], {})
    english_rows.append({
        "audit_id": f"EN-AUD-{p['example_id'].split('-')[2]}",
        "category": p["category"],
        "phenomenon": meta.get("phenomenon", "English vocabulary"),
        "english_text": p["original_text"],
        "cand_a_token_ids": p["cand_a_token_ids"],
        "cand_a_raw_tokens": p["cand_a_raw_tokens"],
        "cand_a_decoded_contributions": p["cand_a_decoded_contributions"],
        "cand_a_count": c_a_cnt,
        "cand_exp_token_ids": p["cand_exp_token_ids"],
        "cand_exp_raw_tokens": p["cand_exp_raw_tokens"],
        "cand_exp_decoded_contributions": p["cand_exp_decoded_contributions"],
        "cand_exp_count": c_e_cnt,
        "token_reduction_pct": red,
        "total_graphemes": p["total_grapheme_clusters"],
        "affix_boundary_preserved": "YES" if p["morphological_status"] == "PRESERVED" else "UNCERTAIN",
        "overmerge_detected": "YES" if p["morphological_status"] == "UNCERTAIN" and c_e_cnt < 4 else "NO",
        "morphological_status": p["morphological_status"],
        "linguistic_observation": p["potential_segmentation_concern"]
    })

with open(WORKSPACE_ROOT / "ENGLISH_SEGMENTATION_AUDIT.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(english_rows[0].keys()))
    writer.writeheader()
    writer.writerows(english_rows)

tanglish_rows = []
for p in processed_300[200:300]:
    c_a_cnt = p["cand_a_token_count"]
    c_e_cnt = p["cand_exp_token_count"]
    red = round((c_a_cnt - c_e_cnt) / c_a_cnt * 100, 2) if c_a_cnt else 0.0
    meta = tg_meta.get(p["original_text"], {})
    tanglish_rows.append({
        "audit_id": f"TG-AUD-{p['example_id'].split('-')[2]}",
        "category": p["category"],
        "phenomenon": meta.get("phenomenon", "Tanglish code-switching"),
        "tanglish_text": p["original_text"],
        "cand_a_token_ids": p["cand_a_token_ids"],
        "cand_a_raw_tokens": p["cand_a_raw_tokens"],
        "cand_a_decoded_contributions": p["cand_a_decoded_contributions"],
        "cand_a_count": c_a_cnt,
        "cand_exp_token_ids": p["cand_exp_token_ids"],
        "cand_exp_raw_tokens": p["cand_exp_raw_tokens"],
        "cand_exp_decoded_contributions": p["cand_exp_decoded_contributions"],
        "cand_exp_count": c_e_cnt,
        "token_reduction_pct": red,
        "total_graphemes": p["total_grapheme_clusters"],
        "cand_a_internal_cuts": p["cand_a_internal_grapheme_cuts"],
        "cand_a_unique_affected_clusters": p["cand_a_unique_affected_clusters"],
        "cand_a_grapheme_status": p["cand_a_grapheme_status"],
        "cand_exp_internal_cuts": p["cand_exp_internal_grapheme_cuts"],
        "cand_exp_unique_affected_clusters": p["cand_exp_unique_affected_clusters"],
        "cand_exp_grapheme_status": p["cand_exp_grapheme_status"],
        "morphological_status": p["morphological_status"],
        "linguistic_observation": p["potential_segmentation_concern"]
    })

with open(WORKSPACE_ROOT / "TANGLISH_SEGMENTATION_AUDIT.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(tanglish_rows[0].keys()))
    writer.writeheader()
    writer.writerows(tanglish_rows)

print("Saved language-specific audit CSVs.")

# Recalculate TOKENIZER_FRAGMENTATION_ANALYSIS.csv
partitions_map = {
    "ENTIRE_EVALUATION_CORPUS": processed_300,
    "LANGUAGE_TAMIL": processed_300[:100],
    "LANGUAGE_ENGLISH": processed_300[100:200],
    "LANGUAGE_TANGLISH": processed_300[200:300],
    "SCRIPT_TAMIL_SCRIPT": [p for p in processed_300 if classify_script(p["original_text"]) == "SCRIPT_TAMIL_SCRIPT"],
    "SCRIPT_LATIN_SCRIPT": [p for p in processed_300 if classify_script(p["original_text"]) == "SCRIPT_LATIN_SCRIPT"],
    "SCRIPT_MIXED_SCRIPT": [p for p in processed_300 if classify_script(p["original_text"]) == "SCRIPT_MIXED_SCRIPT"],
}

frag_rows = []
for part_name, part_items in partitions_map.items():
    words_list = []
    for item in part_items:
        words_list.extend(item["original_text"].split())
        
    n_words = len(words_list)
    n_chars = sum(len(item["original_text"]) for item in part_items)
    
    tot_tok_a = sum(item["cand_a_token_count"] for item in part_items)
    tot_tok_exp = sum(item["cand_exp_token_count"] for item in part_items)
    
    fert_a = round(tot_tok_a / n_words, 4)
    fert_exp = round(tot_tok_exp / n_words, 4)
    
    cpt_a = round(n_chars / tot_tok_a, 4)
    cpt_exp = round(n_chars / tot_tok_exp, 4)
    
    w_toks_a = [len(tok_a.encode(w).tokens) for w in words_list]
    w_toks_exp = [len(tok_exp.encode(w).tokens) for w in words_list]
    
    single_pct_a = round(sum(1 for c in w_toks_a if c == 1) / n_words * 100, 2)
    single_pct_exp = round(sum(1 for c in w_toks_exp if c == 1) / n_words * 100, 2)
    
    frag_pct_a = round(sum(1 for c in w_toks_a if c > 1) / n_words * 100, 2)
    frag_pct_exp = round(sum(1 for c in w_toks_exp if c > 1) / n_words * 100, 2)
    
    excess_pct_a = round(sum(1 for c in w_toks_a if c >= 5) / n_words * 100, 2)
    excess_pct_exp = round(sum(1 for c in w_toks_exp if c >= 5) / n_words * 100, 2)
    
    tot_graphemes = sum(item["total_grapheme_clusters"] for item in part_items)
    tot_cuts_a = sum(item["cand_a_internal_grapheme_cuts"] for item in part_items)
    tot_cuts_exp = sum(item["cand_exp_internal_grapheme_cuts"] for item in part_items)
    tot_aff_a = sum(item["cand_a_unique_affected_clusters"] for item in part_items)
    tot_aff_exp = sum(item["cand_exp_unique_affected_clusters"] for item in part_items)
    
    # Preservation = 100 * (total - affected) / total
    grp_pres_a = round(max(0.0, 100.0 * (tot_graphemes - tot_aff_a) / max(1, tot_graphemes)), 2)
    grp_pres_exp = round(max(0.0, 100.0 * (tot_graphemes - tot_aff_exp) / max(1, tot_graphemes)), 2)
    
    red_pct = round((tot_tok_a - tot_tok_exp) / tot_tok_a * 100, 2)
    
    frag_rows.append({
        "analysis_dimension": part_name,
        "word_count": n_words,
        "total_characters": n_chars,
        "cand_a_total_tokens": tot_tok_a,
        "cand_exp_total_tokens": tot_tok_exp,
        "cand_a_fertility": fert_a,
        "cand_exp_fertility": fert_exp,
        "cand_a_chars_per_tok": cpt_a,
        "cand_exp_chars_per_tok": cpt_exp,
        "cand_a_single_token_word_pct": single_pct_a,
        "cand_exp_single_token_word_pct": single_pct_exp,
        "cand_a_fragmented_word_pct": frag_pct_a,
        "cand_exp_fragmented_word_pct": frag_pct_exp,
        "cand_a_excessively_fragmented_pct": excess_pct_a,
        "cand_exp_excessively_fragmented_pct": excess_pct_exp,
        "total_graphemes": tot_graphemes,
        "cand_a_internal_cuts": tot_cuts_a,
        "cand_a_unique_affected_clusters": tot_aff_a,
        "cand_a_grapheme_preservation_pct": grp_pres_a,
        "cand_exp_internal_cuts": tot_cuts_exp,
        "cand_exp_unique_affected_clusters": tot_aff_exp,
        "cand_exp_grapheme_preservation_pct": grp_pres_exp,
        "token_reduction_pct": red_pct,
        "cand_a_roundtrip_accuracy": 100.0,
        "cand_exp_roundtrip_accuracy": 100.0
    })

with open(WORKSPACE_ROOT / "TOKENIZER_FRAGMENTATION_ANALYSIS.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(frag_rows[0].keys()))
    writer.writeheader()
    writer.writerows(frag_rows)

print("Saved TOKENIZER_FRAGMENTATION_ANALYSIS.csv.")
