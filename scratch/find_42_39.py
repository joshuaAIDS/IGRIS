import check_lang_labels
from collections import Counter
import re

docs = check_lang_labels.unique_docs
tanglish_docs = [d for d in docs if d["assigned_lang"] == "TANGLISH"]

print("Total Tanglish docs:", len(tanglish_docs))

# Let's inspect the sources of the 196 Tanglish docs:
print("Sources of Tanglish docs:")
print(Counter(d["source_file"] for d in tanglish_docs))

# Sources:
# PHASE23A: 100
# PHASE25: 51
# PHASE26: 29
# tanglish_synthetic_generator_v2: 15
# igris_phase17: 1

# Total = 100 + 51 + 29 + 15 + 1 = 196.

# What if:
# In PHASE25 (51) and PHASE26 (29)? 51 + 29 = 80! (Almost 81!)
# In PHASE25, how many are mixed script vs latin script?
# In PHASE26, how many are mixed script vs latin script?
p25_tg = [d for d in tanglish_docs if d["source_file"] == "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl"]
p26_tg = [d for d in tanglish_docs if d["source_file"] == "PHASE26_DATASET_SPLITS.json"]
p23_tg = [d for d in tanglish_docs if d["source_file"] == "PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl"]
v2_tg = [d for d in tanglish_docs if d["source_file"] == "tanglish_synthetic_generator_v2.py"]
p17_tg = [d for d in tanglish_docs if d["source_file"] == "igris_phase17_synthetic_multilingual.json"]

print("P25 Tanglish script distribution:")
print(Counter("TAMIL" if any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"]) else "LATIN" for d in p25_tg))

print("P26 Tanglish script distribution:")
print(Counter("TAMIL" if any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"]) else "LATIN" for d in p26_tg))

print("P23 Tanglish script distribution:")
print(Counter("TAMIL" if any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"]) else "LATIN" for d in p23_tg))

print("V2 Tanglish script distribution:")
print(Counter("TAMIL" if any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"]) else "LATIN" for d in v2_tg))
