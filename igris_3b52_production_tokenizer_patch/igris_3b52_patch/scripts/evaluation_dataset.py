"""IGRIS Milestone 3B.58 — Standardized Comparative Evaluation Dataset.

This dataset provides identical, reproducible text samples across 8 categories:
  1. Tamil
  2. English
  3. Tanglish
  4. Hindi
  5. Multilingual text
  6. Programming code
  7. Technical documentation
  8. Emoji and Unicode edge cases

No production data, approved inventory, quarantine files, or private training
data is accessed. All texts are synthetic / public domain evaluation benchmarks.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class EvaluationSample:
    sample_id: str
    category: str
    description: str
    text: str


EVALUATION_DATASET: list[EvaluationSample] = [
    # -------------------------------------------------------------------------
    # 1. TAMIL
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="tamil_01",
        category="Tamil",
        description="Classical Tamil (Tirukkural couplets with philosophical commentary)",
        text=(
            "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு. "
            "கற்றதனால் ஆய பயன்கொல் வாலறிவன் நற்றாள் தொழாஅர் எனின். "
            "எழுத்துக்கள் எல்லாம் அகரத்தை முதலாகக் கொண்டுள்ளன; அதுபோல உலகம் கடவுளை முதலாகக் கொண்டுள்ளது. "
            "தூய அறிவு வடிவான இறைவனின் திருவடிகளை வணங்காவிட்டால் கற்ற கல்வியினால் என்ன பயன்?"
        ),
    ),
    EvaluationSample(
        sample_id="tamil_02",
        category="Tamil",
        description="Modern Tamil news and formal editorial prose",
        text=(
            "செயற்கை நுண்ணறிவுத் தொழில்நுட்பம் உலகெங்கிலும் உள்ள பல்வேறு துறைகளில் புரட்சிகரமான "
            "மாற்றங்களை ஏற்படுத்தி வருகிறது. குறிப்பாக கல்வி, மருத்துவம், மற்றும் விண்வெளி ஆய்வுகளில் "
            "மொழி மாதிரிகளின் பயன்பாடு நாளுக்கு நாள் அதிகரித்து வருகிறது என்று ஆராய்ச்சியாளர்கள் தெரிவிக்கின்றனர்."
        ),
    ),
    EvaluationSample(
        sample_id="tamil_03",
        category="Tamil",
        description="Agglutinative morphology, complex verb forms and inflected suffixes",
        text=(
            "அவர்களுடையவற்றிலிருந்து பிரித்தெடுக்கப்பட்டவற்றை முறையாகப் பகுப்பாய்வு செய்து, "
            "அவற்றின் மூலக்கூறுகளையெல்லாம் வகைப்படுத்துவதனால் மட்டுமே உண்மையான முடிவுகளைப் பெறமுடியும். "
            "எவ்வாறாயினும், கற்றுக்கொள்ளப்பட்டவற்றைப் பகிர்ந்துகொள்வது அறிவார்ந்த சமூகத்தை உருவாக்கும்."
        ),
    ),
    EvaluationSample(
        sample_id="tamil_04",
        category="Tamil",
        description="Tamil technical, computing and administrative vocabulary",
        text=(
            "நினைவக ஒதுக்கீடு, தரவுத்தள அட்டவணைகள், வலையமைப்பு இணைப்புகள், மற்றும் பல்கூறுச்செயலாக்கம் "
            "போன்ற கணினி அறிவியல் கோட்பாடுகள் நவீன இயங்குதளங்களில் மிகக் கவனமாக வடிவமைக்கப்படுகின்றன. "
            "வரிசைப்படுத்தப்பட்ட மாறிகள் வேகமான நினைவக மீட்டெடுப்பை உறுதி செய்கின்றன."
        ),
    ),
    EvaluationSample(
        sample_id="tamil_05",
        category="Tamil",
        description="Grantha characters, Sanskrit loanwords and Tamil ligatures",
        text=(
            "ஸ்ரீ லக்ஷ்மி நரசிம்மர் ஆலயத்தில் நடைபெற்ற மஹா கும்பாபிஷேக விழாவில் "
            "லக்ஷம் பக்தர்கள் கலந்துகொண்டு புஷ்பாஞ்சலி மற்றும் அர்ச்சனை செய்து க்ஷேமமாக வாழ்ந்திட பிரார்த்தித்தனர். "
            "பக்தர்கள் அனைவருக்கும் பிரசாதமும் விசேஷ ஆசீர்வாதங்களும் வழங்கப்பட்டன."
        ),
    ),

    # -------------------------------------------------------------------------
    # 2. ENGLISH
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="english_01",
        category="English",
        description="Technical computer science and transformer model architecture",
        text=(
            "The decoder-only autoregressive transformer architecture relies heavily on causal multi-head self-attention, "
            "grouped-query attention projections, and rotary position embeddings. Feed-forward blocks typically utilize "
            "gated linear units such as SwiGLU to maximize representational capacity within a strict computational budget."
        ),
    ),
    EvaluationSample(
        sample_id="english_02",
        category="English",
        description="Conversational dialogue with contractions, idioms and colloquial phrasings",
        text=(
            "\"I shouldn't have said that, but wouldn't you agree that we've got to move forward?\" "
            "she asked. \"Don't worry about it—it's water under the bridge, and honestly, they'll understand "
            "as long as we don't drop the ball on this upcoming release.\""
        ),
    ),
    EvaluationSample(
        sample_id="english_03",
        category="English",
        description="Literary descriptive prose with rich vocabulary",
        text=(
            "The twilight deepened over the tranquil estuary, casting ethereal shades of amber and indigo "
            "across the rippling surface. A solitary curlew cried plaintively in the salt marshes, its melancholy "
            "cadence mingling with the distant murmur of the encroaching tide."
        ),
    ),
    EvaluationSample(
        sample_id="english_04",
        category="English",
        description="Formal legal and regulatory disclaimer text",
        text=(
            "Notwithstanding any provision herein to the contrary, neither party shall be liable for any indirect, "
            "consequential, punitive, or exemplary damages arising out of or in connection with the performance "
            "or breach of this Agreement, including but not limited to loss of profits, goodwill, or operational disruption."
        ),
    ),
    EvaluationSample(
        sample_id="english_05",
        category="English",
        description="Short prompt instructions, system queries, and command directives",
        text=(
            "Summarize the key differences between BPE and Unigram tokenization algorithms. "
            "Highlight byte-fallback handling, subword vocabulary allocation, compression efficiency, "
            "and out-of-vocabulary robustness across agglutinative and morphologically rich languages."
        ),
    ),

    # -------------------------------------------------------------------------
    # 3. TANGLISH
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="tanglish_01",
        category="Tanglish",
        description="Everyday casual conversational Tanglish with colloquial particles",
        text=(
            "Romba thanks bro! Naan innaiku evening kandippa unakku call panren. "
            "Appo namma detailed ah pesalaam. Neenga eppavum pola nalla support pandreenga, really appreciate it da!"
        ),
    ),
    EvaluationSample(
        sample_id="tanglish_02",
        category="Tanglish",
        description="Technical developer Tanglish with English computing terminology",
        text=(
            "Intha backend API la edho query timeout issue irukku pola. Database connection pool full aayiduchu, "
            "athanaala async workers queue la wait pannuthu. Immediate ah connection limit increase panni redeploy pannunga."
        ),
    ),
    EvaluationSample(
        sample_id="tanglish_03",
        category="Tanglish",
        description="Social media / instant messaging Tanglish",
        text=(
            "Enna thalaivaa romba naala aalaye kaanom? Project work la semma busy ah? "
            "Weekend aachum free time iruntha sollu, oru tea saappidalaam. Miss pandrom bro!"
        ),
    ),
    EvaluationSample(
        sample_id="tanglish_04",
        category="Tanglish",
        description="Expressive emotional Tanglish with local idioms",
        text=(
            "Vera level performance pa, padam pathuttu goosebumps vanthuduchu! "
            "Climax scene la bgm vera maari irunthathu. Director oda screenplay semma crisp ah connect aaguthu."
        ),
    ),
    EvaluationSample(
        sample_id="tanglish_05",
        category="Tanglish",
        description="Imperative workflow instructions in Tanglish",
        text=(
            "Repo va pull pannittu dependencies install pannu. Test suite run aagi pass aana apram thaan PR raise pannanum. "
            "Lint errors edhavadhu vanthaa fix pannitu commit message clear ah podunga."
        ),
    ),

    # -------------------------------------------------------------------------
    # 4. HINDI
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="hindi_01",
        category="Hindi",
        description="Formal news and constitutional / educational Devanagari prose",
        text=(
            "भारत एक विशाल और विविधतापूर्ण लोकतांत्रिक देश है। यहाँ की सांस्कृतिक धरोहर, ऐतिहासिक "
            "स्मारक और समृद्ध भाषाएँ पूरे विश्व में प्रसिद्ध हैं। संविधान प्रत्येक नागरिक को समानता, "
            "स्वतंत्रता और न्याय का मौलिक अधिकार प्रदान करता है।"
        ),
    ),
    EvaluationSample(
        sample_id="hindi_02",
        category="Hindi",
        description="Conversational Hindi with common polite formulations",
        text=(
            "नमस्ते! आप कैसे हैं? मुझे आपसे मिलकर बहुत प्रसन्नता हुई। "
            "क्या आप कल शाम की बैठक में उपस्थित हो सकेंगे? कृपया अपने समय की पुष्टि करें ताकि हम तैयारी कर सकें।"
        ),
    ),
    EvaluationSample(
        sample_id="hindi_03",
        category="Hindi",
        description="Complex Devanagari conjuncts and Sanskritized vocabulary",
        text=(
            "विश्वविद्यालय के अंतर्राष्ट्रीय संगोष्ठी में वैज्ञानिकों ने अंतरिक्ष अनुसंधान, "
            "सूक्ष्मजीव विज्ञान और नैनो-प्रौद्योगिकी के दृष्टिकोण पर अपने शोध पत्र प्रस्तुत किए। "
            "स्वास्थ्य और पर्यावरण संरक्षण के लिए यह अध्ययन अत्यंत महत्वपूर्ण सिद्ध होगा।"
        ),
    ),
    EvaluationSample(
        sample_id="hindi_04",
        category="Hindi",
        description="Technical computing and artificial intelligence prose in Hindi",
        text=(
            "कृत्रिम बुद्धिमत्ता और मशीन लर्निंग प्रणालियाँ आधुनिक युग के डेटा विश्लेषण को गति प्रदान कर रही हैं। "
            "गहरे तंत्रिका नेटवर्क (डीप न्यूरल नेटवर्क) प्राकृतिक भाषा प्रसंस्करण में अभूतपूर्व सटीकता प्रदर्शित करते हैं।"
        ),
    ),
    EvaluationSample(
        sample_id="hindi_05",
        category="Hindi",
        description="Philosophical reflection and moral literature in Hindi",
        text=(
            "सत्य और अहिंसा मानव जीवन के शाश्वत मूल्य हैं। जब व्यक्ति अपने अंतःकरण की आवाज सुनता है "
            "और बिना किसी स्वार्थ के परोपकार करता है, तब वह वास्तविक शांति और आत्मसंतुष्टि का अनुभव करता है।"
        ),
    ),

    # -------------------------------------------------------------------------
    # 5. MULTILINGUAL TEXT
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="multi_01",
        category="Multilingual text",
        description="Code-switching between Tamil, English, and Tanglish",
        text=(
            "IGRIS model இன் tokenizer architecture மிகச் சிறப்பாக வடிவமைக்கப்பட்டுள்ளது. "
            "It supports exactly 32,768 vocabulary tokens, including both Tamil and English scripts. "
            "Romba smooth ah tokenize aaguthu, with zero token leakage across boundaries."
        ),
    ),
    EvaluationSample(
        sample_id="multi_02",
        category="Multilingual text",
        description="Code-switching between Hindi, English, and Hinglish",
        text=(
            "Humara model multilingual capabilities ke liye train kiya gaya hai. "
            "यह प्रणाली English और Hindi दोनों भाषाओं में उत्कृष्ट परिणाम प्रदान करती है। "
            "Performance benchmarks show high throughput and low latency across mixed queries."
        ),
    ),
    EvaluationSample(
        sample_id="multi_03",
        category="Multilingual text",
        description="Trilingual documentation header (English, Tamil, Hindi)",
        text=(
            "Project IGRIS: High Performance Multilingual Language Model.\n"
            "திட்டம் இக்ரிஸ்: உயர் செயல்திறன் கொண்ட பன்மொழி மாதிரி.\n"
            "परियोजना इग्रिस: उच्च प्रदर्शन वाली बहुभाषी भाषा मॉडल प्रणाली।"
        ),
    ),
    EvaluationSample(
        sample_id="multi_04",
        category="Multilingual text",
        description="Interleaved parallel sentences across scripts",
        text=(
            "Welcome to our platform. நல்வரவு! आपका हार्दिक स्वागत है! "
            "Knowledge is power. அறிவே ஆற்றல். ज्ञान ही शक्ति है. "
            "Peace begins with a smile. அமைதி புன்னகையோடு தொடங்குகிறது."
        ),
    ),
    EvaluationSample(
        sample_id="multi_05",
        category="Multilingual text",
        description="Multilingual system log and status message with timestamps",
        text=(
            "[INFO 2026-11-17T14:49:05Z] Server cluster operational.\n"
            "[தகவல்] சேவையகக் குழு வெற்றிகரமாக இணைக்கப்பட்டது; நினைவக பயன்பாடு சீராக உள்ளது.\n"
            "[सूचना] सभी क्लस्टर सेवाएं सुचारू रूप से कार्य कर रही हैं। स्थिति: सक्रिय (ACTIVE)."
        ),
    ),

    # -------------------------------------------------------------------------
    # 6. PROGRAMMING CODE
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="code_01",
        category="Programming code",
        description="Python asynchronous generator, type annotations, and decorator",
        text=(
            "import asyncio\n"
            "from typing import AsyncIterator, Sequence\n\n"
            "@dataclass(slots=True, frozen=True)\n"
            "class TokenBatch:\n"
            "    batch_id: int\n"
            "    tokens: list[int]\n\n"
            "async def stream_batches(data: Sequence[str], batch_size: int = 32) -> AsyncIterator[TokenBatch]:\n"
            "    for i in range(0, len(data), batch_size):\n"
            "        chunk = data[i:i + batch_size]\n"
            "        yield TokenBatch(batch_id=i // batch_size, tokens=[ord(c) for text in chunk for c in text])\n"
            "        await asyncio.sleep(0.001)\n"
        ),
    ),
    EvaluationSample(
        sample_id="code_02",
        category="Programming code",
        description="TypeScript React functional component with hooks and generics",
        text=(
            "import React, { useState, useEffect, useMemo } from 'react';\n\n"
            "interface ModelMetricsProps<T extends Record<string, number>> {\n"
            "  title: string;\n"
            "  metrics: T;\n"
            "  onRefresh?: () => Promise<void>;\n"
            "}\n\n"
            "export const MetricsCard = <T extends Record<string, number>>({ title, metrics, onRefresh }: ModelMetricsProps<T>) => {\n"
            "  const [loading, setLoading] = useState<boolean>(false);\n"
            "  const total = useMemo(() => Object.values(metrics).reduce((acc, v) => acc + v, 0), [metrics]);\n"
            "  return (\n"
            "    <div className=\"rounded-lg border p-4 shadow-sm bg-white\">\n"
            "      <h3 className=\"text-lg font-semibold\">{title} (Total: {total.toFixed(2)})</h3>\n"
            "    </div>\n"
            "  );\n"
            "};\n"
        ),
    ),
    EvaluationSample(
        sample_id="code_03",
        category="Programming code",
        description="Rust systems implementation with traits, lifetime parameters, and pattern matching",
        text=(
            "use std::sync::Arc;\n"
            "use tokio::sync::RwLock;\n\n"
            "pub trait TokenCodec<'a> {\n"
            "    type Output;\n"
            "    fn encode(&self, input: &'a str) -> Result<Self::Output, CodecError>;\n"
            "}\n\n"
            "impl<'a, T: Backend> TokenCodec<'a> for StrictEngine<T> {\n"
            "    type Output = Vec<u32>;\n"
            "    fn encode(&self, input: &'a str) -> Result<Self::Output, CodecError> {\n"
            "        match self.inner.tokenize(input) {\n"
            "            Ok(tokens) if tokens.len() <= MAX_CONTEXT => Ok(tokens),\n"
            "            Ok(_) => Err(CodecError::ContextExceeded),\n"
            "            Err(e) => Err(CodecError::Underlying(e)),\n"
            "        }\n"
            "    }\n"
            "}\n"
        ),
    ),
    EvaluationSample(
        sample_id="code_04",
        category="Programming code",
        description="SQL analytical query with Common Table Expressions (CTEs) and window functions",
        text=(
            "WITH RankedTokens AS (\n"
            "    SELECT\n"
            "        candidate_id,\n"
            "        language_category,\n"
            "        sample_id,\n"
            "        token_count,\n"
            "        ROW_NUMBER() OVER (PARTITION BY language_category ORDER BY token_count ASC) AS rank_asc,\n"
            "        AVG(token_count) OVER (PARTITION BY language_category) AS avg_category_tokens\n"
            "    FROM tokenizer_benchmark_runs\n"
            "    WHERE status = 'COMPLETED' AND build_version = '3B.58'\n"
            ")\n"
            "SELECT candidate_id, language_category, sample_id, token_count, ROUND(avg_category_tokens, 2) AS avg_tokens\n"
            "FROM RankedTokens\n"
            "WHERE rank_asc <= 3\n"
            "ORDER BY language_category, rank_asc;\n"
        ),
    ),
    EvaluationSample(
        sample_id="code_05",
        category="Programming code",
        description="Configuration format specifications (JSON schema and YAML definitions)",
        text=(
            "{\n"
            "  \"$schema\": \"https://json-schema.org/draft/2020-12/schema\",\n"
            "  \"title\": \"TokenizerConfig\",\n"
            "  \"type\": \"object\",\n"
            "  \"properties\": {\n"
            "    \"vocab_size\": { \"type\": \"integer\", \"const\": 32768 },\n"
            "    \"structural_tokens\": { \"type\": \"array\", \"minItems\": 12, \"maxItems\": 12 },\n"
            "    \"byte_fallback\": { \"type\": \"boolean\", \"const\": true },\n"
            "    \"normalization\": { \"type\": \"string\", \"enum\": [\"NFC\", \"exact\"] }\n"
            "  },\n"
            "  \"required\": [\"vocab_size\", \"structural_tokens\", \"byte_fallback\"]\n"
            "}\n"
        ),
    ),

    # -------------------------------------------------------------------------
    # 7. TECHNICAL DOCUMENTATION
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="doc_01",
        category="Technical documentation",
        description="RESTful API Specification with HTTP verbs, JSON responses, and status codes",
        text=(
            "### POST /api/v1/tokenize/content\n\n"
            "Encodes plain text payload into an array of token IDs using strict escaping.\n\n"
            "**Request Headers:**\n"
            "- `Content-Type: application/json`\n"
            "- `X-IGRIS-Normalization: NFC`\n\n"
            "**Request Body:**\n"
            "```json\n"
            "{\n"
            "  \"text\": \"வணக்கம் உலகம் / Hello world\",\n"
            "  \"exact_unicode\": false\n"
            "}\n"
            "```\n\n"
            "**Response (200 OK):**\n"
            "```json\n"
            "{\n"
            "  \"tokens\": [297, 424, 493, 289, 272],\n"
            "  \"token_count\": 5,\n"
            "  \"byte_length\": 42\n"
            "}\n"
            "```\n"
        ),
    ),
    EvaluationSample(
        sample_id="doc_02",
        category="Technical documentation",
        description="Markdown documentation with nested lists, warning alerts, and tables",
        text=(
            "# Strict Tokenizer Contract Guidelines\n\n"
            "> [!IMPORTANT]\n"
            "> Token IDs in range 0–11 are strictly reserved for structural tokens. Content encoding MUST NEVER emit IDs 0–11.\n\n"
            "| Token ID | Spelling | Type | Usage |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| 0 | `<|pad|>` | PAD | Attention masking |\n"
            "| 1 | `<|begin_of_text|>` | CONTROL | Sequence delimiter |\n"
            "| 2 | `<|end_of_text|>` | CONTROL | Sequence termination |\n"
            "| 9 | `<|system|>` | CONTROL | Role framing |\n"
            "| 10 | `<|user|>` | CONTROL | User turn framing |\n"
            "| 11 | `<|assistant|>` | CONTROL | Assistant turn framing |\n"
        ),
    ),
    EvaluationSample(
        sample_id="doc_03",
        category="Technical documentation",
        description="System architecture design specification and SLA guarantees",
        text=(
            "The tokenizer subsystem operates as an immutable stateless service embedded within the model serving pipeline. "
            "P99 latency budget is allocated at 1.5ms per 1,000 characters. Ingestion workers must process streaming text "
            "without intermediate dynamic allocations. Backpressure mechanisms trigger when the ingestion buffer exceeds 64MB."
        ),
    ),
    EvaluationSample(
        sample_id="doc_04",
        category="Technical documentation",
        description="Mathematical description of BPE vs Unigram algorithms",
        text=(
            "Byte-Pair Encoding (BPE) begins with a base vocabulary of 256 byte tokens and iteratively merges the most frequent "
            "adjacent pair $(u, v) \\to w$ based on corpus co-occurrence counts. Conversely, the Unigram model assumes tokens occur "
            "independently according to a probability distribution $p(x)$ and computes the optimal segmentation via the Viterbi "
            "algorithm maximizing $\\sum_{i} \\log p(x_i)$."
        ),
    ),
    EvaluationSample(
        sample_id="doc_05",
        category="Technical documentation",
        description="Command line interface manual page and flag references",
        text=(
            "USAGE:\n"
            "    igris-tokenize [OPTIONS] --candidate <A|B> --input <FILE>\n\n"
            "OPTIONS:\n"
            "    -c, --candidate <A|B>       Select tokenizer candidate: A (BPE) or B (Unigram)\n"
            "    -n, --normalization <MODE>  Unicode normalization: 'NFC' (default) or 'exact'\n"
            "    -o, --output <PATH>         Destination file path for tokenized binary stream\n"
            "    -v, --verbose               Enable microsecond performance telemetry\n"
            "    -h, --help                  Print help information\n"
        ),
    ),

    # -------------------------------------------------------------------------
    # 8. EMOJI AND UNICODE EDGE CASES
    # -------------------------------------------------------------------------
    EvaluationSample(
        sample_id="emoji_01",
        category="Emoji and Unicode edge cases",
        description="Compound emojis with Zero-Width Joiner (ZWJ) sequences and skin tones",
        text=(
            "Family multi-person emojis: 👨‍👩‍👧‍👦, 👩‍👩‍👦‍👦, 👨‍👨‍👧‍👧. "
            "Profession and gesture sequences with modifier tones: 👩🏽‍💻, 👨🏻‍🔬, 🧑🏿‍🚒, 🏃🏽‍♀️, 🏋️‍♂️. "
            "Flags and composite symbols: 🏳️‍🌈, 🏳️‍⚧️, 🏴‍☠️, 👁️‍🗨️."
        ),
    ),
    EvaluationSample(
        sample_id="emoji_02",
        category="Emoji and Unicode edge cases",
        description="Combining diacritical marks, stacking accents, and decomposed codepoints",
        text=(
            "Acute and grave: e\u0301, a\u0300, o\u0302. "
            "Multiple stacking diacritics: s\u0307\u0323 (s with dot above and dot below), "
            "u\u0308\u0304 (u with diaeresis and macron), "
            "Zalgo extreme combining stack: T\u0346\u030d\u0310\u0312\u0359\u0349\u0323e\u033e\u0304\u0343\u032a\u0339s\u030a\u0352\u032dt."
        ),
    ),
    EvaluationSample(
        sample_id="emoji_03",
        category="Emoji and Unicode edge cases",
        description="Indic ZWNJ and ZWJ script distinctions (Tamil & Devanagari ligatures)",
        text=(
            "Tamil ligature with ZWNJ: க்\u200Cஷ vs Tamil ligature with ZWJ: க்\u200Dஷ. "
            "Devanagari conjunct with ZWNJ: क\u094D\u200Cष vs conjunct with ZWJ: क\u094D\u200Dष. "
            "Word separator markers and zero-width spaces: test\u200Bzero\u200Cwidth\u200Dspacing."
        ),
    ),
    EvaluationSample(
        sample_id="emoji_04",
        category="Emoji and Unicode edge cases",
        description="Right-to-Left (RTL) marks, directional overrides, and bidirectional text",
        text=(
            "English with Arabic and Hebrew fragments: "
            "The phrase \u202Bمرحبا بالعالم\u202C is Arabic, and \u202Bשלום עולם\u202C is Hebrew. "
            "Directional marks: LRM=\u200E, RLM=\u200F, LRE=\u202A, RLE=\u202B, PDF=\u202C."
        ),
    ),
    EvaluationSample(
        sample_id="emoji_05",
        category="Emoji and Unicode edge cases",
        description="Mathematical symbols, box drawing, dingbats, and high Plane 16 codepoints",
        text=(
            "Math and logic: ∀x ∈ ℝ, ∃y : x² + y² = 1 ∧ f(x) ≤ ∫₀^∞ e^(-t) dt. "
            "Box drawing: ┌─────────┬─────────┐ │ Table 1 │ Table 2 │ └─────────┴─────────┘. "
            "Plane 15/16 high boundary codepoint: \U00010ffff and PUA sentinel range."
        ),
    ),
]


def get_dataset() -> list[EvaluationSample]:
    """Return the complete standardized evaluation dataset."""
    return list(EVALUATION_DATASET)


def get_categories() -> list[str]:
    """Return the ordered list of unique evaluation categories."""
    seen: set[str] = set()
    categories: list[str] = []
    for sample in EVALUATION_DATASET:
        if sample.category not in seen:
            seen.add(sample.category)
            categories.append(sample.category)
    return categories
