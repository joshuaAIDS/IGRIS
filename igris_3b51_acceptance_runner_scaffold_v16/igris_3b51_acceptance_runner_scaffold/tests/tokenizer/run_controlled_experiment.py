"""Create a dry-run plan for IGRIS tokenizer repeatability experiments.

No training occurs. The script only reads corpus files and optionally writes
an experiment-plan JSON when --plan-out is supplied.
"""
from __future__ import annotations
import argparse
from .controlled_experiment import build_experiment_plan, plan_to_dict, write_plan
import json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", nargs="+", required=True, help="prepared UTF-8 corpus files")
    parser.add_argument("--output-root", required=True, help="planned artifact output root")
    parser.add_argument("--plan-out", help="optional path for writing plan JSON")
    args = parser.parse_args()
    plan = build_experiment_plan(args.corpus, args.output_root)
    if args.plan_out:
        print(f"Plan written: {write_plan(plan, args.plan_out)}")
    print(json.dumps(plan_to_dict(plan), indent=2, ensure_ascii=False))
    print("TRAINING EXECUTED: NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
