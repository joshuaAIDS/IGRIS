#!/usr/bin/env python3
"""
Generates PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl
Comprehensive, reproducible synthetic benchmark dataset for Phase 25 (Exactly 150 records).
"""

import json
from pathlib import Path

PATCH_DIR = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch")
OUT_FILE = PATCH_DIR / "PHASE25_SYNTHETIC_BENCHMARK_FIXTURES.jsonl"

fixtures = []
cur_id = 1

def add_fixture(text, lang, category, q_pass, is_dup, action, reasons=None, notes=""):
    global cur_id
    rec_id = f"P25-SYN-{cur_id:04d}"
    cur_id += 1
    fixtures.append({
        "id": rec_id,
        "text": text,
        "ground_truth_language": lang,
        "category": category,
        "expected_quality_pass": q_pass,
        "expected_duplicate": is_dup,
        "expected_action": action,
        "expected_rejection_reasons": reasons or [],
        "notes": notes,
    })

# 1. Native Tamil Script Records (Clean) - 16 records
tamil_samples = [
    ("தமிழ் மொழியானது உலகின் மிகத் தொன்மையான செம்மொழிகளில் ஒன்றாகக் கருதப்படுகிறது.", "Literature/History"),
    ("இயற்கை வளங்களைப் பாதுகாப்பது நமது எதிர்கால சந்ததியினரின் நலனுக்கு மிகவும் இன்றியமையாதது ஆகும்.", "Environment/General"),
    ("கணினி அறிவியல் துறையில் செயற்கை நுண்ணறிவு மற்றும் இயந்திரக் கற்றல் பெரும் மாற்றங்களை ஏற்படுத்தி வருகின்றன.", "Technology"),
    ("அறிவியல் ஆராய்ச்சிகள் மனித சமுதாயத்தின் வளர்ச்சிக்கும் நல்வாழ்விற்கும் வழிவகுக்கின்றன.", "Science"),
    ("நூலகங்கள் அறிவின் களஞ்சியங்களாகவும் பண்பாட்டு மையங்களாகவும் திகழ்கின்றன.", "Education"),
    ("சூரிய குடும்பத்தில் பூமி மூன்றாவது கோளாகவும், உயிரினங்கள் வாழக்கூடிய ஒரே இடமாகவும் உள்ளது.", "Astronomy"),
    ("மருத்துவத் துறையில் புதிய தொழில்நுட்பங்களின் பயன்பாடு மனித ஆயுளை நீட்டிக்க உதவுகிறது.", "Healthcare"),
    ("தமிழ்நாட்டில் உள்ள தஞ்சைப் பெருவுடையார் கோயில் சோழர்களின் கட்டிடக்கலைக்கு ஒரு சிறந்த எடுத்துக்காட்டாகும்.", "Architecture"),
    ("விவசாயம் நாட்டின் பொருளாதாரத்தின் முதுகெலும்பாக விளங்குகிறது, உழவர்கள் உணவு உற்பத்தியில் முன்னிற்கின்றனர்.", "Agriculture"),
    ("தொல்காப்பியம் தமிழ் இலக்கணத்தின் மிகப்பழமையான நூலாக இன்றும் அறிஞர்களால் போற்றப்படுகிறது.", "Grammar"),
    ("நீர்வள மேலாண்மை எதிர்கால வறட்சியைத் தடுக்கவும் உணவுப் பாதுகாப்பை உறுதிப்படுத்தவும் அவசியம்.", "Ecology"),
    ("இணையத்தின் வருகை உலகளாவிய தொடர்புகளை எளிமையாக்கி தகவல்களை உடனடியாகப் பகிர உதவுகிறது.", "Internet"),
    ("காற்றாலை மின்சாரம் மற்றும் சூரிய ஒளி மின்சாரம் போன்ற புதுப்பிக்கத்தக்க ஆற்றல் உற்பத்தி அதிகரித்து வருகிறது.", "Energy"),
    ("வானிலை முன்னறிவிப்பு செயற்கைக்கோள் தரவுகளை அடிப்படையாகக் கொண்டு விவசாயிகளுக்கு முன்கூட்டியே வழங்கப்படுகிறது.", "Meteorology"),
    ("ஒவ்வொரு மனிதனும் மற்றவர்களின் கருத்துக்களை மதித்து அமைதியான சமுதாயத்தை உருவாக்க பாடுபட வேண்டும்.", "Ethics"),
    ("திருக்குறள் உலக மக்கள் அனைவருக்கும் பொதுவான வாழ்வியல் நெறிகளை எடுத்துரைக்கும் உன்னத நூல்.", "Philosophy"),
]
for text, cat in tamil_samples:
    add_fixture(text, "TAMIL", f"TAMIL_NATIVE_{cat.upper()}", True, False, "ACCEPTED", notes="Clean native Tamil prose")

