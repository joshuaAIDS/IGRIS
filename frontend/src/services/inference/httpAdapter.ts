import {
  CANDIDATE_A_METADATA,
  estimateCandidateATokens,
  formatCandidateAPrompt,
  TokenizerMetadata,
} from '../tokenizer/candidateA';
import { IInferenceAdapter } from './adapter.interface';
import {
  BackendHealthStatus,
  HardwareTelemetry,
  InferenceChunk,
  InferenceRequest,
  InferenceResponse,
  TokenizeResponse,
  TokenUsage,
} from './types';

export class IgrisHttpBackendAdapter implements IInferenceAdapter {
  readonly id = 'igris-http-adapter';
  readonly name = 'IGRIS Local Runtime Adapter (HTTP/SSE)';
  readonly isDemo = false;
  private currentAbortController: AbortController | null = null;

  async sendMessage(
    request: InferenceRequest,
    onChunk?: (chunk: InferenceChunk) => void,
    signal?: AbortSignal,
  ): Promise<InferenceResponse> {
    this.currentAbortController = new AbortController();
    const effectiveSignal = signal || this.currentAbortController.signal;

    const endpoint = request.endpointUrl || 'http://127.0.0.1:8000/v1/chat/completions';
    const startTime = performance.now();

    // Map history to standard chat turns
    const historyTurns = (request.history || []).map((msg) => ({
      role: msg.role as 'system' | 'user' | 'assistant',
      content: msg.content,
    }));
    historyTurns.push({ role: 'user', content: request.prompt });

    // Format prompt with Candidate A structural tokens
    const promptWithCandidateA = formatCandidateAPrompt(
      historyTurns,
      request.systemPrompt || 'You are IGRIS, an autonomous Voice-First Small Language Model.',
    );

    const payload = {
      model: request.modelId,
      messages: historyTurns,
      prompt: promptWithCandidateA,
      temperature: request.config.temperature,
      top_p: request.config.topP,
      max_tokens: request.config.maxTokens,
      stream: Boolean(request.config.streaming && onChunk),
    };

    let response: Response;
    try {
      response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: request.config.streaming ? 'text/event-stream' : 'application/json',
        },
        body: JSON.stringify(payload),
        signal: effectiveSignal,
      });
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        const error = new Error('Inference request was aborted');
        error.name = 'AbortError';
        throw error;
      }
      const message = err instanceof Error ? err.message : String(err);
      throw new Error(`Failed to connect to IGRIS backend runtime at ${endpoint}: ${message}`);
    }

    if (!response.ok) {
      let errorDetails = response.statusText;
      let errorCode = '';
      try {
        const json = await response.json();
        errorDetails = json.error?.message || json.detail || JSON.stringify(json);
        errorCode = json.error?.code || '';
      } catch {
        // Fall back to status text
      }
      if (response.status === 503 || errorCode === 'MODEL_NOT_TRAINED') {
        throw new Error(`[MODEL_NOT_TRAINED] ${errorDetails}`);
      }
      throw new Error(`IGRIS runtime error (${response.status}): ${errorDetails}`);
    }

    // Handle Streaming Response (SSE)
    if (request.config.streaming && onChunk && response.body) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let fullContent = '';
      let usage: TokenUsage | undefined;

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith(':')) continue;

            if (trimmed === 'data: [DONE]') {
              onChunk({ deltaText: '', isFinal: true });
              continue;
            }

            if (trimmed.startsWith('data: ')) {
              const dataStr = trimmed.slice(6);
              try {
                const parsed = JSON.parse(dataStr);
                const delta = parsed.choices?.[0]?.delta?.content || parsed.delta || '';
                if (delta) {
                  fullContent += delta;
                  onChunk({ deltaText: delta, isFinal: false });
                }
                if (parsed.usage) {
                  usage = {
                    promptTokens: parsed.usage.prompt_tokens,
                    completionTokens: parsed.usage.completion_tokens,
                    totalTokens: parsed.usage.total_tokens,
                    latencyMs: Math.round(performance.now() - startTime),
                  };
                }
              } catch {
                // Non-JSON SSE payload, treat as raw chunk
                fullContent += dataStr;
                onChunk({ deltaText: dataStr, isFinal: false });
              }
            }
          }
        }
      } catch (streamErr: unknown) {
        if (streamErr instanceof DOMException && streamErr.name === 'AbortError') {
          return {
            text: fullContent,
            usage: usage || {
              promptTokens: estimateCandidateATokens(request.prompt),
              completionTokens: estimateCandidateATokens(fullContent),
              totalTokens: estimateCandidateATokens(request.prompt) + estimateCandidateATokens(fullContent),
              latencyMs: Math.round(performance.now() - startTime),
            },
            isDemo: false,
            modelId: request.modelId,
            finishReason: 'abort',
          };
        }
        throw streamErr;
      }

      const totalLatency = Math.round(performance.now() - startTime);
      const promptTokens = usage?.promptTokens || estimateCandidateATokens(request.prompt);
      const completionTokens = usage?.completionTokens || estimateCandidateATokens(fullContent);

      return {
        text: fullContent,
        usage: {
          promptTokens,
          completionTokens,
          totalTokens: promptTokens + completionTokens,
          latencyMs: totalLatency,
          tokensPerSec:
            totalLatency > 0 ? Math.round((completionTokens / totalLatency) * 1000) : undefined,
        },
        isDemo: false,
        modelId: request.modelId,
        finishReason: 'stop',
      };
    }

    // Handle Standard Non-Streaming JSON Response
    const data = await response.json();
    const content =
      data.choices?.[0]?.message?.content || data.response || data.text || JSON.stringify(data);
    const latencyMs = Math.round(performance.now() - startTime);
    const promptTokens = data.usage?.prompt_tokens || estimateCandidateATokens(request.prompt);
    const completionTokens =
      data.usage?.completion_tokens || estimateCandidateATokens(content);

    return {
      text: content,
      usage: {
        promptTokens,
        completionTokens,
        totalTokens: promptTokens + completionTokens,
        latencyMs,
        tokensPerSec:
          latencyMs > 0 ? Math.round((completionTokens / latencyMs) * 1000) : undefined,
      },
      isDemo: false,
      modelId: request.modelId,
      finishReason: 'stop',
    };
  }

  abort(): void {
    if (this.currentAbortController) {
      this.currentAbortController.abort();
      this.currentAbortController = null;
    }
  }

  async checkHealth(endpointUrl?: string): Promise<BackendHealthStatus> {
    const rawEndpoint = endpointUrl || 'http://127.0.0.1:8000';
    const origin = rawEndpoint
      .replace(/\/chat\/completions\/?$/, '')
      .replace(/\/v1\/?$/, '')
      .replace(/\/$/, '');
    const healthUrl = `${origin}/health`;

    const start = performance.now();
    try {
      const response = await fetch(healthUrl, {
        method: 'GET',
        headers: { Accept: 'application/json' },
        signal: AbortSignal.timeout(3000),
      });

      const latencyMs = Math.round(performance.now() - start);
      if (response.ok) {
        let modelName = 'IGRIS-Production-16L';
        let isTrained = false;
        let modelState: 'MODEL LOADED' | 'MODEL NOT TRAINED' = 'MODEL NOT TRAINED';
        let hardware: HardwareTelemetry | undefined;
        let tokenizerStatus: any;
        let checkpointPath: string | null = null;

        try {
          const body = await response.json();
          if (body.model_name) modelName = body.model_name;
          if (body.model) modelName = body.model;
          isTrained = Boolean(body.model_loaded);
          if (body.model_state === 'MODEL_LOADED' || isTrained) {
            modelState = 'MODEL LOADED';
          } else {
            modelState = 'MODEL NOT TRAINED';
          }
          if (body.hardware) hardware = body.hardware;
          if (body.tokenizer) tokenizerStatus = body.tokenizer;
          if (body.checkpoint_path) checkpointPath = body.checkpoint_path;
        } catch {
          // Keep default
        }
        return {
          isConnected: true,
          isDemo: false,
          endpoint: origin,
          statusText: modelState,
          modelState,
          isTrained,
          latencyMs,
          modelName,
          hardware,
          tokenizerStatus,
          checkpointPath,
        };
      }

      return {
        isConnected: false,
        isDemo: false,
        endpoint: origin,
        statusText: `RUNTIME RETURNED HTTP ${response.status}`,
        latencyMs,
        error: `Health check failed with HTTP ${response.status}`,
      };
    } catch (err: unknown) {
      return {
        isConnected: false,
        isDemo: false,
        endpoint: origin,
        statusText: 'DISCONNECTED · STANDBY',
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  getTokenizerInfo(): TokenizerMetadata {
    return CANDIDATE_A_METADATA;
  }

  async tokenize(text: string, endpointUrl?: string): Promise<TokenizeResponse> {
    const rawEndpoint = endpointUrl || 'http://127.0.0.1:8000';
    const origin = rawEndpoint
      .replace(/\/chat\/completions\/?$/, '')
      .replace(/\/v1\/?$/, '')
      .replace(/\/$/, '');
    const tokenizeUrl = `${origin}/v1/tokenize`;

    const response = await fetch(tokenizeUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, add_special_tokens: false }),
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      throw new Error(`Tokenize endpoint returned HTTP ${response.status}`);
    }

    return (await response.json()) as TokenizeResponse;
  }

  async listModels(endpointUrl?: string): Promise<any[]> {
    const rawEndpoint = endpointUrl || 'http://127.0.0.1:8000';
    const origin = rawEndpoint
      .replace(/\/chat\/completions\/?$/, '')
      .replace(/\/v1\/?$/, '')
      .replace(/\/$/, '');
    const modelsUrl = `${origin}/v1/models`;

    const response = await fetch(modelsUrl, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(3000),
    });

    if (!response.ok) {
      throw new Error(`Models endpoint returned HTTP ${response.status}`);
    }

    const data = await response.json();
    return data.data || [];
  }
}
