import csv
import json
import math

print("=== CALCULATING PHASE 22A STORAGE RECONCILIATION ===")

# Storage Components breakdown (Decimal GB & Binary GiB)
# 1 GB = 10^9 bytes, 1 GiB = 2^30 bytes = 1,073,741,824 bytes
# Ratio: GB / GiB = (10^9) / (2^30) = 0.9313225746154785

def gb_to_gib(gb):
    return round(gb * (10**9) / (1024**3), 2)

components = [
    {
        "component_id": "COMP-01-RAW-DOWNLOAD",
        "component_name": "Raw Downloaded Corpus (9 files)",
        "decimal_gb": 183.70,
        "binary_gib": gb_to_gib(183.70),
        "stage_type": "INGRESS",
        "simultaneous_or_sequential": "SIMULTANEOUS_DURING_INGRESS",
        "representation_nature": "PRIMARY_SOURCE_PAYLOAD",
        "deletable_after_verification": "YES_AFTER_CLEANING_AND_VERIFICATION",
        "notes": "Exact declared size of the 9 flat text files from IndicCorp v2."
    },
    {
        "component_id": "COMP-02-QUARANTINE-STAGING",
        "component_name": "Quarantine Staging Directory",
        "decimal_gb": 183.70,
        "binary_gib": gb_to_gib(183.70),
        "stage_type": "QUARANTINE",
        "simultaneous_or_sequential": "ALTERNATIVE_OR_DUPLICATE_IF_STAGED",
        "representation_nature": "STAGING_CONTAINER_OR_DUPLICATE",
        "deletable_after_verification": "YES_UPON_UNQUARANTINING",
        "notes": "If downloaded directly into quarantine, this is identical to COMP-01 (183.7 GB). If copied from a download cache into quarantine, it is an additional 183.7 GB copy."
    },
    {
        "component_id": "COMP-03-EXTRACTION-BUFFER",
        "component_name": "Temporary Extraction & Validation Buffer",
        "decimal_gb": 26.30,
        "binary_gib": gb_to_gib(26.30),
        "stage_type": "VALIDATION",
        "simultaneous_or_sequential": "SIMULTANEOUS_DURING_CHECKSUMMING",
        "representation_nature": "TRANSIENT_WORKING_BUFFER",
        "deletable_after_verification": "YES_IMMEDIATELY_AFTER_HASHING",
        "notes": "Largest single file buffer (data/hi-1.txt or ml.txt ~26.7 GB) during streaming hash computation."
    },
    {
        "component_id": "COMP-04-CLEANED-CORPUS",
        "component_name": "Cleaned & Filtered Corpus",
        "decimal_gb": 130.00,
        "binary_gib": gb_to_gib(130.00),
        "stage_type": "PROCESSING",
        "simultaneous_or_sequential": "SIMULTANEOUS_WITH_RAW_DURING_CLEANING",
        "representation_nature": "FILTERED_TRANSFORMATION",
        "deletable_after_verification": "YES_AFTER_TOKENIZATION",
        "notes": "Post-heuristic filtering, LID verification, and deduplication (~29% reduction from raw text)."
    },
    {
        "component_id": "COMP-05-DEDUP-INDEX",
        "component_name": "Deduplication Index & MinHash Signatures",
        "decimal_gb": 10.00,
        "binary_gib": gb_to_gib(10.00),
        "stage_type": "PROCESSING",
        "simultaneous_or_sequential": "SIMULTANEOUS_DURING_DEDUPLICATION",
        "representation_nature": "METADATA_INDEX",
        "deletable_after_verification": "YES_AFTER_DEDUP_STAGE",
        "notes": "MinHash 128 permutations across 3.72B words for Jaccard LSH clustering."
    },
    {
        "component_id": "COMP-06-TOKENIZED-SHARDS",
        "component_name": "Tokenized Shards (uint16 Token IDs)",
        "decimal_gb": 12.00,
        "binary_gib": gb_to_gib(12.00),
        "stage_type": "TRAINING_READY",
        "simultaneous_or_sequential": "PERSISTENT_ACROSS_TRAINING",
        "representation_nature": "FINAL_TRAINING_INPUT",
        "deletable_after_verification": "NO_PRESERVED_FOR_TRAINING",
        "notes": "5.5B tokens in uint16 format (2 bytes/token = 11.0 GB) + index headers (1.0 GB)."
    },
    {
        "component_id": "COMP-07-CHECKPOINTS",
        "component_name": "Training Checkpoints (10 Checkpoints)",
        "decimal_gb": 15.00,
        "binary_gib": gb_to_gib(15.00),
        "stage_type": "TRAINING_STATE",
        "simultaneous_or_sequential": "ACCUMULATES_DURING_TRAINING",
        "representation_nature": "MODEL_AND_OPTIMIZER_STATE",
        "deletable_after_verification": "NO_ROLLING_PURGE_EXCEPT_BEST",
        "notes": "10 checkpoints @ 1.5 GB each (model weights + AdamW states + master weights + metadata)."
    },
    {
        "component_id": "COMP-08-SCRATCH-SPACE",
        "component_name": "Scratch & Sorting Working Space",
        "decimal_gb": 20.00,
        "binary_gib": gb_to_gib(20.00),
        "stage_type": "SYSTEM_SCRATCH",
        "simultaneous_or_sequential": "EPHEMERAL_PER_OPERATION",
        "representation_nature": "INTERMEDIATE_FILE_IO",
        "deletable_after_verification": "YES_AUTOMATICALLY_CLEANED",
        "notes": "Disk space for multi-threaded sorting, shuffling, and memory-mapping scratch files."
    },
    {
        "component_id": "COMP-09-OS-HEADROOM",
        "component_name": "Operating System Headroom & Pagefile Buffer",
        "decimal_gb": 50.00,
        "binary_gib": gb_to_gib(50.00),
        "stage_type": "SYSTEM_HEADROOM",
        "simultaneous_or_sequential": "PERMANENT_RESERVE",
        "representation_nature": "RESERVED_OPERATIONAL_BUFFER",
        "deletable_after_verification": "NO_SYSTEM_STABILITY_REQUISITE",
        "notes": "Minimum free space required to prevent OS disk-exhaustion crashes and swap lockups."
    }
]

