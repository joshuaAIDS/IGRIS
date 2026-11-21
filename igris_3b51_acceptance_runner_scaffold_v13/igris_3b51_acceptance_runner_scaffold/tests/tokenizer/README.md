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


### 3B.51.9 — Candidate artifact interface/layout contract
Expected directory layout: `artifact_manifest.json`, `metadata.json`, and exactly the candidate backend file (`tokenizer.json` for Candidate A; `tokenizer.model` for Candidate B). The manifest records project/candidate identity and SHA-256 hashes for backend and metadata files. The runner validates this layout and metadata but does not load or execute the model. Artifact-backed tokenizer tests remain BLOCKED until a real trained artifact and production loader are supplied.


### 3B.51.10 — Candidate backend loader
With an artifact directory supplied, the adapter first verifies its manifest, metadata, and SHA-256 hashes. Candidate A is loaded with `tokenizers.Tokenizer.from_file`; Candidate B with `sentencepiece.SentencePieceProcessor(model_file=...)`. Both loaders verify the exact vocabulary size (32768) and all 12 structural token IDs. This milestone does not train/download artifacts and does not yet claim the shared production wrapper or all artifact-backed acceptance groups.


### 3B.51.11 — Candidate trainer modules (implementation only)
Two explicit local-only trainers are included:
- `candidate_a_trainer.py`: Tokenizers ByteLevel BPE.
- `candidate_b_trainer.py`: SentencePiece Unigram with byte fallback.
- `artifact_builder.py`: reopens the trained backend, verifies the exact 32768
  vocabulary and structural IDs 0..11, then writes metadata and SHA-256 manifest.
- `train_tokenizers.py`: optional CLI; it performs training only when manually run.

The trainer modules do not download corpora, install packages, or run training
during import. The caller must provide one or more explicit, non-empty UTF-8
corpus files that have already been prepared using the approved IGRIS
normalization and sentinel-escaping pipeline. This scaffold does not implement
or certify that corpus-preparation pipeline. Do not feed raw, unprepared text
and assume the v1.0.4 preprocessing contract has been met.

Example (run only after the corpus is approved and prepared):

```powershell
# Candidate A
..\\..\\.venv\\Scripts\\python.exe -m tests.tokenizer.train_tokenizers --candidate A --corpus "C:\\IGRIS_DATA\\prepared\\train.txt" --output-dir "C:\\IGRIS_ARTIFACTS\\candidate_a"

# Candidate B
..\\..\\.venv\\Scripts\\python.exe -m tests.tokenizer.train_tokenizers --candidate B --corpus "C:\\IGRIS_DATA\\prepared\\train.txt" --output-dir "C:\\IGRIS_ARTIFACTS\\candidate_b"
```

These commands are examples only and have not been run. Exact-vocabulary
training may fail if the supplied corpus cannot support 32768 pieces; the
trainer deliberately fails rather than silently reducing the vocabulary.

## Milestone 3B.51.12 — local corpus preparation (no training)

`corpus_preparation.py` prepares only explicitly supplied local UTF-8 text files.
It does not download data, install packages, access the network, modify source
files, or train a tokenizer. The output directory must be new/nonexistent.

From the scaffold root, prepare one or more local corpus files:

```powershell
..\\..\\.venv\\Scripts\\python.exe -m tests.tokenizer.corpus_preparation `
  --input "C:\\path\\to\\approved_corpus.txt" `
  --output-dir "C:\\IGRIS_DATA\\prepared_corpus_v1" `
  --mode text_mode
```

Repeat `--input` for additional files. `text_mode` applies Unicode 15.1 NFC
before sentinel escaping. `exact_unicode_mode` preserves code points before
sentinel escaping. The pipeline preserves record order, blank records, and
surrounding whitespace. It reports duplicate records but does not remove them
unless `--deduplicate` is explicitly supplied. It rejects invalid UTF-8 and NUL
characters, leaves source files untouched, and writes `prepared_corpus.txt` plus
`corpus_report.json` (including source/output SHA-256 hashes).

The resulting `prepared_corpus.txt` can be supplied as the corpus input to the
Candidate A/B trainer modules. This milestone does not establish corpus rights,
consent, language balance, representativeness, or suitability; those require a
separate human review. No corpus has been supplied, downloaded, or trained here.


## Milestone 3B.51.13 — Corpus quality audit

Run the read-only audit on an explicitly supplied prepared corpus:

```powershell
python -m tests.tokenizer.test_corpus_quality_audit
python -m tests.tokenizer.corpus_quality_audit --input .\prepared_corpus.txt --report .\corpus_quality_report.json
```

The audit reports heuristic script/keyword buckets, empty/whitespace records, normalized exact duplicates, character-similarity near duplicates, long records, raw structural spellings, UTF-8 validity, and SHA-256. Language labels are not authoritative (especially English vs Tanglish). It does not certify licensing, consent, privacy, representativeness, or training suitability. It never modifies the corpus, downloads data, or trains a tokenizer.
