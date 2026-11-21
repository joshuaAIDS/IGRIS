# IGRIS tokenizer acceptance scaffold\n\n## Milestone 3B.51.14 — Training configuration validation\n\nRun from this scaffold root:\n\n```powershell\n& C:\\IGRIS\\.venv\\Scripts\\python.exe -m tests.tokenizer.test_training_config\n```\n\nThis validates configuration descriptors and fair A/B corpus fingerprints only. It does not train tokenizers, download corpora, install packages, or modify the main repository. Candidate A has no explicit seed-control setting in the current trainer; deterministic training is therefore not guaranteed.\n

## Milestone 3B.51.16 — Controlled repeat-run experiment scaffold

This is a dry-run planner and artifact hash auditor only. It never invokes Candidate A/B trainers. It plans two isolated runs per candidate, fingerprints the ordered corpus inputs and frozen configurations, and can optionally write a JSON plan.

Unit tests: `& C:\IGRIS\.venv\Scripts\python.exe -m tests.tokenizer.test_controlled_experiment`

Dry-run example (replace the corpus path):

```powershell
& C:\IGRIS\.venv\Scripts\python.exe -m tests.tokenizer.run_controlled_experiment --corpus "C:\path\to\prepared.txt" --output-root "C:\IGRIS\tokenizer_experiments" --plan-out "C:\IGRIS\tokenizer_experiments\plan.json"
```

No training is executed. The plan command reads corpus files and writes JSON only if `--plan-out` is supplied. SHA-256 equality proves byte identity only; semantic equivalence requires backend-level tests.
