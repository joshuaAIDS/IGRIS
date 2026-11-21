#!/usr/bin/env python3
r"""IGRIS Phase 24 — Comprehensive Infrastructure Evaluation Pipeline.

Runs all evaluation steps against actual module APIs:
1. Language classification on Phase 23A Tanglish fixtures
2. Unicode adversarial tests with Tamil combining marks
3. Duplicate detection precision/recall
4. Quality filter on fixtures + adversarial cases
5. Tokenizer evaluation (read-only, Candidate A)
6. Tanglish analysis on fixtures

Outputs JSON results to C:\IGRIS\scratch\phase24_eval_results.json
"""

import json
import os
import sys
import hashlib
from pathlib import Path
from collections import Counter, defaultdict

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
sys.path.insert(0, str(PATCH_DIR / "scripts"))
sys.path.insert(0, str(PATCH_DIR))

from language_identifier_v2 import LanguageIdentifierV2
from unicode_processor_v2 import UnicodeProcessorV2
from tanglish_analyzer import TanglishAnalyzer
from quality_filter_v2 import QualityFilterV2
from duplicate_detector_v2 import DuplicateDetectorV2

results = {}

# ============================================================
# STEP 3: Language Classification on Phase 23A Fixtures
# ============================================================
print("=" * 70)
print("STEP 3: Language Classification on Phase 23A Fixtures")
print("=" * 70)

lid = LanguageIdentifierV2()
fixtures_path = PATCH_DIR / "PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl"

fixtures = []
with open(fixtures_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            fixtures.append(json.loads(line))

print(f"Loaded {len(fixtures)} fixtures")

# Map fixture categories to expected LID labels
CATEGORY_TO_EXPECTED = {
    "TAMIL_SCRIPT_ENGLISH_TECH": "TANGLISH",
    "ROMANIZED_TAMIL_INFORMAL": "TANGLISH",
    "ENGLISH_TAMIL_COLLOQUIAL": "TANGLISH",
    "INTRA_SENTENTIAL_SWITCH": "TANGLISH",
    "DISCOURSE_PARTICLE_MIX": "TANGLISH",
}

y_true = []
y_pred = []
per_category_results = defaultdict(lambda: {"correct": 0, "total": 0, "predictions": Counter()})
classification_details = []

for i, fix in enumerate(fixtures):
    text = fix.get("text", "")
    category = fix.get("category", "UNKNOWN")
    expected = CATEGORY_TO_EXPECTED.get(category, "UNKNOWN")

    result = lid.identify(text)
    predicted = result.label
    confidence = result.confidence

    y_true.append(expected)
    y_pred.append(predicted)

    is_correct = predicted == expected
    per_category_results[category]["total"] += 1
    per_category_results[category]["predictions"][predicted] += 1
    if is_correct:
        per_category_results[category]["correct"] += 1

    classification_details.append({
        "index": i,
        "category": category,
        "expected": expected,
        "predicted": predicted,
        "confidence": confidence,
        "correct": is_correct,
        "sublabel": result.sublabel,
    })

# Confusion matrix
labels = sorted(set(y_true + y_pred))
confusion = {}
for true_label in labels:
    confusion[true_label] = {}
    for pred_label in labels:
        confusion[true_label][pred_label] = sum(
            1 for yt, yp in zip(y_true, y_pred) if yt == true_label and yp == pred_label
        )

total_correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
overall_accuracy = total_correct / len(y_true) if y_true else 0.0

per_class_metrics = {}
for label in labels:
    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == label and yp == label)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != label and yp == label)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == label and yp != label)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    per_class_metrics[label] = {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp, "fp": fp, "fn": fn,
    }

per_category_summary = {}
for cat, data in per_category_results.items():
    per_category_summary[cat] = {
        "total": data["total"],
        "correct": data["correct"],
        "accuracy": round(data["correct"] / data["total"], 4) if data["total"] > 0 else 0.0,
        "predictions": dict(data["predictions"]),
    }

