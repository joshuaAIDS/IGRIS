"""
scratch/run_task2_reproduction.py

Runs the 4 test commands required by Phase 21B3E Task 2:
1. Repository-wide pytest collection
2. Repository-wide pytest execution
3. Readiness tests independently
4. Acquisition security tests independently

Captures raw output, exit codes, and durations.
"""

import sys
import os
import subprocess
import time

CWD = r"C:\IGRIS"
TESTS_DIR = r"igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests"

results = {}

# 1. Repository-wide pytest collection
print("1. Running repository-wide pytest collection...")
t0 = time.time()
cmd1 = [sys.executable, "-m", "pytest", TESTS_DIR, "--collect-only"]
res1 = subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=CWD)
dur1 = time.time() - t0
results["collection"] = {
    "cmd": "pytest igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests --collect-only",
    "exit_code": res1.returncode,
    "duration": dur1,
    "output": res1.stdout
}
print(f"Collection finished in {dur1:.2f}s (Exit Code: {res1.returncode})")

# 2. Repository-wide pytest execution
print("2. Running repository-wide pytest execution...")
t0 = time.time()
cmd2 = [sys.executable, "-m", "pytest", TESTS_DIR, "-v"]
res2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=CWD)
dur2 = time.time() - t0
results["full_execution"] = {
    "cmd": "pytest igris_3b52_production_tokenizer_patch/igris_3b52_patch/tests -v",
    "exit_code": res2.returncode,
    "duration": dur2,
    "output": res2.stdout
}
print(f"Full execution finished in {dur2:.2f}s (Exit Code: {res2.returncode})")

# 3. Readiness tests independently
print("3. Running readiness tests independently...")
t0 = time.time()
cmd3 = [sys.executable, "-m", "pytest", f"{TESTS_DIR}/test_readiness.py", "-v"]
res3 = subprocess.run(cmd3, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=CWD)
dur3 = time.time() - t0
results["readiness"] = {
    "cmd": f"pytest {TESTS_DIR}/test_readiness.py -v",
    "exit_code": res3.returncode,
    "duration": dur3,
    "output": res3.stdout
}
print(f"Readiness tests finished in {dur3:.2f}s (Exit Code: {res3.returncode})")

# 4. Acquisition security tests independently
print("4. Running acquisition security tests independently...")
acq_files = [
    f"{TESTS_DIR}/test_phase12_acquisition_security.py",
    f"{TESTS_DIR}/test_phase13_controlled_acquisition.py",
    f"{TESTS_DIR}/test_phase20_final_readiness.py",
    f"{TESTS_DIR}/test_phase20b_consistency_verification.py",
    f"{TESTS_DIR}/test_phase21_controlled_dataset_preparation.py",
    f"{TESTS_DIR}/test_phase21a_tokenizer_selection_and_dataset_review.py"
]
t0 = time.time()
cmd4 = [sys.executable, "-m", "pytest"] + acq_files + ["-v"]
res4 = subprocess.run(cmd4, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=CWD)
dur4 = time.time() - t0
results["acquisition_security"] = {
    "cmd": f"pytest {' '.join(acq_files)} -v",
    "exit_code": res4.returncode,
    "duration": dur4,
    "output": res4.stdout
}
print(f"Acquisition security tests finished in {dur4:.2f}s (Exit Code: {res4.returncode})")

import json
# Save raw results dictionary summary to scratch/reproduction_summary.json
with open(r"C:\IGRIS\scratch\reproduction_summary.json", "w", encoding="utf-8") as f:
    json.dump({
        k: {
            "cmd": v["cmd"],
            "exit_code": v["exit_code"],
            "duration": v["duration"],
            "output_len": len(v["output"])
        } for k, v in results.items()
    }, f, indent=2)

# Save collection output
with open(r"C:\IGRIS\scratch\collection_raw.txt", "w", encoding="utf-8") as f:
    f.write(results["collection"]["output"])

# Save full results output
with open(r"C:\IGRIS\scratch\full_results_raw.txt", "w", encoding="utf-8") as f:
    f.write(results["full_execution"]["output"])

# Save readiness output
with open(r"C:\IGRIS\scratch\readiness_raw.txt", "w", encoding="utf-8") as f:
    f.write(results["readiness"]["output"])

# Save acquisition security output
with open(r"C:\IGRIS\scratch\acquisition_security_raw.txt", "w", encoding="utf-8") as f:
    f.write(results["acquisition_security"]["output"])

print("All reproduction runs finished and raw files saved to scratch/.")