# Calculate Four Capacities:
# A. Minimum theoretical capacity: Just the single largest stage + scratch + OS
# Ingress stage: raw (183.70) + buffer (26.30) + OS (50.00) = 260.00 GB
min_theoretical_gb = 183.70 + 26.30 + 50.00
min_theoretical_gib = gb_to_gib(min_theoretical_gb)

# B. Peak simultaneous capacity (Naive uncleaned co-existence of all representations):
# If raw + duplicate quarantine copy + buffer + clean + dedup + tokens + checkpoints + scratch + OS:
peak_simultaneous_full_gb = sum(c["decimal_gb"] for c in components)
peak_simultaneous_full_gib = gb_to_gib(peak_simultaneous_full_gb)

# Peak simultaneous (In-place quarantine, no duplicate copy):
# 183.70 (raw) + 26.30 (buffer) + 130.00 (clean) + 10.00 (dedup) + 12.00 (tokens) + 15.00 (ckpts) + 20.00 (scratch) + 50.00 (OS)
peak_simultaneous_inplace_gb = 183.70 + 26.30 + 130.00 + 10.00 + 12.00 + 15.00 + 20.00 + 50.00
peak_simultaneous_inplace_gib = gb_to_gib(peak_simultaneous_inplace_gb)

# C. Sequential processing capacity with verified cleanup:
# Stage 1: Ingress: 183.70 + 26.30 + 50.00 = 260.00 GB
# Stage 2: Cleaning: 183.70 (raw) + 130.00 (clean) + 10.00 (dedup) + 20.00 (scratch) + 50.00 (OS) = 393.70 GB
# Then purge raw (183.70) and dedup (10.00). Remaining on disk: 130.00 GB
# Stage 3: Tokenization: 130.00 (clean) + 12.00 (tokens) + 20.00 (scratch) + 50.00 (OS) = 212.00 GB
# Then purge clean (130.00). Remaining on disk: 12.00 GB
# Stage 4: Training: 12.00 (tokens) + 15.00 (ckpts) + 20.00 (scratch) + 50.00 (OS) = 97.00 GB
# Max of sequential stages is Stage 2:
seq_peak_gb = 393.70
seq_peak_gib = gb_to_gib(seq_peak_gb)

# D. Recommended capacity with operational safety margin:
# Standard 1 TB cloud volume: 1,000 GB decimal = 931.32 GiB binary
rec_gb = 1000.00
rec_gib = gb_to_gib(rec_gb)

print(f"Components sum (Naive All): {peak_simultaneous_full_gb:.2f} GB ({peak_simultaneous_full_gib:.2f} GiB)")
print(f"In-place simultaneous: {peak_simultaneous_inplace_gb:.2f} GB ({peak_simultaneous_inplace_gib:.2f} GiB)")
print(f"Sequential peak (Stage 2): {seq_peak_gb:.2f} GB ({seq_peak_gib:.2f} GiB)")
print(f"Minimum theoretical: {min_theoretical_gb:.2f} GB ({min_theoretical_gib:.2f} GiB)")
print(f"Recommended (1 TB): {rec_gb:.2f} GB ({rec_gib:.2f} GiB)")

