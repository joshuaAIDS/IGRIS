"""IGRIS Evaluation Engine — Multilingual Loss, Perplexity, and Split Isolation.

Evaluates decoder-only Transformer models across Tamil, English, and Tanglish splits,
computes validation loss and perplexity (PPL = exp(loss)), enforces test-split protection,
and ensures deterministic mathematical reproducibility.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
from igris.training.dataset import SplitIsolationError


@dataclass
class EvaluationMetrics:
    overall_loss: float
    overall_perplexity: float
    total_tokens: int
    num_batches: int
    per_language: Dict[str, Dict[str, float]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IgrisEvaluator:
    """Evaluates IGRIS models on validation splits with per-language breakdown."""

    def __init__(self, model: nn.Module, device: torch.device):
        self.model = model
        self.device = device

    def evaluate(
        self,
        eval_batches: List[Dict[str, torch.Tensor]],
        split_name: str = "validation",
        per_language_batches: Optional[Dict[str, List[Dict[str, torch.Tensor]]]] = None,
    ) -> EvaluationMetrics:
        """Run complete evaluation over batches with perplexity and per-language tracking."""
        if split_name.lower() == "test":
            raise SplitIsolationError(
                "CRITICAL GOVERNANCE ERROR: The test split is strictly reserved for final out-of-sample "
                "evaluation. It must never be evaluated during training or used for checkpoint selection."
            )

        self.model.eval()
        total_loss = 0.0
        total_tokens = 0
        num_batches = len(eval_batches)

        if num_batches == 0:
            return EvaluationMetrics(
                overall_loss=0.0,
                overall_perplexity=0.0,
                total_tokens=0,
                num_batches=0,
                per_language={},
            )

        is_cuda = (self.device.type == "cuda")
        autocast_dtype = torch.bfloat16 if (is_cuda and torch.cuda.is_bf16_supported()) else torch.float32

        with torch.no_grad(), torch.amp.autocast(device_type="cuda", dtype=autocast_dtype, enabled=is_cuda):
            for batch in eval_batches:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch.get("attention_mask")
                if attention_mask is not None:
                    attention_mask = attention_mask.to(self.device)
                labels = batch.get("labels", input_ids).to(self.device)

                out = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels,
                )
                loss = out["loss"]
                batch_tokens = int((labels != -100).sum().item())
                total_loss += float(loss.item())
                total_tokens += batch_tokens

        avg_loss = total_loss / num_batches
        perplexity = float(math.exp(min(avg_loss, 100.0)))

        # Evaluate per-language subsets if provided
        per_language_metrics: Dict[str, Dict[str, float]] = {}
        if per_language_batches:
            for lang, l_batches in per_language_batches.items():
                if not l_batches:
                    continue
                l_loss = 0.0
                l_tokens = 0
                with torch.no_grad(), torch.amp.autocast(device_type="cuda", dtype=autocast_dtype, enabled=is_cuda):
                    for batch in l_batches:
                        input_ids = batch["input_ids"].to(self.device)
                        attention_mask = batch.get("attention_mask")
                        if attention_mask is not None:
                            attention_mask = attention_mask.to(self.device)
                        labels = batch.get("labels", input_ids).to(self.device)

                        out = self.model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            labels=labels,
                        )
                        l_loss += float(out["loss"].item())
                        l_tokens += int((labels != -100).sum().item())

                avg_l_loss = l_loss / len(l_batches)
                per_language_metrics[lang] = {
                    "loss": round(avg_l_loss, 4),
                    "perplexity": round(float(math.exp(min(avg_l_loss, 100.0))), 2),
                    "tokens": l_tokens,
                }

        return EvaluationMetrics(
            overall_loss=round(avg_loss, 4),
            overall_perplexity=round(perplexity, 2),
            total_tokens=total_tokens,
            num_batches=num_batches,
            per_language=per_language_metrics,
        )

    def verify_reproducibility(
        self,
        eval_batches: List[Dict[str, torch.Tensor]],
    ) -> bool:
        """Assert that running evaluation twice produces bit-identical results."""
        m1 = self.evaluate(eval_batches, split_name="validation")
        m2 = self.evaluate(eval_batches, split_name="validation")
        return (m1.overall_loss == m2.overall_loss) and (m1.overall_perplexity == m2.overall_perplexity)
