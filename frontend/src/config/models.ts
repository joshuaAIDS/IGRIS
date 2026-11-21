export interface ModelSpec {
  id: string;
  name: string;
  family: string;
  params: string;
  quantization: string;
  contextWindow: string;
  contextTokens: number;
  desc: string;
  targetHardware?: string;
  status: 'Active' | 'Standby' | 'Remote' | 'Demo';
}

export const IGRIS_MODEL_CATALOG: Record<string, ModelSpec> = {
  'IGRIS-PROD-16L': {
    id: 'IGRIS-PROD-16L',
    name: 'IGRIS-Production-16L',
    family: 'IGRIS Multilingual SLM (Authoritative Production)',
    params: '79.7M (tied) / 96.5M (untied)',
    quantization: 'FP16 / INT8',
    contextWindow: '2,048',
    contextTokens: 2048,
    targetHardware: 'NVIDIA RTX 3050 Laptop GPU (6GB VRAM)',
    desc: 'Authoritative 16-layer decoder-only transformer (hidden: 512, intermediate: 2048, GQA 8:4, SwiGLU, RMSNorm eps=1e-5, RoPE theta=10000.0, tied embeddings). High-performance trilingual reasoning across Tamil Unicode, English, and Tanglish.',
    status: 'Standby',
  },
  'IGRIS-50M-BASELINE': {
    id: 'IGRIS-50M-BASELINE',
    name: 'IGRIS-50M-Baseline',
    family: 'IGRIS Conceptual Baseline',
    params: '51.6M (tied) / 68.4M (untied)',
    quantization: 'FP16 / INT8',
    contextWindow: '2,048',
    contextTokens: 2048,
    targetHardware: 'NVIDIA RTX 3050 (6GB VRAM) / Safe CPU Fallback',
    desc: 'Earlier 12-layer exploratory baseline architecture (hidden: 512, intermediate: 1376, GQA 8:4, SwiGLU, RMSNorm). Reconciled in Phase 23 audit.',
    status: 'Demo',
  },
  'IGRIS-CANDIDATE-A': {
    id: 'IGRIS-CANDIDATE-A',
    name: 'Candidate A Tokenizer (32K BPE)',
    family: 'IGRIS Linguistic Foundation',
    params: '32,768 Vocab',
    quantization: 'ByteLevel BPE',
    contextWindow: '2,048',
    contextTokens: 2048,
    targetHardware: 'CPU / GPU Unified Cache',
    desc: 'Production ByteLevel BPE tokenizer with 12 structural tokens, 256-byte fallback, SHA256: ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561.',
    status: 'Active',
  },
  'IGRIS-LOCAL-RUNTIME': {
    id: 'IGRIS-LOCAL-RUNTIME',
    name: 'IGRIS Local Runtime (HTTP/SSE)',
    family: 'Local Inference Gateway',
    params: '79.7M / 51.6M Runtime Bound',
    quantization: 'FP16 / INT8 Safe Fallback',
    contextWindow: '2,048',
    contextTokens: 2048,
    targetHardware: 'NVIDIA RTX 3050 6GB / Intel i5-13420H',
    desc: 'Official local FastAPI/Uvicorn HTTP & SSE streaming inference daemon on http://127.0.0.1:8000. Features real token counting with production tokenizer, full duplex cancellation, and hardware telemetry.',
    status: 'Remote',
  },
};

export const DEFAULT_MODEL_ID = 'IGRIS-PROD-16L';
