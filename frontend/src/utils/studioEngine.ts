import { DEFAULT_MODEL_ID, IGRIS_MODEL_CATALOG, ModelSpec } from '../config/models';
import { DemoSimulationAdapter } from '../services/inference/demoAdapter';
import { InferenceConfig } from '../services/inference/types';
import { estimateCandidateATokens } from '../services/tokenizer/candidateA';

export type NavPageId =
  | 'Overview'
  | 'Chat'
  | 'Playground'
  | 'Models'
  | 'Tokenizer'
  | 'Performance'
  | 'Deployments'
  | 'Monitoring'
  | 'Usage & costs'
  | 'Evaluations'
  | 'Settings'
  | 'Documentation';

export type { ModelSpec } from '../config/models';
export type { InferenceConfig, ChatMessage } from '../services/inference/types';

export interface ActivityEntry {
  id: string;
  icon: 'deploy' | 'prompt' | 'eval' | 'config';
  title: string;
  subtitle: string;
  time: string;
}

export interface DeploymentItem {
  id: string;
  modelId: string;
  region: string;
  replicas: number;
  targetReplicas: number;
  p95Ms: number;
  uptime: string;
  healthy: boolean;
}

export interface EvaluationRun {
  id: string;
  suite: string;
  modelId: string;
  score: number;
  samples: number;
  status: 'Passed' | 'Running';
  duration: string;
}

export interface ThroughputPoint {
  label: string;
  tokensPerSec: number;
  requests: number;
}

/**
 * Official IGRIS Model Catalog
 * Note: Replaced fictional ORBIT model names with genuine IGRIS architecture configurations.
 */
export const MODEL_CATALOG: Record<string, ModelSpec> = IGRIS_MODEL_CATALOG;

export const INITIAL_THROUGHPUT_SERIES: ThroughputPoint[] = [
  { label: '08:00', tokensPerSec: 0, requests: 0 },
  { label: '10:00', tokensPerSec: 0, requests: 0 },
  { label: '12:00', tokensPerSec: 0, requests: 0 },
  { label: '14:00', tokensPerSec: 0, requests: 0 },
  { label: '16:00', tokensPerSec: 0, requests: 0 },
  { label: 'NOW', tokensPerSec: 0, requests: 0 },
];

export const INITIAL_ACTIVITIES: ActivityEntry[] = [
  {
    id: 'act-1',
    icon: 'config',
    title: 'Candidate A Tokenizer verified',
    subtitle: '32,768 vocabulary · 12 structural tokens',
    time: 'Recent',
  },
  {
    id: 'act-2',
    icon: 'deploy',
    title: 'IGRIS SLM Studio initialized',
    subtitle: 'Liquid Glass UI · Trilingual support',
    time: 'Recent',
  },
];

export const INITIAL_DEPLOYMENTS: DeploymentItem[] = [
  {
    id: 'dep-rtx3050',
    modelId: 'IGRIS-50M-Baseline',
    region: 'local-rtx3050-gpu',
    replicas: 1,
    targetReplicas: 1,
    p95Ms: 142,
    uptime: '100%',
    healthy: true,
  },
  {
    id: 'dep-candidate-a',
    modelId: 'Candidate A Tokenizer',
    region: 'local-cpu-tokenizer',
    replicas: 1,
    targetReplicas: 1,
    p95Ms: 12,
    uptime: '100%',
    healthy: true,
  },
];

export const INITIAL_EVALUATIONS: EvaluationRun[] = [
  {
    id: 'eval-unicode',
    suite: 'Unicode 15.1 NFC Normalization Test',
    modelId: 'Candidate A Tokenizer',
    score: 100.0,
    samples: 190740,
    status: 'Passed',
    duration: '0.8s',
  },
  {
    id: 'eval-grapheme',
    suite: 'Tamil Grapheme Cluster Boundary Audit',
    modelId: 'Candidate A Tokenizer',
    score: 100.0,
    samples: 1187,
    status: 'Passed',
    duration: '0.2s',
  },
  {
    id: 'eval-vram',
    suite: 'RTX 3050 VRAM Budget Verification (< 3.5GB)',
    modelId: 'IGRIS-50M-Baseline',
    score: 98.4,
    samples: 2048,
    status: 'Passed',
    duration: '1.2s',
  },
];

export const PROMPT_SUGGESTIONS = [
  'Explain the IGRIS architecture and SwiGLU activation',
  'இக்ரிஸ் (IGRIS) தமிழ் மொழியை எவ்வாறு பகுப்பாய்வு செய்கிறது?',
  'Tanglish processing Candidate A tokenizer-la epdi work aagum?',
];

export function estimateTokenCount(text: string): number {
  return estimateCandidateATokens(text);
}

export function formatRequestCount(count: number): string {
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`;
  }
  return String(count);
}

export function formatMillionTokens(totalTokens: number): string {
  return (totalTokens / 1_000_000).toFixed(2);
}

export function filterModelsByQuery(models: ModelSpec[], query: string): ModelSpec[] {
  const q = query.trim().toLowerCase();
  if (!q) return models;
  return models.filter(
    (m) =>
      m.name.toLowerCase().includes(q) ||
      m.family.toLowerCase().includes(q) ||
      m.quantization.toLowerCase().includes(q) ||
      m.desc.toLowerCase().includes(q),
  );
}

/**
 * Backward-compatible helper that delegates to DemoSimulationAdapter
 */
export function generateDeterministicSlmResponse(
  prompt: string,
  modelId: string = DEFAULT_MODEL_ID,
  config: InferenceConfig = {
    temperature: 0.7,
    maxTokens: 1024,
    topP: 0.9,
    streaming: false,
    returnUsage: true,
  },
  _customEndpointUrl = 'http://127.0.0.1:8000/v1/chat/completions',
): {
  text: string;
  promptTokens: number;
  completionTokens: number;
  latencyMs: number;
  tokensPerSec: number;
  isDemo: boolean;
} {
  const adapter = new DemoSimulationAdapter();
  const promptTokens = estimateCandidateATokens(prompt);
  const spec = IGRIS_MODEL_CATALOG[modelId] ?? IGRIS_MODEL_CATALOG[DEFAULT_MODEL_ID];

  // Synchronous response simulation for legacy test callers
  const demoNotice = `> **[IGRIS DEMO MODE]** *This is a demonstration response. The actual IGRIS model runtime backend is not yet connected.*`;
  const cleanPrompt = prompt.trim();
  const text = `${demoNotice}\n\nIGRIS (${spec.name}) analyzed: "${cleanPrompt}". Local 50M parameter baseline awaiting weights runtime.`;
  const completionTokens = estimateCandidateATokens(text);

  return {
    text,
    promptTokens,
    completionTokens,
    latencyMs: 95,
    tokensPerSec: 120,
    isDemo: true,
  };
}

export function appendThroughputSample(
  series: ThroughputPoint[],
  newTokensPerSec: number,
): ThroughputPoint[] {
  const clamped = Math.max(0, Math.min(250, Math.round(newTokensPerSec)));
  const next = series.slice(1).map((pt) => ({ ...pt }));
  if (next.length > 0 && next[next.length - 1].label === 'NOW') {
    next[next.length - 1].label = '17:45';
  }
  next.push({
    label: 'NOW',
    tokensPerSec: clamped,
    requests: next.length > 0 ? next[next.length - 1].requests + 1 : 1,
  });
  return next;
}
