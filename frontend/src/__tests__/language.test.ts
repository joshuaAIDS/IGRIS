import test from 'node:test';
import assert from 'node:assert/strict';
import { SUPPORTED_LANGUAGES } from '../config/languages';
import { detectLanguage, getLanguageDisplayName } from '../utils/languageDetector';

test('Language Support: strictly limited to English, Tamil, and Tanglish', () => {
  assert.equal(SUPPORTED_LANGUAGES.length, 3);
  const ids = SUPPORTED_LANGUAGES.map((l) => l.id).sort();
  assert.deepEqual(ids, ['en', 'ta', 'tanglish']);
});

test('detectLanguage: identifies Tamil Unicode text accurately', () => {
  assert.equal(detectLanguage('வணக்கம்'), 'ta');
  assert.equal(detectLanguage('இக்ரிஸ் மாதிரி எவ்வாறு இயங்குகிறது?'), 'ta');
  assert.equal(detectLanguage('தமிழ் மொழியின் அழகு'), 'ta');
});

test('detectLanguage: identifies Tanglish phonetic markers accurately', () => {
  assert.equal(detectLanguage('Enna panreenga bro?'), 'tanglish');
  assert.equal(detectLanguage('Epdi irukkeenga thala?'), 'tanglish');
  assert.equal(detectLanguage('Idhu romba nalla model-aa irukku'), 'tanglish');
  assert.equal(detectLanguage('IGRIS tamil and english mix panni sollunga'), 'tanglish');
});

test('detectLanguage: defaults to English for standard Latin script', () => {
  assert.equal(detectLanguage('What is the context window length for IGRIS?'), 'en');
  assert.equal(detectLanguage('Explain the RMSNorm and SwiGLU formulations.'), 'en');
  assert.equal(detectLanguage('How does GQA 8:4 reduce KV cache memory?'), 'en');
});

test('getLanguageDisplayName: returns appropriate display strings', () => {
  assert.equal(getLanguageDisplayName('en'), 'English');
  assert.equal(getLanguageDisplayName('ta'), 'தமிழ் (Tamil)');
  assert.equal(getLanguageDisplayName('tanglish'), 'Tanglish (Romanized Tamil)');
});
