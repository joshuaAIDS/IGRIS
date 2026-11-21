import importlib.util, tempfile, unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_tamil_pilot.py"
spec = importlib.util.spec_from_file_location("audit_tamil_pilot", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class AuditTests(unittest.TestCase):
    def test_basic_tamil_and_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.txt"
            p.write_text("வணக்கம்\nவணக்கம்\nhello\n", encoding="utf-8")
            r = mod.audit(p)
            self.assertTrue(r["utf8_valid"])
            self.assertEqual(r["nonempty_records"], 3)
            self.assertEqual(r["exact_duplicate_records_beyond_first"], 1)
            self.assertEqual(r["record_script_profile"]["records_with_tamil"], 2)
            self.assertEqual(r["record_script_profile"]["records_without_tamil"], 1)
    def test_invalid_utf8_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.txt"
            p.write_bytes(b"\xff")
            r = mod.audit(p)
            self.assertFalse(r["utf8_valid"])
            self.assertEqual(r["status"], "FAIL")
    def test_structural_token_flag(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "token.txt"
            p.write_text("வணக்கம் <|user|>\n", encoding="utf-8")
            r = mod.audit(p)
            self.assertIn("<|user|>", r["structural_token_occurrences_by_record"])
unittest.main()
