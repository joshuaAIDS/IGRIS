import csv
import json
import sys
import unicodedata
import re
from collections import Counter
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

from duplicate_detector_v2 import DuplicateDetectorV2
from language_identifier_v2 import LanguageIdentifierV2

NON_TARGET_RANGES = [
    (0x0900, 0x097F),
    (0x0980, 0x09FF),
    (0x0A00, 0x0A7F),
    (0x0A80, 0x0AFF),
    (0x0B00, 0x0B7F),
    (0x0C00, 0x0C7F),
    (0x0C80, 0x0CFF),
    (0x0D00, 0x0D7F),
    (0x0600, 0x06FF),
    (0x0400, 0x04FF),
    (0x4E00, 0x9FFF),
]

def contains_non_target_script(text: str) -> bool:
    for ch in text:
        cp = ord(ch)
        for s, e in NON_TARGET_RANGES:
            if s <= cp <= e:
                return True
    return False

def clean_text(text: str) -> str:
    cleaned = re.sub(r'\s*\(Sample \d+ - Test Partition \w+\)', '', text)
    return unicodedata.normalize("NFC", cleaned.strip())

# Sources
sources_meta = [
    ("PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl", PATCH_ROOT / "PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl"),
    ("PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl", PATCH_ROOT / "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl"),
    ("PHASE26_DATASET_SPLITS.json", PATCH_ROOT / "PHASE26_DATASET_SPLITS.json"),
    ("igris_phase17_synthetic_multilingual.json", PATCH_ROOT / "data" / "synthetic_pretraining_fixtures" / "igris_phase17_synthetic_multilingual.json"),
    ("synthetic_dryrun_dataset.json", PATCH_ROOT / "experiments" / "phase19_dry_run" / "synthetic_dryrun_dataset.json"),
]

raw_records = []

# S1
with open(sources_meta[0][1], encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        raw_records.append({
            "source_file": "PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl",
            "raw_id": item["id"],
            "text": item["text"],
            "lang_hint": "TANGLISH"
        })

# S2
with open(sources_meta[1][1], encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        gt = item.get("ground_truth_language")
        raw_records.append({
            "source_file": "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl",
            "raw_id": item["id"],
            "text": item["text"],
            "lang_hint": gt if gt in ("TAMIL", "ENGLISH", "TANGLISH") else "OUT_OF_SCOPE"
        })

# S3
with open(sources_meta[2][1], encoding="utf-8") as f:
    data = json.load(f)
    for sp in ["dev", "val", "test"]:
        for item in data["splits"][sp]:
            gt = item.get("ground_truth_language")
            raw_records.append({
                "source_file": "PHASE26_DATASET_SPLITS.json",
                "raw_id": item["id"],
                "text": item["text"],
                "lang_hint": gt if gt in ("TAMIL", "ENGLISH", "TANGLISH") else "OUT_OF_SCOPE"
            })

# S4
with open(sources_meta[3][1], encoding="utf-8") as f:
    data = json.load(f)
    for item in data["records"]:
        l = item.get("language")
        map_l = {"ta": "TAMIL", "en": "ENGLISH", "tanglish": "TANGLISH"}.get(l, "OUT_OF_SCOPE")
        raw_records.append({
            "source_file": "igris_phase17_synthetic_multilingual.json",
            "raw_id": item["record_id"],
            "text": item["text"],
            "lang_hint": map_l
        })

# S5
with open(sources_meta[4][1], encoding="utf-8") as f:
    data = json.load(f)
    for item in data["records"]:
        l = item.get("language")
        map_l = {"ta": "TAMIL", "en": "ENGLISH"}.get(l, "OUT_OF_SCOPE")
        raw_records.append({
            "source_file": "synthetic_dryrun_dataset.json",
            "raw_id": item["record_id"],
            "text": item["text"],
            "lang_hint": map_l
        })

# S6
import tanglish_synthetic_generator_v2
for item in tanglish_synthetic_generator_v2.generate_v2_sample():
    raw_records.append({
        "source_file": "tanglish_synthetic_generator_v2.py",
        "raw_id": item["v2_id"],
        "text": item["text"],
        "lang_hint": "TANGLISH"
    })

# S7
import phase31_synthetic_validator
for doc in phase31_synthetic_validator.SYNTHETIC_PYTHON_DOCS:
    if "humaneval" not in doc["type"]:
        raw_records.append({
            "source_file": "phase31_synthetic_validator.py",
            "raw_id": doc["id"],
            "text": doc["text"],
            "lang_hint": "ENGLISH"
        })

dup_detector = DuplicateDetectorV2(near_dup_threshold=0.70)
lang_classifier = LanguageIdentifierV2()

unique_docs = []
for r in raw_records:
    t_clean = clean_text(r["text"])
    if len(t_clean) < 5 or contains_non_target_script(t_clean) or r["lang_hint"] == "OUT_OF_SCOPE":
        continue
    dup_res = dup_detector.check_and_register(r["raw_id"], t_clean)
    if dup_res.is_duplicate:
        continue
    
    # Pure LID check:
    lid_res = lang_classifier.identify(t_clean)
    
    # Rule used in original run_synthetic_tokenizer_training:
    if lid_res.label in ("TAMIL", "ENGLISH", "TANGLISH"):
        assigned_lang = lid_res.label
    elif r["lang_hint"] in ("TAMIL", "ENGLISH", "TANGLISH"):
        assigned_lang = r["lang_hint"]
    else:
        continue

    unique_docs.append({
        "raw_id": r["raw_id"],
        "source_file": r["source_file"],
        "text": t_clean,
        "lang_hint": r["lang_hint"],
        "lid_label": lid_res.label,
        "lid_confidence": lid_res.confidence,
        "assigned_lang": assigned_lang,
    })

print(f"Total unique docs: {len(unique_docs)}")
print(f"Assigned lang counts: {Counter(d['assigned_lang'] for d in unique_docs)}")
print(f"Pure LID label counts: {Counter(d['lid_label'] for d in unique_docs)}")
print(f"Lang hint counts: {Counter(d['lang_hint'] for d in unique_docs)}")

# Let's see what happens if we use pure LID vs lang_hint
