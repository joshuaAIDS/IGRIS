#!/usr/bin/env python3
import argparse, csv, hashlib, json, unicodedata
from pathlib import Path

EXPECTED_RAW_SHA = "54dffb4960bf1e3c48477ef6bc9a7933dea68687c4ea9fcf097a69425d5d019d"
EXPECTED_CLEAN_SHA = "8b26af54e5b77c1434d583b487cec4db8af6a2560bdfdff015e85d8e8ea45064"
EXPECTED_QUARANTINE_SHA = "f3e32408d6a96b99d4def3ca4079770d6cf7594a553d57cda1a44cfeedced874"
EXPECTED_MIXED_SHA = "b957db99e9abf197a32d14d0f4f4198f97d3e33f5eb5266d8780a8c294b4251b"

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def read_jsonl(p):
    out=[]
    with open(p,encoding="utf-8") as f:
        for n,line in enumerate(f,1):
            if line.strip():
                try: out.append(json.loads(line))
                except Exception as e: raise ValueError(f"{p}: invalid JSONL line {n}: {e}")
    return out

def main():
    ap=argparse.ArgumentParser()
    for name in ["raw","clean","quarantine","mixed","recovered","unresolved","remediation-report","recovery-report","out"]:
        ap.add_argument("--"+name,required=True)
    a=ap.parse_args()
    paths={k:Path(getattr(a,k.replace("-","_"))) for k in ["raw","clean","quarantine","mixed","recovered","unresolved","remediation-report","recovery-report"]}
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    checks=[]; blockers=[]; reviews=[]
    for k,p in paths.items():
        if not p.is_file(): blockers.append(f"missing_input:{k}:{p}")
    if blockers:
        report={"status":"BLOCKED","blockers":blockers}
        (out/"tamil_dataset_final_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(report,indent=2)); return 2

    hashes={k:sha(p) for k,p in paths.items() if k not in ["remediation-report","recovery-report"]}
    raw_report=read_json(paths["recovery-report"])
    rem_report=read_json(paths["remediation-report"])
    expected_raw=raw_report.get("raw_source_sha256")
    expected_clean=rem_report.get("outputs",{}).get("clean_sha256")
    expected_q=rem_report.get("outputs",{}).get("quarantine_sha256")
    expected_m=rem_report.get("outputs",{}).get("mixed_script_review_sha256")
    for key,actual,expected in [
        ("raw_sha256",hashes["raw"],expected_raw or EXPECTED_RAW_SHA),
        ("clean_sha256",hashes["clean"],expected_clean or EXPECTED_CLEAN_SHA),
        ("quarantine_sha256",hashes["quarantine"],expected_q or EXPECTED_QUARANTINE_SHA),
        ("mixed_sha256",hashes["mixed"],expected_m or EXPECTED_MIXED_SHA)]:
        ok=(actual==expected); checks.append({"check":key,"pass":ok,"actual":actual,"expected":expected})
        if not ok: blockers.append(key+"_mismatch")

    try:
        raw_text=paths["raw"].read_text(encoding="utf-8")
        clean_text=paths["clean"].read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        blockers.append("invalid_utf8:"+str(e)); raw_text=""; clean_text=""
    raw_lines=raw_text.splitlines()
    clean_lines=[x for x in clean_text.splitlines() if x.strip()]
    q=read_jsonl(paths["quarantine"]); mixed=read_jsonl(paths["mixed"])
    recovered=read_jsonl(paths["recovered"]); unresolved=read_jsonl(paths["unresolved"])
    # Reconcile every unresolved item against its 1-based source line using NFC.
    reconciled=[]; mismatch=[]
    for item in unresolved:
        line_no=item.get("source_line_1_based")
        orig=item.get("original_classification_record",{}).get("original_record",{})
        saved=orig.get("text", item.get("text",""))
        if not isinstance(line_no,int) or line_no<1 or line_no>len(raw_lines):
            mismatch.append({"source_line":line_no,"reason":"invalid_line_reference"})
            continue
        src=raw_lines[line_no-1]
        ok=unicodedata.normalize("NFC",src)==unicodedata.normalize("NFC",saved)
        reconciled.append({"source_line":line_no,"nfc_match":ok})
        if not ok: mismatch.append({"source_line":line_no,"reason":"nfc_text_mismatch"})
    if mismatch: blockers.append("unresolved_source_mismatches")
    if len(raw_lines)!=10000: reviews.append(f"raw_line_count_is_{len(raw_lines)}_expected_10000")
    if len(clean_lines)!=9766: reviews.append(f"clean_record_count_is_{len(clean_lines)}_expected_9766")
    if len(q)!=65: reviews.append(f"quarantine_count_is_{len(q)}_expected_65")
    if len(mixed)!=723: reviews.append(f"mixed_review_count_is_{len(mixed)}_expected_723")
    if len(unresolved)!=10: reviews.append(f"unresolved_count_is_{len(unresolved)}_expected_10")
    if any(unicodedata.normalize("NFC",x)!=x for x in clean_lines): blockers.append("clean_file_contains_non_nfc_records")
    # Candidate output only if source identity and reconciliation both pass.
    if not blockers:
        (out/"approved_records.txt").write_text("\n".join(clean_lines)+"\n",encoding="utf-8")
    rows=[
      ("raw_records",len(raw_lines)),("clean_records",len(clean_lines)),
      ("quarantine_records",len(q)),("mixed_script_review_records",len(mixed)),
      ("recovered_records",len(recovered)),("unresolved_records",len(unresolved)),
      ("unresolved_nfc_matches",sum(x["nfc_match"] for x in reconciled)),
      ("unresolved_nfc_mismatches",len(mismatch))]
    with open(out/"tamil_dataset_summary.csv","w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f); w.writerow(["metric","value"]); w.writerows(rows)
    status="BLOCKED" if blockers else ("PASS_WITH_REVIEW" if reviews or True else "PASS")
    report={"status":status,"checks":checks,"counts":dict(rows),
      "raw_sha256":hashes["raw"],"clean_sha256":hashes["clean"],
      "quarantine_sha256":hashes["quarantine"],"mixed_sha256":hashes["mixed"],
      "unresolved_reconciliation":reconciled,"mismatches":mismatch,
      "blockers":blockers,"review_items":reviews,
      "notes":["Read-only audit; input files were not modified.",
       "NFC source-line reconciliation does not establish content quality.",
       "Mixed-script records require human review.",
       "Technical approval is not licensing or commercial-rights approval.",
       "The pilot's first 10,000 source lines are not a representative random sample."]}
    (out/"tamil_dataset_final_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 2 if blockers else 0

if __name__=="__main__": raise SystemExit(main())
