"""
scratch/run_full_training_validation.py

End-to-end technical validation of the complete IGRIS training backend:
1. Binary Memory-Mapped Dataset Infrastructure (.bin, .idx, manifest SHA256)
2. Multi-document Sequence Packing (EOS boundaries, truncation, padding, attention masks)
3. Train/Val/Test Isolation and Per-Language Evaluation (Tamil, English, Tanglish loss & PPL)
4. Checkpoint Persistence, Model-Only Export, and Interrupted Training Recovery
5. Hardware Profiling on NVIDIA RTX 3050 (VRAM, Host RAM, Steps/sec, Tokens/sec, Save/Load duration)
"""

import csv
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import psutil
import torch
from tokenizers import Tokenizer

WORKSPACE_ROOT = Path(r"C:\IGRIS")
sys.path.insert(0, str(WORKSPACE_ROOT / "src"))

from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_production_config,
)
from igris.training import (
    BinaryDatasetWriter,
    CheckpointMetadata,
    DatasetIntegrityError,
    DatasetManifest,
    EvaluationMetrics,
    IgrisCheckpointManager,
    IgrisEvaluator,
    IgrisTrainer,
    MMapDataset,
    SequencePacker,
    SplitIsolationError,
    StreamingDatasetLoader,
    TrainingConfig,
    compute_config_fingerprint,
    compute_file_sha256,
)

CAND_A_PATH = WORKSPACE_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
EXPECTED_CAND_A_HASH = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"

SYNTHETIC_CORPUS_PATH = WORKSPACE_ROOT / "data" / "eval_generalization" / "INDEPENDENT_SYNTHETIC_CORPUS_MANIFEST.csv"


