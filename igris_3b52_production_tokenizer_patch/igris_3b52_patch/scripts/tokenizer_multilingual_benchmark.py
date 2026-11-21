"""IGRIS Phase 15 — Standardized Multilingual Tokenizer Benchmark Suite.

Provides standardized, reproducible text samples across 11 evaluation categories:
  1. English (en)
  2. Hindi (hi)
  3. Tamil (ta)
  4. Telugu (te)
  5. Malayalam (ml)
  6. Kannada (kn)
  7. Bengali (bn)
  8. Gujarati (gu)
  9. Tanglish (tanglish)
 10. Code-Switching (multilingual mixing)
 11. Robustness & Unknown (edge cases, adversarial repetition, symbols, foreign scripts)

All text samples are synthetic or public domain benchmarks. No production datasets,
quarantine files, or private corpora are accessed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class BenchmarkSample:
    sample_id: str
    category: str
    language_code: str
    description: str
    text: str


BENCHMARK_SAMPLES: list[BenchmarkSample] = [
    # -------------------------------------------------------------------------
    # 1. ENGLISH (en)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="en_01",
        category="English",
        language_code="en",
        description="Standard expository English prose on computing architectures",
        text=(
            "The IGRIS multilingual decoder-only transformer architecture is designed with 16 layers, "
            "8 attention heads, and 4 key-value heads using grouped-query attention. It operates over a "
            "2048-token context window with rotary position embeddings for stable sequence modeling."
        ),
    ),
    BenchmarkSample(
        sample_id="en_02",
        category="English",
        language_code="en",
        description="Complex English syntax with formal vocabulary and punctuation",
        text=(
            "Notwithstanding the initial latency constraints, the distributed training framework "
            "demonstrated exemplary convergence rates; furthermore, gradient synchronization overhead "
            "remained negligible across high-bandwidth interconnect topologies."
        ),
    ),
    BenchmarkSample(
        sample_id="en_03",
        category="English",
        language_code="en",
        description="Technical documentation and configuration parameters",
        text=(
            "Configuration summary: batch_size=32, learning_rate=3e-4, weight_decay=0.01, "
            "warmup_steps=2000, adam_beta1=0.9, adam_beta2=0.95, and grad_clip=1.0."
        ),
    ),
    BenchmarkSample(
        sample_id="en_04",
        category="English",
        language_code="en",
        description="Colloquial English dialogue and contraction handling",
        text=(
            "Hey, aren't you coming to the tech sync today? I've been reviewing the PR, "
            "and we're definitely going to need a quick huddle before deploying to staging."
        ),
    ),

    # -------------------------------------------------------------------------
    # 2. HINDI (hi)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="hi_01",
        category="Hindi",
        language_code="hi",
        description="Formal Devanagari Hindi prose on technological progress",
        text=(
            "नमस्ते! कृत्रिम बुद्धिमत्ता और प्राकृतिक भाषा प्रसंस्करण के क्षेत्र में भारतीय भाषाओं का विकास "
            "अत्यंत तीव्र गति से हो रहा है। बहुभाषी मॉडल ज्ञान और सूचना तक सबकी पहुँच को सरल बनाते हैं।"
        ),
    ),
    BenchmarkSample(
        sample_id="hi_02",
        category="Hindi",
        language_code="hi",
        description="Official administrative Hindi with complex conjuncts and nuktas",
        text=(
            "सार्वजनिक उपक्रमों तथा स्वायत्त संस्थाओं में पारदर्शी शासन व्यवस्था सुनिश्चित करने के लिए "
            "डिजिटल प्रणालियों का प्रभावी क्रियान्वयन अनिवार्य कर दिया गया है। सभी संबंधित विभाग दिशा-निर्देशों का पालन करें।"
        ),
    ),
    BenchmarkSample(
        sample_id="hi_03",
        category="Hindi",
        language_code="hi",
        description="Conversational Hindi with mixed vocabulary and numerals",
        text=(
            "आज शाम को लगभग ५:३० बजे हमारी बैठक तय हुई है। क्या आप समय पर पहुँच सकेंगे? "
            "कृपया अपनी प्रस्तुति की फ़ाइल पहले से साझा कर दें ताकि समय की बचत हो सके।"
        ),
    ),

    # -------------------------------------------------------------------------
    # 3. TAMIL (ta)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="ta_01",
        category="Tamil",
        language_code="ta",
        description="Classical Tamil commentary and philosophical prose",
        text=(
            "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு. கற்றதனால் ஆய பயன்கொல் வாலறிவன் "
            "நற்றாள் தொழாஅர் எனின். எழுத்துக்கள் எல்லாம் அகரத்தை முதலாகக் கொண்டுள்ளன; "
            "அதுபோல உலகம் கடவுளை முதலாகக் கொண்டுள்ளது."
        ),
    ),
    BenchmarkSample(
        sample_id="ta_02",
        category="Tamil",
        language_code="ta",
        description="Modern formal Tamil journalism and public discourse",
        text=(
            "செயற்கை நுண்ணறிவுத் தொழில்நுட்பம் உலகெங்கிலும் உள்ள பல்வேறு துறைகளில் புரட்சிகரமான "
            "மாற்றங்களை ஏற்படுத்தி வருகிறது. குறிப்பாக கல்வி, மருத்துவம், மற்றும் விண்வெளி ஆய்வுகளில் "
            "மொழி மாதிரிகளின் பயன்பாடு நாளுக்கு நாள் அதிகரித்து வருகிறது."
        ),
    ),
    BenchmarkSample(
        sample_id="ta_03",
        category="Tamil",
        language_code="ta",
        description="Agglutinative Tamil morphology with complex suffix inflections",
        text=(
            "அவர்களுடையவற்றிலிருந்து பிரித்தெடுக்கப்பட்டவற்றை முறையாகப் பகுப்பாய்வு செய்து, "
            "அவற்றின் மூலக்கூறுகளையெல்லாம் வகைப்படுத்துவதனால் மட்டுமே உண்மையான முடிவுகளைப் பெறமுடியும்."
        ),
    ),
    BenchmarkSample(
        sample_id="ta_04",
        category="Tamil",
        language_code="ta",
        description="Technical Tamil vocabulary for computer science and data structures",
        text=(
            "நினைவக ஒதுக்கீடு, தரவுத்தள அட்டவணைகள், வலையமைப்பு இணைப்புகள், மற்றும் பல்கூறுச்செயலாக்கம் "
            "போன்ற கணினி அறிவியல் கோட்பாடுகள் நவீன இயங்குதளங்களில் மிகக் கவனமாக வடிவமைக்கப்படுகின்றன."
        ),
    ),

    # -------------------------------------------------------------------------
    # 4. TELUGU (te)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="te_01",
        category="Telugu",
        language_code="te",
        description="Modern Telugu prose on cultural heritage and literature",
        text=(
            "నమస్కారం! తెలుగు భారతదేశంలో అత్యంత ప్రాచీనమైన మరియు శ్రావ్యమైన ద్రావిడ భాషలలో ఒకటి. "
            "ఆంధ్రప్రదేశ్ మరియు తెలంగాణ రాష్ట్రాలలో ఇది అధికారిక భాషగా గుర్తింపు పొందింది."
        ),
    ),
    BenchmarkSample(
        sample_id="te_02",
        category="Telugu",
        language_code="te",
        description="Telugu technical and administrative prose with conjunct wattulu",
        text=(
            "సమాచార సాంకేతిక పరిజ్ఞానం గ్రామీణ ప్రాంతాల అభివృద్ధికి సరికొత్త మార్గాలను సుగమం చేస్తోంది. "
            "డిజిటల్ సేవలు ప్రజలకు పారదర్శకంగా మరియు సమర్థవంతంగా అందుబాటులోకి వస్తున్నాయి."
        ),
    ),
    BenchmarkSample(
        sample_id="te_03",
        category="Telugu",
        language_code="te",
        description="Conversational Telugu with numbers and punctuation",
        text=(
            "రేపు ఉదయం 10 గంటలకు కార్యాలయంలో ముఖ్యమైన సమీక్ష సమావేశం జరుగుతుంది. "
            "అందరూ సమయానికి హాజరై తమ నివేదికలను సమర్పించాలని కోరడమైనది."
        ),
    ),

    # -------------------------------------------------------------------------
    # 5. MALAYALAM (ml)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="ml_01",
        category="Malayalam",
        language_code="ml",
        description="Formal Malayalam prose with chillu characters and ligatures",
        text=(
            "മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്. കേരളത്തിലും ലക്ഷദ്വീപിലും പുതുച്ചേരിയുടെ ഭാഗമായ മാഹിയിലും "
            "ഇത് പ്രധാനമായും സംസാരിക്കപ്പെടുന്നു. സാഹിത്യ സമ്പന്നതയാൽ അനുഗൃഹീതമാണ് ഈ മനോഹര ഭാഷ."
        ),
    ),
    BenchmarkSample(
        sample_id="ml_02",
        category="Malayalam",
        language_code="ml",
        description="Malayalam technical journalism with complex consonant clusters",
        text=(
            "ശാസ്ത്ര സാങ്കേതിക വിദ്യയുടെ വളർച്ച മനുഷ്യജീവിതത്തിൽ വരുത്തിയ മാറ്റങ്ങൾ അഭൂതപൂർവ്വമാണ്. "
            "കംപ്യൂട്ടർ സാങ്കേതികവിദ്യയും ആർട്ടിഫിഷ്യൽ ഇന്റലിജൻസും പുത്തൻ സാധ്യതകൾ തുറന്നിടുന്നു."
        ),
    ),
    BenchmarkSample(
        sample_id="ml_03",
        category="Malayalam",
        language_code="ml",
        description="Conversational Malayalam with numerals and punctuation",
        text=(
            "നാളെ വൈകുന്നേരം 4 മണിക്ക് നടക്കുന്ന ചർച്ചയിൽ പങ്കെടുക്കാൻ താങ്കൾക്ക് സാധിക്കുമോ? "
            "വിശദമായ വിവരങ്ങൾ അടങ്ങിയ രേഖകൾ ഇതിനകം ഇമെയിൽ വഴി അയച്ചിട്ടുണ്ട്."
        ),
    ),

    # -------------------------------------------------------------------------
    # 6. KANNADA (kn)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="kn_01",
        category="Kannada",
        language_code="kn",
        description="Standard Kannada prose on state history and literature",
        text=(
            "ಕನ್ನಡವು ಭಾರತದ ಕರ್ನಾಟಕ ರಾಜ್ಯದ ಅಧಿಕೃತ ಮತ್ತು ಪ್ರಮುಖ ಭಾಷೆಯಾಗಿದೆ. "
            "ಸಾವಿರಾರು ವರ್ಷಗಳ ಶ್ರೀಮಂತ ಇತಿಹಾಸ ಮತ್ತು ಸಾಹಿತ್ಯ ಪರಂಪರೆಯನ್ನು ಹೊಂದಿರುವ ಈ ಭಾಷೆಗೆ ಶಾಸ್ತ್ರೀಯ ಸ್ಥಾನಮಾನವಿದೆ."
        ),
    ),
    BenchmarkSample(
        sample_id="kn_02",
        category="Kannada",
        language_code="kn",
        description="Kannada technical and administrative text with consonant ottu forms",
        text=(
            "ಮಾಹಿತಿ ತಂತ್ರಜ್ಞಾನ ಕ್ಷೇತ್ರದ ನವೀನ ಆವಿಷ್ಕಾರಗಳು ಸಾರ್ವಜನಿಕ ಸೇವೆಗಳ ವಿತರಣೆಯನ್ನು ಅತ್ಯಂತ ಸರಳಗೊಳಿಸಿವೆ. "
            "ಯುವ ಸಂಶೋಧಕರು ತಂತ್ರಜ್ಞಾನ ಆಧಾರಿತ ಪರಿಹಾರಗಳನ್ನು ರೂಪಿಸುವಲ್ಲಿ ಸಕ್ರಿಯರಾಗಿದ್ದಾರೆ."
        ),
    ),
    BenchmarkSample(
        sample_id="kn_03",
        category="Kannada",
        language_code="kn",
        description="Everyday conversational Kannada with dates and numbers",
        text=(
            "ನಾಳೆ ಬೆಳಗ್ಗೆ 11:00 ಗಂಟೆಗೆ ನಡೆಯಲಿರುವ ಕಾರ್ಯಾಗಾರಕ್ಕೆ ಎಲ್ಲರೂ ತಪ್ಪದೆ ಆಗಮಿಸಿ. "
            "ಕಾರ್ಯಕ್ರಮದ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಈಗಾಗಲೇ ಎಲ್ಲರಿಗೂ ತಲುಪಿಸಲಾಗಿದೆ."
        ),
    ),

    # -------------------------------------------------------------------------
    # 7. BENGALI (bn)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="bn_01",
        category="Bengali",
        language_code="bn",
        description="Literary Bengali prose reflecting standard cultural discourse",
        text=(
            "বাংলা ভাষা একটি সমৃদ্ধ ইন্দো-আর্য ভাষা যা দক্ষিণ এশিয়ার বাঙালি জনগণের প্রধান মাতৃভাষা। "
            "রবীন্দ্রনাথ ঠাকুর ও কাজী নজরুল ইসলামের অমর সৃষ্টি বাংলা সাহিত্যকে বিশ্বদরবারে সম্মানিত করেছে।"
        ),
    ),
    BenchmarkSample(
        sample_id="bn_02",
        category="Bengali",
        language_code="bn",
        description="Bengali technological and educational prose with complex yuktakshar",
        text=(
            "কৃত্রিম বুদ্ধিমত্তা এবং তথ্যপ্রযুক্তির ক্রমবিকাশ বর্তমান বিশ্বে এক বিশাল রূপান্তর এনেছে। "
            "শিক্ষাব্যবস্থায় আধুনিক প্রযুক্তির সংমিশ্রণ শিক্ষার্থীদের জ্ঞানার্জনের দিগন্তকে প্রসারিত করছে।"
        ),
    ),
    BenchmarkSample(
        sample_id="bn_03",
        category="Bengali",
        language_code="bn",
        description="Conversational Bengali with numbers and temporal markers",
        text=(
            "আগামীকাল দুপুর ২:৩০ মিনিটে আমাদের নতুন প্রকল্প নিয়ে একটি বিস্তারিত আলোচনা সভা অনুষ্ঠিত হবে। "
            "অনুগ্রহ করে যথাসময়ে উপস্থিত থাকবেন।"
        ),
    ),

    # -------------------------------------------------------------------------
    # 8. GUJARATI (gu)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="gu_01",
        category="Gujarati",
        language_code="gu",
        description="Standard Gujarati prose on commercial and cultural heritage",
        text=(
            "નમસ્તે! ગુજરાતી એ ભારત દેશના પશ્ચિમ ભાગમાં આવેલા ગુજરાત રાજ્યની મુખ્ય અને અધિકૃત ભાષા છે. "
            "તેનો સમૃદ્ધ સાહિત્યિક ઇતિહાસ અને વ્યાપારિક સંસ્કૃતિ વૈશ્વિક સ્તરે પ્રખ્યાત છે."
        ),
    ),
    BenchmarkSample(
        sample_id="gu_02",
        category="Gujarati",
        language_code="gu",
        description="Gujarati technical and educational text with matras and viramas",
        text=(
            "વિજ્ઞાન અને ટેક્નોલોજીના ક્ષેત્રમાં થઈ રહેલા નવા સંશોધનો માનવ જીવનને વધુ સુવિધાજનક બનાવી રહ્યા છે. "
            "ડિજિટલ ક્રાંતિ દ્વારા શિક્ષણ અને ઉદ્યોગ જગતમાં અભૂતપૂર્વ પરિવર્તન આવ્યું છે."
        ),
    ),
    BenchmarkSample(
        sample_id="gu_03",
        category="Gujarati",
        language_code="gu",
        description="Conversational Gujarati with monetary numbers and punctuation",
        text=(
            "આજે સાંજે ૬ વાગ્યે અમે નવી યોજના વિશે ચર્ચા કરવા માટે મળીશું. "
            "કુલ ખર્ચનો અંદાજ લગભગ રૂ. ૫૦,૦૦૦ જેટલો રહેશે."
        ),
    ),

    # -------------------------------------------------------------------------
    # 9. TANGLISH (tanglish)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="tanglish_01",
        category="Tanglish",
        language_code="tanglish",
        description="Colloquial conversational Tanglish with greeting and state inquiry",
        text=(
            "vanakkam nanba! epdi irukinga? romba naala aachu unga kooda pesi. "
            "innaiku evening namma tea shop la meet pannalama?"
        ),
    ),
    BenchmarkSample(
        sample_id="tanglish_02",
        category="Tanglish",
        language_code="tanglish",
        description="Tanglish informal tech and workplace discussion with English terms",
        text=(
            "machan, indha build romba slow ah irukku da. cache clear pannitu marubadiyum "
            "run pannu, kandippa speed aagum. release ku innum two days dhaan irukku."
        ),
    ),
    BenchmarkSample(
        sample_id="tanglish_03",
        category="Tanglish",
        language_code="tanglish",
        description="Tanglish orthographic variations and agglutinative Latin suffixes",
        text=(
            "namma office la pudhu project start pannanga. adhula AI integration irukku. "
            "velai ellam mudichutu seekiram veetuku poga vendiyadhu dhaan."
        ),
    ),

    # -------------------------------------------------------------------------
    # 10. CODE-SWITCHING (multilingual mixing)
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="codeswitch_01",
        category="Code-Switching",
        language_code="mixed",
        description="English-to-Tamil intra-sentential code-switching with transition punctuation",
        text=(
            "Welcome to Chennai! இந்த நகரம் கலை, கலாச்சாரம், மற்றும் IT நிறுவனங்களின் மையமாக திகழ்கிறது. "
            "You will find amazing food here."
        ),
    ),
    BenchmarkSample(
        sample_id="codeswitch_02",
        category="Code-Switching",
        language_code="mixed",
        description="English-to-Hindi intra-sentential technical code-switching",
        text=(
            "Machine Learning algorithms require massive compute power, लेकिन सही डेटा आर्किटेक्चर के बिना "
            "model convergence संभव नहीं है।"
        ),
    ),
    BenchmarkSample(
        sample_id="codeswitch_03",
        category="Code-Switching",
        language_code="mixed",
        description="Indic-to-English transition with mixed-script terminology",
        text=(
            "ನಮ್ಮ ಸಂಶೋಧನಾ ತಂಡವು deep learning frameworks ಬಳಸಿ ಹೊಸ NLP ಪರಿಹಾರಗಳನ್ನು ಅಭಿವೃದ್ಧಿಪಡಿಸುತ್ತಿದೆ. "
            "This achieves state-of-the-art results across benchmarks."
        ),
    ),
    BenchmarkSample(
        sample_id="codeswitch_04",
        category="Code-Switching",
        language_code="mixed",
        description="Telugu-English mixed dialogue with numbers and punctuation",
        text=(
            "రేపు జరిగే tech conference లో cloud computing and microservices గురించి మాట్లాడతాను. "
            "Please register before 5:00 PM today."
        ),
    ),

    # -------------------------------------------------------------------------
    # 11. ROBUSTNESS & UNKNOWN / EDGE CASES
    # -------------------------------------------------------------------------
    BenchmarkSample(
        sample_id="robust_01",
        category="Robustness",
        language_code="unknown",
        description="Adversarially repetitive characters and symbol bursts",
        text="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ????????????????????",
    ),
    BenchmarkSample(
        sample_id="robust_02",
        category="Robustness",
        language_code="unknown",
        description="High-density symbols, ASCII delimiters, and punctuation noise",
        text="<<<|>>> [[[---]]] {{{***}}} &&& ### $$$ @@@ ~~~ +++ === /// \\\\\\ ;;; :::: ,,,,",
    ),
    BenchmarkSample(
        sample_id="robust_03",
        category="Robustness",
        language_code="unknown",
        description="Emoji sequences and diverse multilingual Unicode pictographs",
        text="🚀 🤖 🇮🇳 ✨ 🌍 💻 📊 🔒 ⚙️ 🎯 Multi-emoji sequence for tokenizer resilience! 🎉",
    ),
    BenchmarkSample(
        sample_id="robust_04",
        category="Robustness",
        language_code="unknown",
        description="Non-target foreign scripts (Cyrillic, Arabic, CJK) testing byte fallback",
        text="Привет мир! مرحبا بالعالم! 你好世界! (Testing fallback encoding mechanisms)",
    ),
    BenchmarkSample(
        sample_id="robust_05",
        category="Robustness",
        language_code="en",
        description="Very long continuous document (repetition stress test)",
        text=("The IGRIS transformer tokenization pipeline processes sequences deterministically. " * 30),
    ),
]


def get_benchmark_categories() -> list[str]:
    """Return ordered list of unique benchmark categories."""
    seen = []
    for s in BENCHMARK_SAMPLES:
        if s.category not in seen:
            seen.append(s.category)
    return seen


def get_samples_for_category(category: str) -> list[BenchmarkSample]:
    """Retrieve all benchmark samples belonging to a specific category."""
    return [s for s in BENCHMARK_SAMPLES if s.category == category]
