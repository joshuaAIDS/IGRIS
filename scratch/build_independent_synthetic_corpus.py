"""
scratch/build_independent_synthetic_corpus.py

Generates 3,200 independent synthetic evaluation records
covering 16 semantic categories across Tamil, English, and Tanglish.
Guarantees 100% uniqueness, zero overlap with the original 399 records,
and full compliance with IGRIS-SPEC-LANG-TAXONOMY-V1.
"""

import hashlib
import json
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

WORKSPACE_ROOT = Path(r"C:\IGRIS")
PATCH_ROOT = WORKSPACE_ROOT / "igris_3b52_production_tokenizer_patch" / "igris_3b52_patch"
ARTIFACT_DIR = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102")

GENERATOR_VERSION = "v1.0.0"
RANDOM_SEED = 20261120

def detect_script_form(text: str) -> str:
    has_tamil = bool(re.search(r"[\u0B80-\u0BFF]", text))
    has_latin = bool(re.search(r"[a-zA-Z]", text))
    if has_tamil and has_latin:
        return "MIXED_SCRIPT"
    elif has_tamil:
        return "TAMIL_SCRIPT"
    elif has_latin:
        return "LATIN_SCRIPT"
    else:
        return "OTHER_OR_UNKNOWN"

def build_full_corpus():
    # 1. Load original 399 documents for contamination prevention
    orig_path = WORKSPACE_ROOT / "scratch" / "original_399_texts.json"
    with open(orig_path, encoding="utf-8") as f:
        orig_data = json.load(f)
    
    orig_texts = set(unicodedata.normalize("NFC", d["text"].strip()) for d in orig_data)
    orig_hashes = set(hashlib.sha256(t.encode("utf-8")).hexdigest() for t in orig_texts)
    print(f"Loaded {len(orig_texts)} original reference documents from {orig_path.name}.")

    records = []
    global_seen_texts = set()

    # Category definitions with rich combinatorics
    categories_spec = [
        # 1. TAMIL_CONVERSATIONAL
        {
            "name": "TAMIL_CONVERSATIONAL",
            "op_lang": "TAMIL", "mat_lang": "TAMIL", "subtype": "NONE",
            "slots": [
                [
                    "வணக்கம் நண்பரே,", "அன்பான நண்பா,", "வணக்கம் ஐயா,", "வணக்கம் தோழரே,",
                    "காலை வணக்கம்,", "மாலை வணக்கம் நண்பா,", "வணக்கம் அண்ணா,", "வணக்கம் தம்பி,",
                    "நலம்தானா நண்பரே,", "வணக்கம் சகோதரி,", "அன்புடையீர்,", "இனிய காலை வணக்கம்,"
                ],
                [
                    "நீங்கள் இன்று காலை அலுவலகத்திற்கு", "உங்கள் குடும்பத்தினர் அனைவரும்",
                    "நாம் அனைவரும் அடுத்த வாரம்", "நீங்கள் கேட்ட அந்த புதிய புத்தகம்",
                    "நேற்று நடைபெற்ற கலந்துரையாடல் பற்றி", "உங்கள் புதிய திட்டப் பணிகள்",
                    "மாலை நேரத்தில் நடைப்பயிற்சி செல்ல", "இந்த வார இறுதியில் ஒரு பயணம் மேற்கொள்ள",
                    "நமது ஊர் திருவிழாவிற்கு செல்வது குறித்து", "உங்கள் உடல்நலம் இப்போது எப்படி உள்ளது என்பது பற்றி",
                    "குழந்தைகளின் பள்ளிப் பருவ கல்வி முறை பற்றி", "வீட்டுத் தோட்டம் அமைக்கும் உங்கள் விருப்பம் பற்றி",
                    "புதிய கணினி வாங்குவது குறித்த உங்கள் கருத்து பற்றி", "நமது பழைய நண்பர்களை சந்திப்பது குறித்து"
                ],
                [
                    "எத்தனை மணிக்கு வர திட்டமிட்டுள்ளீர்கள்?", "நலமாக இருக்கிறார்களா என்று அறிந்துகொள்ள விரும்புகிறேன்.",
                    "ஒன்றாக இணைந்து தேநீர் அருந்த செல்லலாமா?", "உங்களுக்கு மிகவும் பயனுள்ளதாக அமைந்ததா?",
                    "மேலும் சில விவரங்களை பகிர்ந்து கொள்ள முடியுமா?", "எந்த அளவிற்கு முன்னேற்றம் கண்டுள்ளது?",
                    "வானிலை மிகவும் இதமாக உள்ளது.", "நாம் அனைவரும் ஒன்றாக திட்டமிடலாம்.",
                    "அனைத்து ஏற்பாடுகளும் சரியாக நடந்து கொண்டிருக்கின்றனவா?", "மருத்துவர் கூறிய ஆலோசனைகளை முறையாகப் பின்பற்றுகிறீர்களா?",
                    "நல்ல முன்னேற்றம் ஏற்பட்டுள்ளது என்று நம்புகிறேன்.", "அனைத்து விவரங்களையும் விரிவாகப் பேச வேண்டும்.",
                    "தங்கள் மேலான கருத்துக்களை தெரிவிக்க வேண்டுகிறேன்.", "எப்போது நேரம் கிடைக்கும் என்பதை எனக்குத் தெரிவியுங்கள்."
                ],
                [
                    "உங்கள் பதிலை ஆவலுடன் எதிர்பார்க்கிறேன்.", "நேரம் கிடைக்கும்போது அழையுங்கள்.",
                    "விரைவில் மீண்டும் சந்திப்போம்.", "நன்றி, நல்ல நாளாக அமையட்டும்.",
                    "பார்த்து கவனமாக செல்லுங்கள்.", "தங்கள் வருகைக்கு மிக்க நன்றி.",
                    "குடும்பத்தினருக்கு எனது அன்பைத் தெரிவியுங்கள்.", "எப்போதும் தொடர்பில் இருப்போம்.",
                    "அனைவருக்கும் எனது நல்வாழ்த்துகள்.", "நன்றி, வணக்கம்."
                ]
            ],
            "template": "{0} {1} {2} {3}"
        },
        # 2. TAMIL_FORMAL
        {
            "name": "TAMIL_FORMAL",
            "op_lang": "TAMIL", "mat_lang": "TAMIL", "subtype": "NONE",
            "slots": [
                [
                    "தமிழ்நாடு அரசின் உயர்கல்வித் துறை", "சென்னை மாநகராட்சி நிர்வாகம்",
                    "மாவட்ட ஆட்சியர் அலுவலக செய்திக்குறிப்பு", "மாநில திட்டக் குழுவின் புதிய அறிக்கை",
                    "பல்கலைக்கழக மானியக் குழுவின் வழிகாட்டுதல்கள்", "பொது சுகாதாரத் துறையின் அறிவிப்பு",
                    "தொழிலாளர் நல வாரியத்தின் புதிய திட்டம்", "சுற்றுச்சூழல் பாதுகாப்பு ஆணையத்தின் உத்தரவு",
                    "மாநில போக்குவரத்து கழக தலைமை அலுவலகம்", "நீர்வள ஆதாரங்கள் மேலாண்மைத் துறை",
                    "வருவாய் மற்றும் பேரிடர் மேலாண்மைத் துறை", "வேளாண்மை மற்றும் உழவர் நலத்துறை"
                ],
                [
                    "அனைத்து அரசு மற்றும் தனியார் நிறுவனங்களுக்கும் அதிகாரப்பூர்வ சுற்றறிக்கை அனுப்பியுள்ளது.",
                    "பொதுமக்களின் நல்வாழ்வு கருதி சிறப்பு மருத்துவ மற்றும் விழிப்புணர்வு முகாம்களை ஏற்பாடு செய்துள்ளது.",
                    "வருடாந்திர நிதி ஒதுக்கீடு மற்றும் செலவினங்கள் குறித்த விரிவான ஆய்வறிக்கையை வெளியிட்டுள்ளது.",
                    "புதிய ஒழுங்குமுறை விதிகளையும் நடைமுறைகளையும் உடனடியாக அமல்படுத்த உத்தரவிட்டுள்ளது.",
                    "கிராமப்புற மாணவர்களின் கல்வித் தரத்தை உயர்த்தும் முன்னோடித் திட்டங்களை வகுத்துள்ளது.",
                    "நிலத்தடி நீர்மட்டத்தை உயர்த்த மழைநீர் சேகரிப்பு அமைப்புகளை கட்டாயமாக்கியுள்ளது.",
                    "விவசாயிகளுக்கு தேவையான நவீன வேளாண் கருவிகளையும் விதைகளையும் மானிய விலையில் வழங்குகிறது.",
                    "சாலைப் பாதுகாப்பை உறுதி செய்ய நவீன கண்காணிப்பு கேமராக்களை நிறுவியுள்ளது.",
                    "தொழில் முனைவோருக்கான கடன் வசதிகளையும் வழிகாட்டுதல்களையும் விரிவுபடுத்தியுள்ளது.",
                    "பேரிடர் கால அவசர உதவி மையங்களை இருபத்து நான்கு மணி நேரமும் செயல்பட வைத்துள்ளது."
                ],
                [
                    "இதன் மூலம் பல்லாயிரக்கணக்கான மக்கள் நேரடியாகப் பயனடைவார்கள் என்று எதிர்பார்க்கப்படுகிறது.",
                    "இத்திட்டம் மாநிலத்தின் நிலையான பொருளாதார வளர்ச்சிக்கு வலுவான அடித்தளமாக அமையும்.",
                    "அனைத்து துறைசார் அதிகாரிகளும் விதிமுறைகளை முறையாகப் பின்பற்றுமாறு அறிவுறுத்தப்படுகிறார்கள்.",
                    "பொதுமக்கள் இந்த நல்வாய்ப்பினை முழுமையாகப் பயன்படுத்திக் கொள்ள வேண்டும் என கேட்டுக் கொள்ளப்படுகிறார்கள்.",
                    "எதிர்கால தலைமுறையினரின் வாழ்க்கைத் தரத்தை உயர்த்துவதில் இது முக்கிய மைல்கல்லாக விளங்கும்.",
                    "இதன் முன்னேற்றம் குறித்த மாதாந்திர அறிக்கை அரசிடம் நேரடியாக சமர்ப்பிக்கப்படும்.",
                    "அரசு இயந்திரத்தின் வெளிப்படையான நிர்வாகத்திற்கு இது ஒரு சிறந்த முன்னுதாரணமாகும்."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 3. TAMIL_EDUCATIONAL
        {
            "name": "TAMIL_EDUCATIONAL",
            "op_lang": "TAMIL", "mat_lang": "TAMIL", "subtype": "NONE",
            "slots": [
                [
                    "ஒளிச்சேர்க்கை என்பது", "பூமியின் வளிமண்டலத்தில் காணப்படும் நைட்ரஜன் வாயு",
                    "மனித உடலில் உள்ள இரத்த ஓட்ட மண்டலம்", "நியூட்டனின் இரண்டாம் இயக்க விதி",
                    "சூரியக் குடும்பத்தில் உள்ள கோள்களின் சுழற்சி முறை", "நீரின் சுழற்சி மற்றும் ஆவியாதல் நிகழ்வு",
                    "டிஎன்ஏ மூலக்கூறின் இரட்டைச் சுருள் கட்டமைப்பு", "பண்டைய சோழப் பேரரசின் நீர்ப்பாசனக் கட்டமைப்பு",
                    "காந்தப்புலமும் மின்னோட்டமும் உருவாக்கும் மின்காந்தத் தூண்டல்", "புவியீர்ப்பு விசை மற்றும் நிறை ஈர்ப்பு மையத்தின் பண்புகள்",
                    "தாவர செல்களில் உள்ள பசுங்கணிகங்களின் வேதிவினை", "மனித மூளையின் நரம்பு மண்டலத் தகவல் பரிமாற்றம்",
                    "அமிலங்கள் மற்றும் காரங்களின் வேதியியல் சமநிலை", "பண்டைய தமிழர்களின் வானியல் மற்றும் பஞ்சாங்கக் கணிப்பு"
                ],
                [
                    "தாவரங்கள் சூரிய ஒளியைப் பயன்படுத்தி தமக்குத் தேவையான உணவைத் தயாரிக்கும் அடிப்படை உயிரியல் செயல்பாடாகும்.",
                    "சுமார் எழுபத்தெட்டு விழுக்காடு அளவில் நிறைந்து பூமியின் வெப்பநிலையை சீராகப் பராமரிக்க உதவுகிறது.",
                    "இதயம், இரத்தக் குழாய்கள் மற்றும் இரத்தம் ஆகியவற்றின் மூலம் உடலின் அனைத்து செல்களுக்கும் ஊட்டச்சத்தை வழங்குகிறது.",
                    "பொருளின் மீது செயல்படும் விசை அதன் நிறை மற்றும் முடுக்கத்தின் பெருக்கற்பலனுக்கு சமம் என்பதை விளக்குகிறது.",
                    "ஈர்ப்பு விசையின் காரணமாக சூரியனை மையமாகக் கொண்டு நீள்வட்டப் பாதையில் தொடர்ந்து இயங்குகிறது.",
                    "கடல் நீரானது ஆவியாகி மேகங்களாக மாறி மீண்டும் மழையாகப் பொழியும் தொடர்ச்சியான இயற்கை நிகழ்வாகும்.",
                    "மரபியல் தகவல்களை தலைமுறை தலைமுறையாகக் கடத்தும் முதன்மையான மூலக்கூறு அமைப்பாக செயல்படுகிறது.",
                    "விவசாய உற்பத்தியை பெருக்க ஏரிகள், கால்வாய்கள் மற்றும் அணைகளை அமைத்து வரலாற்று சாதனை படைத்தது.",
                    "மின்சார உற்பத்தியிலும் நவீன மின்னணு சாதனங்களின் இயக்கத்திலும் மிக முக்கிய பங்கு வகிக்கிறது.",
                    "பூமியில் உள்ள அனைத்துப் பொருட்களையும் அதன் மையத்தை நோக்கி ஈர்க்கும் இயற்கை விதியாகும்.",
                    "கார்பன் டை ஆக்சைடு மற்றும் நீரைப் பயன்படுத்தி குளுக்கோஸ் மூலக்கூறுகளை உற்பத்தி செய்கிறது.",
                    "மில்லியன் கணக்கான நியூரான்கள் மின் சமிக்ஞைகள் வழியே எண்ணங்களையும் உணர்வுகளையும் கடத்துகின்றன.",
                    "ஹைட்ரஜன் அயனிகளின் செறிவை அடிப்படையாகக் கொண்டு அமிலத்தன்மையும் காரத்தன்மையும் அளவிடப்படுகின்றன.",
                    "சூரியன், சந்திரன் மற்றும் நட்சத்திரங்களின் நகர்வுகளை துல்லியமாகக் கணித்து காலத்தைப் பிரித்தனர்."
                ],
                [
                    "இக்கருத்து அறிவியல் பாடத்திட்டத்தில் மிக முக்கியமான அடிப்படைப் பகுதியாகக் கருதப்படுகிறது.",
                    "இதனைப் புரிந்து கொள்வது உயர்நிலை அறிவியல் ஆய்வுகளுக்கு அடித்தளமாக அமைகிறது.",
                    "இயற்கையின் விதிகளையும் சமநிலையையும் உணர்ந்து கொள்ள இது ஒரு சிறந்த சான்றாகும்.",
                    "மாணவர்கள் இத்தகைய அறிவியல் உண்மைகளை செய்முறை வழியே கற்பது கூடுதல் தெளிவை அளிக்கும்.",
                    "அறிவியல் அறிவை நடைமுறை வாழ்க்கையோடு இணைத்துப் பார்க்க இது வழிவகை செய்கிறது.",
                    "நவீன கண்டுபிடிப்புகளுக்கு இத்தகைய அடிப்படை அறிவியல் கோட்பாடுகளே வழிகாட்டியாக உள்ளன.",
                    "ஆராய்ச்சித் துறையில் சிறந்து விளங்க இந்த அடிப்படைக் கோட்பாடுகள் இன்றியமையாதவை."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 4. TAMIL_TECHNICAL
        {
            "name": "TAMIL_TECHNICAL",
            "op_lang": "TAMIL", "mat_lang": "TAMIL", "subtype": "NONE",
            "slots": [
                [
                    "கணினி அமைப்புகளில் நினைவக மேலாண்மை", "நவீன வலைப்பின்னல் பாதுகாப்பு நெறிமுறைகள்",
                    "தரவுத்தள அட்டவணைகளின் சுட்டெண் வடிவமைப்பு", "வரிசை மற்றும் அடுக்கு போன்ற அடிப்படைத் தரவுக் கட்டமைப்புகள்",
                    "செயற்கை நுண்ணறிவு மாதிரிகளின் பயிற்சி வழிமுறைகள்", "நிகழ்நேர செயலாக்க அமைப்புகளில் தாமதத்தைக் குறைக்கும் நுட்பங்கள்",
                    "பகிர்ந்தளிக்கப்பட்ட கணினி அமைப்புகளில் தரவு ஒத்திசைவு", "இயக்க முறைமையின் மையக் கருவான கர்னல் மேலாண்மை",
                    "வலைத்தள பாதுகாப்பு மற்றும் குறியாக்க நெறிமுறைகள்", "மேகக்கணி உள்கட்டமைப்பில் வளங்களை தானாக அளவிடுதல்",
                    "தொகுப்பு நிரலாக்கம் மற்றும் உரை திருத்தக் கருவிகளின் வடிவமைப்பு", "இணைய நெறிமுறை முகவரிகளின் வழியமைப்பு நெறிமுறைகள்"
                ],
                [
                    "தேவையற்ற நினைவகக் கசிவுகளைத் தடுத்து மென்பொருளின் வேகத்தை பன்மடங்கு அதிகரிக்க உதவுகிறது.",
                    "அங்கீகரிக்கப்படாத ஊடுருவல்களைத் தடுத்து ரகசியத் தரவுகளின் ஒருமைப்பாட்டை உறுதி செய்கிறது.",
                    "தேடல் வினவல்களின் வேகத்தை உயர்த்தி வட்டு வாசிப்பு நேரத்தை கணிசமாகக் குறைக்கிறது.",
                    "அல்காரிதம்களின் நேரச் சிக்கல் மற்றும் இடச் சிக்கலை திறம்பட நிர்வகிக்க வழிவகுக்கிறது.",
                    "பெரிய அளவிலான தரவுத்தொகுப்புகளைப் பகுப்பாய்வு செய்து துல்லியமான கணிப்புகளை வழங்குகிறது.",
                    "செயல்திறன் இடையூறுகளைக் கண்டறிந்து வன்பொருள் வளங்களை உகந்த முறையில் பயன்படுத்துகிறது.",
                    "வலையமைப்புத் தடங்கல்கள் ஏற்பட்டாலும் கணினி சேவைகள் தடையின்றி இயங்குவதை உறுதி செய்கிறது.",
                    "செயலிகளுக்கு நினைவகம் மற்றும் வன்பொருள் சாதனங்களை பாரபட்சமின்றி ஒதுக்கீடு செய்கிறது.",
                    "தரவுப் பரிமாற்றத்தின் போது ரகசியத்தன்மையை பாதுகாக்கும் நவீன கிரிப்டோகிராஃபி முறைகளைப் பயன்படுத்துகிறது.",
                    "பயனர்களின் போக்குவரத்து அதிகரிக்கும் போது தானாகவே புதிய சேவையகங்களை உருவாக்குகிறது."
                ],
                [
                    "இது பொறியியல் வடிவமைப்பில் மிகச் சிறந்த நடைமுறையாக பரிந்துரைக்கப்படுகிறது.",
                    "மென்பொருள் பொறியாளர்கள் இந்த கொள்கைகளைத் துல்லியமாகக் கடைப்பிடிப்பது அவசியமாகும்.",
                    "உயர் செயல்திறன் கொண்ட உற்பத்தி அமைப்புகளில் இக்கட்டமைப்பு அத்தியாவசியமானது.",
                    "கணினி அறிவியலின் நவீன வளர்ச்சியில் இது ஒரு மைல்கல்லாகக் கருதப்படுகிறது.",
                    "இதன் மூலம் கணினி வளங்களின் விரயம் தடுக்கப்பட்டு செலவுகள் குறைக்கப்படுகின்றன.",
                    "நம்பகமான அமைப்புகளை கட்டமைக்க இந்த வடிவமைப்பு நெறிமுறைகள் பெரிதும் உதவுகின்றன."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 5. TAMIL_LONGFORM
        {
            "name": "TAMIL_LONGFORM",
            "op_lang": "TAMIL", "mat_lang": "TAMIL", "subtype": "NONE",
            "slots": [
                [
                    "தமிழ்ச் செவ்வியல் இலக்கியங்களும் நவீன அறிவியல் சிந்தனைகளும் மனித குலத்திற்கு ஆழமான வழிகாட்டலை வழங்குகின்றன.",
                    "வரலாற்று ரீதியாக தமிழர்களின் கடல்சார் வாணிபமும் நகரக் கட்டமைப்பும் உலக அளவில் தனித்துவமான பெருமை பெற்றவை.",
                    "இயற்கையோடு இயைந்த வாழ்வியலும் சுற்றுச்சூழல் சமநிலையும் நமது தொன்மையான மரபில் ஆழமாக வேரூன்றியுள்ளன.",
                    "அறிவியல் மற்றும் தொழில்நுட்ப வளர்ச்சியானது தாய்மொழி வழிக் கல்வியின் மூலம் சமூகத்தின் அனைத்துத் தளங்களையும் சென்றடைய வேண்டும்.",
                    "பண்டைய தமிழகத்தின் நீர் மேலாண்மை திட்டங்களும் வேளாண்மை நுணுக்கங்களும் இன்றும் ஆய்வாளர்களை வியப்பில் ஆழ்த்துகின்றன.",
                    "மொழியின் தொன்மையும் இலக்கியச் செறிவும் ஒரு சமூகத்தின் பண்பாட்டு அடையாளத்தை நிலைநிறுத்தும் தூண்களாக விளங்குகின்றன.",
                    "தற்கால தகவல் தொழில்நுட்ப யுகத்தில் தமிழ் மொழியின் பயன்பாடு உலகெங்கிலும் பரந்து விரிந்து காணப்படுகிறது.",
                    "கலை, கட்டிடக்கலை மற்றும் சிற்பக்கலை ஆகியவற்றில் தமிழர்களின் பங்களிப்பு உலக பாரம்பரியச் சின்னங்களாகப் போற்றப்படுகின்றன."
                ],
                [
                    "சங்க இலக்கியங்கள் இயற்கையை வெறும் பின்னணியாகப் பார்க்காமல், மனித உணர்வுகளோடு இணைத்துப் பாடியுள்ளன. காடுகளையும் ஆறுகளையும் பாதுகாப்பது சமூகத்தின் கடமை என்று அவை வலியுறுத்துகின்றன.",
                    "பூம்புகார், கொற்கை போன்ற துறைமுகங்கள் வழியே ரோம், எகிப்து மற்றும் தென்கிழக்கு ஆசிய நாடுகளோடு விரிவான வர்த்தகத் தொடர்புகள் நிலவின. ஏற்றுமதி செய்யப்பட்ட மிளகு மற்றும் முத்து உலகச் சந்தைகளில் மிகுந்த மதிப்பைப் பெற்றிருந்தன.",
                    "கல்லணை போன்ற பிரம்மாண்டமான நீர் மேலாண்மைக் கட்டமைப்புகள் இரண்டாயிரம் ஆண்டுகளுக்கு முன்பே தமிழர்களின் பொறியியல் அறிவிற்கு சான்றாக திகழ்கின்றன. ஆற்று நீரை சமதளத்தில் திருப்பி விவசாயத்திற்குப் பயன்படுத்திய விதம் வியப்பிற்குரியது.",
                    "நவீன கணினித் தொழில்நுட்பத்தில் தமிழ் மொழியை முதன்மைப்படுத்தும் மென்பொருட்களும் உள்ளீட்டுக் கருவிகளும் தொடர்ந்து உருவாக்கப்பட்டு வருகின்றன. இதன் வாயிலாக அறிவுப் பரவலாக்கம் விரைவுபடுத்தப்படுகிறது.",
                    "திருக்குறள் போன்ற அறநூல்கள் மனித வாழ்க்கைக்குத் தேவையான உலகளாவிய விழுமியங்களை எளிய ஈரடிகளில் அழகுற விளக்குகின்றன. காலம் கடந்தும் வாழும் இந்த தத்துவங்கள் எக்காலத்திற்கும் ஏற்ற நெறிமுறைகளாகப் திகழ்கின்றன.",
                    "தஞ்சைப் பெருவுடையார் கோவில் போன்ற கட்டிடக்கலை அதிசயங்கள் தமிழர்களின் கணித, சிற்ப மற்றும் புவியியல் ஞானத்தின் உச்சக்கட்ட சாதனையாக விளங்குகின்றன. பிரம்மாண்டமான கருங்கற்களை அடுக்கி கட்டப்பட்ட இந்த கோபுரம் கம்பீரமாக நிற்கிறது."
                ],
                [
                    "அத்தகைய விழிப்புணர்வு இன்றைய காலநிலை மாற்ற சூழலில் மேலும் பொருத்தமுடையதாகிறது.",
                    "கல்வெட்டுகள் மற்றும் நாணயச் சான்றுகள் இந்த வளமான வணிக வரலாற்றை உறுதிப்படுத்துகின்றன.",
                    "இது போன்ற நுட்பங்களை தற்கால நீரியல் ஆய்வுகளிலும் ஆய்வாளர்கள் பெருமையுடன் குறிப்பிடுகின்றனர்.",
                    "கிராமப்புற மாணவர்களும் புதிய தலைமுறை ஆய்வாளர்களும் தொழில்நுட்பப் பலன்களை எளிதில் பெற முடிகிறது.",
                    "உலகப் பொதுமறை என்று போற்றப்படும் இந்நூல் பல்வேறு உலக மொழிகளில் மொழிபெயர்க்கப்பட்டுள்ளது.",
                    "ஆயிரம் ஆண்டுகள் கடந்தும் இயற்கைச் சீற்றங்களைத் தாங்கி தமிழர்களின் பெருமையை பறைசாற்றுகிறது."
                ],
                [
                    "எனவே, நமது தொன்மையை நினைவுகூர்வதுடன் எதிர்காலத் தேவைகளுக்கான புத்தாக்கங்களையும் உருவாக்குவதே நமது முதன்மையான கடமையாகும்.",
                    "இத்தகைய வரலாற்றுப் பாடங்கள் எதிர்கால சந்ததியினருக்கு தன்னம்பிக்கையையும் தெளிவான வழிகாட்டலையும் தொடர்ந்து வழங்கும் என்பதில் ஐயமில்லை.",
                    "பாரம்பரிய அறிவையும் சமகால அறிவியல் பார்வையையும் இணைத்து முன்னேறுவதே ஒரு சமூகத்தின் முழுமையான வளர்ச்சிக்கு வழிகோலும்.",
                    "இப்பெருமைமிகு மரபினைப் பாதுகாத்து உலக அரங்கில் தொடர்ந்து முன்னிறுத்துவது நம் ஒவ்வொருவரின் வரலாற்றுப் பொறுப்பாகும்.",
                    "நமது மொழி மற்றும் பண்பாட்டின் உன்னதத்தை அடுத்த தலைமுறைக்கு கொண்டு சேர்ப்பதில் நாம் அனைவரும் உறுதியாக இருப்போம்."
                ]
            ],
            "template": "{0} {1} {2} {3}"
        },
        # 6. ENGLISH_CONVERSATIONAL
        {
            "name": "ENGLISH_CONVERSATIONAL",
            "op_lang": "ENGLISH", "mat_lang": "ENGLISH", "subtype": "NONE",
            "slots": [
                [
                    "Hello team,", "Good morning everyone,", "Hi Sarah,", "Hey Alex,",
                    "Good afternoon colleagues,", "Hi everyone,", "Hello David,", "Hi team,",
                    "Hope you are having a great week,", "Good day to everyone,", "Hi all,", "Greetings team,"
                ],
                [
                    "could we quickly sync up on the sprint progress", "let us review the feedback received from the customer testing session",
                    "please make sure to submit your timesheets and project updates", "I wanted to check if the staging deployment completed successfully",
                    "can we reschedule our afternoon architectural alignment discussion", "let us make sure everyone has access to the new testing environment",
                    "do we have all the required assets for tomorrow's client presentation", "I have summarized the core action items from our morning standup",
                    "would you be open to a quick call regarding the UI design mocks", "we should definitely coordinate our schedule for next week's release",
                    "could you confirm if the latest pull request has passed all sanity checks", "let us review the updated sprint velocity and backlog tickets"
                ],
                [
                    "before we jump into the wider executive review.", "so that we can address any blocking questions right away.",
                    "as early as possible to prevent payroll cutoff delays.", "and whether all integration tests passed without regressions.",
                    "to give everyone enough time to prepare their proposals.", "before we start the scheduled end-to-end regression run.",
                    "so we can run through the slides one final time.", "and shared them on the project workspace channel.",
                    "and see if there are any pending design clarifications.", "to ensure a smooth and seamless rollout for our users.",
                    "before merging the branch into our release candidate.", "and identify tasks that need immediate assistance from the leads."
                ],
                [
                    "Looking forward to catching up soon.", "Let me know if you need any assistance.",
                    "Thanks for your continuous support and great work.", "Feel free to ping me if anything looks urgent.",
                    "Have a wonderful and productive day ahead.", "Best regards to everyone.",
                    "Appreciate your prompt attention to this matter.", "Talk to you all shortly."
                ]
            ],
            "template": "{0} {1} {2} {3}"
        },
        # 7. ENGLISH_TECHNICAL_DOCS
        {
            "name": "ENGLISH_TECHNICAL_DOCS",
            "op_lang": "ENGLISH", "mat_lang": "ENGLISH", "subtype": "NONE",
            "slots": [
                [
                    "The distributed identity service", "This microservice API gateway",
                    "The event-driven messaging layer", "Our relational database connection pool",
                    "The telemetry and metrics ingestion pipeline", "The containerized cluster orchestrator",
                    "The object storage replication subsystem", "The edge proxy caching mechanism",
                    "The asynchronous task scheduling daemon", "The schema validation middleware",
                    "The distributed configuration coordinator", "The network ingress controller"
                ],
                [
                    "issues cryptographically signed JWT tokens with a fifteen-minute expiration window",
                    "routes incoming HTTP requests based on path prefixes and authenticated tenant headers",
                    "guarantees at-least-once message delivery using distributed consumer groups and offset commits",
                    "dynamically maintains healthy database connections using exponential backoff and circuit breaking",
                    "aggregates high-cardinality time series metrics and streams structured audit logs",
                    "monitors node health and automatically schedules pods across isolated availability zones",
                    "asynchronously synchronizes blob objects across multi-region geographic storage buckets",
                    "caches static asset responses at point-of-presence servers to minimize origin server load",
                    "executes scheduled background cleanup jobs with strict execution timeouts and deadlocks checks",
                    "validates incoming JSON request payloads against strict OpenAPI specification schemas",
                    "distributes dynamic environment variables with cryptographic key decryption at startup",
                    "terminates TLS handshakes using modern elliptic curve ciphers and manages certificate renewal"
                ],
                [
                    "ensuring strict compliance with enterprise security and audit standards.",
                    "thereby preventing cascading failures during sudden upstream network partitions.",
                    "which significantly enhances horizontal scalability under heavy concurrent load.",
                    "providing sub-millisecond p99 response times for mission-critical operations.",
                    "while maintaining deterministic idempotent processing for all write mutations.",
                    "reducing operational maintenance overhead across heterogeneous cloud environments.",
                    "facilitating real-time observability across all downstream consumer microservices.",
                    "preventing unauthorized data exfiltration across isolated tenant boundaries."
                ]
            ],
            "template": "{0} {1}, {2}"
        },
        # 8. ENGLISH_PROGRAMMING
        {
            "name": "ENGLISH_PROGRAMMING",
            "op_lang": "ENGLISH", "mat_lang": "ENGLISH", "subtype": "NONE",
            "slots": [
                [
                    "In modern asynchronous programming, using non-blocking primitives",
                    "When implementing concurrent hash maps, lock striping techniques",
                    "Recursive algorithms operating on deeply nested hierarchical trees",
                    "Utilizing immutable data structures in multi-threaded workflows",
                    "Memory profiling tools that track heap allocations and garbage collection cycles",
                    "Dependency injection patterns applied to modular software architectures",
                    "Database transaction isolation levels such as snapshot isolation",
                    "Optimizing matrix multiplication kernels using vectorized SIMD instructions",
                    "Implementing rate limiting algorithms like token bucket or leaky bucket",
                    "Designing robust error handling pipelines using monadic result types",
                    "Applying structural pattern matching to parse complex Abstract Syntax Trees",
                    "Managing thread pool worker threads with bounded blocking queues"
                ],
                [
                    "prevent thread starvation and maximize CPU core utilization during heavy I/O operations.",
                    "substantially reduce synchronization contention among competing worker threads.",
                    "require logarithmic call stack depth to avoid catastrophic stack overflow exceptions.",
                    "eliminate data races by rendering shared state completely read-only after initialization.",
                    "help developers identify persistent memory leaks and uncollected object references.",
                    "decouple interface contracts from concrete implementations, facilitating comprehensive unit testing.",
                    "prevent phantom reads and non-repeatable reads without incurring pervasive table-level locks.",
                    "achieve near-theoretical peak memory bandwidth and computational throughput.",
                    "safeguard downstream backend microservices against distributed denial of service spikes.",
                    "eliminate unhandled null pointer exceptions by explicitly encoding failure domains.",
                    "simplify compiler transformation passes and optimize intermediate code generation.",
                    "provide graceful backpressure when incoming traffic exceeds server processing capacity."
                ],
                [
                    "This principle is fundamental to designing reliable high-throughput software systems.",
                    "Engineers should rigorously benchmark these implementations under production-like traffic profiles.",
                    "Adhering to this design pattern simplifies code readability and ongoing maintainability.",
                    "Careful profiling ensures optimal cache locality and predictable execution latencies.",
                    "Software teams widely consider this pattern an industry gold standard in distributed systems.",
                    "Following these guidelines drastically reduces maintenance debt and production outages."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 9. ENGLISH_EDUCATIONAL
        {
            "name": "ENGLISH_EDUCATIONAL",
            "op_lang": "ENGLISH", "mat_lang": "ENGLISH", "subtype": "NONE",
            "slots": [
                [
                    "Photosynthesis in green plants", "The theory of plate tectonics",
                    "Cellular respiration in aerobic organisms", "The macroeconomic concept of inflation",
                    "Newton's universal law of gravitation", "The structure of the human central nervous system",
                    "The historical impact of the printing press", "The fundamental principles of thermodynamics",
                    "The chemical bonding mechanisms in covalent molecules", "The mathematical concept of prime numbers and factorization",
                    "The hydrological cycle of precipitation and evaporation", "The evolutionary mechanics of natural selection"
                ],
                [
                    "converts carbon dioxide and water into glucose and oxygen utilizing photon energy absorbed by chlorophyll pigments.",
                    "explains how large continental and oceanic plates drift over the asthenosphere, causing earthquakes and volcanic activity.",
                    "breaks down nutrient molecules inside the mitochondria to generate adenosine triphosphate for cellular metabolic work.",
                    "describes the general sustained increase in price levels and the corresponding erosion of purchasing power within an economy.",
                    "states that every particle attracts every other particle with a force proportional to the product of their masses.",
                    "integrates sensory inputs and coordinates voluntary and involuntary physiological responses throughout the human body.",
                    "democratized the widespread dissemination of scientific literature and accelerated literacy rates across Renaissance Europe.",
                    "dictates the conservation of total energy and the inevitable increase in entropy within isolated physical systems.",
                    "involves the mutual sharing of valence electron pairs between atoms to establish stable electron configurations.",
                    "serves as the mathematical foundation for modern public key cryptography and secure communication channels.",
                    "continuously circulates freshwater across oceans, atmosphere, and land surfaces through solar heating.",
                    "demonstrates how organisms with favorable traits exhibit greater reproductive success across successive generations."
                ],
                [
                    "Understanding this foundational concept is essential for advanced studies in the biological and physical sciences.",
                    "This scientific model revolutionized our understanding of natural phenomena across centuries of inquiry.",
                    "Educators emphasize this topic as a cornerstone of rigorous scientific and historical literacy.",
                    "Empirical experiments continue to validate the mathematical and observational predictions of this theory.",
                    "Grasping these core principles provides vital intuition for solving complex real-world challenges.",
                    "Modern curricula consider this principle fundamental to fostering scientific curiosity and critical thinking."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 10. ENGLISH_LONGFORM
        {
            "name": "ENGLISH_LONGFORM",
            "op_lang": "ENGLISH", "mat_lang": "ENGLISH", "subtype": "NONE",
            "slots": [
                [
                    "The evolution of distributed computing architectures has fundamentally redefined enterprise software engineering practices.",
                    "Modern database management systems must navigate subtle trade-offs between consistency, availability, and partition tolerance.",
                    "The proliferation of artificial intelligence models has heightened the importance of algorithmic transparency and data provenance.",
                    "Operating system kernels have progressively evolved to balance low-latency hardware abstraction with robust fault isolation.",
                    "The history of network protocols reveals a continuous tension between centralized coordination and autonomous peer-to-peer routing.",
                    "Software security architectures increasingly adopt zero-trust principles to protect against insider threats and perimeter breaches."
                ],
                [
                    "Historically, monolithic systems concentrated business logic and state persistence within tightly coupled deployment units. As user bases expanded into tens of millions, horizontal scaling constraints compelled the transition toward decentralized microservice networks.",
                    "Under the CAP theorem, distributed data stores cannot simultaneously achieve linearizable consistency and continuous availability during network splits. Systems opting for eventual consistency rely on vector clocks, gossip protocols, and conflict-free replicated data types.",
                    "Training large-scale deep learning models demands enormous computational throughput across specialized accelerator clusters. Effective pipeline parallelism and tensor sharding strategies are critical to prevent memory exhaustion and communication bottlenecks.",
                    "Contemporary microkernels and virtualized hypervisors compartmentalize untrusted device drivers outside privileged execution rings. By enforcing strict memory protection boundaries through hardware-assisted page table virtualization, platforms prevent compromised firmware from destabilizing the host.",
                    "In modern zero-trust security postures, network locality no longer implies implicit authorization. Every single remote procedure call must present verifiable cryptographic identity tokens, mutual TLS authentication, and fine-grained attribute-based access controls.",
                    "Cloud-native container orchestration platforms dynamically automate resource allocation, health checks, and rolling software upgrades across thousands of bare-metal machines. Decoupling application packaging from the underlying OS distribution provides predictable environments."
                ],
                [
                    "While microservices introduce operational complexity in service discovery and distributed tracing, they grant independent teams the autonomy to iterate and deploy features rapidly.",
                    "This architectural compromise delivers outstanding read throughput while sustaining acceptable resilience against transient network outages.",
                    "Furthermore, establishing immutable audit trails for dataset acquisition and curation ensures that downstream model representations remain reproducible and verifiable.",
                    "Consequently, high-security computing environments achieve predictable performance without forfeiting defense-in-depth guarantees.",
                    "This comprehensive verification prevents lateral movement in the event of an individual node compromise.",
                    "Eliminating subtle environmental discrepancies between staging and production dramatically improves long-term software reliability."
                ],
                [
                    "In conclusion, addressing these multifaceted challenges requires a harmonious blend of principled theoretical design and pragmatic systems engineering.",
                    "Ultimately, software architects must carefully evaluate specific workload characteristics rather than adopting dogmatic technological solutions.",
                    "Continuous empirical benchmarking and automated regression testing remain the most dependable safeguards for maintaining long-term system stability.",
                    "Moving forward, adopting open standards and transparent operational telemetry will be indispensable for building resilient digital infrastructure.",
                    "These enduring architectural principles will continue to shape the trajectory of modern computer systems for decades to come."
                ]
            ],
            "template": "{0} {1} {2} {3}"
        },
        # 11. TANGLISH_ROMANIZED
        {
            "name": "TANGLISH_ROMANIZED",
            "op_lang": "TANGLISH", "mat_lang": "TANGLISH", "subtype": "ROMANIZED_TAMIL",
            "slots": [
                [
                    "Vanakkam nanba,", "Enna bro,", "Dei thambi,", "Vanakkam boss,",
                    "Hello machan,", "Hi friend,", "Kekkutha bro,", "Vanakkam thozha,",
                    "Enna da,", "Machi,", "Vanakkam anna,", "Hi nanbargale,"
                ],
                [
                    "innaiku office-kku late-ah thaan poven", "nethu sonna project work-ah",
                    "intha pudhiya feature development-ah", "antha API documentation file-ah",
                    "namma team meeting discussion-la", "weekend trip porathukku tickets-ah",
                    "intha code review changes-ah", "system performance issue-va",
                    "database query latency problem-ah", "mobile app crashing issue-va",
                    "deployment pipeline failure reason-ah", "client feedback email-ah"
                ],
                [
                    "kandippa innaiku evening kulla mudikanum.", "check panni status update anuppungada.",
                    "seekiram mudichu testing team-kku kudukanum.", "email-la attach panni send pannirukken.",
                    "ellorume kandippa participate pannanum.", "book panniyaacha nu therinjukalam.",
                    "merge panna munnadi verify pannanum.", "analyze panni fix panna try panren.",
                    "optimize panni load test panni paakanum.", "reproduce panni debug panna paakuren.",
                    "root cause identify panni report pannanum.", "careful-ah read panni reply panren."
                ],
                [
                    "Neenga enna ninaikireenga nu sollunga.", "Konjam free aana udane call pannu.",
                    "Romba thanks for your help da.", "Appuram pesalam, take care pa.",
                    "Kandippa seekiram mudikka paakuren.", "Idhula ethavathu doubt iruntha kelunga.",
                    "Team-kku updates seekiram share pannidren.", "Nalaikku morning standup-la discuss pannuvom."
                ]
            ],
            "template": "{0} {1} {2} {3}"
        },
        # 12. TANGLISH_TAMIL_SCRIPT_TECH
        {
            "name": "TANGLISH_TAMIL_SCRIPT_TECH",
            "op_lang": "TANGLISH", "mat_lang": "TAMIL", "subtype": "TAMIL_SCRIPT_ENGLISH_TECHNICAL",
            "slots": [
                [
                    "நமது microservice architecture-ல்", "இந்த Kubernetes cluster deployment-ல்",
                    "நமது backend PostgreSQL database-ல்", "இந்த React frontend application-ல்",
                    "நமது CI/CD pipeline automation-ல்", "இந்த Redis cache invalidation logic-ல்",
                    "நமது cloud security policy-ல்", "இந்த distributed tracing system-ல்",
                    "நமது Kafka message broker consumer group-ல்", "இந்த Docker containerization workflow-ல்",
                    "நமது Elasticsearch log indexing cluster-ல்", "இந்த GraphQL API schema federation-ல்"
                ],
                [
                    "API gateway மூலமாக load balancing சீராக நடைபெறுகிறது",
                    "container crash loop backoff பிழையை உடனடியாக debug செய்ய வேண்டும்",
                    "indexing மற்றும் query optimization செய்து latency-ஐ குறைக்க வேண்டும்",
                    "state management மற்றும் re-rendering செயல்திறனை optimize செய்ய வேண்டும்",
                    "unit test suites மற்றும் integration checks pass ஆவதை verify செய்ய வேண்டும்",
                    "memory overhead மற்றும் cache miss விகிதத்தை கண்காணிக்க வேண்டும்",
                    "firewall rules மற்றும் IAM role permissions-ஐ audit செய்ய வேண்டும்",
                    "latency spikes மற்றும் error rate metrics-ஐ dashboard-ல் பார்க்க வேண்டும்",
                    "partition lag மற்றும் throughput metrics-ஐ analyze செய்ய வேண்டும்",
                    "multi-stage build பயன்படுத்தி image size-ஐ குறைக்க வேண்டும்",
                    "search query performance மற்றும் heap memory usage-ஐ கண்காணிக்க வேண்டும்",
                    "resolver latency மற்றும் schema breaking changes-ஐ test செய்ய வேண்டும்"
                ],
                [
                    "என்பது மிக முக்கியமான தொழில்நுட்பத் தேவையாகும்.",
                    "என்பதை DevOps குழுவினர் உறுதிப்படுத்த வேண்டும்.",
                    "என்பதை அடுத்த sprint வெளியீட்டில் நாம் சேர்க்க வேண்டும்.",
                    "என்பதால் production stability பன்மடங்கு உயரும்.",
                    "என்பதை engineering leads அனைவரும் ஒப்புக்கொண்டுள்ளனர்.",
                    "என்பதால் system reliability தொடர்ந்து பாதுகாக்கப்படும்."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 13. TANGLISH_ENGLISH_TAMIL_PARTICLES
        {
            "name": "TANGLISH_ENGLISH_TAMIL_PARTICLES",
            "op_lang": "TANGLISH", "mat_lang": "ENGLISH", "subtype": "ENGLISH_WITH_TAMIL_PARTICLES",
            "slots": [
                [
                    "Aiyo, look at the server logs,", "Machan, can you review this code quickly,",
                    "Dei, do not push to production directly,", "Seri, let us start the migration now,",
                    "Aiyo, the database connection timed out again,", "Machan, the test cases are failing,",
                    "Dei, check the memory utilization on node three,", "Seri pa, we will deploy the hotfix today,",
                    "Aiyo, the background worker crashed suddenly,", "Machan, the staging environment is down,",
                    "Dei, do not forget to take database backup,", "Seri, let us discuss this in the standup,"
                ],
                [
                    "because the CPU utilization hit ninety percent da.",
                    "so that we can get this pull request approved today pa.",
                    "without running the automated regression suite first da.",
                    "and monitor the application metrics continuously pa.",
                    "even after we restarted the container cluster da.",
                    "on the newly introduced authorization module pa.",
                    "before the background worker throws an out of memory error da.",
                    "as soon as the QA team gives final sign-off pa.",
                    "due to an unexpected heap allocation spike da.",
                    "before the client demo starts this afternoon pa.",
                    "otherwise data recovery will be very difficult da.",
                    "and get approval from our technical architect pa."
                ],
                [
                    "What do you suggest we do now da?", "Please take a look at it right away pa.",
                    "Let us not take any unnecessary risks da.", "Everything should go smoothly this time pa.",
                    "We need to find the root cause urgently da.", "Keep me posted once it is resolved pa.",
                    "Let us ping the infrastructure team right now da.", "I will wait for your confirmation message pa."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 14. TANGLISH_INTRA_SENTENTIAL
        {
            "name": "TANGLISH_INTRA_SENTENTIAL",
            "op_lang": "TANGLISH", "mat_lang": "TANGLISH", "subtype": "INTRA_SENTENTIAL_CODE_SWITCH",
            "slots": [
                [
                    "ஸ்பிரிண்ட் பிளானிங் முடிந்ததும்,", "இந்த அல்காரிதம் மிகவும் மெதுவாக செயல்படுவதால்,",
                    "கிளையன்ட் தேவைகள் மாறினாலும் கூட,", "டேட்டாபேஸ் வினவல் உகப்பாக்கம் செய்த பிறகு,",
                    "கோட் ரிவ்யூ கருத்துக்கள் அனைத்தையும் சரிசெய்து,", "புதிய அம்சங்களின் வெளியீடு தயாரானதும்,",
                    "பின்னணி சேவையக உள்கட்டமைப்பை மாற்றியமைக்கும் போது,", "தயாரிப்பு சூழலில் ஏற்பட்ட சிக்கலை தீர்த்த பின்,",
                    "ஆவணங்கள் அனைத்தையும் முழுமையாக சரிபார்த்துவிட்டு,", "முக்கியமான பாதுகாப்பு சோதனைகள் முடிந்தவுடன்,"
                ],
                [
                    "we will immediately deploy the microservices to the staging cluster",
                    "we decided to benchmark the cache lookups using in-memory queues",
                    "our engineering team successfully delivered the core milestone on time",
                    "we observed a massive fifty percent reduction in latency metrics",
                    "the team approved the pull request and merged it into main branch",
                    "the QA lead will trigger automated smoke tests across all test suites",
                    "we must preserve backward compatibility for all existing public APIs",
                    "the engineering director conducted a comprehensive blameless post-mortem",
                    "we will publish the technical documentation to the developer portal",
                    "all developers can safely merge their pending feature branches"
                ],
                [
                    "என்று குழுவினர் அனைவருக்கும் தெரிவிக்கப்பட்டது.",
                    "என்பதால் எதிர்கால பராமரிப்பு மிகவும் எளிதாகிவிடும்.",
                    "என்பதை உறுதி செய்ய நாம் தொடர்ந்து கண்காணிக்க வேண்டும்.",
                    "என்பதால் பயனர்களுக்கு தடையற்ற சேவை கிடைக்கும்.",
                    "என்று தொழில்நுட்பத் தலைமை அதிகாரி குறிப்பிட்டுள்ளார்.",
                    "என்பதை அடுத்த கூட்டத்தில் விரிவாக விவாதிக்கலாம்."
                ]
            ],
            "template": "{0} {1} {2}"
        },
        # 15. TANGLISH_INFORMAL
        {
            "name": "TANGLISH_INFORMAL",
            "op_lang": "TANGLISH", "mat_lang": "TANGLISH", "subtype": "ROMANIZED_TAMIL",
            "slots": [
                [
                    "Enna machan,", "Dei nanba,", "Hi bro,", "Machi,", "Aiyo friend,",
                    "Hello thambi,", "Enna da,", "Mappillai,", "Dei machi,", "Hi thozha,"
                ],
                [
                    "weekend enna plan vachirukka?", "innaiku evening cafeteria-la tea kudikkalama?",
                    "nethu release aana puthu movie paathiya?", "office work romba heavy-ah irunthuchu da,",
                    "lunch-kku enna saapida pora?", "gym-kku innaiku timing enna vachirukka?",
                    "intha trip plan-ah confirm pannitiya?", "cricket match score paathiya da,",
                    "puthu bike delivery vanthirucha?", "intha song ketriya romba super-ah irukku,"
                ],
                [
                    "romba stress-ah irukku, konjam chill pannanum.", "ticket book pannitiya illa innum decide pannala-ya?",
                    "super entertaining-ah irunthuchu nu sonnanga.", "seekiram mudichitu kelambalam nu paakuren.",
                    "hotel-la order pannalama illa cafeteria polama?", "innaiku workout skip panna koodathu machan.",
                    "friends ellam waiting, seekiram reply pannu.", "kadasi over-la match sema thrilling-ah pochu.",
                    "long ride poga sema excitement-ah irukku.", "playlist-la add panni loop-la kettu paaru."
                ],
                [
                    "Call pannu pesalam.", "Message paatha udane ping pannu da.",
                    "Appuram kandippa meet pannuvom.", "Take care, enjoy the day da.",
                    "Evening seekiram varen, waiting pa.", "Kandippa innaiku plan drop pannidatha."
                ]
            ],
            "template": "{0} {1} {2} {3}"
        },
        # 16. TANGLISH_FORMAL_TECH
        {
            "name": "TANGLISH_FORMAL_TECH",
            "op_lang": "TANGLISH", "mat_lang": "TANGLISH", "subtype": "INTRA_SENTENTIAL_CODE_SWITCH",
            "slots": [
                [
                    "In today's architecture review meeting,", "Regarding the production cluster upgrade,",
                    "During the cross-functional sprint planning session,", "In our cloud infrastructure cost optimization review,",
                    "Regarding the security compliance audit checklist,", "While analyzing the recent latency spike in payment gateway,",
                    "During the quarterly disaster recovery simulation,", "In the backend API deprecation review,"
                ],
                [
                    "intha microservice scalability issue-va address panna",
                    "database query indexing strategy-ஐ restructure panni",
                    "container autoscaling policy-ஐ properly configure panni",
                    "asynchronous message broker throughput-ஐ enhance panna",
                    "caching layer invalidation logic-ஐ optimize panni",
                    "system logging and monitoring telemetry-ஐ streamline panni",
                    "network security firewall rules-ஐ audit panni",
                    "distributed data replication lag-ஐ minimize panna"
                ],
                [
                    "we must deploy distributed tracing across all interconnected components.",
                    "the engineering team will conduct rigorous end-to-end performance benchmarking.",
                    "we will publish an updated architecture decision record before next release.",
                    "all developers should follow strict idempotent design patterns in API contracts.",
                    "we need to ensure zero downtime during database schema migration.",
                    "automated alert thresholds must trigger immediate alerts for on-call engineers.",
                    "we should restrict direct database access to authenticated service accounts.",
                    "the lead architect will present the findings to the technology council."
                ],
                [
                    "Idhoda progress-ஐ daily standup-la track pannuvom.",
                    "Intha approach system reliability-ஐ drastically improve pannum.",
                    "Team leads ellarum intha specification-ஐ review panni sign-off tharanum.",
                    "Documentation-ஐ internal engineering wiki-la update panni vachirukkom.",
                    "All stakeholder approvals must be documented before final rollout.",
                    "Production deployment date will be confirmed by tomorrow morning."
                ]
            ],
            "template": "{0} {1}, {2} {3}"
        }
    ]

    for cat_idx, cat in enumerate(categories_spec):
        cat_rng = random.Random(RANDOM_SEED + cat_idx)
        slots = cat["slots"]
        tmpl = cat["template"]

        # Build all combinations
        import itertools
        all_combos = list(itertools.product(*slots))
        cat_rng.shuffle(all_combos)
        print(f"Category {cat['name']}: {len(all_combos)} total combinatorial candidates available.")

        cat_records = 0
        for combo in all_combos:
            txt_cand = unicodedata.normalize("NFC", tmpl.format(*combo).strip())
            if txt_cand not in global_seen_texts and txt_cand not in orig_texts:
                global_seen_texts.add(txt_cand)
                records.append({
                    "category": cat["name"],
                    "operational_language": cat["op_lang"],
                    "matrix_language": cat["mat_lang"],
                    "tanglish_subtype": cat["subtype"],
                    "text": txt_cand
                })
                cat_records += 1
                if cat_records == 200:
                    break

        if cat_records < 200:
            raise RuntimeError(f"Could not generate 200 unique records for category {cat['name']}! Got {cat_records}")

    print(f"Total records successfully generated: {len(records)}")

    # Assign IDs, script_forms, counts, hashes
    for idx, r in enumerate(records):
        doc_id = f"SYNTH-EVAL-{idx + 1:04d}"
        r["doc_id"] = doc_id
        r["script_form"] = detect_script_form(r["text"])
        r["word_count"] = len(r["text"].split())
        r["char_count"] = len(r["text"])
        r["sha256"] = hashlib.sha256(r["text"].encode("utf-8")).hexdigest()
        r["generator_version"] = GENERATOR_VERSION
        r["random_seed"] = RANDOM_SEED

    return records, orig_texts

if __name__ == "__main__":
    records, orig_texts = build_full_corpus()
    unique_hashes = set(r["sha256"] for r in records)
    print(f"Total records: {len(records)}, Unique SHA256: {len(unique_hashes)}")
    assert len(records) == 3200
    assert len(unique_hashes) == 3200

    # Contamination check: exact match
    new_texts = set(r["text"] for r in records)
    overlap = new_texts.intersection(orig_texts)
    print(f"Contamination overlap with 399 original records: {len(overlap)}")
    assert len(overlap) == 0

    cat_counts = Counter(r["category"] for r in records)
    lang_counts = Counter(r["operational_language"] for r in records)
    script_counts = Counter(r["script_form"] for r in records)
    subtype_counts = Counter(r["tanglish_subtype"] for r in records)

    print("\nCategory counts:")
    for c, n in sorted(cat_counts.items()):
        print(f"  {c:35s}: {n}")

    print("\nOperational language counts:")
    for l, n in sorted(lang_counts.items()):
        print(f"  {l:15s}: {n}")

    print("\nScript form counts:")
    for s, n in sorted(script_counts.items()):
        print(f"  {s:15s}: {n}")

    print("\nTanglish subtype counts:")
    for st, n in sorted(subtype_counts.items()):
        print(f"  {st:30s}: {n}")
