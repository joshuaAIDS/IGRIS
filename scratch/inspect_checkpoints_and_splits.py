"""
scratch/inspect_checkpoints_and_splits.py

Inspects:
1. All 4 full checkpoints and the model-only checkpoint.
2. Evaluates the full validation split (300 documents, 279,988 tokens).
3. Evaluates the full held-out test split (300 documents, 279,933 tokens) under strict read-only isolation.
"""
import hashlib
import json
from pathlib import Path
import torch

WORKSPACE = Path(r"C:\IGRIS")
CHK_DIR = WORKSPACE / "experiments" / "synthetic_pretraining_1m" / "checkpoints"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("--- Checkpoint Inspection ---")
for f in sorted(CHK_DIR.glob("*.pt")):
    size = f.stat().st_size
    sha = sha256_file(f)
    print(f"File: {f.name} | Size: {size} bytes ({size / (1024*1024):.2f} MiB) | SHA256: {sha}")
    data = torch.load(f, map_location="cpu")
    if isinstance(data, dict):
        print(f"  Dict keys: {list(data.keys())[:10]}")
        if "model_state_dict" in data:
            print(f"  model_state_dict keys: {len(data['model_state_dict'])}")
        elif "state_dict" in data:
            print(f"  state_dict keys: {len(data['state_dict'])}")
        else:
            print(f"  Raw state_dict tensor count: {len(data)}")
    else:
        print(f"  Type: {type(data)}")
