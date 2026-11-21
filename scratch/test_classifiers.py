import csv
import sys
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

from language_identifier import LanguageIdentifier
from language_identifier_v2 import LanguageIdentifierV2

import check_lang_labels
unique_docs = check_lang_labels.unique_docs

lid_v1 = LanguageIdentifier()
lid_v2 = LanguageIdentifierV2()

v1_counts = Counter()
v2_counts = Counter()

for d in unique_docs:
    t = d["text"]
    res1 = lid_v1.identify_language(t)
    v1_counts[res1.primary_language] += 1
    
    res2 = lid_v2.identify(t)
    v2_counts[res2.label] += 1

print(f"V1 primary_language counts: {v1_counts}")
print(f"V2 label counts: {v2_counts}")
