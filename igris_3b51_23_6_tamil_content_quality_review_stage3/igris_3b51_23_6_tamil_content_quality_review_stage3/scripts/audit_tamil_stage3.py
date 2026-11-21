import argparse, csv, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
import unicodedata2 as ud
import regex

URL = re.compile(r"(?i)(https?://|www\.|\b[a-z0-9.-]+\.(com|in|org|net|edu|gov)\b)")
HTML = re.compile(r"(?is)<\s*/?\s*[a-z][^>]{0,300}>|&(?:nbsp|amp|quot|lt|gt);")
TOKENS = re.compile(r"<\|(?:pad|begin_of_text|end_of_text|system|user|assistant)\|>|</?(?:think|action|action_result)>")
SENT_END = regex.compile(r"[.!?।॥…]+")
TAMIL = regex.compile(r"\p{Script=Tamil}")
LATIN = regex.compile(r"\p{Script=Latin}")
LETTERS = regex.compile(r"\p{L}")
CONTROL = regex.compile(r"[[\p{Cc}]--[\t\n\r]]", regex.VERSION1)

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def pct(a,p):
    if not a: return None
    a=sorted(a); x=(len(a)-1)*p; lo=int(x); hi=min(lo+1,len(a)-1)
    return round(a[lo]+(a[hi]-a[lo])*(x-lo),2)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--clean",required=True)
    ap.add_argument("--review-register")
    ap.add_argument("--out",default="./reports/stage3")
    ap.add_argument("--max-record-chars",type=int,default=4000)
    a=ap.parse_args()
    src=Path(a.clean).resolve(); out=Path(a.out).resolve(); out.mkdir(parents=True,exist_ok=True)
    raw=src.read_bytes(); text=raw.decode("utf-8","strict"); lines=text.splitlines()
    lengths=[]; graphemes=[]; sentences=[]; flags=defaultdict(list); seen={}
    tamil_records=latin_records=mixed_records=no_tamil=0
    totals=Counter(); dup=[]
    for n,line in enumerate(lines,1):
        if not line.strip():
            flags[n].append("blank_record"); continue
        lengths.append(len(line))
        gs=regex.findall(r"\X",line); graphemes.append(len(gs))
        sentences.append(max(1,len(SENT_END.findall(line))))
        tn=len(TAMIL.findall(line)); ln=len(LATIN.findall(line)); letters=len(LETTERS.findall(line))
        tamil_records += bool(tn); latin_records += bool(ln); mixed_records += bool(tn and ln); no_tamil += not bool(tn)
        totals["characters"]+=len(line); totals["grapheme_clusters"]+=len(gs)
        totals["tamil_codepoints"]+=tn; totals["latin_codepoints"]+=ln
        if ud.normalize("NFC",line)!=line: flags[n].append("not_nfc")
        if len(line)>a.max_record_chars: flags[n].append("over_length")
        if URL.search(line): flags[n].append("url_marker")
        if HTML.search(line): flags[n].append("html_or_entity_marker")
        if TOKENS.search(line): flags[n].append("structural_token_spelling")
        if CONTROL.search(line): flags[n].append("control_character")
        if "\ufffd" in line: flags[n].append("replacement_character")
        if letters and tn/letters<0.35: flags[n].append("low_tamil_letter_ratio_review")
        key=regex.sub(r"\s+"," ",ud.normalize("NFC",line)).strip()
        if key in seen:
            dup.append({"first_line":seen[key],"duplicate_line":n}); flags[n].append("duplicate_record")
        else: seen[key]=n
        chunks=[x.strip() for x in SENT_END.split(line) if len(x.strip())>=40]
        c=Counter(chunks)
        if any(v>1 for v in c.values()): flags[n].append("repeated_sentence_chunk_review")
    flag_rows=[{"source_line":n,"reasons":";".join(rs),"record_characters":len(lines[n-1])}
               for n,rs in sorted(flags.items()) if n<=len(lines) and lines[n-1].strip()]
    review=None
    if a.review_register:
        rp=Path(a.review_register).resolve()
        with rp.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f))
        classes=Counter(r.get("preliminary_classification",r.get("classification","UNKNOWN")) for r in rows)
        approvals=Counter(r.get("human_approval_status","UNKNOWN") for r in rows)
        review={"sha256":digest(rp),"records":len(rows),"classification_counts":dict(classes),"human_approval_counts":dict(approvals)}
    reasons=Counter(x for r in flag_rows for x in r["reasons"].split(";"))
    report={
      "status":"AUDIT_COMPLETE_REVIEW_REQUIRED" if flag_rows or dup else "AUDIT_COMPLETE_NO_AUTOMATED_FLAGS",
      "audit_scope":"READ_ONLY_PROFILE_AND_HEURISTIC_FLAGS",
      "decision":"NO_SOURCE_MODIFICATION_NO_RECORD_DELETION_NO_MERGE_NO_DATASET_OR_LICENSE_APPROVAL_NO_TOKENIZER_TRAINING",
      "input":{"path":str(src),"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"line_count_including_blank":len(lines),"nonempty_records":sum(bool(x.strip()) for x in lines)},
      "unicode_database_version":ud.unidata_version,
      "profile":{"record_characters":{"min":min(lengths) if lengths else None,"median":pct(lengths,.5),"p95":pct(lengths,.95),"p99":pct(lengths,.99),"max":max(lengths) if lengths else None},
        "grapheme_clusters":{"total":totals["grapheme_clusters"],"median_per_record":pct(graphemes,.5)},
        "sentence_terminator_count":sum(sentences),"tamil_records":tamil_records,"latin_present_records":latin_records,
        "tamil_and_latin_records":mixed_records,"records_without_tamil":no_tamil,"character_totals":dict(totals)},
      "quality_signals":{"flagged_records":len(flag_rows),"flag_reason_counts":dict(reasons),"exact_duplicate_pairs_after_nfc_whitespace_key":len(dup),"duplicate_pair_examples":dup[:100]},
      "stage2_review_register":review,
      "limitations":["Sentence and repeated-passage checks are heuristic, not linguistic validation.","Tamil/Latin proportions do not determine whether a record is Tanglish or contaminated.","URL/markup markers are review signals, not automatic rejection decisions.","Grapheme counts do not prove one tokenizer token per grapheme.","This audit does not verify provenance, copyright, licensing, factual accuracy, or commercial-training suitability.","No record is automatically deleted, changed, merged, promoted, or approved."]
    }
    (out/"tamil_stage3_quality_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    with (out/"tamil_stage3_flagged_records.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["source_line","reasons","record_characters"]); w.writeheader(); w.writerows(flag_rows)
    print(json.dumps({"status":report["status"],"nonempty_records":report["input"]["nonempty_records"],
      "flagged_records":len(flag_rows),"duplicate_pairs":len(dup),"unicode_database_version":ud.unidata_version,
      "outputs":["tamil_stage3_quality_audit.json","tamil_stage3_flagged_records.csv"],"decision":report["decision"]},ensure_ascii=False,indent=2))
if __name__=="__main__": main()

