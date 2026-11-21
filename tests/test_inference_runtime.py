"""Comprehensive test suite for IGRIS Local Inference Engine, Tokenizer, and HTTP API."""
import os
import sys
import unittest
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import torch
from starlette.testclient import TestClient

from igris.inference.engine import (
    CANDIDATE_A_EXPECTED_SHA256,
    IgrisInferenceEngine,
    ModelNotTrainedError,
    TokenizerIntegrityError,
)
from igris.inference.hardware import inspect_hardware
from igris.inference.server import app, get_engine
from igris.model.transformer import (
    IgrisConfig,
    IgrisDecoderTransformer,
    get_baseline_50m_config,
    get_production_config,
    get_test_tiny_config,
)


class TestIgrisInferenceRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.engine = get_engine()

    def test_01_candidate_a_tokenizer_integrity(self):
        """Verify Candidate A tokenizer loads with exact invariant SHA-256."""
        self.assertTrue(self.engine.tokenizer_verified)
        self.assertEqual(self.engine.tokenizer_sha256, CANDIDATE_A_EXPECTED_SHA256)
        self.assertEqual(self.engine.tokenizer.get_vocab_size(), 32768)

    def test_02_trilingual_tokenizer_encoding(self):
        """Verify Candidate A tokenizer correctly processes English, Tamil, and Tanglish."""
        # English
        en_tokens = self.engine.count_tokens("The IGRIS architecture incorporates SwiGLU activations.")
        self.assertGreater(en_tokens, 5)

        # Tamil Unicode
        ta_tokens = self.engine.count_tokens("இக்ரிஸ் மாதிரி தமிழ் மொழியை மிகச் சிறந்த முறையில் பகுப்பாய்வு செய்கிறது.")
        self.assertGreater(ta_tokens, 5)

        # Tanglish
        tanglish_tokens = self.engine.count_tokens("IGRIS architecture epdi design panni irukkeenga bro?")
        self.assertGreater(tanglish_tokens, 5)

    def test_03_hardware_inspection_and_vram_profiling(self):
        """Verify hardware inspection identifies target RTX 3050 and manages safe fallback."""
        hw = inspect_hardware()
        self.assertIn("device", hw.to_dict())
        self.assertIn("device_name", hw.to_dict())
        if hw.cuda_available and hw.safe_for_gpu:
            self.assertIn("cuda", hw.device)
            self.assertGreater(hw.total_vram_gb, 4.0)
        else:
            self.assertEqual(hw.device, "cpu")

    def test_04_architecture_parameter_counts(self):
        """Verify mathematical parameter counts of Authoritative Production and Baseline profiles."""
        prod_cfg = get_production_config()
        prod_cfg.tie_word_embeddings = True
        prod_model = IgrisDecoderTransformer(prod_cfg)
        unique_prod = sum(p.numel() for p in set(prod_model.parameters()))
        self.assertEqual(unique_prod, 79708672)  # 79.7M unique parameters

        base_cfg = get_baseline_50m_config()
        base_cfg.tie_word_embeddings = True
        base_model = IgrisDecoderTransformer(base_cfg)
        unique_base = sum(p.numel() for p in set(base_model.parameters()))
        self.assertEqual(unique_base, 51589632)  # 51.6M unique parameters

    def test_05_health_endpoint(self):
        """Verify GET /health returns status, verified tokenizer, and genuine model state."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["model_state"], "MODEL_NOT_TRAINED")
        self.assertFalse(data["model_loaded"])
        self.assertTrue(data["tokenizer"]["verified"])
        self.assertEqual(data["tokenizer"]["sha256"], CANDIDATE_A_EXPECTED_SHA256)
        self.assertEqual(data["tokenizer"]["vocab_size"], 32768)

    def test_06_models_endpoint(self):
        """Verify GET /v1/models returns registry with production, baseline, and Candidate A."""
        res = self.client.get("/v1/models")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        model_ids = [m["id"] for m in data["data"]]
        self.assertIn("igris-prod-16l", model_ids)
        self.assertIn("igris-50m-baseline", model_ids)
        self.assertIn("igris-candidate-a", model_ids)

    def test_07_untrained_chat_completion_reports_model_not_trained(self):
        """Verify POST /v1/chat/completions strictly reports MODEL_NOT_TRAINED when weights are missing."""
        payload = {
            "model": "igris-prod-16l",
            "messages": [{"role": "user", "content": "Hello IGRIS"}],
            "temperature": 0.7,
            "max_tokens": 128,
            "stream": False,
        }
        res = self.client.post("/v1/chat/completions", json=payload)
        self.assertEqual(res.status_code, 503)
        data = res.json()
        self.assertEqual(data["error"]["code"], "MODEL_NOT_TRAINED")
        self.assertEqual(data["error"]["model_state"], "MODEL_NOT_TRAINED")

    def test_08_invalid_chat_request_handling(self):
        """Verify malformed requests return 400 Bad Request."""
        payload = {
            "model": "igris-prod-16l",
            "messages": [],  # Empty messages
        }
        res = self.client.post("/v1/chat/completions", json=payload)
        self.assertEqual(res.status_code, 400)

    def test_09_synthetic_trained_mode_autoregressive_and_streaming(self):
        """Verify autoregressive decoding, SSE streaming, and actual token counting in trained mode."""
        # Create a tiny test engine with synthetic weights to verify the full generation pipeline
        tiny_cfg = get_test_tiny_config()
        tiny_engine = IgrisInferenceEngine(
            model_name="igris-test-tiny",
            device_override="cpu",
        )
        # Mark as trained for synthetic test execution
        tiny_engine.is_trained = True
        tiny_engine.model_state = "MODEL_LOADED"

        # Test non-streaming generation
        import asyncio

        res = asyncio.run(
            tiny_engine.generate(
                [{"role": "user", "content": "Synthetic prompt test in English"}],
                max_tokens=10,
                temperature=0.0,
            )
        )
        self.assertIn("text", res)
        self.assertIn("usage", res)
        self.assertGreater(res["usage"]["prompt_tokens"], 0)
        self.assertGreaterEqual(res["usage"]["completion_tokens"], 0)

        # Test streaming generator
        async def run_stream():
            chunks = []
            async for chunk in tiny_engine.generate_stream(
                [{"role": "user", "content": "Synthetic stream test"}],
                max_tokens=5,
                temperature=0.0,
            ):
                chunks.append(chunk)
            return chunks

        chunks = asyncio.run(run_stream())
        self.assertGreater(len(chunks), 0)
        final_chunk = chunks[-1]
        self.assertTrue(final_chunk["is_final"])
        self.assertIn("usage", final_chunk)

    def test_10_synthetic_streaming_cancellation(self):
        """Verify streaming cancellation terminates autoregressive generation cleanly."""
        tiny_engine = IgrisInferenceEngine(
            model_name="igris-test-tiny",
            device_override="cpu",
        )
        tiny_engine.is_trained = True

        import asyncio

        cancelled_state = False

        async def cancel_check():
            return cancelled_state

        async def run_cancellation():
            nonlocal cancelled_state
            step_count = 0
            chunks = []
            async for chunk in tiny_engine.generate_stream(
                "Generate with cancellation",
                max_tokens=50,
                cancellation_check=cancel_check,
            ):
                chunks.append(chunk)
                step_count += 1
                if step_count == 2:
                    cancelled_state = True  # Trigger abort
            return chunks

        chunks = asyncio.run(run_cancellation())
        final_chunk = chunks[-1]
        self.assertEqual(final_chunk["finish_reason"], "abort")

    def test_11_trilingual_synthetic_generation(self):
        """Verify trilingual generation accepts Tamil Unicode and Tanglish prompts cleanly."""
        tiny_engine = IgrisInferenceEngine(
            model_name="igris-test-tiny",
            device_override="cpu",
        )
        tiny_engine.is_trained = True

        import asyncio

        # Tamil prompt
        res_ta = asyncio.run(
            tiny_engine.generate(
                [{"role": "user", "content": "இக்ரிஸ் மாடல் செயல்பாடு பற்றி கூறுக"}],
                max_tokens=6,
                temperature=0.0,
            )
        )
        self.assertIn("text", res_ta)
        self.assertGreater(res_ta["usage"]["prompt_tokens"], 0)

        # Tanglish prompt
        res_tanglish = asyncio.run(
            tiny_engine.generate(
                [{"role": "user", "content": "IGRIS architecture epdi work aagum?"}],
                max_tokens=6,
                temperature=0.0,
            )
        )
        self.assertIn("text", res_tanglish)
        self.assertGreater(res_tanglish["usage"]["prompt_tokens"], 0)

    def test_12_out_of_memory_handling(self):
        """Verify out-of-memory exception handler returns clean 503 instead of crashing."""
        from unittest.mock import patch

        with patch("igris.inference.server.get_engine") as mock_get_engine:
            mock_engine = mock_get_engine.return_value
            mock_engine.is_trained = True
            mock_engine.generate.side_effect = torch.cuda.OutOfMemoryError("CUDA out of memory in test")

            res = self.client.post(
                "/v1/chat/completions",
                json={
                    "model": "igris-prod-16l",
                    "messages": [{"role": "user", "content": "Trigger test OOM"}],
                    "stream": False,
                },
            )
            self.assertEqual(res.status_code, 503)
            data = res.json()
            self.assertEqual(data["error"]["code"], "OUT_OF_MEMORY")

    def test_13_v1_health_alias(self):
        """Verify GET /v1/health functions as an identical alias to GET /health."""
        res = self.client.get("/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["model_state"], "MODEL_NOT_TRAINED")

    def test_14_candidate_a_tokenize_endpoint(self):
        """Verify POST /v1/tokenize returns exact Candidate A token IDs and pieces."""
        payload = {"text": "server-ல்", "add_special_tokens": False}
        res = self.client.post("/v1/tokenize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["tokenizer_name"], "Candidate A (ByteLevel BPE)")
        self.assertEqual(data["tokenizer_sha256"], CANDIDATE_A_EXPECTED_SHA256)
        self.assertGreater(data["token_count"], 0)
        self.assertEqual(len(data["tokens"]), data["token_count"])
        self.assertTrue(data["exact_roundtrip"])
        self.assertEqual(data["reconstructed_text"], "server-ல்")
        # Check first token piece structure
        first = data["tokens"][0]
        self.assertIn("id", first)
        self.assertIn("piece", first)
        self.assertIn("decoded", first)
        self.assertIn("raw_hex", first)


if __name__ == "__main__":
    unittest.main()
