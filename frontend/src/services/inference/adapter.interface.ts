import { TokenizerMetadata } from '../tokenizer/candidateA';
import {
  BackendHealthStatus,
  InferenceChunk,
  InferenceRequest,
  InferenceResponse,
} from './types';

export interface IInferenceAdapter {
  readonly id: string;
  readonly name: string;
  readonly isDemo: boolean;

  /**
   * Send a prompt request to the inference backend.
   * Supports streaming chunks via onChunk callback and cancellation via AbortSignal.
   */
  sendMessage(
    request: InferenceRequest,
    onChunk?: (chunk: InferenceChunk) => void,
    signal?: AbortSignal,
  ): Promise<InferenceResponse>;

  /**
   * Health and connectivity check.
   */
  checkHealth(endpointUrl?: string): Promise<BackendHealthStatus>;

  /**
   * Access to Candidate A tokenizer metadata and configuration.
   */
  getTokenizerInfo(): TokenizerMetadata;

  /**
   * Abort active generation.
   */
  abort(): void;
}
