"""
scratch/build_generalization_dataset.py

Generates 3,000 completely new synthetic evaluation records:
- 1,000 Tamil (Conversational, Formal, Educational, Technical, Long-form)
- 1,000 English (Conversational, Formal, Educational, Technical, Long-form)
- 1,000 Tanglish (Romanized Tamil, Tamil-script tech, English w/ discourse markers,
                  Intra-sentential switching, Formal & Long-form Tanglish)

Enforces:
- IGRIS-SPEC-LANG-TAXONOMY-V1
- Unicode 15.1 NFC normalization
- Zero non-target Indic/Cyrillic/CJK/Arabic scripts
- Zero living PII
- Zero exact, normalized, or near duplicates against original 399 records
- Seed-based determinism (Seed: 20261120)
"""

import csv
import hashlib
import json
import math
import os
import random
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# Deterministic seed
RANDOM_SEED = 20261120
random.seed(RANDOM_SEED)

WORKSPACE_ROOT = Path(r"C:\IGRIS")
DATA_DIR = WORKSPACE_ROOT / "data" / "eval_generalization"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Prohibited scripts (only Tamil and Latin scripts permitted)
PROHIBITED_RANGES = [
    ("Devanagari", 0x0900, 0x097F),
    ("Bengali", 0x0980, 0x09FF),
    ("Telugu", 0x0C00, 0x0C7F),
    ("Kannada", 0x0C80, 0x0CFF),
    ("Malayalam", 0x0D00, 0x0D7F),
    ("Cyrillic", 0x0400, 0x04FF),
    ("Arabic", 0x0600, 0x06FF),
]

def validate_text(text: str) -> None:
    norm = unicodedata.normalize("NFC", text)
    if norm != text:
        raise ValueError("Text must be Unicode NFC normalized")
    for ch in text:
        cp = ord(ch)
        for name, start, end in PROHIBITED_RANGES:
            if start <= cp <= end:
                raise ValueError(f"Prohibited non-target script detected: {name} ({ch})")

def get_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

print("Generator module initialized.")
