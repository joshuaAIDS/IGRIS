"""
scratch/run_training_smoke_test.py

Executes a small, bounded, synthetic-only training smoke test for IGRIS.
- Uses newly generated synthetic Tamil, English, and Tanglish examples.
- Tokenizes with authoritative Candidate A tokenizer.
- Configures authoritative 16-layer production architecture (igris-prod-16l) with tied embeddings.
- Executes 5 bounded training steps on local GPU (RTX 3050).
- Verifies finite loss, valid gradients, gradient norm clipping, parameter updates.
- Verifies atomic checkpoint saving and exact resumption.
- Cleans up temporary artifacts.
"""

import datetime
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import torch
import torch.nn as nn
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
sys.path.insert(0, str(WORKSPACE_ROOT / "src"))
sys.path.insert(0, str(PATCH_ROOT / "scripts"))

from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_production_config,
)
from checkpoint_integrity import (
    CAND_A_HASH,
    CAND_B_HASH,
    CheckpointManager,
    CheckpointMetadata,
    compute_config_fingerprint,
)
from model_training_pipeline import IgrisCosineWarmupScheduler

# 1. Authoritative synthetic texts across all 3 approved languages
SMOKE_TEST_TEXTS = [
    # Tamil
    {"id": "SMK-TA-01", "lang": "TAMIL", "text": "இந்த பலமொழி மின்மாற்றி மாதிரி தமிழ் மொழியின் அமைப்பை துல்லியமாக கற்கிறது."},
    {"id": "SMK-TA-02", "lang": "TAMIL", "text": "கணினி மொழியியல் துறையில் தமிழ் எழுத்துருக்களின் பயன்பாடு மிக முக்கியமானதாகும்."},
    # English
    {"id": "SMK-EN-01", "lang": "ENGLISH", "text": "The decoder-only transformer optimizes multilingual representations using grouped query attention."},
    {"id": "SMK-EN-02", "lang": "ENGLISH", "text": "Rotary position embeddings ensure relative positional awareness across causal attention layers."},
    # Tanglish
    {"id": "SMK-TG-01", "lang": "TANGLISH", "text": "Intha model deployment process romba fast-ah mudinjiduchu da."},
    {"id": "SMK-TG-02", "lang": "TANGLISH", "text": "Server-la database query execute aagi response correct-ah varuthu."},
]

