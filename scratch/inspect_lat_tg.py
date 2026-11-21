import check_lang_labels

docs = check_lang_labels.unique_docs
tanglish_docs = [d for d in docs if d["assigned_lang"] == "TANGLISH"]

lat_tg = [d for d in tanglish_docs if d["source_file"] in ("PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl", "PHASE26_DATASET_SPLITS.json", "igris_phase17_synthetic_multilingual.json") and not any(0x0B80 <= ord(c) <= 0x0BFF for c in d["text"])]

print(f"Total Latin Tanglish records from P25/P26/P17: {len(lat_tg)}")
for i, d in enumerate(lat_tg):
    print(f"[{i+1:02d}] {d['source_file'][:15]} | {d['raw_id']} | {repr(d['text'][:60])}")