results["language_classification"] = {
    "total_fixtures": len(fixtures),
    "overall_accuracy": round(overall_accuracy, 4),
    "total_correct": total_correct,
    "total_incorrect": len(fixtures) - total_correct,
    "confusion_matrix": confusion,
    "per_class_metrics": per_class_metrics,
    "per_category_accuracy": per_category_summary,
    "labels": labels,
    "misclassified": [d for d in classification_details if not d["correct"]],
}

print(f"Overall accuracy: {overall_accuracy:.2%} ({total_correct}/{len(fixtures)})")
for cat, data in sorted(per_category_summary.items()):
    print(f"  {cat}: {data['accuracy']:.2%} ({data['correct']}/{data['total']})")
print(f"Per-class metrics:")
for label, m in sorted(per_class_metrics.items()):
    print(f"  {label}: P={m['precision']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f}")

# Additional pure Tamil/English/Tanglish test samples
additional_tests = [
    ("தமிழ் ஒரு அழகான மொழி. இது மிகவும் பழமையானது.", "TAMIL"),
    ("நான் பள்ளிக்கு போகிறேன். என் நண்பர்கள் அங்கே இருக்கிறார்கள்.", "TAMIL"),
    ("இந்த புத்தகம் மிகவும் நல்லது. நான் அதை படித்தேன்.", "TAMIL"),
    ("The quick brown fox jumps over the lazy dog.", "ENGLISH"),
    ("Python is a high-level programming language.", "ENGLISH"),
    ("Machine learning models require large datasets for training.", "ENGLISH"),
    ("Natural language processing enables computers to understand human language.", "ENGLISH"),
    ("Naan school poren da, late aagidum.", "TANGLISH"),
    ("Enna da ipdi pannura, not fair at all.", "TANGLISH"),
    ("இந்த code-ல error இருக்கு, debug பண்ணு.", "TANGLISH"),
]

additional_results = []
for text, expected in additional_tests:
    result = lid.identify(text)
    additional_results.append({
        "text": text[:50] + "..." if len(text) > 50 else text,
        "expected": expected,
        "predicted": result.label,
        "confidence": result.confidence,
        "correct": result.label == expected,
    })

additional_correct = sum(1 for r in additional_results if r["correct"])
print(f"\nAdditional test samples: {additional_correct}/{len(additional_results)} correct")
for r in additional_results:
    s = "✓" if r["correct"] else "✗"
    print(f"  {s} [{r['expected']}→{r['predicted']}] {r['text']}")
results["additional_lid_tests"] = {
    "total": len(additional_results),
    "correct": additional_correct,
    "accuracy": round(additional_correct / len(additional_results), 4),
    "details": additional_results,
}

# ============================================================
# STEP 4: Unicode Adversarial Tests
# ============================================================
print("\n" + "=" * 70)
print("STEP 4: Unicode Adversarial Tests")
print("=" * 70)

up = UnicodeProcessorV2()

unicode_test_cases = [
    ("கா", "Tamil AA vowel sign"),
    ("கி", "Tamil I vowel sign"),
    ("கீ", "Tamil II vowel sign"),
    ("கு", "Tamil U vowel sign"),
    ("கூ", "Tamil UU vowel sign"),
    ("கெ", "Tamil E vowel sign"),
    ("கே", "Tamil EE vowel sign"),
    ("கை", "Tamil AI vowel sign"),
    ("கொ", "Tamil O vowel sign"),
    ("கோ", "Tamil OO vowel sign"),
    ("கௌ", "Tamil AU vowel sign"),
    ("க்", "Virama preserved"),
    ("ங்க", "Virama conjunct"),
    ("க்\u200Dக", "ZWJ after virama"),
    ("க்\u200Cக", "ZWNJ after virama"),
    ("க்்", "Double virama — adversarial"),
    ("\u0BBE", "Lone AA vowel sign — adversarial"),
    ("தமிழ் Python code", "Tamil + Latin mixed"),
    ("Hello உலகம்", "Latin + Tamil mixed"),
    ("௧௨௩", "Tamil digits"),
    ("வணக்கம்! எப்படி இருக்கீர்கள்?", "Tamil with punctuation"),
    ("தமிழ்நாடு இந்தியாவின் தென்பகுதியில் அமைந்துள்ள ஒரு மாநிலம். சென்னை அதன் தலைநகரம்.", "Long Tamil"),
    ("Hello \uFFFD World", "Replacement character U+FFFD"),
    ("Hello\x00World\x01Test", "Control characters"),
    ("நிலை", "Tamil word requiring NFC"),
]

