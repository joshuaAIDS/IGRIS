import { SupportedLanguage } from '../../config/languages';

export interface InferenceConfig {
  temperature: number;
  maxTokens: number;
  topP: number;
  streaming: boolean;
  returnUsage: boolean;
}

export interface TokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  latencyMs: number;
  tokensPerSec?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  modelId?: string;
  timestamp: string;
  language?: SupportedLanguage;
  usage?: TokenUsage;
  isDemo?: boolean;
  error?: boolean;
}

export interface InferenceRequest {
  prompt: string;
  history?: ChatMessage[];
  modelId: string;
  config: InferenceConfig;
  endpointUrl?: string;
  language?: SupportedLanguage;
  systemPrompt?: string;
}

export interface InferenceChunk {
  deltaText: string;
  isFinal: boolean;
  usage?: TokenUsage;
  isDemo?: boolean;
  error?: string;
}

export interface InferenceResponse {
  text: string;
  usage: TokenUsage;
  isDemo: boolean;
  modelId: string;
  finishReason?: 'stop' | 'length' | 'abort' | 'error';
}

export type ModelLifecycleState =
  | 'DEMO MODE'
  | 'MODEL NOT TRAINED'
  | 'MODEL LOADED'
  | 'MODEL GENERATING';

export interface TokenPiece {
  id: number;
  piece: string;
  decoded: string;
  start?: number;
  end?: number;
}

export interface TokenizeResponse {
  tokens: TokenPiece[];
  token_count: number;
  character_count: number;
  byte_count: number;
  tokenizer_name: string;
  tokenizer_sha256: string;
}

export interface HardwareTelemetry {
  device?: string;
  device_name?: string;
  cuda_available?: boolean;
  total_vram_gb?: number;
  free_vram_gb?: number;
  cpu_architecture?: string;
  cpu_threads?: number;
  system_platform?: string;
  safe_for_gpu?: boolean;
  fallback_reason?: string | null;
  system_ram_total_gb?: number | null;
  system_ram_available_gb?: number | null;
  system_ram_used_gb?: number | null;
  system_ram_util_pct?: number | null;
}

export interface BackendHealthStatus {
  isConnected: boolean;
  isDemo: boolean;
  endpoint: string;
  statusText: string;
  latencyMs?: number;
  modelName?: string;
  modelState?: ModelLifecycleState;
  isTrained?: boolean;
  error?: string;
  hardware?: HardwareTelemetry;
  tokenizerStatus?: {
    name: string;
    vocab_size: number;
    sha256: string;
    verified: boolean;
    structural_tokens_count: number;
  };
  checkpointPath?: string | null;
}