# Reconciliation of 532.40 GB vs 600.70 GB:
# 600.70 GB = 183.70 (raw) + 183.70 (quarantine) + 26.30 (buffer) + 130.00 (clean) + 12.00 (tokens) + 15.00 (ckpts) + 50.00 (OS)
# 532.40 GB = 183.70 (raw) + 183.70 (quarantine) + 130.00 (clean) + 20.00 (tokens) + 15.00 (ckpts)
# The difference (600.70 - 532.40 = 68.30 GB):
# 600.70 included 50.00 GB OS headroom + 26.30 GB buffer, but tokens was 12.00 GB instead of 20.00 GB:
# 50.00 + 26.30 - (20.00 - 12.00) = 76.30 - 8.00 = 68.30 GB!
print(f"Reconciliation difference check: 600.70 - 532.40 = {600.70 - 532.40:.2f} GB")

print("\n=== CALCULATING TRAINING THROUGHPUT SCENARIOS ===")
# Target Token Counts: 1B, 3B, 5.5B, 10B
tokens_list = [
    ("1B Tokens", 1_000_000_000),
    ("3B Tokens", 3_000_000_000),
    ("5.5B Tokens (Full IndicCorp)", 5_500_000_000),
    ("10B Tokens", 10_000_000_000)
]

scenarios = [
    {
        "id": "SCEN-01-THROTTLED-LOCAL",
        "name": "Local RTX 3050 Laptop GPU (Throttled / Full Context)",
        "throughput_tok_sec": 1750.0,
        "duty_cycle": 0.80, # 20% overhead for thermal cooling pauses & sync
        "effective_tok_sec": 1750.0 * 0.80, # 1400 tok/sec
        "description": "Empirical lower bound observed during sustained heating / B=1, L=2048 full context."
    },
    {
        "id": "SCEN-02-NOMINAL-LOCAL",
        "name": "Local RTX 3050 Laptop GPU (Nominal Measured Experiment A)",
        "throughput_tok_sec": 2658.6,
        "duty_cycle": 0.88, # 12% overhead for evaluation & checkpoint atomic writes
        "effective_tok_sec": 2658.6 * 0.88, # 2339.57 tok/sec
        "description": "Direct Phase 17 Experiment A measured benchmark on 96.5M model (B=2, L=256)."
    },
    {
        "id": "SCEN-03-PEAK-LOCAL",
        "name": "Local RTX 3050 Laptop GPU (Optimal Batch Grid Point 6)",
        "throughput_tok_sec": 3816.5,
        "duty_cycle": 0.90, # 10% overhead for periodic checkpointing
        "effective_tok_sec": 3816.5 * 0.90, # 3434.85 tok/sec
        "description": "Phase 17 Experiment C Grid Point 6 measured peak throughput (B=4, L=512, 72.4% VRAM)."
    },
    {
        "id": "SCEN-04-CLOUD-RTX4090",
        "name": "Cloud Single NVIDIA RTX 4090 (24GB VRAM)",
        "throughput_tok_sec": 25000.0,
        "duty_cycle": 0.95, # 5% overhead for checkpointing
        "effective_tok_sec": 25000.0 * 0.95, # 23750 tok/sec
        "description": "Cloud consumer flagship with 24GB VRAM, enabling B=16, L=2048 with FlashAttention 2."
    },
    {
        "id": "SCEN-05-CLOUD-A100",
        "name": "Cloud Single NVIDIA A100 (80GB SXM)",
        "throughput_tok_sec": 45000.0,
        "duty_cycle": 0.96, # 4% overhead
        "effective_tok_sec": 45000.0 * 0.96, # 43200 tok/sec
        "description": "Phase 17 reference enterprise benchmark for single SXM A100."
    }
]

duration_results = []
for sc in scenarios:
    for t_name, t_count in tokens_list:
        raw_hours = t_count / (sc["throughput_tok_sec"] * 3600)
        raw_days = raw_hours / 24
        eff_hours = t_count / (sc["effective_tok_sec"] * 3600)
        eff_days = eff_hours / 24
        duration_results.append({
            "scenario_id": sc["id"],
            "scenario_name": sc["name"],
            "nominal_tok_sec": sc["throughput_tok_sec"],
            "duty_cycle_pct": int(sc["duty_cycle"] * 100),
            "effective_tok_sec": round(sc["effective_tok_sec"], 2),
            "token_budget": t_name,
            "raw_hours": round(raw_hours, 2),
            "raw_days": round(raw_days, 2),
            "effective_hours": round(eff_hours, 2),
            "effective_days": round(eff_days, 2)
        })

