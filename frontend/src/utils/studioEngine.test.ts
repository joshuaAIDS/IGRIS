import test from 'node:test';
import assert from 'node:assert/strict';
import {
  MODEL_CATALOG,
  INITIAL_THROUGHPUT_SERIES,
  appendThroughputSample,
  estimateTokenCount,
  filterModelsByQuery,
  formatMillionTokens,
  formatRequestCount,
  generateDeterministicSlmResponse,
} from './studioEngine';

test('estimateTokenCount handles empty and non-empty prompts accurately', () => {
  assert.equal(estimateTokenCount('   '), 0);
  assert.ok(estimateTokenCount('Explain the IGRIS architecture') >= 4);
});

test('formatRequestCount and formatMillionTokens format tabular metrics cleanly', () => {
  assert.equal(formatRequestCount(24800), '24.8k');
  assert.equal(formatRequestCount(842), '842');
  assert.equal(formatMillionTokens(1_420_000), '1.42');
});

test('filterModelsByQuery matches by IGRIS model name, quantization, and description', () => {
  const all = Object.values(MODEL_CATALOG);
  assert.equal(filterModelsByQuery(all, '').length, 4);
  const prodMatches = filterModelsByQuery(all, '16L');
  assert.equal(prodMatches.length, 1);
  assert.equal(prodMatches[0].id, 'IGRIS-PROD-16L');
  const baselineMatches = filterModelsByQuery(all, '50M');
  assert.equal(baselineMatches.length, 1);
  assert.equal(baselineMatches[0].id, 'IGRIS-50M-BASELINE');
  const candidateAMatches = filterModelsByQuery(all, 'Candidate A');
  assert.equal(candidateAMatches.length, 1);
  assert.equal(candidateAMatches[0].id, 'IGRIS-CANDIDATE-A');
});

test('generateDeterministicSlmResponse respects model selection and identifies as demo', () => {
  const res = generateDeterministicSlmResponse('Explain the SwiGLU activation', 'IGRIS-50M-BASELINE', {
    temperature: 0.4,
    maxTokens: 1024,
    topP: 0.9,
    streaming: false,
    returnUsage: true,
  });
  assert.match(res.text, /IGRIS-50M-Baseline/);
  assert.match(res.text, /\[IGRIS DEMO MODE\]/);
  assert.equal(res.isDemo, true);
  assert.ok(res.promptTokens > 0);
  assert.ok(res.completionTokens > 0);
});

test('appendThroughputSample preserves series length and clamps values', () => {
  const updated = appendThroughputSample(INITIAL_THROUGHPUT_SERIES, 94);
  assert.equal(updated.length, INITIAL_THROUGHPUT_SERIES.length);
  assert.equal(updated[updated.length - 1].label, 'NOW');
  assert.equal(updated[updated.length - 1].tokensPerSec, 94);
});
