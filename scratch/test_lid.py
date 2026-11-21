import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))
from language_identifier_v2 import LanguageIdentifierV2

split_manifest = PATCH_ROOT / "CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv"
prov_audit = PATCH_ROOT / "CANDIDATE_A_PROVENANCE_AUDIT.csv"

with open(split_manifest, encoding="utf-8") as f:
    split_rows = list(csv.DictReader(f))

with open(prov_audit, encoding="utf-8") as f:
    prov_rows = list(csv.DictReader(f))

lid = LanguageIdentifierV2()

# Reconstruct all 399 texts from raw sources using doc_id -> raw source mapping
# Let's see how build_corpus_accounting_audit.py reconstructed them
# Let's run build_corpus_accounting_audit.py logic to get accepted_docs
from build_corpus_accounting_audit import *

# Let's check what lid produces on each accepted_doc
lid_labels = []
for doc in accepted_docs:
    res = lid.identify(doc["text"])
    lid_labels.append(res.label)

print("LID on full accepted text:")
print(Counter(lid_labels))
