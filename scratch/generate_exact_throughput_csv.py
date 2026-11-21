import csv

rates = [
    {
        "id": "RATE_01_THROTTLED",
        "target": "Local RTX 3050 Laptop GPU",
        "doc": "PHASE18_SCALABILITY_BENCHMARK.json",
        "config": "bf16_act_ckpt (B=2 L=256 native bf16 with activation checkpointing latency 302.3ms)",
        "nominal_rate": 1693.56,
        "derating_formula": "Derated by 82.67% to account for laptop thermal throttling (target 1400 tok/s)",
        "effective_rate": 1400.00,
        "classification": "MEASURED_AND_ADJUSTED",
        "notes": "Full context B=1 L=2048 causes high thermal buildup; 82.7% duty cycle accounts for throttling pauses."
    },
    {
        "id": "RATE_02_NOMINAL",
        "target": "Local RTX 3050 Laptop GPU",
        "doc": "PHASE17_RESOURCE_UTILIZATION_REPORT.md",
        "config": "Experiment A 16L Production Model (FP32 B=2 L=256 step latency 192.6ms)",
        "nominal_rate": 2658.60,
        "derating_formula": "Derated by 88.0% (Nominal * 0.88) to account for eval and checkpoint IO",
        "effective_rate": 2339.57,
        "classification": "MEASURED_AND_ADJUSTED",
        "notes": "Phase 17 empirical baseline; 12% overhead for periodic validation and atomic checkpoint writes."
    },
    {
        "id": "RATE_03_PEAK_LOCAL",
        "target": "Local RTX 3050 Laptop GPU",
        "doc": "PHASE17_RESOURCE_UTILIZATION_REPORT.md",
        "config": "Experiment C Grid Point 6 (FP32 B=4 L=512 step latency 536.6ms 72.4% VRAM)",
        "nominal_rate": 3816.50,
        "derating_formula": "Derated by 90.0% (Nominal * 0.90) for rolling checkpointing",
        "effective_rate": 3434.85,
        "classification": "MEASURED_AND_ADJUSTED",
        "notes": "Peak local batch efficiency; consumes 4.34 GB VRAM leaving 1.65 GB headroom."
    },
    {
        "id": "RATE_04_CLOUD_4090",
        "target": "Cloud 1x NVIDIA RTX 4090 24GB",
        "doc": "Reference Desktop Flagship Architecture",
        "config": "Projected for 1x RTX 4090 (B=16 L=2048 FlashAttention 2)",
        "nominal_rate": 25000.00,
        "derating_formula": "Derated by 95.0% (Nominal * 0.95) for checkpoint IO",
        "effective_rate": 23750.00,
        "classification": "HYPOTHETICAL_CLOUD_PROJECTION",
        "notes": "High-end consumer card; NOT measured locally. Based on 24GB VRAM batch scaling."
    },
    {
        "id": "RATE_05_CLOUD_A100",
        "target": "Cloud 1x NVIDIA A100 80GB SXM",
        "doc": "PHASE17_RESOURCE_UTILIZATION_REPORT.md",
        "config": "Section 5.3 Reference Extrapolation for A100 SXM (B=32 L=2048)",
        "nominal_rate": 45000.00,
        "derating_formula": "Derated by 96.0% (Nominal * 0.96) for distributed checkpointing",
        "effective_rate": 43200.00,
        "classification": "HYPOTHETICAL_CLOUD_PROJECTION",
        "notes": "Enterprise accelerator; NOT measured locally. Reference projection from Phase 17."
    }
]

tokens = [
    ("1B Tokens", 1_000_000_000),
    ("3B Tokens", 3_000_000_000),
    ("5.5B Tokens (Full IndicCorp)", 5_500_000_000),
    ("10B Tokens", 10_000_000_000),
]

fieldnames = [
    "rate_id", "hardware_target", "benchmark_source_document", "benchmark_config_details",
    "measured_nominal_tok_sec", "derating_formula_and_pct", "effective_tok_sec",
    "rate_classification", "token_target", "nominal_hours", "nominal_days",
    "effective_hours", "effective_days", "operational_uncertainty_notes"
]

rows = []
for r in rates:
    for t_name, t_val in tokens:
        nom_h = round(t_val / (r["nominal_rate"] * 3600), 2)
        nom_d = round(nom_h / 24, 2)
        eff_h = round(t_val / (r["effective_rate"] * 3600), 2)
        eff_d = round(eff_h / 24, 2)
        rows.append({
            "rate_id": r["id"],
            "hardware_target": r["target"],
            "benchmark_source_document": r["doc"],
            "benchmark_config_details": r["config"],
            "measured_nominal_tok_sec": f"{r['nominal_rate']:.2f}",
            "derating_formula_and_pct": r["derating_formula"],
            "effective_tok_sec": f"{r['effective_rate']:.2f}",
            "rate_classification": r["classification"],
            "token_target": t_name,
            "nominal_hours": f"{nom_h:.2f}",
            "nominal_days": f"{nom_d:.2f}",
            "effective_hours": f"{eff_h:.2f}",
            "effective_days": f"{eff_d:.2f}",
            "operational_uncertainty_notes": r["notes"]
        })

csv_text = ",".join(fieldnames) + "\n"
for row in rows:
    csv_text += ",".join([f'"{row[fn]}"' if "," in row[fn] else str(row[fn]) for fn in fieldnames]) + "\n"

print("Generated CSV text length:", len(csv_text))
for dest in [
    r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE22B_TRAINING_THROUGHPUT_AUDIT.csv",
    r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102\PHASE22B_TRAINING_THROUGHPUT_AUDIT.csv"
]:
    with open(dest, "w", encoding="utf-8") as f:
        f.write(csv_text)
    print("Wrote to", dest)
