import { SupportedLanguage } from '../config/languages';

const TAMIL_UNICODE_REGEX = /[\u0B80-\u0BFF]/;

const TANGLISH_COMMON_PATTERNS = [
  /\b(enna|panreenga|epdi|irukkeenga|sollunga|vaanga|ponga|aama|illa|venum|panna|pannum|teriyum|puriyala|eppadi|romba|nalla|illai|kudunga|podunga|theriyuma)\b/i,
  /\b(la|da|pa|ma|bro|machan|nanba|thala)\b/i,
  /(nga|ga|la|ley|chu|ttu|ren|rom)\b/i,
];

export function detectLanguage(text: string): SupportedLanguage {
  const trimmed = text.trim();
  if (!trimmed) return 'en';

  // Check for Tamil Unicode characters
  if (TAMIL_UNICODE_REGEX.test(trimmed)) {
    return 'ta';
  }

  // Check for Tanglish phonetic vocabulary and markers
  const lower = trimmed.toLowerCase();
  for (const pattern of TANGLISH_COMMON_PATTERNS) {
    if (pattern.test(lower)) {
      return 'tanglish';
    }
  }

  // Default to English
  return 'en';
}

export function getLanguageDisplayName(lang: SupportedLanguage): string {
  switch (lang) {
    case 'ta':
      return 'தமிழ் (Tamil)';
    case 'tanglish':
      return 'Tanglish (Romanized Tamil)';
    case 'en':
    default:
      return 'English';
  }
}
