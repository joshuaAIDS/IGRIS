#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, hashlib, json, sys
from pathlib import Path
try:
    import unicodedata2 as ud
except ImportError:
    raise SystemExit("ERROR: unicodedata2 is required. Expected installed version 15.1.0; no installation is attempted.")

EXPECTED_UNICODE = "15.1.0"
TAMIL = range(0x0B80, 0x0C00)
STRUCTURAL = [
    "<|pad|>", "<|begin_of_text|>", "<|end_of_text|>", "<think>", "</think>",
    "<action>", "</action>", "<action_result>", "</action_result>",
    "<|system|>", "<|user|>", "<|assistant|>"
]
MAX_CHARS = 4000

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--max-chars",type=int,default=MAX_CHARS)
    args=ap.parse_args()
    if ud.unidata_version != EXPECTED_UNICODE:
        raise SystemExit(f"ERROR: Unicode database {ud.unidata_version}; expected {EXPECTED_UNICODE}.")
    src=Path(args.input)
    raw=src.read_bytes()
    text=raw.decode("utf-8",errors="strict")
    lines=text.splitlines()
    accepted=[]
    quarantine=[]
    mixed=[]
    seen=set()
    duplicates=0
    nfc_changed=0
    structural_hits=0
    char_counts=collections.Counter()
    reasons=collections.Counter()
    lengths=[]
    records=[]
    for idx,line in enumerate(lines,1):
        normalized=ud.normalize("NFC",line)
        if normalized != line: nfc_changed+=1
        for ch in normalized: char_counts[ord(ch)] += 1
        reasons_here=[]
        if "\ufffd" in normalized: reasons_here.append("replacement_character_U+FFFD")
        if "\x00" in normalized: reasons_here.append("NUL")
        if any((ord(c)<32 and c not in "\t") or 0x7F<=ord(c)<=0x9F for c in normalized):
            reasons_here.append("control_character")
        if len(normalized)>args.max_chars: reasons_here.append("over_length")
        hits=[tok for tok in STRUCTURAL if tok in normalized]
        if hits:
            structural_hits+=1
            reasons_here.append("structural_token_spelling")
        has_tamil=any(ord(c) in TAMIL for c in normalized)
        has_latin=any(("A"<=c<="Z") or ("a"<=c<="z") for c in normalized)
        if has_tamil and has_latin:
            mixed.append({"line":idx,"text":normalized[:500],"truncated":len(normalized)>500})
        if not normalized.strip():
            reasons_here.append("blank_record")
        if reasons_here:
            quarantine.append({"line":idx,"reasons":reasons_here,"text":normalized})
            reasons.update(reasons_here)
            continue
        key=normalized
        if key in seen:
            duplicates+=1
            continue
        seen.add(key)
        accepted.append(normalized)
        lengths.append(len(normalized))
    outdir=Path(__file__).resolve().parents[1]
    (outdir/"processed").mkdir(exist_ok=True)
    (outdir/"reports").mkdir(exist_ok=True)
    clean_data=("".join(x+"\n" for x in accepted)).encode("utf-8")
    quarantine_data=("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in quarantine)).encode("utf-8")
    mixed_data=("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in mixed)).encode("utf-8")
    clean_path=outdir/"processed"/"tamil_nfc_deduplicated.txt"
    q_path=outdir/"processed"/"tamil_quarantine.jsonl"
    m_path=outdir/"processed"/"tamil_mixed_script_review.jsonl"
    clean_path.write_bytes(clean_data); q_path.write_bytes(quarantine_data); m_path.write_bytes(mixed_data)
    report={
      "status":"PASS_WITH_REVIEW" if quarantine or mixed or duplicates else "PASS",
      "input":str(src.resolve()),"input_bytes":len(raw),"input_sha256":sha256_bytes(raw),
      "unicode_database_version":ud.unidata_version,"utf8_valid":True,
      "input_records":len(lines),"nfc_changed_records":nfc_changed,
      "exact_duplicates_after_nfc_removed":duplicates,
      "accepted_unique_records":len(accepted),"quarantined_records":len(quarantine),
      "mixed_tamil_latin_records_for_review":len(mixed),
      "structural_token_records_flagged":structural_hits,
      "max_record_chars_threshold":args.max_chars,
      "accepted_length_chars":{
        "min":min(lengths) if lengths else 0,
        "median":sorted(lengths)[len(lengths)//2] if lengths else 0,
        "max":max(lengths) if lengths else 0
      },
      "character_counts":{
        "tamil_block":sum(v for cp,v in char_counts.items() if cp in TAMIL),
        "latin_letters":sum(v for cp,v in char_counts.items() if (65<=cp<=90 or 97<=cp<=122)),
        "replacement_U+FFFD":char_counts[0xFFFD],
        "NUL":char_counts[0],
        "control_excluding_tab":sum(v for cp,v in char_counts.items() if ((cp<32 and cp!=9) or 0x7F<=cp<=0x9F))
      },
      "quarantine_reason_counts":dict(reasons),
      "outputs":{
        "clean":str(clean_path),"clean_records":len(accepted),"clean_sha256":sha256_bytes(clean_data),
        "quarantine":str(q_path),"quarantine_sha256":sha256_bytes(quarantine_data),
        "mixed_script_review":str(m_path),"mixed_script_review_sha256":sha256_bytes(mixed_data)
      },
      "policy_notes":[
        "Original input was not modified.",
        "NFC normalization used Unicode 15.1.",
        "Duplicates were removed only from the processed output after NFC.",
        "Mixed Tamil-Latin records remain in clean output and are separately flagged.",
        "Suspicious and over-length records were quarantined, not deleted.",
        "This is a technical quality report, not a licensing or commercial-rights approval."
      ]
    }
    report_path=outdir/"reports"/"tamil_remediation_report.json"
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print(f"\nReport saved: {report_path}")
if __name__=="__main__": main()
