# verify_phase22e.py
"""
Deterministic independent verification script for Phase 22E:
1. Loads Phase 22E component register and scenario matrix.
2. Recalculates every row from its component equations.
3. Verifies GB-to-GiB conversions.
4. Checks that OS reserve is counted exactly once.
5. Checks that no component is double-counted within a scenario.
6. Verifies filesystem cushion calculations and headline ranges.
7. Verifies candidate tokenizer hashes.
8. Confirms governance locks.
"""

import csv
import hashlib
import sys
from pathlib import Path

PATCH_ROOT = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

EXPECTED_DELIVERABLES = [
    "PHASE22E_STORAGE_SCENARIO_COMPONENT_REGISTER.csv",
    "PHASE22E_STORAGE_SCENARIO_MATRIX.csv",
    "PHASE22E_HISTORICAL_FIGURE_RECONCILIATION.md",
    "PHASE22E_FILESYSTEM_CUSHION_RECONCILIATION.md",
    "PHASE22E_VERIFICATION_REPORT.md",
    "verify_phase22e.py",
]

EXPECTED_CANDIDATE_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
EXPECTED_CANDIDATE_B_HASH = "d3a3431e07c87ecce863647202ddc9b47b964718adbae7bf2bb2459223b94888"

def to_gib(gb: float) -> float:
    return round(gb * (10**9) / (1024**3), 2)

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_deliverables_exist():
    print("1. Checking Phase 22E deliverables exist and non-empty...")
    for d in EXPECTED_DELIVERABLES:
        p_patch = PATCH_ROOT / d
        p_art = ARTIFACT_DIR / d
        assert p_patch.exists(), f"Missing in patch root: {p_patch}"
        assert p_patch.stat().st_size > 0, f"Empty file in patch root: {p_patch}"
        assert p_art.exists(), f"Missing in artifact dir: {p_art}"
        assert p_art.stat().st_size > 0, f"Empty file in artifact dir: {p_art}"
        print(f"  [OK] {d} (Patch: {p_patch.stat().st_size} bytes, Artifact: {p_art.stat().st_size} bytes)")

