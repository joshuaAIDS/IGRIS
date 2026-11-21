import test from 'node:test';
import assert from 'node:assert/strict';
import { DemoSimulationAdapter } from '../services/inference/demoAdapter';
import { IgrisHttpBackendAdapter } from '../services/inference/httpAdapter';
import { InferenceRequest } from '../services/inference/types';

test('DemoSimulationAdapter: identifies as demo and returns demo notice banner', async () => {
  const adapter = new DemoSimulationAdapter();
  assert.equal(adapter.isDemo, true);

  const req: InferenceRequest = {
    prompt: 'What is the SwiGLU hidden dimension for IGRIS?',
    modelId: 'IGRIS-50M-BASELINE',
    config: {
      temperature: 0.7,
      maxTokens: 512,
      topP: 0.9,
      streaming: false,
      returnUsage: true,
    },
    language: 'en',
  };

  const response = await adapter.sendMessage(req);
  assert.equal(response.isDemo, true);
  assert.match(response.text, /\[IGRIS DEMO MODE\]/);
  assert.match(response.text, /50M Parameter Baseline/);
  assert.ok(response.usage.promptTokens > 0);
  assert.ok(response.usage.completionTokens > 0);
  assert.ok(response.usage.latencyMs > 0);
});

test('DemoSimulationAdapter: responds in Tamil Unicode when Tamil prompt is provided', async () => {
  const adapter = new DemoSimulationAdapter();
  const req: InferenceRequest = {
    prompt: 'இக்ரிஸ் மாடலின் கட்டமைப்பு பற்றி கூறுங்கள்.',
    modelId: 'IGRIS-50M-BASELINE',
    config: {
      temperature: 0.7,
      maxTokens: 512,
      topP: 0.9,
      streaming: false,
      returnUsage: true,
    },
    language: 'ta',
  };

  const response = await adapter.sendMessage(req);
  assert.equal(response.isDemo, true);
  assert.match(response.text, /வணக்கம்/);
  assert.match(response.text, /இக்ரிஸ்/);
  assert.match(response.text, /சொல்லகராதி/);
});

test('DemoSimulationAdapter: responds in Tanglish when Tanglish prompt is provided', async () => {
  const adapter = new DemoSimulationAdapter();
  const req: InferenceRequest = {
    prompt: 'IGRIS architecture epdi design panni irukkeenga?',
    modelId: 'IGRIS-50M-BASELINE',
    config: {
      temperature: 0.7,
      maxTokens: 512,
      topP: 0.9,
      streaming: false,
      returnUsage: true,
    },
    language: 'tanglish',
  };

  const response = await adapter.sendMessage(req);
  assert.equal(response.isDemo, true);
  assert.match(response.text, /Vanakkam/);
  assert.match(response.text, /Tanglish/);
});

test('DemoSimulationAdapter: streaming emits chunks progressively', async () => {
  const adapter = new DemoSimulationAdapter();
  const req: InferenceRequest = {
    prompt: 'Explain Candidate A tokenizer',
    modelId: 'IGRIS-50M-BASELINE',
    config: {
      temperature: 0.7,
      maxTokens: 256,
      topP: 0.9,
      streaming: true,
      returnUsage: true,
    },
    language: 'en',
  };

  const chunks: string[] = [];
  let isFinalSeen = false;

  const response = await adapter.sendMessage(req, (chunk) => {
    chunks.push(chunk.deltaText);
    if (chunk.isFinal) isFinalSeen = true;
  });

  assert.ok(chunks.length > 5, 'Streaming should emit multiple chunks');
  assert.equal(isFinalSeen, true, 'isFinal should be signaled on last chunk');
  assert.equal(chunks.join(''), response.text);
});

test('DemoSimulationAdapter: cancellation immediately halts stream and marks finishReason as abort', async () => {
  const adapter = new DemoSimulationAdapter();
  const abortCtrl = new AbortController();

  const req: InferenceRequest = {
    prompt: 'Generate a long response that will be cancelled',
    modelId: 'IGRIS-50M-BASELINE',
    config: {
      temperature: 0.7,
      maxTokens: 1024,
      topP: 0.9,
      streaming: true,
      returnUsage: true,
    },
    language: 'en',
  };

  let chunksCount = 0;
  const promise = adapter.sendMessage(
    req,
    (_chunk) => {
      chunksCount++;
      if (chunksCount === 2) {
        abortCtrl.abort(); // Cancel during streaming turn
      }
    },
    abortCtrl.signal,
  );

  const response = await promise;
  assert.equal(response.finishReason, 'abort');
  assert.ok(response.text.length > 0);
});

test('IgrisHttpBackendAdapter: handles backend connection refusal gracefully with descriptive error', async () => {
  const adapter = new IgrisHttpBackendAdapter();
  const req: InferenceRequest = {
    prompt: 'Testing connection to offline backend port',
    modelId: 'IGRIS-50M-BASELINE',
    config: {
      temperature: 0.7,
      maxTokens: 128,
      topP: 0.9,
      streaming: false,
      returnUsage: true,
    },
    endpointUrl: 'http://127.0.0.1:59999/v1/chat/completions', // Unused port
  };

  await assert.rejects(
    async () => {
      await adapter.sendMessage(req);
    },
    (err: Error) => {
      assert.match(err.message, /Failed to connect to IGRIS backend runtime/);
      return true;
    },
  );
});

test('IgrisHttpBackendAdapter: health check on offline endpoint returns isConnected false', async () => {
  const adapter = new IgrisHttpBackendAdapter();
  const status = await adapter.checkHealth('http://127.0.0.1:59999/v1');

  assert.equal(status.isConnected, false);
  assert.equal(status.isDemo, false);
  assert.equal(status.statusText, 'DISCONNECTED · STANDBY');
  assert.ok(status.error);
});
