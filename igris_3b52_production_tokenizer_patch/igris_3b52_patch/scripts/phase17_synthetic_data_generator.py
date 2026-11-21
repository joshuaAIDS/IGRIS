"""IGRIS Phase 17 — Synthetic Multilingual Pretraining Dataset Generator.

Generates isolated, reproducible synthetic multilingual pretraining data across 9 Indic & Latin language registers.
Labels all records with strict synthetic provenance metadata and computes SHA-256 manifests.
Zero production data or external network endpoints are accessed.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

from tokenizers import Tokenizer

# Setup patch paths
_PATCH_ROOT = Path(__file__).resolve().parents[1]
_PATCH_SRC = str(_PATCH_ROOT / "src")
_PATCH_SCRIPTS = str(_PATCH_ROOT / "scripts")
for p in [_PATCH_SRC, _PATCH_SCRIPTS]:
    if p not in sys.path:
        sys.path.insert(0, p)

CAND_A_TOKENIZER_PATH = _PATCH_ROOT / "artifacts" / "tokenizer" / "candidate_a" / "tokenizer.json"
OUTPUT_DIR = _PATCH_ROOT / "data" / "synthetic_pretraining_fixtures"
MANIFEST_PATH = _PATCH_ROOT / "PHASE17_SYNTHETIC_DATA_MANIFEST.json"


# Multilingual sentence templates simulating authentic language registers
LANGUAGE_TEMPLATES = {
    "en": [
        "The multilingual decoder model evaluates representations across linguistic topologies.",
        "Computational linguistics requires balanced tokenization across underrepresented scripts.",
        "Deep autoregressive transformers predict next tokens conditioned on causal attention.",
        "The neural architecture combines grouped query attention with rotary position embeddings.",
        "Gradient clipping preserves numerical stability across high-dimensional parameter updates.",
        "Hardware acceleration on local tensor cores optimizes sustained pretraining throughput.",
    ],
    "hi": [
        "यह बहुभाषी ट्रांसफार्मर मॉडल विभिन्न लिपियों के प्रतिनिधित्व का विश्लेषण करता है।",
        "कंप्यूटेशनल भाषाविज्ञान में सभी भारतीय भाषाओं का संतुलित प्रतिनिधित्व आवश्यक है।",
        "यह न्यूरल आर्किटेक्चर स्वदेशी लिपियों के लिए कुशल टोकनाइज़ेशन सुनिश्चित करता है।",
        "ग्रूप्ड क्वेरी अटेंशन और रोटरी एम्बेडिंग मॉडल की गति और सटीकता को बढ़ाते हैं।",
        "पूर्वानुमानित टोकन वितरण बहुभाषी समझ को सशक्त और सुसंगत बनाता है।",
    ],
    "ta": [
        "இந்த பலமொழி மின்மாற்றி மாதிரி இந்திய மொழிகளுக்கான ஆழமான பிரதிநிதித்துவத்தை வழங்குகிறது.",
        "கணினி மொழியியல் ஆய்வில் தமிழ் எழுத்துருக்களின் பயன்பாடு மிக முக்கிய பங்கு வகிக்கிறது.",
        "செயற்கை நுண்ணறிவு கட்டமைப்புகள் மொழிகளுக்கு இடையேயான தொடர்புகளை எளிதாக்குகின்றன.",
        "ரோட்டரி பொசிஷன் எம்பட்டிங் முறையானது தொடர் குறியாக்கத்தை திறம்பட செய்கிறது.",
        "குழு வினவல் கவனம் அமைப்பு நினைவக தேவையை குறைத்து வேகத்தை அதிகரிக்கிறது.",
    ],
    "te": [
        "ఈ బహుభాషా న్యూరల్ నెట్వర్క్ భారతీయ భాషల సహజ భాషా ప్రాసెసింగ్ను మెరుగుపరుస్తుంది.",
        "ట్రాన్స్ఫార్మర్ నమూనా పదాల ప్రాతినిధ్యాలను ఖచ్చితంగా నేర్చుకోవడానికి సహాయపడుతుంది.",
        "గ్రూప్డ్ క్వెరీ అటెన్షన్ మెమరీ వినియోగాన్ని సమర్థవంతంగా తగ్గిస్తుంది.",
        "భాషా నమూనాలు పెద్ద ఎత్తున టెక్స్ట్ డేటాను విశ్లేషించడానికి ఉపయోగపడతాయి.",
    ],
    "ml": [
        "ഈ ബഹുഭാഷാ ട്രാൻസ്ഫോർമർ മോഡൽ സ്വാഭാവിക ഭാഷാ വിശകലനം കൂടുതൽ വേഗത്തിലാക്കുന്നു.",
        "കമ്പ്യൂട്ടേഷണൽ ലിംഗ്വിസ്റ്റിക്സിൽ മലയാളം അക്ഷരങ്ങളുടെ കൃത്യമായ പ്രാതിനിധ്യം അത്യാവശ്യമാണ്.",
        "റോട്ടറി പൊസിഷൻ എംബെഡിംഗ് ദീർഘദൂര സന്ദർഭങ്ങളെ തിരിച്ചറിയാൻ സഹായിക്കുന്നു.",
    ],
    "kn": [
        "ಈ ಬಹುಭಾಷಾ ಮಾದರಿಯು ಭಾರತೀಯ ಭಾಷೆಗಳ ವಿಶ್ಲೇಷಣೆಗೆ ಹೊಸ ದಾರಿಯನ್ನು ತೆರೆಯುತ್ತದೆ.",
        "ಕಂಪ್ಯೂಟೇಶನಲ್ ಲಿಂಗ್ವಿಸ್ಟಿಕ್ಸ್ ಮೂಲಕ ಭಾಷಾ ಸಂಸ್ಕೃತಿಯನ್ನು ರಕ್ಷಿಸಬಹುದು.",
        "ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್ ಮಾದರಿಯು ನಿಖರವಾದ ಪದ ಮುನ್ಸೂಚನೆಯನ್ನು ಒದಗಿಸುತ್ತದೆ.",
    ],
    "bn": [
        "এই বহুভাষিক ট্রান্সফরমার মডেল ভাষা প্রক্রিয়াকরণে অভূতপূর্ব অগ্রগতি এনেছে।",
        "কম্পিউটেশনাল ভাষাতত্ত্বে বিভিন্ন লিপির সঠিক সমন্বয় একান্ত প্রয়োজন।",
        "রোটারি পজিশন এমবেডিং মডেলের দীর্ঘমেয়াদী প্রাসঙ্গিকতা বজায় রাখে।",
    ],
    "gu": [
        "આ બહુભાષી મોડેલ ભારતીય ભાષાઓના ડેટા પર ચોકસાઈપૂર્વક પ્રક્રિયા કરે છે.",
        "ડીપ લર્નિંગ આધારિત ટ્રાન્સફોર્મર કુદરતી ભાષાના વિશ્લેષણમાં મહત્વપૂર્ણ ભૂમિકા ભજવે છે.",
        "ગતિશીલ ગણતરી અને સ્વચ્છ ટોકનાઇઝેશન મોડેલની કાર્યક્ષમતામાં વધારો કરે છે.",
    ],
    "tanglish": [
        "Intha multilingual architecture romba efficiently perform panrathu for Tamil English code-mixed text.",
        "Namma transformer model tokenization evaluation perfectly handle pannuthu without any issue.",
        "Speed and accuracy renderum semma balanced ah irukku on GPU hardware.",
    ],
}


def generate_synthetic_pretraining_dataset(
    target_records: int = 500,
    seed: int = 42,
    output_dir: Path | str | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Generate isolated synthetic multilingual corpus, tokenized tensors, and manifest."""
    random.seed(seed)
    out_dir = Path(output_dir or OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not CAND_A_TOKENIZER_PATH.exists():
        raise FileNotFoundError(f"Candidate A tokenizer not found at {CAND_A_TOKENIZER_PATH}")

    tokenizer = Tokenizer.from_file(str(CAND_A_TOKENIZER_PATH))

    records = []
    total_tokens = 0
    language_counts: dict[str, int] = {lang: 0 for lang in LANGUAGE_TEMPLATES}

    languages = list(LANGUAGE_TEMPLATES.keys())

    for idx in range(target_records):
        lang = languages[idx % len(languages)]
        templates = LANGUAGE_TEMPLATES[lang]
        base_sentence = templates[idx % len(templates)]

        # Augment with slight deterministic variations
        variation_suffix = f" (Sample {idx + 1:04d} - Test Partition {lang})"
        full_text = base_sentence + variation_suffix

        # Tokenize using Candidate A
        encoding = tokenizer.encode(full_text)
        raw_ids = encoding.ids

        # Prepend BOS (1) and append EOS (2)
        token_ids = [1] + raw_ids + [2]

        record = {
            "record_id": f"syn_rec_{idx + 1:06d}",
            "language": lang,
            "text": full_text,
            "token_ids": token_ids,
            "seq_len": len(token_ids),
            "is_synthetic": True,
            "data_label": "SYNTHETIC_TEST_ONLY",
            "provenance": "IGRIS_PHASE17_SYNTHETIC_GENERATOR",
        }
        records.append(record)
        total_tokens += len(token_ids)
        language_counts[lang] += 1

    # Save dataset to JSON
    dataset_file = out_dir / "igris_phase17_synthetic_multilingual.json"
    dataset_content = {
        "metadata": {
            "dataset_id": "IGRIS-DS-PHASE17-SYNTHETIC-001",
            "dataset_type": "SYNTHETIC_FIXTURE_ONLY",
            "generator": "scripts/phase17_synthetic_data_generator.py",
            "random_seed": seed,
            "record_count": len(records),
            "total_tokens": total_tokens,
            "language_distribution": language_counts,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "governance_model": "SOLO_DEVELOPER_OWNER_REVIEW",
            "production_data_present": False,
            "is_production_authorized": False,
        },
        "records": records,
    }

    serialized_data = json.dumps(dataset_content, indent=2, ensure_ascii=False)
    dataset_file.write_text(serialized_data, encoding="utf-8")

    file_sha256 = hashlib.sha256(dataset_file.read_bytes()).hexdigest()

    # Create dataset manifest
    manifest = {
        "dataset_id": "IGRIS-DS-PHASE17-SYNTHETIC-001",
        "dataset_type": "SYNTHETIC_FIXTURE_ONLY",
        "generator_script": "scripts/phase17_synthetic_data_generator.py",
        "random_seed": seed,
        "record_count": len(records),
        "total_tokens": total_tokens,
        "average_seq_len": round(total_tokens / len(records), 2),
        "language_distribution": language_counts,
        "file_name": dataset_file.name,
        "relative_path": str(dataset_file.relative_to(_PATCH_ROOT)),
        "file_sha256": file_sha256,
        "is_synthetic": True,
        "production_data_present": False,
        "governance_status": "LOCKED_SYNTHETIC_EXPERIMENT_ONLY",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return dataset_file, manifest


if __name__ == "__main__":
    data_path, man = generate_synthetic_pretraining_dataset(target_records=500, seed=42)
    print("================================================================================")
    print("IGRIS PHASE 17 — SYNTHETIC DATASET GENERATION COMPLETE")
    print("================================================================================")
    print(f"Dataset File:   {data_path}")
    print(f"Records:        {man['record_count']}")
    print(f"Total Tokens:   {man['total_tokens']:,}")
    print(f"Avg Seq Len:    {man['average_seq_len']}")
    print(f"SHA-256:        {man['file_sha256']}")
    print(f"Manifest Path:  {MANIFEST_PATH}")
    print("================================================================================")
