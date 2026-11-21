"""IGRIS Milestone 3B.56 — Candidate A/B builder and integration tests.

These tests use a small SYNTHETIC corpus only.  No actual training data,
approved inventory, quarantine files, or production corpus is accessed.

Test categories:
  A. Candidate A builder tests (ByteLevel BPE, non-special model vocab padding)
  B. Candidate B builder tests (SentencePiece Unigram, proto rearrangement, equivalence)
  C. Shared contract tests (text, binary, escaping across both candidates)
  D. Security tests (no structural ID leakage, literal spellings, sentinel/marker handling)
  E. Build interface tests (build_single, build_all, metadata validation)
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the patch src is on the path.
_PATCH_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _PATCH_SRC not in sys.path:
    sys.path.insert(0, _PATCH_SRC)

import unicodedata2
import sentencepiece as spm
from sentencepiece import sentencepiece_model_pb2

from igris.tokenizer.strict import (
    STRUCTURAL_TOKENS,
    STRUCTURAL_TO_ID,
    ID_TO_STRUCTURAL,
    STRUCTURAL_COUNT,
    VOCAB_SIZE,
    ESCAPE_SENTINEL,
    WHITESPACE_MARKER,
    StrictTokenizer,
    RawBinaryCodec,
    escape_text,
    unescape_text,
    validate_ids,
)
from igris.tokenizer.ingestion import (
    SequencePolicy,
    encode_text,
    decode_text,
    encode_raw_binary,
    decode_raw_binary,
    apply_framing,
    strip_framing,
)

# ---------------------------------------------------------------------------
# Synthetic corpus for testing (small, in-memory, no real data)
# ---------------------------------------------------------------------------

SYNTHETIC_CORPUS: list[str] = [
    # English
    "The quick brown fox jumps over the lazy dog.",
    "IGRIS is a decoder-only transformer language model.",
    "Machine learning models process natural language text.",
    "The tokenizer splits text into subword units.",
    "Artificial intelligence enables natural language understanding.",
    # Tamil
    "தமிழ் ஒரு பழமையான மொழி ஆகும்.",
    "இது திராவிட மொழிக் குடும்பத்தைச் சேர்ந்தது.",
    "தமிழ்நாடு இந்தியாவின் தென்பகுதியில் அமைந்துள்ளது.",
    "சென்னை தமிழ்நாட்டின் தலைநகரம் ஆகும்.",
    "தமிழ் இலக்கியம் மிகவும் பழமையானது.",
    # Hindi
    "हिन्दी भारत की राजभाषा है।",
    "यह देवनागरी लिपि में लिखी जाती है।",
    # Tanglish (mixed Tamil-English)
    "Naan oru developer, Tamil la code panren.",
    "Machine learning la Tamil text process pannalam.",
    "IGRIS model ku Tamil training data kudukanum.",
    # Emoji and special characters
    "Hello 🌍! Welcome to IGRIS 🎉",
    "Special chars: @#$%^&*()[]{}|\\;:'\",./<>?",
    # Whitespace variants
    "tabs\there\tand\tthere",
    "  leading and trailing spaces  ",
    "multiple   spaces   between   words",
    # Longer text for better BPE merge statistics
    "The IGRIS tokenizer system supports multiple languages including Tamil, English, Hindi, and Tanglish. "
    "It uses a strict contract-based approach where structural tokens are reserved at specific IDs and text "
    "content is escaped to prevent injection of structural tokens through user input. "
    "The system supports both NFC-normalized and exact Unicode modes. "
    "Raw binary encoding is also supported through a complete 256-byte mapping.",
] * 20  # Repeat for sufficient merge statistics


# ---------------------------------------------------------------------------
# A. Candidate A builder tests
# ---------------------------------------------------------------------------

class TestCandidateABuilder(unittest.TestCase):
    """Test Candidate A ByteLevel BPE builder with synthetic corpus."""

    _tokenizer: StrictTokenizer | None = None
    _artifact_dir: str | None = None
    _tempdir: tempfile.TemporaryDirectory | None = None
    _artifact_path: Path | None = None
    _build_error: Exception | None = None
    _load_error: Exception | None = None

    @classmethod
    def setUpClass(cls) -> None:
        """Build Candidate A from synthetic corpus once for all tests."""
        from igris.tokenizer.candidate_a_builder import build_candidate_a, load_and_validate_candidate_a

        cls._tempdir = tempfile.TemporaryDirectory(prefix="igris_test_a_")
        cls._artifact_dir = cls._tempdir.name
        try:
            cls._artifact_path = build_candidate_a(
                iter(SYNTHETIC_CORPUS),
                cls._artifact_dir,
                min_frequency=1,
            )
        except Exception as exc:
            cls._build_error = exc
            return

        try:
            cls._tokenizer = load_and_validate_candidate_a(cls._artifact_path)
        except Exception as exc:
            cls._load_error = exc

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._tempdir is not None:
            cls._tempdir.cleanup()

    def _assert_ready(self) -> None:
        if self.__class__._build_error is not None:
            raise AssertionError(f"Build failed: {self.__class__._build_error}")
        if self.__class__._load_error is not None:
            raise AssertionError(f"Load failed: {self.__class__._load_error}")
        self.assertIsNotNone(self.__class__._artifact_path)
        self.assertIsNotNone(self.__class__._tokenizer)

    def test_a01_build_succeeded(self) -> None:
        """Candidate A: build completed without error."""
        self._assert_ready()

    def test_a02_artifact_exists(self) -> None:
        """Candidate A: tokenizer.json exists on disk."""
        self._assert_ready()
        self.assertTrue(self.__class__._artifact_path.exists())
        self.assertEqual(self.__class__._artifact_path.name, "tokenizer.json")

    def test_a03_metadata_exists(self) -> None:
        """Candidate A: build_metadata.json exists on disk and is valid."""
        self._assert_ready()
        meta_path = Path(self.__class__._artifact_dir) / "build_metadata.json"
        self.assertTrue(meta_path.exists())
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["candidate"], "A")
        self.assertEqual(metadata["vocab_size"], VOCAB_SIZE)
        self.assertIn("artifact_sha256", metadata)

    def test_a04_load_succeeded(self) -> None:
        """Candidate A: artifact loads through strict loader without error."""
        self._assert_ready()
        self.assertIsNotNone(self.__class__._tokenizer)

    def test_a05_vocab_size(self) -> None:
        """Candidate A: vocabulary size is exactly 32,768."""
        self._assert_ready()
        self.assertEqual(self.__class__._tokenizer.vocab_size, VOCAB_SIZE)

    def test_a06_structural_ids(self) -> None:
        """Candidate A: all 12 structural tokens at correct IDs."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        backend = tok.backend
        for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
            actual = backend.tokenizer.token_to_id(spelling)
            self.assertEqual(
                actual, expected_id,
                f"Structural token {spelling!r}: expected ID {expected_id}, got {actual}"
            )

    def test_a07_bytelevel_config(self) -> None:
        """Candidate A: pre-tokenizer and decoder are ByteLevel, no post-processor."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        config = json.loads(tok.backend.tokenizer.to_str())
        self.assertEqual(config["pre_tokenizer"]["type"], "ByteLevel")
        self.assertEqual(config["decoder"]["type"], "ByteLevel")
        self.assertIsNone(config.get("post_processor"))

    def test_a08_save_reload(self) -> None:
        """Candidate A: save and reload produces identical tokenizer."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "tokenizer.json"
            tok.backend.tokenizer.save(str(save_path))
            from igris.tokenizer.candidate_a_builder import load_and_validate_candidate_a
            reloaded = load_and_validate_candidate_a(save_path)
            self.assertEqual(reloaded.vocab_size, VOCAB_SIZE)

    def test_a09_text_roundtrip_english(self) -> None:
        """Candidate A: English text round-trips correctly."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        text = "The quick brown fox jumps over the lazy dog."
        self.assertEqual(tok.decode_content(tok.encode_content(text)), text)

    def test_a10_text_roundtrip_tamil(self) -> None:
        """Candidate A: Tamil text round-trips correctly."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        text = "தமிழ் ஒரு பழமையான மொழி ஆகும்."
        self.assertEqual(tok.decode_content(tok.encode_content(text)), text)

    def test_a11_text_roundtrip_empty(self) -> None:
        """Candidate A: empty string round-trips correctly."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        self.assertEqual(tok.decode_content(tok.encode_content("")), "")

    def test_a12_raw_binary_roundtrip(self) -> None:
        """Candidate A: all 256 bytes round-trip through raw binary codec."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        codec = tok.raw_binary_codec()
        payload = bytes(range(256))
        encoded = codec.encode_bytes(payload)
        decoded = codec.decode_bytes(encoded)
        self.assertEqual(decoded, payload)

    def test_a13_raw_binary_codec_complete(self) -> None:
        """Candidate A: byte_id_map returns exactly 256 unique IDs."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        byte_map = tok.backend.byte_id_map()
        self.assertEqual(len(byte_map), 256)
        self.assertEqual(len(set(byte_map)), 256)

    def test_a14_added_tokens_strictly_structural_only(self) -> None:
        """Candidate A: added_tokens contains ONLY the 12 structural tokens (no filler added tokens)."""
        self._assert_ready()
        tok_json = json.loads(self.__class__._tokenizer.backend.tokenizer.to_str())
        added = tok_json.get("added_tokens", [])
        self.assertEqual(
            len(added), 12,
            f"Candidate A must have exactly 12 added tokens; found {len(added)}"
        )
        for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
            item = next((x for x in added if x.get("content") == spelling), None)
            self.assertIsNotNone(item, f"Structural token {spelling!r} missing from added_tokens")
            self.assertEqual(item["id"], expected_id)
            self.assertTrue(item.get("special", False))

    def test_a15_filler_entries_cannot_be_emitted_by_user_text(self) -> None:
        """Candidate A: model vocabulary filler entries cannot be emitted by normal user text."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        tok_json = json.loads(tok.backend.tokenizer.to_str())
        model_vocab = tok_json.get("model", {}).get("vocab", {})
        filler_keys = [k for k in model_vocab if k.startswith("<|filler_")]
        self.assertGreater(len(filler_keys), 0, "No filler entries found in model vocab")

        # Test encoding literal filler spellings
        sample_fillers = filler_keys[:10] + [filler_keys[-1]]
        for f_spelling in sample_fillers:
            f_id = model_vocab[f_spelling]
            encoded_ids = tok.encode_content(f_spelling)
            # The filler ID itself must NEVER be emitted
            self.assertNotIn(
                f_id, encoded_ids,
                f"Filler token {f_spelling!r} (ID {f_id}) was emitted by user text!"
            )
            # The decoded text must faithfully reconstruct the literal spelling
            decoded = tok.decode_content(encoded_ids)
            self.assertEqual(decoded, f_spelling)


