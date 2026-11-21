import json
import time
import tracemalloc
from pathlib import Path
from collections import defaultdict

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
import sys
sys.path.insert(0, str(PATCH_DIR / "scripts"))

from dataset_pipeline_v2 import DatasetPipelineV2, RawRecord

with open(PATCH_DIR / "PHASE26_DATASET_SPLITS.json", "r", encoding="utf-8") as f:
    pkg = json.load(f)

# Combine all 300 records for the resource benchmark
all_records = []
for split in ["dev", "val", "test"]:
    for r in pkg["splits"][split]:
        all_records.append(RawRecord(
            id=r["id"],
            text=r["text"],
            source_id="BENCHMARK_PROFILING",
            metadata=r
        ))

pipeline = DatasetPipelineV2(near_dup_threshold=0.70)

# Profile individual stages
stage_times = defaultdict(float)
total_tokens_estimated = 0

tracemalloc.start()
t0_proc = time.process_time()
t0_wall = time.perf_counter()

processed_records = []
for rec in all_records:
    orig_text = rec.text

    # Stage 1: Validation
    s1_0 = time.perf_counter()
    input_valid = isinstance(rec.id, str) and isinstance(orig_text, str)
    s1_1 = time.perf_counter()
    stage_times["1_input_validation"] += (s1_1 - s1_0)

    # Stage 2: Unicode
    s2_0 = time.perf_counter()
    norm_text, u_rep = pipeline.unicode_proc.normalize(orig_text)
    s2_1 = time.perf_counter()
    stage_times["2_unicode_normalization"] += (s2_1 - s2_0)

    # Stage 3: LID
    s3_0 = time.perf_counter()
    l_res = pipeline.lang_id.identify(norm_text)
    s3_1 = time.perf_counter()
    stage_times["3_language_identification"] += (s3_1 - s3_0)

    # Stage 4: Tanglish
    s4_0 = time.perf_counter()
    if l_res.label == "TANGLISH" and norm_text.strip():
        t_res = pipeline.tanglish_analyzer.analyze(norm_text)
    s4_1 = time.perf_counter()
    stage_times["4_tanglish_analysis"] += (s4_1 - s4_0)

    # Stage 5: Quality
    s5_0 = time.perf_counter()
    q_res = pipeline.quality_filter.evaluate(norm_text)
    s5_1 = time.perf_counter()
    stage_times["5_quality_filtering"] += (s5_1 - s5_0)

    # Stage 6: Duplicate
    s6_0 = time.perf_counter()
    if norm_text.strip():
        d_res = pipeline.dup_detector.check_and_register(rec.id, norm_text)
    s6_1 = time.perf_counter()
    stage_times["6_duplicate_detection"] += (s6_1 - s6_0)

    # Token count estimate (words * 9)
    total_tokens_estimated += len(norm_text.split()) * 9

t1_wall = time.perf_counter()
t1_proc = time.process_time()
cur_mem, peak_mem = tracemalloc.get_traced_memory()
tracemalloc.stop()

wall_time = t1_wall - t0_wall
proc_time = t1_proc - t0_proc
cpu_util = (proc_time / wall_time * 100) if wall_time > 0 else 0.0

rec_per_sec = len(all_records) / wall_time if wall_time > 0 else 0
tokens_per_sec = total_tokens_estimated / wall_time if wall_time > 0 else 0

print("=" * 60)
print(f"Total records processed: {len(all_records)}")
print(f"Wall clock time: {wall_time:.4f} s")
print(f"Process CPU time: {proc_time:.4f} s")
print(f"CPU Utilization: {cpu_util:.1f}%")
print(f"Peak Memory: {peak_mem / (1024*1024):.2f} MB")
print(f"Records / sec: {rec_per_sec:.1f}")
print(f"Tokens / sec (est): {tokens_per_sec:.1f}")
print("\nStage breakdown (seconds and %):")
total_stage_time = sum(stage_times.values())
for st, dt in sorted(stage_times.items()):
    pct = (dt / total_stage_time * 100) if total_stage_time > 0 else 0
    print(f"  {st}: {dt:.5f} s ({pct:.1f}%)")
