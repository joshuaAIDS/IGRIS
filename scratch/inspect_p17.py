import check_lang_labels

docs = check_lang_labels.unique_docs
tanglish_docs = [d for d in docs if d["assigned_lang"] == "TANGLISH"]

# 51 from P25
# 29 from P26
# 1 from P17
# 100 from P23
# 15 from V2

# What is the 1 record in P17?
p17_tg = [d for d in tanglish_docs if d["source_file"] == "igris_phase17_synthetic_multilingual.json"]
print("P17 record:", p17_tg[0]["raw_id"], repr(p17_tg[0]["text"]))

# What about the 23 Latin records in P25?
p25_lat = [d for d in tanglish_docs if d["source_file"] == "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl" and not any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]
print("P25 Latin count:", len(p25_lat))

# What about the 16 Latin records in P26?
p26_lat = [d for d in tanglish_docs if d["source_file"] == "PHASE26_DATASET_SPLITS.json" and not any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]
print("P26 Latin count:", len(p26_lat))

# What about the 28 Tamil records in P25?
p25_ta = [d for d in tanglish_docs if d["source_file"] == "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl" and any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]
print("P25 Tamil count:", len(p25_ta))

# What about the 13 Tamil records in P26?
p26_ta = [d for d in tanglish_docs if d["source_file"] == "PHASE26_DATASET_SPLITS.json" and any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]
print("P26 Tamil count:", len(p26_ta))

# Let's inspect P17 record: is P17 record Tamil or Latin?
# It has text: let's see why it has no Tamil chars or if it has any Tamil chars
t = p17_tg[0]["text"]
print("P17 text:", repr(t))
print("P17 chars:", [(c, hex(ord(c))) for c in t if ord(c) > 127])
