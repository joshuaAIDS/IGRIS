"""Local, read-only quality audit for an explicitly supplied prepared corpus.

Language labels are heuristic estimates, not validated language identification.
The audit never edits its input and never downloads data or trains models.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

STRUCTURAL = (
    "<|pad|>", "<|begin_of_text|>", "<|end_of_text|>", "<think>", "</think>",
    "<action>", "</action>", "<action_result>", "</action_result>",
    "<|system|>", "<|user|>", "<|assistant|>",
)
TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
TANGLISH_HINTS = {
    "enna", "epdi", "epடி", "iruku", "irukku", "illa", "illai", "pannu", "pannunga",
    "machi", "machan", "seri", "sollu", "venum", "vendam", "romba", "nalla", "athu",
    "ithu", "unga", "naan", "nee", "neenga", "pogalam", "varum", "da", "di",
}

def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def _language_bucket(text: str) -> str:
    tamil=bool(TAMIL_RE.search(text)); latin=bool(LATIN_RE.search(text))
    if tamil and latin: return 'mixed_tamil_latin'
    if tamil: return 'tamil_script'
    if latin:
        words=set(re.findall(r"[a-zA-Z]+", text.casefold()))
        if words & TANGLISH_HINTS: return 'possible_tanglish'
        return 'latin_script_other_or_english'
    return 'other_or_no_letters'

def _near_duplicate_pairs(records: list[str], threshold: float, max_records: int):
    if len(records)>max_records:
        return [], True
    normalized=[re.sub(r"\s+", " ", x).strip().casefold() for x in records]
    pairs=[]
    # Only compare same-length buckets within a 20% length window to reduce work.
    buckets={}
    for i,s in enumerate(normalized):
        if not s: continue
        buckets.setdefault(len(s)//20, []).append((i,s))
    seen=set()
    for bucket, items in buckets.items():
        candidates=items + buckets.get(bucket-1, []) + buckets.get(bucket+1, [])
        for pos,(i,a) in enumerate(items):
            for j,b in candidates:
                if j<=i or (i,j) in seen: continue
                seen.add((i,j))
                if not a or not b: continue
                ratio=SequenceMatcher(None,a,b,autojunk=False).ratio()
                if ratio>=threshold: pairs.append({'record_a':i+1,'record_b':j+1,'similarity':round(ratio,4)})
    return pairs, False

def audit_corpus(corpus_path: str|Path, *, near_duplicate_threshold: float=0.92, max_near_duplicate_records: int=2000, max_record_chars: int=10000) -> dict:
    path=Path(corpus_path).expanduser().resolve()
    if not path.is_file(): raise FileNotFoundError(path)
    if not 0.5 <= near_duplicate_threshold <= 1.0: raise ValueError('near_duplicate_threshold must be between 0.5 and 1.0')
    if type(max_near_duplicate_records) is not int or max_near_duplicate_records<1: raise ValueError('max_near_duplicate_records must be a positive integer')
    if type(max_record_chars) is not int or max_record_chars<1: raise ValueError('max_record_chars must be a positive integer')
    raw=path.read_bytes()
    try: text=raw.decode('utf-8', errors='strict')
    except UnicodeDecodeError as e: raise ValueError(f'corpus is not valid UTF-8: {e}') from e
    if text.startswith('\ufeff'): raise ValueError('UTF-8 BOM detected; prepared corpus must be BOM-free')
    records=text.splitlines()
    if not records: raise ValueError('corpus has no records')
    counts=Counter(_language_bucket(r) for r in records)
    empty=sum(r=='' for r in records)
    whitespace=sum(bool(r) and not r.strip() for r in records)
    nul=sum('\x00' in r for r in records)
    surrogates=sum(any(0xD800<=ord(c)<=0xDFFF for c in r) for r in records)
    structural_hits=[]
    for idx,r in enumerate(records,1):
        for token in STRUCTURAL:
            if token in r: structural_hits.append({'record':idx,'token':token})
    long_records=[{'record':i,'characters':len(r)} for i,r in enumerate(records,1) if len(r)>max_record_chars]
    exact_seen={}; exact_dupes=[]
    for i,r in enumerate(records,1):
        key=re.sub(r'\s+',' ',r).strip().casefold()
        if key in exact_seen: exact_dupes.append({'record_a':exact_seen[key],'record_b':i})
        else: exact_seen[key]=i
    near_pairs, near_skipped=_near_duplicate_pairs(records,near_duplicate_threshold,max_near_duplicate_records)
    findings=[]
    if empty: findings.append('empty_records_present')
    if whitespace: findings.append('whitespace_only_records_present')
    if structural_hits: findings.append('unescaped_structural_spellings_present')
    if long_records: findings.append('long_records_present')
    if exact_dupes: findings.append('normalized_exact_duplicates_present')
    if near_pairs: findings.append('near_duplicates_present')
    if near_skipped: findings.append('near_duplicate_scan_skipped_record_limit')
    if nul or surrogates: findings.append('invalid_text_scalar_or_nul_detected')
    return {
      'project':'IGRIS','project_version':'2.2.28','pipeline':'3B.51.13',
      'input_path':str(path),'input_bytes':len(raw),'input_sha256':hashlib.sha256(raw).hexdigest(),
      'record_count':len(records),'character_count':sum(map(len,records)),
      'language_bucket_counts':dict(sorted(counts.items())),
      'language_detection_note':'Heuristic script/keyword buckets only; not a reliable language classifier. Latin-only English vs Tanglish cannot be established conclusively.',
      'empty_record_count':empty,'whitespace_only_record_count':whitespace,
      'nul_record_count':nul,'surrogate_record_count':surrogates,
      'structural_spelling_hits':structural_hits,'long_records':long_records,
      'normalized_exact_duplicate_pairs':exact_dupes,
      'near_duplicate_threshold':near_duplicate_threshold,'near_duplicate_pairs':near_pairs,
      'near_duplicate_scan_skipped':near_skipped,
      'findings':findings,
      'audit_status':'REVIEW_REQUIRED' if findings else 'NO_AUTOMATED_ISSUES_FOUND',
      'limitations':['No licensing, consent, provenance, factuality, privacy, or representativeness review is performed.',
        'Language buckets are heuristic and cannot certify English/Tamil/Tanglish proportions.',
        'Near-duplicate similarity is character-based and may produce false positives/negatives.',
        'A clean report does not mean the corpus is approved for training.']
    }

def main(argv=None):
    ap=argparse.ArgumentParser(description='Read-only IGRIS prepared-corpus quality audit; no training or downloads.')
    ap.add_argument('--input',required=True); ap.add_argument('--report',required=True)
    ap.add_argument('--near-duplicate-threshold',type=float,default=.92)
    ap.add_argument('--max-near-duplicate-records',type=int,default=2000)
    ap.add_argument('--max-record-chars',type=int,default=10000)
    a=ap.parse_args(argv); result=audit_corpus(a.input,near_duplicate_threshold=a.near_duplicate_threshold,max_near_duplicate_records=a.max_near_duplicate_records,max_record_chars=a.max_record_chars)
    out=Path(a.report).expanduser().resolve()
    if out.exists(): raise FileExistsError(f'report already exists: {out}')
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f"Audit status: {result['audit_status']}"); print(f"Records: {result['record_count']}; findings: {len(result['findings'])}"); print(f"Report: {out}"); print('Corpus modified: NO; training: NO; downloads: NO')
    return 0
if __name__=='__main__': raise SystemExit(main())
