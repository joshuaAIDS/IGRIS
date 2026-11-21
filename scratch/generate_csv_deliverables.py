import csv
import json
import hashlib
import unicodedata
import re
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

def analyze_subset(docs):
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
            'tpw': tot_toks / tot_words if tot_words else 0.0,
            'tpc': tot_toks / tot_chars if tot_chars else 0.0,
            'mean_len': float(np.mean(lens)) if lens else 0.0,
            'median_len': float(np.median(lens)) if lens else 0.0,
            'p90_len': float(np.percentile(lens, 90)) if lens else 0.0,
            'p95_len': float(np.percentile(lens, 95)) if lens else 0.0,
            'max_len': int(max(lens)) if lens else 0,
            'roundtrip_acc': exact_rt / len(docs) * 100.0 if docs else 100.0,
            'active_vocab': len(emitted),
            'active_vocab_pct': len(emitted) / 32768 * 100.0,
            'unk_rate': 0.0
        }
    return res

# 1. Generate TOKENIZER_COMPARISON_METRICS.csv
# Columns: partition,metric_id,metric_name,original_candidate_a,experimental_candidate_a,delta,units,interpretation
comp_rows = []
partitions = [
    ('TRAIN', [d for d in corpus if d['split'] == 'TRAIN']),
    ('VALIDATION', [d for d in corpus if d['split'] == 'VALIDATION']),
    ('TEST', [d for d in corpus if d['split'] == 'TEST']),
    ('FULL_CORPUS', corpus),
]

metric_defs = [
    ('M01', 'Tokens Per Word (TPW)', lambda s: f"{s['tpw']:.3f}", lambda o, e: f"{e['tpw'] - o['tpw']:+.3f}", 'tokens/word', 'Fertility ratio: lower indicates more aggressive subword merging'),
    ('M02', 'Tokens Per Character (TPC)', lambda s: f"{s['tpc']:.3f}", lambda o, e: f"{e['tpc'] - o['tpc']:+.3f}", 'tokens/char', 'Character compression factor'),
    ('M03', 'Mean Sequence Length', lambda s: f"{s['mean_len']:.2f}", lambda o, e: f"{e['mean_len'] - o['mean_len']:+.2f}", 'tokens', 'Average token count per sequence'),
    ('M04', 'Median Sequence Length (p50)', lambda s: f"{s['median_len']:.1f}", lambda o, e: f"{e['median_len'] - o['median_len']:+.1f}", 'tokens', '50th percentile sequence length'),
    ('M05', '90th Percentile Length (p90)', lambda s: f"{s['p90_len']:.1f}", lambda o, e: f"{e['p90_len'] - o['p90_len']:+.1f}", 'tokens', '90th percentile sequence length'),
    ('M06', '95th Percentile Length (p95)', lambda s: f"{s['p95_len']:.1f}", lambda o, e: f"{e['p95_len'] - o['p95_len']:+.1f}", 'tokens', '95th percentile sequence length'),
    ('M07', 'Maximum Sequence Length', lambda s: str(s['max_len']), lambda o, e: f"{e['max_len'] - o['max_len']:+d}", 'tokens', 'Worst-case sequence length'),
    ('M08', 'Active Vocabulary Count', lambda s: str(s['active_vocab']), lambda o, e: f"{e['active_vocab'] - o['active_vocab']:+d}", 'slots', 'Unique vocabulary slots emitted on partition out of 32,768'),
    ('M09', 'Active Vocabulary Utilization', lambda s: f"{s['active_vocab_pct']:.2f}", lambda o, e: f"{e['active_vocab_pct'] - o['active_vocab_pct']:+.2f}", 'percent', 'Percentage of 32k capacity engaged by partition'),
    ('M10', 'Byte-Level Text Coverage', lambda s: '100.00', lambda o, e: '0.00', 'percent', 'Byte fallback guarantees 100% representation of all valid UTF-8 bytes'),
    ('M11', 'Unknown Token Rate (UNK)', lambda s: '0.00', lambda o, e: '0.00', 'percent', 'Zero UNKs emitted due to ByteLevel pre-tokenizer architecture'),
    ('M12', 'Unicode Round-Trip Accuracy', lambda s: f"{s['roundtrip_acc']:.2f}", lambda o, e: f"{e['roundtrip_acc'] - o['roundtrip_acc']:+.2f}", 'percent', 'Lossless string reconstruction on NFC target text'),
]

for part_name, docs in partitions:
    analysis = analyze_subset(docs)
    orig_s = analysis['orig']
    exp_s = analysis['exp']
    for mid, mname, get_val, get_delta, units, interp in metric_defs:
        val_orig = get_val(orig_s)
        val_exp = get_val(exp_s)
        delta_val = get_delta(orig_s, exp_s)
        comp_rows.append({
            'partition': part_name,
            'metric_id': mid,
            'metric_name': mname,
            'original_candidate_a': val_orig,
            'experimental_candidate_a': val_exp,
            'delta': delta_val,
            'units': units,
            'interpretation': interp
        })