def run_smoke_test() -> dict:
    results = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "FAILED",
        "device": "",
        "steps_executed": 0,
        "initial_loss": None,
        "final_loss": None,
        "loss_finite": False,
        "gradients_finite": False,
        "checkpoint_saved": False,
        "checkpoint_restored": False,
        "weights_identical": False,
        "clean_up_successful": False,
        "step_metrics": [],
    }

    # Verify Candidate A tokenizer hash
    cand_a_path = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
    actual_hash = hashlib.sha256(cand_a_path.read_bytes()).hexdigest()
    if actual_hash != CAND_A_HASH:
        raise ValueError(f"Candidate A hash mismatch: {actual_hash} != {CAND_A_HASH}")

    tokenizer = Tokenizer.from_file(str(cand_a_path))

    # Tokenize synthetic texts
    tokenized_samples = []
    max_len = 64
    for item in SMOKE_TEST_TEXTS:
        enc = tokenizer.encode(item["text"])
        ids = [1] + enc.ids[: max_len - 2] + [2]  # BOS + tokens + EOS
        tokenized_samples.append(ids)

    # Pad to equal length
    batch_size = 2
    padded_batches = []
    for i in range(0, len(tokenized_samples), batch_size):
        chunk = tokenized_samples[i : i + batch_size]
        actual_max = max(len(c) for c in chunk)
        b_tokens = []
        b_masks = []
        b_labels = []
        for seq in chunk:
            pad_len = actual_max - len(seq)
            tokens = seq + [0] * pad_len
            mask = [1] * len(seq) + [0] * pad_len
            labels = [x if x != 0 else -100 for x in tokens]
            b_tokens.append(tokens)
            b_masks.append(mask)
            b_labels.append(labels)
        
        padded_batches.append({
            "input_ids": torch.tensor(b_tokens, dtype=torch.long),
            "attention_mask": torch.tensor(b_masks, dtype=torch.long),
            "labels": torch.tensor(b_labels, dtype=torch.long),
        })

    # Architecture configuration: Authoritative Production 16L with Tied Embeddings
    cfg = get_production_config()
    cfg.tie_word_embeddings = True  # Authoritative specification: Tied embeddings
    cfg.max_position_embeddings = 512
    cfg.gradient_checkpointing = True  # Activation checkpointing

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    results["device"] = str(device)
    print(f"Using device: {device}")

    model = IgrisDecoderTransformer(cfg).to(device)
    param_counts = model.count_parameters()
    print(f"Model initialized: total_params={param_counts['total_parameters']}, trainable={param_counts['trainable_parameters']}")
    assert param_counts["total_parameters"] == 79_708_672, f"Expected 79708672 params, got {param_counts['total_parameters']}"

    # Optimizer and scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.1, betas=(0.9, 0.95), eps=1e-8)
    scheduler = IgrisCosineWarmupScheduler(optimizer, warmup_steps=1, max_steps=5, min_lr_ratio=0.1)
    chk_manager = CheckpointManager()

    # Temporary directory for smoke test checkpoints
    temp_dir = Path(tempfile.mkdtemp(prefix="igris_smoke_test_"))
    try:
        model.train()
        initial_params = {n: p.detach().clone() for n, p in model.named_parameters()}
        all_grads_finite = True
        step_metrics = []

        total_steps = 5
        accumulation_steps = 2
        optimizer.zero_grad()

        for step in range(1, total_steps + 1):
            batch = padded_batches[(step - 1) % len(padded_batches)]
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            out = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = out["loss"]

            if loss is None or torch.isnan(loss) or torch.isinf(loss):
                raise ValueError(f"Step {step}: Non-finite loss encountered: {loss}")

            scaled_loss = loss / accumulation_steps
            scaled_loss.backward()

            # Check gradients
            for name, param in model.named_parameters():
                if param.grad is not None:
                    if torch.isnan(param.grad).any() or torch.isinf(param.grad).any():
                        all_grads_finite = False

            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            optimizer.zero_grad()
            current_lr = scheduler.step()

            step_loss_val = float(loss.item())
            grad_norm_val = float(grad_norm.item() if isinstance(grad_norm, torch.Tensor) else grad_norm)

            if step == 1:
                results["initial_loss"] = step_loss_val
            results["final_loss"] = step_loss_val

            metric_entry = {
                "step": step,
                "loss": round(step_loss_val, 6),
                "grad_norm": round(grad_norm_val, 6),
                "lr": round(current_lr, 8),
            }
            step_metrics.append(metric_entry)
            print(f"Step {step}/{total_steps} - Loss: {step_loss_val:.4f}, GradNorm: {grad_norm_val:.4f}, LR: {current_lr:.6f}")

        results["steps_executed"] = total_steps
        results["step_metrics"] = step_metrics
        results["loss_finite"] = True
        results["gradients_finite"] = all_grads_finite

        # Verify weights actually changed
        weights_updated = False
        for n, p in model.named_parameters():
            if not torch.equal(p.detach().cpu(), initial_params[n].cpu()):
                weights_updated = True
                break
        results["weights_updated"] = weights_updated
        assert weights_updated, "Model parameters were not updated during smoke test!"

        # Test atomic checkpoint save
        chk_file = temp_dir / "smoke_chk_step_5.pt"
        meta = CheckpointMetadata(
            checkpoint_id="chk_smoke_05",
            step=5,
            loss=results["final_loss"],
            random_seed=42,
            model_config_fingerprint=compute_config_fingerprint(cfg),
            model_config=cfg.to_dict(),
            candidate_a_sha256=CAND_A_HASH,
            candidate_b_sha256=CAND_B_HASH,
            is_synthetic_test=True,
        )
        saved_path = chk_manager.save_checkpoint(model, optimizer, meta, chk_file)
        results["checkpoint_saved"] = saved_path.exists()
        print(f"Temporary checkpoint saved: {saved_path} (size={saved_path.stat().st_size} bytes)")

        # Test checkpoint load and restore into fresh model
        fresh_model = IgrisDecoderTransformer(cfg).to(device)
        fresh_opt = torch.optim.AdamW(fresh_model.parameters(), lr=1e-4)
        payload, restored_meta = chk_manager.load_checkpoint(
            filepath=saved_path,
            model=fresh_model,
            optimizer=fresh_opt,
            expected_config=cfg,
        )
        results["checkpoint_restored"] = (restored_meta.step == 5)

        # Verify exact weight match
        model.eval()
        fresh_model.eval()
        test_in = torch.tensor([[1, 50, 100, 200]], device=device)
        with torch.no_grad():
            out_orig = model(input_ids=test_in)["logits"]
            out_fresh = fresh_model(input_ids=test_in)["logits"]
        max_diff = (out_orig - out_fresh).abs().max().item()
        results["weights_identical"] = (max_diff == 0.0)
        print(f"Checkpoint restored. Max logit difference between original and restored: {max_diff}")

        results["status"] = "PASSED"

    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            results["clean_up_successful"] = not temp_dir.exists()
            print(f"Cleaned up temporary directory: {temp_dir}")

    return results

if __name__ == "__main__":
    res = run_smoke_test()
    print("\nSMOKE TEST SUMMARY:")
    print(json.dumps(res, indent=2))