# 2. English Records (Clean) - 16 records
english_samples = [
    ("The decoder-only transformer architecture forms the foundation of modern large language models.", "AI/ML"),
    ("Operating system processes manage virtual memory allocation and inter-process communication channels.", "Systems"),
    ("Cryptographic hash functions produce fixed-size deterministic digests from arbitrary input byte streams.", "Security"),
    ("Distributed consensus protocols ensure data consistency across replicated state machines in the cluster.", "Distributed Systems"),
    ("Database indexing structures such as B-trees significantly reduce the latency of query lookups.", "Databases"),
    ("Software compilation involves lexical analysis, parsing, semantic verification, and code generation.", "Compilers"),
    ("Network transport layers establish reliable end-to-end connections using transmission control protocols.", "Networking"),
    ("Version control systems maintain complete history logs of repository modifications over time.", "DevOps"),
    ("Containerization encapsulates applications with their dependencies to enable consistent runtime environments.", "Infrastructure"),
    ("Asynchronous event loops handle multiple concurrent non-blocking input and output operations efficiently.", "Async I/O"),
    ("Information retrieval algorithms rank relevant documents using statistical token frequencies and vector similarity.", "Search"),
    ("Cache coherence mechanisms maintain memory uniformity across multiple processing cores in modern processors.", "Hardware"),
    ("Static code analysis detects potential security vulnerabilities and logic defects prior to deployment.", "Quality Assurance"),
    ("High-availability architectures eliminate single points of failure through automated failover mechanisms.", "Cloud Architecture"),
    ("Microservice architectures decouple application components into independently deployable units communicating over HTTP.", "Microservices"),
    ("Memory safety guarantees prevent buffer overflows and dangling pointer dereferences in low-level systems.", "Memory Management"),
]
for text, cat in english_samples:
    add_fixture(text, "ENGLISH", f"ENGLISH_STANDARD_{cat.upper()}", True, False, "ACCEPTED", notes="Clean standard English prose")

# 3. Romanized Tamil (Informal & Everyday) - 16 records
romanized_tamil_samples = [
    ("Innaiku kaalaila romba mazhai peyudhu, veliya poga mudiyala pa.", "Weather"),
    ("Naalaiku office-ku seekiram kelambanum, mukkiyamaana client meeting irukku.", "Work"),
    ("Indha hotel-la biryani taste romba nalla iruku, kandippa marubadiyum varanum.", "Food"),
    ("Weekend-la friends ellarum serndhu cinema-ku polama nu yosikirom.", "Leisure"),
    ("Unakku enna problem, edhuku ipdi kavalappattutu irukka, ellam seri aayidum.", "Advice"),
    ("Pudhiya laptop vangiyachu, build quality super-aa iruku, performance semma speed.", "Tech/Review"),
    ("Exam-ku nalla prepare pannitiya? Enaku innum konjam portions padikka vendiyirukku.", "Studies"),
    ("Train tickets confirm aayiducha illai waiting list-la dhaan iruka nu check pannu.", "Travel"),
    ("Amma samachadhu eppovume super taste, oorukku poganum nu aasaia irukku.", "Home"),
    ("Avan kitta andha project files ellam kuduthuten, innum review pannala nu sonnan.", "Office"),
    ("Nethu night football match paathiya, climax-la semma goal pottanga thala.", "Sports"),
    ("Romba tired-aa irukku, oru cup tea kudinga, appuram velaiya thodangalaam.", "Daily Life"),
    ("Phone battery seekiram discharge aagudhu, service center-la kudukka vendiyirukkum.", "Device"),
    ("Namma oorla pudhusa oru supermarket thirandhurukaanga, anga poyi paakalam.", "Local"),
    ("Enakku indha vishayam theriyadhu, avana kettu solren, konjam wait pannu.", "Casual"),
    ("Bus stand-ku poga autokaaran kitta pesi paathen, romba adhigama kekkuraan da.", "Transport"),
]
for text, cat in romanized_tamil_samples:
    add_fixture(text, "TANGLISH", f"ROMANIZED_TAMIL_{cat.upper()}", True, False, "ACCEPTED", notes="Romanized spoken Tamil")

