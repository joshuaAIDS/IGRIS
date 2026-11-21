"""
scratch/audit_hardware_clean.py

Independent Hardware & Memory Audit for IGRIS
Hardware: NVIDIA GeForce RTX 3050 6GB Laptop GPU + Intel i5-13420H + 16GB RAM
Operating Model: SOLO_DEVELOPER_OWNER_REVIEW
"""

import gc
import json
import os
import psutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

import torch
import torch.nn as nn
from torch.optim import AdamW

# Set paths
WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
sys.path.insert(0, str(PATCH_ROOT / "src"))
sys.path.insert(0, str(WORKSPACE_ROOT / "src"))

from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_production_config,
)
from igris.training.checkpoint import IgrisCheckpointManager
from igris.training.engine import TrainingConfig, IgrisTrainer
from igris.training.dataset import SequencePacker

BYTE_TO_MIB = 1.0 / (1024.0 ** 2)
BYTE_TO_MB = 1.0 / 1e6
BYTE_TO_GIB = 1.0 / (1024.0 ** 3)
BYTE_TO_GB = 1.0 / 1e9

def get_cuda_mem():
    if not torch.cuda.is_available():
        return {"allocated_bytes": 0, "allocated_mib": 0, "allocated_mb": 0,
                "reserved_bytes": 0, "reserved_mib": 0, "reserved_mb": 0,
                "free_bytes": 0, "free_mib": 0, "free_mb": 0}
    alloc = torch.cuda.memory_allocated()
    res = torch.cuda.memory_reserved()
    free_b, tot_b = torch.cuda.mem_get_info()
    return {
        "allocated_bytes": alloc,
        "allocated_mib": round(alloc * BYTE_TO_MIB, 2),
        "allocated_mb": round(alloc * BYTE_TO_MB, 2),
        "reserved_bytes": res,
        "reserved_mib": round(res * BYTE_TO_MIB, 2),
        "reserved_mb": round(res * BYTE_TO_MB, 2),
        "driver_free_bytes": free_b,
        "driver_free_mib": round(free_b * BYTE_TO_MIB, 2),
        "driver_free_mb": round(free_b * BYTE_TO_MB, 2),
    }

def get_peak_cuda_mem():
    if not torch.cuda.is_available():
        return {"max_allocated_mib": 0, "max_reserved_mib": 0}
    max_alloc = torch.cuda.max_memory_allocated()
    max_res = torch.cuda.max_memory_reserved()
    return {
        "max_allocated_bytes": max_alloc,
        "max_allocated_mib": round(max_alloc * BYTE_TO_MIB, 2),
        "max_allocated_mb": round(max_alloc * BYTE_TO_MB, 2),
        "max_reserved_bytes": max_res,
        "max_reserved_mib": round(max_res * BYTE_TO_MIB, 2),
        "max_reserved_mb": round(max_res * BYTE_TO_MB, 2),
    }

def clean_gpu():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

