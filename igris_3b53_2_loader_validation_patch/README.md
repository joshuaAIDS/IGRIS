# IGRIS 3B.53.2 — tokenizer artifact loader-validation patch

## Purpose
Adds strict metadata/configuration checks for real Candidate A and Candidate B
artifacts. This is a separate review patch. It does not edit `C:\IGRIS`, train a
tokenizer, read a corpus, install packages, download data, or create artifacts.

## Files
- `src/igris/tokenizer/artifact_validation.py`

## Integration into the 3B.52 patch
In `strict.py`, add these imports near the top:

```python
from .artifact_validation import (
    validate_candidate_a_config,
    validate_candidate_b_config,
)
```

In `load_candidate_a`, immediately after:
```python
backend = _TokenizersBackend(Tokenizer.from_file(path))
```
add:
```python
validate_candidate_a_config(backend.tokenizer)
```

In `load_candidate_b`, immediately after:
```python
backend = _SentencePieceBackend(processor)
```
add:
```python
validate_candidate_b_config(processor)
```

Keep the existing `_validate_artifact`, byte-map checks, wrapper behavior, and
all public APIs. These checks supplement, rather than replace, existing checks.

## Important acceptance notes
- These validators have NOT been run against real trained artifacts.
- Candidate A validation checks BPE model type, ByteLevel pre-tokenizer and
  decoder, null post-processor, full vocabulary count, structural IDs, and
  structural AddedToken flags.
- Candidate B validation checks the serialized SentencePiece model proto:
  Unigram, byte fallback, vocabulary, PAD/BOS/EOS/UNK IDs, identity
  normalization and whitespace settings, structural piece order and types.
- SentencePiece metadata must match the approved contract exactly. If the
  installed SentencePiece build exposes a proto/API difference, report it;
  do not weaken the checks silently.
- A/B byte-fallback and 256-byte mapping acceptance still requires real
  artifacts and the existing `RawBinaryCodec` validation.
- This patch does not authorize training or corpus use.

## Run after manually integrating
```powershell
C:\IGRIS\.venv\Scripts\python.exe -m compileall "C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\src"
C:\IGRIS\.venv\Scripts\python.exe "C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\tests\test_contract.py"
```
These commands test syntax and the existing in-memory wrapper tests only. They
do not establish artifact acceptance.
