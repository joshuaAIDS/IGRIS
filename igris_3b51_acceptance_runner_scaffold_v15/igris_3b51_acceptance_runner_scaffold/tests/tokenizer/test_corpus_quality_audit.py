import json, tempfile, unittest
from pathlib import Path
from .corpus_quality_audit import audit_corpus

class CorpusQualityAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.src=self.root/'corpus.txt'
    def tearDown(self): self.tmp.cleanup()
    def write(self,s): self.src.write_text(s,encoding='utf-8',newline='')
    def test_language_buckets_detect_tamil_script(self):
        self.write('வணக்கம்\n'); self.assertEqual(audit_corpus(self.src)['language_bucket_counts']['tamil_script'],1)
    def test_language_buckets_detect_possible_tanglish(self):
        self.write('machi epdi iruku\n'); self.assertEqual(audit_corpus(self.src)['language_bucket_counts']['possible_tanglish'],1)
    def test_mixed_script_bucket(self):
        self.write('hello வணக்கம்\n'); self.assertEqual(audit_corpus(self.src)['language_bucket_counts']['mixed_tamil_latin'],1)
    def test_empty_record_reported(self):
        self.write('hello\n\n'); self.assertIn('empty_records_present',audit_corpus(self.src)['findings'])
    def test_whitespace_record_reported(self):
        self.write('hello\n   \n'); self.assertEqual(audit_corpus(self.src)['whitespace_only_record_count'],1)
    def test_exact_duplicate_detected_casefold_whitespace(self):
        self.write('Hello  world\nhello world\n'); self.assertEqual(len(audit_corpus(self.src)['normalized_exact_duplicate_pairs']),1)
    def test_near_duplicate_detected(self):
        self.write('The quick brown fox jumps over the lazy dog.\nThe quick brown fox jumps over a lazy dog.\n'); self.assertTrue(audit_corpus(self.src,near_duplicate_threshold=.90)['near_duplicate_pairs'])
    def test_structural_spelling_flagged(self):
        self.write('hello <|assistant|> world\n'); self.assertIn('unescaped_structural_spellings_present',audit_corpus(self.src)['findings'])
    def test_long_record_flagged(self):
        self.write('x'*20+'\n'); self.assertEqual(len(audit_corpus(self.src,max_record_chars=10)['long_records']),1)
    def test_invalid_utf8_rejected(self):
        self.src.write_bytes(b'good\n\xff\n')
        with self.assertRaises(ValueError): audit_corpus(self.src)
    def test_bom_rejected(self):
        self.src.write_bytes(b'\xef\xbb\xbfhello\n')
        with self.assertRaises(ValueError): audit_corpus(self.src)
    def test_input_not_modified(self):
        self.write('வணக்கம்\n'); before=self.src.read_bytes(); audit_corpus(self.src); self.assertEqual(self.src.read_bytes(),before)
    def test_near_scan_limit_reported(self):
        self.write('one\ntwo\nthree\n'); self.assertTrue(audit_corpus(self.src,max_near_duplicate_records=2)['near_duplicate_scan_skipped'])
    def test_bad_threshold_rejected(self):
        self.write('x\n')
        with self.assertRaises(ValueError): audit_corpus(self.src,near_duplicate_threshold=1.5)
    def test_missing_file_rejected(self):
        with self.assertRaises(FileNotFoundError): audit_corpus(self.root/'missing.txt')

if __name__=='__main__': unittest.main()