def run_hardware_audit():
    print("=====================================================================")
    print("         IGRIS INDEPENDENT HARDWARE & MEMORY AUDIT")
    print("=====================================================================")

    clean_gpu()
    audit_results: Dict[str, Any] = {}

    # 1. Hardware Inspection
    dev_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    props = torch.cuda.get_device_properties(0) if torch.cuda.is_available() else None
    free_b, total_b = torch.cuda.mem_get_info(0) if torch.cuda.is_available() else (0, 0)
    vm = psutil.virtual_memory()

    # Query nvidia-smi driver
    driver_version = "Unknown"
    try:
        smi_out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
            text=True
        ).strip()
        driver_version = smi_out
    except Exception:
        pass

    # Other compute processes
    compute_procs = []
    try:
        smi_proc = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"],
            text=True
        ).strip().splitlines()
        for p in smi_proc:
            if p.strip():
                compute_procs.append(p.strip())
    except Exception:
        pass

    audit_results["hardware"] = {
        "gpu_model": dev_name,
        "driver_version": driver_version,
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "pytorch_version": torch.__version__,
        "compute_capability": f"{props.major}.{props.minor}" if props else None,
        "sm_count": props.multi_processor_count if props else 0,
        "physical_vram_bytes": total_b,
        "physical_vram_mib": round(total_b * BYTE_TO_MIB, 2),
        "physical_vram_mb": round(total_b * BYTE_TO_MB, 2),
        "physical_vram_gib": round(total_b * BYTE_TO_GIB, 4),
        "physical_vram_gb": round(total_b * BYTE_TO_GB, 4),
        "initial_free_vram_bytes": free_b,
        "initial_free_vram_mib": round(free_b * BYTE_TO_MIB, 2),
        "initial_free_vram_mb": round(free_b * BYTE_TO_MB, 2),
        "os_dwm_overhead_bytes": total_b - free_b,
        "os_dwm_overhead_mib": round((total_b - free_b) * BYTE_TO_MIB, 2),
        "system_ram_total_bytes": vm.total,
        "system_ram_total_gib": round(vm.total * BYTE_TO_GIB, 2),
        "system_ram_available_bytes": vm.available,
        "system_ram_available_gib": round(vm.available * BYTE_TO_GIB, 2),
        "system_ram_percent_used": vm.percent,
        "other_compute_processes": compute_procs,
    }

    print(f"GPU: {dev_name} (Driver: {driver_version}, CUDA: {torch.version.cuda})")
    print(f"Physical VRAM: {total_b} bytes ({audit_results['hardware']['physical_vram_mib']} MiB / {audit_results['hardware']['physical_vram_gb']} GB)")
    print(f"Free VRAM: {free_b} bytes ({audit_results['hardware']['initial_free_vram_mib']} MiB)")
    print(f"OS/DWM Overhead: {audit_results['hardware']['os_dwm_overhead_mib']} MiB")
    print(f"System RAM: {audit_results['hardware']['system_ram_total_gib']} GiB (Available: {audit_results['hardware']['system_ram_available_gib']} GiB)")
    print(f"Other Compute Procs: {compute_procs}")

    # Safety limits: 15% physical headroom
    vram_15pct_headroom_bytes = int(0.15 * total_b)
    vram_safety_ceiling_bytes = free_b - vram_15pct_headroom_bytes
    audit_results["safety_limits"] = {
        "vram_15pct_headroom_bytes": vram_15pct_headroom_bytes,
        "vram_15pct_headroom_mib": round(vram_15pct_headroom_bytes * BYTE_TO_MIB, 2),
        "vram_safety_ceiling_bytes": vram_safety_ceiling_bytes,
        "vram_safety_ceiling_mib": round(vram_safety_ceiling_bytes * BYTE_TO_MIB, 2),
    }
    print(f"\n15% Physical VRAM Safety Headroom: {audit_results['safety_limits']['vram_15pct_headroom_mib']} MiB")
    print(f"CUDA Allocated Safety Ceiling: {audit_results['safety_limits']['vram_safety_ceiling_mib']} MiB")

    # 2. Forensic Phase-by-Phase Lifecycle Profiling
    print("\n--- 2. Forensic Lifecycle Profiling (igris-prod-16l) ---")
    clean_gpu()
    m_cfg = get_production_config()
    m_cfg.tie_word_embeddings = True
    m_cfg.gradient_checkpointing = True

    phases: Dict[str, Any] = {}
    phases["0_initial_clean"] = get_cuda_mem()

    # Instantiate model
    t0 = time.perf_counter()
    model = IgrisDecoderTransformer(m_cfg).to("cuda")
    model.train()
    phases["1_model_weights_instantiated"] = {
        "mem": get_cuda_mem(),
        "peak": get_peak_cuda_mem(),
        "duration_sec": round(time.perf_counter() - t0, 4),
        "param_count": sum(p.numel() for p in model.parameters()),
    }

    # Instantiate AdamW optimizer
    t0 = time.perf_counter()
    optimizer = AdamW(model.parameters(), lr=1e-4, weight_decay=0.01)
    phases["2_optimizer_instantiated"] = {
        "mem": get_cuda_mem(),
        "peak": get_peak_cuda_mem(),
        "duration_sec": round(time.perf_counter() - t0, 4),
    }

    # Generate synthetic batch (T=256, B=1)
    x = torch.randint(0, m_cfg.vocab_size, (1, 256), device="cuda", dtype=torch.long)
    y = torch.randint(0, m_cfg.vocab_size, (1, 256), device="cuda", dtype=torch.long)

    # Forward pass under autocast BF16
    clean_gpu()
    torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()
    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        out = model(x, labels=y)
        loss = out["loss"]
    phases["3_forward_pass_peak"] = {
        "mem": get_cuda_mem(),
        "peak": get_peak_cuda_mem(),
        "duration_sec": round(time.perf_counter() - t0, 4),
    }

    # Backward pass
    t0 = time.perf_counter()
    loss.backward()
    phases["4_backward_pass_peak"] = {
        "mem": get_cuda_mem(),
        "peak": get_peak_cuda_mem(),
        "duration_sec": round(time.perf_counter() - t0, 4),
    }

    # Optimizer step
    t0 = time.perf_counter()
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    phases["5_optimizer_step_peak"] = {
        "mem": get_cuda_mem(),
        "peak": get_peak_cuda_mem(),
        "duration_sec": round(time.perf_counter() - t0, 4),
    }

    # Checkpoint save
    chk_dir = WORKSPACE_ROOT / "scratch" / "audit_chk"
    chk_dir.mkdir(parents=True, exist_ok=True)
    chk_mgr = IgrisCheckpointManager(chk_dir)
    t0 = time.perf_counter()
    chk_path = chk_mgr.save_full_checkpoint(
        step=1, epoch=1, model=model, optimizer=optimizer, scheduler=None, config=m_cfg, train_loss=float(loss.item())
    )
    t_save = time.perf_counter() - t0
    chk_size_bytes = Path(chk_path).stat().st_size
    phases["6_checkpoint_save"] = {
        "mem": get_cuda_mem(),
        "peak": get_peak_cuda_mem(),
        "save_duration_sec": round(t_save, 4),
        "checkpoint_size_bytes": chk_size_bytes,
        "checkpoint_size_mib": round(chk_size_bytes * BYTE_TO_MIB, 2),
        "checkpoint_size_mb": round(chk_size_bytes * BYTE_TO_MB, 2),
    }

    # Model-only export
    t0 = time.perf_counter()
    exp_path = chk_mgr.export_model_only_checkpoint(
        model=model, config=m_cfg, output_filepath=chk_dir / "model_export.pt", step=1
    )
    t_exp = time.perf_counter() - t0
    exp_size_bytes = Path(exp_path).stat().st_size
    phases["7_model_only_export"] = {
        "mem": get_cuda_mem(),
        "export_duration_sec": round(t_exp, 4),
        "export_size_bytes": exp_size_bytes,
        "export_size_mib": round(exp_size_bytes * BYTE_TO_MIB, 2),
        "export_size_mb": round(exp_size_bytes * BYTE_TO_MB, 2),
    }

    # Checkpoint load
    t0 = time.perf_counter()
    chk_mgr.load_checkpoint(chk_path, model=model, optimizer=optimizer, expected_config=m_cfg, device=torch.device("cuda"))
    t_load = time.perf_counter() - t0
    phases["8_checkpoint_load"] = {
        "mem": get_cuda_mem(),
        "peak": get_peak_cuda_mem(),
        "load_duration_sec": round(t_load, 4),
    }

    # Cleanup temporary model & checkpoints
    del model, optimizer, loss, out, x, y
    clean_gpu()
    try:
        Path(chk_path).unlink(missing_ok=True)
        Path(exp_path).unlink(missing_ok=True)
        Path(str(chk_path).replace(".pt", ".json")).unlink(missing_ok=True)
        Path(str(exp_path).replace(".pt", ".json")).unlink(missing_ok=True)
        chk_dir.rmdir()
    except Exception:
        pass

    audit_results["lifecycle_phases"] = phases

    for pname, pdata in phases.items():
        if "mem" in pdata and "peak" in pdata:
            print(f"Phase {pname}: Alloc={pdata['mem']['allocated_mib']} MiB, PeakAlloc={pdata['peak']['max_allocated_mib']} MiB, PeakRes={pdata['peak']['max_reserved_mib']} MiB")

    # 3. Progressive Conservative Synthetic Tests Sweep
    print("\n--- 3. Progressive Conservative Configuration Sweep ---")
    test_configs = [
        {"seq_len": 256, "micro_batch": 1, "accum_steps": 2, "precision": "bf16", "name": "Conservative Baseline (T=256, B=1)"},
        {"seq_len": 512, "micro_batch": 1, "accum_steps": 2, "precision": "bf16", "name": "Safe Scaled (T=512, B=1)"},
        {"seq_len": 512, "micro_batch": 2, "accum_steps": 2, "precision": "bf16", "name": "Medium Batch (T=512, B=2)"},
        {"seq_len": 1024, "micro_batch": 1, "accum_steps": 2, "precision": "bf16", "name": "Production Context (T=1024, B=1)"},
        {"seq_len": 2048, "micro_batch": 1, "accum_steps": 2, "precision": "bf16", "name": "Extended Context (T=2048, B=1)"},
    ]

    sweep_results: List[Dict[str, Any]] = []

    for cfg in test_configs:
        clean_gpu()
        s_len = cfg["seq_len"]
        m_batch = cfg["micro_batch"]
        acc_s = cfg["accum_steps"]
        eff_tokens = s_len * m_batch * acc_s

        print(f"\nTesting Config: {cfg['name']} (SeqLen={s_len}, MicroBatch={m_batch}, Accum={acc_s}, EffTokens={eff_tokens})")

        # Setup trainer
        temp_chk = WORKSPACE_ROOT / "scratch" / f"sweep_{s_len}_{m_batch}"
        t_cfg = TrainingConfig(
            model_name="igris-prod-16l",
            max_seq_len=s_len,
            micro_batch_size=m_batch,
            gradient_accumulation_steps=acc_s,
            precision=cfg["precision"],
            activation_checkpointing=True,
            max_steps=5,
            output_dir=str(temp_chk),
        )
        m_conf = get_production_config()
        m_conf.tie_word_embeddings = True
        m_conf.max_position_embeddings = max(s_len, 2048)
        m_conf.gradient_checkpointing = True

        trainer = IgrisTrainer(config=t_cfg, model_config=m_conf)

        # Generate synthetic batches
        dummy_batches = []
        for _ in range(acc_s * 4):
            dummy_batches.append({
                "input_ids": torch.randint(0, m_conf.vocab_size, (m_batch, s_len), device="cuda"),
                "attention_mask": torch.ones((m_batch, s_len), device="cuda", dtype=torch.long),
                "labels": torch.randint(0, m_conf.vocab_size, (m_batch, s_len), device="cuda"),
            })

        # Warmup step
        trainer.train_step(dummy_batches[:acc_s], step=1)

        # Timed execution over 3 steps
        clean_gpu()
        torch.cuda.reset_peak_memory_stats()

        step_times = []
        telem_list = []
        for s in range(2, 5):
            t0 = time.perf_counter()
            t_data = trainer.train_step(dummy_batches[:acc_s], step=s)
            torch.cuda.synchronize()
            elapsed = time.perf_counter() - t0
            step_times.append(elapsed)
            telem_list.append(t_data)

        avg_step_sec = sum(step_times) / len(step_times)
        avg_steps_per_sec = 1.0 / avg_step_sec
        avg_tokens_per_sec = eff_tokens / avg_step_sec

        peak_alloc = torch.cuda.max_memory_allocated()
        peak_res = torch.cuda.max_memory_reserved()
        free_after, _ = torch.cuda.mem_get_info()
        proc_ram = psutil.Process().memory_info().rss

        headroom_bytes = free_after
        headroom_pct_physical = (headroom_bytes / total_b) * 100.0
        headroom_pct_safety = ((vram_safety_ceiling_bytes - peak_alloc) / vram_safety_ceiling_bytes) * 100.0 if vram_safety_ceiling_bytes > peak_alloc else 0.0

        is_safe = (headroom_pct_physical >= 15.0) and (peak_alloc < vram_safety_ceiling_bytes)

        sweep_entry = {
            "name": cfg["name"],
            "sequence_length": s_len,
            "micro_batch_size": m_batch,
            "accum_steps": acc_s,
            "effective_batch_tokens": eff_tokens,
            "peak_allocated_bytes": peak_alloc,
            "peak_allocated_mib": round(peak_alloc * BYTE_TO_MIB, 2),
            "peak_allocated_mb": round(peak_alloc * BYTE_TO_MB, 2),
            "peak_reserved_bytes": peak_res,
            "peak_reserved_mib": round(peak_res * BYTE_TO_MIB, 2),
            "peak_reserved_mb": round(peak_res * BYTE_TO_MB, 2),
            "driver_free_bytes": free_after,
            "driver_free_mib": round(free_after * BYTE_TO_MIB, 2),
            "host_ram_rss_bytes": proc_ram,
            "host_ram_rss_mib": round(proc_ram * BYTE_TO_MIB, 2),
            "avg_step_duration_sec": round(avg_step_sec, 4),
            "avg_steps_per_sec": round(avg_steps_per_sec, 2),
            "measured_tokens_per_sec": round(avg_tokens_per_sec, 1),
            "vram_headroom_bytes": headroom_bytes,
            "vram_headroom_mib": round(headroom_bytes * BYTE_TO_MIB, 2),
            "vram_headroom_pct_physical": round(headroom_pct_physical, 2),
            "is_safe_under_15pct_rule": is_safe,
        }
        sweep_results.append(sweep_entry)

        print(f"Allocated: {sweep_entry['peak_allocated_mib']} MiB ({sweep_entry['peak_allocated_mb']} MB)")
        print(f"Reserved: {sweep_entry['peak_reserved_mib']} MiB ({sweep_entry['peak_reserved_mb']} MB)")
        print(f"Throughput: {sweep_entry['measured_tokens_per_sec']} tokens/sec ({sweep_entry['avg_steps_per_sec']} steps/sec)")
        print(f"Physical Headroom: {sweep_entry['vram_headroom_mib']} MiB ({sweep_entry['vram_headroom_pct_physical']}%) -> SAFE: {is_safe}")

        # Cleanup
        del trainer, dummy_batches
        clean_gpu()
        try:
            for p in temp_chk.glob("*"):
                p.unlink(missing_ok=True)
            temp_chk.rmdir()
        except Exception:
            pass

    audit_results["sweep_results"] = sweep_results

    # 4. Training Time Projections
    print("\n--- 4. Training Time Projections ---")
    token_milestones = [1_000_000, 10_000_000, 50_000_000, 100_000_000]
    projections = {}

    for entry in sweep_results:
        cfg_name = entry["name"]
        tps = entry["measured_tokens_per_sec"]
        eff_tokens = entry["effective_batch_tokens"]
        cfg_projections = []

        for target_tokens in token_milestones:
            total_steps = (target_tokens + eff_tokens - 1) // eff_tokens
            est_seconds = target_tokens / max(tps, 1e-5)
            est_hours = est_seconds / 3600.0
            cfg_projections.append({
                "target_tokens": target_tokens,
                "target_tokens_label": f"{target_tokens // 1_000_000}M",
                "total_steps": total_steps,
                "estimated_seconds": round(est_seconds, 1),
                "estimated_hours": round(est_hours, 2),
                "estimated_formatted": f"{int(est_hours)}h {int((est_hours % 1) * 60)}m",
                "basis": "PROJECTION_FROM_MEASUREMENT",
                "measured_tokens_per_sec": tps,
            })
        projections[cfg_name] = cfg_projections

    audit_results["training_projections"] = projections

    # 5. Root Cause Reconciliation of Previous 6,508 MB Report
    audit_results["reconciliation"] = {
        "previous_512_tokens_allocated_mb": 5796,
        "previous_512_tokens_reserved_mb": 5996,
        "previous_1024_tokens_allocated_mb": 6221,
        "previous_1024_tokens_reserved_mb": 6508,
        "previous_2048_tokens_allocated_mb": 6097,
        "previous_2048_tokens_reserved_mb": 6508,
        "physical_vram_capacity_bytes": total_b,
        "physical_vram_capacity_mib": round(total_b * BYTE_TO_MIB, 2),
        "physical_vram_capacity_mb": round(total_b * BYTE_TO_MB, 2),
        "unit_clarification": "Previous code calculated bytes / (1024**2) and labeled it 'MB'. It was actually MiB.",
        "6508_mib_in_bytes": 6508 * (1024 ** 2),
        "6508_mib_in_decimal_mb": round((6508 * (1024 ** 2)) / 1e6, 2),
        "6508_mib_percent_of_physical_vram": round(((6508 * (1024 ** 2)) / total_b) * 100.0, 2),
        "root_cause_1": "Cumulative lingering model instances from Section 3 (evaluation) and Section 4 (checkpoint validation with 3 models: model_a, model_b, model_c) without garbage collection or torch.cuda.empty_cache().",
        "root_cause_2": "Sequential loop over configurations in Section 5 instantiated new IgrisTrainer objects without deleting prior trainers or resetting peak stats via torch.cuda.reset_peak_memory_stats().",
        "root_cause_3": "WDDM 2.x/3.x Shared GPU Memory paging. On Windows, PyTorch requests exceeding physical VRAM page out to host RAM rather than immediately throwing CUDA OOM, causing 6,824 MB to be tracked by PyTorch while thrashing PCIe bus and cratering throughput.",
        "isolated_true_allocated_mib_t512": sweep_results[1]["peak_allocated_mib"],
        "isolated_true_reserved_mib_t512": sweep_results[1]["peak_reserved_mib"],
        "isolated_true_allocated_mib_t1024": sweep_results[3]["peak_allocated_mib"],
        "isolated_true_reserved_mib_t1024": sweep_results[3]["peak_reserved_mib"],
    }

    # Save complete JSON
    out_json = WORKSPACE_ROOT / "scratch" / "hardware_audit_verified.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)
    print(f"\nAudit complete! Saved detailed results to: {out_json}")

    return audit_results

if __name__ == "__main__":
    run_hardware_audit()