# 4. Intra-Sentential Code-Switching (Mixed Tamil and Latin Script) - 15 records
mixed_script_samples = [
    ("Server reboot aana piragu microservices automatically start aagala, script execute பண்ணனும்.", "DevOps"),
    ("Database connection pool timeout increase பண்ணினா, concurrency issues solve aagidum.", "Backend"),
    ("Indha API endpoint-ku JSON response structure validate பண்ணியாச்சு, frontend integrate பண்ணலாம்.", "Fullstack"),
    ("Model training loss stabilize aaga 50 epochs வரை run பண்ண வேண்டியிருக்கும்.", "AI/ML"),
    ("Production deployment-க்கு முன்னாடி regression tests run பண்ணி report generate பண்ணுங்க.", "QA"),
    ("Code review-ல performance optimization suggestions கொடுத்திருக்காங்க, change பண்ணனும்.", "Workflow"),
    ("Security audit-ல் cryptographic tokens check பண்ணி authorization headers verify பண்ணினோம்.", "Security"),
    ("Docker container restart loop-ல மாட்டிக்கிச்சு, container logs inspect பண்ணி debug பண்ணு.", "Containers"),
    ("User authentication token expire ஆயிடுச்சு, session refresh பண்ணி retry பண்ணுங்க.", "Auth"),
    ("Cloud storage bucket permissions properly configure செய்யப்பட வேண்டும்.", "Cloud"),
    ("Distributed cache miss rate அதிகமா இருக்கு, TTL duration adjust பண்ணி பாருங்க.", "Caching"),
    ("Unit test suite execute ஆகும்போது memory leak warning காண்பிக்கிறது.", "Testing"),
    ("Load balancer health check fail ஆனா traffic secondary instance-க்கு route ஆகும்.", "Networking"),
    ("Dataset tokenization process complete ஆகிவிட்டது, vocabulary hash verify பண்ணலாம்.", "NLP"),
    ("Kubernetes cluster node status ready-ஆ இல்லை, worker node logs analyse பண்ண வேண்டும்.", "K8s"),
]
for text, cat in mixed_script_samples:
    add_fixture(text, "TANGLISH", f"INTRA_SENTENTIAL_CODE_SWITCH_{cat.upper()}", True, False, "ACCEPTED", notes="Tamil script + Latin script code switching")

