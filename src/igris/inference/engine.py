"""Local IGRIS Inference Engine.

Orchestrates:
  - Invariant Candidate A Tokenizer (SHA256: ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561)
  - IgrisDecoderTransformer architecture (Authoritative Production & Baseline profiles)
  - Hardware device selection with safe CPU fallback
  - Autoregressive causal decoding with streaming & cancellation
  - Strict honesty: Reports MODEL_NOT_TRAINED when no trained weights exist.
"""
from __future__ import annotations

import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F
from tokenizers import Tokenizer

from igris.inference.hardware import HardwareProfile, inspect_hardware
from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_baseline_50m_config,
    get_production_config,
    get_test_tiny_config,
)

logger = logging.getLogger(__name__)

CANDIDATE_A_EXPECTED_SHA256 = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
DEFAULT_TOKENIZER_PATH = Path("artifacts/tokenizer/candidate_a/tokenizer.json")


class ModelNotTrainedError(Exception):
    """Raised when inference is attempted on an untrained model checkpoint."""
    pass


class TokenizerIntegrityError(Exception):
    """Raised when Candidate A tokenizer artifact fails SHA-256 verification."""
    pass


class IgrisInferenceEngine:
    def __init__(
        self,
        tokenizer_path: Optional[str | Path] = None,
        checkpoint_path: Optional[str | Path] = None,
        model_name: str = "igris-prod-16l",
        device_override: Optional[str] = None,
    ):
        self.root_dir = Path(__file__).resolve().parents[3]
        self.tokenizer_path = Path(tokenizer_path) if tokenizer_path else self.root_dir / DEFAULT_TOKENIZER_PATH
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.model_name = model_name
        self.device_override = device_override

        # Hardware profiling
        self.hardware: HardwareProfile = inspect_hardware()
        self.device = torch.device(self.device_override or self.hardware.device)

        # Tokenizer initialization
        self.tokenizer: Tokenizer
        self.tokenizer_verified: bool = False
        self.tokenizer_sha256: str = ""
        self._load_and_verify_tokenizer()

        # Model configuration & initialization
        self.config: IgrisConfig = self._resolve_config(self.model_name)
        self.model: IgrisDecoderTransformer = IgrisDecoderTransformer(self.config).to(self.device)
        self.model.eval()

        # Checkpoint status
        self.is_trained: bool = False
        self.model_state: str = "MODEL_NOT_TRAINED"
        self._inspect_and_load_checkpoint()

    def _resolve_config(self, model_name: str) -> IgrisConfig:
        clean = model_name.lower()
        if "50m" in clean or "baseline" in clean:
            cfg = get_baseline_50m_config()
            cfg.tie_word_embeddings = True
            return cfg
        elif "tiny" in clean or "test" in clean:
            return get_test_tiny_config()
        else:
            cfg = get_production_config()
            cfg.tie_word_embeddings = True
            return cfg

    def _load_and_verify_tokenizer(self) -> None:
        if not self.tokenizer_path.exists():
            raise FileNotFoundError(f"Candidate A tokenizer not found at: {self.tokenizer_path}")

        raw_bytes = self.tokenizer_path.read_bytes()
        computed_sha256 = hashlib.sha256(raw_bytes).hexdigest()
        self.tokenizer_sha256 = computed_sha256

        if computed_sha256 != CANDIDATE_A_EXPECTED_SHA256:
            raise TokenizerIntegrityError(
                f"Candidate A SHA-256 mismatch! Expected {CANDIDATE_A_EXPECTED_SHA256}, got {computed_sha256}"
            )

        self.tokenizer = Tokenizer.from_file(str(self.tokenizer_path))
        self.tokenizer_verified = True
        logger.info(
            f"Candidate A tokenizer loaded & verified: vocab={self.tokenizer.get_vocab_size()}, SHA256={computed_sha256}"
        )

    def _inspect_and_load_checkpoint(self) -> None:
        if self.checkpoint_path and self.checkpoint_path.exists():
            try:
                ckpt = torch.load(self.checkpoint_path, map_location=self.device)
                if not isinstance(ckpt, dict):
                    raise ValueError("Checkpoint must be a serialized state dictionary.")

                # 1. Validate tokenizer metadata if present in checkpoint
                ckpt_tok_hash = ckpt.get("tokenizer_sha256")
                if ckpt_tok_hash and ckpt_tok_hash != CANDIDATE_A_EXPECTED_SHA256:
                    raise TokenizerIntegrityError(
                        f"Checkpoint tokenizer hash mismatch: {ckpt_tok_hash} != {CANDIDATE_A_EXPECTED_SHA256}"
                    )

                # 2. Validate architecture configuration if present in checkpoint
                ckpt_cfg = ckpt.get("config")
                if isinstance(ckpt_cfg, dict):
                    for key in ["num_hidden_layers", "hidden_size", "intermediate_size", "vocab_size"]:
                        if key in ckpt_cfg and getattr(self.config, key) != ckpt_cfg[key]:
                            raise ValueError(
                                f"Checkpoint config mismatch on '{key}': expected {getattr(self.config, key)}, got {ckpt_cfg[key]}"
                            )

                state_dict = ckpt.get("model_state_dict", ckpt.get("state_dict", ckpt))
                # 3. Strict loading rejects incompatible weights or dimension mutations
                self.model.load_state_dict(state_dict, strict=True)
                self.is_trained = True
                self.model_state = "MODEL_LOADED"
                logger.info(f"Loaded verified compatible checkpoint from {self.checkpoint_path}")
            except Exception as exc:
                logger.warning(f"Rejected incompatible checkpoint at {self.checkpoint_path}: {exc}")
                self.is_trained = False
                self.model_state = "MODEL_NOT_TRAINED"
        else:
            self.is_trained = False
            self.model_state = "MODEL_NOT_TRAINED"
            logger.info("No trained checkpoint loaded. Runtime initialized in MODEL_NOT_TRAINED state.")

    def format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format messages using Candidate A structural delimiters."""
        chunks: List[str] = ["<|begin_of_text|>"]
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "").strip()
            if role == "system":
                chunks.append(f"<|system|>\n{content}")
            elif role == "user":
                chunks.append(f"<|user|>\n{content}")
            elif role == "assistant":
                chunks.append(f"<|assistant|>\n{content}")
        chunks.append("<|assistant|>\n")
        return "\n".join(chunks)

    def count_tokens(self, text: str) -> int:
        """Return exact token count encoded by Candidate A."""
        return len(self.tokenizer.encode(text).ids)

    @torch.inference_mode()
    async def generate_stream(
        self,
        prompt_or_messages: str | List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 512,
        stop_sequences: Optional[List[str]] = None,
        cancellation_check: Optional[Any] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Autoregressive streaming generator.

        Yields dicts with {"delta_text": str, "is_final": bool, "usage": ...}
        """
        # Strict honesty: If no trained checkpoint exists, report MODEL_NOT_TRAINED
        if not self.is_trained:
            raise ModelNotTrainedError(
                "IGRIS model weights are not trained. Architecture and Candidate A tokenizer are verified, "
                "but no trained checkpoint has been loaded. In accordance with project governance, "
                "untrained random weights cannot generate truthful responses."
            )

        start_time = time.perf_counter()

        if isinstance(prompt_or_messages, list):
            formatted_prompt = self.format_chat_prompt(prompt_or_messages)
        else:
            formatted_prompt = prompt_or_messages

        encoded = self.tokenizer.encode(formatted_prompt)
        prompt_ids = encoded.ids
        prompt_tokens_count = len(prompt_ids)

        if prompt_tokens_count > self.config.max_position_embeddings - 16:
            raise ValueError(
                f"Prompt length ({prompt_tokens_count}) exceeds context budget ({self.config.max_position_embeddings})"
            )

        input_ids = torch.tensor([prompt_ids], dtype=torch.long, device=self.device)
        generated_ids: List[int] = []
        eos_token_id = self.config.eos_token_id

        eos_candidates = [eos_token_id]
        pad_id = self.config.pad_token_id
        if pad_id is not None:
            eos_candidates.append(pad_id)

        finish_reason = "length"

        for step in range(max_tokens):
            if cancellation_check and await cancellation_check():
                finish_reason = "abort"
                break

            outputs = self.model(input_ids)
            next_token_logits = outputs["logits"][:, -1, :]

            # Temperature scaling
            if temperature > 0.0:
                logits = next_token_logits / max(temperature, 1e-4)

                # Top-P (nucleus) filtering
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices[sorted_indices_to_remove]
                    logits[0, indices_to_remove] = -float("Inf")

                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

            token_id = next_token.item()
            generated_ids.append(token_id)

            if token_id in eos_candidates:
                finish_reason = "stop"
                break

            delta_text = self.tokenizer.decode([token_id])

            yield {
                "delta_text": delta_text,
                "is_final": False,
                "token_id": token_id,
            }

            input_ids = torch.cat([input_ids, next_token], dim=1)

            if stop_sequences:
                full_text_so_far = self.tokenizer.decode(generated_ids)
                if any(stop_seq in full_text_so_far for stop_seq in stop_sequences):
                    finish_reason = "stop"
                    break

        total_latency = int((time.perf_counter() - start_time) * 1000)
        yield {
            "delta_text": "",
            "is_final": True,
            "finish_reason": finish_reason,
            "usage": {
                "prompt_tokens": prompt_tokens_count,
                "completion_tokens": len(generated_ids),
                "total_tokens": prompt_tokens_count + len(generated_ids),
                "latency_ms": total_latency,
            },
        }

    @torch.inference_mode()
    async def generate(
        self,
        prompt_or_messages: str | List[Dict[str, str]],
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 512,
        stop_sequences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Non-streaming complete generation."""
        collected_text = ""
        final_usage = None
        finish_reason = "length"

        async for chunk in self.generate_stream(
            prompt_or_messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop_sequences=stop_sequences,
        ):
            if chunk.get("delta_text"):
                collected_text += chunk["delta_text"]
            if chunk.get("is_final"):
                final_usage = chunk.get("usage")
                finish_reason = chunk.get("finish_reason", "stop")

        return {
            "text": collected_text,
            "usage": final_usage,
            "finish_reason": finish_reason,
            "model_state": self.model_state,
        }
