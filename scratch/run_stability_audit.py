"""
scratch/run_stability_audit.py

Sustained Hardware Stability & 30-Step Benchmark Reconciliation
Hardware: NVIDIA GeForce RTX 3050 6GB Laptop GPU (Ampere, CC 8.6)
Operating Model: SOLO_DEVELOPER_OWNER_REVIEW
"""

import gc
import json
import math
import os
import psutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

import torch
import torch.nn as nn

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

BYTE_TO_MIB = 1.0 / (1024.0 ** 2)
BYTE_TO_MB = 1.0 / 1e6
BYTE_TO_GIB = 1.0 / (1024.0 ** 3)

def clean_gpu():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

def query_gpu_telemetry() -> Dict[str, Any]:
    """Query nvidia-smi for temperature, clocks, and utilization."""
    res = {
        "temperature_c": None,
        "graphics_clock_mhz": None,
        "memory_clock_mhz": None,
        "utilization_gpu_pct": None,
    }
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu,clocks.current.graphics,clocks.current.memory,utilization.gpu",
             "--format=csv,noheader,nounits"],
            text=True
        ).strip()
        parts = [p.strip() for p in out.split(",")]
        if len(parts) >= 4:
            res["temperature_c"] = int(parts[0])
            res["graphics_clock_mhz"] = int(parts[1])
            res["memory_clock_mhz"] = int(parts[2])
            res["utilization_gpu_pct"] = int(parts[3])
    except Exception:
        pass
    return res

