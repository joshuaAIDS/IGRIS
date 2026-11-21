import test from 'node:test';
import assert from 'node:assert/strict';
import {
  CANDIDATE_A_METADATA,
  CANDIDATE_A_STRUCTURAL_TOKENS,
  CANDIDATE_A_VOCAB_SIZE,
  estimateCandidateATokens,
  formatCandidateAPrompt,
} from '../services/tokenizer/candidateA';

test('Candidate A: reserves exactly 12 structural special tokens in specification order', () => {
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS.length, 12);
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[0], '<|pad|>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[1], '<|begin_of_text|>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[2], '<|end_of_text|>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[3], '<think>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[4], '</think>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[5], '<action>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[6], '</action>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[7], '<action_result>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[8], '</action_result>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[9], '<|system|>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[10], '<|user|>');
  assert.equal(CANDIDATE_A_STRUCTURAL_TOKENS[11], '<|assistant|>');
});

test('Candidate A: configured with 32,768 vocabulary and byte fallback', () => {
  assert.equal(CANDIDATE_A_VOCAB_SIZE, 32_768);
  assert.equal(CANDIDATE_A_METADATA.vocabSize, 32_768);
  assert.equal(CANDIDATE_A_METADATA.byteFallback, true);
});

test('Candidate A: token estimation handles English, Tamil, and Tanglish linguistic ratios', () => {
  // Empty
  assert.equal(estimateCandidateATokens(''), 0);

  // English
  const enTokens = estimateCandidateATokens('Explain how IGRIS handles trilingual tokenization with Candidate A.');
  assert.ok(enTokens >= 8 && enTokens <= 16, `English token count expected ~11, got ${enTokens}`);

  // Tamil Unicode
  const taTokens = estimateCandidateATokens('இக்ரிஸ் தமிழ் மொழியை எவ்வாறு புரிந்துகொள்கிறது?');
  assert.ok(taTokens >= 6, `Tamil token count expected >= 6, got ${taTokens}`);

  // Tanglish
  const tanglishTokens = estimateCandidateATokens('IGRIS Tamil and English mix panni epdi answer pannum?');
  assert.ok(tanglishTokens >= 8, `Tanglish token count expected >= 8, got ${tanglishTokens}`);
});

test('Candidate A: formatCandidateAPrompt formats conversation turns with structural delimiters', () => {
  const formatted = formatCandidateAPrompt(
    [
      { role: 'user', content: 'Hello IGRIS' },
      { role: 'assistant', content: 'Greetings!' },
      { role: 'user', content: 'What is your model baseline?' },
    ],
    'System instructions for IGRIS',
  );

  assert.ok(formatted.startsWith('<|begin_of_text|>'));
  assert.ok(formatted.includes('<|system|>\nSystem instructions for IGRIS'));
  assert.ok(formatted.includes('<|user|>\nHello IGRIS'));
  assert.ok(formatted.includes('<|assistant|>\nGreetings!'));
  assert.ok(formatted.includes('<|user|>\nWhat is your model baseline?'));
  assert.ok(formatted.endsWith('<|assistant|>\n'));
});
