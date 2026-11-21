"""IGRIS Milestone 3B.59 — Unit tests for Context Window (2048) engine."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Add patch src and scripts
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

from igris.tokenizer.strict import load_candidate_a, load_candidate_b
from context_window_evaluation import (
    MAX_CONTEXT_LENGTH,
    SequenceTier,
    chunk_sequence,
    classify_sequence_tier,
    frame_with_structural_budget,
    truncate_to_context,
    verify_no_automatic_bos_eos,
)

CANDIDATE_A_PATH = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
CANDIDATE_B_PATH = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_b" / "tokenizer.model"


class TestContextWindow(unittest.TestCase):
    def test_sequence_tier_classification(self) -> None:
        """Classifies token lengths into correct sequence tiers."""
        self.assertEqual(classify_sequence_tier(0), SequenceTier.EMPTY)
        self.assertEqual(classify_sequence_tier(1), SequenceTier.SHORT)
        self.assertEqual(classify_sequence_tier(64), SequenceTier.SHORT)
        self.assertEqual(classify_sequence_tier(65), SequenceTier.MEDIUM)
        self.assertEqual(classify_sequence_tier(1024), SequenceTier.MEDIUM)
        self.assertEqual(classify_sequence_tier(1025), SequenceTier.LONG)
        self.assertEqual(classify_sequence_tier(2048), SequenceTier.LONG)
        self.assertEqual(classify_sequence_tier(2049), SequenceTier.OVERFLOW)
        self.assertEqual(classify_sequence_tier(10000), SequenceTier.OVERFLOW)

    def test_truncation_under_budget(self) -> None:
        """Sequences <= 2048 tokens are not truncated."""
        tokens = list(range(500))
        res = truncate_to_context(tokens, max_length=MAX_CONTEXT_LENGTH)
        self.assertFalse(res.was_truncated)
        self.assertEqual(res.truncated_length, 500)
        self.assertEqual(res.tokens, tokens)
        self.assertEqual(res.tier, SequenceTier.MEDIUM)

    def test_truncation_over_budget(self) -> None:
        """Sequences > 2048 tokens are truncated to exactly 2048."""
        tokens = list(range(3500))
        res = truncate_to_context(tokens, max_length=MAX_CONTEXT_LENGTH)
        self.assertTrue(res.was_truncated)
        self.assertEqual(res.original_length, 3500)
        self.assertEqual(res.truncated_length, 2048)
        self.assertEqual(len(res.tokens), 2048)
        self.assertEqual(res.tokens, list(range(2048)))
        self.assertEqual(res.tier, SequenceTier.OVERFLOW)

    def test_sliding_window_chunking(self) -> None:
        """Splits long sequence into overlapping chunks <= 2048 tokens."""
        tokens = list(range(4000))
        chunks = chunk_sequence(tokens, chunk_size=2048, stride=1536)

        # Expected:
        # Chunk 0: 0 .. 2048 (len 2048)
        # Chunk 1: 1536 .. 3584 (len 2048)
        # Chunk 2: 3072 .. 4000 (len 928, is_last=True)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].start_offset, 0)
        self.assertEqual(chunks[0].end_offset, 2048)
        self.assertEqual(len(chunks[0].tokens), 2048)
        self.assertFalse(chunks[0].is_last)

        self.assertEqual(chunks[1].start_offset, 1536)
        self.assertEqual(chunks[1].end_offset, 3584)
        self.assertFalse(chunks[1].is_last)

        self.assertEqual(chunks[2].start_offset, 3072)
        self.assertEqual(chunks[2].end_offset, 4000)
        self.assertEqual(len(chunks[2].tokens), 928)
        self.assertTrue(chunks[2].is_last)

    def test_framing_budget_with_structural_tokens(self) -> None:
        """Framing reserves structural budget and enforces total length <= 2048."""
        content = list(range(100, 2600))  # 2500 content tokens
        # Prefix: <|user|> (ID 10), Suffix: <|assistant|> (ID 11)
        res = frame_with_structural_budget(
            content_tokens=content,
            prefix_structural_ids=[10],
            suffix_structural_ids=[11],
            max_context=MAX_CONTEXT_LENGTH,
        )

        self.assertTrue(res.exceeded_budget)
        self.assertEqual(res.total_tokens, 2048)
        self.assertEqual(res.content_tokens, 2046)  # 2048 - 2
        self.assertEqual(res.sequence_ids[0], 10)
        self.assertEqual(res.sequence_ids[-1], 11)
        self.assertEqual(res.sequence_ids[1:2047], content[:2046])

    def test_framing_rejects_invalid_structural_token(self) -> None:
        """Framing rejects token IDs >= 12 as framing tokens."""
        with self.assertRaises(ValueError):
            frame_with_structural_budget(
                content_tokens=[100],
                prefix_structural_ids=[12],  # ID 12 is NOT a structural token
                suffix_structural_ids=[11],
            )

    def test_no_automatic_bos_eos_candidates(self) -> None:
        """Verifies that neither Candidate A nor Candidate B adds automatic BOS/EOS."""
        tok_a = load_candidate_a(str(CANDIDATE_A_PATH))
        tok_b = load_candidate_b(str(CANDIDATE_B_PATH))

        self.assertTrue(verify_no_automatic_bos_eos(tok_a, "Hello world"))
        self.assertTrue(verify_no_automatic_bos_eos(tok_a, "தமிழ் மொழி"))
        self.assertTrue(verify_no_automatic_bos_eos(tok_b, "Hello world"))
        self.assertTrue(verify_no_automatic_bos_eos(tok_b, "தமிழ் மொழி"))


if __name__ == "__main__":
    unittest.main()
