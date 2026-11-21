import csv
import json
import hashlib
import unicodedata
import re
import time
from pathlib import Path
from tokenizers import Tokenizer
import numpy as np

PATCH_ROOT = Path(r'C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch')
split_csv = PATCH_ROOT / 'CANDIDATE_A_SYNTHETIC_SPLIT_MANIFEST.csv'
labels_csv = PATCH_ROOT / 'CANDIDATE_A_MULTIDIMENSIONAL_LANGUAGE_LABELS.csv'

with open(split_csv, encoding='utf-8') as f:
    split_rows = list(csv.DictReader(f))
with open(labels_csv, encoding='utf-8') as f:
    label_rows = list(csv.DictReader(f))

# Reconstruct all 399 texts
source_records = {}
with open(PATCH_ROOT / 'PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        source_records[('PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl', item['id'])] = item['text']

with open(PATCH_ROOT / 'PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl', encoding='utf-8') as f:
    for line in f:
        item = json.loads(line)
        source_records[('PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl', item['id'])] = item['text']

with open(PATCH_ROOT / 'PHASE26_DATASET_SPLITS.json', encoding='utf-8') as f:
    data = json.load(f)
    for sp_name, recs in data.get('splits', {}).items():
        for r in recs:
            source_records[('PHASE26_DATASET_SPLITS.json', r['id'])] = r['text']

p17 = PATCH_ROOT / 'data' / 'synthetic_pretraining_fixtures' / 'igris_phase17_synthetic_multilingual.json'
with open(p17, encoding='utf-8') as f:
    data = json.load(f)
    for r in data.get('records', []):
        source_records[('igris_phase17_synthetic_multilingual.json', r['record_id'])] = r['text']

p_dry = PATCH_ROOT / 'experiments' / 'phase19_dry_run' / 'synthetic_dryrun_dataset.json'
with open(p_dry, encoding='utf-8') as f:
    data = json.load(f)
    for r in data.get('records', []):
        source_records[('synthetic_dryrun_dataset.json', r['record_id'])] = r['text']

import sys
sys.path.insert(0, str(PATCH_ROOT / 'scripts'))
import tanglish_synthetic_generator_v2
for item in tanglish_synthetic_generator_v2.generate_v2_sample():
    source_records[('tanglish_synthetic_generator_v2.py', item['v2_id'])] = item['text']

import phase31_synthetic_validator
for doc in phase31_synthetic_validator.SYNTHETIC_PYTHON_DOCS:
    source_records[('phase31_synthetic_validator.py', doc['id'])] = doc['text']
for tree in phase31_synthetic_validator.SYNTHETIC_OASST1_TREES:
    for node in tree.get('nodes', []):
        source_records[('phase31_synthetic_validator.py', node['id'])] = node['text']

def clean_text(text: str) -> str:
    cleaned = re.sub(r'\s*\(Sample \d+ - Test Partition \w+\)', '', text)
    return unicodedata.normalize('NFC', cleaned.strip())

corpus = []
for i, r in enumerate(split_rows):
    lbl = label_rows[i]
    raw_txt = source_records[(r['source_file'], lbl['source_record_id'])]
    c_txt = clean_text(raw_txt)
    h = hashlib.sha256(c_txt.encode('utf-8')).hexdigest()
    if h != r['text_sha256']:
        c_txt = unicodedata.normalize('NFC', raw_txt.strip())
    doc = {
        'doc_id': r['doc_id'],
        'split': r['split'],
        'operational_language': r['language'],
        'matrix_language': lbl['linguistic_matrix_language'],
        'script_form': lbl['script_form'],
        'contains_tamil_discourse_markers': lbl['contains_tamil_discourse_markers'],
        'text': c_txt,
        'words': max(1, len(c_txt.split())),
        'chars': len(c_txt)
    }
    corpus.append(doc)

tok_orig = Tokenizer.from_file('artifacts/tokenizer/candidate_a/tokenizer.json')
tok_exp = Tokenizer.from_file('igris_3b52_production_tokenizer_patch/igris_3b52_patch/artifacts/tokenizer/candidate_a_synthetic_experiment/tokenizer.json')

def analyze_group(docs):
    res = {}
    for name, tok in [('orig', tok_orig), ('exp', tok_exp)]:
        lens = []
        words = []
        chars = []
        emitted = set()
        exact_rt = 0
        for d in docs:
            enc = tok.encode(d['text'])
            dec = tok.decode(enc.ids)
            lens.append(len(enc.ids))
            words.append(d['words'])
            chars.append(d['chars'])
            emitted.update(enc.ids)
            if dec == d['text']:
                exact_rt += 1
        
        tot_toks = sum(lens)
        tot_words = sum(words)
        tot_chars = sum(chars)
        res[name] = {
            'count': len(docs),
            'total_tokens': tot_toks,
            'total_words': tot_words,
            'total_chars': tot_chars,
            'tpw': tot_toks / tot_words if tot_words else 0,
            'tpc': tot_toks / tot_chars if tot_chars else 0,
            'mean_len': float(np.mean(lens)) if lens else 0.0,
            'median_len': float(np.median(lens)) if lens else 0.0,
            'p90_len': float(np.percentile(lens, 90)) if lens else 0.0,
            'p95_len': float(np.percentile(lens, 95)) if lens else 0.0,
            'max_len': int(max(lens)) if lens else 0,
            'roundtrip_acc': exact_rt / len(docs) * 100 if docs else 100.0,
            'active_vocab': len(emitted),
            'active_vocab_pct': len(emitted) / 32768 * 100.0,
            'unk_rate': 0.0
        }
    return res

splits_analysis = {
    'TRAIN': analyze_group([d for d in corpus if d['split'] == 'TRAIN']),
    'VALIDATION': analyze_group([d for d in corpus if d['split'] == 'VALIDATION']),
    'TEST': analyze_group([d for d in corpus if d['split'] == 'TEST']),
    'FULL': analyze_group(corpus)
}

print('=== SPLIT SUMMARY ===')
for sp, data in splits_analysis.items():
    o = data['orig']
    e = data['exp']
    print(f"{sp:10s} | Docs: {o['count']:3d} | Orig TPW: {o['tpw']:6.3f} (TPC {o['tpc']:5.3f}) | Exp TPW: {e['tpw']:6.3f} (TPC {e['tpc']:5.3f}) | Orig Vocab: {o['active_vocab']:4d} ({o['active_vocab_pct']:5.2f}%) | Exp Vocab: {e['active_vocab']:4d} ({e['active_vocab_pct']:5.2f}%)")

print('\n=== SEQUENCE LENGTH PERCENTILES (MEDIAN, P90, P95, MAX) ===')
for sp, data in splits_analysis.items():
    o = data['orig']
    e = data['exp']
    print(f"{sp:10s} | Orig: med={o['median_len']:5.1f}, p90={o['p90_len']:5.1f}, p95={o['p95_len']:5.1f}, max={o['max_len']:3d} | Exp: med={e['median_len']:5.1f}, p90={e['p90_len']:5.1f}, p95={e['p95_len']:5.1f}, max={e['max_len']:3d}")

print('\n=== OPERATIONAL LANGUAGE BREAKDOWN (TRAIN, VAL, TEST, FULL) ===')
for sp in ['TRAIN', 'VALIDATION', 'TEST', 'FULL']:
    print(f"\n--- Split: {sp} ---")
    base_docs = corpus if sp == 'FULL' else [d for d in corpus if d['split'] == sp]
    for lang in ['TAMIL', 'ENGLISH', 'TANGLISH']:
        sub = [d for d in base_docs if d['operational_language'] == lang]
        a = analyze_group(sub)
        o, e = a['orig'], a['exp']
        print(f"  {lang:8s} | Docs: {o['count']:3d} | Orig TPW: {o['tpw']:6.3f} (TPC {o['tpc']:5.3f}) | Exp TPW: {e['tpw']:6.3f} (TPC {e['tpc']:5.3f}) | Delta: {e['tpw']-o['tpw']:+6.3f}")

print('\n=== MATRIX LANGUAGE BREAKDOWN (FULL) ===')
for lang in ['TAMIL', 'ENGLISH', 'TANGLISH']:
    sub = [d for d in corpus if d['matrix_language'] == lang]
    a = analyze_group(sub)
    o, e = a['orig'], a['exp']
    print(f"  {lang:8s} | Docs: {o['count']:3d} | Orig TPW: {o['tpw']:6.3f} (TPC {o['tpc']:5.3f}) | Exp TPW: {e['tpw']:6.3f} (TPC {e['tpc']:5.3f}) | Delta: {e['tpw']-o['tpw']:+6.3f}")

print('\n=== SCRIPT FORM BREAKDOWN (FULL) ===')
for sc in ['TAMIL_SCRIPT', 'LATIN_SCRIPT', 'MIXED_SCRIPT']:
    sub = [d for d in corpus if d['script_form'] == sc]
    a = analyze_group(sub)
    o, e = a['orig'], a['exp']
    print(f"  {sc:12s} | Docs: {o['count']:3d} | Orig TPW: {o['tpw']:6.3f} (TPC {o['tpc']:5.3f}) | Exp TPW: {e['tpw']:6.3f} (TPC {e['tpc']:5.3f})")

sub_dm = [d for d in corpus if d['contains_tamil_discourse_markers'] == 'YES']
a_dm = analyze_group(sub_dm)
o_dm, e_dm = a_dm['orig'], a_dm['exp']
print(f"\n=== TAMIL DISCOURSE MARKERS (YES) ===\n  Docs: {o_dm['count']:3d} | Orig TPW: {o_dm['tpw']:6.3f} | Exp TPW: {e_dm['tpw']:6.3f} | Delta: {e_dm['tpw']-o_dm['tpw']:+6.3f}")

# Timing benchmarks on test set with warmup
print('\n=== TIMING SPEED BENCHMARK (TEST SPLIT x 100) ===')
test_texts = [d['text'] for d in corpus if d['split'] == 'TEST'] * 100

for label, tok in [('Original Candidate A', tok_orig), ('Experimental Candidate A', tok_exp)]:
    # Warmup
    for _ in range(5):
        _ = [tok.encode(t) for t in test_texts[:50]]
    
    # Encode timing
    t0 = time.perf_counter()
    encs = [tok.encode(t) for t in test_texts]
    t1 = time.perf_counter()
    enc_time = t1 - t0
    tot_toks = sum(len(e.ids) for e in encs)
    enc_sps = len(test_texts) / enc_time
    enc_tps = tot_toks / enc_time

    # Decode timing
    t0 = time.perf_counter()
    for e in encs:
        _ = tok.decode(e.ids)
    t1 = time.perf_counter()
    dec_time = t1 - t0
    dec_sps = len(test_texts) / dec_time
    dec_tps = tot_toks / dec_time

    print(f"{label}:")
    print(f"  Encode Speed: {enc_sps:8.1f} sents/sec ({enc_tps:9.1f} tokens/sec) in {enc_time*1000:.1f}ms")
    print(f"  Decode Speed: {dec_sps:8.1f} sents/sec ({dec_tps:9.1f} tokens/sec) in {dec_time*1000:.1f}ms")
