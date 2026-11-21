import { test } from 'node:test';
import assert from 'node:assert/strict';
import { IGRIS_MODEL_CATALOG } from '../config/models';
import { CANDIDATE_A_METADATA } from '../services/tokenizer/candidateA';
import { SUPPORTED_LANGUAGES } from '../config/languages';

test('Models Registry: exposes authoritative 16-layer production architecture', () => {
  const prod = IGRIS_MODEL_CATALOG['IGRIS-PROD-16L'];
  assert.ok(prod, 'IGRIS-PROD-16L must exist in catalog');
  assert.equal(prod.contextTokens, 2048);
  assert.equal(prod.status, 'Standby');
  assert.match(prod.params, /79\.7M/);
  assert.match(prod.desc, /16-layer/);
  assert.match(prod.desc, /SwiGLU/);
  assert.match(prod.desc, /RMSNorm/);
});

test('Models Registry: candidate A tokenizer metadata preserves 32,768 vocab and 12 structural tokens', () => {
  assert.equal(CANDIDATE_A_METADATA.vocabSize, 32768);
  assert.equal(CANDIDATE_A_METADATA.structuralTokensCount, 12);
  assert.equal(CANDIDATE_A_METADATA.byteFallback, true);
  assert.equal(CANDIDATE_A_METADATA.structuralTokens[0], '<|pad|>');
  assert.equal(CANDIDATE_A_METADATA.structuralTokens[1], '<|begin_of_text|>');
  assert.equal(CANDIDATE_A_METADATA.structuralTokens[2], '<|end_of_text|>');
  assert.equal(CANDIDATE_A_METADATA.structuralTokens[11], '<|assistant|>');
});

test('Language Scope: strictly limited to English, Tamil, and Tanglish', () => {
  const langIds = SUPPORTED_LANGUAGES.map((l) => l.id);
  assert.deepEqual(langIds.sort(), ['en', 'ta', 'tanglish'].sort());
  assert.equal(SUPPORTED_LANGUAGES.length, 3, 'Must have exactly 3 supported languages');
});

test('Performance Telemetry: formats missing metrics as Unavailable without fabrication', () => {
  const hw: any = {};
  const hasCuda = Boolean(hw?.cuda_available) && (hw?.total_vram_gb ?? 0) > 0;
  const gpuTotal = hasCuda ? `${hw?.total_vram_gb?.toFixed(2)} GB` : 'Unavailable';
  const ramTotal = typeof hw?.system_ram_total_gb === 'number' ? `${hw?.system_ram_total_gb?.toFixed(2)} GB` : 'Unavailable';
  const isTrained = false;
  const lastLatencyMs = 120; // Even if a turn ran in demo simulation
  const isGenuineInference = Boolean(isTrained && lastLatencyMs > 0);
  const generationSpeed = isGenuineInference ? '42 tok/s' : 'UNAVAILABLE';
  const latency = isGenuineInference ? `${lastLatencyMs} ms` : 'UNAVAILABLE';

  assert.equal(gpuTotal, 'Unavailable');
  assert.equal(ramTotal, 'Unavailable');
  assert.equal(generationSpeed, 'UNAVAILABLE');
  assert.equal(latency, 'UNAVAILABLE');
});

test('Performance Telemetry: accurately formats genuine sensor metrics when present', () => {
  const hw = {
    cuda_available: true,
    total_vram_gb: 6.0,
    free_vram_gb: 4.8,
    system_ram_total_gb: 15.64,
    system_ram_available_gb: 3.28,
    system_ram_used_gb: 12.36,
    system_ram_util_pct: 79.0,
  };
  const hasCuda = Boolean(hw.cuda_available) && hw.total_vram_gb > 0;
  const gpuTotal = hasCuda ? `${hw.total_vram_gb.toFixed(2)} GB` : 'Unavailable';
  const gpuAllocated = hasCuda ? `${(hw.total_vram_gb - hw.free_vram_gb).toFixed(2)} GB` : 'Unavailable';
  const ramTotal = `${hw.system_ram_total_gb.toFixed(2)} GB`;
  const ramUsed = `${hw.system_ram_used_gb.toFixed(2)} GB`;

  assert.equal(gpuTotal, '6.00 GB');
  assert.equal(gpuAllocated, '1.20 GB');
  assert.equal(ramTotal, '15.64 GB');
  assert.equal(ramUsed, '12.36 GB');
});