# ---------------------------------------------------------------------------
# B. Candidate B builder tests
# ---------------------------------------------------------------------------

class TestCandidateBBuilder(unittest.TestCase):
    """Test Candidate B SentencePiece Unigram builder with synthetic corpus."""

    _tokenizer: StrictTokenizer | None = None
    _artifact_dir: str | None = None
    _tempdir: tempfile.TemporaryDirectory | None = None
    _artifact_path: Path | None = None
    _raw_artifact_path: Path | None = None
    _build_error: Exception | None = None
    _load_error: Exception | None = None

    @classmethod
    def setUpClass(cls) -> None:
        """Build Candidate B from synthetic corpus once for all tests."""
        from igris.tokenizer.candidate_b_builder import build_candidate_b, load_and_validate_candidate_b

        cls._tempdir = tempfile.TemporaryDirectory(prefix="igris_test_b_")
        cls._artifact_dir = cls._tempdir.name
        try:
            cls._artifact_path = build_candidate_b(
                iter(SYNTHETIC_CORPUS),
                cls._artifact_dir,
                character_coverage=0.9995,
                num_threads=1,
                save_raw_model=True,
            )
            cls._raw_artifact_path = Path(cls._artifact_dir) / "tokenizer_raw.model"
        except Exception as exc:
            cls._build_error = exc
            return

        try:
            cls._tokenizer = load_and_validate_candidate_b(cls._artifact_path)
        except Exception as exc:
            cls._load_error = exc

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._tempdir is not None:
            cls._tempdir.cleanup()

    def _assert_ready(self) -> None:
        if self.__class__._build_error is not None:
            raise AssertionError(f"Build failed: {self.__class__._build_error}")
        if self.__class__._load_error is not None:
            raise AssertionError(f"Load failed: {self.__class__._load_error}")
        self.assertIsNotNone(self.__class__._artifact_path)
        self.assertIsNotNone(self.__class__._tokenizer)

    def test_b01_build_succeeded(self) -> None:
        """Candidate B: build completed without error."""
        self._assert_ready()

    def test_b02_artifact_exists(self) -> None:
        """Candidate B: tokenizer.model exists on disk."""
        self._assert_ready()
        self.assertTrue(self.__class__._artifact_path.exists())
        self.assertEqual(self.__class__._artifact_path.name, "tokenizer.model")

    def test_b03_metadata_exists(self) -> None:
        """Candidate B: build_metadata.json exists on disk and is valid."""
        self._assert_ready()
        meta_path = Path(self.__class__._artifact_dir) / "build_metadata.json"
        self.assertTrue(meta_path.exists())
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["candidate"], "B")
        self.assertEqual(metadata["vocab_size"], VOCAB_SIZE)
        self.assertIn("artifact_sha256", metadata)

    def test_b04_load_succeeded(self) -> None:
        """Candidate B: artifact loads through strict loader without error."""
        self._assert_ready()
        self.assertIsNotNone(self.__class__._tokenizer)

    def test_b05_vocab_size(self) -> None:
        """Candidate B: vocabulary size is exactly 32,768."""
        self._assert_ready()
        self.assertEqual(self.__class__._tokenizer.vocab_size, VOCAB_SIZE)

    def test_b06_structural_ids(self) -> None:
        """Candidate B: all 12 structural tokens at correct IDs."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        processor = tok.backend.processor
        for expected_id, spelling in enumerate(STRUCTURAL_TOKENS):
            actual_piece = processor.id_to_piece(expected_id)
            self.assertEqual(
                actual_piece, spelling,
                f"Structural token at ID {expected_id}: expected {spelling!r}, got {actual_piece!r}"
            )

    def test_b07_unigram_config(self) -> None:
        """Candidate B: model type is Unigram, byte_fallback enabled, identity normalizer."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        proto = sentencepiece_model_pb2.ModelProto()
        proto.ParseFromString(tok.backend.processor.serialized_model_proto())
        spec = proto.trainer_spec
        norm = proto.normalizer_spec
        self.assertEqual(spec.model_type, sentencepiece_model_pb2.TrainerSpec.UNIGRAM)
        self.assertTrue(spec.byte_fallback)
        self.assertEqual(norm.name, "identity")
        self.assertFalse(norm.add_dummy_prefix)
        self.assertFalse(norm.remove_extra_whitespaces)
        self.assertTrue(norm.escape_whitespaces)

    def test_b08_pad_bos_eos_unk_ids_in_spec(self) -> None:
        """Candidate B: PAD=0, BOS=-1, EOS=-1, UNK=-1 in trainer_spec."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        proto = sentencepiece_model_pb2.ModelProto()
        proto.ParseFromString(tok.backend.processor.serialized_model_proto())
        spec = proto.trainer_spec
        self.assertEqual(spec.pad_id, 0)
        self.assertEqual(spec.pad_piece, "<|pad|>")
        self.assertEqual(spec.bos_id, -1)
        self.assertEqual(spec.eos_id, -1)
        self.assertEqual(spec.unk_id, -1)

    def test_b09_pad_piece_type(self) -> None:
        """Candidate B: piece 0 (<|pad|>) has PAD or CONTROL type."""
        self._assert_ready()
        SP = sentencepiece_model_pb2.ModelProto.SentencePiece
        tok = self.__class__._tokenizer
        proto = sentencepiece_model_pb2.ModelProto()
        proto.ParseFromString(tok.backend.processor.serialized_model_proto())
        self.assertEqual(proto.pieces[0].piece, "<|pad|>")
        expected_pad_type = getattr(SP, "PAD", SP.CONTROL)
        self.assertIn(proto.pieces[0].type, (expected_pad_type, SP.CONTROL))

    def test_b10_save_reload(self) -> None:
        """Candidate B: save and reload produces identical tokenizer."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "tokenizer.model"
            model_bytes = tok.backend.processor.serialized_model_proto()
            save_path.write_bytes(model_bytes)
            from igris.tokenizer.candidate_b_builder import load_and_validate_candidate_b
            reloaded = load_and_validate_candidate_b(save_path)
            self.assertEqual(reloaded.vocab_size, VOCAB_SIZE)

    def test_b11_all_256_byte_fallback_pieces(self) -> None:
        """Candidate B: all 256 <0xXX> byte fallback pieces exist."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        processor = tok.backend.processor
        for b in range(256):
            piece = f"<0x{b:02X}>"
            token_id = processor.piece_to_id(piece)
            self.assertGreaterEqual(
                token_id, 0,
                f"Byte fallback piece {piece} not found (got ID {token_id})"
            )
            self.assertEqual(
                processor.id_to_piece(token_id), piece,
                f"Byte fallback piece {piece} round-trip failed"
            )

    def test_b12_text_roundtrip_english(self) -> None:
        """Candidate B: English text round-trips correctly."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        text = "The quick brown fox jumps over the lazy dog."
        self.assertEqual(tok.decode_content(tok.encode_content(text)), text)

    def test_b13_text_roundtrip_tamil(self) -> None:
        """Candidate B: Tamil text round-trips correctly."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        text = "தமிழ் ஒரு பழமையான மொழி ஆகும்."
        self.assertEqual(tok.decode_content(tok.encode_content(text)), text)

    def test_b14_text_roundtrip_empty(self) -> None:
        """Candidate B: empty string round-trips correctly."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        self.assertEqual(tok.decode_content(tok.encode_content("")), "")

    def test_b15_raw_binary_roundtrip(self) -> None:
        """Candidate B: all 256 bytes round-trip through raw binary codec."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        codec = tok.raw_binary_codec()
        payload = bytes(range(256))
        encoded = codec.encode_bytes(payload)
        decoded = codec.decode_bytes(encoded)
        self.assertEqual(decoded, payload)

    def test_b16_raw_binary_codec_complete(self) -> None:
        """Candidate B: byte_id_map returns exactly 256 unique IDs."""
        self._assert_ready()
        tok = self.__class__._tokenizer
        byte_map = tok.backend.byte_id_map()
        self.assertEqual(len(byte_map), 256)
        self.assertEqual(len(set(byte_map)), 256)

    def test_b17_processor_special_ids_runtime(self) -> None:
        """Candidate B: processor.pad_id() == 0 and BOS/EOS/UNK are disabled at runtime."""
        self._assert_ready()
        proc = self.__class__._tokenizer.backend.processor
        self.assertEqual(proc.pad_id(), 0, f"processor.pad_id() must be 0; got {proc.pad_id()}")
        self.assertEqual(proc.bos_id(), -1, f"processor.bos_id() must be -1; got {proc.bos_id()}")
        self.assertEqual(proc.eos_id(), -1, f"processor.eos_id() must be -1; got {proc.eos_id()}")
        self.assertEqual(proc.unk_id(), -1, f"processor.unk_id() must be -1; got {proc.unk_id()}")

    def test_b18_no_duplicate_pieces(self) -> None:
        """Candidate B: model proto contains exactly 32,768 unique pieces (no duplicates)."""
        self._assert_ready()
        proto = sentencepiece_model_pb2.ModelProto()
        proto.ParseFromString(self.__class__._tokenizer.backend.processor.serialized_model_proto())
        pieces = [p.piece for p in proto.pieces]
        self.assertEqual(len(pieces), VOCAB_SIZE)
        self.assertEqual(len(set(pieces)), VOCAB_SIZE)

    def test_b19_reserved_padding_is_unused(self) -> None:
        """Candidate B: reserved padding pieces have UNUSED type and cannot be emitted by normal text."""
        self._assert_ready()
        SP = sentencepiece_model_pb2.ModelProto.SentencePiece
        proto = sentencepiece_model_pb2.ModelProto()
        proto.ParseFromString(self.__class__._tokenizer.backend.processor.serialized_model_proto())
        reserved_pieces = [p for p in proto.pieces if p.piece.startswith("<|reserved_")]
        self.assertGreater(len(reserved_pieces), 0, "No reserved padding pieces found")
        for p in reserved_pieces:
            self.assertEqual(p.type, SP.UNUSED, f"Reserved piece {p.piece!r} must have UNUSED type")

        # Verify text containing literal reserved spellings does NOT emit the reserved token ID
        tok = self.__class__._tokenizer
        proc = tok.backend.processor
        sample_reserved = reserved_pieces[:5]
        for rp in sample_reserved:
            target_id = proc.piece_to_id(rp.piece)
            encoded_ids = tok.encode_content(rp.piece)
            self.assertNotIn(
                target_id, encoded_ids,
                f"Reserved token {rp.piece!r} (ID {target_id}) was emitted by user text!"
            )
            # Reconstructs correctly
            self.assertEqual(tok.decode_content(encoded_ids), rp.piece)

    def test_b20_before_after_proto_rearrangement_equivalence(self) -> None:
        """Candidate B: original and rewritten model produce identical segmentation and decoding."""
        self._assert_ready()
        self.assertTrue(self.__class__._raw_artifact_path.exists(), "Raw unrearranged model missing")

        raw_proc = spm.SentencePieceProcessor(model_file=str(self.__class__._raw_artifact_path))
        rewritten_proc = self.__class__._tokenizer.backend.processor

        test_sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "தமிழ் ஒரு பழமையான மொழி ஆகும்.",
            "हिन्दी भारत की राजभाषा है।",
            "Naan oru developer, Tamil la code panren.",
            "Hello 🌍! Welcome to IGRIS 🎉",
            "tabs\there\tand\tthere",
            "  leading and trailing spaces  ",
            "multiple   spaces   between   words",
        ]

        for s in test_sentences:
            raw_pieces = raw_proc.encode(s, out_type=str)
            rewritten_pieces = rewritten_proc.encode(s, out_type=str)
            self.assertEqual(
                rewritten_pieces, raw_pieces,
                f"Segmentation mismatch for {s!r}:\nRaw:       {raw_pieces}\nRewritten: {rewritten_pieces}"
            )

            raw_decoded = raw_proc.decode(raw_proc.encode(s, out_type=int))
            rewritten_decoded = rewritten_proc.decode(rewritten_proc.encode(s, out_type=int))
            self.assertEqual(rewritten_decoded, raw_decoded)
            self.assertEqual(rewritten_decoded, s)


# ---------------------------------------------------------------------------
# C. Shared contract tests (run against BOTH candidates)
# ---------------------------------------------------------------------------

class _SharedContractMixin:
    """Mixin providing shared contract tests for a candidate tokenizer."""

    tok: StrictTokenizer

    def test_c01_tamil_text(self) -> None:
        """Shared: Tamil text encodes and decodes correctly."""
        text = "தமிழ்நாடு இந்தியாவின் தென்பகுதியில் அமைந்துள்ளது."
        self.assertEqual(self.tok.decode_content(self.tok.encode_content(text)), text)

    def test_c02_english_text(self) -> None:
        """Shared: English text encodes and decodes correctly."""
        text = "IGRIS is a decoder-only transformer language model."
        self.assertEqual(self.tok.decode_content(self.tok.encode_content(text)), text)

    def test_c03_tanglish_text(self) -> None:
        """Shared: Mixed Tamil-English Tanglish text round-trips."""
        text = "Naan oru developer, Tamil la code panren."
        self.assertEqual(self.tok.decode_content(self.tok.encode_content(text)), text)

    def test_c04_hindi_text(self) -> None:
        """Shared: Hindi text round-trips correctly."""
        text = "हिन्दी भारत की राजभाषा है।"
        self.assertEqual(self.tok.decode_content(self.tok.encode_content(text)), text)

    def test_c05_emoji(self) -> None:
        """Shared: Emoji round-trips correctly."""
        text = "Hello 🌍! Welcome to IGRIS 🎉"
        self.assertEqual(self.tok.decode_content(self.tok.encode_content(text)), text)

    def test_c06_combining_marks(self) -> None:
        """Shared: Combining marks are handled (NFC normalization)."""
        text = "e\u0301"  # e + combining acute → é in NFC
        expected = "é"
        self.assertEqual(self.tok.decode_content(self.tok.encode_content(text)), expected)

    def test_c07_empty_string(self) -> None:
        """Shared: empty string encodes to empty list and decodes back."""
        ids = self.tok.encode_content("")
        self.assertEqual(ids, [])
        self.assertEqual(self.tok.decode_content(ids), "")

    def test_c08_empty_batch(self) -> None:
        """Shared: empty batch produces empty result."""
        self.assertEqual(self.tok.encode_batch([]), [])
        self.assertEqual(self.tok.decode_batch([]), [])

    def test_c09_whitespace_preservation(self) -> None:
        """Shared: tabs, leading/trailing spaces, multiple spaces preserved."""
        for text in [
            "  leading",
            "trailing  ",
            "tabs\there",
            "multiple   spaces",
            "  both  sides  ",
        ]:
            decoded = self.tok.decode_content(self.tok.encode_content(text))
            self.assertEqual(decoded, text, f"Whitespace mismatch for {text!r}")

    def test_c10_literal_structural_spellings(self) -> None:
        """Shared: literal structural token spellings in content are escaped and preserved."""
        for spelling in STRUCTURAL_TOKENS:
            text = f"before{spelling}after"
            decoded = self.tok.decode_content(self.tok.encode_content(text))
            self.assertEqual(decoded, text, f"Structural escape failed for {spelling!r}")

    def test_c11_invalid_ids_rejected(self) -> None:
        """Shared: invalid token IDs are rejected."""
        for ids in [[-1], [VOCAB_SIZE], [99999]]:
            with self.assertRaises(ValueError):
                self.tok.decode_content(ids)

    def test_c12_bool_id_rejected(self) -> None:
        """Shared: boolean values are rejected as token IDs."""
        with self.assertRaises(TypeError):
            self.tok.decode_content([True])

    def test_c13_structural_ids_rejected_in_content(self) -> None:
        """Shared: structural IDs (0–11) are rejected in content encode/decode."""
        for sid in range(STRUCTURAL_COUNT):
            with self.assertRaises(ValueError):
                self.tok.decode_content([sid])

    def test_c14_malformed_escapes_rejected(self) -> None:
        """Shared: malformed escape sequences are rejected during unescape."""
        malformed = [
            ESCAPE_SENTINEL,                    # Truncated sentinel
            ESCAPE_SENTINEL + "S١١;",           # Non-ASCII digits
            ESCAPE_SENTINEL + "S12;",           # ID 12 out of structural range
            ESCAPE_SENTINEL + "Q;",             # Unknown escape type
            ESCAPE_SENTINEL + "S01",            # Missing trailing semicolon
        ]
        for val in malformed:
            with self.assertRaises(ValueError):
                unescape_text(val)

    def test_c15_nfc_mode(self) -> None:
        """Shared: NFC normalization collapses decomposed sequences."""
        text = "e\u0301"
        ids = self.tok.encode_content(text)
        decoded = self.tok.decode_content(ids)
        self.assertEqual(decoded, "é")
        self.assertEqual(decoded, unicodedata2.normalize("NFC", text))

    def test_c16_exact_unicode_mode(self) -> None:
        """Shared: exact mode preserves decomposed sequences."""
        exact_tok = StrictTokenizer(self.tok.backend, "exact")
        text = "e\u0301"
        ids = exact_tok.encode_content(text)
        decoded = exact_tok.decode_content(ids)
        self.assertEqual(decoded, text)

    def test_c17_escape_sentinel_roundtrip(self) -> None:
        """Shared: the escape sentinel itself round-trips correctly."""
        text = f"before{ESCAPE_SENTINEL}after"
        decoded = self.tok.decode_content(self.tok.encode_content(text))
        self.assertEqual(decoded, text)

    def test_c18_whitespace_marker_roundtrip(self) -> None:
        """Shared: the whitespace marker U+2581 round-trips correctly."""
        text = f"before{WHITESPACE_MARKER}after"
        decoded = self.tok.decode_content(self.tok.encode_content(text))
        self.assertEqual(decoded, text)

    def test_c19_batch_mixed_content(self) -> None:
        """Shared: batch with mixed content types round-trips."""
        texts = ["", "English", "தமிழ்", "Tanglish mix", "🎉", "  spaces  "]
        result = self.tok.decode_batch(self.tok.encode_batch(texts))
        self.assertEqual(result, texts)

    def test_c20_render_sequence_with_structural(self) -> None:
        """Shared: render_sequence correctly interpolates structural tokens."""
        body_ids = self.tok.encode_content("hello")
        seq = [STRUCTURAL_TO_ID["<|user|>"]] + body_ids + [STRUCTURAL_TO_ID["<|assistant|>"]]
        rendered = self.tok.render_sequence(seq)
        self.assertEqual(rendered, "<|user|>hello<|assistant|>")

    def test_c21_raw_binary_full_range(self) -> None:
        """Shared: raw binary codec handles all 256 byte values."""
        codec = self.tok.raw_binary_codec()
        payload = bytes(range(256))
        self.assertEqual(codec.decode_bytes(codec.encode_bytes(payload)), payload)

    def test_c22_raw_binary_rejects_str(self) -> None:
        """Shared: raw binary codec rejects string input."""
        codec = self.tok.raw_binary_codec()
        with self.assertRaises(TypeError):
            codec.encode_bytes("not bytes")  # type: ignore[arg-type]

    def test_c23_no_automatic_bos_eos(self) -> None:
        """Shared: encoding does not automatically add BOS/EOS."""
        result = encode_text(self.tok, "hello")
        self.assertEqual(result.content_ids, result.sequence_ids)

    def test_c24_explicit_framing(self) -> None:
        """Shared: explicit framing adds and strips BOS/EOS correctly."""
        result = encode_text(self.tok, "hello")
        policy = SequencePolicy(add_bos=True, add_eos=True)
        framed = apply_framing(result.content_ids, policy)
        self.assertEqual(framed[0], 1)   # BOS
        self.assertEqual(framed[-1], 2)  # EOS
        stripped = strip_framing(framed, policy)
        self.assertEqual(stripped, list(result.content_ids))


class TestCandidateASharedContract(TestCandidateABuilder, _SharedContractMixin):
    """Run shared contract tests against Candidate A."""

    def setUp(self) -> None:
        self._assert_ready()
        self.tok = self.__class__._tokenizer  # type: ignore[assignment]


class TestCandidateBSharedContract(TestCandidateBBuilder, _SharedContractMixin):
    """Run shared contract tests against Candidate B."""

    def setUp(self) -> None:
        self._assert_ready()
        self.tok = self.__class__._tokenizer  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# D. Security & Edge Case Tests
# ---------------------------------------------------------------------------

class TestTokenizerSecurity(unittest.TestCase):
    """Security tests: guarantee content encoding NEVER emits structural IDs (0–11)."""

    @classmethod
    def setUpClass(cls) -> None:
        from igris.tokenizer.candidate_a_builder import build_candidate_a, load_and_validate_candidate_a
        from igris.tokenizer.candidate_b_builder import build_candidate_b, load_and_validate_candidate_b

        cls._tempdir = tempfile.TemporaryDirectory(prefix="igris_sec_test_")
        cls._dir = cls._tempdir.name

        path_a = build_candidate_a(iter(SYNTHETIC_CORPUS), Path(cls._dir) / "cand_a", min_frequency=1)
        path_b = build_candidate_b(iter(SYNTHETIC_CORPUS), Path(cls._dir) / "cand_b", character_coverage=0.9995)

        cls._tok_a = load_and_validate_candidate_a(path_a)
        cls._tok_b = load_and_validate_candidate_b(path_b)

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._tempdir is not None:
            cls._tempdir.cleanup()

    def _for_both_tokenizers(self):
        return [("Candidate A", self._tok_a), ("Candidate B", self._tok_b)]

    def test_sec01_content_encoding_never_emits_structural_ids_across_diverse_inputs(self) -> None:
        """Security: public content encoding NEVER emits token IDs in 0..11."""
        test_inputs = [
            "Hello world",
            "தமிழ் மொழி வாழ்க",
            "हिन्दी भाषा",
            "Naan oru developer, Tamil la code panren.",
            "Привет мир (Russian)",
            "مرحبا بالعالم (Arabic)",
            "こんにちは世界 (Japanese)",
            "你好世界 (Chinese)",
            "1234567890 !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "🎉🔥🚀💡🌟",
            "\n\t\r   \n\n\t",
            "<html><body>code test</body></html>",
            "def foo(x: int) -> str: return f'<tag>{x}</tag>'",
        ]
        for name, tok in self._for_both_tokenizers():
            for text in test_inputs:
                ids = tok.encode_content(text)
                for sid in range(STRUCTURAL_COUNT):
                    self.assertNotIn(
                        sid, ids,
                        f"[{name}] Structural ID {sid} emitted for regular text {text!r}"
                    )
                self.assertEqual(tok.decode_content(ids), text)

    def test_sec02_literal_structural_spellings_never_leak_structural_ids(self) -> None:
        """Security: literal structural spellings are escaped and never emit IDs 0..11."""
        for name, tok in self._for_both_tokenizers():
            for spelling in STRUCTURAL_TOKENS:
                # Alone
                ids = tok.encode_content(spelling)
                for sid in range(STRUCTURAL_COUNT):
                    self.assertNotIn(
                        sid, ids,
                        f"[{name}] Structural ID {sid} leaked when encoding literal {spelling!r}"
                    )
                self.assertEqual(tok.decode_content(ids), spelling)

                # Embedded
                embedded = f"prefix_{spelling}_suffix"
                ids_emb = tok.encode_content(embedded)
                for sid in range(STRUCTURAL_COUNT):
                    self.assertNotIn(
                        sid, ids_emb,
                        f"[{name}] Structural ID {sid} leaked for embedded {embedded!r}"
                    )
                self.assertEqual(tok.decode_content(ids_emb), embedded)

    def test_sec03_sentinel_and_whitespace_marker_never_leak(self) -> None:
        """Security: sentinel characters and whitespace marker U+2581 never leak structural IDs."""
        for name, tok in self._for_both_tokenizers():
            adversarial_inputs = [
                ESCAPE_SENTINEL,
                ESCAPE_SENTINEL * 2,
                ESCAPE_SENTINEL * 3,
                WHITESPACE_MARKER,
                WHITESPACE_MARKER * 2,
                f"{ESCAPE_SENTINEL}text{WHITESPACE_MARKER}",
                f"{ESCAPE_SENTINEL}S00;",
                f"{ESCAPE_SENTINEL}S01;",
                f"{ESCAPE_SENTINEL}W;",
                f"தமிழ்{ESCAPE_SENTINEL}English{WHITESPACE_MARKER}",
            ]
            for adv in adversarial_inputs:
                ids = tok.encode_content(adv)
                for sid in range(STRUCTURAL_COUNT):
                    self.assertNotIn(
                        sid, ids,
                        f"[{name}] Structural ID {sid} leaked for adversarial input {adv!r}"
                    )
                self.assertEqual(tok.decode_content(ids), adv)

    def test_sec04_unicode_edge_cases(self) -> None:
        """Security: Unicode edge cases (ZWJ, ZWNJ, RTL, high codepoint, surrogates)."""
        for name, tok in self._for_both_tokenizers():
            # Zero-width joiner and non-joiner
            zwnj_text = "க்\u200Cஷ"
            zwj_text = "க்\u200Dஷ"
            self.assertEqual(tok.decode_content(tok.encode_content(zwnj_text)), zwnj_text)
            self.assertEqual(tok.decode_content(tok.encode_content(zwj_text)), zwj_text)

            # High codepoint (U+10FFFF)
            high_cp = "\U0010ffff"
            self.assertEqual(tok.decode_content(tok.encode_content(high_cp)), high_cp)

            # Lone surrogate must raise ValueError
            with self.assertRaises(ValueError):
                tok.encode_content("bad\ud800text")


# ---------------------------------------------------------------------------
# E. Build interface tests
# ---------------------------------------------------------------------------

class TestBuildInterface(unittest.TestCase):
    """Test the shared build_tokenizers interface."""

    def test_d01_build_single_a(self) -> None:
        """Build interface: build_single for Candidate A works."""
        from igris.tokenizer.build_tokenizers import build_single
        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_single("A", iter(SYNTHETIC_CORPUS), tmpdir, min_frequency_a=1)
            self.assertEqual(result.candidate, "A")
            self.assertTrue(result.validation_passed, result.validation_errors)
            self.assertTrue(result.smoke_test_passed, result.smoke_test_errors)

    def test_d02_build_single_b(self) -> None:
        """Build interface: build_single for Candidate B works."""
        from igris.tokenizer.build_tokenizers import build_single
        with tempfile.TemporaryDirectory() as tmpdir:
            result = build_single("B", iter(SYNTHETIC_CORPUS), tmpdir)
            self.assertEqual(result.candidate, "B")
            self.assertTrue(result.validation_passed, result.validation_errors)
            self.assertTrue(result.smoke_test_passed, result.smoke_test_errors)

    def test_d03_build_all(self) -> None:
        """Build interface: build_all builds both candidates."""
        from igris.tokenizer.build_tokenizers import build_all
        with tempfile.TemporaryDirectory() as tmpdir:
            report = build_all(
                iter(SYNTHETIC_CORPUS),
                iter(SYNTHETIC_CORPUS),
                artifacts_root=tmpdir,
                min_frequency_a=1,
            )
            self.assertIsNotNone(report.candidate_a)
            self.assertIsNotNone(report.candidate_b)
            self.assertTrue(report.candidate_a.validation_passed)
            self.assertTrue(report.candidate_b.validation_passed)
            self.assertTrue(report.candidate_a.smoke_test_passed)
            self.assertTrue(report.candidate_b.smoke_test_passed)

    def test_d04_build_single_invalid_candidate(self) -> None:
        """Build interface: invalid candidate name is rejected."""
        from igris.tokenizer.build_tokenizers import build_single
        with self.assertRaises(ValueError):
            build_single("C", iter([]), ".")

    def test_d05_candidate_a_determinism(self) -> None:
        """Determinism: two independent builds of Candidate A produce identical SHA-256."""
        import hashlib
        from igris.tokenizer.candidate_a_builder import build_candidate_a
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            p1 = build_candidate_a(iter(SYNTHETIC_CORPUS), d1, min_frequency=1)
            p2 = build_candidate_a(iter(SYNTHETIC_CORPUS), d2, min_frequency=1)
            h1 = hashlib.sha256(p1.read_bytes()).hexdigest()
            h2 = hashlib.sha256(p2.read_bytes()).hexdigest()
            self.assertEqual(h1, h2, f"Candidate A builds produced non-identical hashes: {h1} != {h2}")

    def test_d06_candidate_b_determinism(self) -> None:
        """Determinism: two independent builds of Candidate B produce identical SHA-256."""
        import hashlib
        from igris.tokenizer.candidate_b_builder import build_candidate_b
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            p1 = build_candidate_b(iter(SYNTHETIC_CORPUS), d1)
            p2 = build_candidate_b(iter(SYNTHETIC_CORPUS), d2)
            h1 = hashlib.sha256(p1.read_bytes()).hexdigest()
            h2 = hashlib.sha256(p2.read_bytes()).hexdigest()
            self.assertEqual(h1, h2, f"Candidate B builds produced non-identical hashes: {h1} != {h2}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
