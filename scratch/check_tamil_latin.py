import check_lang_labels

docs = check_lang_labels.unique_docs
tamil_docs = [d for d in docs if d["assigned_lang"] == "TAMIL"]

print("Total Tamil docs:", len(tamil_docs))
for d in tamil_docs:
    t = d["text"]
    lat_chars = [c for c in t if ('a' <= c <= 'z') or ('A' <= c <= 'Z')]
    if lat_chars:
        print(d["source_file"], d["raw_id"], "Latin chars:", set(lat_chars), repr(t[:60]))