unicode_results = []
for text, description in unicode_test_cases:
    normalized, report = up.normalize(text)
    roundtrip_ok = up.round_trip_check(text)

    unicode_results.append({
        "description": description,
        "input_len": len(text),
        "output_len": len(normalized),
        "is_nfc_original": report.is_nfc_original,
        "has_replacement_char": report.has_replacement_char,
        "control_chars_removed": report.control_chars_removed,
        "tamil_combining_preserved": report.tamil_combining_marks_preserved,
        "virama_preserved": report.virama_sequences_preserved,
        "zwj_zwnj_preserved": report.zwj_zwnj_preserved,
        "malformed_sequences": report.malformed_sequences,
        "roundtrip_ok": roundtrip_ok,
    })

    s = "✓" if roundtrip_ok else "⚠"
    print(f"  {s} {description}: in={len(text)} out={len(normalized)} NFC={report.is_nfc_original} "
          f"combining={report.tamil_combining_marks_preserved} virama={report.virama_sequences_preserved} "
          f"zwj={report.zwj_zwnj_preserved} malformed={report.malformed_sequences}")

# Round-trip stability on all 100 fixtures
fixture_rt_pass = 0
fixture_rt_details = []
for fix in fixtures:
    text = fix.get("text", "")
    normalized, _ = up.normalize(text)
    re_normalized, _ = up.normalize(normalized)
    stable = normalized == re_normalized
    if stable:
        fixture_rt_pass += 1
    fixture_rt_details.append({
        "id": fix.get("id", ""),
        "category": fix.get("category", ""),
        "stable": stable,
    })

print(f"\nFixture round-trip stability: {fixture_rt_pass}/{len(fixtures)}")

results["unicode_tests"] = {
    "total_adversarial_tests": len(unicode_test_cases),
    "details": unicode_results,
    "fixture_round_trip": {
        "total": len(fixtures),
        "stable": fixture_rt_pass,
        "stability_rate": round(fixture_rt_pass / len(fixtures), 4) if fixtures else 0.0,
    },
}

# ============================================================
# STEP 5: Duplicate Detection
# ============================================================
print("\n" + "=" * 70)
print("STEP 5: Duplicate Detection")
print("=" * 70)

dd = DuplicateDetectorV2()

unique_count = 0
dup_count_in_fixtures = 0
for i, fix in enumerate(fixtures):
    text = fix.get("text", "")
    doc_id = f"fixture-{i}"
    r = dd.check_and_register(doc_id, text)
    if r.is_duplicate:
        dup_count_in_fixtures += 1
    else:
        unique_count += 1

print(f"Phase 23A fixtures: {unique_count} unique, {dup_count_in_fixtures} duplicates out of {len(fixtures)}")

# Inject deliberate test duplicates
test_dup_cases = [
    {"type": "exact_dup", "doc_id": "test-exact", "text": fixtures[0]["text"], "expected_dup": True},
    {"type": "whitespace_var", "doc_id": "test-ws", "text": "  " + fixtures[1]["text"] + "  ", "expected_dup": True},
    {"type": "near_dup", "doc_id": "test-near", "text": fixtures[3]["text"] + " extra word", "expected_dup": True},
    {"type": "new_text", "doc_id": "test-new", "text": "This is a completely new and unique test sentence that does not appear anywhere in the fixture set at all.", "expected_dup": False},
    {"type": "tamil_exact", "doc_id": "test-tamil-dup", "text": fixtures[5]["text"], "expected_dup": True},
]

