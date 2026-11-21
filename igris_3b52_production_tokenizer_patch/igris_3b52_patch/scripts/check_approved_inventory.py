"""Read-only consistency check; does not authorize or run tokenizer training."""
import argparse, csv, json
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("inventory", help="Path to approved_line_inventory.csv")
    args = p.parse_args()
    rows = list(csv.DictReader(Path(args.inventory).open(encoding="utf-8-sig", newline="")))
    required = {"source_line", "classification", "approval_status", "training_candidate_status"}
    if not rows or not required.issubset(rows[0]): raise SystemExit("FAIL: missing rows or required columns")
    if len(rows) != 42: raise SystemExit(f"FAIL: expected 42 review rows, found {len(rows)}")
    if len({r["source_line"] for r in rows}) != 42: raise SystemExit("FAIL: duplicate source_line values")
    if any(r["approval_status"] != "APPROVED_CLASSIFICATION_ONLY" for r in rows): raise SystemExit("FAIL: unexpected approval status")
    keep = [r for r in rows if r["training_candidate_status"] == "CANDIDATE_PENDING_CLEANUP_AND_PROVENANCE"]
    excluded = [r for r in rows if r["training_candidate_status"] == "EXCLUDED_QUARANTINE"]
    other = [r for r in rows if r not in keep and r not in excluded]
    if len(keep) != 20 or len(excluded) != 22 or other: raise SystemExit(f"FAIL: keep={len(keep)}, excluded={len(excluded)}, other={len(other)}")
    print(json.dumps({"status":"PASS_READ_ONLY_INVENTORY_CHECK", "review_rows":42, "candidate_pending_cleanup_and_provenance":20, "excluded_quarantine":22, "training_authorized":False, "decision":"CLASSIFICATION_ONLY; NO TRAINING AUTHORIZATION"}, indent=2))
if __name__ == "__main__": main()
