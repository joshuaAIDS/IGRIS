import json
import csv
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
import check_lang_labels

docs = check_lang_labels.unique_docs
print("Total unique docs:", len(docs))

gt_counts = Counter(d["lang_hint"] for d in docs)
print("Ground truth lang_hint counts:")
for k, v in gt_counts.items():
    print(f"  {k}: {v}")

# What if we inspect each source file's ground truth for the 399 docs?
src_gt = Counter((d["source_file"], d["lang_hint"]) for d in docs)
for k, v in sorted(src_gt.items()):
    print(f"  {k[0]} -> {k[1]}: {v}")