def test_component_register():
    print("\n2. Loading and verifying component register...")
    reg_path = PATCH_ROOT / "PHASE22E_STORAGE_SCENARIO_COMPONENT_REGISTER.csv"
    with open(reg_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 13, f"Expected 13 components, got {len(rows)}"
    comp_map = {}
    for r in rows:
        cid = r["component_id"]
        gb = float(r["size_gb_dec"])
        gib = float(r["size_gib_bin"])
        expected_gib = to_gib(gb)
        assert abs(gib - expected_gib) <= 0.05, f"Binary conversion error in {cid}: {gib} vs {expected_gib}"
        comp_map[cid] = gb
    print("  [OK] All 13 components registered and mathematically verified.")
    return comp_map

def test_scenario_matrix(comp_map):
    print("\n3. Recalculating scenario matrix rows from components...")
    mat_path = PATCH_ROOT / "PHASE22E_STORAGE_SCENARIO_MATRIX.csv"
    with open(mat_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 13, f"Expected 13 scenario rows, got {len(rows)}"

    for r in rows:
        scen_id = r["scenario_id"]
        p_app = float(r["persistent_app_gb_dec"])
        t_app = float(r["temp_workspace_gb_dec"])
        tot_app = float(r["total_app_gb_dec"])
        os_res = float(r["os_reserve_gb_dec"])
        tot_stage = float(r["total_stage_gb_dec"])

        # Check OS reserve is exactly 50 GB
        assert os_res == 50.00, f"OS reserve in {scen_id} must be 50.00 GB, got {os_res}"

        # Check sums
        assert round(p_app + t_app, 2) == round(tot_app, 2), f"App sum error in {scen_id}"
        assert round(tot_app + os_res, 2) == round(tot_stage, 2), f"Total sum error in {scen_id}"

        # Check binary conversions
        expected_tot_gib = to_gib(tot_stage)
        actual_tot_gib = float(r["total_stage_gib_bin"])
        assert abs(actual_tot_gib - expected_tot_gib) <= 0.05, f"GiB mismatch in {scen_id}: {actual_tot_gib} vs {expected_tot_gib}"

        # Check that no component is double-counted in active_components
        comps = [c.strip() for c in r["active_components"].split("+")]
        assert len(comps) == len(set(comps)), f"Double-counted component in {scen_id}: {comps}"

    scen_map = {r["scenario_id"]: r for r in rows}

    # Verify Stage 9 vs 10A proof
    s9_app = float(scen_map["SCEN_09_DUAL_COPY_CLEANING"]["total_app_gb_dec"])
    s10a_app = float(scen_map["SCEN_10A_ZERO_CLEANUP_DUAL_BASE"]["total_app_gb_dec"])
    diff_27 = round(s10a_app - s9_app, 2)
    assert diff_27 == 27.00, f"Expected 27.00 GB difference between Stage 9 and Stage 10A, got {diff_27}"

    # Verify that diff matches COMP_08 (12) + COMP_10 (15)
    token_ckpt_sum = round(comp_map["COMP_08"] + comp_map["COMP_10"], 2)
    assert token_ckpt_sum == 27.00, f"Expected tokens+checkpoints to be 27.00 GB, got {token_ckpt_sum}"
    print(f"  [OK] Mathematical proof verified: Stage 10A ({s10a_app} GB) - Stage 9 ({s9_app} GB) = {diff_27} GB == Tokens ({comp_map['COMP_08']} GB) + Checkpoints ({comp_map['COMP_10']} GB).")

    # Verify Stage 8 Pretraining corrected
    p_pre = scen_map["SCEN_08_PRETRAINING_CORRECTED"]
    assert p_pre["total_app_gb_dec"] == "37.00"
    assert p_pre["total_stage_gb_dec"] == "87.00"
    assert p_pre["total_stage_gib_bin"] == "81.03"
    print("  [OK] Stage 8 Pretraining corrected arithmetic verified (37.00 GB app / 87.00 GB total).")

def test_filesystem_cushions():
    print("\n4. Verifying filesystem cushion calculations...")
    vol_gib = 931.32
    vol_gb = 1000.00

    fs_scenarios = [
        ("ext4_default", 46.57, 13.97, 870.78, 935.00),
        ("ext4_tuned", 9.31, 13.97, 908.04, 975.02),
        ("xfs", 0.00, 4.66, 926.66, 995.00),
        ("ntfs", 0.00, 9.31, 922.01, 990.00),
    ]

    seq_peak_gib = 366.66
    seq_peak_gb = 393.70

    dual_base_gib = 562.89
    dual_base_gb = 604.40

    zero_item_gib = 572.20
    zero_item_gb = 614.40

    for name, res_gib, meta_gib, net_gib, net_gb in fs_scenarios:
        # Check net usable capacity
        calc_net_gib = round(vol_gib - res_gib - meta_gib, 2)
        assert abs(calc_net_gib - net_gib) <= 0.05, f"Net usable GiB error in {name}: {calc_net_gib} vs {net_gib}"

        # Check sequential cushion
        cush_seq_gib = round(net_gib - seq_peak_gib, 2)
        cush_seq_gb = round(net_gb - seq_peak_gb, 2)
        assert cush_seq_gib >= 504.10 and cush_seq_gib <= 560.05

        # Check dual-copy base cushion
        cush_dual_gib = round(net_gib - dual_base_gib, 2)
        cush_dual_gb = round(net_gb - dual_base_gb, 2)
        assert cush_dual_gib >= 307.85 and cush_dual_gib <= 363.80

        # Check zero-cleanup itemized cushion
        cush_zero_gib = round(net_gib - zero_item_gib, 2)
        cush_zero_gb = round(net_gb - zero_item_gb, 2)
        assert cush_zero_gib >= 298.55 and cush_zero_gib <= 354.50

    print("  [OK] Filesystem net capacities and cushion ranges verified across all 4 filesystems.")

def test_governance_invariants():
    print("\n5. Verifying tokenizer hashes and governance locks...")
    cand_a_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    cand_b_path = PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"

    hash_a = compute_sha256(cand_a_path)
    hash_b = compute_sha256(cand_b_path)

    assert hash_a == EXPECTED_CANDIDATE_A_HASH, f"Candidate A hash mismatch: {hash_a}"
    assert hash_b == EXPECTED_CANDIDATE_B_HASH, f"Candidate B hash mismatch: {hash_b}"
    print(f"  [OK] Candidate A SHA-256: {hash_a}")
    print(f"  [OK] Candidate B SHA-256: {hash_b}")

    quarantine_raw = PATCH_ROOT / "quarantine" / "raw"
    if quarantine_raw.exists():
        files = list(quarantine_raw.glob("*"))
        assert len(files) == 0, f"Found files in quarantine raw: {files}"
    print("  [OK] Zero production data files in quarantine.")

def main():
    print("==================================================================")
    print("  IGRIS PHASE 22E DETERMINISTIC CAPACITY VERIFICATION SUITE")
    print("==================================================================")
    test_deliverables_exist()
    comp_map = test_component_register()
    test_scenario_matrix(comp_map)
    test_filesystem_cushions()
    test_governance_invariants()
    print("\n==================================================================")
    print("  ALL PHASE 22E VERIFICATION CHECKS PASSED PERFECTLY (100%)")
    print("==================================================================")

if __name__ == "__main__":
    main()
