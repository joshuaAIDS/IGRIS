import csv
from collections import defaultdict
from pathlib import Path
import regex
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"

tok_a = Tokenizer.from_file(str(WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"))
tok_exp = Tokenizer.from_file(str(PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a_synthetic_experiment" / "tokenizer.json"))

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

def classify_script(text: str) -> str:
    has_tam = any("\u0B80" <= c <= "\u0BFF" for c in text)
    has_lat = any(("a" <= c <= "z") or ("A" <= c <= "Z") for c in text)
    if has_tam and has_lat:
        return "MIXED_SCRIPT"
    elif has_tam:
        return "TAMIL_SCRIPT"
    elif has_lat:
        return "LATIN_SCRIPT"
    else:
        return "PUNCT_OR_OTHER"

with open(WORKSPACE_ROOT / "TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "r", encoding="utf-8") as f:
    records = list(csv.DictReader(f))

print(f"Total records: {len(records)}")

stats_a = defaultdict(lambda: {"records": 0, "graphemes": 0, "internal_cuts": 0, "cuts_inside": 0, "cuts_between": 0, "byte_cuts_inside": 0})
stats_exp = defaultdict(lambda: {"records": 0, "graphemes": 0, "internal_cuts": 0, "cuts_inside": 0, "cuts_between": 0, "byte_cuts_inside": 0})

def compute_record(text, tok):
    enc = tok.encode(text)
    clusters = list(regex.finditer(r"\X", text))
    
    # Char spans of graphemes
    g_char_spans = [(c.start(), c.end(), c.group()) for c in clusters]
    
    # Byte spans of graphemes
    g_byte_spans = []
    b_curr = 0
    for c in clusters:
        b_len = len(text[c.start():c.end()].encode("utf-8"))
        g_byte_spans.append((b_curr, b_curr + b_len, c.group()))
        b_curr += b_len
        
    tok_bytes = [token_to_bytes(t) for t in enc.tokens]
    
    # Token byte spans
    t_byte_spans = []
    cum = 0
    for b in tok_bytes:
        t_byte_spans.append((cum, cum + len(b)))
        cum += len(b)
        
    total_graphemes = len(clusters)
    total_internal_cuts = len(enc.tokens) - 1
    
    # Character cuts inside graphemes
    cuts_inside_char = 0
    for i in range(total_internal_cuts):
        cut_char = enc.offsets[i][1]
        if any(cs < cut_char < ce for cs, ce, g in g_char_spans):
            cuts_inside_char += 1
            
    # Byte cuts inside graphemes
    cuts_inside_byte = 0
    for i in range(total_internal_cuts):
        cut_byte = t_byte_spans[i][1]
        if any(bs < cut_byte < be for bs, be, g in g_byte_spans):
            cuts_inside_byte += 1
            
    cuts_between_char = total_internal_cuts - cuts_inside_char
    
    return {
        "graphemes": total_graphemes,
        "internal_cuts": total_internal_cuts,
        "cuts_inside": cuts_inside_char,
        "cuts_between": cuts_between_char,
        "byte_cuts_inside": cuts_inside_byte
    }

for r in records:
    text = r["original_text"]
    lang = r["language"]
    script = classify_script(text)
    
    res_a = compute_record(text, tok_a)
    res_exp = compute_record(text, tok_exp)
    
    for group in ["TOTAL", f"LANG_{lang}", f"SCRIPT_{script}"]:
        for k in ["records"]:
            stats_a[group][k] += 1
            stats_exp[group][k] += 1
        for k in ["graphemes", "internal_cuts", "cuts_inside", "cuts_between", "byte_cuts_inside"]:
            stats_a[group][k] += res_a[k]
            stats_exp[group][k] += res_exp[k]

print("\n=== AGGREGATE SUMMARY TABLE ===")
headers = ["Dimension", "Records", "Graphemes", "CandA_TotCuts", "CandA_Inside", "CandA_Between", "CandA_ByteInside", "Exp_TotCuts", "Exp_Inside", "Exp_Between", "Exp_ByteInside"]
row_format = "{:<22} {:>7} {:>9} {:>13} {:>12} {:>13} {:>16} {:>11} {:>10} {:>11} {:>14}"
print(row_format.format(*headers))
print("-" * 145)

for dim in ["TOTAL", "LANG_TAMIL", "LANG_ENGLISH", "LANG_TANGLISH", "SCRIPT_TAMIL_SCRIPT", "SCRIPT_LATIN_SCRIPT", "SCRIPT_MIXED_SCRIPT"]:
    sa = stats_a[dim]
    se = stats_exp[dim]
    print(row_format.format(
        dim,
        sa["records"],
        sa["graphemes"],
        sa["internal_cuts"],
        sa["cuts_inside"],
        sa["cuts_between"],
        sa["byte_cuts_inside"],
        se["internal_cuts"],
        se["cuts_inside"],
        se["cuts_between"],
        se["byte_cuts_inside"]
    ))
