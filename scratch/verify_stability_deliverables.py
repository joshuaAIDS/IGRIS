"""
scratch/verify_stability_deliverables.py

Verifies the 3 final deliverables and mirrors them to patch and artifact roots.
"""

import json
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

DELIVERABLES = [
    "FINAL_BENCHMARK_RECONCILIATION.md",
    "VERIFIED_SYNTHETIC_TRAINING_CONFIGURATION.md",
    "HARDWARE_STABILITY_RESULTS.md",
]

def verify_and_mirror():
    print("=====================================================================")
    print("      VERIFYING FINAL STABILITY DELIVERABLES & MIRRORING")
    print("=====================================================================")

    # 1. Check deliverables exist
    for doc in DELIVERABLES:
        doc_path = WORKSPACE_ROOT / doc
        assert doc_path.exists(), f"Missing deliverable: {doc_path}"
        txt = doc_path.read_text(encoding="utf-8")
        assert len(txt) > 1000, f"Deliverable too short: {doc_path}"
        print(f"[PASS] {doc} exists and contains {len(txt)} chars.")

    # 2. Check JSON
    json_path = WORKSPACE_ROOT / "scratch" / "stability_audit_verified.json"
    assert json_path.exists(), f"Missing {json_path}"
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    cfgs = data["configurations"]
    assert "CONFIG_A" in cfgs and "CONFIG_B" in cfgs and "CONFIG_C" in cfgs
    assert data["checkpoint_recovery_audit"]["checkpoint_bit_exact_recovery"] is True
    assert data["checkpoint_recovery_audit"]["max_loss_difference"] < 1e-6
    print("[PASS] stability_audit_verified.json validated.")

    # 3. Mirror files
    PATCH_ROOT.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    for doc in DELIVERABLES:
        shutil.copy2(WORKSPACE_ROOT / doc, PATCH_ROOT / doc)
        shutil.copy2(WORKSPACE_ROOT / doc, ARTIFACT_DIR / doc)
        print(f"[PASS] Mirrored {doc} to patch and artifact directories.")

    shutil.copy2(json_path, PATCH_ROOT / "stability_audit_verified.json")
    shutil.copy2(json_path, ARTIFACT_DIR / "stability_audit_verified.json")
    print("[PASS] Mirrored stability_audit_verified.json to patch and artifact directories.")

    print("\n=====================================================================")
    print(" ALL 3 DELIVERABLES AND AUDIT JSON VERIFIED AND MIRRORED (100%)")
    print("=====================================================================")

if __name__ == "__main__":
    verify_and_mirror()
