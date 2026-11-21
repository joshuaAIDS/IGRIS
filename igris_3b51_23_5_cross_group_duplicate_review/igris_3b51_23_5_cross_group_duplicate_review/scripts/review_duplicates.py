#!/usr/bin/env python3
"""Read-only cross-group duplicate review for IGRIS Tamil pilot."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

def read_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                rows.append(json.loads(line))
    return rows

def extract_text(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for k in ("text", "content", "original_text", "recovered_full_source_text"):
            if isinstance(obj.get(k), str):
                return obj[k]
        for k in ("original_record", "original_classification_record"):
            if k in obj:
                found = extract_text(obj[k])
                if found is not None:
                    return found
    return None

def get_nested(obj, *keys):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--duplicates", required=True)
    p.add_argument("--clean", required=True)
    p.add_argument("--mixed", required=True)
    p.add_argument("--quarantine", required=True)
    p.add_argument("--recovered", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()

    paths = {
        "duplicates": Path(a.duplicates),
        "clean": Path(a.clean),
        "mixed": Path(a.mixed),
        "quarantine": Path(a.quarantine),
        "recovered_review_only": Path(a.recovered),
    }
    missing = [f"{k}: {v}" for k, v in paths.items() if not v.is_file()]
    if missing:
        raise SystemExit("BLOCKED: missing inputs:\n" + "\n".join(missing))

    clean = [x for x in paths["clean"].read_text(encoding="utf-8").splitlines() if x != ""]
    mixed = read_jsonl(paths["mixed"])
    quarantine = read_jsonl(paths["quarantine"])
    recovered = read_jsonl(paths["recovered_review_only"])
    indexed = {
        "clean": clean,
        "mixed": mixed,
        "quarantine": quarantine,
        "recovered_review_only": recovered,
    }

    output_rows = []
    category_counts = {}
    errors = []
    with paths["duplicates"].open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"nfc_text_sha256", "groups", "references_json"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise SystemExit(f"BLOCKED: duplicate CSV must contain {sorted(required)}")
        for csv_line, row in enumerate(reader, 2):
            refs = json.loads(row["references_json"])
            groups = sorted({r["group"] for r in refs})
            category = ";".join(groups)
            category_counts[category] = category_counts.get(category, 0) + 1
            details = []
            for ref in refs:
                group = ref["group"]
                row_no = int(ref["row"])
                if group not in indexed or row_no < 1 or row_no > len(indexed[group]):
                    errors.append({"csv_line": csv_line, "bad_reference": ref})
                    continue
                obj = indexed[group][row_no - 1]
                text = obj if isinstance(obj, str) else extract_text(obj)
                digest = hashlib.sha256(text.encode("utf-8")).hexdigest() if isinstance(text, str) else None
                quarantine_reasons = None
                source_line = None
                if isinstance(obj, dict):
                    quarantine_reasons = obj.get("reasons")
                    source_line = obj.get("line")
                details.append({
                    "group": group,
                    "row": row_no,
                    "source_line": source_line,
                    "text_available": isinstance(text, str),
                    "text_sha256": digest,
                    "quarantine_reasons": quarantine_reasons,
                })
            if len(details) != len(refs):
                review_status = "REFERENCE_ERROR"
            elif category == "clean;mixed":
                review_status = "EXPECTED_REVIEW_LAYER_OVERLAP"
            elif category in ("clean;recovered_review_only", "clean;mixed;recovered_review_only"):
                review_status = "RECOVERED_COPY_ALREADY_PRESENT_IN_CLEAN_KEEP_REVIEW_ONLY"
            elif category == "mixed;quarantine":
                review_status = "QUARANTINE_PREVAILS_MANUAL_CONTENT_REVIEW_REQUIRED"
            else:
                review_status = "MANUAL_REVIEW_REQUIRED"
            output_rows.append({
                "nfc_text_sha256": row["nfc_text_sha256"],
                "groups": category,
                "occurrence_count": row.get("occurrence_count", ""),
                "review_status": review_status,
                "references": details,
            })

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    review_csv = out / "duplicate_review_register.csv"
    fields = ["nfc_text_sha256", "groups", "occurrence_count", "review_status", "references_json"]
    with review_csv.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in output_rows:
            w.writerow({
                "nfc_text_sha256": row["nfc_text_sha256"],
                "groups": row["groups"],
                "occurrence_count": row["occurrence_count"],
                "review_status": row["review_status"],
                "references_json": json.dumps(row["references"], ensure_ascii=False),
            })

    summary = {
        "status": "PASS_WITH_REVIEW" if not errors else "REVIEW_REQUIRED",
        "decision": "DUPLICATE_CLASSIFICATION_ONLY_NO_DELETE_NO_MERGE_NO_PROMOTION",
        "duplicate_keys_reviewed": len(output_rows),
        "category_counts": category_counts,
        "reference_errors": errors,
        "review_policy": {
            "clean;mixed": "Mixed-script review is an additional classification layer; do not remove from clean solely because of this overlap.",
            "clean;recovered_review_only": "Recovered copy already appears in clean; keep recovered copy review-only.",
            "clean;mixed;recovered_review_only": "Same content appears in clean and mixed review; recovered copy remains review-only.",
            "mixed;quarantine": "Quarantine reason takes precedence; keep quarantined pending manual review.",
            "all_other_categories": "Manual review required; no automatic action.",
        },
        "input_hashes": {
            k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths.items()
        },
        "outputs": [str(review_csv), str(out / "duplicate_review_summary.json")],
        "limitations": [
            "NFC-hash matches identify exact normalized text duplicates, not semantic duplicates.",
            "This script does not determine licensing, provenance, safety, or commercial-use rights.",
            "No input records are modified, deleted, merged, or approved.",
        ],
    }
    summary_path = out / "duplicate_review_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