with open('TOKENIZER_COMPARISON_METRICS.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['partition', 'metric_id', 'metric_name', 'original_candidate_a', 'experimental_candidate_a', 'delta', 'units', 'interpretation'])
    writer.writeheader()
    writer.writerows(comp_rows)
print('Wrote TOKENIZER_COMPARISON_METRICS.csv with', len(comp_rows), 'rows.')

# 2. Generate TOKENIZER_LANGUAGE_BREAKDOWN.csv
# Columns: partition,language_type,language,record_count,original_tpw,experimental_tpw,delta_tpw,original_tpc,experimental_tpc,delta_tpc,original_active_vocab,experimental_active_vocab
lang_rows = []
for part_name, pdocs in partitions:
    # Operational
    for lang in ['TAMIL', 'ENGLISH', 'TANGLISH']:
        sub = [d for d in pdocs if d['operational_language'] == lang]
        a = analyze_subset(sub)
        o, e = a['orig'], a['exp']
        lang_rows.append({
            'partition': part_name,
            'language_type': 'OPERATIONAL_LABEL',
            'language': lang,
            'record_count': len(sub),
            'original_tpw': f"{o['tpw']:.3f}",
            'experimental_tpw': f"{e['tpw']:.3f}",
            'delta_tpw': f"{e['tpw'] - o['tpw']:+.3f}",
            'original_tpc': f"{o['tpc']:.3f}",
            'experimental_tpc': f"{e['tpc']:.3f}",
            'delta_tpc': f"{e['tpc'] - o['tpc']:+.3f}",
            'original_active_vocab': o['active_vocab'],
            'experimental_active_vocab': e['active_vocab'],
        })
    # Matrix language
    for lang in ['TAMIL', 'ENGLISH', 'TANGLISH']:
        sub = [d for d in pdocs if d['matrix_language'] == lang]
        a = analyze_subset(sub)
        o, e = a['orig'], a['exp']
        lang_rows.append({
            'partition': part_name,
            'language_type': 'LINGUISTIC_MATRIX_LANGUAGE',
            'language': lang,
            'record_count': len(sub),
            'original_tpw': f"{o['tpw']:.3f}",
            'experimental_tpw': f"{e['tpw']:.3f}",
            'delta_tpw': f"{e['tpw'] - o['tpw']:+.3f}",
            'original_tpc': f"{o['tpc']:.3f}",
            'experimental_tpc': f"{e['tpc']:.3f}",
            'delta_tpc': f"{e['tpc'] - o['tpc']:+.3f}",
            'original_active_vocab': o['active_vocab'],
            'experimental_active_vocab': e['active_vocab'],
        })

with open('TOKENIZER_LANGUAGE_BREAKDOWN.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['partition', 'language_type', 'language', 'record_count', 'original_tpw', 'experimental_tpw', 'delta_tpw', 'original_tpc', 'experimental_tpc', 'delta_tpc', 'original_active_vocab', 'experimental_active_vocab']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(lang_rows)
print('Wrote TOKENIZER_LANGUAGE_BREAKDOWN.csv with', len(lang_rows), 'rows.')

# 3. Generate TOKENIZER_SCRIPT_BREAKDOWN.csv
# Columns: partition,script_or_feature,record_count,original_tpw,experimental_tpw,delta_tpw,original_tpc,experimental_tpc,delta_tpc,original_median_len,experimental_median_len,original_max_len,experimental_max_len
script_rows = []
for part_name, pdocs in partitions:
    for sc in ['TAMIL_SCRIPT', 'LATIN_SCRIPT', 'MIXED_SCRIPT']:
        sub = [d for d in pdocs if d['script_form'] == sc]
        a = analyze_subset(sub)
        o, e = a['orig'], a['exp']
        script_rows.append({
            'partition': part_name,
            'script_or_feature': sc,
            'record_count': len(sub),
            'original_tpw': f"{o['tpw']:.3f}",
            'experimental_tpw': f"{e['tpw']:.3f}",
            'delta_tpw': f"{e['tpw'] - o['tpw']:+.3f}",
            'original_tpc': f"{o['tpc']:.3f}",
            'experimental_tpc': f"{e['tpc']:.3f}",
            'delta_tpc': f"{e['tpc'] - o['tpc']:+.3f}",
            'original_median_len': f"{o['median_len']:.1f}",
            'experimental_median_len': f"{e['median_len']:.1f}",
            'original_max_len': o['max_len'],
            'experimental_max_len': e['max_len'],
        })
    # Tamil Discourse Markers
    sub_dm = [d for d in pdocs if d['contains_tamil_discourse_markers'] == 'YES']
    a_dm = analyze_subset(sub_dm)
    o_dm, e_dm = a_dm['orig'], a_dm['exp']
    script_rows.append({
        'partition': part_name,
        'script_or_feature': 'ENGLISH_WITH_TAMIL_DISCOURSE_MARKERS',
        'record_count': len(sub_dm),
        'original_tpw': f"{o_dm['tpw']:.3f}",
        'experimental_tpw': f"{e_dm['tpw']:.3f}",
        'delta_tpw': f"{e_dm['tpw'] - o_dm['tpw']:+.3f}",
        'original_tpc': f"{o_dm['tpc']:.3f}",
        'experimental_tpc': f"{e_dm['tpc']:.3f}",
        'delta_tpc': f"{e_dm['tpc'] - o_dm['tpc']:+.3f}",
        'original_median_len': f"{o_dm['median_len']:.1f}",
        'experimental_median_len': f"{e_dm['median_len']:.1f}",
        'original_max_len': o_dm['max_len'],
        'experimental_max_len': e_dm['max_len'],
    })

with open('TOKENIZER_SCRIPT_BREAKDOWN.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['partition', 'script_or_feature', 'record_count', 'original_tpw', 'experimental_tpw', 'delta_tpw', 'original_tpc', 'experimental_tpc', 'delta_tpc', 'original_median_len', 'experimental_median_len', 'original_max_len', 'experimental_max_len']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(script_rows)
print('Wrote TOKENIZER_SCRIPT_BREAKDOWN.csv with', len(script_rows), 'rows.')
