# IGRIS Tokenizer Acceptance Runner

## Status
The scaffold runs static contract checks, strict input validation (TS-VAL),
and backend-independent Unicode/structural-spelling escaping checks (TS-UNI
and TS-SEC helper tests). Candidate artifact-backed Unicode round-trip and
public-encoder structural-ID isolation remain BLOCKED until trained Candidate
A/B artifacts and production adapter integration are available.

## Requirements
Python standard library plus the already-approved `unicodedata2==15.1.0`
runtime dependency for Unicode normalization checks. The runner does not
install packages. If that exact Unicode engine is unavailable, relevant tests
fail visibly rather than silently falling back to a different Unicode version.

## Run
From the extracted acceptance-runner scaffold folder:

```powershell
..\.venv\Scripts\python.exe -m tests.tokenizer.acceptance_runner --candidate all
```

Optional JSON report:

```powershell
..\.venv\Scripts\python.exe -m tests.tokenizer.acceptance_runner --candidate all --json-report reports/tokenizer_acceptance/report.json
```

A non-zero exit code is expected while mandatory artifact tests are BLOCKED or FAIL.

## Scope and safety boundaries
- No tokenizer training.
- No corpus access or downloads.
- No package installation.
- No production tokenizer files modified.
- Shared escape-helper tests are not proof of Candidate A/B backend integration.
- No test claims that text escaping itself prevents the tokenizer from emitting
  structural IDs; that requires artifact-backed public API tests.

## Next work
1. Finalize candidate artifact loader contract.
2. Implement candidate adapters against actual artifact formats.
3. Implement remaining artifact-backed acceptance tests.
4. Run full acceptance against trained artifacts.