def run_full_validation() -> dict:
    validation_results = {
        "timestamp": str(np.datetime64("now")),
        "dataset_infrastructure": {},
        "sequence_packing": {},
        "evaluation_metrics": {},
        "checkpoint_recovery": {},
        "hardware_benchmark": {},
        "status": "FAILED",
    }

    # Verify Candidate A tokenizer hash
    actual_hash = compute_file_sha256(CAND_A_PATH)
    assert actual_hash == EXPECTED_CAND_A_HASH, f"Candidate A hash mismatch: {actual_hash}"
    tokenizer = Tokenizer.from_file(str(CAND_A_PATH))

    temp_dir = Path(tempfile.mkdtemp(prefix="igris_train_validation_"))
    print(f"Working in isolated validation directory: {temp_dir}")

    try:
        # =====================================================================
        # 1. Dataset Infrastructure & Train/Val/Test Separation
        # =====================================================================
        print("\n--- 1. Testing Dataset Infrastructure (MMap Binary & Shards) ---")
        dataset_dir = temp_dir / "mmap_dataset"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Load 300 synthetic records (100 Tamil, 100 English, 100 Tanglish)
        records_by_lang = {"TAMIL": [], "ENGLISH": [], "TANGLISH": []}
        with open(SYNTHETIC_CORPUS_PATH, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                lang = row["language"]
                if lang in records_by_lang and len(records_by_lang[lang]) < 100:
                    records_by_lang[lang].append(row["text"])

        # Create train (240: 80 per lang), val (30: 10 per lang), test (30: 10 per lang)
        splits_data = {"train": [], "validation": [], "test": []}
        splits_meta = {"train": [], "validation": [], "test": []}

        for lang, texts in records_by_lang.items():
            for i, text in enumerate(texts):
                tokens = tokenizer.encode(text).ids
                item = {"tokens": tokens, "lang": lang}
                if i < 80:
                    splits_data["train"].append(item)
                elif i < 90:
                    splits_data["validation"].append(item)
                else:
                    splits_data["test"].append(item)

        manifests = {}
        for split_name, items in splits_data.items():
            writer = BinaryDatasetWriter(output_dir=dataset_dir, split_name=split_name)
            for item in items:
                writer.add_document(item["tokens"], language=item["lang"])
            manifest = writer.close()
            manifests[split_name] = manifest.to_dict()
            print(f"Split '{split_name}': {manifest.num_documents} docs, {manifest.total_tokens} tokens, bin_sha256={manifest.bin_sha256[:16]}...")

        # Load with MMapDataset and test integrity
        train_mmap = MMapDataset(output_dir=dataset_dir, split_name="train", verify_integrity=True)
        val_mmap = MMapDataset(output_dir=dataset_dir, split_name="validation", verify_integrity=True)
        test_mmap = MMapDataset(output_dir=dataset_dir, split_name="test", verify_integrity=True)

        assert len(train_mmap) == 240
        assert len(val_mmap) == 30
        assert len(test_mmap) == 30

        # Test zero-RAM indexing and exact token match
        sample_doc = train_mmap[0]
        assert isinstance(sample_doc, torch.Tensor)
        assert sample_doc.dtype == torch.int64
        assert len(sample_doc) == len(splits_data["train"][0]["tokens"])
        assert sample_doc.tolist() == splits_data["train"][0]["tokens"]

        validation_results["dataset_infrastructure"] = {
            "status": "PASSED",
            "splits": {k: {"docs": v["num_documents"], "tokens": v["total_tokens"], "sha256": v["bin_sha256"]} for k, v in manifests.items()},
            "mmap_indexing_verified": True,
            "manifest_sha256_verified": True,
        }

        # =====================================================================
        # 2. Sequence Packing, EOS Boundaries, and Truncation
        # =====================================================================
        print("\n--- 2. Testing Multi-Document Sequence Packing & EOS Boundaries ---")
        packer = SequencePacker(max_seq_len=128)

        # Create test documents of varying lengths
        doc1 = [100, 101, 102]          # 3 tokens -> with BOS/EOS = 5 tokens
        doc2 = [200, 201, 202, 203]     # 4 tokens -> with BOS/EOS = 6 tokens
        doc3 = list(range(500, 700))     # 200 tokens -> exceeds 128! Must be truncated cleanly

        packed = packer.pack_documents([doc1, doc2, doc3], prepend_bos=True, append_eos=True)
        assert len(packed) >= 2

        # Verify Batch 1: doc1 and doc2 packed together
        b1 = packed[0]
        assert b1["input_ids"].shape == (128,)
        assert b1["attention_mask"].shape == (128,)
        assert b1["labels"].shape == (128,)

        # Check BOS and EOS presence
        b1_tokens = b1["input_ids"][: b1["actual_tokens"]].tolist()
        assert b1_tokens[0] == 1  # BOS
        assert b1_tokens[4] == 2  # EOS of doc 1
        assert b1_tokens[5] == 1  # BOS of doc 2
        assert b1_tokens[10] == 2  # EOS of doc 2

        # Check padding
        assert (b1["input_ids"][b1["actual_tokens"] :] == 0).all()
        assert (b1["attention_mask"][b1["actual_tokens"] :] == 0).all()
        assert (b1["labels"][b1["actual_tokens"] :] == -100).all()

        # Check Batch 2: doc3 was truncated to exactly 128 tokens with EOS at position 127
        b2 = packed[1]
        assert b2["actual_tokens"] == 128
        assert b2["input_ids"][0] == 1
        assert b2["input_ids"][127] == 2  # Clean EOS termination

        validation_results["sequence_packing"] = {
            "status": "PASSED",
            "multi_doc_packing_verified": True,
            "eos_boundary_demarcation_verified": True,
            "truncation_verified": True,
            "padding_and_attention_mask_verified": True,
        }

        # =====================================================================
        # 3. Evaluation Engine & Split Protection
        # =====================================================================
        print("\n--- 3. Testing Evaluation Engine, Perplexity & Split Protection ---")
        cfg_prod = get_production_config()
        cfg_prod.tie_word_embeddings = True
        cfg_prod.max_position_embeddings = 512
        cfg_prod.gradient_checkpointing = True

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = IgrisDecoderTransformer(cfg_prod).to(device)

        evaluator = IgrisEvaluator(model, device)

        # Prepare val batches
        val_loader = StreamingDatasetLoader(val_mmap, batch_size=2, max_seq_len=128)
        val_batches = list(val_loader)

        # Prepare per-language val batches
        per_lang_batches = {}
        for l_idx, lang in enumerate(["TAMIL", "ENGLISH", "TANGLISH"]):
            lang_docs = [splits_data["validation"][i]["tokens"] for i in range(l_idx * 10, (l_idx + 1) * 10)]
            p = SequencePacker(max_seq_len=128).pack_documents(lang_docs)
            per_lang_batches[lang] = [
                {
                    "input_ids": p[j]["input_ids"].unsqueeze(0),
                    "attention_mask": p[j]["attention_mask"].unsqueeze(0),
                    "labels": p[j]["labels"].unsqueeze(0),
                }
                for j in range(len(p))
            ]

        eval_metrics = evaluator.evaluate(
            eval_batches=val_batches,
            split_name="validation",
            per_language_batches=per_lang_batches,
        )

        print(f"Validation Loss: {eval_metrics.overall_loss:.4f}, Perplexity: {eval_metrics.overall_perplexity:.2f}")
        for lang, l_m in eval_metrics.per_language.items():
            print(f"  {lang}: Loss={l_m['loss']:.4f}, PPL={l_m['perplexity']:.2f}, Tokens={l_m['tokens']}")

        # Test reproducibility
        is_reproducible = evaluator.verify_reproducibility(val_batches)
        assert is_reproducible is True, "Evaluation was not reproducible!"

        # Test split protection: passing 'test' split without authorization must raise SplitIsolationError
        test_blocked = False
        try:
            evaluator.evaluate(eval_batches=val_batches, split_name="test")
        except SplitIsolationError:
            test_blocked = True
        assert test_blocked is True, "Test split was not blocked by SplitIsolationError!"

        validation_results["evaluation_metrics"] = {
            "status": "PASSED",
            "overall_loss": eval_metrics.overall_loss,
            "overall_perplexity": eval_metrics.overall_perplexity,
            "per_language": eval_metrics.per_language,
            "reproducibility_verified": True,
            "test_split_protection_active": True,
        }

        # =====================================================================
        # 4. Checkpoint Persistence, Model-Only Export, and Recovery
        # =====================================================================
        print("\n--- 4. Testing Checkpoint Persistence, Export, and Crash Recovery ---")
        chk_dir = temp_dir / "checkpoints"
        chk_mgr = IgrisCheckpointManager(checkpoint_dir=chk_dir, candidate_a_hash=EXPECTED_CAND_A_HASH)

        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

        # 4.1 Save full training checkpoint
        train_manifest_hash = manifests["train"]["bin_sha256"]
        full_chk_path = chk_mgr.save_full_checkpoint(
            step=10,
            epoch=1,
            model=model,
            optimizer=optimizer,
            scheduler=None,
            config=cfg_prod,
            train_loss=8.45,
            val_loss=eval_metrics.overall_loss,
            val_perplexity=eval_metrics.overall_perplexity,
            per_language_metrics=eval_metrics.per_language,
            dataset_manifest_sha256=train_manifest_hash,
            precision="bf16",
        )
        assert full_chk_path.exists()
        full_chk_size_mb = round(full_chk_path.stat().st_size / (1024**2), 2)
        print(f"Full training checkpoint saved: {full_chk_path.name} ({full_chk_size_mb} MB)")

        # 4.2 Save model-only export for inference
        export_path = chk_dir / "igris_prod_16l_inference.pt"
        exported = chk_mgr.export_model_only_checkpoint(model=model, config=cfg_prod, output_filepath=export_path, step=10)
        assert exported.exists()
        export_size_mb = round(exported.stat().st_size / (1024**2), 2)
        print(f"Model-only inference checkpoint exported: {exported.name} ({export_size_mb} MB)")

        # 4.3 Controlled Interruption & Resumption Experiment
        print("\nTesting Controlled Interruption and Resume (Uninterrupted vs Interrupted)...")
        # Run A: Uninterrupted 6 steps
        torch.manual_seed(42)
        model_a = IgrisDecoderTransformer(cfg_prod).to(device)
        opt_a = torch.optim.AdamW(model_a.parameters(), lr=1e-3)

        train_loader = StreamingDatasetLoader(train_mmap, batch_size=2, max_seq_len=128, shuffle=False)
        train_batches = list(train_loader)[:6]

        losses_a = []
        for s in range(6):
            opt_a.zero_grad()
            b = train_batches[s]
            out = model_a(b["input_ids"].to(device), labels=b["labels"].to(device))
            out["loss"].backward()
            opt_a.step()
            losses_a.append(float(out["loss"].item()))

        # Run B: Steps 1..3 -> Save -> "Crash" -> Restore -> Steps 4..6
        torch.manual_seed(42)
        model_b = IgrisDecoderTransformer(cfg_prod).to(device)
        opt_b = torch.optim.AdamW(model_b.parameters(), lr=1e-3)

        losses_b = []
        for s in range(3):
            opt_b.zero_grad()
            b = train_batches[s]
            out = model_b(b["input_ids"].to(device), labels=b["labels"].to(device))
            out["loss"].backward()
            opt_b.step()
            losses_b.append(float(out["loss"].item()))

        interrupted_chk_path = chk_mgr.save_full_checkpoint(
            step=3,
            epoch=1,
            model=model_b,
            optimizer=opt_b,
            scheduler=None,
            config=cfg_prod,
            train_loss=losses_b[-1],
        )

        # Restore into fresh model_c and opt_c
        t_load_start = time.perf_counter()
        model_c = IgrisDecoderTransformer(cfg_prod).to(device)
        opt_c = torch.optim.AdamW(model_c.parameters(), lr=1e-3)
        chk_mgr.load_checkpoint(
            filepath=interrupted_chk_path,
            model=model_c,
            optimizer=opt_c,
            expected_config=cfg_prod,
            restore_rng=True,
            device=device,
        )
        t_load_duration = time.perf_counter() - t_load_start

        # Resume steps 4..6
        for s in range(3, 6):
            opt_c.zero_grad()
            b = train_batches[s]
            out = model_c(b["input_ids"].to(device), labels=b["labels"].to(device))
            out["loss"].backward()
            opt_c.step()
            losses_b.append(float(out["loss"].item()))

        # Verify losses in Run A and Run B match bit-identically
        max_loss_diff = max(abs(la - lb) for la, lb in zip(losses_a, losses_b))
        print(f"Max loss difference between uninterrupted and resumed run: {max_loss_diff}")
        assert max_loss_diff < 1e-5, f"Resumption did not match uninterrupted run! Diff: {max_loss_diff}"

        # Verify final model weights match exactly
        with torch.no_grad():
            test_x = torch.tensor([[1, 25, 50, 100]], device=device)
            out_a = model_a(input_ids=test_x)["logits"]
            out_c = model_c(input_ids=test_x)["logits"]
            weight_diff = (out_a - out_c).abs().max().item()
        print(f"Final logit divergence between uninterrupted and resumed models: {weight_diff}")
        assert weight_diff < 1e-5, f"Weights diverged! Diff: {weight_diff}"

        validation_results["checkpoint_recovery"] = {
            "status": "PASSED",
            "full_checkpoint_mb": full_chk_size_mb,
            "model_only_export_mb": export_size_mb,
            "uninterrupted_vs_resumed_loss_diff": max_loss_diff,
            "final_weight_divergence": weight_diff,
            "load_duration_sec": round(t_load_duration, 4),
        }

        # =====================================================================
        # 5. Hardware Profiling & Benchmark on RTX 3050 6GB
        # =====================================================================
        print("\n--- 5. Hardware Profiling on RTX 3050 6GB ---")
        benchmark_configs = [
            {"seq_len": 512, "micro_batch": 2, "accum_steps": 2, "precision": "bf16"},
            {"seq_len": 1024, "micro_batch": 2, "accum_steps": 2, "precision": "bf16"},
            {"seq_len": 2048, "micro_batch": 1, "accum_steps": 2, "precision": "bf16"},
        ]

        bench_results = []
        for bcfg in benchmark_configs:
            s_len = bcfg["seq_len"]
            m_batch = bcfg["micro_batch"]
            acc_s = bcfg["accum_steps"]

            t_cfg = TrainingConfig(
                model_name="igris-prod-16l",
                max_seq_len=s_len,
                micro_batch_size=m_batch,
                gradient_accumulation_steps=acc_s,
                precision=bcfg["precision"],
                activation_checkpointing=True,
                max_steps=3,
                output_dir=str(temp_dir / f"bench_{s_len}"),
            )

            m_cfg = get_production_config()
            m_cfg.tie_word_embeddings = True
            m_cfg.max_position_embeddings = max(s_len, 2048)

            trainer = IgrisTrainer(config=t_cfg, model_config=m_cfg)

            # Generate synthetic batches for benchmark
            bench_packer = SequencePacker(max_seq_len=s_len)
            train_docs = [splits_data["train"][i]["tokens"] for i in range(20)]
            p_seqs = bench_packer.pack_documents(train_docs)
            b_list = []
            for i in range(0, len(p_seqs), m_batch):
                c = p_seqs[i : i + m_batch]
                if len(c) == m_batch:
                    b_list.append({
                        "input_ids": torch.stack([x["input_ids"] for x in c]),
                        "attention_mask": torch.stack([x["attention_mask"] for x in c]),
                        "labels": torch.stack([x["labels"] for x in c]),
                    })

            # Time checkpoint save duration
            t_save_start = time.perf_counter()
            chk_out = trainer.checkpoint_manager.save_full_checkpoint(
                step=1,
                epoch=1,
                model=trainer.model,
                optimizer=trainer.optimizer,
                scheduler=trainer.scheduler,
                config=m_cfg,
                train_loss=10.0,
            )
            t_save_duration = time.perf_counter() - t_save_start

            # Time checkpoint load duration
            t_load_start = time.perf_counter()
            trainer.checkpoint_manager.load_checkpoint(chk_out, model=trainer.model, optimizer=trainer.optimizer, expected_config=m_cfg)
            t_load_duration = time.perf_counter() - t_load_start

            # Warmup step
            trainer.train_step(b_list[:acc_s], step=1)

            # Timed step
            telem = trainer.train_step(b_list[:acc_s], step=2)

            bench_entry = {
                "sequence_length": s_len,
                "micro_batch_size": m_batch,
                "gradient_accumulation_steps": acc_s,
                "effective_batch_tokens": m_batch * acc_s * s_len,
                "allocated_vram_mb": telem["allocated_vram_mb"],
                "reserved_vram_mb": telem["reserved_vram_mb"],
                "host_ram_mb": telem["host_ram_mb"],
                "tokens_per_sec": telem["tokens_per_sec"],
                "steps_per_sec": telem["steps_per_sec"],
                "step_duration_sec": telem["step_duration_sec"],
                "checkpoint_save_sec": round(t_save_duration, 4),
                "checkpoint_load_sec": round(t_load_duration, 4),
            }
            bench_results.append(bench_entry)
            print(f"SeqLen {s_len}: Allocated={bench_entry['allocated_vram_mb']}MB, Reserved={bench_entry['reserved_vram_mb']}MB, Tokens/s={bench_entry['tokens_per_sec']}, Save={bench_entry['checkpoint_save_sec']}s")

        validation_results["hardware_benchmark"] = {
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
            "benchmark_results": bench_results,
        }

        validation_results["status"] = "PASSED"

    finally:
        try:
            if 'train_mmap' in locals():
                train_mmap.close()
            if 'val_mmap' in locals():
                val_mmap.close()
            if 'test_mmap' in locals():
                test_mmap.close()
        except Exception:
            pass
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Cleaned up temporary validation directory: {temp_dir}")

    return validation_results

if __name__ == "__main__":
    res = run_full_validation()
    print("\nFINAL TECHNICAL VALIDATION RESULTS:")
    print(json.dumps(res, indent=2))
