# IGRIS 3B.51.17 — Corpus Pilot Kit

## Purpose
A safe, local-only pilot corpus preparation kit. It does **not** download data,
install packages, modify the main IGRIS repository, or train a tokenizer.

## Source policy
Review `metadata/source_manifest.json` before adding any dataset. IndicCorp V2
and DravidianCodeMix are conditional candidates, not blanket legal guarantees.
Tanglish Corpus 185K is marked HOLD because its card describes platform-derived
YouTube/Reddit material; do not put it into a commercial corpus until the
underlying rights and platform terms are reviewed.

## Folder inputs
Place only approved, legally obtained files under:
- `data/raw/tamil/`
- `data/raw/english/`
- `data/raw/tanglish/`

Accepted formats: UTF-8 TXT, JSONL, CSV. For JSONL/CSV, a text field named
`text`, `sentence`, `comment`, or `content` is read.

## Run on Windows PowerShell
From the extracted kit folder:

```powershell
& C:\IGRIS\.venv\Scripts\python.exe .\scripts\prepare_pilot.py
```

The script uses only Python's standard library. It writes script-level buckets
under `data/processed/` and a report under `reports/`.

## Important classification limitation
The script can detect Tamil Unicode versus Latin-script text, but it cannot
reliably distinguish English from Tanglish. Latin text is placed in
`latin_review.txt`; manually label a reviewed sample before creating language
percentages. It does not invent a 35/35/30 balance.

## Structural tokens
The pilot rejects lines containing common structural-token-like spellings for
manual review rather than silently treating them as ordinary text. Confirm the
actual IGRIS reserved-token list against the production tokenizer specification
before final corpus approval.

## Acceptance gate
Do not train until:
1. each source has an approved licence/provenance record;
2. the actual IGRIS reserved-token list has been checked;
3. English/Tamil/Tanglish labels have been manually reviewed;
4. duplicates, Unicode, malformed records and sample lengths are audited;
5. corpus split and SHA-256 manifest are frozen and approved.
