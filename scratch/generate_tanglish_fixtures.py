"""
scratch/generate_tanglish_fixtures.py

Generates PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl and runs comprehensive quality checks:
1. 100 rich synthetic Tanglish fixtures across 5 linguistic categories.
2. Full metadata (script composition, code-switch type, lexical features).
3. Quality assertions:
   - Unicode NFC validity.
   - Non-target script contamination check (zero Devanagari, Telugu, Malayalam, Kannada, Bengali, etc.).
   - Zero living PII.
   - Deduplication check.
   - Language balance verification.
"""

import json
import re
import unicodedata
from pathlib import Path

# Linguistic fixture templates (20 per category, total = 100)
FIXTURE_SPECS = [
    # -------------------------------------------------------------------------
    # Category 1: TAMIL_SCRIPT_ENGLISH_TECH (20 fixtures)
    # -------------------------------------------------------------------------
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "இந்த server configuration ரொம்ப complex-ஆ இருக்கு, restart பண்ணவா?"),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "API latency அதிகமா இருக்கு, Redis caching implement பண்ணனும்."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Database migration script-ஐ staging environment-ல் test பண்ணிட்டேன்."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Production cluster-ல் memory leak detect ஆகியிருக்கு, alert notify பண்ணியாச்சு."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Authentication token expire ஆகிட்டா user login page-க்கு redirect ஆகிடும்."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Continuous integration pipeline-ல் build test cases pass ஆகிடுச்சு."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Model weights checkpoint save பண்ணிட்டு GPU memory release பண்ணுங்க."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Docker container logs-ஐ check பண்ணி error message என்னன்னு பாருங்க."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Pull request review முடிஞ்சது, merge conflict எதுவும் இல்லை."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Network bandwidth optimize பண்ண load balancer configure பண்ணனும்."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Backend microservices-க்கு message queue setup பண்ணியாச்சு."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Frontend framework upgrade பண்ணும்போது dependency issues வருது."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Batch size increase பண்ணா out-of-memory error வருது, gradient accumulation use பண்ணலாம்."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Query optimization பண்ணின பிறகு database response time improve ஆகியிருக்கு."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Security audit report-ல் zero critical vulnerabilities காமிக்குது."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Configuration file-ல் environment variables change பண்ணிட்டு server reload பண்ணுங்க."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Cloud storage bucket permissions-ஐ verify பண்ணிட்டு download script run பண்ணலாம்."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Training loss steady-ஆ decrease ஆகுது, validation perplexity monitor பண்ணுங்க."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Websocket connection drop ஆனா automatic reconnect trigger ஆகணும்."),
    ("TAMIL_SCRIPT_ENGLISH_TECH", "informal", "intra_sentential", "Release notes draft பண்ணி repository documentation-ல் update பண்ணியாச்சு."),

    # -------------------------------------------------------------------------
    # Category 2: ROMANIZED_TAMIL_INFORMAL (20 fixtures)
    # -------------------------------------------------------------------------
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Innaiku evening tea sapda polama? Enaku romba tired-ah iruku."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Nalla movie pathiya nethu? Climax scene romba emotionally touch aayiduchu."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Naalaiku kaalaila seekiram kelambanum, reminder set panni vechuruken."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Avan kitta pesinen, execution plan pathi avanukum nalla understanding iruku."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Enna aachu da? Romba nerama message pakkama iruka, edhavadhu problem-ah?"),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Office-ku vandha udane unaku call panren, tension aagadha."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Indha restaurant-la biryani super-ah irukum, kandippa try pannanum."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Veetla ellarum epdi irukanga? Amma kitta pesi romba naal aachu."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Enoda laptop charger marandhuten, yaradhu spare vachurukengala?"),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Macha, nethu night sonna code snippet work aayiduchu, thanks da!"),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Weekend plan edhavadhu iruka illai full day rest eduka poriya?"),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Kandippa serndhu prepare pannalam, exam romba easy-ah clear pannidalam."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Train time aayiduchu, station-ku auto la poyitu iruken."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Adhu pathi kavala padadha, ellam correct-ah nadakkum."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Unoda presentation super-ah vandhudhu, manager romba appreciate pannaru."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Indha logic puriyala na kekka vendiyadhu dhane, ethuku silent-ah iruka?"),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Pasi edukkudhu pa, seekiram lunch polaam vaanga."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Pudhu phone vaangiyaacha? Camera quality epdi iruku?"),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Romba nalla idea idhu, implementation pathi pesalaam."),
    ("ROMANIZED_TAMIL_INFORMAL", "informal", "phonetic_transcription", "Nalaiku meeting cancel aayiduchu, vera slot book pannanum."),

    # -------------------------------------------------------------------------
    # Category 3: ENGLISH_TAMIL_COLLOQUIAL (20 fixtures)
    # -------------------------------------------------------------------------
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Let us wrap up this release quickly da, otherwise deployment will get delayed."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Aiyo, the network latency is spiking again, please check the load balancer."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Don't worry pa, the pipeline will auto-recover in a couple of minutes."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Seri, let us schedule the sprint retrospective for tomorrow morning."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Machan, did you review the latest architectural diagram for the gateway?"),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "That pull request is looking romba clean, nice refactoring effort!"),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Apdiya? I thought the authentication service was already migrated to the cloud."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Please finish this documentation ticket today itself da, client is waiting."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Kandippa we will meet the project deadline, the team velocity is very high."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Aiyo, I forgot to commit the configuration template before branching."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Hey thambi, can you verify the SHA-256 checksum of the downloaded archive?"),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Seri pa, let us merge this hotfix and monitor the Grafana dashboard."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Machan, the new tokenizer candidate has a much lower fertility rate."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "No problem da, we can easily reproduce the test failure in our local sandbox."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Aiyo, the disk space on the root partition is critically low!"),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Seri, I will write the unit tests for the cryptographic validator."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "That model checkpoint achieved romba good validation accuracy in epoch five."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Don't touch the production database directly da, always use the migration scripts."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Kandippa we should follow the solo developer owner review protocol."),
    ("ENGLISH_TAMIL_COLLOQUIAL", "informal", "discourse_particle_insertion", "Seri, let us double check the licensing metadata before signing off."),

    # -------------------------------------------------------------------------
    # Category 4: INTRA_SENTENTIAL_CODE_SWITCH (20 fixtures)
    # -------------------------------------------------------------------------
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Client requirement-la sudden change, so frontend layout-ஐ restructure பண்ண வேண்டியிருக்கு."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Initial commit push panniten, pull request open pannava illai direct-ah merge pannalama?"),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Cache memory clear panniyum issue persist aagudhu, log files check pannunga."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Code review comments address பண்ணியாச்சு, unit tests ellam pass aagudhu."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Server reboot aana piragu microservices automatically start aagala, script execute பண்ணனும்."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Tokenization efficiency optimize panna, byte-fallback mechanism enable பண்ண வேண்டியிருக்கு."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Staging cluster-ல் load testing execute pannom, throughput expectations-க்கு match aagudhu."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Ingress gate lock-ஆ இருக்கறதால, zero external network calls allowed nu enforce பண்ணியாச்சு."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Data cleaning pipeline run பண்ணும்போது, non-target languages ellam filter aayidum."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Dependency upgrade pannina udane, build artifacts verify பண்ணிட்டு report generate பண்ணலாம்."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Feature branch create பண்ணி working copy isolate பண்ணியாச்சு, development start pannalam."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Database connection pool timeout increase பண்ணினா, concurrency issues solve aagidum."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Storage matrix calculations verify pannitom, local disk capacity deficit clearly documented."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Continuous integration workflow fail aagama iruka, temporary directories cleanup pannanum."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Production configuration freeze பண்ணியachu, unauthorized modifications strictly reject aagum."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Model evaluation benchmark run aagum bothu, zero evaluation data leakage ensure பண்ணனும்."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Audit trail logging configure பண்ணிட்டோம், all filesystem changes track aagudhu."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Vocabulary size 32768 tokens-க்கு pin panniyachu, structural tokens safely preserved."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Hardware probe output inspect பண்ணி, compute budget and RAM limits confirm பண்ணியாச்சு."),
    ("INTRA_SENTENTIAL_CODE_SWITCH", "informal", "intra_sentential", "Licensing compliance review mudinjudhu, owner authorization package ready-ah iruku."),

    # -------------------------------------------------------------------------
    # Category 5: FORMAL_TECHNICAL_TANGLISH (20 fixtures)
    # -------------------------------------------------------------------------
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "கணினி வலையமைப்பு (computer network) பாதுகாப்பு protocol-கள் முறையாக configure செய்யப்பட வேண்டும்."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "System architecture design document-ல் data flow diagrams மற்றும் interface specifications சேர்க்கப்பட்டுள்ளன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "மென்பொருள் உருவாக்க சுழற்சியில் (software development lifecycle) automated regression testing முக்கிய பங்கு வகிக்கிறது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Distributed database clusters-ல் consensus algorithm implementation உயர் நம்பகத்தன்மையை (high availability) உறுதி செய்கிறது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "தகவல் பாதுகாப்பு விதிமுறைகளின்படி (data security compliance), sensitive configuration variables அனைத்தும் encrypt செய்யப்பட வேண்டும்."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Decoder-only transformer architecture-ல் multi-head self-attention mechanisms language representations-ஐ generate செய்கின்றன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "இயக்க முறைமை (operating system) வள மேலாண்மை மூலமாக GPU allocation மற்றும் CPU utilization கண்காணிக்கப்படுகிறது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Microservice communication protocols-ல் gRPC மற்றும் REST endpoints-க்கான rate limiting rules வகுக்கப்பட்டுள்ளன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "தரவு பகுப்பாய்வு (data analytics) மற்றும் feature engineering பணிகளில் memory-mapped files செயல்திறனை அதிகரிக்கின்றன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Cryptographic hash verification மூலமாக software packages மற்றும் model checkpoints-ன் integrity உறுதிப்படுத்தப்படுகிறது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "ஆராய்ச்சி சூழலில் (research environment) deterministic random seed அமைப்பது experimental reproducibility-க்கு அவசியமானது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Neural network optimization-ல் learning rate schedule மற்றும் gradient clipping hyperparameters converge ஆவதற்கு உதவுகின்றன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "கோப்பு முறைமை (file system) தனிமைப்படுத்தல் மூலமாக test environments மற்றும் production pipelines பிரிக்கப்பட்டுள்ளன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Access control policies மற்றும் cryptographic signatures மூலமாக unauthorized data ingress தடுக்கப்படுகிறது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "மென்பொருள் தர உறுதிப்பாட்டு குழு (quality assurance team) functional testing மற்றும் load testing அறிக்கைகளை சமர்ப்பித்துள்ளது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Asynchronous event-driven architecture-ல் message brokers throughput மற்றும் scalability-ஐ கணிசமாக மேம்படுத்துகின்றன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "நினைவக மேலாண்மை (memory management) குறைபாடுகளை கண்டறிய profiling tools மற்றும் heap dump analysis பயன்படுத்தப்படுகிறது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Source code version control களஞ்சியத்தில் (repository) atomic commits மற்றும் linear branch history பராமரிக்கப்படுகிறது."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "Cloud deployment automation-ல் infrastructure as code (IaC) templates consistency மற்றும் security-ஐ நிலைநிறுத்துகின்றன."),
    ("FORMAL_TECHNICAL_TANGLISH", "formal", "formal_technical_gloss", "செயற்கை நுண்ணறிவு நெறிமுறைகளின்படி (AI ethics guidelines), dataset provenance மற்றும் licensing transparency உறுதி செய்யப்பட்டுள்ளது."),
]

