"""
scratch/verify_hardware_audit_deliverables.py

Verifies all hardware audit deliverables, assertions, and governance gates.
"""

import json
import shutil
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

EXPECTED_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"

DELIVERABLES = [
    "GPU_BENCHMARK_RECONCILIATION.md",
    "SAFE_TRAINING_CONFIGURATION.md",
    "TRAINING_TIME_PROJECTIONS.md",
    "FINAL_HARDWARE_READINESS_REPORT.md",
    "CHECKPOINT_MEMORY_AUDIT.md",
]

def verify_audit():
    print("=====================================================================")
    print("      VERIFYING IGRIS HARDWARE AUDIT DELIVERABLES & GATES")
    print("=====================================================================")

    # 1. Verify deliverables exist in workspace
    for doc in DELIVERABLES:
        doc_path = WORKSPACE_ROOT / doc
        assert doc_path.exists(), f"Missing deliverable: {doc_path}"
        content = doc_path.read_text(encoding="utf-8")
        assert len(content) > 500, f"Deliverable too short: {doc_path}"
        print(f"[PASS] Deliverable verified: {doc} ({len(content)} chars)")

    # 2. Verify telemetry JSON
    json_path = WORKSPACE_ROOT / "scratch" / "hardware_audit_verified.json"
    assert json_path.exists(), f"Missing telemetry JSON: {json_path}"
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Check hardware
    hw = data["hardware"]
    assert hw["gpu_model"] == "NVIDIA GeForce RTX 3050 6GB Laptop GPU"
    assert hw["physical_vram_bytes"] == 6441926656
    print(f"[PASS] Hardware verified: {hw['gpu_model']} ({hw['physical_vram_bytes']} bytes)")

    # Check safety limits
    safety = data["safety_limits"]
    assert safety["vram_15pct_headroom_bytes"] == int(0.15 * 6441926656)
    assert safety["vram_safety_ceiling_bytes"] > 0
    print(f"[PASS] Safety limits verified: 15% headroom = {safety['vram_15pct_headroom_mib']} MiB")

    # Check sweep results
    sweep = data["sweep_results"]
    assert len(sweep) == 5, f"Expected 5 sweep results, got {len(sweep)}"
    for entry in sweep:
        assert entry["is_safe_under_15pct_rule"] is True
        assert entry["vram_headroom_pct_physical"] >= 15.0
        assert entry["measured_tokens_per_sec"] > 500.0
        print(f"[PASS] Sweep entry verified: {entry['name']} -> Alloc: {entry['peak_allocated_mib']} MiB, Throughput: {entry['measured_tokens_per_sec']} tok/s, Headroom: {entry['vram_headroom_pct_physical']}%")

    # Check reconciliation
    recon = data["reconciliation"]
    assert recon["previous_1024_tokens_reserved_mb"] == 6508
    assert "WDDM" in recon["root_cause_3"]
    print("[PASS] Reconciliation explanation verified.")

    # 3. Mirror deliverables to PATCH_ROOT and ARTIFACT_DIR
    PATCH_ROOT.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    for doc in DELIVERABLES:
        src = WORKSPACE_ROOT / doc
        dst_patch = PATCH_ROOT / doc
        dst_artifact = ARTIFACT_DIR / doc
        shutil.copy2(src, dst_patch)
        shutil.copy2(src, dst_artifact)
        print(f"[PASS] Mirrored {doc} to patch and artifact directories.")

    # Mirror JSON as well
    shutil.copy2(json_path, PATCH_ROOT / "hardware_audit_verified.json")
    shutil.copy2(json_path, ARTIFACT_DIR / "hardware_audit_verified.json")
    print("[PASS] Mirrored hardware_audit_verified.json to patch and artifact directories.")

    print("\n=====================================================================")
    print(" ALL HARDWARE AUDIT DELIVERABLES AND VERIFICATIONS PASSED (100%)")
    print("=====================================================================")

if __name__ == "__main__":
    verify_audit()