dup_tp = dup_tn = dup_fp = dup_fn = 0
dup_test_results = []
for case in test_dup_cases:
    r = dd.check_and_register(case["doc_id"], case["text"])
    expected = case["expected_dup"]
    detected = r.is_duplicate
    correct = detected == expected
    if expected and detected: dup_tp += 1
    elif not expected and not detected: dup_tn += 1
    elif not expected and detected: dup_fp += 1
    else: dup_fn += 1

    dup_test_results.append({
        "type": case["type"],
        "expected": expected,
        "detected": detected,
        "dup_type": r.dup_type,
        "matched_id": r.matched_id,
        "similarity": r.similarity,
        "correct": correct,
    })
    s = "✓" if correct else "✗"
    print(f"  {s} {case['type']}: expected={expected} detected={detected} type={r.dup_type} sim={r.similarity:.2f}")

dup_precision = dup_tp / (dup_tp + dup_fp) if (dup_tp + dup_fp) > 0 else 1.0
dup_recall = dup_tp / (dup_tp + dup_fn) if (dup_tp + dup_fn) > 0 else 1.0
dup_f1 = 2 * dup_precision * dup_recall / (dup_precision + dup_recall) if (dup_precision + dup_recall) > 0 else 0.0

print(f"\nDuplicate detection: P={dup_precision:.4f} R={dup_recall:.4f} F1={dup_f1:.4f}")

results["duplicate_detection"] = {
    "fixtures_unique": unique_count,
    "fixtures_duplicate": dup_count_in_fixtures,
    "total_fixtures": len(fixtures),
    "test_cases": dup_test_results,
    "tp": dup_tp, "tn": dup_tn, "fp": dup_fp, "fn": dup_fn,
    "precision": round(dup_precision, 4),
    "recall": round(dup_recall, 4),
    "f1": round(dup_f1, 4),
}

# ============================================================
# STEP 6: Quality Filter
# ============================================================
print("\n" + "=" * 70)
print("STEP 6: Quality Filter Evaluation")
print("=" * 70)

qf = QualityFilterV2()

fixture_pass = 0
fixture_fail = 0
rejection_reasons = Counter()
fixture_filter_details = []

for fix in fixtures:
    text = fix.get("text", "")
    verdict = qf.evaluate(text)
    if verdict.passed:
        fixture_pass += 1
    else:
        fixture_fail += 1
        for r in verdict.rejection_reasons:
            rejection_reasons[r] += 1
    fixture_filter_details.append({
        "id": fix.get("id", ""),
        "category": fix.get("category", ""),
        "passed": verdict.passed,
        "reasons": verdict.rejection_reasons,
        "char_count": verdict.char_count,
        "word_count": verdict.word_count,
    })

print(f"Fixtures: {fixture_pass} passed, {fixture_fail} rejected out of {len(fixtures)}")
if rejection_reasons:
    print(f"Rejection reasons: {dict(rejection_reasons)}")

# Adversarial rejection cases
adversarial_quality_cases = [
    {"text": "", "expected_reason": "EMPTY_RECORD", "desc": "Empty string"},
    {"text": "   \t\n  ", "expected_reason": "EMPTY_RECORD", "desc": "Whitespace only"},
    {"text": "Hi", "expected_reason": "TOO_SHORT", "desc": "Too short (2 chars)"},
    {"text": "ab", "expected_reason": "TOO_SHORT", "desc": "Too short (2 chars alt)"},
    {"text": "a" * 100, "expected_reason": "REPEATED_CHAR_SPAM", "desc": "Repeated char spam"},
    {"text": "http://example.com http://test.com http://foo.com http://bar.com http://baz.com more urls http://a.com http://b.com", "expected_reason": "URL_HEAVY", "desc": "URL heavy"},
    {"text": "!!!???...!!!???...!!!???...!!!???...", "expected_reason": "EXCESSIVE_PUNCTUATION", "desc": "Excessive punctuation"},
    {"text": "Hello \uFFFD world \uFFFD test \uFFFD more \uFFFD text", "expected_reason": "MALFORMED_UNICODE", "desc": "Malformed Unicode"},
    {"text": "Click here to unsubscribe. All rights reserved. Terms and conditions apply. Privacy policy. Cookie policy.", "expected_reason": "BOILERPLATE_DETECTED", "desc": "Boilerplate text"},
    {"text": "12345 67890 !@#$% ^&*()", "expected_reason": "NO_ALPHABETIC_CHARS", "desc": "No alphabetic chars"},
    {"text": "This is a perfectly normal English sentence with adequate length for testing.", "expected_reason": None, "desc": "Normal English (should pass)"},
    {"text": "தமிழ் ஒரு அழகான மொழி. இது மிகவும் பழமையானது.", "expected_reason": None, "desc": "Normal Tamil (should pass)"},
]

