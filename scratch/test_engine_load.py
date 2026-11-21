"""
scratch/test_engine_load.py
"""
import os
import sys
from pathlib import Path
import torch

WORKSPACE = Path(r"C:\IGRIS")
sys.path.insert(0, str(WORKSPACE / "src"))

from igris.inference.engine import IgrisInferenceEngine

ckpt_path = WORKSPACE / "experiments" / "synthetic_pretraining_1m" / "checkpoints" / "igris_model_only_step489.pt"
print(f"Loading checkpoint from: {ckpt_path}")

engine = IgrisInferenceEngine(checkpoint_path=ckpt_path)
print(f"Engine is_trained: {engine.is_trained}")
print(f"Engine model_state: {engine.model_state}")
print(f"Tokenizer verified: {engine.tokenizer_verified}")
print(f"Active device: {engine.device}")
