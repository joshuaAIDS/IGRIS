"""Command-line entry point; training occurs only when the user runs this script."""
from __future__ import annotations

import argparse

from .artifact_builder import finalize_artifact
from .candidate_a_trainer import train_candidate_a
from .candidate_b_trainer import train_candidate_b


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train one IGRIS tokenizer candidate from explicitly supplied prepared corpus files."
    )
    parser.add_argument("--candidate", choices=("A", "B"), required=True)
    parser.add_argument("--corpus", action="append", required=True,
                        help="Prepared UTF-8 corpus file; repeat this option for multiple files.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    if args.candidate == "A":
        backend = train_candidate_a(args.corpus, args.output_dir)
    else:
        backend = train_candidate_b(args.corpus, args.output_dir)
    metadata, manifest = finalize_artifact(args.candidate, args.output_dir)
    print(f"Candidate {args.candidate} backend: {backend}")
    print(f"Metadata: {metadata}")
    print(f"Manifest: {manifest}")
    print("Artifact generated and backend vocabulary/structural IDs verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
