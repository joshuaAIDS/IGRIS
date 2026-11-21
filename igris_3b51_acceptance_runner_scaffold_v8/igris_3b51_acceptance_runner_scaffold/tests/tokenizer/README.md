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


### 3B.51.5 — Batch contract probes
The shared TS-BAT tests validate batch input rules, ordering in a reference contract probe, empty items, and atomic validation. They do not prove Candidate A/B production batch APIs; those remain artifact-blocked until real adapters and trained artifacts are integrated.


### 3B.51.6 — Trusted sequence rendering
TS-REN shared tests exercise a reference renderer: trusted structural IDs render as fixed spellings, maximal contiguous content spans are decoded independently, and content-only decoding rejects structural IDs. These tests do not prove production candidate adapters are wired to the renderer; candidate integration remains artifact-blocked.


### 3B.51.7 — Raw binary codec contract
TS-BIN shared tests exercise a reference one-byte-to-one-content-token mapping codec, including all 256 byte values, arbitrary binary payloads, strict type/range/mapping validation, and exact byte preservation. The mapping used by these tests is synthetic: Candidate A must provide IDs from its ByteLevel byte-to-Unicode mapping, and Candidate B must provide IDs for its SentencePiece <0xXX> BYTE pieces. Neither candidate mapping nor production binary API is verified by this shared contract suite.


### 3B.51.8 — Metadata and save/reload contract
TS-META shared tests validate a proposed metadata schema, candidate identity/configuration fields, fixed vocabulary and structural-token metadata, canonical JSON serialization, and JSON save/reload. These tests exercise the scaffold's metadata helper only; they do not inspect or validate metadata embedded in trained Candidate A/B artifacts.
