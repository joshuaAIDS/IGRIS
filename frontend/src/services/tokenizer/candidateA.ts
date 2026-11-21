import { SupportedLanguage } from '../../config/languages';
import { detectLanguage } from '../../utils/languageDetector';

/**
 * Candidate A Structural Special Tokens
 * Exactly mapped from igris_candidate_a_v228.py
 */
export const CANDIDATE_A_STRUCTURAL_TOKENS = [
  '<|pad|>',
  '<|begin_of_text|>',
  '<|end_of_text|>',
  '<think>',
  '</think>',
  '<action>',
  '</action>',
  '<action_result>',
  '</action_result>',
  '<|system|>',
  '<|user|>',
  '<|assistant|>',
] as const;

export type CandidateAStructuralToken = (typeof CANDIDATE_A_STRUCTURAL_TOKENS)[number];

export const CANDIDATE_A_VOCAB_SIZE = 32_768;

export interface TokenizerMetadata {
  name: string;
  vocabSize: number;
  structuralTokensCount: number;
  structuralTokens: readonly string[];
  byteFallback: boolean;
  targetTpws: {
    english: string;
    tamilUnicode: string;
    tanglish: string;
  };
}

export const CANDIDATE_A_METADATA: TokenizerMetadata = {
  name: 'IGRIS Candidate A (ByteLevel BPE)',
  vocabSize: CANDIDATE_A_VOCAB_SIZE,
  structuralTokensCount: CANDIDATE_A_STRUCTURAL_TOKENS.length,
  structuralTokens: CANDIDATE_A_STRUCTURAL_TOKENS,
  byteFallback: true,
  targetTpws: {
    english: '1.15 – 1.30 TPW',
    tamilUnicode: '1.30 – 1.65 TPW',
    tanglish: '1.20 – 1.45 TPW',
  },
};

/**
 * Accurately estimates token count using Candidate A linguistic compression specifications.
 * - Tamil Unicode: ~1.45 TPW
 * - Tanglish: ~1.30 TPW
 * - English: ~1.20 TPW
 */
export function estimateCandidateATokens(text: string, overrideLanguage?: SupportedLanguage): number {
  const trimmed = text.trim();
  if (!trimmed) return 0;

  const lang = overrideLanguage ?? detectLanguage(trimmed);
  const words = trimmed.split(/\s+/).filter(Boolean);
  const wordCount = words.length;

  let multiplier = 1.25;
  if (lang === 'ta') {
    // Tamil Unicode characters: each grapheme cluster is 1 to 2 bytes, 1.45 TPW target
    multiplier = 1.45;
  } else if (lang === 'tanglish') {
    multiplier = 1.30;
  } else {
    multiplier = 1.20;
  }

  // Factor in punctuation, control markers, and minimum bound
  const punctuationCount = (text.match(/[,.!?;:()\[\]{}"'\\\/<>-]/g) || []).length;
  const estimated = Math.ceil(wordCount * multiplier + punctuationCount * 0.4);

  return Math.max(1, estimated);
}

/**
 * Format conversation turns with Candidate A structural prompt delimiters.
 */
export function formatCandidateAPrompt(
  turns: { role: 'system' | 'user' | 'assistant'; content: string }[],
  systemPrompt?: string,
): string {
  const chunks: string[] = ['<|begin_of_text|>'];

  if (systemPrompt) {
    chunks.push(`<|system|>\n${systemPrompt.trim()}`);
  }

  for (const turn of turns) {
    if (turn.role === 'user') {
      chunks.push(`<|user|>\n${turn.content.trim()}`);
    } else if (turn.role === 'assistant') {
      chunks.push(`<|assistant|>\n${turn.content.trim()}`);
    }
  }

  // Prepares the generation prompt by appending the assistant prefix
  chunks.push('<|assistant|>\n');
  return chunks.join('\n');
}