print(f"Generated {len(duration_results)} training duration scenario rows.")

print("\n=== CALCULATING CLOUD COST SCENARIOS ===")
# Providers: RunPod, Lambda Labs, AWS EC2, GCP Compute Engine
# Scenarios: Low, Expected, High
cost_scenarios = [
    {
        "scenario": "LOW_COST",
        "provider": "RunPod (Community / Secure Cloud)",
        "instance_type": "1x RTX 4090 (24GB VRAM, 16 vCPU, 64GB RAM)",
        "gpu_hourly_rate": 0.44,
        "storage_monthly_rate_1tb": 20.00, # RunPod network volume ~$0.07/GB-mo or $0.02/hr
        "storage_daily_rate_1tb": 20.00 / 30, # ~$0.67 / day
        "data_prep_hours": 12.0,
        "data_prep_hourly_cost": 0.20, # CPU-only droplet
        "training_hours_5_5b": 64.3, # 5.5B / (23,750 tok/s * 3600)
        "storage_retention_days": 4.0, # 4 days
        "egress_gb": 20.0,
        "egress_rate_per_gb": 0.00, # RunPod free egress
        "total_compute_cost": round(12.0 * 0.20 + 64.3 * 0.44, 2), # 2.40 + 28.29 = 30.69
        "total_storage_cost": round(4.0 * (20.0 / 30), 2), # 2.67
        "total_egress_cost": 0.00,
        "total_estimated_cost": round(30.69 + 2.67, 2), # ~33.36
        "classification": "PARTIALLY_SUPPORTED",
        "assumptions": "Community GPU availability, zero GPU usage during data prep, immediate volume teardown within 4 days."
    },
    {
        "scenario": "EXPECTED_COST",
        "provider": "Lambda Labs (On-Demand Cloud)",
        "instance_type": "1x NVIDIA A100 (80GB SXM4, 30 vCPU, 200GB RAM)",
        "gpu_hourly_rate": 1.89,
        "storage_monthly_rate_1tb": 100.00, # Lambda persistent storage ~$0.10/GB-mo
        "storage_daily_rate_1tb": 100.00 / 30, # ~$3.33 / day
        "data_prep_hours": 10.0,
        "data_prep_hourly_cost": 1.89, # Same instance used end-to-end
        "training_hours_5_5b": 35.3, # 5.5B / (43,200 tok/s * 3600)
        "storage_retention_days": 7.0, # 1 week retention
        "egress_gb": 25.0,
        "egress_rate_per_gb": 0.00, # Lambda free egress
        "total_compute_cost": round((10.0 + 35.3) * 1.89, 2), # 45.3 * 1.89 = 85.62
        "total_storage_cost": round(7.0 * (100.0 / 30), 2), # 23.33
        "total_egress_cost": 0.00,
        "total_estimated_cost": round(85.62 + 23.33, 2), # ~108.95
        "classification": "PARTIALLY_SUPPORTED",
        "assumptions": "Standard on-demand availability, single instance used for preparation and training, 7-day retention of checkpoints."
    },
    {
        "scenario": "HIGH_COST_ENTERPRISE",
        "provider": "Google Cloud Platform (GCP) or AWS EC2",
        "instance_type": "GCP a2-highgpu-1g (1x A100 40GB, 12 vCPU, 85GB RAM) or AWS p4d",
        "gpu_hourly_rate": 3.67,
        "storage_monthly_rate_1tb": 100.00, # 1TB pd-ssd or gp3 ~$0.10/GB-mo
        "storage_daily_rate_1tb": 100.00 / 30, # ~$3.33 / day
        "data_prep_hours": 12.0,
        "data_prep_hourly_cost": 3.67,
        "training_hours_5_5b": 40.0,
        "storage_retention_days": 30.0, # Full month volume retention
        "egress_gb": 30.0,
        "egress_rate_per_gb": 0.09, # AWS/GCP internet egress ~$0.09/GB
        "total_compute_cost": round((12.0 + 40.0) * 3.67, 2), # 52.0 * 3.67 = 190.84
        "total_storage_cost": 100.00,
        "total_egress_cost": round(30.0 * 0.09, 2), # 2.70
        "total_estimated_cost": round(190.84 + 100.00 + 2.70, 2), # ~293.54
        "classification": "UNSUPPORTED_UNDER_35_65",
        "assumptions": "Major cloud tier-1 on-demand pricing, full month storage allocation, full standard egress fees."
    }
]

print("Cost Scenarios:")
for cs in cost_scenarios:
    print(f"  {cs['scenario']}: ${cs['total_estimated_cost']} ({cs['provider']}) - {cs['classification']}")