adv_results = []
adv_correct = 0
for case in adversarial_quality_cases:
    verdict = qf.evaluate(case["text"])
    if case["expected_reason"] is None:
        correct = verdict.passed
    else:
        correct = not verdict.passed and case["expected_reason"] in verdict.rejection_reasons
    if correct:
        adv_correct += 1
    adv_results.append({
        "desc": case["desc"],
        "expected_reason": case["expected_reason"],
        "passed": verdict.passed,
        "actual_reasons": verdict.rejection_reasons,
        "correct": correct,
    })
    s = "✓" if correct else "✗"
    print(f"  {s} {case['desc']}: passed={verdict.passed} reasons={verdict.rejection_reasons}")

print(f"\nAdversarial quality tests: {adv_correct}/{len(adversarial_quality_cases)} correct")

results["quality_filter"] = {
    "fixture_total": len(fixtures),
    "fixture_passed": fixture_pass,
    "fixture_rejected": fixture_fail,
    "rejection_reason_distribution": dict(rejection_reasons),
    "adversarial_total": len(adversarial_quality_cases),
    "adversarial_correct": adv_correct,
    "adversarial_accuracy": round(adv_correct / len(adversarial_quality_cases), 4),
    "adversarial_details": adv_results,
}

# ============================================================
# STEP 7: Tokenizer Evaluation (Read-Only)
# ============================================================
print("\n" + "=" * 70)
print("STEP 7: Tokenizer Evaluation (Read-Only)")
print("=" * 70)

tokenizer_path = PATCH_DIR / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
tokenizer_results = {}

