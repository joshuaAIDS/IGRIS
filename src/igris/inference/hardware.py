"""Hardware inspection, VRAM budgeting, and safe compute device selection for IGRIS.

Calibrated for target hardware:
  - NVIDIA GeForce RTX 3050 6GB Laptop GPU (CUDA 12.x)
  - 13th Gen Intel Core i5-13420H
  - ~16GB System RAM
"""
from __future__ import annotations

import logging
import os
import platform
from dataclasses import dataclass
from typing import Any, Optional

import torch

logger = logging.getLogger(__name__)


@dataclass
class HardwareProfile:
    device: str
    device_name: str
    cuda_available: bool
    total_vram_gb: float
    free_vram_gb: float
    cpu_architecture: str
    cpu_threads: int
    system_platform: str
    safe_for_gpu: bool
    fallback_reason: Optional[str] = None
    system_ram_total_gb: Optional[float] = None
    system_ram_available_gb: Optional[float] = None
    system_ram_used_gb: Optional[float] = None
    system_ram_util_pct: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "device": self.device,
            "device_name": self.device_name,
            "cuda_available": self.cuda_available,
            "total_vram_gb": round(self.total_vram_gb, 2),
            "free_vram_gb": round(self.free_vram_gb, 2),
            "cpu_architecture": self.cpu_architecture,
            "cpu_threads": self.cpu_threads,
            "system_platform": self.system_platform,
            "safe_for_gpu": self.safe_for_gpu,
            "fallback_reason": self.fallback_reason,
        }
        if self.system_ram_total_gb is not None:
            d["system_ram_total_gb"] = self.system_ram_total_gb
            d["system_ram_available_gb"] = self.system_ram_available_gb
            d["system_ram_used_gb"] = self.system_ram_used_gb
            d["system_ram_util_pct"] = self.system_ram_util_pct
        return d


def inspect_hardware(min_vram_headroom_gb: float = 1.0) -> HardwareProfile:
    """Inspect local hardware and determine the optimal execution device.

    Guarantees safe CPU fallback if CUDA is unavailable, driver is incompatible,
    or free VRAM is below the safety threshold.
    """
    sys_platform = platform.platform()
    cpu_arch = platform.processor() or platform.machine()
    cpu_threads = os.cpu_count() or 4

    ram_total: Optional[float] = None
    ram_avail: Optional[float] = None
    ram_used: Optional[float] = None
    ram_pct: Optional[float] = None
    try:
        import psutil
        vm = psutil.virtual_memory()
        ram_total = round(vm.total / (1024**3), 2)
        ram_avail = round(vm.available / (1024**3), 2)
        ram_used = round((vm.total - vm.available) / (1024**3), 2)
        ram_pct = round(vm.percent, 1)
    except Exception:
        pass

    if not torch.cuda.is_available():
        return HardwareProfile(
            device="cpu",
            device_name=f"CPU ({cpu_arch})",
            cuda_available=False,
            total_vram_gb=0.0,
            free_vram_gb=0.0,
            cpu_architecture=cpu_arch,
            cpu_threads=cpu_threads,
            system_platform=sys_platform,
            safe_for_gpu=False,
            fallback_reason="CUDA is not available in PyTorch environment",
            system_ram_total_gb=ram_total,
            system_ram_available_gb=ram_avail,
            system_ram_used_gb=ram_used,
            system_ram_util_pct=ram_pct,
        )

    try:
        gpu_idx = 0
        device_name = torch.cuda.get_device_name(gpu_idx)
        total_vram = torch.cuda.get_device_properties(gpu_idx).total_memory / (1024**3)
        free_bytes, total_bytes = torch.cuda.mem_get_info(gpu_idx)
        free_vram = free_bytes / (1024**3)

        if free_vram < min_vram_headroom_gb:
            return HardwareProfile(
                device="cpu",
                device_name=device_name,
                cuda_available=True,
                total_vram_gb=total_vram,
                free_vram_gb=free_vram,
                cpu_architecture=cpu_arch,
                cpu_threads=cpu_threads,
                system_platform=sys_platform,
                safe_for_gpu=False,
                fallback_reason=(
                    f"Free VRAM ({free_vram:.2f} GB) is below required safety threshold ({min_vram_headroom_gb:.2f} GB)"
                ),
                system_ram_total_gb=ram_total,
                system_ram_available_gb=ram_avail,
                system_ram_used_gb=ram_used,
                system_ram_util_pct=ram_pct,
            )

        return HardwareProfile(
            device=f"cuda:{gpu_idx}",
            device_name=device_name,
            cuda_available=True,
            total_vram_gb=total_vram,
            free_vram_gb=free_vram,
            cpu_architecture=cpu_arch,
            cpu_threads=cpu_threads,
            system_platform=sys_platform,
            safe_for_gpu=True,
            fallback_reason=None,
            system_ram_total_gb=ram_total,
            system_ram_available_gb=ram_avail,
            system_ram_used_gb=ram_used,
            system_ram_util_pct=ram_pct,
        )

    except Exception as exc:
        logger.warning(f"Failed to query CUDA hardware details: {exc}. Falling back to CPU.")
        return HardwareProfile(
            device="cpu",
            device_name=f"CPU ({cpu_arch})",
            cuda_available=False,
            total_vram_gb=0.0,
            free_vram_gb=0.0,
            cpu_architecture=cpu_arch,
            cpu_threads=cpu_threads,
            system_platform=sys_platform,
            safe_for_gpu=False,
            fallback_reason=f"CUDA inspection exception: {exc}",
            system_ram_total_gb=ram_total,
            system_ram_available_gb=ram_avail,
            system_ram_used_gb=ram_used,
            system_ram_util_pct=ram_pct,
        )


def estimate_model_footprint(
    params_count: int,
    dtype: torch.dtype = torch.float16,
    context_length: int = 2048,
    num_layers: int = 16,
    num_kv_heads: int = 4,
    head_dim: int = 64,
) -> dict[str, float]:
    """Calculate exact memory requirements for model weights and KV cache.

    Returns memory in Megabytes (MB).
    """
    bytes_per_param = 2 if dtype in (torch.float16, torch.bfloat16) else 4
    weights_mb = (params_count * bytes_per_param) / (1024 * 1024)

    # KV cache = 2 (keys + values) * layers * kv_heads * head_dim * context * bytes_per_param
    kv_cache_bytes = 2 * num_layers * num_kv_heads * head_dim * context_length * bytes_per_param
    kv_cache_mb = kv_cache_bytes / (1024 * 1024)

    # Scratchpad working buffer (logits, attention matrix scratchpad, activations)
    scratchpad_mb = 180.0

    total_est_mb = weights_mb + kv_cache_mb + scratchpad_mb

    return {
        "weights_mb": round(weights_mb, 2),
        "kv_cache_mb": round(kv_cache_mb, 2),
        "scratchpad_mb": round(scratchpad_mb, 2),
        "total_estimated_mb": round(total_est_mb, 2),
    }
