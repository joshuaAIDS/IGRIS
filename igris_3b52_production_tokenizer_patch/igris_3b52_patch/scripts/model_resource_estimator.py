"""IGRIS Phase 16 — Model Training Resource and Compute Estimator.

Calculates theoretical and empirical memory, compute, and hardware requirements for IGRIS transformer models.
Profiles local hardware (RTX 3050 6GB Laptop GPU, CPU, RAM) and provides sizing recommendations.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

# Setup patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

import torch
from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_baseline_50m_config,
    get_production_config,
)


@dataclass
class HardwareProfile:
    platform: str
    cuda_available: bool
    device_name: str
    total_vram_gb: float
    compute_capability: str
    pytorch_version: str


@dataclass
class MemoryEstimation:
    model_name: str
    total_params: int
    trainable_params: int
    param_memory_fp32_mb: float
    param_memory_fp16_mb: float
    grad_memory_fp32_mb: float
    grad_memory_fp16_mb: float
    adamw_optimizer_memory_mb: float  # FP32 states (8 bytes/param) or mixed (12 bytes/param)
    activations_b4_l512_mb: float
    activations_b4_l2048_mb: float
    total_train_vram_b4_l512_gb: float
    total_train_vram_b4_l2048_gb: float
    local_gpu_feasible_b4_l512: bool
    local_gpu_feasible_b4_l2048: bool


def detect_hardware() -> HardwareProfile:
    """Inspect local execution platform and CUDA accelerator."""
    cuda_avail = torch.cuda.is_available()
    dev_name = "None"
    vram_gb = 0.0
    cap = "N/A"

    if cuda_avail:
        dev_name = torch.cuda.get_device_name(0)
        vram_bytes = torch.cuda.get_device_properties(0).total_memory
        vram_gb = round(vram_bytes / (1024**3), 3)
        major, minor = torch.cuda.get_device_capability(0)
        cap = f"{major}.{minor}"

    return HardwareProfile(
        platform=sys.platform,
        cuda_available=cuda_avail,
        device_name=dev_name,
        total_vram_gb=vram_gb,
        compute_capability=cap,
        pytorch_version=torch.__version__,
    )


def estimate_activations_mb(
    config: IgrisConfig,
    batch_size: int,
    seq_len: int,
    use_activation_checkpointing: bool = False,
) -> float:
    """Estimate forward-backward activation memory per batch in megabytes.

    Formulation:
    Per layer:
      - Attention: Q, K, V activations [B, L, H] (3 * 2 bytes in fp16)
      - Attention matrix: [B, num_heads, L, L] (2 bytes in fp16)
      - Attention dropout/output: [B, L, H]
      - SwiGLU MLP: gate_proj, up_proj [B, L, intermediate_size] * 2
      - LayerNorms: 2 * [B, L, H]
    """
    b = batch_size
    l = seq_len
    h = config.hidden_size
    inter = config.intermediate_size
    n_layers = config.num_hidden_layers
    bytes_per_elem = 2  # fp16/bf16 activations

    # Per-layer activations (in bytes)
    # Norms: 2 * (B * L * H)
    norm_bytes = 2 * (b * l * h * bytes_per_elem)
    # Q, K, V projections + attention output
    qkv_bytes = (config.num_attention_heads + 2 * config.num_key_value_heads) * (h // config.num_attention_heads) * b * l * bytes_per_elem
    # Attention matrix: B * num_heads * L * L
    attn_matrix_bytes = b * config.num_attention_heads * l * l * bytes_per_elem
    # SwiGLU MLP: gate, up, act, down
    swiglu_bytes = (2 * inter + inter) * b * l * bytes_per_elem

    layer_bytes = norm_bytes + qkv_bytes + attn_matrix_bytes + swiglu_bytes

    if use_activation_checkpointing:
        # Only store layer boundary activations + single layer during backward
        total_bytes = (n_layers * b * l * h * bytes_per_elem) + layer_bytes
    else:
        total_bytes = n_layers * layer_bytes

    return round(total_bytes / (1024 * 1024), 2)


def estimate_model_resources(config: IgrisConfig, hw: HardwareProfile) -> MemoryEstimation:
    """Compute detailed memory footprint and feasibility against local GPU."""
    # Build dummy model on CPU to count parameters exactly
    model = IgrisDecoderTransformer(config)
    param_counts = model.count_parameters()
    total_params = param_counts["total_parameters"]
    trainable_params = param_counts["trainable_parameters"]

    # Parameter memory
    param_fp32_mb = round((total_params * 4) / (1024 * 1024), 2)
    param_fp16_mb = round((total_params * 2) / (1024 * 1024), 2)

    # Gradient memory
    grad_fp32_mb = round((trainable_params * 4) / (1024 * 1024), 2)
    grad_fp16_mb = round((trainable_params * 2) / (1024 * 1024), 2)

    # Optimizer memory: AdamW maintains 1st and 2nd momentum in FP32 (8 bytes/param)
    # plus master weights if mixed precision (4 bytes/param) -> 12 bytes/param
    adamw_mb = round((trainable_params * 12) / (1024 * 1024), 2)

    # Activation memory
    act_b4_l512 = estimate_activations_mb(config, batch_size=4, seq_len=512)
    act_b4_l2048 = estimate_activations_mb(config, batch_size=4, seq_len=2048)

    # Base framework overhead (PyTorch context, CUDA kernels, allocator)
    cuda_overhead_mb = 750.0

    # Total training VRAM (FP16 mixed precision + AdamW)
    total_vram_b4_l512_gb = round(
        (param_fp16_mb + grad_fp16_mb + adamw_mb + act_b4_l512 + cuda_overhead_mb) / 1024,
        3,
    )
    total_vram_b4_l2048_gb = round(
        (param_fp16_mb + grad_fp16_mb + adamw_mb + act_b4_l2048 + cuda_overhead_mb) / 1024,
        3,
    )

    avail_vram = hw.total_vram_gb if hw.cuda_available else 0.0
    feasible_512 = avail_vram >= total_vram_b4_l512_gb
    feasible_2048 = avail_vram >= total_vram_b4_l2048_gb

    return MemoryEstimation(
        model_name=config.name,
        total_params=total_params,
        trainable_params=trainable_params,
        param_memory_fp32_mb=param_fp32_mb,
        param_memory_fp16_mb=param_fp16_mb,
        grad_memory_fp32_mb=grad_fp32_mb,
        grad_memory_fp16_mb=grad_fp16_mb,
        adamw_optimizer_memory_mb=adamw_mb,
        activations_b4_l512_mb=act_b4_l512,
        activations_b4_l2048_mb=act_b4_l2048,
        total_train_vram_b4_l512_gb=total_vram_b4_l512_gb,
        total_train_vram_b4_l2048_gb=total_vram_b4_l2048_gb,
        local_gpu_feasible_b4_l512=feasible_512,
        local_gpu_feasible_b4_l2048=feasible_2048,
    )


def compute_training_flops(params_non_embed: int, tokens: int) -> dict[str, Any]:
    """Estimate total FLOPs and compute budget for pretraining."""
    # Standard Chinchilla / Kaplan formulation:
    # Forward pass: ~2 * P_non_embed FLOPs/token
    # Backward pass: ~4 * P_non_embed FLOPs/token
    # Total: ~6 * P_non_embed FLOPs/token
    flops_per_token = 6 * params_non_embed
    total_flops = flops_per_token * tokens

    # GPU theoretical throughput (RTX 3050 Laptop Tensor Cores FP16 ~36 TFLOPS peak, ~15 TFLOPS achieved at 40% MFU)
    tflops_achieved = 15.0 * (10**12)
    seconds_est = total_flops / tflops_achieved
    hours_est = seconds_est / 3600.0
    days_est = hours_est / 24.0

    return {
        "tokens": tokens,
        "flops_per_token": flops_per_token,
        "total_flops": f"{total_flops:.3e}",
        "achieved_tflops_assumed": 15.0,
        "estimated_training_hours_single_rtx3050": round(hours_est, 1),
        "estimated_training_days_single_rtx3050": round(days_est, 1),
    }


def generate_resource_report() -> dict[str, Any]:
    """Generate comprehensive resource estimation report."""
    hw = detect_hardware()
    prod_cfg = get_production_config()
    base_cfg = get_baseline_50m_config()

    prod_est = estimate_model_resources(prod_cfg, hw)
    base_est = estimate_model_resources(base_cfg, hw)

    # Compute FLOPs for 1B, 5B, and 10B token pretraining runs
    prod_non_embed = prod_est.total_params - (prod_cfg.vocab_size * prod_cfg.hidden_size * 2)
    flops_1b = compute_training_flops(prod_non_embed, 1_000_000_000)
    flops_5b = compute_training_flops(prod_non_embed, 5_000_000_000)
    flops_10b = compute_training_flops(prod_non_embed, 10_000_000_000)

    report = {
        "hardware_profile": asdict(hw),
        "production_16l_estimates": asdict(prod_est),
        "baseline_12l_estimates": asdict(base_est),
        "compute_estimates_prod": {
            "1_billion_tokens": flops_1b,
            "5_billion_tokens": flops_5b,
            "10_billion_tokens": flops_10b,
        },
    }
    return report


if __name__ == "__main__":
    report = generate_resource_report()
    hw = report["hardware_profile"]
    p = report["production_16l_estimates"]
    b = report["baseline_12l_estimates"]

    print("================================================================================")
    print("IGRIS PHASE 16 — MODEL RESOURCE & HARDWARE ESTIMATION")
    print("================================================================================")
    print(f"Hardware Detected: {hw['device_name']} ({hw['total_vram_gb']} GB VRAM)")
    print(f"CUDA Available:    {hw['cuda_available']} (PyTorch {hw['pytorch_version']})")
    print("\n--- Production 16-Layer Model (~96.5M Params) ---")
    print(f"  Total Params:       {p['total_params']:,}")
    print(f"  Weights (FP16):     {p['param_memory_fp16_mb']:.1f} MB")
    print(f"  Gradients (FP16):   {p['grad_memory_fp16_mb']:.1f} MB")
    print(f"  AdamW Optimizer:    {p['adamw_optimizer_memory_mb']:.1f} MB")
    print(f"  Total VRAM (B=4, L=512):  {p['total_train_vram_b4_l512_gb']:.2f} GB (Feasible: {p['local_gpu_feasible_b4_l512']})")
    print(f"  Total VRAM (B=4, L=2048): {p['total_train_vram_b4_l2048_gb']:.2f} GB (Feasible: {p['local_gpu_feasible_b4_l2048']})")

    print("\n--- Baseline 12-Layer Model (~68.4M Untied / ~51.6M Tied) ---")
    print(f"  Total Params:       {b['total_params']:,}")
    print(f"  Total VRAM (B=4, L=512):  {b['total_train_vram_b4_l512_gb']:.2f} GB (Feasible: {b['local_gpu_feasible_b4_l512']})")
    print(f"  Total VRAM (B=4, L=2048): {b['total_train_vram_b4_l2048_gb']:.2f} GB (Feasible: {b['local_gpu_feasible_b4_l2048']})")

    c = report["compute_estimates_prod"]["1_billion_tokens"]
    print("\n--- Compute Estimation (1B Tokens) ---")
    print(f"  Total FLOPs: {c['total_flops']}")
    print(f"  Estimated Wall-clock on single RTX 3050: {c['estimated_training_hours_single_rtx3050']} hours ({c['estimated_training_days_single_rtx3050']} days)")
    print("================================================================================")
