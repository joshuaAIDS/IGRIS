"""
scratch/test_corpus_generator.py

Draft generator for 3,200 independent synthetic evaluation records
covering 16 semantic categories across Tamil, English, and Tanglish.
"""

import hashlib
import json
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

# Seed & version
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

def build_corpus():
    rng = random.Random(RANDOM_SEED)
    records = []

    # 1. TAMIL_CONVERSATIONAL
    t_conv_openers = [
        "வணக்கம் நண்பரே,", "அன்பான நண்பா,", "வணக்கம் ஐயா,", "வணக்கம் தோழரே,",
        "காலை வணக்கம்,", "மாலை வணக்கம் நண்பா,", "வணக்கம் அண்ணா,", "வணக்கம் தம்பி,"
    ]
    t_conv_subjects = [
        "நீங்கள் இன்று காலை அலுவலகத்திற்கு", "உங்கள் குடும்பத்தினர் அனைவரும்",
        "நாம் அனைவரும் அடுத்த வாரம்", "நீங்கள் கேட்ட அந்த புதிய புத்தகம்",
        "நேற்று நடைபெற்ற கலந்துரையாடல் பற்றி", "உங்கள் புதிய திட்டப் பணிகள்",
        "மாலை நேரத்தில் நடைப்பயிற்சி செல்ல", "இந்த வார இறுதியில் ஒரு பயணம் மேற்கொள்ள"
    ]
    t_conv_actions = [
        "எத்தனை மணிக்கு வர திட்டமிட்டுள்ளீர்கள்?", "நலமாக இருக்கிறார்களா என்று அறிந்துகொள்ள விரும்புகிறேன்.",
        "ஒன்றாக இணைந்து தேநீர் அருந்த செல்லலாமா?", "உங்களுக்கு மிகவும் பயனுள்ளதாக அமைந்ததா?",
        "மேலும் சில விவரங்களை பகிர்ந்து கொள்ள முடியுமா?", "எந்த அளவிற்கு முன்னேற்றம் கண்டுள்ளது?",
        "வானிலை மிகவும் இதமாக உள்ளது.", "நாம் அனைவரும் ஒன்றாக திட்டமிடலாம்."
    ]
    t_conv_closers = [
        "உங்கள் பதிலை ஆவலுடன் எதிர்பார்க்கிறேன்.", "நேரம் கிடைக்கும்போது அழையுங்கள்.",
        "விரைவில் மீண்டும் சந்திப்போம்.", "நன்றி, நல்ல நாளாக அமையட்டும்.",
        "பார்த்து கவனமாக செல்லுங்கள்.", "தங்கள் வருகைக்கு மிக்க நன்றி."
    ]

    for i in range(200):
        op = rng.choice(t_conv_openers)
        sub = rng.choice(t_conv_subjects)
        act = rng.choice(t_conv_actions)
        clo = rng.choice(t_conv_closers)
        txt = f"{op} {sub} {act} {clo}"
        records.append({
            "category": "TAMIL_CONVERSATIONAL",
            "operational_language": "TAMIL",
            "matrix_language": "TAMIL",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 2. TAMIL_FORMAL
    t_form_subjects = [
        "தமிழ்நாடு அரசின் உயர்கல்வித் துறை", "சென்னை மாநகராட்சி நிர்வாகம்",
        "மாவட்ட ஆட்சியர் அலுவலக செய்திக்குறிப்பு", "மாநில திட்டக் குழுவின் புதிய அறிக்கை",
        "பல்கலைக்கழக மானியக் குழுவின் வழிகாட்டுதல்கள்", "பொது சுகாதாரத் துறையின் அறிவிப்பு",
        "தொழிலாளர் நல வாரியத்தின் புதிய திட்டம்", "சுற்றுச்சூழல் பாதுகாப்பு ஆணையத்தின் உத்தரவு"
    ]
    t_form_clauses = [
        "அனைத்து அரசு மற்றும் தனியார் நிறுவனங்களுக்கும் சுற்றறிக்கை அனுப்பியுள்ளது.",
        "பொதுமக்களின் நலன் கருதி சிறப்பு விழிப்புணர்வு முகாம்களை ஏற்பாடு செய்துள்ளது.",
        "வருடாந்திர நிதி ஒதுக்கீடு குறித்த முழுமையான ஆய்வறிக்கையை வெளியிட்டுள்ளது.",
        "புதிய ஒழுங்குமுறை விதிகளை உடனடியாக நடைமுறைப்படுத்த உத்தரவிட்டுள்ளது.",
        "கிராமப்புற மாணவர்களின் கல்வித் தரத்தை மேம்படுத்த புதிய செயல்திட்டங்களை வகுத்துள்ளது.",
        "நிலத்தடி நீர்மட்டத்தை உயர்த்த மழைநீர் சேகரிப்பை கட்டாயமாக்கியுள்ளது."
    ]
    t_form_impacts = [
        "இதன் மூலம் பல்லாயிரக்கணக்கான மக்கள் நேரடியாகப் பயனடைவார்கள் என்று எதிர்பார்க்கப்படுகிறது.",
        "இத்திட்டம் மாநிலத்தின் நிலையான வளர்ச்சிக்கு வலுவான அடித்தளமாக அமையும்.",
        "அனைத்து அதிகாரிகளும் விதிமுறைகளை முறையாகப் பின்பற்றுமாறு அறிவுறுத்தப்படுகிறார்கள்.",
        "பொதுமக்கள் இந்த வாய்ப்பினை முழுமையாகப் பயன்படுத்திக் கொள்ள வேண்டும் என கேட்டுக் கொள்ளப்படுகிறார்கள்."
    ]

    for i in range(200):
        sub = rng.choice(t_form_subjects)
        cla = rng.choice(t_form_clauses)
        imp = rng.choice(t_form_impacts)
        txt = f"{sub} {cla} {imp}"
        records.append({
            "category": "TAMIL_FORMAL",
            "operational_language": "TAMIL",
            "matrix_language": "TAMIL",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 3. TAMIL_EDUCATIONAL
    t_edu_topics = [
        "ஒளிச்சேர்க்கை என்பது", "பூமியின் வளிமண்டலத்தில் காணப்படும் நைட்ரஜன் வாயு",
        "மனித உடலில் உள்ள இரத்த ஓட்ட மண்டலம்", "நியூட்டனின் இரண்டாம் இயக்க விதி",
        "சூரியக் குடும்பத்தில் உள்ள கோள்களின் சுழற்சி முறை", "நீரின் சுழற்சி மற்றும் ஆவியாதல் நிகழ்வு",
        "டிஎன்ஏ மூலக்கூறின் இரட்டைச் சுருள் கட்டமைப்பு", "பண்டைய சோழப் பேரரசின் நீர்ப்பாசனக் கட்டமைப்பு"
    ]
    t_edu_expls = [
        "தாவரங்கள் சூரிய ஒளியைப் பயன்படுத்தி தமக்குத் தேவையான உணவைத் தயாரிக்கும் அடிப்படை உயிரியல் செயல்பாடாகும்.",
        "சுமார் எழுபத்தெட்டு விழுக்காடு அளவில் நிறைந்து பூமியின் வெப்பநிலையை சீராகப் பராமரிக்க உதவுகிறது.",
        "இதயம், இரத்தக் குழாய்கள் மற்றும் இரத்தம் ஆகியவற்றின் மூலம் உடலின் அனைத்து செல்களுக்கும் ஊட்டச்சத்தை வழங்குகிறது.",
        "பொருளின் மீது செயல்படும் விசை அதன் நிறை மற்றும் முடுக்கத்தின் பெருக்கற்பலனுக்கு சமம் என்பதை விளக்குகிறது.",
        "ஈர்ப்பு விசையின் காரணமாக சூரியனை மையமாகக் கொண்டு நீள்வட்டப் பாதையில் இயங்குகிறது.",
        "கடல் நீரானது ஆவியாகி மேகங்களாக மாறி மீண்டும் மழையாகப் பொழியும் தொடர்ச்சியான இயற்கை நிகழ்வாகும்.",
        "மரபியல் தகவல்களை தலைமுறை தலைமுறையாகக் கடத்தும் முதன்மையான காரணியாக செயல்படுகிறது.",
        "விவசாய உற்பத்தியை பெருக்க ஏரிகள், கால்வாய்கள் மற்றும் அணைகளை அமைத்து வரலாற்று சாதனை படைத்தது."
    ]
    t_edu_concls = [
        "இக்கருத்து அறிவியல் பாடத்திட்டத்தில் மிக முக்கியமான அடிப்படைப் பகுதியாகக் கருதப்படுகிறது.",
        "இதனைப் புரிந்து கொள்வது உயர்நிலை அறிவியல் ஆய்வுகளுக்கு அடித்தளமாக அமைகிறது.",
        "இயற்கையின் விதிகளையும் சமநிலையையும் உணர்ந்து கொள்ள இது ஒரு சிறந்த சான்றாகும்.",
        "மாணவர்கள் இத்தகைய அறிவியல் உண்மைகளை செய்முறை வழியே கற்பது கூடுதல் தெளிவை அளிக்கும்."
    ]

    for i in range(200):
        top = rng.choice(t_edu_topics)
        exp = rng.choice(t_edu_expls)
        con = rng.choice(t_edu_concls)
        txt = f"{top} {exp} {con}"
        records.append({
            "category": "TAMIL_EDUCATIONAL",
            "operational_language": "TAMIL",
            "matrix_language": "TAMIL",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 4. TAMIL_TECHNICAL
    t_tech_subjects = [
        "கணினி அமைப்புகளில் நினைவக மேலாண்மை", "நவீன வலைப்பின்னல் பாதுகாப்பு நெறிமுறைகள்",
        "தரவுத்தள அட்டவணைகளின் சுட்டெண் வடிவமைப்பு", "வரிசை மற்றும் அடுக்கு போன்ற அடிப்படைத் தரவுக் கட்டமைப்புகள்",
        "செயற்கை நுண்ணறிவு மாதிரிகளின் பயிற்சி வழிமுறைகள்", "நிகழ்நேர செயலாக்க அமைப்புகளில் தாமதத்தைக் குறைக்கும் நுட்பங்கள்",
        "பகிர்ந்தளிக்கப்பட்ட கணினி அமைப்புகளில் தரவு ஒத்திசைவு", "இயக்க முறைமையின் மையக் கருவான கர்னல் மேலாண்மை"
    ]
    t_tech_details = [
        "தேவையற்ற நினைவகக் கசிவுகளைத் தடுத்து மென்பொருளின் வேகத்தை பன்மடங்கு அதிகரிக்க உதவுகிறது.",
        "அங்கீகரிக்கப்படாத ஊடுருவல்களைத் தடுத்து ரகசியத் தரவுகளின் ஒருமைப்பாட்டை உறுதி செய்கிறது.",
        "தேடல் வினவல்களின் வேகத்தை உயர்த்தி வட்டு வாசிப்பு நேரத்தை கணிசமாகக் குறைக்கிறது.",
        "அல்காரிதம்களின் நேரச் சிக்கல் மற்றும் இடச் சிக்கலை திறம்பட நிர்வகிக்க வழிவகுக்கிறது.",
        "பெரிய அளவிலான தரவுத்தொகுப்புகளைப் பகுப்பாய்வு செய்து துல்லியமான கணிப்புகளை வழங்குகிறது.",
        "செயல்திறன் இடையூறுகளைக் கண்டறிந்து வன்பொருள் வளங்களை உகந்த முறையில் பயன்படுத்துகிறது.",
        "வலையமைப்புத் தடங்கல்கள் ஏற்பட்டாலும் கணினி சேவைகள் தடையின்றி இயங்குவதை உறுதி செய்கிறது."
    ]
    t_tech_concls = [
        "இது பொறியியல் வடிவமைப்பில் மிகச் சிறந்த நடைமுறையாக பரிந்துரைக்கப்படுகிறது.",
        "மென்பொருள் பொறியாளர்கள் இந்த கொள்கைகளைத் துல்லியமாகக் கடைப்பிடிப்பது அவசியமாகும்.",
        "உயர் செயல்திறன் கொண்ட உற்பத்தி அமைப்புகளில் இக்கட்டமைப்பு அத்தியாவசியமானது.",
        "கணினி அறிவியலின் நவீன வளர்ச்சியில் இது ஒரு மைல்கல்லாகக் கருதப்படுகிறது."
    ]

    for i in range(200):
        sub = rng.choice(t_tech_subjects)
        det = rng.choice(t_tech_details)
        con = rng.choice(t_tech_concls)
        txt = f"{sub} {det} {con}"
        records.append({
            "category": "TAMIL_TECHNICAL",
            "operational_language": "TAMIL",
            "matrix_language": "TAMIL",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 5. TAMIL_LONGFORM (multi-sentence paragraphs)
    t_long_intros = [
        "தமிழ்ச் செவ்வியல் இலக்கியங்களும் நவீன அறிவியல் சிந்தனைகளும் மனித குலத்திற்கு ஆழமான வழிகாட்டலை வழங்குகின்றன.",
        "வரலாற்று ரீதியாக தமிழர்களின் கடல்சார் வாணிபமும் நகரக் கட்டமைப்பும் உலக அளவில் தனித்துவமான பெருமை பெற்றவை.",
        "இயற்கையோடு இயைந்த வாழ்வியலும் சுற்றுச்சூழல் சமநிலையும் நமது தொன்மையான மரபில் ஆழமாக வேரூன்றியுள்ளன.",
        "அறிவியல் மற்றும் தொழில்நுட்ப வளர்ச்சியானது தாய்மொழி வழிக் கல்வியின் மூலம் சமூகத்தின் அனைத்துத் தளங்களையும் சென்றடைய வேண்டும்."
    ]
    t_long_bodies = [
        "சங்க இலக்கியங்கள் இயற்கையை வெறும் பின்னணியாகப் பார்க்காமல், மனித உணர்வுகளோடு இணைத்துப் பாடியுள்ளன. காடுகளையும் ஆறுகளையும் பாதுகாப்பது சமூகத்தின் கடமை என்று அவை வலியுறுத்துகின்றன. அத்தகைய விழிப்புணர்வு இன்றைய காலநிலை மாற்ற சூழலில் மேலும் பொருத்தமுடையதாகிறது.",
        "பூம்புகார், கொற்கை போன்ற துறைமுகங்கள் வழியே ரோம், எகிப்து மற்றும் தென்கிழக்கு ஆசிய நாடுகளோடு விரிவான வர்த்தகத் தொடர்புகள் நிலவின. ஏற்றுமதி செய்யப்பட்ட மிளகு, முத்து மற்றும் பருத்தி ஆடைகள் உலகச் சந்தைகளில் மிகுந்த மதிப்பைப் பெற்றிருந்தன. கல்வெட்டுகள் மற்றும் நாணயச் சான்றுகள் இந்த வளமான வணிக வரலாற்றை உறுதிப்படுத்துகின்றன.",
        "கல்லணை போன்ற பிரம்மாண்டமான நீர் மேலாண்மைக் கட்டமைப்புகள் இரண்டாயிரம் ஆண்டுகளுக்கு முன்பே தமிழர்களின் பொறியியல் அறிவிற்கு சான்றாக திகழ்கின்றன. ஆற்று நீரை சமதளத்தில் திருப்பி விவசாயத்திற்குப் பயன்படுத்திய விதம் வியப்பிற்குரியது. இது போன்ற நுட்பங்களை தற்கால நீரியல் ஆய்வுகளிலும் ஆய்வாளர்கள் பெருமையுடன் குறிப்பிடுகின்றனர்.",
        "நவீன கணினித் தொழில்நுட்பத்தில் தமிழ் மொழியை முதன்மைப்படுத்தும் மென்பொருட்களும் உள்ளீட்டுக் கருவிகளும் தொடர்ந்து உருவாக்கப்பட்டு வருகின்றன. இதன் வாயிலாக அறிவுப் பரவலாக்கம் விரைவுபடுத்தப்பட்டு கிராமப்புற மாணவர்களும் தொழில்நுட்பப் பலன்களை எளிதில் பெற முடிகிறது. புதிய தலைமுறை ஆய்வாளர்கள் இந்த மொழியியல் முன்னேற்றத்திற்கு பெரும் பங்களிப்பை வழங்கி வருகின்றனர்."
    ]
    t_long_concls = [
        "எனவே, நமது தொன்மையை நினைவுகூர்வதுடன் எதிர்காலத் தேவைகளுக்கான புத்தாக்கங்களையும் உருவாக்குவதே நமது முதன்மையான கடமையாகும்.",
        "இத்தகைய வரலாற்றுப் பாடங்கள் எதிர்கால சந்ததியினருக்கு தன்னம்பிக்கையையும் தெளிவான வழிகாட்டலையும் தொடர்ந்து வழங்கும் என்பதில் ஐயமில்லை.",
        "பாரம்பரிய அறிவையும் சமகால அறிவியல் பார்வையையும் இணைத்து முன்னேறுவதே ஒரு சமூகத்தின் முழுமையான வளர்ச்சிக்கு வழிகோலும்."
    ]

    for i in range(200):
        intro = rng.choice(t_long_intros)
        body = rng.choice(t_long_bodies)
        concl = rng.choice(t_long_concls)
        txt = f"{intro} {body} {concl}"
        records.append({
            "category": "TAMIL_LONGFORM",
            "operational_language": "TAMIL",
            "matrix_language": "TAMIL",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    print(f"Generated Tamil records: {len(records)}")

    # 6. ENGLISH_CONVERSATIONAL
    e_conv_openers = [
        "Hello team,", "Good morning everyone,", "Hi Sarah,", "Hey Alex,",
        "Good afternoon colleagues,", "Hi everyone,", "Hello David,", "Hi team,"
    ]
    e_conv_topics = [
        "could we quickly sync up on the sprint progress", "let us review the feedback received from the customer testing session",
        "please make sure to submit your timesheets and project updates", "I wanted to check if the staging deployment completed successfully",
        "can we reschedule our afternoon architectural alignment discussion", "let us make sure everyone has access to the new testing environment",
        "do we have all the required assets for tomorrow's client presentation", "I have summarized the core action items from our morning standup"
    ]
    e_conv_actions = [
        "before we jump into the wider executive review.", "so that we can address any blocking questions right away.",
        "as early as possible to prevent payroll cutoff delays.", "and whether all integration tests passed without regressions.",
        "to give everyone enough time to prepare their proposals.", "before we start the scheduled end-to-end regression run.",
        "so we can run through the slides one final time.", "and shared them on the project workspace channel."
    ]
    e_conv_closers = [
        "Looking forward to catching up soon.", "Let me know if you need any assistance.",
        "Thanks for your continuous support and great work.", "Feel free to ping me if anything looks urgent.",
        "Have a wonderful and productive day ahead.", "Best regards to everyone."
    ]

    for i in range(200):
        op = rng.choice(e_conv_openers)
        top = rng.choice(e_conv_topics)
        act = rng.choice(e_conv_actions)
        clo = rng.choice(e_conv_closers)
        txt = f"{op} {top} {act} {clo}"
        records.append({
            "category": "ENGLISH_CONVERSATIONAL",
            "operational_language": "ENGLISH",
            "matrix_language": "ENGLISH",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 7. ENGLISH_TECHNICAL_DOCS
    e_doc_subjects = [
        "The distributed identity service", "This microservice API gateway",
        "The event-driven messaging layer", "Our relational database connection pool",
        "The telemetry and metrics ingestion pipeline", "The containerized cluster orchestrator",
        "The object storage replication subsystem", "The edge proxy caching mechanism"
    ]
    e_doc_behaviors = [
        "issues cryptographically signed JWT tokens with a fifteen-minute expiration window",
        "routes incoming HTTP requests based on path prefixes and authenticated tenant headers",
        "guarantees at-least-once message delivery using distributed consumer groups and offset commits",
        "dynamically maintains healthy database connections using exponential backoff and circuit breaking",
        "aggregates high-cardinality time series metrics and streams structured audit logs",
        "monitors node health and automatically schedules pods across isolated availability zones",
        "asynchronously synchronizes blob objects across multi-region geographic storage buckets",
        "caches static asset responses at point-of-presence servers to minimize origin server load"
    ]
    e_doc_clauses = [
        "ensuring strict compliance with enterprise security and audit standards.",
        "thereby preventing cascading failures during sudden upstream network partitions.",
        "which significantly enhances horizontal scalability under heavy concurrent load.",
        "providing sub-millisecond p99 response times for mission-critical operations.",
        "while maintaining deterministic idempotent processing for all write mutations.",
        "reducing operational maintenance overhead across heterogeneous cloud environments."
    ]

    for i in range(200):
        sub = rng.choice(e_doc_subjects)
        beh = rng.choice(e_doc_behaviors)
        cla = rng.choice(e_doc_clauses)
        txt = f"{sub} {beh}, {cla}"
        records.append({
            "category": "ENGLISH_TECHNICAL_DOCS",
            "operational_language": "ENGLISH",
            "matrix_language": "ENGLISH",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 8. ENGLISH_PROGRAMMING
    e_prog_subjects = [
        "In modern asynchronous programming, using non-blocking primitives",
        "When implementing concurrent hash maps, lock striping techniques",
        "Recursive algorithms operating on deeply nested hierarchical trees",
        "Utilizing immutable data structures in multi-threaded workflows",
        "Memory profiling tools that track heap allocations and garbage collection cycles",
        "Dependency injection patterns applied to modular software architectures",
        "Database transaction isolation levels such as snapshot isolation",
        "Optimizing matrix multiplication kernels using vectorized SIMD instructions"
    ]
    e_prog_details = [
        "prevent thread starvation and maximize CPU core utilization during heavy I/O operations.",
        "substantially reduce synchronization contention among competing worker threads.",
        "require logarithmic call stack depth to avoid catastrophic stack overflow exceptions.",
        "eliminate data races by rendering shared state completely read-only after initialization.",
        "help developers identify persistent memory leaks and uncollected object references.",
        "decouple interface contracts from concrete implementations, facilitating comprehensive unit testing.",
        "prevent phantom reads and non-repeatable reads without incurring pervasive table-level locks.",
        "achieve near-theoretical peak memory bandwidth and computational throughput."
    ]
    e_prog_concls = [
        "This principle is fundamental to designing reliable high-throughput software systems.",
        "Engineers should rigorously benchmark these implementations under production-like traffic profiles.",
        "Adhering to this design pattern simplifies code readability and ongoing maintainability.",
        "Careful profiling ensures optimal cache locality and predictable execution latencies."
    ]

    for i in range(200):
        sub = rng.choice(e_prog_subjects)
        det = rng.choice(e_prog_details)
        con = rng.choice(e_prog_concls)
        txt = f"{sub} {det} {con}"
        records.append({
            "category": "ENGLISH_PROGRAMMING",
            "operational_language": "ENGLISH",
            "matrix_language": "ENGLISH",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 9. ENGLISH_EDUCATIONAL
    e_edu_subjects = [
        "Photosynthesis in green plants", "The theory of plate tectonics",
        "Cellular respiration in aerobic organisms", "The macroeconomic concept of inflation",
        "Newton's universal law of gravitation", "The structure of the human central nervous system",
        "The historical impact of the printing press", "The fundamental principles of thermodynamics"
    ]
    e_edu_explanations = [
        "converts carbon dioxide and water into glucose and oxygen utilizing photon energy absorbed by chlorophyll pigments.",
        "explains how large continental and oceanic plates drift over the asthenosphere, causing earthquakes and volcanic activity.",
        "breaks down nutrient molecules inside the mitochondria to generate adenosine triphosphate for cellular metabolic work.",
        "describes the general sustained increase in price levels and the corresponding erosion of purchasing power within an economy.",
        "states that every particle attracts every other particle with a force proportional to the product of their masses.",
        "integrates sensory inputs and coordinates voluntary and involuntary physiological responses throughout the human body.",
        "democratized the widespread dissemination of scientific literature and accelerated literacy rates across Renaissance Europe.",
        "dictates the conservation of total energy and the inevitable increase in entropy within isolated physical systems."
    ]
    e_edu_summaries = [
        "Understanding this foundational concept is essential for advanced studies in the biological and physical sciences.",
        "This scientific model revolutionized our understanding of natural phenomena across centuries of inquiry.",
        "Educators emphasize this topic as a cornerstone of rigorous scientific and historical literacy.",
        "Empirical experiments continue to validate the mathematical and observational predictions of this theory."
    ]

    for i in range(200):
        sub = rng.choice(e_edu_subjects)
        exp = rng.choice(e_edu_explanations)
        summ = rng.choice(e_edu_summaries)
        txt = f"{sub} {exp} {summ}"
        records.append({
            "category": "ENGLISH_EDUCATIONAL",
            "operational_language": "ENGLISH",
            "matrix_language": "ENGLISH",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 10. ENGLISH_LONGFORM
    e_long_intros = [
        "The evolution of distributed computing architectures has fundamentally redefined enterprise software engineering practices.",
        "Modern database management systems must navigate subtle trade-offs between consistency, availability, and partition tolerance.",
        "The proliferation of artificial intelligence models has heightened the importance of algorithmic transparency and data provenance.",
        "Operating system kernels have progressively evolved to balance low-latency hardware abstraction with robust fault isolation."
    ]
    e_long_bodies = [
        "Historically, monolithic systems concentrated business logic and state persistence within tightly coupled deployment units. As user bases expanded into tens of millions, horizontal scaling constraints compelled the transition toward decentralized microservice networks. While microservices introduce operational complexity in service discovery and distributed tracing, they grant independent teams the autonomy to iterate and deploy features rapidly.",
        "Under the CAP theorem, distributed data stores cannot simultaneously achieve linearizable consistency and continuous availability during network splits. Systems opting for eventual consistency rely on vector clocks, gossip protocols, and conflict-free replicated data types to reconcile divergent state replicas. This architectural compromise delivers outstanding read throughput while sustaining acceptable resilience against transient network outages.",
        "Training large-scale deep learning models demands enormous computational throughput across specialized accelerator clusters. Effective pipeline parallelism and tensor sharding strategies are critical to prevent memory exhaustion and communication bottlenecks. Furthermore, establishing immutable audit trails for dataset acquisition and curation ensures that downstream model representations remain reproducible and verifiable.",
        "Contemporary microkernels and virtualized hypervisors compartmentalize untrusted device drivers outside privileged execution rings. By enforcing strict memory protection boundaries through hardware-assisted page table virtualization, modern platforms prevent compromised peripheral firmware from destabilizing the host system. Consequently, high-security computing environments achieve predictable performance without forfeiting defense-in-depth guarantees."
    ]
    e_long_concls = [
        "In conclusion, addressing these multifaceted challenges requires a harmonious blend of principled theoretical design and pragmatic systems engineering.",
        "Ultimately, software architects must carefully evaluate specific workload characteristics rather than adopting dogmatic technological solutions.",
        "Continuous empirical benchmarking and automated regression testing remain the most dependable safeguards for maintaining long-term system stability."
    ]

    for i in range(200):
        intro = rng.choice(e_long_intros)
        body = rng.choice(e_long_bodies)
        concl = rng.choice(e_long_concls)
        txt = f"{intro} {body} {concl}"
        records.append({
            "category": "ENGLISH_LONGFORM",
            "operational_language": "ENGLISH",
            "matrix_language": "ENGLISH",
            "tanglish_subtype": "NONE",
            "text": unicodedata.normalize("NFC", txt)
        })

    print(f"Generated English records: {len(records) - 1000} (Total: {len(records)})")

    # 11. TANGLISH_ROMANIZED (pure Latin script, Tamil phonology)
    tr_openers = [
        "Vanakkam nanba,", "Enna bro,", "Dei thambi,", "Vanakkam boss,",
        "Hello machan,", "Hi friend,", "Kekkutha bro,", "Vanakkam thozha,"
    ]
    tr_subjects = [
        "innaiku office-kku late-ah thaan poven", "nethu sonna project work-ah",
        "intha pudhiya feature development-ah", "antha API documentation file-ah",
        "namma team meeting discussion-la", "weekend trip porathukku tickets-ah",
        "intha code review changes-ah", "system performance issue-va"
    ]
    tr_verbs = [
        "kandippa innaiku evening kulla mudikanum.", "check panni status update anuppungada.",
        "seekiram mudichu testing team-kku kudukanum.", "email-la attach panni send pannirukken.",
        "ellorume kandippa participate pannanum.", "book panniyaacha nu therinjukalam.",
        "merge panna munnadi verify pannanum.", "analyze panni fix panna try panren."
    ]
    tr_closers = [
        "Neenga enna ninaikireenga nu sollunga.", "Konjam free aana udane call pannu.",
        "Romba thanks for your help da.", "Appuram pesalam, take care pa.",
        "Kandippa seekiram mudikka paakuren.", "Idhula ethavathu doubt iruntha kelunga."
    ]

    for i in range(200):
        op = rng.choice(tr_openers)
        sub = rng.choice(tr_subjects)
        v = rng.choice(tr_verbs)
        clo = rng.choice(tr_closers)
        txt = f"{op} {sub} {v} {clo}"
        records.append({
            "category": "TANGLISH_ROMANIZED",
            "operational_language": "TANGLISH",
            "matrix_language": "TANGLISH",
            "tanglish_subtype": "ROMANIZED_TAMIL",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 12. TANGLISH_TAMIL_SCRIPT_TECH (Tamil script matrix containing English technical terms in Latin or transliterated script)
    tt_subjects = [
        "நமது microservice architecture-ல்", "இந்த Kubernetes cluster deployment-ல்",
        "நமது backend PostgreSQL database-ல்", "இந்த React frontend application-ல்",
        "நமது CI/CD pipeline automation-ல்", "இந்த Redis cache invalidation logic-ல்",
        "நமது cloud security policy-ல்", "இந்த distributed tracing system-ல்"
    ]
    tt_actions = [
        "API gateway மூலமாக load balancing சீராக நடைபெறுகிறது",
        "container crash loop backoff பிழையை உடனடியாக debug செய்ய வேண்டும்",
        "indexing மற்றும் query optimization செய்து latency-ஐ குறைக்க வேண்டும்",
        "state management மற்றும் re-rendering செயல்திறனை optimize செய்ய வேண்டும்",
        "unit test suites மற்றும் integration checks pass ஆவதை verify செய்ய வேண்டும்",
        "memory overhead மற்றும் cache miss விகிதத்தை கண்காணிக்க வேண்டும்",
        "firewall rules மற்றும் IAM role permissions-ஐ audit செய்ய வேண்டும்",
        "latency spikes மற்றும் error rate metrics-ஐ dashboard-ல் பார்க்க வேண்டும்"
    ]
    tt_concls = [
        "என்பது மிக முக்கியமான தொழில்நுட்பத் தேவையாகும்.",
        "என்பதை DevOps குழுவினர் உறுதிப்படுத்த வேண்டும்.",
        "என்பதை அடுத்த sprint வெளியீட்டில் நாம் சேர்க்க வேண்டும்.",
        "என்பதால் production stability பன்மடங்கு உயரும்."
    ]

    for i in range(200):
        sub = rng.choice(tt_subjects)
        act = rng.choice(tt_actions)
        con = rng.choice(tt_concls)
        txt = f"{sub} {act} {con}"
        records.append({
            "category": "TANGLISH_TAMIL_SCRIPT_TECH",
            "operational_language": "TANGLISH",
            "matrix_language": "TAMIL",
            "tanglish_subtype": "TAMIL_SCRIPT_ENGLISH_TECHNICAL",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 13. TANGLISH_ENGLISH_TAMIL_PARTICLES (English sentence matrix containing colloquial Tamil discourse particles: da, pa, machan, aiyo, seri, dei)
    ep_openers = [
        "Aiyo, look at the server logs,", "Machan, can you review this code quickly,",
        "Dei, do not push to production directly,", "Seri, let us start the migration now,",
        "Aiyo, the database connection timed out again,", "Machan, the test cases are failing,",
        "Dei, check the memory utilization on node three,", "Seri pa, we will deploy the hotfix today,"
    ]
    ep_bodies = [
        "because the CPU utilization hit ninety percent da.",
        "so that we can get this pull request approved today pa.",
        "without running the automated regression suite first da.",
        "and monitor the application metrics continuously pa.",
        "even after we restarted the container cluster da.",
        "on the newly introduced authorization module pa.",
        "before the background worker throws an out of memory error da.",
        "as soon as the QA team gives final sign-off pa."
    ]
    ep_closers = [
        "What do you suggest we do now da?", "Please take a look at it right away pa.",
        "Let us not take any unnecessary risks da.", "Everything should go smoothly this time pa.",
        "We need to find the root cause urgently da.", "Keep me posted once it is resolved pa."
    ]

    for i in range(200):
        op = rng.choice(ep_openers)
        bod = rng.choice(ep_bodies)
        clo = rng.choice(ep_closers)
        txt = f"{op} {bod} {clo}"
        records.append({
            "category": "TANGLISH_ENGLISH_TAMIL_PARTICLES",
            "operational_language": "TANGLISH",
            "matrix_language": "ENGLISH",
            "tanglish_subtype": "ENGLISH_WITH_TAMIL_PARTICLES",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 14. TANGLISH_INTRA_SENTENTIAL (Alternating Tamil and English clauses within the sentence)
    is_tamil_clauses = [
        "Sprint planning mudinjathum,", "Intha algorithm romba slow-ah execute aaguthu,",
        "Client requirements change aanaalum,", "Database query optimization pannitu,",
        "Code review comments ellam address panni,", "New feature deployment ready aana udane,",
        "Backend architecture refactoring pannumpothu,", "Production incident resolve pannathukku appuram,"
    ]
    is_english_clauses = [
        "we will immediately deploy the microservices to the staging cluster.",
        "so we decided to benchmark the cache lookups using in-memory queues.",
        "our engineering team successfully delivered the core milestone on time.",
        "we observed a massive fifty percent reduction in latency metrics.",
        "the team approved the pull request and merged it into main branch.",
        "the QA lead will trigger automated smoke tests across all test suites.",
        "we must preserve backward compatibility for all existing public APIs.",
        "the engineering director conducted a comprehensive blameless post-mortem."
    ]
    is_concls = [
        "Idhula ethavathu problem iruntha team-kku update pannunga.",
        "Kandippa intha approach romba clean-ah irukkum nu ninaikiren.",
        "Athanala future maintenance work romba easy aagidum da.",
        "Let us monitor the production metrics very closely tonight."
    ]

    for i in range(200):
        tc = rng.choice(is_tamil_clauses)
        ec = rng.choice(is_english_clauses)
        co = rng.choice(is_concls)
        txt = f"{tc} {ec} {co}"
        records.append({
            "category": "TANGLISH_INTRA_SENTENTIAL",
            "operational_language": "TANGLISH",
            "matrix_language": "TANGLISH",
            "tanglish_subtype": "INTRA_SENTENTIAL_CODE_SWITCH",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 15. TANGLISH_INFORMAL (Casual everyday conversational Tanglish)
    inf_openers = [
        "Enna machan,", "Dei nanba,", "Hi bro,", "Machi,", "Aiyo friend,",
        "Hello thambi,", "Enna da,", "Mappillai,"
    ]
    inf_topics = [
        "weekend enna plan vachirukka?", "innaiku evening cafeteria-la tea kudikkalama?",
        "nethu release aana puthu movie paathiya?", "office work romba heavy-ah irunthuchu da,",
        "lunch-kku enna saapida pora?", "gym-kku innaiku timing enna vachirukka?",
        "intha trip plan-ah confirm pannitiya?", "cricket match score paathiya da,"
    ]
    inf_reactions = [
        "romba stress-ah irukku, konjam chill pannanum.", "ticket book pannitiya illa innum decide pannala-ya?",
        "super entertaining-ah irunthuchu nu sonnanga.", "seekiram mudichitu kelambalam nu paakuren.",
        "hotel-la order pannalama illa cafeteria polama?", "innaiku workout skip panna koodathu machan.",
        "friends ellam waiting, seekiram reply pannu.", "kadasi over-la match sema thrilling-ah pochu."
    ]
    inf_closers = [
        "Call pannu pesalam.", "Message paatha udane ping pannu da.",
        "Appuram kandippa meet pannuvom.", "Take care, enjoy the day da."
    ]

    for i in range(200):
        op = rng.choice(inf_openers)
        top = rng.choice(inf_topics)
        reac = rng.choice(inf_reactions)
        clo = rng.choice(inf_closers)
        txt = f"{op} {top} {reac} {clo}"
        records.append({
            "category": "TANGLISH_INFORMAL",
            "operational_language": "TANGLISH",
            "matrix_language": "TANGLISH",
            "tanglish_subtype": "ROMANIZED_TAMIL",
            "text": unicodedata.normalize("NFC", txt)
        })

    # 16. TANGLISH_FORMAL_TECH (Professional bilingual engineering discourse)
    ft_contexts = [
        "In today's architecture review meeting,", "Regarding the production cluster upgrade,",
        "During the cross-functional sprint planning session,", "In our cloud infrastructure cost optimization review,",
        "Regarding the security compliance audit checklist,", "While analyzing the recent latency spike in payment gateway,"
    ]
    ft_tamil_phrases = [
        "intha microservice scalability issue-va address panna",
        "database query indexing strategy-ஐ restructure panni",
        "container autoscaling policy-ஐ properly configure panni",
        "asynchronous message broker throughput-ஐ enhance panna",
        "caching layer invalidation logic-ஐ optimize panni",
        "system logging and monitoring telemetry-ஐ streamline panni"
    ]
    ft_actions = [
        "we must deploy distributed tracing across all interconnected components.",
        "the engineering team will conduct rigorous end-to-end performance benchmarking.",
        "we will publish an updated architecture decision record before next release.",
        "all developers should follow strict idempotent design patterns in API contracts.",
        "we need to ensure zero downtime during database schema migration.",
        "automated alert thresholds must trigger immediate alerts for on-call engineers."
    ]
    ft_closers = [
        "Idhoda progress-ஐ daily standup-la track pannuvom.",
        "Intha approach system reliability-ஐ drastically improve pannum.",
        "Team leads ellarum intha specification-ஐ review panni sign-off tharanum.",
        "Documentation-ஐ internal engineering wiki-la update panni vachirukkom."
    ]

    for i in range(200):
        ctx = rng.choice(ft_contexts)
        tp = rng.choice(ft_tamil_phrases)
        act = rng.choice(ft_actions)
        clo = rng.choice(ft_closers)
        txt = f"{ctx} {tp}, {act} {clo}"
        records.append({
            "category": "TANGLISH_FORMAL_TECH",
            "operational_language": "TANGLISH",
            "matrix_language": "TANGLISH",
            "tanglish_subtype": "INTRA_SENTENTIAL_CODE_SWITCH",
            "text": unicodedata.normalize("NFC", txt)
        })

    print(f"Total generated records: {len(records)}")

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

    return records

if __name__ == "__main__":
    records = build_corpus()
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

    # Check uniqueness
    unique_hashes = set(r["sha256"] for r in records)
    print(f"\nTotal records: {len(records)}, Unique hashes: {len(unique_hashes)}")