try:
    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(str(tokenizer_path))
    print(f"Tokenizer loaded from: {tokenizer_path}")

    with open(tokenizer_path, "rb") as f:
        tok_hash = hashlib.sha256(f.read()).hexdigest()
    expected_hash = "ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561"
    hash_match = tok_hash == expected_hash
    print(f"Hash: {tok_hash[:20]}... match={hash_match}")

    vocab_size = tok.get_vocab_size()
    print(f"Vocabulary size: {vocab_size}")

    structural_tokens_ok = True
    structural_token_map = {}
    for token_id in range(12):
        token = tok.id_to_token(token_id)
        structural_token_map[token_id] = token
        if token is None:
            structural_tokens_ok = False

    eval_samples = {
        "english": [
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning models require large datasets.",
            "Python is a versatile programming language.",
            "Natural language processing is a subfield of AI.",
            "Deep learning has revolutionized computer vision.",
        ],
        "tamil": [
            "தமிழ் ஒரு அழகான மொழி.",
            "நான் பள்ளிக்கு போகிறேன்.",
            "இந்த புத்தகம் மிகவும் நல்லது.",
            "சென்னை தமிழ்நாட்டின் தலைநகரம்.",
            "கணினி அறிவியல் ஒரு முக்கிய துறை.",
        ],
        "tanglish": [
            "Naan school poren da, late aagidum.",
            "Enna da ipdi pannura, not fair at all.",
            "Weekend-la movie polamaa, nalla comedy padam iruku.",
            "Exam-ku prepare aaganum, but lazy-aa iruku.",
            "Office meeting boring-aa irunthuchu, skip pannidalam.",
        ],
        "tamil_script_mixed": [
            "இந்த code-ல error இருக்கு.",
            "Python-ல program எழுது.",
            "Machine learning model train பண்ணு.",
        ],
    }

    # Find UNK token
    unk_token_id = tok.token_to_id("[UNK]")
    if unk_token_id is None:
        unk_token_id = tok.token_to_id("<unk>")
    if unk_token_id is None:
        unk_token_id = tok.token_to_id("<UNK>")

    total_unk_count = 0
    total_token_count = 0
    fertility_results = {}

    for lang, samples in eval_samples.items():
        lang_tokens = 0
        lang_words = 0
        lang_unk = 0
        lang_roundtrip_ok = 0
        sample_details = []

        for text in samples:
            encoding = tok.encode(text)
            tokens = encoding.ids
            n_tokens = len(tokens)
            words = text.split()
            n_words = len(words)
            unk_count = sum(1 for t in tokens if t == unk_token_id) if unk_token_id is not None else 0
            decoded = tok.decode(tokens)
            roundtrip_ok = text.strip() == decoded.strip()
            fertility = n_tokens / n_words if n_words > 0 else 0.0

            lang_tokens += n_tokens
            lang_words += n_words
            lang_unk += unk_count
            if roundtrip_ok:
                lang_roundtrip_ok += 1
            total_unk_count += unk_count
            total_token_count += n_tokens

            sample_details.append({
                "text": text[:60],
                "tokens": n_tokens,
                "words": n_words,
                "fertility": round(fertility, 4),
                "unk_count": unk_count,
                "roundtrip_ok": roundtrip_ok,
            })

        avg_fertility = lang_tokens / lang_words if lang_words > 0 else 0.0
        unk_rate = lang_unk / lang_tokens if lang_tokens > 0 else 0.0

        fertility_results[lang] = {
            "total_tokens": lang_tokens,
            "total_words": lang_words,
            "avg_fertility": round(avg_fertility, 4),
            "total_unk": lang_unk,
            "unk_rate": round(unk_rate, 6),
            "roundtrip_pass": lang_roundtrip_ok,
            "roundtrip_total": len(samples),
            "samples": sample_details,
        }
        print(f"  {lang}: fertility={avg_fertility:.4f} UNK_rate={unk_rate:.6f} roundtrip={lang_roundtrip_ok}/{len(samples)}")

    overall_unk_rate = total_unk_count / total_token_count if total_token_count > 0 else 0.0

    # Fixture tokenization
    fixture_lengths = []
    fixture_unk_total = 0
    fixture_token_total = 0
    fixture_roundtrip_ok = 0
    for fix in fixtures:
        text = fix.get("text", "")
        encoding = tok.encode(text)
        tokens = encoding.ids
        fixture_lengths.append(len(tokens))
        if unk_token_id is not None:
            fixture_unk_total += sum(1 for t in tokens if t == unk_token_id)
        fixture_token_total += len(tokens)
        decoded = tok.decode(tokens)
        if text.strip() == decoded.strip():
            fixture_roundtrip_ok += 1

    fixture_unk_rate = fixture_unk_total / fixture_token_total if fixture_token_total > 0 else 0.0

    if fixture_lengths:
        sorted_lens = sorted(fixture_lengths)
        seq_len_stats = {
            "min": sorted_lens[0],
            "max": sorted_lens[-1],
            "mean": round(sum(sorted_lens) / len(sorted_lens), 2),
            "median": sorted_lens[len(sorted_lens) // 2],
            "p95": sorted_lens[int(len(sorted_lens) * 0.95)],
        }
    else:
        seq_len_stats = {}

    print(f"\nFixture tokenization: {fixture_token_total} total tokens, UNK rate={fixture_unk_rate:.6f}")
    print(f"Fixture roundtrip: {fixture_roundtrip_ok}/{len(fixtures)}")
    print(f"Sequence length: min={seq_len_stats.get('min')} max={seq_len_stats.get('max')} mean={seq_len_stats.get('mean')} p95={seq_len_stats.get('p95')}")

    tokenizer_results = {
        "loaded": True,
        "hash": tok_hash,
        "hash_match": hash_match,
        "vocab_size": vocab_size,
        "structural_tokens_ok": structural_tokens_ok,
        "structural_token_map": structural_token_map,
        "unk_token_id": unk_token_id,
        "fertility_by_language": fertility_results,
        "overall_unk_rate": round(overall_unk_rate, 6),
        "fixture_evaluation": {
            "total_tokens": fixture_token_total,
            "total_unk": fixture_unk_total,
            "unk_rate": round(fixture_unk_rate, 6),
            "roundtrip_ok": fixture_roundtrip_ok,
            "roundtrip_total": len(fixtures),
            "sequence_length_stats": seq_len_stats,
        },
    }

except ImportError:
    print("WARNING: tokenizers library not available")
    tokenizer_results = {"loaded": False, "error": "tokenizers library not available"}
except Exception as e:
    print(f"ERROR: {e}")
    import traceback; traceback.print_exc()
    tokenizer_results = {"loaded": False, "error": str(e)}

results["tokenizer_evaluation"] = tokenizer_results

# ============================================================
# STEP: Tanglish Analyzer on Fixtures
# ============================================================
print("\n" + "=" * 70)
print("BONUS: Tanglish Analyzer on Fixtures")
print("=" * 70)

ta = TanglishAnalyzer()

total_switch = 0
total_discourse = 0
total_romanized = 0
total_suffixes = 0
plausibility_scores = []
ta_details = []

for fix in fixtures:
    text = fix.get("text", "")
    analysis = ta.analyze(text)
    sw = len(analysis.code_switch_points) if hasattr(analysis, 'code_switch_points') else 0
    dm = len(analysis.discourse_markers_found) if hasattr(analysis, 'discourse_markers_found') else 0
    rc = len(analysis.romanized_tamil_candidates) if hasattr(analysis, 'romanized_tamil_candidates') else 0
    ts = len(analysis.tamil_suffixes_detected) if hasattr(analysis, 'tamil_suffixes_detected') else 0
    pl = analysis.is_structurally_plausible if hasattr(analysis, 'is_structurally_plausible') else False

    total_switch += sw
    total_discourse += dm
    total_romanized += rc
    total_suffixes += ts
    plausibility_scores.append(1 if pl else 0)

    ta_details.append({
        "id": fix.get("id", ""),
        "category": fix.get("category", ""),
        "switch_points": sw,
        "discourse_markers": dm,
        "romanized_candidates": rc,
        "tamil_suffixes": ts,
        "plausible": pl,
    })

n = len(fixtures) if fixtures else 1
plausible_count = sum(plausibility_scores)
print(f"Avg code-switch points: {total_switch / n:.2f}")
print(f"Avg discourse markers: {total_discourse / n:.2f}")
print(f"Avg romanized Tamil candidates: {total_romanized / n:.2f}")
print(f"Avg Tamil suffixes: {total_suffixes / n:.2f}")
print(f"Structurally plausible: {plausible_count}/{len(fixtures)}")

results["tanglish_analysis"] = {
    "total_fixtures": len(fixtures),
    "avg_switch_points": round(total_switch / n, 4),
    "avg_discourse_markers": round(total_discourse / n, 4),
    "avg_romanized_candidates": round(total_romanized / n, 4),
    "avg_tamil_suffixes": round(total_suffixes / n, 4),
    "structurally_plausible_count": plausible_count,
    "structurally_plausible_rate": round(plausible_count / n, 4),
    "totals": {
        "switch_points": total_switch,
        "discourse_markers": total_discourse,
        "romanized_candidates": total_romanized,
        "tamil_suffixes": total_suffixes,
    },
}

# ============================================================
# Save
# ============================================================
output_path = Path(r"C:\IGRIS\scratch\phase24_eval_results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n{'=' * 70}")
print(f"All results saved to: {output_path}")
print(f"{'=' * 70}")