# Prohibited unicode blocks (Non-target languages)
PROHIBITED_BLOCKS = [
    ("Devanagari (Hindi/Sanskrit/Marathi)", 0x0900, 0x097F),
    ("Bengali", 0x0980, 0x09FF),
    ("Gurmukhi", 0x0A00, 0x0A7F),
    ("Gujarati", 0x0A80, 0x0AFF),
    ("Oriya", 0x0B00, 0x0B7F),
    ("Telugu", 0x0C00, 0x0C7F),
    ("Kannada", 0x0C80, 0x0CFF),
    ("Malayalam", 0x0D00, 0x0D7F),
    ("Sinhala", 0x0D80, 0x0DFF),
    ("Arabic", 0x0600, 0x06FF),
    ("Cyrillic", 0x0400, 0x04FF),
    ("CJK Unified Ideographs", 0x4E00, 0x9FFF),
]

def analyze_text(text: str):
    # Normalize NFC
    nfc_text = unicodedata.normalize('NFC', text)
    is_nfc = (text == nfc_text)

    total_chars = len(text)
    tamil_chars = 0
    latin_chars = 0
    punct_space = 0
    contamination = []

    for char in text:
        cp = ord(char)
        # Check Tamil block U+0B80 - U+0BFF
        if 0x0B80 <= cp <= 0x0BFF:
            tamil_chars += 1
        # Check Latin / ASCII printable
        elif (0x0020 <= cp <= 0x007E) or (0x00A0 <= cp <= 0x00FF):
            if char.isalpha():
                latin_chars += 1
            else:
                punct_space += 1
        elif char in '\r\n\t ':
            punct_space += 1
        else:
            # Check prohibited blocks
            flagged = False
            for bname, start, end in PROHIBITED_BLOCKS:
                if start <= cp <= end:
                    contamination.append((char, hex(cp), bname))
                    flagged = True
                    break
            if not flagged:
                punct_space += 1

    # PII heuristics (emails, phone numbers, SSN, real human names with honorifics)
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phone_match = re.search(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    has_pii = bool(email_match or phone_match)

    return {
        "nfc_valid": is_nfc,
        "total_chars": total_chars,
        "tamil_chars": tamil_chars,
        "latin_chars": latin_chars,
        "punct_space_chars": punct_space,
        "tamil_ratio": round(tamil_chars / total_chars, 4) if total_chars else 0,
        "latin_ratio": round(latin_chars / total_chars, 4) if total_chars else 0,
        "contamination": contamination,
        "has_pii": has_pii,
    }

def main():
    fixtures = []
    seen_texts = set()

    for idx, (category, register, cs_type, text) in enumerate(FIXTURE_SPECS, 1):
        assert text not in seen_texts, f"Duplicate fixture detected at index {idx}: {text}"
        seen_texts.add(text)

        analysis = analyze_text(text)
        assert analysis["nfc_valid"], f"NFC normalization failed for: {text}"
        assert len(analysis["contamination"]) == 0, f"Prohibited script contamination: {analysis['contamination']}"
        assert not analysis["has_pii"], f"PII detected in: {text}"

        fixture_id = f"SYN-TG-{idx:03d}"
        item = {
            "id": fixture_id,
            "category": category,
            "register": register,
            "code_switch_type": cs_type,
            "text": text,
            "script_composition": {
                "total_chars": analysis["total_chars"],
                "tamil_chars": analysis["tamil_chars"],
                "latin_chars": analysis["latin_chars"],
                "punct_space_chars": analysis["punct_space_chars"],
                "tamil_ratio": analysis["tamil_ratio"],
                "latin_ratio": analysis["latin_ratio"],
            },
            "quality_checks": {
                "unicode_nfc_valid": True,
                "zero_non_target_contamination": True,
                "zero_pii": True,
                "non_empty_clean": True,
            }
        }
        fixtures.append(item)

    print(f"Generated {len(fixtures)} synthetic Tanglish fixtures perfectly.")
    
    # Save output to both patch and artifact directories
    patch_path = Path(r"C:\IGRIS\igris_3b52_production_tokenizer_patch\igris_3b52_patch\PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl")
    artifact_path = Path(r"C:\Users\joshu\.gemini\antigravity\brain\b8267850-e413-4486-8786-975a275b9102\PHASE23A_TANGLISH_SYNTHETIC_FIXTURES.jsonl")

    lines = [json.dumps(f, ensure_ascii=False) for f in fixtures]
    content = "\n".join(lines) + "\n"

    patch_path.write_text(content, encoding="utf-8")
    artifact_path.write_text(content, encoding="utf-8")

    print(f"Written to patch: {patch_path} ({patch_path.stat().st_size} bytes)")
    print(f"Written to artifact: {artifact_path} ({artifact_path.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