# 5. English Sentences with Tamil Discourse Particles - 15 records
english_particles_samples = [
    ("Let us wrap up this release quickly da, otherwise deployment will get delayed.", "da particle"),
    ("Aiyo, the network latency is spiking again, please check the load balancer.", "aiyo particle"),
    ("Don't worry pa, the pipeline will auto-recover in a couple of minutes.", "pa particle"),
    ("Please finish this documentation ticket today itself da, client is waiting.", "da particle"),
    ("Aiyo, I forgot to commit the configuration template before branching.", "aiyo particle"),
    ("No problem da, we can easily reproduce the test failure in our local sandbox.", "da particle"),
    ("Aiyo, the disk space on the root partition is critically low!", "aiyo particle"),
    ("Don't touch the production database directly da, always use the migration scripts.", "da particle"),
    ("Hey machan, check the build logs, everything compiled smoothly without errors.", "machan particle"),
    ("Seri, let us schedule the database backup window for midnight tonight.", "seri particle"),
    ("Romba carefully review the pull request, it touches the core payment flow.", "romba particle"),
    ("Thambi, don't push code without running the pre-commit linting checks first.", "thambi particle"),
    ("Aiyoo, the entire monitoring dashboard is showing timeout errors across all nodes.", "aiyoo particle"),
    ("You must verify the cryptographic signatures before approving the release da.", "da particle"),
    ("Dei, did you push the latest schema migrations to the staging environment yet?", "dei particle"),
]
for text, cat in english_particles_samples:
    add_fixture(text, "TANGLISH", f"ENGLISH_WITH_TAMIL_PARTICLE_{cat.upper().replace(' ', '_')}", True, False, "ACCEPTED", notes="English with conversational Tamil particles")

# 6. Formal & Technical Tanglish (Architecture & Case Markers) - 15 records
formal_tech_samples = [
    ("Decoder-only transformer architecture-ல் multi-head self-attention mechanisms language representations-ஐ generate செய்கின்றன.", "Self-Attention"),
    ("Tokenizer vocabulary-யில் 32,768 structural and subword tokens முறையாக allocate செய்யப்பட்டுள்ளன.", "Tokenizer"),
    ("Gradient clipping threshold 1.0-க்கு மேலாக செல்லாமல் training stability ensure செய்யப்படுகிறது.", "Training"),
    ("Checkpoint integrity verification SHA-256 hash validation மூலமாக confirm செய்யப்படுகிறது.", "Checkpoints"),
    ("Context window length 2048 tokens-க்கு உட்பட்டு input sequences truncate செய்யப்படுகின்றன.", "Context Window"),
    ("Rotary position embeddings (RoPE) relative token distances-ஐ encode செய்ய உதவுகின்றன.", "RoPE"),
    ("SwiGLU activation function feed-forward network layers-ல் gradient flow-ஐ மேம்படுத்துகிறது.", "Activations"),
    ("Grouped-query attention (GQA) key-value cache memory overhead-ஐ 50% reduce செய்கிறது.", "GQA"),
    ("Root Mean Square Normalization (RMSNorm) layer outputs-ஐ stabilize செய்து training speed-ஐ அதிகரிக்கிறது.", "RMSNorm"),
    ("FlashAttention v2 memory-efficient exact attention computation-ஐ GPU hardware-ல் execute செய்கிறது.", "FlashAttention"),
    ("AdamW optimizer decoupled weight decay mechanism மூலமாக model overfitting-ஐ தடுக்கிறது.", "AdamW"),
    ("Cosine annealing learning rate schedule training loss convergence-ஐ smooth ஆக்குகிறது.", "LR Schedule"),
    ("Bfloat16 precision training numerical stability-ஐ maintain செய்து GPU memory-ஐ மிச்சப்படுத்துகிறது.", "Precision"),
    ("Data loader pipeline multithreaded workers மூலமாக tokenized shards-ஐ stream செய்கிறது.", "Data Loader"),
    ("Cross-entropy loss function target probability distribution-ஐ evaluate செய்து gradients calculate செய்கிறது.", "Loss Function"),
]
for text, cat in formal_tech_samples:
    add_fixture(text, "TANGLISH", f"FORMAL_TECHNICAL_TANGLISH_{cat.upper().replace('-', '_')}", True, False, "ACCEPTED", notes="Formal technical English with Tamil case suffixes")

