import csv
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
split_manifest = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"

with open(split_manifest, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Let's get the 196 Tanglish rows
tanglish_rows = [r for r in rows if r["language"] == "TANGLISH"]
tamil_rows = [r for r in rows if r["language"] == "TAMIL"]
english_rows = [r for r in rows if r["language"] == "ENGLISH"]

print(f"Tanglish: {len(tanglish_rows)}, Tamil: {len(tamil_rows)}, English: {len(english_rows)}")

# Let's inspect script content of Tanglish rows
# How many have Tamil script?
# How many are purely Latin?
# How many have both?
tang_script = Counter()
for r in tanglish_rows:
    t = r["preview_text"]
    has_ta = any(0x0B80 <= ord(c) <= 0x0BFF for c in t)
    has_en = any(('a' <= c <= 'z') or ('A' <= c <= 'Z') for c in t)
    if has_ta and has_en:
        tang_script["BOTH_TAMIL_AND_LATIN"] += 1
    elif has_ta:
        tang_script["TAMIL_SCRIPT_ONLY"] += 1
    elif has_en:
        tang_script["LATIN_SCRIPT_ONLY_ROMANIZED"] += 1
    else:
        tang_script["OTHER"] += 1

print("\nTanglish rows script composition:")
for k, v in tang_script.items():
    print(f"  {k}: {v}")

# Now let's inspect the actual full text of all 196 Tanglish records
import check_lang_labels
unique_docs = {d["raw_id"]: d for d in check_lang_labels.unique_docs}
# Map s_rows to full text
full_tanglish = []
for r in tanglish_rows:
    # Find matching doc in unique_docs by sha256 or preview
    # Or let's match by source_file and preview_text
    match = None
    for d in check_lang_labels.unique_docs:
        if d["source_file"] == r["source_file"] and d["text"].startswith(r["preview_text"][:30]):
            match = d
            break
    if match:
        full_tanglish.append(match)

print(f"Full tanglish matches: {len(full_tanglish)}")
full_tang_script = Counter()
for d in full_tanglish:
    t = d["text"]
    has_ta = any(0x0B80 <= ord(c) <= 0x0BFF for c in t)
    has_en = any(('a' <= c <= 'z') or ('A' <= c <= 'Z') for c in t)
    if has_ta and has_en:
        full_tang_script["BOTH_TAMIL_AND_LATIN"] += 1
    elif has_ta:
        full_tang_script["TAMIL_SCRIPT_ONLY"] += 1
    elif has_en:
        full_tang_script["LATIN_SCRIPT_ONLY_ROMANIZED"] += 1
    else:
        full_tang_script["OTHER"] += 1

print("\nFull text Tanglish script composition:")
for k, v in full_tang_script.items():
    print(f"  {k}: {v}")
