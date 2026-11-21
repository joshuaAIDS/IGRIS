import test from 'node:test';
import assert from 'node:assert/strict';
import { IgrisHttpBackendAdapter } from '../services/inference/httpAdapter';
import { DemoSimulationAdapter } from '../services/inference/demoAdapter';
import { InferenceRequest } from '../services/inference/types';

const LIVE_ENDPOINT = 'http://127.0.0.1:8000';

test('Live Backend Health: connects to running local runtime and confirms MODEL_NOT_TRAINED state', async (t) => {
  const adapter = new IgrisHttpBackendAdapter();
  const status = await adapter.checkHealth(LIVE_ENDPOINT);

  if (!status.isConnected) {
    t.skip('Live inference server offline at ' + LIVE_ENDPOINT);
    return;
  }

  assert.equal(status.isConnected, true, 'Server should be listening and connected on port 8000');
  assert.equal(status.isDemo, false, 'Live HTTP adapter must not report isDemo = true');
  assert.equal(status.modelState, 'MODEL NOT TRAINED', 'Untrained runtime must report MODEL NOT TRAINED');
  assert.equal(status.isTrained, false, 'isTrained must be false when no checkpoint is loaded');
  assert.ok(status.latencyMs !== undefined && status.latencyMs >= 0, 'Latency must be reported');
});

test('Live Backend Completions: trilingual requests are rejected with honest MODEL_NOT_TRAINED error', async (t) => {
  const adapter = new IgrisHttpBackendAdapter();
  const health = await adapter.checkHealth(LIVE_ENDPOINT);

  if (!health.isConnected) {
    t.skip('Live inference server offline at ' + LIVE_ENDPOINT);
    return;
  }

  const trilingualPrompts = [
    { lang: 'en', prompt: 'Explain the SwiGLU projection dimensions in IGRIS.' },
    { lang: 'ta', prompt: 'இக்ரிஸ் மாதிரியின் தமிழ் சொல்லகராதி அளவு என்ன?' },
    { lang: 'tanglish', prompt: 'IGRIS-la Candidate A tokenizer epdi work aagum?' },
  ];

  for (const item of trilingualPrompts) {
    const req: InferenceRequest = {
      prompt: item.prompt,
      modelId: 'igris-prod-16l',
      config: {
        temperature: 0.7,
        maxTokens: 64,
        topP: 0.9,
        streaming: false,
        returnUsage: true,
      },
      endpointUrl: `${LIVE_ENDPOINT}/v1/chat/completions`,
    };

    await assert.rejects(
      async () => {
        await adapter.sendMessage(req);
      },
      (err: Error) => {
        assert.match(
          err.message,
          /\[MODEL_NOT_TRAINED\]/,
          `Prompt in ${item.lang} must be rejected with [MODEL_NOT_TRAINED]`,
        );
        return true;
      },
    );
  }
});

test('Live Backend Streaming: streaming requests are also rejected with honest MODEL_NOT_TRAINED', async (t) => {
  const adapter = new IgrisHttpBackendAdapter();
  const health = await adapter.checkHealth(LIVE_ENDPOINT);

  if (!health.isConnected) {
    t.skip('Live inference server offline at ' + LIVE_ENDPOINT);
    return;
  }

  const req: InferenceRequest = {
    prompt: 'Streaming check for untrained model',
    modelId: 'igris-prod-16l',
    config: {
      temperature: 0.7,
      maxTokens: 64,
      topP: 0.9,
      streaming: true,
      returnUsage: true,
    },
    endpointUrl: `${LIVE_ENDPOINT}/v1/chat/completions`,
  };

  await assert.rejects(
    async () => {
      await adapter.sendMessage(req, (_chunk) => {});
    },
    (err: Error) => {
      assert.match(err.message, /\[MODEL_NOT_TRAINED\]/);
      return true;
    },
  );
});

test('Demo Mode Fallback: returns simulated output without fabricating real model execution', async () => {
  const demoAdapter = new DemoSimulationAdapter();
  const health = await demoAdapter.checkHealth();

  assert.equal(health.isConnected, false);
  assert.equal(health.isDemo, true);
  assert.equal(health.modelState, 'DEMO MODE');

  const req: InferenceRequest = {
    prompt: 'Demo query',
    modelId: 'igris-prod-16l',
    config: {
      temperature: 0.7,
      maxTokens: 64,
      topP: 0.9,
      streaming: false,
      returnUsage: true,
    },
  };

  const response = await demoAdapter.sendMessage(req);
  assert.equal(response.isDemo, true);
  assert.match(response.text, /\[IGRIS DEMO MODE\]/);
});