# 7. Unicode Edge Cases & Linguistic Variations - 15 records
unicode_edge_cases = [
    ("கா கி கீ கு கூ கெ கே கை கொ கோ கௌ ஆகிய உயிர்மெய் எழுத்துக்கள் சரியாக பராமரிக்கப்பட வேண்டும்.", "TAMIL", "TAMIL_VOWEL_SIGNS", True, False, "ACCEPTED", "All 11 Tamil vowel signs"),
    ("மெய்யெழுத்துக்கள் க் ங் ச் ஞ் ட் ண் த் ந் ப் ம் ய் ர் ல் வ் ழ் ள் ற் ன் புள்ளி எழுத்துக்கள் ஆகும்.", "TAMIL", "TAMIL_VIRAMA_SERIES", True, False, "ACCEPTED", "Complete 18 Tamil virama consonants"),
    ("தமிழ் எண்கள் ௧ ௨ ௩ ௪ ௫ ௬ ௭ ௮ ௯ ௰ பண்டைய ஆவணங்களில் பரவலாகப் பயன்படுத்தப்பட்டன.", "TAMIL", "TAMIL_NUMERALS", True, False, "ACCEPTED", "Tamil numerals"),
    ("சொற்களைப் பிழை திருத்தம் செய்தல் மற்றும் கற்றல் கற்பித்தல் முறைகள் செம்மைப்படுத்தப்படுகின்றன.", "TAMIL", "TAMIL_SANDHI_VARIATION", True, False, "ACCEPTED", "Tamil legitimate sandhi variation"),
    ("நன்றாகப் படித்து தேர்வில் முதல் மதிப்பெண் பெற்ற மாணவர்களுக்கு வாழ்த்துகள் தெரிவிக்கப்பட்டது.", "TAMIL", "TAMIL_COLLOQUIAL_SPELLING", True, False, "ACCEPTED", "Colloquial vs formal spelling variations"),
    ("ஸ்ரீ ராமன் என்ற அடைமொழி மற்றும் கிரந்த எழுத்துக்கள் ஜ, ஷ, ஸ, ஹ, க்ஷ பயன்பாட்டில் உள்ளன.", "TAMIL", "TAMIL_GRANTHA_LETTERS", True, False, "ACCEPTED", "Tamil Grantha characters"),
    ("க்\u200Dக மற்றும் க்\u200Cக போன்ற ZWJ மற்றும் ZWNJ குறியீடுகள் ரெண்டரிங்கில் பாதுகாக்கப்படுகின்றன.", "TAMIL", "TAMIL_ZWJ_ZWNJ", True, False, "ACCEPTED", "Tamil with ZWJ and ZWNJ"),
    ("க்் இரட்டைப் புள்ளி உள்ள பிழையான சொல்.", "TAMIL", "ADVERSARIAL_DOUBLE_VIRAMA", False, False, "REJECTED", "Adversarial double virama"),
    ("\u0BBE தனித்த உயிர்மெய்க் குறியீடு பிழையானது.", "TAMIL", "ADVERSARIAL_LONE_COMBINING", False, False, "REJECTED", "Lone combining vowel sign"),
    ("This text contains an invalid replacement character \uFFFD causing encoding rejection.", "ENGLISH", "ADVERSARIAL_REPLACEMENT_CHAR", False, False, "REJECTED", "U+FFFD replacement char"),
    ("கணினி\x00கட்டுப்பாடு\x01எழுத்துக்கள் நீக்கப்பட வேண்டும்.", "TAMIL", "CONTROL_CHARACTERS", True, False, "ACCEPTED", "Sanitized control characters"),
    ("நவீன தமிழ் உரைநடை மற்றும் பழங்கால இலக்கண மரபுகள் ஆகியவற்றுக்கு இடையேயான ஒப்பீடு.", "TAMIL", "TAMIL_MORPHOLOGY_VARIATION", True, False, "ACCEPTED", "Complex Tamil morphology"),
    ("ஆங்கிலம் மற்றும் தமிழ் சொற்கள் கலந்து வருவது தற்கால பேச்சு வழக்கில் இயல்பாகிவிட்டது da.", "TANGLISH", "MIXED_UNICODE_CONVERSATIONAL", True, False, "ACCEPTED", "Tamil with single English particle"),
    ("Microprocessor architecture-ல் cache hierarchy instructions-ஐ prefetch செய்கிறது.", "TANGLISH", "TECHNICAL_MIXED_ACCENT", True, False, "ACCEPTED", "Technical mixed with Tamil verbs"),
    ("Deep learning models require balanced multilingual datasets for optimal representation.", "ENGLISH", "ENGLISH_COMPLEX_VOCAB", True, False, "ACCEPTED", "Clean complex English"),
]
for text, lang, cat, q_pass, is_dup, action, notes in unicode_edge_cases:
    reasons = ["MALFORMED_UNICODE"] if not q_pass else []
    add_fixture(text, lang, cat, q_pass, is_dup, action, reasons=reasons, notes=notes)

