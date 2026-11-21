import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from igris.tokenizer.strict import (
    StrictTokenizer, RawBinaryCodec, escape_text, unescape_text,
    ESCAPE_SENTINEL, WHITESPACE_MARKER, STRUCTURAL_TOKENS,
)
from igris.tokenizer.ingestion import (
    SequencePolicy, encode_text, apply_framing, strip_framing,
    encode_raw_binary, decode_raw_binary,
)

class ByteTextBackend:
    """Test double only: UTF-8 bytes mapped above reserved IDs."""
    name = "test-double"
    vocab_size = 32768
    def encode_raw_text(self, text): return [b + 12 for b in text.encode("utf-8")]
    def decode_raw_text(self, ids): return bytes(i - 12 for i in ids).decode("utf-8", errors="strict")
    def byte_id_map(self): return [12 + b for b in range(256)]

class ContractTests(unittest.TestCase):
    def setUp(self): self.tok = StrictTokenizer(ByteTextBackend())
    def test_nfc_and_exact(self):
        nfc = self.tok.encode_content("e\u0301")
        exact = StrictTokenizer(self.tok.backend, "exact").encode_content("e\u0301")
        self.assertNotEqual(nfc, exact)
        self.assertEqual(self.tok.decode_content(nfc), "é")
        self.assertEqual(StrictTokenizer(self.tok.backend, "exact").decode_content(exact), "e\u0301")
    def test_reserved_literal_roundtrip(self):
        value = "x" + STRUCTURAL_TOKENS[5] + WHITESPACE_MARKER + ESCAPE_SENTINEL + "தமிழ்"
        self.assertEqual(self.tok.decode_content(self.tok.encode_content(value)), value)
    def test_escape_malformed_rejected(self):
        for value in (ESCAPE_SENTINEL, ESCAPE_SENTINEL + "S١١;", ESCAPE_SENTINEL + "S12;", ESCAPE_SENTINEL + "Q;"):
            with self.assertRaises(ValueError): unescape_text(value)
    def test_content_rejects_structural_and_bool(self):
        for ids in ([0], [1], [True], [-1], [32768]):
            with self.assertRaises((ValueError, TypeError)): self.tok.decode_content(ids)
    def test_batch_and_empty(self):
        values = ["", "தமிழ்", "Tanglish vanakkam", "e\u0301"]
        self.assertEqual(self.tok.decode_batch(self.tok.encode_batch(values)), ["", "தமிழ்", "Tanglish vanakkam", "é"])
        self.assertEqual(self.tok.encode_batch([]), [])
        self.assertEqual(self.tok.decode_batch([]), [])
    def test_render_sequence(self):
        body = self.tok.encode_content("hello")
        self.assertEqual(self.tok.render_sequence([10] + body + [11]), "<|user|>hello<|assistant|>")
    def test_no_automatic_framing(self):
        result = encode_text(self.tok, "hello")
        self.assertEqual(result.content_ids, result.sequence_ids)
        framed = apply_framing(result.content_ids, SequencePolicy(add_bos=True, add_eos=True))
        self.assertEqual(framed[0], 1); self.assertEqual(framed[-1], 2)
        self.assertEqual(strip_framing(framed, SequencePolicy(add_bos=True, add_eos=True)), list(result.content_ids))
    def test_raw_binary_roundtrip(self):
        codec = RawBinaryCodec(self.tok.backend.byte_id_map(), 32768)
        payload = bytes(range(256)) + b"\x00\xffIGRIS"
        encoded = encode_raw_binary(payload, codec)
        self.assertEqual(decode_raw_binary(encoded.content_ids, codec), payload)
    def test_raw_binary_rejects_text(self):
        codec = RawBinaryCodec(self.tok.backend.byte_id_map(), 32768)
        with self.assertRaises(TypeError): codec.encode_bytes("not bytes")
    def test_lone_surrogate_rejected(self):
        with self.assertRaises(ValueError): self.tok.encode_content("bad\ud800")

if __name__ == "__main__": unittest.main(verbosity=2)
