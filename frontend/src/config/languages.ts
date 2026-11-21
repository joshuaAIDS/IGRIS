export type SupportedLanguage = 'en' | 'ta' | 'tanglish';

export interface LanguageOption {
  id: SupportedLanguage;
  name: string;
  nativeName: string;
  badge: string;
  samplePrompt: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  {
    id: 'en',
    name: 'English',
    nativeName: 'English',
    badge: 'EN',
    samplePrompt: 'Explain how IGRIS coordinates trilingual reasoning within its 50M parameter baseline.',
  },
  {
    id: 'ta',
    name: 'Tamil',
    nativeName: 'தமிழ்',
    badge: 'தமிழ்',
    samplePrompt: 'இக்ரிஸ் (IGRIS) தமிழ் மொழியின் எழுத்துக்களை எவ்வாறு சிறப்பான முறையில் பகுப்பாய்வு செய்கிறது?',
  },
  {
    id: 'tanglish',
    name: 'Tanglish',
    nativeName: 'Tanglish',
    badge: 'Tanglish',
    samplePrompt: 'IGRIS Tamil and English mix panni epdi seamless-aa decode pannum?',
  },
];

export const PROMPT_SUGGESTIONS: { label: string; text: string; language: SupportedLanguage }[] = [
  {
    label: 'English Architecture',
    text: 'Explain the custom Transformer architecture and SwiGLU activation of IGRIS.',
    language: 'en',
  },
  {
    label: 'தமிழ் கட்டமைப்பு (Tamil)',
    text: 'இக்ரிஸ் (IGRIS) மாடலின் தமிழ் டோக்கனைசேஷன் சிறப்பம்சங்களை விவரி.',
    language: 'ta',
  },
  {
    label: 'Tanglish Processing',
    text: 'Candidate A tokenizer Tanglish digraphs like "zh", "dh", "th" epdi normalize pannuthu?',
    language: 'tanglish',
  },
  {
    label: 'Desktop Safety Model',
    text: 'How does IGRIS enforce the three-tier permission gate for desktop automation?',
    language: 'en',
  },
];
