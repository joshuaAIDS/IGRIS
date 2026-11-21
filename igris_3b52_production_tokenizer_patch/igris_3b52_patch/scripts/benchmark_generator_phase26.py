"""
scripts/benchmark_generator_phase26.py

Generates PHASE26_DATASET_SPLITS.json:
- 3 non-overlapping splits: dev (100), val (100), test (100) -> 300 records total.
- Complete schema: id, text, ground_truth_language, category, expected_processing_behavior,
  difficulty, provenance, dataset_split, expected_quality_pass, expected_duplicate,
  expected_rejection_reasons, notes.
- Zero fixture leakage between splits.
"""

import json
from pathlib import Path

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
OUT_JSON = PATCH_DIR / "PHASE26_DATASET_SPLITS.json"

def build_split(split_name, prefix, seed_offset):
    records = []
    rec_num = 1

    def add(text, lang, cat, action, diff, q_pass, is_dup, reasons=None, notes=""):
        nonlocal rec_num
        rec_id = f"{prefix}-{rec_num:04d}"
        rec_num += 1
        records.append({
            "id": rec_id,
            "text": text,
            "ground_truth_language": lang,
            "category": cat,
            "expected_processing_behavior": action,
            "difficulty": diff,
            "provenance": "SYNTHETIC_GENERATOR_PHASE26",
            "dataset_split": split_name,
            "expected_quality_pass": q_pass,
            "expected_duplicate": is_dup,
            "expected_rejection_reasons": reasons or [],
            "notes": notes,
        })

    # =========================================================================
    # 1. TAMIL RECORDS (20 records)
    # =========================================================================
    if split_name == "dev":
        add("தமிழ் மொழியானது உலகின் மிகத் தொன்மையான செம்மொழிகளில் ஒன்றாகக் கருதப்படுகிறது.", "TAMIL", "TAMIL_LITERATURE", "ACCEPTED", "EASY", True, False, notes="Classical Tamil heritage prose")
        add("இயற்கை வளங்களைப் பாதுகாப்பது நமது எதிர்கால சந்ததியினரின் நலனுக்கு மிகவும் இன்றியமையாதது ஆகும்.", "TAMIL", "TAMIL_GENERAL", "ACCEPTED", "EASY", True, False, notes="General informative Tamil")
        add("கணினி அறிவியல் துறையில் செயற்கை நுண்ணறிவு மற்றும் இயந்திரக் கற்றல் பெரும் மாற்றங்களை ஏற்படுத்துகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "MEDIUM", True, False, notes="Modern computing Tamil")
        add("அறிவியல் ஆராய்ச்சிகள் மனித சமுதாயத்தின் வளர்ச்சிக்கும் நல்வாழ்விற்கும் வழிவகுக்கின்றன.", "TAMIL", "TAMIL_SCIENCE", "ACCEPTED", "EASY", True, False, notes="Scientific prose in Tamil")
        add("நூலகங்கள் அறிவின் களஞ்சியங்களாகவும் பண்பாட்டு மையங்களாகவும் திகழ்கின்றன.", "TAMIL", "TAMIL_EDUCATION", "ACCEPTED", "EASY", True, False, notes="Educational prose")
        add("காலை வேளையில் நடைப்பயிற்சி மேற்கொள்வது உடல் நலத்திற்கும் மன அமைதிக்கும் நல்லது.", "TAMIL", "TAMIL_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Informal daily advice")
        add("நேற்று மாலை நண்பர்களுடன் கடற்கரைக்குச் சென்று இனிமையாகப் பொழுதைக் கழித்தோம்.", "TAMIL", "TAMIL_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Past event conversational")
        add("புதிய தொழில் தொடங்குவதற்குத் தேவையான திட்ட அறிக்கையை வங்கி அதிகாரிகளிடம் சமர்ப்பித்தார்.", "TAMIL", "TAMIL_FORMAL", "ACCEPTED", "MEDIUM", True, False, notes="Formal financial prose")
        add("சுற்றுச்சூழல் விழிப்புணர்வு பேரணியில் கல்லூரி மாணவர்கள் அனைவரும் ஆர்வத்துடன் கலந்துகொண்டனர்.", "TAMIL", "TAMIL_NEWS", "ACCEPTED", "EASY", True, False, notes="News reporting style")
        add("மருத்துவ பரிசோதனை முடிவுகள் அனைத்தும் திருப்திகரமாக இருப்பதாக மருத்துவர் தெரிவித்தார்.", "TAMIL", "TAMIL_HEALTHCARE", "ACCEPTED", "EASY", True, False, notes="Medical diagnosis context")
        add("தரவுத்தள அட்டவணைகளில் உள்ள குறியீடுகள் வினவல் வேகத்தை பல மடங்கு அதிகரிக்க உதவுகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Database indexing technical Tamil")
        add("வலைப்பின்னல் பாதுகாப்பு நெறிமுறைகள் அங்கீகரிக்கப்படாத தரவு அணுகலைத் திறம்பட தடுக்கின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Network security technical Tamil")
        add("செயலி நிரலாக்கத்தில் நினைவக மேலாண்மை கசிவுகளைத் தவிர்ப்பது முதன்மையான பணியாகும்.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Programming memory management")
        add("செயற்கைக்கோள் தொலை உணர்வுத் தரவுகள் பயிர் விளைச்சல் மதிப்பீட்டிற்குப் பயன்படுகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "MEDIUM", True, False, notes="Remote sensing satellite Tamil")
        add("மின்னாற்றல் பகிர்வு வலையமைப்பில் தானியங்கி சுவிட்சுகள் தடங்கலற்ற மின்சாரத்தை வழங்குகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Power grid technical Tamil")
        add("கற்பவை கற்று வல்லுநராய் விளங்குதல் சான்றோரின் தலையாய கடமையாகப் போற்றப்படுகிறது.", "TAMIL", "TAMIL_MORPHOLOGY", "ACCEPTED", "HARD", True, False, notes="Classical sandhi and morphology")
        add("சொற்பொழிவாளர் கூறிய கருத்துக்கள் அவையோரின் சிந்தனையைத் தூண்டுவனவாக அமைந்திருந்தன.", "TAMIL", "TAMIL_MORPHOLOGY", "ACCEPTED", "MEDIUM", True, False, notes="Formal rhetoric vocabulary")
        add("வளர்ந்தோங்கும் அறிவியல் உலகில் தமிழ்ச் சொற்களஞ்சியத்தை விரிவுபடுத்துவது அவசியமாகிறது.", "TAMIL", "TAMIL_MORPHOLOGY", "ACCEPTED", "HARD", True, False, notes="Sandhi concatenation rules")
        add("பண்பாட்டு விழுமியங்களைப் பேணிப் பாதுகாத்தல் இளைய தலைமுறையினரின் நற்கடமையாகும்.", "TAMIL", "TAMIL_LITERATURE", "ACCEPTED", "MEDIUM", True, False, notes="Cultural ethics prose")
        add("திருக்குறள் அறத்துப்பால் மனிதனின் நன்னடத்தைக்கான அடிப்படைக் கொள்கைகளை விளக்குகிறது.", "TAMIL", "TAMIL_LITERATURE", "ACCEPTED", "EASY", True, False, notes="Ethical philosophy")
    elif split_name == "val":
        add("தொன்மை வாய்ந்த தமிழ் இலக்கியங்கள் மனித வாழ்வின் விழுமியங்களை மிக அழகாக எடுத்துரைக்கின்றன.", "TAMIL", "TAMIL_LITERATURE", "ACCEPTED", "EASY", True, False, notes="Literary value prose")
        add("மழைநீர் சேகரிப்பு அமைப்புகளை வீடுகளில் அமைப்பது நிலத்தடி நீர்மட்டத்தை உயர்த்த மிகவும் உதவும்.", "TAMIL", "TAMIL_ENVIRONMENT", "ACCEPTED", "EASY", True, False, notes="Water conservation")
        add("செயற்கை நுண்ணறிவு மாதிரிகள் பெரிய அளவிலான தரவுத்தொகுப்புகளைக் கொண்டு பயிற்றுவிக்கப்படுகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "MEDIUM", True, False, notes="AI training sets in Tamil")
        add("பண்டைய சோழர்களின் கடல்சார் வணிகம் தென்கிழக்கு ஆசிய நாடுகளில் பரவியிருந்ததை வரலாறு கூறுகிறது.", "TAMIL", "TAMIL_HISTORY", "ACCEPTED", "EASY", True, False, notes="Maritime history prose")
        add("ஆசிரியர் மாணவர்களுக்கு கணிதக் கோட்பாடுகளை எளிய உதாரணங்களுடன் புரியும்படி விளக்கினார்.", "TAMIL", "TAMIL_EDUCATION", "ACCEPTED", "EASY", True, False, notes="Pedagogical narrative")
        add("இன்று மதியம் அலுவலக உணவகத்தில் சுவையான சாம்பார் சாதம் மற்றும் அப்பளம் வழங்கப்பட்டது.", "TAMIL", "TAMIL_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Daily lunch conversation")
        add("வார இறுதியில் குடும்பத்தினருடன் கிராமத்திற்குச் சென்று அமைதியான சூழலில் தங்கி வந்தோம்.", "TAMIL", "TAMIL_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Weekend travel narrative")
        add("நகராட்சி நிர்வாகம் சாலை விரிவாக்கப் பணிகளை விரைந்து முடிக்குமாறு ஒப்பந்ததாரருக்கு உத்தரவிட்டது.", "TAMIL", "TAMIL_FORMAL", "ACCEPTED", "MEDIUM", True, False, notes="Civic governance notice")
        add("மாவட்ட அளவிலான அறிவியல் கண்காட்சியில் பள்ளி மாணவர்களின் கண்டுபிடிப்புகள் பாராட்டப்பட்டன.", "TAMIL", "TAMIL_NEWS", "ACCEPTED", "EASY", True, False, notes="Science exhibition news")
        add("யோகா மற்றும் தியானப் பயிற்சிகள் மன அழுத்தத்தைக் குறைத்து உடல் சுறுசுறுப்பை அதிகரிக்கின்றன.", "TAMIL", "TAMIL_HEALTHCARE", "ACCEPTED", "EASY", True, False, notes="Wellness and health")
        add("விநியோகிக்கப்பட்ட அமைப்புகளில் தரவு ஒருமைப்பாட்டைப் பராமரிக்க ஒருமித்த நெறிமுறைகள் பயன்படுகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Distributed consensus Tamil")
        add("இயக்க முறைமை செயல்முறைகளுக்கு இடையேயான தொடர்புகளை பாதுகாப்பான நினைவகப் பாதையில் அமைக்கிறது.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="IPC operating system Tamil")
        add("நுண்செயலி வடிவமைப்பு வழிமுறைகள் மின் நுகர்வைக் குறைத்து செயலாக்கத் திறனை மேம்படுத்துகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Microprocessor architecture")
        add("மேகக்கணி சேமிப்பகத்தில் தரவுகள் குறியாக்கப்பட்டு அங்கீகரிக்கப்பட்ட பயனர்களுக்கு மட்டுமே பகிரப்படுகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "MEDIUM", True, False, notes="Cloud encryption Tamil")
        add("தானியங்கி வாகனங்கள் சென்சார் தகவல்களை நிகழ்நேரத்தில் பகுப்பாய்வு செய்து பாதையைத் தீர்மானிக்கின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Autonomous systems Tamil")
        add("எப்பொருள் யார்யார்வாய்க் கேட்பினும் அப்பொருள் மெய்ப்பொருள் காண்பது அறிவு என்பது தமிழ் மரபு.", "TAMIL", "TAMIL_MORPHOLOGY", "ACCEPTED", "HARD", True, False, notes="Proverbial classical sandhi")
        add("பழங்காலக் கல்வெட்டுகள் அக்காலத்து ஆட்சிமுறை மற்றும் சமூக நிலையைப் படம்பிடித்துக் காட்டுகின்றன.", "TAMIL", "TAMIL_HISTORY", "ACCEPTED", "MEDIUM", True, False, notes="Epigraphy and history")
        add("மொழிபெயர்ப்புத் துறையில் சொல்லாக்க நெறிகளைப் பின்பற்றி புதிய கலைச்சொற்கள் உருவாக்கப்படுகின்றன.", "TAMIL", "TAMIL_LINGUISTICS", "ACCEPTED", "HARD", True, False, notes="Tamil terminology creation")
        add("மகிழ்ச்சியான மனநிலையே ஒரு மனிதனின் ஆரோக்கியமான நீண்ட ஆயுளுக்கு முதன்மையான காரணியாகும்.", "TAMIL", "TAMIL_WELLNESS", "ACCEPTED", "EASY", True, False, notes="Psychological wellness")
        add("பாரதியாரின் கவிதைகள் விடுதலை உணர்வையும் பெண் கல்வியின் அவசியத்தையும் ஓங்கி முழங்கின.", "TAMIL", "TAMIL_LITERATURE", "ACCEPTED", "EASY", True, False, notes="Bharathiyar literature")
    else:  # test split
        add("சங்க இலக்கியங்கள் தமிழர்களின் உயரிய காதல் மற்றும் வீர வாழ்வை விவரிக்கும் ஒப்பற்ற கருவூலமாகும்.", "TAMIL", "TAMIL_LITERATURE", "ACCEPTED", "EASY", True, False, notes="Sangam literature prose")
        add("காடுகளைப் பாதுகாப்பதன் மூலமே பருவமழை பொய்க்காமல் விவசாயம் தழைத்தோங்க வழிவகை செய்ய இயலும்.", "TAMIL", "TAMIL_ENVIRONMENT", "ACCEPTED", "EASY", True, False, notes="Forest preservation")
        add("நரம்பியல் வலையமைப்புகள் மனித மூளையின் செயல்பாடுகளைப் போன்ற கற்றல் திறனைப் பெற்று விளங்குகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "MEDIUM", True, False, notes="Neural networks Tamil")
        add("காவிரி டெல்டா பாசன விவசாயிகள் நவீன நெல் சாகுபடி முறைகளை வெற்றிகரமாகக் கையாண்டு வருகின்றனர்.", "TAMIL", "TAMIL_AGRICULTURE", "ACCEPTED", "EASY", True, False, notes="Agriculture technology")
        add("பல்கலைக்கழகப் பட்டமளிப்பு விழாவில் சாதனை படைத்த மாணவர்களுக்கு தங்கப் பதக்கங்கள் வழங்கப்பட்டன.", "TAMIL", "TAMIL_EDUCATION", "ACCEPTED", "EASY", True, False, notes="University convocation")
        add("கடும் வேலைப்பளுவுக்குப் பிறகு ஒரு சிறிய விடுமுறை எடுத்துக்கொண்டு மலை வாசஸ்தலம் செல்லவிருக்கிறேன்.", "TAMIL", "TAMIL_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Vacation plan conversation")
        add("என் செல்லப் பிராணிக்கு உடல்நிலை சரியில்லாததால் கால்நடை மருத்துவமனைக்கு அழைத்துச் சென்றேன்.", "TAMIL", "TAMIL_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Pet healthcare conversational")
        add("பாதுகாப்பு அமைச்சகம் எல்லைப் பகுதிகளில் நவீன கண்காணிப்பு உபகரணங்களைப் பொருத்தியுள்ளது.", "TAMIL", "TAMIL_FORMAL", "ACCEPTED", "MEDIUM", True, False, notes="Defense formal news")
        add("சர்வதேச திரைப்பட விழாவில் தமிழ் திரைப்படம் ஒன்றுக்கு சிறந்த ஒளிப்பதிவுக்கான விருது கிடைத்தது.", "TAMIL", "TAMIL_NEWS", "ACCEPTED", "EASY", True, False, notes="Cinema news coverage")
        add("பாரம்பரிய சித்த மருத்துவ முறைகள் பல நாள்பட்ட நோய்களுக்கு பக்கவிளைவுகளற்ற தீர்வை வழங்குகின்றன.", "TAMIL", "TAMIL_HEALTHCARE", "ACCEPTED", "EASY", True, False, notes="Siddha traditional medicine")
        add("குவாண்டம் கணினி தொழில்நுட்பம் எதிர்காலத்தில் சிக்கலான குறியாக்க அமைப்புகளைத் தீர்க்க வல்லது.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Quantum computing Tamil")
        add("வலைதள சேவையகங்கள் அதிக அளவிலான கோரிக்கைகளை கையாள சுமை சமநிலைக் கருவிகளைப் பயன்படுத்துகின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Load balancing technical Tamil")
        add("நிகழ்நேர இயக்க முறைமைகள் வினாடியின் மைக்ரோ பகுதிக்குள் பணிகளை முடிக்கும் உத்தரவாதத்தை அளிக்கின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Real-time OS Tamil")
        add("குறியாக்கவியல் வழிமுறைகள் மின்னணு பணப்பரிவர்த்தனைகளை இணைய மோசடிகளில் இருந்து பாதுகாக்கின்றன.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "HARD", True, False, notes="Cryptography financial Tamil")
        add("ரோபோட்டிக்ஸ் தொழில்நுட்பம் தொழிற்சாலைகளில் உற்பத்தித்திறனையும் பாதுகாப்பையும் பெருமளவில் கூட்டுகிறது.", "TAMIL", "TAMIL_TECHNICAL", "ACCEPTED", "MEDIUM", True, False, notes="Industrial robotics Tamil")
        add("கற்பனைக் கதைகளைக் காட்டிலும் வரலாற்று உண்மைகளை ஆதாரங்களுடன் விளக்குவதே ஆய்வின் நோக்கம்.", "TAMIL", "TAMIL_MORPHOLOGY", "ACCEPTED", "HARD", True, False, notes="Historical research prose")
        add("தன் கடமையை செவ்வனே ஆற்றுவோருக்கு வெற்றியானது தானாகவே வந்து சேரும் என்பது உறுதி.", "TAMIL", "TAMIL_PHILOSOPHY", "ACCEPTED", "MEDIUM", True, False, notes="Philosophical reflection")
        add("தமிழறிஞர்கள் பலரும் உலகெங்கிலும் பரவி தமிழ் பண்பாட்டை அடுத்த தலைமுறைக்குக் கடத்துகின்றனர்.", "TAMIL", "TAMIL_CULTURE", "ACCEPTED", "MEDIUM", True, False, notes="Global Tamil diaspora")
        add("இளைய தலைமுறை மாணவர்கள் நூல்களை வாசிக்கும் பழக்கத்தை வளர்த்துக்கொள்வது அவர்களின் சிந்தனைக்கு நலம்.", "TAMIL", "TAMIL_EDUCATION", "ACCEPTED", "EASY", True, False, notes="Reading habits advice")
        add("சிலப்பதிகாரம் கண்ணகியின் கற்பின் மாண்பையும் பாண்டிய மன்னனின் நீதி தவறாத தன்மையையும் விவரிக்கிறது.", "TAMIL", "TAMIL_LITERATURE", "ACCEPTED", "EASY", True, False, notes="Silappathikaram epic")

    # =========================================================================
    # 2. ENGLISH RECORDS (20 records, including potential false-suffix challenges)
    # =========================================================================
    if split_name == "dev":
        add("The decoder-only transformer architecture forms the foundation of modern large language models.", "ENGLISH", "ENGLISH_SYSTEMS", "ACCEPTED", "EASY", True, False, notes="Transformer architecture")
        add("Operating system processes manage virtual memory allocation and inter-process communication channels.", "ENGLISH", "ENGLISH_SYSTEMS", "ACCEPTED", "EASY", True, False, notes="OS memory management")
        add("Cryptographic hash functions produce fixed-size deterministic digests from arbitrary input byte streams.", "ENGLISH", "ENGLISH_SECURITY", "ACCEPTED", "EASY", True, False, notes="Cryptographic digests")
        add("Distributed consensus protocols ensure data consistency across replicated state machines in the cluster.", "ENGLISH", "ENGLISH_DISTRIBUTED", "ACCEPTED", "MEDIUM", True, False, notes="Distributed consensus")
        add("Database indexing structures such as B-trees significantly reduce the latency of query lookups.", "ENGLISH", "ENGLISH_DATABASES", "ACCEPTED", "EASY", True, False, notes="B-tree index query latency")
        add("We should discuss the quarterly project milestones during our weekly synchronization meeting tomorrow.", "ENGLISH", "ENGLISH_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Office collaboration conversation")
        add("Please ensure all unit test cases are executed before opening a pull request for team review.", "ENGLISH", "ENGLISH_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="PR guideline conversation")
        add("The restaurant downtown serves excellent Italian pasta with freshly baked sourdough bread and olive oil.", "ENGLISH", "ENGLISH_GENERAL", "ACCEPTED", "EASY", True, False, notes="Casual dining recommendation")
        add("Regular physical exercise combined with balanced nutrition contributes significantly to cardiovascular health.", "ENGLISH", "ENGLISH_HEALTHCARE", "ACCEPTED", "EASY", True, False, notes="Health and nutrition advice")
        add("Autonomous navigation algorithms utilize real-time sensor streams to detect obstacles in urban environments.", "ENGLISH", "ENGLISH_ROBOTICS", "ACCEPTED", "MEDIUM", True, False, notes="Autonomous navigation")
        add("Software compilation involves lexical analysis, parsing, semantic verification, and code generation.", "ENGLISH", "ENGLISH_COMPILERS", "ACCEPTED", "MEDIUM", True, False, notes="Compiler stages")
        add("Static analysis tools inspect syntax trees to enforce architectural boundary constraints across modules.", "ENGLISH", "ENGLISH_CODE_QUALITY", "ACCEPTED", "MEDIUM", True, False, notes="Static code analysis")
        add("High-availability architectures eliminate single points of failure through automated failover mechanisms.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'single', 'failover'")
        add("Microservice architectures decouple application components into independently deployable units communicating over HTTP.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'decouple', 'deployable'")
        add("Cache coherence mechanisms maintain memory uniformity across multiple processing cores in modern processors.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'multiple'")
        add("Network transport layers establish reliable end-to-end connections using transmission control protocols.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'reliable', 'protocol'")
        add("Asynchronous event loops handle multiple concurrent non-blocking input and output operations efficiently.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'handle', 'multiple'")
        add("Memory safety guarantees prevent buffer overflows and dangling pointer dereferences in low-level systems.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "MEDIUM", True, False, notes="Low-level memory safety")
        add("Garbage collection routines traverse object reference graphs to reclaim unreachable heap allocations safely.", "ENGLISH", "ENGLISH_SYSTEMS", "ACCEPTED", "MEDIUM", True, False, notes="Garbage collection graph traversal")
        add("The primary objective of automated unit testing is isolating components to verify behavioral invariants.", "ENGLISH", "ENGLISH_TESTING", "ACCEPTED", "EASY", True, False, notes="Unit test invariants")
    elif split_name == "val":
        add("Modern operating systems enforce hardware-assisted address space separation to secure user processes.", "ENGLISH", "ENGLISH_SYSTEMS", "ACCEPTED", "EASY", True, False, notes="Address space separation")
        add("Relational database engines rely on cost-based optimizers to select efficient physical execution plans.", "ENGLISH", "ENGLISH_DATABASES", "ACCEPTED", "MEDIUM", True, False, notes="Query optimizer plans")
        add("Public key cryptography enables confidential communication over insecure channels using asymmetric key pairs.", "ENGLISH", "ENGLISH_SECURITY", "ACCEPTED", "EASY", True, False, notes="Asymmetric encryption")
        add("Fault-tolerant message queues buffer incoming requests to decouple ingestion from asynchronous processing workers.", "ENGLISH", "ENGLISH_DISTRIBUTED", "ACCEPTED", "MEDIUM", True, False, notes="Message queues buffering")
        add("Deep learning frameworks construct dynamic computation graphs to compute backward gradients automatically.", "ENGLISH", "ENGLISH_AI_ML", "ACCEPTED", "EASY", True, False, notes="Autograd computation graph")
        add("Could you review the proposed schema migration before we apply it to the staging environment tonight?", "ENGLISH", "ENGLISH_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="Schema migration request")
        add("The conference speaker presented fascinating research on sustainable urban transportation infrastructure.", "ENGLISH", "ENGLISH_GENERAL", "ACCEPTED", "EASY", True, False, notes="Conference keynote report")
        add("Continuous integration pipelines run linting, security scanning, and unit tests upon every commit.", "ENGLISH", "ENGLISH_DEVOPS", "ACCEPTED", "EASY", True, False, notes="CI pipeline automation")
        add("Effective documentation clarifies architectural design decisions and simplifies onboarding for new engineers.", "ENGLISH", "ENGLISH_DOCUMENTATION", "ACCEPTED", "EASY", True, False, notes="Engineering documentation")
        add("Browser rendering engines parse cascading style sheets and construct the visual render tree incrementally.", "ENGLISH", "ENGLISH_WEB", "ACCEPTED", "MEDIUM", True, False, notes="DOM CSS render tree")
        add("Virtual machines provide isolated guest operating systems by virtualizing underlying hardware resources.", "ENGLISH", "ENGLISH_VIRTUALIZATION", "ACCEPTED", "MEDIUM", True, False, notes="Hypervisors and VMs")
        add("Distributed transactions utilize two-phase commit protocols to guarantee atomic commit across multiple partitions.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'multiple'")
        add("Scalable architectures assemble stateless backend services fronted by resilient load balancers.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'assemble'")
        add("Web frameworks handle incoming HTTP requests through composable middleware filter pipelines.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'handle', 'composable'")
        add("Reliable data transmission protocols retransmit dropped packets using sliding window flow control mechanisms.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'reliable'")
        add("Event-driven architectures decouple state mutation publishers from independent downstream subscribers cleanly.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'decouple'")
        add("Low-latency trading platforms optimize network interface ring buffers to minimize serialization delays.", "ENGLISH", "ENGLISH_SYSTEMS", "ACCEPTED", "MEDIUM", True, False, notes="Trading platform latency")
        add("Content delivery networks cache static media assets at geographic edge locations near end users.", "ENGLISH", "ENGLISH_NETWORKING", "ACCEPTED", "EASY", True, False, notes="CDN edge caching")
        add("Container orchestrators reconcile cluster desired states by scheduling workload replicas across compute nodes.", "ENGLISH", "ENGLISH_CLOUD", "ACCEPTED", "MEDIUM", True, False, notes="K8s scheduling loop")
        add("Comprehensive observability platforms ingest structured logs, distributed traces, and metric time series.", "ENGLISH", "ENGLISH_MONITORING", "ACCEPTED", "EASY", True, False, notes="Observability telemetry")
    else:  # test split
        add("Hardware abstraction layers encapsulate device-specific register operations behind uniform kernel driver interfaces.", "ENGLISH", "ENGLISH_SYSTEMS", "ACCEPTED", "EASY", True, False, notes="HAL driver interfaces")
        add("Columnar storage formats optimize analytical queries by compressing homogeneous column vectors independently.", "ENGLISH", "ENGLISH_DATABASES", "ACCEPTED", "MEDIUM", True, False, notes="Parquet columnar formats")
        add("Zero-trust security models authenticate and authorize every identity before granting access to network perimeters.", "ENGLISH", "ENGLISH_SECURITY", "ACCEPTED", "EASY", True, False, notes="Zero trust security")
        add("Raft consensus clusters elect a unique leader node to sequence log entries across peer replica nodes.", "ENGLISH", "ENGLISH_DISTRIBUTED", "ACCEPTED", "MEDIUM", True, False, notes="Raft consensus leader")
        add("Quantization techniques compress neural network weights into low-bit integers to accelerate edge inference.", "ENGLISH", "ENGLISH_AI_ML", "ACCEPTED", "EASY", True, False, notes="Model quantization INT8")
        add("I checked the production monitoring metrics and verified that request error rates remained well below threshold.", "ENGLISH", "ENGLISH_CONVERSATIONAL", "ACCEPTED", "EASY", True, False, notes="SRE metric verification")
        add("The local botanical garden features thousands of rare indigenous plant species and educational walking tours.", "ENGLISH", "ENGLISH_GENERAL", "ACCEPTED", "EASY", True, False, notes="Botanical garden prose")
        add("Automated canary deployments route a small fraction of live user traffic to newly deployed revisions.", "ENGLISH", "ENGLISH_DEVOPS", "ACCEPTED", "EASY", True, False, notes="Canary deployment rollout")
        add("Strong typing disciplines detect representational bugs at compile time before binaries execute in production.", "ENGLISH", "ENGLISH_PL_THEORY", "ACCEPTED", "MEDIUM", True, False, notes="Type system safety")
        add("WebAssembly provides a sandboxed stack-based bytecode virtual machine running with near-native speed in browsers.", "ENGLISH", "ENGLISH_WEB", "ACCEPTED", "MEDIUM", True, False, notes="Wasm bytecode runtime")
        add("Non-volatile storage controllers utilize wear leveling algorithms to maximize flash memory durability.", "ENGLISH", "ENGLISH_HARDWARE", "ACCEPTED", "MEDIUM", True, False, notes="SSD wear leveling")
        add("Resilient software systems handle transient network partitions by employing exponential backoff and jitter.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'handle'")
        add("Modular codebases decouple domain business logic from infrastructure persistence adapters through interfaces.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'decouple'")
        add("High-throughput stream processors assemble unbounded record streams into sliding window aggregations.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'assemble'")
        add("Distributed tracing libraries correlate individual service spans by propagating unique trace identifiers.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'correlate'")
        add("Extensible microkernel architectures isolate device drivers into user space to prevent kernel panics.", "ENGLISH", "ENGLISH_CHALLENGE_SUFFIX", "ACCEPTED", "HARD", True, False, notes="Contains 'extensible'")
        add("Connection pooling libraries manage database socket lifecycles to eliminate repetitive handshake latency overhead.", "ENGLISH", "ENGLISH_SYSTEMS", "ACCEPTED", "MEDIUM", True, False, notes="DB connection pools")
        add("Load testing tools simulate peak concurrent user traffic to identify database connection bottlenecks.", "ENGLISH", "ENGLISH_QA", "ACCEPTED", "EASY", True, False, notes="Load testing concurrency")
        add("Stateless microservices scale horizontally by provisioning additional container replicas behind traffic balancers.", "ENGLISH", "ENGLISH_CLOUD", "ACCEPTED", "MEDIUM", True, False, notes="Autoscaling microservices")
        add("Immutable infrastructure patterns replace misbehaving virtual servers rather than applying in-place mutations.", "ENGLISH", "ENGLISH_DEVOPS", "ACCEPTED", "EASY", True, False, notes="Immutable server patterns")

    # =========================================================================
    # 3. TANGLISH RECORDS (30 records: Romanized, Particles, Mixed, Technical)
    # =========================================================================
    if split_name == "dev":
        # Romanized Tamil (8)
        add("Innaiku kaalaila romba mazhai peyudhu, veliya poga mudiyala pa.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Weather conversational")
        add("Naalaiku office-ku seekiram kelambanum, mukkiyamaana client meeting irukku.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Office commute conversation")
        add("Indha hotel-la biryani taste romba nalla iruku, kandippa marubadiyum varanum.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Food recommendation")
        add("Weekend-la friends ellarum serndhu cinema-ku polama nu yosikirom.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Cinema outing plan")
        add("Unakku enna problem, edhuku ipdi kavalappattutu irukka, ellam seri aayidum.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "MEDIUM", True, False, notes="Emotional consolation")
        add("Pudhiya laptop vangiyachu, build quality super-aa iruku, performance semma speed.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Gadget review")
        add("Exam-ku nalla prepare pannitiya? Enaku innum konjam portions padikka vendiyirukku.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "MEDIUM", True, False, notes="Exam prep question")
        add("Train tickets confirm aayiducha illai waiting list-la dhaan iruka nu check pannu.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Ticket confirmation")
        # English with Tamil Particles (8)
        add("Let us wrap up this release quickly da, otherwise deployment will get delayed.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Trailing 'da' particle")
        add("Aiyo, the network latency is spiking again, please check the load balancer.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Leading 'aiyo' exclamation")
        add("Don't worry pa, the pipeline will auto-recover in a couple of minutes.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Interjected 'pa' reassurance")
        add("Please finish this documentation ticket today itself da, client is waiting.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Urgent request with 'da'")
        add("No problem da, we can easily reproduce the test failure in our local sandbox.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Debugging reassurance with 'da'")
        add("Aiyoo, the entire monitoring dashboard is showing timeout errors across all nodes.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Crisis exclamation 'aiyoo'")
        add("Hey machan, check the build logs, everything compiled smoothly without errors.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "EASY", True, False, notes="Friendly 'machan' address")
        add("Seri, let us schedule the database backup window for midnight tonight.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Agreement marker 'seri'")
        # Intra-Sentential Code-Switching (7)
        add("Server reboot aana piragu microservices automatically start aagala, script execute பண்ணனும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="DevOps code-switching")
        add("Database connection pool timeout increase பண்ணினா, concurrency issues solve aagidum.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="Backend DB code-switch")
        add("Indha API endpoint-ku JSON response structure validate பண்ணியாச்சு, frontend integrate பண்ணலாம்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="API frontend integration")
        add("Model training loss stabilize aaga 50 epochs வரை run பண்ண வேண்டியிருக்கும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="ML training code-switch")
        add("Production deployment-க்கு முன்னாடி regression tests run பண்ணி report generate பண்ணுங்க.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Pre-deployment QA check")
        add("Code review-ல performance optimization suggestions கொடுத்திருக்காங்க, change பண்ணனும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="PR review feedback")
        add("Docker container restart loop-ல மாட்டிக்கிச்சு, container logs inspect பண்ணி debug பண்ணு.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="Container crash debug")
        # Formal Technical Tanglish (7)
        add("Decoder-only transformer architecture-ல் multi-head self-attention mechanisms language representations-ஐ generate செய்கின்றன.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Attention representations")
        add("Tokenizer vocabulary-யில் 32,768 structural and subword tokens முறையாக allocate செய்யப்பட்டுள்ளன.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Tokenizer allocation")
        add("Gradient clipping threshold 1.0-க்கு மேலாக செல்லாமல் training stability ensure செய்யப்படுகிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Gradient clipping")
        add("Checkpoint integrity verification SHA-256 hash validation மூலமாக confirm செய்யப்படுகிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Hash checkpoint audit")
        add("Context window length 2048 tokens-க்கு உட்பட்டு input sequences truncate செய்யப்படுகின்றன.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Context sequence limit")
        add("Grouped-query attention (GQA) key-value cache memory overhead-ஐ 50% reduce செய்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="GQA cache reduction")
        add("FlashAttention v2 memory-efficient exact attention computation-ஐ GPU hardware-ல் execute செய்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="FlashAttention kernel execution")
    elif split_name == "val":
        # Romanized Tamil (8)
        add("Phone battery seekiram discharge aagudhu, service center-la kudukka vendiyirukkum.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Battery complaint")
        add("Namma oorla pudhusa oru supermarket thirandhurukaanga, anga poyi paakalam.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Supermarket visit")
        add("Enakku indha vishayam theriyadhu, avana kettu solren, konjam wait pannu.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Information query")
        add("Bus stand-ku poga autokaaran kitta pesi paathen, romba adhigama kekkuraan da.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "MEDIUM", True, False, notes="Auto fare bargaining")
        add("Amma samachadhu eppovume super taste, oorukku poganum nu aasaia irukku.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Home cooking nostalgia")
        add("Avan kitta andha project files ellam kuduthuten, innum review pannala nu sonnan.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "MEDIUM", True, False, notes="Project handover")
        add("Nethu night football match paathiya, climax-la semma goal pottanga thala.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Football match commentary")
        add("Romba tired-aa irukku, oru cup tea kudinga, appuram velaiya thodangalaam.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Tea break advice")
        # English with Tamil Particles (8)
        add("Aiyo, I forgot to commit the configuration template before branching.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Git branching oops")
        add("Aiyo, the disk space on the root partition is critically low!", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Disk full alert")
        add("Don't touch the production database directly da, always use the migration scripts.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="DB safety warning")
        add("Romba carefully review the pull request, it touches the core payment flow.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Payment PR review")
        add("Thambi, don't push code without running the pre-commit linting checks first.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "EASY", True, False, notes="Junior dev advice")
        add("You must verify the cryptographic signatures before approving the release da.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Security verification")
        add("Dei, did you push the latest schema migrations to the staging environment yet?", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "EASY", True, False, notes="Casual check with 'dei'")
        add("The memory footprint looks completely stable now pa, no signs of memory leaks.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Memory status with 'pa'")
        # Intra-Sentential Code-Switching (7)
        add("User authentication token expire ஆயிடுச்சு, session refresh பண்ணி retry பண்ணுங்க.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="Session auth retry")
        add("Cloud storage bucket permissions properly configure செய்யப்பட வேண்டும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="S3 permissions config")
        add("Distributed cache miss rate அதிகமா இருக்கு, TTL duration adjust பண்ணி பாருங்க.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Cache TTL tuning")
        add("Unit test suite execute ஆகும்போது memory leak warning காண்பிக்கிறது.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="Test suite memory leak")
        add("Load balancer health check fail ஆனா traffic secondary instance-க்கு route ஆகும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Failover routing")
        add("Dataset tokenization process complete ஆகிவிட்டது, vocabulary hash verify பண்ணலாம்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="Tokenizer finish check")
        add("Kubernetes cluster node status ready-ஆ இல்லை, worker node logs analyse பண்ண வேண்டும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="K8s worker node check")
        # Formal Technical Tanglish (7)
        add("SwiGLU activation function feed-forward network layers-ல் gradient flow-ஐ மேம்படுத்துகிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="SwiGLU activation")
        add("Root Mean Square Normalization (RMSNorm) layer outputs-ஐ stabilize செய்து training speed-ஐ அதிகரிக்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="RMSNorm stabilization")
        add("Rotary position embeddings (RoPE) relative token distances-ஐ encode செய்ய உதவுகின்றன.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="RoPE embedding")
        add("AdamW optimizer decoupled weight decay mechanism மூலமாக model overfitting-ஐ தடுக்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="AdamW weight decay")
        add("Cosine annealing learning rate schedule training loss convergence-ஐ smooth ஆக்குகிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Cosine LR decay")
        add("Bfloat16 precision training numerical stability-ஐ maintain செய்து GPU memory-ஐ மிச்சப்படுத்துகிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Bfloat16 precision")
        add("Cross-entropy loss function target probability distribution-ஐ evaluate செய்து gradients calculate செய்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Cross entropy loss")
    else:  # test split
        # Romanized Tamil (8)
        add("Enaku innum rendunaal-la assignment submit pannanum, aana matter innum ready aagala.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "MEDIUM", True, False, notes="Assignment deadline panic")
        add("Pudhusa release aana web series pathiya? Semma suspense, climax twist vera level.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Web series review")
        add("Kalyanathuku poitu vandhom, sapadu laaddu semma sweet, relatives ellarayum meet pannom.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Wedding feast reflection")
        add("Bike service pottu vandhutten, engine sound ippo smooth-aa iruku, mileage epdi irukunu paakanum.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Bike maintenance feedback")
        add("Interview round romba tough-aa irunthuchu da, system design questions ellam depth-aa kettanga.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "HARD", True, False, notes="Tech interview report")
        add("Online order potta parcel innum varala, tracking status check pannina transit-la dhaan kaatuthu.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="E-commerce tracking")
        add("Gym-ku daily poganum nu mudivu panniruken, morning 6 manikke alarm vechu elundhirikanum.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Fitness resolution")
        add("Raincoat eduthu vechuko da, sky dark-aa irukku, eppo venaalum heavy rain start aagalaam.", "TANGLISH", "ROMANIZED_TAMIL", "ACCEPTED", "EASY", True, False, notes="Rain warning to friend")
        # English with Tamil Particles (8)
        add("Please don't forget to push the git tags after merge da, otherwise the build will fail.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Tag release request")
        add("Aiyo, the SSL certificate expired this morning, clients are seeing security warnings!", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Certificate expiration emergency")
        add("Everything will be completely fine pa, our database replicas are fully in sync.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Replication reassurance")
        add("Hey machan, check the benchmark report, throughput has jumped by thirty percent.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "EASY", True, False, notes="Throughput celebration")
        add("Seri, I will create the Jira tickets and assign the bug fixes to the morning sprint.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Jira planning with seri")
        add("Dei, did you verify the database connection pool settings on the staging server?", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "EASY", True, False, notes="Casual server check")
        add("Romba strictly avoid running administrative commands directly inside production pods.", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "HARD", True, False, notes="Container security rule")
        add("Aiyoo, someone accidentally deleted the shared testing branch on GitHub!", "TANGLISH", "ENGLISH_WITH_PARTICLES", "ACCEPTED", "MEDIUM", True, False, notes="Git disaster alert")
        # Intra-Sentential Code-Switching (7)
        add("Ingress controller routing rules update பண்ணியாச்சு, traffic new canary deployment-க்கு போகுது.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Ingress routing rules")
        add("Web socket connection disconnect ஆனா, client automatically exponential backoff-ல reconnect பண்ணும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Websocket backoff")
        add("Kafka topic partitioning key balance ஆகல, consumer lag increase ஆயிட்டே போகுது.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Kafka consumer lag")
        add("PostgreSQL database query plan analyze பண்ணினோம், missing index add பண்ண உடனே speed ஆச்சு.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Query tuning index")
        add("Microservice health checks pass ஆனா மட்டும் தான் traffic route பண்ண வேண்டும்.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="Health check routing")
        add("Security firewall rules modify பண்ணி, external IP range-க்கு access restrict பண்ணியாச்சு.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "HARD", True, False, notes="Firewall IP restriction")
        add("CI/CD pipeline build fail ஆயிடுச்சு, dependency cache clean பண்ணி retry பண்ணுங்க.", "TANGLISH", "INTRA_SENTENTIAL_CODE_SWITCH", "ACCEPTED", "MEDIUM", True, False, notes="Build cache failure")
        # Formal Technical Tanglish (7)
        add("Data loader pipeline multithreaded workers மூலமாக tokenized shards-ஐ stream செய்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="DataLoader streaming shards")
        add("Attention matrix softmax normalization token attention weights-ஐ compute செய்ய உதவுகிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Softmax attention weights")
        add("Gradient accumulation steps effective batch size-ஐ GPU memory limits-க்கு உட்பட கூட்டுகின்றன.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Gradient accumulation")
        add("Linear layer weight initialization variance exploding gradients-ஐ ஆரம்ப நிலையிலேயே தடுக்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Weight initialization")
        add("Residual connections deep neural network layers-ல் vanishing gradient problem-ஐ தீர்க்கின்றன.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Residual skip connections")
        add("Byte-Pair Encoding (BPE) subword segmentation algorithm rare words-ஐ character sequences-ஆ பிரிக்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="BPE subword algorithm")
        add("Cross-entropy validation loss early stopping mechanism மூலமாக model training-ஐ நிறைவு செய்கிறது.", "TANGLISH", "FORMAL_TECHNICAL_TANGLISH", "ACCEPTED", "HARD", True, False, notes="Early stopping loss")

    # =========================================================================
    # 4. OUT-OF-SCOPE LANGUAGES (10 records: Hindi, Telugu, Kannada, Malayalam)
    # =========================================================================
    if split_name == "dev":
        add("भारत एक विशाल और विविधताओं से भरा हुआ देश है जहां अनेक भाषाएं बोली जाती हैं।", "OUT_OF_SCOPE", "HINDI_PROSE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari")
        add("हिंदी साहित्य का इतिहास बहुत प्राचीन और समृद्ध माना जाता है।", "OUT_OF_SCOPE", "HINDI_LITERATURE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari")
        add("पर्यावरण की सुरक्षा हम सभी का नैतिक कर्तव्य और जिम्मेदारी है।", "OUT_OF_SCOPE", "HINDI_ENVIRONMENT", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari")
        add("తెలుగు భారతదేశంలో అత్యధికంగా మాట్లాడే భాషలలో ఒకటిగా గుర్తింపు పొందింది.", "OUT_OF_SCOPE", "TELUGU_PROSE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script")
        add("ఆంధ్రప్రదేశ్ మరియు తెలంగాణ రాష్ట్రాల అధికారిక భాషగా తెలుగు ఉంది.", "OUT_OF_SCOPE", "TELUGU_OFFICIAL", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script")
        add("ప్రకృతి వనరులను సద్వినియోగం చేసుకోవడం భవిష్యత్ తరాలకు ఎంతో అవసరం.", "OUT_OF_SCOPE", "TELUGU_ECOLOGY", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script")
        add("ಕನ್ನಡ ಸಾಹಿತ್ಯವು ಅತ್ಯಂತ ಪ್ರಾಚೀನ ಮತ್ತು ಸಮೃದ್ಧ ಇತಿಹಾಸವನ್ನು ಹೊಂದಿದೆ.", "OUT_OF_SCOPE", "KANNADA_LITERATURE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: KANNADA"], "Kannada script")
        add("ಬೆಂಗಳೂರು ಭಾರತದ ಪ್ರಮುಖ ಮಾಹಿತಿ ತಂತ್ರಜ್ಞಾನ ಕೇಂದ್ರವಾಗಿ ಬೆಳೆದಿದೆ.", "OUT_OF_SCOPE", "KANNADA_TECH", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: KANNADA"], "Kannada script")
        add("മലയാള ഭാഷ ദക്ഷിണേന്ത്യയിലെ പ്രധാനപ്പെട്ട ദ്രാവിഡ ഭാഷകളിൽ ഒന്നാണ്.", "OUT_OF_SCOPE", "MALAYALAM_PROSE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: MALAYALAM"], "Malayalam script")
        add("കേരളം പ്രകൃതിഭംഗി കൊണ്ടും സാംസ്കാരിക പൈതൃകം കൊണ്ടും പ്രസിദ്ധമാണ്.", "OUT_OF_SCOPE", "MALAYALAM_CULTURE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: MALAYALAM"], "Malayalam script")
    elif split_name == "val":
        add("वैज्ञानिक दृष्टिकोण अपनाने से समाज में अंधविश्वास और कुरीतियां समाप्त होती हैं।", "OUT_OF_SCOPE", "HINDI_SCIENCE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi scientific outlook")
        add("शिक्षा मनुष्य को आत्मनिर्भर बनाने के साथ-साथ समाज का एक जिम्मेदार नागरिक बनाती है।", "OUT_OF_SCOPE", "HINDI_EDUCATION", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi education")
        add("सौर ऊर्जा का उपयोग करके हम बिजली की बचत कर सकते हैं और पर्यावरण सुरक्षित रख सकते हैं।", "OUT_OF_SCOPE", "HINDI_ENERGY", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi solar power")
        add("హైదరాబాద్ నగరం చారిత్రక కట్టడాలు మరియు ఐటీ పరిశ్రమలకు కేంద్రంగా ప్రసిద్ధి చెందింది.", "OUT_OF_SCOPE", "TELUGU_CITY", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu Hyderabad IT")
        add("రైతులు దేశానికి వెన్నెముక వంటి వారు, వ్యవసాయం ఆర్థిక వ్యవస్థకు ముఖ్యమైన ఆధారం.", "OUT_OF_SCOPE", "TELUGU_AGRI", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu agriculture")
        add("సంగీతం మరియు నాట్య కళలు మనుషుల మానసిక ఉల్లాసానికి ఎంతగానో దోహదపడతాయి.", "OUT_OF_SCOPE", "TELUGU_ARTS", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu fine arts")
        add("ಕರ್ನಾಟಕದ ಕರಾವಳಿ ತೀರವು ನೈಸರ್ಗಿಕ ಸೌಂದರ್ಯ ಮತ್ತು ಪ್ರಾಚೀನ ದೇವಾಲಯಗಳಿಗೆ ಹೆಸರುವಾಸಿಯಾಗಿದೆ.", "OUT_OF_SCOPE", "KANNADA_COASTAL", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: KANNADA"], "Kannada coastal beauty")
        add("ವಿದ್ಯಾರ್ಥಿಗಳು ಶ್ರದ್ಧೆಯಿಂದ ಅಧ್ಯಯನ ಮಾಡಿ ತಮ್ಮ ಭವಿಷ್ಯವನ್ನು ಉಜ್ವಲಗೊಳಿಸಬೇಕು.", "OUT_OF_SCOPE", "KANNADA_EDUCATION", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: KANNADA"], "Kannada student study")
        add("ആരോഗ്യസംരക്ഷണത്തിന് ശുദ്ധമായ കുടിവെള്ളവും സമീകൃതാഹാരവും വളരെ അത്യാവശ്യമാണ്.", "OUT_OF_SCOPE", "MALAYALAM_HEALTH", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: MALAYALAM"], "Malayalam health water")
        add("വിദ്യാഭ്യാസ രംഗത്ത് കേരളം രാജ്യത്ത് ഏറ്റവും മുൻപന്തിയിൽ നിൽക്കുന്ന സംസ്ഥാനമാണ്.", "OUT_OF_SCOPE", "MALAYALAM_EDUCATION", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: MALAYALAM"], "Malayalam education rank")
    else:  # test split
        add("राष्ट्रीय एकता और अखंडता को बनाए रखना प्रत्येक भारतीय नागरिक का परम धर्म है।", "OUT_OF_SCOPE", "HINDI_NATIONAL", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi national unity")
        add("पुस्तकालय ज्ञान के भंडार होते हैं जहां सभी विषयों की महत्वपूर्ण पुस्तकें उपलब्ध रहती हैं।", "OUT_OF_SCOPE", "HINDI_LIBRARY", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi libraries")
        add("योग और प्राणायाम करने से शरीर निरोगी रहता है और मानसिक तनाव पूरी तरह दूर होता है।", "OUT_OF_SCOPE", "HINDI_YOGA", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi yoga meditation")
        add("సాంకేతిక రంగంలో నూతన ఆవిష్కరణలు మానవ జీవన విధానాన్ని సులభతరం చేస్తున్నాయి.", "OUT_OF_SCOPE", "TELUGU_TECH", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu tech innovation")
        add("భాష సంస్కృతిని ప్రతిబింబిస్తుంది, మన మాతృభాషను గౌరవించడం మన బాధ్యత.", "OUT_OF_SCOPE", "TELUGU_CULTURE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu mother tongue")
        add("వన సంరక్షణ ద్వారా మాత్రమే వాతావరణ సమతుల్యతను కాపాడటం సాధ్యమవుతుంది.", "OUT_OF_SCOPE", "TELUGU_FOREST", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu forest ecology")
        add("ಕೃಷಿ ಕ್ಷೇತ್ರದ ಸುಸ್ಥಿರ ಅಭಿವೃದ್ಧಿಗೆ ಆಧುನಿಕ ನೀರಾವರಿ ಪದ್ಧತಿಗಳು ಅತ್ಯಗತ್ಯವಾಗಿವೆ.", "OUT_OF_SCOPE", "KANNADA_AGRI", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: KANNADA"], "Kannada modern irrigation")
        add("ಕನ್ನಡ ಭಾಷೆಯ ಶ್ರೀಮಂತಿಕೆಯನ್ನು ಉಳಿಸಿ ಬೆಳೆಸಲು ಸಾಹಿತ್ಯ ಸಮ್ಮೇಳನಗಳು ಸಹಕಾರಿಯಾಗಿವೆ.", "OUT_OF_SCOPE", "KANNADA_LANGUAGE", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: KANNADA"], "Kannada literary meet")
        add("പരിസ്ഥിതി സംരക്ഷണം വരുംതലമുറയ്ക്കായുള്ള നമ്മുടെ പ്രധാന കടമകളിൽ ഒന്നാണ്.", "OUT_OF_SCOPE", "MALAYALAM_ECOLOGY", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: MALAYALAM"], "Malayalam ecology conservation")
        add("സാഹിത്യവും കലകളും മനുഷ്യന്റെ സൗന്ദര്യബോധത്തെ ഉണർത്താൻ സഹായിക്കുന്നു.", "OUT_OF_SCOPE", "MALAYALAM_ARTS", "REJECTED", "EASY", True, False, ["OUT_OF_SCOPE_LANGUAGE: MALAYALAM"], "Malayalam arts aesthetic")

    # =========================================================================
    # 5. UNICODE EDGE CASES & ADVERSARIAL (10 records)
    # =========================================================================
    # 5 Legitimate (ACCEPTED) + 5 Adversarial (REJECTED)
    if split_name == "dev":
        add("கா கி கீ கு கூ கெ கே கை கொ கோ கௌ ஆகிய உயிர்மெய் எழுத்துக்கள் சரியாக பராமரிக்கப்பட வேண்டும்.", "TAMIL", "UNICODE_VOWEL_SIGNS", "ACCEPTED", "MEDIUM", True, False, notes="11 Tamil vowel signs preserved")
        add("மெய்யெழுத்துக்கள் க் ங் ச் ஞ் ட் ண் த் ந் ப் ம் ய் ர் ல் வ் ழ் ள் ற் ன் புள்ளி எழுத்துக்கள் ஆகும்.", "TAMIL", "UNICODE_VIRAMA_SERIES", "ACCEPTED", "MEDIUM", True, False, notes="18 pulli virama consonants")
        add("தமிழ் எண்கள் ௧ ௨ ௩ ௪ ௫ ௬ ௭ ௮ ௯ ௰ ஆவணங்களில் பாதுகாப்பாக பராமரிக்கப்படுகின்றன.", "TAMIL", "UNICODE_NUMERALS", "ACCEPTED", "MEDIUM", True, False, notes="Tamil traditional digits")
        add("ஸ்ரீ ராமன் மற்றும் கிரந்த எழுத்துக்கள் ஜ, ஷ, ஸ, ஹ, க்ஷ பயன்பாட்டில் உள்ளன.", "TAMIL", "UNICODE_GRANTHA", "ACCEPTED", "MEDIUM", True, False, notes="Grantha characters")
        add("க்\u200Dக மற்றும் க்\u200Cக போன்ற ZWJ மற்றும் ZWNJ குறியீடுகள் ரெண்டரிங்கில் பாதுகாக்கப்படுகின்றன.", "TAMIL", "UNICODE_JOINERS", "ACCEPTED", "HARD", True, False, notes="ZWJ and ZWNJ ligatures")
        # Adversarial (REJECTED)
        add("க்் இரட்டைப் புள்ளி உள்ள பிழையான சொல் திருத்தப்பட வேண்டும்.", "TAMIL", "ADVERSARIAL_DOUBLE_VIRAMA", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Double virama sequence")
        add("\u0BBE தனித்த உயிர்மெய்க் குறியீடு வாக்கியத்தின் தொடக்கத்தில் பிழையானது.", "TAMIL", "ADVERSARIAL_LONE_COMBINING", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Lone vowel sign U+0BBE")
        add("This record contains corrupted bytes \uFFFD in stream causing strict encoding rejection.", "ENGLISH", "ADVERSARIAL_REPLACEMENT_CHAR", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Replacement char U+FFFD")
        add("Data corruption \uFFFD occurred during transmission across unverified socket channel.", "ENGLISH", "ADVERSARIAL_REPLACEMENT_CHAR", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Replacement char U+FFFD second instance")
        add("த்் தவறான மெய்க்குறியீடு வரிசை சரிபார்க்கப்பட வேண்டும்.", "TAMIL", "ADVERSARIAL_DOUBLE_VIRAMA", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Double virama on tha")
    elif split_name == "val":
        add("பா பி பீ பு பூ பெ பே பை பொ போ பௌ அனைத்து பா வரிசை உயிர்மெய் எழுத்துக்களும் உள்ளன.", "TAMIL", "UNICODE_VOWEL_SIGNS", "ACCEPTED", "MEDIUM", True, False, notes="Pa vowel signs series")
        add("வல்லினம் மெல்லினம் இடையினம் க் ச் ட் த் ப் ற் எழுத்துக்கள் முறையாக அமைக்கப்பட்டுள்ளன.", "TAMIL", "UNICODE_VIRAMA_SERIES", "ACCEPTED", "MEDIUM", True, False, notes="Vallinam consonants with pulli")
        add("பழங்கால கணக்கு வழக்குகளில் ௱ மற்றும் ௲ ஆகிய தமிழ் நூறு மற்றும் ஆயிரம் எண்கள் வழங்கின.", "TAMIL", "UNICODE_NUMERALS", "ACCEPTED", "HARD", True, False, notes="Tamil 100 and 1000 numerals")
        add("ரிஷப ராசி மற்றும் கஜமுகன் போன்ற கிரந்த சொற்கள் தமிழ் உரைநடையில் பயன்படுகின்றன.", "TAMIL", "UNICODE_GRANTHA", "ACCEPTED", "MEDIUM", True, False, notes="Grantha religious vocabulary")
        add("தமிழ் உரை\u200Dநடை மற்றும் சொல்\u200Cவளம் சீராக பராமரிக்கப்பட வேண்டும்.", "TAMIL", "UNICODE_JOINERS", "ACCEPTED", "HARD", True, False, notes="NFC joiner preservation")
        # Adversarial (REJECTED)
        add("ப்் இரட்டைப் புள்ளி வரிசை நிராகரிக்கப்பட வேண்டும்.", "TAMIL", "ADVERSARIAL_DOUBLE_VIRAMA", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Double virama on pa")
        add("\u0BC0 தனித்த நெடில் குறியீடு சொல் தொடக்கத்தில் அமையக்கூடாது.", "TAMIL", "ADVERSARIAL_LONE_COMBINING", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Lone vowel sign U+0BC0")
        add("Network socket stream received invalid surrogate \uFFFD replacement byte entity.", "ENGLISH", "ADVERSARIAL_REPLACEMENT_CHAR", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "U+FFFD replacement entity")
        add("Database transaction log corrupted with \uFFFD invalid Unicode codepoint marker.", "ENGLISH", "ADVERSARIAL_REPLACEMENT_CHAR", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "U+FFFD in DB log")
        add("ச்் இரட்டைப் புள்ளி உள்ள பிழையான சொல் அச்சுக்கோர்ப்பில் தவிர்க்கப்பட வேண்டும்.", "TAMIL", "ADVERSARIAL_DOUBLE_VIRAMA", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Double virama on cha")
    else:  # test split
        add("தா தி தீ து தூ தெ தே தை தொ தோ தௌ ஆகிய உயிர்மெய் வரிசைகள் சரியாக உள்ளன.", "TAMIL", "UNICODE_VOWEL_SIGNS", "ACCEPTED", "MEDIUM", True, False, notes="Tha vowel signs series")
        add("மெய்யெழுத்துக்களின் ஒலிப்பு முறைகள் ங் ஞ் ண் ந் ம் ன் மெல்லின எழுத்துக்களில் தெளிவாகின்றன.", "TAMIL", "UNICODE_VIRAMA_SERIES", "ACCEPTED", "MEDIUM", True, False, notes="Mellinam consonants with pulli")
        add("கல்வெட்டுகளில் ௧௫ மற்றும் ௨௦ போன்ற தமிழ் எண் குறியீடுகள் பொறிக்கப்பட்டுள்ளன.", "TAMIL", "UNICODE_NUMERALS", "ACCEPTED", "HARD", True, False, notes="Tamil compound numerals")
        add("புஷ்பம் மற்றும் சந்தோஷம் போன்ற சொற்களில் கிரந்த எழுத்துக்கள் நிறைந்துள்ளன.", "TAMIL", "UNICODE_GRANTHA", "ACCEPTED", "MEDIUM", True, False, notes="Grantha words")
        add("கணினி\u200Dவலையமைப்பு மற்றும் தரவு\u200Cத்தளம் ரெண்டரிங் பாதுகாக்கப்படுகிறது.", "TAMIL", "UNICODE_JOINERS", "ACCEPTED", "HARD", True, False, notes="Rendering joiners test")
        # Adversarial (REJECTED)
        add("ம்் இரட்டைப் புள்ளி சொல் பிழையாக பதியப்பட்டுள்ளது.", "TAMIL", "ADVERSARIAL_DOUBLE_VIRAMA", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Double virama on ma")
        add("\u0BCA தனித்த ஒற்றைக் கொம்பு குறியீடு சொல் தொடக்கத்தில் பிழையானது.", "TAMIL", "ADVERSARIAL_LONE_COMBINING", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Lone vowel sign U+0BCA")
        add("Incoming message packet failed decoding with replacement character \uFFFD detected.", "ENGLISH", "ADVERSARIAL_REPLACEMENT_CHAR", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Packet decoding replacement char")
        add("Storage sector sector dump contains corrupted \uFFFD unmapped character symbol.", "ENGLISH", "ADVERSARIAL_REPLACEMENT_CHAR", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Storage corruption U+FFFD")
        add("ல்் இரட்டைப் புள்ளி சொல் நிராகரிக்கப்பட வேண்டிய ஒன்றாகும்.", "TAMIL", "ADVERSARIAL_DOUBLE_VIRAMA", "REJECTED", "ADVERSARIAL", False, False, ["MALFORMED_UNICODE"], "Double virama on la")

    # =========================================================================
    # 6. LOW-QUALITY & MALFORMED TEXT (5 records)
    # =========================================================================
    if split_name == "dev":
        add("", "UNKNOWN", "EMPTY_RECORD", "REJECTED", "EASY", False, False, ["EMPTY_RECORD"], "Completely empty string")
        add("Hi ok", "ENGLISH", "TOO_SHORT", "REJECTED", "EASY", False, False, ["TOO_SHORT"], "Under 10 characters")
        add("a" * 80, "UNKNOWN", "REPEATED_CHAR_SPAM", "REJECTED", "EASY", False, False, ["TOO_FEW_WORDS", "REPEATED_CHAR_SPAM"], "80 consecutive 'a' characters")
        add("https://site.com/a https://site.com/b https://site.com/c https://site.com/d https://site.com/e more links https://site.com/f", "ENGLISH", "URL_HEAVY", "REJECTED", "MEDIUM", False, False, ["URL_HEAVY"], "High URL density")
        add("??? !!! .... ,,,, :::: ;;;; ??? !!! .... ,,,, :::: ;;;;", "UNKNOWN", "EXCESSIVE_PUNCTUATION", "REJECTED", "EASY", False, False, ["TOO_FEW_WORDS", "EXCESSIVE_PUNCTUATION", "NO_ALPHABETIC_CHARS"], "Punctuation spam")
    elif split_name == "val":
        add("   \t\n  ", "UNKNOWN", "WHITESPACE_ONLY", "REJECTED", "EASY", False, False, ["EMPTY_RECORD"], "Whitespace and tabs only")
        add("வா போ", "TAMIL", "TOO_SHORT_TAMIL", "REJECTED", "EASY", False, False, ["TOO_SHORT"], "Under 10 characters Tamil")
        add("ஹ" * 40, "TAMIL", "REPEATED_CHAR_SPAM_TAMIL", "REJECTED", "EASY", False, False, ["TOO_FEW_WORDS", "REPEATED_CHAR_SPAM"], "40 consecutive 'ஹ' characters")
        add("http://link1.org/test http://link2.org/test http://link3.org/test http://link4.org/test http://link5.org/test url list", "ENGLISH", "URL_HEAVY", "REJECTED", "MEDIUM", False, False, ["URL_HEAVY"], "URL heavy payload")
        add("1234567890 9876543210 1122334455", "UNKNOWN", "NO_ALPHABETIC_CHARS", "REJECTED", "EASY", False, False, ["NO_ALPHABETIC_CHARS"], "Digits only text")
    else:  # test split
        add("          ", "UNKNOWN", "WHITESPACE_ONLY", "REJECTED", "EASY", False, False, ["EMPTY_RECORD"], "Spaces only")
        add("Good", "ENGLISH", "TOO_SHORT", "REJECTED", "EASY", False, False, ["TOO_SHORT", "TOO_FEW_WORDS"], "Single 4-letter word")
        add("z" * 90, "UNKNOWN", "REPEATED_CHAR_SPAM", "REJECTED", "EASY", False, False, ["TOO_FEW_WORDS", "REPEATED_CHAR_SPAM"], "90 consecutive 'z' characters")
        add("https://alpha.io https://beta.io https://gamma.io https://delta.io https://epsilon.io https://zeta.io spam links", "ENGLISH", "URL_HEAVY", "REJECTED", "MEDIUM", False, False, ["URL_HEAVY"], "URL link farm")
        add("!@#$%^&*()_+=-`~[]{}|;:',.<>/?", "UNKNOWN", "NO_ALPHABETIC_CHARS", "REJECTED", "EASY", False, False, ["TOO_FEW_WORDS", "EXCESSIVE_PUNCTUATION", "NO_ALPHABETIC_CHARS"], "Symbols only text")

    # =========================================================================
    # 7. DUPLICATES (5 records within this split)
    # =========================================================================
    # Referencing records 1, 21, 41 of this split
    base_tamil = records[0]["text"]
    base_english = records[20]["text"]
    base_tanglish = records[40]["text"]

    # Exact Duplicates (2)
    add(base_tamil, "TAMIL", "EXACT_DUPLICATE_TAMIL", "DUPLICATE_FLAGGED", "EASY", True, True, ["DUPLICATE_EXACT"], f"Exact duplicate of {prefix}-0001")
    add(base_english, "ENGLISH", "EXACT_DUPLICATE_ENGLISH", "DUPLICATE_FLAGGED", "EASY", True, True, ["DUPLICATE_EXACT"], f"Exact duplicate of {prefix}-0021")

    # Normalized Duplicates (2)
    add("   " + base_tamil + "  \n", "TAMIL", "NORMALIZED_DUPLICATE_TAMIL", "DUPLICATE_FLAGGED", "MEDIUM", True, True, ["DUPLICATE_NORMALIZED"], f"Whitespace variant of {prefix}-0001")
    add("  " + base_english.upper() + "  ", "ENGLISH", "NORMALIZED_DUPLICATE_ENGLISH", "DUPLICATE_FLAGGED", "MEDIUM", True, True, ["DUPLICATE_NORMALIZED"], f"Uppercase and whitespace variant of {prefix}-0021")

    # Near Duplicate (1: Jaccard ~0.85)
    add(base_tanglish + " nalla irukku thala.", "TANGLISH", "NEAR_DUPLICATE_TANGLISH", "DUPLICATE_FLAGGED", "HARD", True, True, ["DUPLICATE_NEAR_DUPLICATE"], f"Near duplicate of {prefix}-0041 with minor appended phrase")

    return records

def generate_splits():
    dev_records = build_split("dev", "P26-DEV", seed_offset=100)
    val_records = build_split("val", "P26-VAL", seed_offset=200)
    test_records = build_split("test", "P26-TEST", seed_offset=300)

    dataset_package = {
        "benchmark_version": "IGRIS-P26-BENCHMARK-V1.0",
        "description": "Standardized 3-way evaluation benchmark for IGRIS language engineering infrastructure",
        "splits_summary": {
            "dev_count": len(dev_records),
            "val_count": len(val_records),
            "test_count": len(test_records),
            "total_records": len(dev_records) + len(val_records) + len(test_records),
        },
        "splits": {
            "dev": dev_records,
            "val": val_records,
            "test": test_records,
        }
    }

    OUT_JSON.write_text(json.dumps(dataset_package, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {OUT_JSON} with 3 non-overlapping splits (300 records total).")

    # Also write to artifacts directory
    artifact_path = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102") / "PHASE26_DATASET_SPLITS.json"
    artifact_path.write_text(json.dumps(dataset_package, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Copied to artifact directory: {artifact_path}")

if __name__ == "__main__":
    generate_splits()