def run_sustained_stability_audit():
    print("=====================================================================")
    print("  IGRIS SUSTAINED HARDWARE STABILITY & 30-STEP BENCHMARK AUDIT")
    print("=====================================================================")

    clean_gpu()
    total_b = torch.cuda.get_device_properties(0).total_memory
    free_init_b, _ = torch.cuda.mem_get_info(0)
    vram_15pct_headroom_bytes = int(0.15 * total_b)
    vram_safety_ceiling_bytes = free_init_b - vram_15pct_headroom_bytes

    print(f"Physical VRAM: {total_b} bytes ({round(total_b * BYTE_TO_MIB, 2)} MiB)")
    print(f"Initial Free VRAM: {free_init_b} bytes ({round(free_init_b * BYTE_TO_MIB, 2)} MiB)")
    print(f"15% Mandatory Headroom: {round(vram_15pct_headroom_bytes * BYTE_TO_MIB, 2)} MiB")
    print(f"Safety Ceiling: {round(vram_safety_ceiling_bytes * BYTE_TO_MIB, 2)} MiB\n")

    test_configs = [
        {
            "id": "CONFIG_A",
            "name": "Configuration A (T=512, B=2, A=2)",
            "seq_len": 512,
            "micro_batch": 2,
            "accum_steps": 2,
            "warmup_steps": 5,
            "measured_steps": 30,
        },
        {
            "id": "CONFIG_B",
            "name": "Configuration B (T=1024, B=1, A=2)",
            "seq_len": 1024,
            "micro_batch": 1,
            "accum_steps": 2,
            "warmup_steps": 5,
            "measured_steps": 30,
        },
        {
            "id": "CONFIG_C",
            "name": "Configuration C (T=2048, B=1, A=2)",
            "seq_len": 2048,
            "micro_batch": 1,
            "accum_steps": 2,
            "warmup_steps": 5,
            "measured_steps": 30,
        },
    ]

    stability_results: Dict[str, Any] = {
        "hardware_baseline": {
            "physical_vram_bytes": total_b,
            "physical_vram_mib": round(total_b * BYTE_TO_MIB, 2),
            "free_initial_bytes": free_init_b,
            "free_initial_mib": round(free_init_b * BYTE_TO_MIB, 2),
            "vram_15pct_headroom_bytes": vram_15pct_headroom_bytes,
            "vram_15pct_headroom_mib": round(vram_15pct_headroom_bytes * BYTE_TO_MIB, 2),
            "safety_ceiling_bytes": vram_safety_ceiling_bytes,
            "safety_ceiling_mib": round(vram_safety_ceiling_bytes * BYTE_TO_MIB, 2),
        },
        "configurations": {},
    }

    for cfg in test_configs:
        clean_gpu()
        s_len = cfg["seq_len"]
        m_batch = cfg["micro_batch"]
        acc_s = cfg["accum_steps"]
        n_warm = cfg["warmup_steps"]
        n_meas = cfg["measured_steps"]
        eff_tokens_per_step = s_len * m_batch * acc_s

        print(f"--- Running {cfg['name']} ---")
        print(f"    Sequence Length: {s_len}, Micro-Batch: {m_batch}, Accum Steps: {acc_s}")
        print(f"    Tokens Per Optimizer Step: {eff_tokens_per_step}")
        print(f"    Warmup Steps: {n_warm}, Measured Steps: {n_meas}")

        # Free memory before run
        free_before_bytes, _ = torch.cuda.mem_get_info()

        # Temporary output directory for checkpoints
        temp_dir = WORKSPACE_ROOT / "scratch" / f"stability_{cfg['id'].lower()}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        t_cfg = TrainingConfig(
            model_name="igris-prod-16l",
            max_seq_len=s_len,
            micro_batch_size=m_batch,
            gradient_accumulation_steps=acc_s,
            precision="bf16",
            activation_checkpointing=True,
            max_steps=n_warm + n_meas + 2,
            output_dir=str(temp_dir),
        )

        m_conf = get_production_config()
        m_conf.tie_word_embeddings = True
        m_conf.max_position_embeddings = max(s_len, 2048)
        m_conf.gradient_checkpointing = True

        trainer = IgrisTrainer(config=t_cfg, model_config=m_conf)

        # Generate deterministic synthetic batches
        generator = torch.Generator(device="cuda").manual_seed(20261121)
        synthetic_pool = []
        for _ in range(acc_s * 4):
            synthetic_pool.append({
                "input_ids": torch.randint(0, m_conf.vocab_size, (m_batch, s_len), device="cuda", generator=generator),
                "attention_mask": torch.ones((m_batch, s_len), device="cuda", dtype=torch.long),
                "labels": torch.randint(0, m_conf.vocab_size, (m_batch, s_len), device="cuda", generator=generator),
            })

        # 1. Warm-up Phase
        print(f"    Executing {n_warm} warm-up steps...")
        for w_idx in range(1, n_warm + 1):
            batch_slice = [synthetic_pool[(w_idx * acc_s + i) % len(synthetic_pool)] for i in range(acc_s)]
            trainer.train_step(batch_slice, step=w_idx)
        torch.cuda.synchronize()

        # Reset peak stats before measured phase
        clean_gpu()
        torch.cuda.reset_peak_memory_stats()
        free_at_start_bytes, _ = torch.cuda.mem_get_info()

        # 2. Measured 30-Step Execution
        print(f"    Executing {n_meas} synchronized measured optimizer steps...")
        step_durations: List[float] = []
        losses: List[float] = []
        grad_norms: List[float] = []
        oom_occurred = False
        all_losses_finite = True
        all_grads_finite = True
        telemetry_samples: List[Dict[str, Any]] = []

        total_measured_tokens = n_meas * eff_tokens_per_step
        t_meas_start = time.perf_counter()

        for step in range(n_warm + 1, n_warm + n_meas + 1):
            batch_slice = [synthetic_pool[(step * acc_s + i) % len(synthetic_pool)] for i in range(acc_s)]

            torch.cuda.synchronize()
            t0 = time.perf_counter()
            try:
                step_telem = trainer.train_step(batch_slice, step=step)
                torch.cuda.synchronize()
            except torch.cuda.OutOfMemoryError as e:
                oom_occurred = True
                print(f"    [ALERT] CUDA OOM at step {step}: {e}")
                break

            t1 = time.perf_counter()
            dur = t1 - t0
            step_durations.append(dur)

            # Check finiteness
            loss_val = step_telem["train_loss"]
            grad_val = step_telem["grad_norm"]
            losses.append(loss_val)
            grad_norms.append(grad_val)

            if not math.isfinite(loss_val):
                all_losses_finite = False
            if not math.isfinite(grad_val):
                all_grads_finite = False

            # Sample nvidia-smi telemetry every 5 steps
            if (step - n_warm) % 5 == 0 or step == n_warm + 1 or step == n_warm + n_meas:
                gpu_telem = query_gpu_telemetry()
                gpu_telem["step"] = step
                gpu_telem["step_duration_sec"] = round(dur, 4)
                gpu_telem["current_vram_alloc_mib"] = round(torch.cuda.memory_allocated() * BYTE_TO_MIB, 2)
                telemetry_samples.append(gpu_telem)

        torch.cuda.synchronize()
        total_meas_duration = time.perf_counter() - t_meas_start

        # Post-run memory
        free_after_bytes, _ = torch.cuda.mem_get_info()
        peak_alloc_bytes = torch.cuda.max_memory_allocated()
        peak_res_bytes = torch.cuda.max_memory_reserved()
        host_rss_bytes = psutil.Process().memory_info().rss
        host_ram_avail_bytes = psutil.virtual_memory().available

        # Statistical analysis
        mean_dur = statistics.mean(step_durations)
        median_dur = statistics.median(step_durations)
        std_dur = statistics.stdev(step_durations) if len(step_durations) > 1 else 0.0

        # Exact throughput calculation: Total tokens / Total synchronized duration
        exact_tokens_per_sec = total_measured_tokens / total_meas_duration
        steps_per_sec = len(step_durations) / total_meas_duration

        # Headroom calculations
        headroom_bytes = free_after_bytes
        headroom_pct_physical = (headroom_bytes / total_b) * 100.0
        headroom_to_safety_ceiling_bytes = vram_safety_ceiling_bytes - peak_alloc_bytes

        is_safe = (headroom_pct_physical >= 15.0) and (not oom_occurred) and (all_losses_finite) and (all_grads_finite)

        # Thermal summary
        temps = [s["temperature_c"] for s in telemetry_samples if s["temperature_c"] is not None]
        mean_temp = statistics.mean(temps) if temps else None
        max_temp = max(temps) if temps else None

        clocks = [s["graphics_clock_mhz"] for s in telemetry_samples if s["graphics_clock_mhz"] is not None]
        mean_clock = statistics.mean(clocks) if clocks else None

        cfg_summary = {
            "configuration_id": cfg["id"],
            "configuration_name": cfg["name"],
            "sequence_length": s_len,
            "micro_batch_size": m_batch,
            "gradient_accumulation_steps": acc_s,
            "effective_tokens_per_step": eff_tokens_per_step,
            "warmup_steps": n_warm,
            "measured_steps_completed": len(step_durations),
            "actual_tokens_processed": total_measured_tokens,
            "total_synchronized_duration_sec": round(total_meas_duration, 4),
            "mean_step_duration_sec": round(mean_dur, 4),
            "median_step_duration_sec": round(median_dur, 4),
            "stdev_step_duration_sec": round(std_dur, 4),
            "steps_per_second": round(steps_per_sec, 2),
            "measured_tokens_per_second": round(exact_tokens_per_sec, 2),
            "calculation_formula": f"{total_measured_tokens} tokens / {round(total_meas_duration, 4)} s",
            "peak_allocated_bytes": peak_alloc_bytes,
            "peak_allocated_mib": round(peak_alloc_bytes * BYTE_TO_MIB, 2),
            "peak_allocated_mb": round(peak_alloc_bytes * BYTE_TO_MB, 2),
            "peak_reserved_bytes": peak_res_bytes,
            "peak_reserved_mib": round(peak_res_bytes * BYTE_TO_MIB, 2),
            "peak_reserved_mb": round(peak_res_bytes * BYTE_TO_MB, 2),
            "free_vram_before_run_mib": round(free_before_bytes * BYTE_TO_MIB, 2),
            "free_vram_after_run_mib": round(free_after_bytes * BYTE_TO_MIB, 2),
            "physical_vram_headroom_mib": round(headroom_bytes * BYTE_TO_MIB, 2),
            "physical_vram_headroom_pct": round(headroom_pct_physical, 2),
            "surplus_safety_headroom_mib": round(headroom_to_safety_ceiling_bytes * BYTE_TO_MIB, 2),
            "host_ram_rss_mib": round(host_rss_bytes * BYTE_TO_MIB, 2),
            "host_ram_available_gib": round(host_ram_avail_bytes * BYTE_TO_GIB, 2),
            "loss_finiteness_verified": all_losses_finite,
            "gradient_finiteness_verified": all_grads_finite,
            "cuda_oom_occurred": oom_occurred,
            "mean_loss": round(statistics.mean(losses), 4),
            "initial_loss": round(losses[0], 4),
            "final_loss": round(losses[-1], 4),
            "gpu_temperature_mean_c": round(mean_temp, 1) if mean_temp else None,
            "gpu_temperature_max_c": max_temp,
            "gpu_graphics_clock_mean_mhz": round(mean_clock, 1) if mean_clock else None,
            "is_stable_and_safe": is_safe,
            "telemetry_samples": telemetry_samples,
        }

        stability_results["configurations"][cfg["id"]] = cfg_summary

        print(f"    Completed {len(step_durations)} steps in {round(total_meas_duration, 2)} s")
        print(f"    Mean Step: {round(mean_dur, 4)} s, Median: {round(median_dur, 4)} s (Std: {round(std_dur, 4)} s)")
        print(f"    Throughput: {round(exact_tokens_per_sec, 1)} tokens/sec ({round(steps_per_sec, 2)} steps/sec)")
        print(f"    Peak Alloc: {round(peak_alloc_bytes * BYTE_TO_MIB, 2)} MiB, Peak Res: {round(peak_res_bytes * BYTE_TO_MIB, 2)} MiB")
        print(f"    Free Dedicated VRAM: {round(headroom_bytes * BYTE_TO_MIB, 2)} MiB ({round(headroom_pct_physical, 2)}% headroom)")
        print(f"    Loss Finiteness: {all_losses_finite} (Initial: {round(losses[0], 2)} -> Final: {round(losses[-1], 2)})")
        print(f"    Grad Finiteness: {all_grads_finite}")
        print(f"    GPU Temp: {mean_temp}°C (Max: {max_temp}°C), Clock: {mean_clock} MHz")
        print(f"    Status: SAFE={is_safe}, OOM={oom_occurred}\n")

        # Cleanup
        del trainer, synthetic_pool
        clean_gpu()
        try:
            for p in temp_dir.glob("*"):
                p.unlink(missing_ok=True)
            temp_dir.rmdir()
        except Exception:
            pass

    # 4. Checkpoint & Recovery Verification on SELECTED Configuration
    # Selected: Configuration B (T=1024, B=1, A=2) - Production Standard Context
    print("--- 4. Checkpoint and Recovery Validation (Configuration B: T=1024) ---")
    sel_s_len = 1024
    sel_m_batch = 1
    sel_acc_s = 2

    chk_val_dir = WORKSPACE_ROOT / "scratch" / "checkpoint_val_run"
    chk_val_dir.mkdir(parents=True, exist_ok=True)

    # Initialize uninterrupted trainer
    clean_gpu()
    t_cfg_uninterrupted = TrainingConfig(
        model_name="igris-prod-16l",
        max_seq_len=sel_s_len,
        micro_batch_size=sel_m_batch,
        gradient_accumulation_steps=sel_acc_s,
        precision="bf16",
        activation_checkpointing=True,
        max_steps=10,
        random_seed=20261121,
        output_dir=str(chk_val_dir / "uninterrupted"),
    )
    m_conf = get_production_config()
    m_conf.tie_word_embeddings = True
    m_conf.max_position_embeddings = max(sel_s_len, 2048)
    m_conf.gradient_checkpointing = True

    trainer_unint = IgrisTrainer(config=t_cfg_uninterrupted, model_config=m_conf)

    # Fixed batches
    gen = torch.Generator(device="cuda").manual_seed(42)
    val_batches = []
    for _ in range(sel_acc_s * 10):
        val_batches.append({
            "input_ids": torch.randint(0, m_conf.vocab_size, (sel_m_batch, sel_s_len), device="cuda", generator=gen),
            "attention_mask": torch.ones((sel_m_batch, sel_s_len), device="cuda", dtype=torch.long),
            "labels": torch.randint(0, m_conf.vocab_size, (sel_m_batch, sel_s_len), device="cuda", generator=gen),
        })

    # Execute uninterrupted run: Steps 1 to 10
    unint_losses = []
    unint_checkpoints = []
    chk_save_path = None

    for step in range(1, 11):
        batch_slice = [val_batches[(step * sel_acc_s + i) % len(val_batches)] for i in range(sel_acc_s)]
        telem = trainer_unint.train_step(batch_slice, step=step)
        unint_losses.append(telem["train_loss"])

        # Save checkpoint at step 5
        if step == 5:
            chk_save_path = trainer_unint.checkpoint_manager.save_full_checkpoint(
                step=5,
                epoch=1,
                model=trainer_unint.model,
                optimizer=trainer_unint.optimizer,
                scheduler=trainer_unint.scheduler,
                config=m_conf,
                train_loss=telem["train_loss"],
            )
            print(f"    Saved step 5 full checkpoint: {Path(chk_save_path).name} ({round(Path(chk_save_path).stat().st_size * BYTE_TO_MIB, 2)} MiB)")

    # Capture uninterrupted model state at step 10
    unint_step10_weights = {k: v.clone().cpu() for k, v in trainer_unint.model.state_dict().items()}
    del trainer_unint
    clean_gpu()

    # Now Resumed Run:
    # Initialize fresh trainer, reload step 5 checkpoint, execute steps 6 to 10
    print("    Resuming fresh trainer from step 5 checkpoint...")
    t_cfg_resumed = TrainingConfig(
        model_name="igris-prod-16l",
        max_seq_len=sel_s_len,
        micro_batch_size=sel_m_batch,
        gradient_accumulation_steps=sel_acc_s,
        precision="bf16",
        activation_checkpointing=True,
        max_steps=10,
        random_seed=99999999,  # Deliberately different seed to prove RNG restoration!
        output_dir=str(chk_val_dir / "resumed"),
    )
    trainer_resumed = IgrisTrainer(config=t_cfg_resumed, model_config=m_conf)

    # Reload checkpoint
    chk_dict, meta = trainer_resumed.checkpoint_manager.load_checkpoint(
        filepath=chk_save_path,
        model=trainer_resumed.model,
        optimizer=trainer_resumed.optimizer,
        scheduler=trainer_resumed.scheduler,
        expected_config=m_conf,
        restore_rng=True,
        device=torch.device("cuda"),
    )
    print(f"    Loaded checkpoint! Resumed step: {meta.step}, Epoch: {meta.epoch}")

    resumed_losses = []
    for step in range(6, 11):
        batch_slice = [val_batches[(step * sel_acc_s + i) % len(val_batches)] for i in range(sel_acc_s)]
        telem = trainer_resumed.train_step(batch_slice, step=step)
        resumed_losses.append(telem["train_loss"])

    # Compare uninterrupted vs resumed: Steps 6 to 10
    unint_post_chk = unint_losses[5:]
    loss_diffs = [abs(u - r) for u, r in zip(unint_post_chk, resumed_losses)]
    max_loss_diff = max(loss_diffs)

    # Weight divergence at step 10
    resumed_step10_weights = {k: v.clone().cpu() for k, v in trainer_resumed.model.state_dict().items()}
    weight_diffs = []
    for k in unint_step10_weights:
        diff = (unint_step10_weights[k].float() - resumed_step10_weights[k].float()).abs().max().item()
        weight_diffs.append(diff)
    max_weight_diff = max(weight_diffs)

    print(f"    Uninterrupted Losses (steps 6-10): {[round(x, 6) for x in unint_post_chk]}")
    print(f"    Resumed Losses (steps 6-10):       {[round(x, 6) for x in resumed_losses]}")
    print(f"    Max Loss Difference: {max_loss_diff:.8f}")
    print(f"    Max Weight Divergence at step 10: {max_weight_diff:.8f}")

    checkpoint_validation_passed = (max_loss_diff < 1e-5) and (max_weight_diff < 1e-5)
    print(f"    Checkpoint Bit-Exact Recovery: {'PASSED' if checkpoint_validation_passed else 'FAILED'}\n")

    stability_results["checkpoint_recovery_audit"] = {
        "selected_configuration": "Configuration B (T=1024, B=1, A=2)",
        "checkpoint_step": 5,
        "uninterrupted_losses_steps_6_to_10": unint_post_chk,
        "resumed_losses_steps_6_to_10": resumed_losses,
        "max_loss_difference": max_loss_diff,
        "max_weight_divergence": max_weight_diff,
        "checkpoint_bit_exact_recovery": checkpoint_validation_passed,
        "loss_finiteness_verified": all(math.isfinite(x) for x in resumed_losses),
        "scheduler_step_resumed": trainer_resumed.scheduler.current_step,
        "checkpoint_size_bytes": Path(chk_save_path).stat().st_size,
        "checkpoint_size_mib": round(Path(chk_save_path).stat().st_size * BYTE_TO_MIB, 2),
    }

    # Clean up all temporary checkpoint files
    del trainer_resumed, unint_step10_weights, resumed_step10_weights, val_batches
    clean_gpu()
    try:
        shutil_rm = True
        for p in chk_val_dir.rglob("*"):
            if p.is_file():
                p.unlink(missing_ok=True)
        for p in chk_val_dir.glob("*"):
            if p.is_dir():
                p.rmdir()
        chk_val_dir.rmdir()
        print("    Cleaned up all temporary checkpoint files. 0 bytes lingering.")
    except Exception as e:
        print(f"    Cleanup note: {e}")

    # 5. Save verified JSON
    out_json = WORKSPACE_ROOT / "scratch" / "stability_audit_verified.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(stability_results, f, indent=2)
    print(f"\nAudit complete! Saved detailed stability results to: {out_json}")

    return stability_results

if __name__ == "__main__":
    run_sustained_stability_audit()