# 8. Duplicate and Near-Duplicate Records - 15 records
dup_records = [
    (tamil_samples[0][0], "TAMIL", "EXACT_DUPLICATE_TAMIL", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_EXACT"], "Exact duplicate of P25-SYN-0001"),
    (english_samples[0][0], "ENGLISH", "EXACT_DUPLICATE_ENGLISH", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_EXACT"], "Exact duplicate of P25-SYN-0017"),
    (romanized_tamil_samples[0][0], "TANGLISH", "EXACT_DUPLICATE_ROMANIZED", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_EXACT"], "Exact duplicate of P25-SYN-0033"),
    (mixed_script_samples[0][0], "TANGLISH", "EXACT_DUPLICATE_MIXED", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_EXACT"], "Exact duplicate of P25-SYN-0049"),
    (english_particles_samples[0][0], "TANGLISH", "EXACT_DUPLICATE_PARTICLE", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_EXACT"], "Exact duplicate of P25-SYN-0064"),
    ("  " + tamil_samples[1][0] + "  \n", "TAMIL", "NORMALIZED_DUPLICATE_TAMIL", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NORMALIZED"], "Whitespace padding variant of P25-SYN-0002"),
    ("   " + english_samples[1][0].upper() + "   ", "ENGLISH", "NORMALIZED_DUPLICATE_ENGLISH", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NORMALIZED"], "Uppercase and whitespace variant of P25-SYN-0018"),
    ("  " + romanized_tamil_samples[1][0] + "  ", "TANGLISH", "NORMALIZED_DUPLICATE_ROMANIZED", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NORMALIZED"], "Whitespace variant of P25-SYN-0034"),
    (mixed_script_samples[1][0] + "   \n\t", "TANGLISH", "NORMALIZED_DUPLICATE_MIXED", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NORMALIZED"], "Trailing whitespace variant of P25-SYN-0050"),
    ("  " + english_particles_samples[1][0] + "  ", "TANGLISH", "NORMALIZED_DUPLICATE_PARTICLE", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NORMALIZED"], "Whitespace variant of P25-SYN-0065"),
    (tamil_samples[2][0] + " நிச்சயமாக உண்மை.", "TAMIL", "NEAR_DUPLICATE_TAMIL", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NEAR_DUPLICATE"], "Near duplicate of P25-SYN-0003 with trailing words"),
    (english_samples[2][0] + " This is verified.", "ENGLISH", "NEAR_DUPLICATE_ENGLISH", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NEAR_DUPLICATE"], "Near duplicate of P25-SYN-0019 with appended sentence"),
    (romanized_tamil_samples[2][0] + " romba taste pa.", "TANGLISH", "NEAR_DUPLICATE_ROMANIZED", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NEAR_DUPLICATE"], "Near duplicate of P25-SYN-0035 with appended phrase"),
    (mixed_script_samples[2][0] + " verified completely.", "TANGLISH", "NEAR_DUPLICATE_MIXED", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NEAR_DUPLICATE"], "Near duplicate of P25-SYN-0051 with added token"),
    (english_particles_samples[2][0] + " definitely sure.", "TANGLISH", "NEAR_DUPLICATE_PARTICLE", True, True, "DUPLICATE_FLAGGED", ["DUPLICATE_NEAR_DUPLICATE"], "Near duplicate of P25-SYN-0066 with added words"),
]
for text, lang, cat, q_pass, is_dup, action, reasons, notes in dup_records:
    add_fixture(text, lang, cat, q_pass, is_dup, action, reasons=reasons, notes=notes)

# 9. Malformed and Low-Quality Records (Quality Rejections) - 15 records
low_quality_samples = [
    ("", "UNKNOWN", "EMPTY_RECORD", False, False, "REJECTED", ["EMPTY_RECORD"], "Empty string"),
    ("   \t\n  ", "UNKNOWN", "WHITESPACE_ONLY", False, False, "REJECTED", ["EMPTY_RECORD"], "Whitespace only"),
    ("Hi", "ENGLISH", "TOO_SHORT_ENGLISH", False, False, "REJECTED", ["TOO_SHORT", "TOO_FEW_WORDS"], "Under 10 characters"),
    ("வா", "TAMIL", "TOO_SHORT_TAMIL", False, False, "REJECTED", ["TOO_SHORT", "TOO_FEW_WORDS"], "Single Tamil syllable under 10 chars"),
    ("a" * 80, "ENGLISH", "REPEATED_CHAR_SPAM_ENGLISH", False, False, "REJECTED", ["TOO_FEW_WORDS", "REPEATED_CHAR_SPAM"], "80 consecutive 'a' chars"),
    ("ஹ" * 30, "TAMIL", "REPEATED_CHAR_SPAM_TAMIL", False, False, "REJECTED", ["TOO_FEW_WORDS", "REPEATED_CHAR_SPAM"], "30 consecutive 'ஹ' chars"),
    ("https://example.com/a https://example.com/b https://example.com/c https://test.org/d https://links.net/e more links https://final.com", "ENGLISH", "URL_HEAVY", False, False, "REJECTED", ["URL_HEAVY"], "High URL character ratio"),
    ("??? !!! .... ,,,, :::: ;;;; ??? !!! .... ,,,, :::: ;;;;", "UNKNOWN", "EXCESSIVE_PUNCTUATION", False, False, "REJECTED", ["TOO_FEW_WORDS", "EXCESSIVE_PUNCTUATION", "NO_ALPHABETIC_CHARS"], "Punctuation spam"),
    ("Please accept our cookie policy and review our terms of service before using this site.", "ENGLISH", "BOILERPLATE_LEGAL", False, False, "REJECTED", ["BOILERPLATE_DETECTED"], "Legal boilerplate keywords"),
    ("Click here to subscribe now and read our privacy policy advertisement.", "ENGLISH", "BOILERPLATE_MARKETING", False, False, "REJECTED", ["BOILERPLATE_DETECTED"], "Marketing boilerplate keywords"),
    ("1234567890 9876543210 1122334455", "UNKNOWN", "NO_ALPHABETIC_DIGITS", False, False, "REJECTED", ["NO_ALPHABETIC_CHARS"], "Digits only no alphabetic"),
    ("!@#$%^&*()_+=-`~[]{}|;:',.<>/?", "UNKNOWN", "NO_ALPHABETIC_SYMBOLS", False, False, "REJECTED", ["TOO_FEW_WORDS", "EXCESSIVE_PUNCTUATION", "NO_ALPHABETIC_CHARS"], "Special symbols only"),
    ("Hello \uFFFD world with corrupted \uFFFD bytes \uFFFD in stream", "ENGLISH", "MALFORMED_UNICODE_CORRUPTION", False, False, "REJECTED", ["MALFORMED_UNICODE"], "Corrupted replacement chars"),
    ("Error 404 not found page not found on web server.", "ENGLISH", "BOILERPLATE_404", False, False, "REJECTED", ["BOILERPLATE_DETECTED"], "404 boilerplate"),
    ("OK", "ENGLISH", "TOO_SHORT_ACRONYM", False, False, "REJECTED", ["TOO_SHORT", "TOO_FEW_WORDS"], "Two letter response"),
]
for text, lang, cat, q_pass, is_dup, action, reasons, notes in low_quality_samples:
    add_fixture(text, lang, cat, q_pass, is_dup, action, reasons=reasons, notes=notes)

# 10. Out-of-Scope Languages (Non-Target Rejections) - 12 records (Hindi, Telugu, Kannada, Malayalam)
out_of_scope_samples = [
    ("भारत एक विशाल और विविधताओं से भरा हुआ देश है जहां अनेक भाषाएं बोली जाती हैं।", "OUT_OF_SCOPE", "HINDI_DEVANAGARI_PROSE", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari"),
    ("हिंदी साहित्य का इतिहास बहुत प्राचीन और समृद्ध माना जाता है।", "OUT_OF_SCOPE", "HINDI_DEVANAGARI_LITERATURE", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari"),
    ("कंप्यूटर विज्ञान में कृत्रिम बुद्धिमत्ता का उपयोग तेजी से बढ़ रहा है।", "OUT_OF_SCOPE", "HINDI_DEVANAGARI_TECH", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari"),
    ("मौसम विभाग ने आज भारी बारिश की चेतावनी जारी की है।", "OUT_OF_SCOPE", "HINDI_DEVANAGARI_NEWS", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari"),
    ("पर्यावरण की सुरक्षा हम सभी का नैतिक कर्तव्य और जिम्मेदारी है।", "OUT_OF_SCOPE", "HINDI_DEVANAGARI_ENVIRONMENT", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: DEVANAGARI"], "Hindi Devanagari"),
    ("తెలుగు భారతదేశంలో అత్యధికంగా మాట్లాడే భాషలలో ఒకటిగా గుర్తింపు పొందింది.", "OUT_OF_SCOPE", "TELUGU_SCRIPT_PROSE", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script"),
    ("ఆంధ్రప్రదేశ్ మరియు తెలంగాణ రాష్ట్రాల అధికారిక భాషగా తెలుగు ఉంది.", "OUT_OF_SCOPE", "TELUGU_SCRIPT_OFFICIAL", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script"),
    ("సాంకేతిక రంగంలో నూతన ఆవిష్కరణలు మానవ జీవన విధానాన్ని సులభతరం చేస్తున్నాయి.", "OUT_OF_SCOPE", "TELUGU_SCRIPT_TECH", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script"),
    ("రైతులు దేశానికి వెన్నెముక వంటి వారు, వ్యవసాయం ఆర్థిక వ్యవస్థకు ఆధారం.", "OUT_OF_SCOPE", "TELUGU_SCRIPT_AGRI", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script"),
    ("ప్రకృతి వనరులను సద్వినియోగం చేసుకోవడం భవిష్యత్ తరాలకు ఎంతో అవసరం.", "OUT_OF_SCOPE", "TELUGU_SCRIPT_ECOLOGY", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: TELUGU"], "Telugu script"),
    ("ಕನ್ನಡ ಸಾಹಿತ್ಯವು ಅತ್ಯಂತ ಪ್ರಾಚೀನ ಮತ್ತು ಸಮೃದ್ಧ ಇತಿಹಾಸವನ್ನು ಹೊಂದಿದೆ.", "OUT_OF_SCOPE", "KANNADA_SCRIPT_LITERATURE", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: KANNADA"], "Kannada script"),
    ("മലയാള ഭാഷ ദക്ഷിണേന്ത്യയിലെ പ്രധാനപ്പെട്ട ദ്രാവിഡ ഭാഷകളിൽ ഒന്നാണ്.", "OUT_OF_SCOPE", "MALAYALAM_SCRIPT_PROSE", True, False, "REJECTED", ["OUT_OF_SCOPE_LANGUAGE: MALAYALAM"], "Malayalam script"),
]
for text, lang, cat, q_pass, is_dup, action, reasons, notes in out_of_scope_samples:
    add_fixture(text, lang, cat, q_pass, is_dup, action, reasons=reasons, notes=notes)

# Write output file
with open(OUT_FILE, "w", encoding="utf-8") as f:
    for fix in fixtures:
        f.write(json.dumps(fix, ensure_ascii=False) + "\n")

print(f"Generated exactly {len(fixtures)} synthetic fixtures in {OUT_FILE}")
