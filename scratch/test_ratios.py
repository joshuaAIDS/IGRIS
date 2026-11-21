import csv
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
import check_lang_labels

docs = check_lang_labels.unique_docs
# 399 docs
print("Total docs:", len(docs))

# Let's check each doc's script and language
tanglish_docs = [d for d in docs if d["assigned_lang"] == "TANGLISH"]
tamil_docs = [d for d in docs if d["assigned_lang"] == "TAMIL"]
english_docs = [d for d in docs if d["assigned_lang"] == "ENGLISH"]

# In the 196 Tanglish docs:
# Let's compute:
# - tamil_char_ratio
# - latin_char_ratio
for d in tanglish_docs:
    t = d["text"]
    ta_chars = sum(1 for c in t if 0x0B80 <= ord(c) <= 0x0BFF)
    lat_chars = sum(1 for c in t if ('a' <= c <= 'z') or ('A' <= c <= 'Z'))
    total_alpha = ta_chars + lat_chars
    d["ta_chars"] = ta_chars
    d["lat_chars"] = lat_chars
    d["ta_ratio"] = ta_chars / total_alpha if total_alpha else 0.0
    d["lat_ratio"] = lat_chars / total_alpha if total_alpha else 0.0

# Let's sort tanglish docs by ta_ratio descending
by_ta_ratio = sorted(tanglish_docs, key=lambda x: x["ta_ratio"], reverse=True)

print("Top 50 by Tamil ratio in Tanglish docs:")
for i, d in enumerate(by_ta_ratio[:50]):
    print(f"[{i+1:02d}] ta_ratio={d['ta_ratio']:.2f} lat_ratio={d['lat_ratio']:.2f} | {d['source_file']} | {d['raw_id']} | {repr(d['text'][:50])}")

# Notice how many have ta_ratio > some threshold?
for thresh in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]:
    count = sum(1 for d in tanglish_docs if d["ta_ratio"] >= thresh)
    print(f"Tanglish with ta_ratio >= {thresh}: {count}")

# What about Latin ratio?
print("\nTop 50 by Latin ratio in Tanglish docs:")
by_lat_ratio = sorted(tanglish_docs, key=lambda x: x["lat_ratio"], reverse=True)
for i, d in enumerate(by_lat_ratio[:50]):
    print(f"[{i+1:02d}] lat_ratio={d['lat_ratio']:.2f} ta_ratio={d['ta_ratio']:.2f} | {d['source_file']} | {d['raw_id']} | {repr(d['text'][:50])}")

for thresh in [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]:
    count = sum(1 for d in tanglish_docs if d["lat_ratio"] >= thresh)
    print(f"Tanglish with lat_ratio >= {thresh}: {count}")
