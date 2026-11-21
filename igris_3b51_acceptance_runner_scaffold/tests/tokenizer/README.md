# IGRIS Tokenizer Acceptance Runner

## Status
Initial scaffold only. Static contract checks are executable. Artifact-dependent
acceptance tests are BLOCKED until trained Candidate A/B artifacts and production
adapter integration are available.

## Requirements
Python standard library only. No additional package installation is required.

## Run from the IGRIS repository root

```powershell
python -m tests.tokenizer.acceptance_runner --candidate all
python -m tests.tokenizer.acceptance_runner --candidate A
python -m tests.tokenizer.acceptance_runner --candidate B
```

Optional JSON report:

```powershell
python -m tests.tokenizer.acceptance_runner --candidate all --json-report reports/tokenizer_acceptance/report.json
```

A non-zero exit code is expected while mandatory tests are BLOCKED or FAIL.

## Safety boundaries
- Does not train tokenizers.
- Does not read corpora.
- Does not download data.
- Does not install packages.
- Does not modify production tokenizer files.
- Does not infer that an artifact passes based only on its filename or metadata.

## Next work
1. Finalize candidate artifact loader contract.
2. Implement candidate adapters against actual artifact formats.
3. Implement each test group from acceptance specification v1.0.4.
4. Run artifact-backed acceptance tests.
