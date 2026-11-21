import React, { useState } from 'react';
import { Check, Play, RefreshCw, Search, Server } from 'lucide-react';
import { IGRIS_MODEL_CATALOG, ModelSpec } from '../../config/models';
import { CANDIDATE_A_METADATA } from '../../services/tokenizer/candidateA';
import { NavPageId, ThroughputPoint } from '../../utils/studioEngine';
import { GlassButton } from '../glass/GlassButton';
import { GlassCard } from '../glass/GlassCard';
import { GlassInputField } from '../glass/GlassInputField';
import { GlassSlider } from '../glass/GlassSlider';
import { GlassSwitch } from '../glass/GlassSwitch';
import { ModelsRegistryCard } from './ModelsRegistryCard';
import { PerformanceTelemetryCard } from './PerformanceTelemetryCard';
import { RuntimeMonitorCard } from './RuntimeMonitorCard';
import { SettingsCard } from './SettingsCard';
import { ThroughputChartCard } from './ThroughputChartCard';
import { TokenizerLabCard } from './TokenizerLabCard';

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

interface WorkspaceViewsProps {
  activePage: NavPageId;
  selectedModelId: string;
  deployments: DeploymentItem[];
  evaluations: EvaluationRun[];
  throughputSeries: ThroughputPoint[];
  gpuUtil: number | null;
  memoryGb: number | null;
  queueDepth: number;
  customEndpointUrl: string;
  backendMode: 'demo' | 'http';
  backendConnected: boolean;
  glassFrost: number;
  glassBlur: number;
  onSelectModelAndOpenPlayground: (modelId: string) => void;
  onToggleDeploymentHealth: (id: string) => void;
  onScaleDeployment: (id: string, delta: number) => void;
  onRunEvaluation: (modelId: string) => void;
  onUpdateEndpointUrl: (url: string) => void;
  onUpdateBackendMode: (mode: 'demo' | 'http') => void;
  onTestBackendConnection: () => Promise<void>;
  onUpdateGlassSettings: (frost: number, blur: number) => void;
}

export function WorkspaceViews({
  activePage,
  selectedModelId,
  deployments,
  evaluations,
  throughputSeries,
  gpuUtil,
  memoryGb,
  queueDepth,
  customEndpointUrl,
  backendMode,
  backendConnected,
  glassFrost,
  glassBlur,
  onSelectModelAndOpenPlayground,
  onToggleDeploymentHealth,
  onScaleDeployment,
  onRunEvaluation,
  onUpdateEndpointUrl,
  onUpdateBackendMode,
  onTestBackendConnection,
  onUpdateGlassSettings,
}: WorkspaceViewsProps) {
  const [modelSearch, setModelSearch] = useState('');
  const [isTestingConnection, setIsTestingConnection] = useState(false);
  const [connectionTestResult, setConnectionTestResult] = useState<string | null>(null);

  const handleTestConnection = async () => {
    setIsTestingConnection(true);
    setConnectionTestResult(null);
    try {
      await onTestBackendConnection();
      setConnectionTestResult('Health check completed.');
    } catch (err) {
      setConnectionTestResult(`Connection test error: ${err}`);
    } finally {
      setIsTestingConnection(false);
    }
  };

  if (activePage === 'Models') {
    return (
      <ModelsRegistryCard
        selectedModelId={selectedModelId}
        onSelectModelAndOpenPlayground={onSelectModelAndOpenPlayground}
      />
    );
  }

  if (activePage === 'Tokenizer') {
    return <TokenizerLabCard />;
  }

  if (activePage === 'Performance') {
    return <PerformanceTelemetryCard />;
  }

  if (activePage === 'Deployments') {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {deployments.map((dep) => (
          <GlassCard key={dep.id} rounded="2xl" className="p-5 flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center justify-between gap-2">
                <span className="inline-flex items-center gap-1.5 font-mono-tabular text-[10px] text-white/70">
                  <Server size={12} /> {dep.region}
                </span>
                <span
                  className={`font-mono-tabular text-[10px] ${
                    dep.healthy ? 'text-[#72eab8]' : 'text-[#f5c879]'
                  }`}
                >
                  {dep.healthy ? '● ACTIVE' : '● STANDBY'}
                </span>
              </div>
              <h3 className="text-base font-bold text-white mt-2 mb-1">{dep.modelId}</h3>
              <p className="font-mono-tabular text-[11px] text-white/65 m-0">
                Uptime {dep.uptime} · Target RTX 3050 GPU
              </p>
            </div>

            <div className="frosted-well rounded-[16px] p-3 flex items-center justify-between">
              <div>
                <span className="block font-mono-tabular text-[9px] text-white/60">TARGET WORKERS</span>
                <b className="text-sm font-bold text-white tabular-nums">
                  {dep.replicas} / {dep.targetReplicas} active
                </b>
              </div>
              <div className="flex items-center gap-1.5">
                <GlassButton
                  size="sm"
                  onClick={() => onScaleDeployment(dep.id, -1)}
                  aria-label={`Scale down ${dep.modelId}`}
                >
                  −
                </GlassButton>
                <GlassButton
                  size="sm"
                  onClick={() => onScaleDeployment(dep.id, 1)}
                  aria-label={`Scale up ${dep.modelId}`}
                >
                  +
                </GlassButton>
              </div>
            </div>

            <GlassButton
              variant={dep.healthy ? 'glass' : 'primary'}
              onClick={() => onToggleDeploymentHealth(dep.id)}
            >
              {dep.healthy ? 'Pause runtime target' : 'Activate runtime target'}
            </GlassButton>
          </GlassCard>
        ))}
      </div>
    );
  }

  if (activePage === 'Monitoring') {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <ThroughputChartCard series={throughputSeries} tall />
        </div>
        <RuntimeMonitorCard
          gpuUtilPct={gpuUtil}
          vramAllocatedGb={memoryGb}
          totalMemoryGb={6}
          queueDepth={queueDepth}
          isLive={backendConnected}
        />
      </div>
    );
  }

  if (activePage === 'Usage & costs') {
    const costRows = [
      { model: 'IGRIS-50M-Baseline', target: 'NVIDIA RTX 3050 (6GB)', context: '2,048 tok', compute: 'Local Zero-Egress ($0.00)' },
      { model: 'Candidate A Tokenizer', target: 'ByteLevel BPE 32K', context: '12 Special Tokens', compute: 'Subword Engine ($0.00)' },
      { model: 'IGRIS Local Runtime Daemon', target: 'FastAPI / PyTorch', context: 'HTTP / SSE', compute: 'Loopback Daemon ($0.00)' },
    ];
    return (
      <GlassCard rounded="2xl" className="p-5">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
          <div>
            <h2 className="text-sm font-bold text-white m-0">Zero-Egress Compute Allocation</h2>
            <p className="text-xs text-white/70 mt-1 mb-0">
              IGRIS operates fully locally on consumer hardware without external AI API dependencies.
            </p>
          </div>
          <span className="frosted-glass-bright rounded-full px-3 py-1.5 text-[11px] font-mono-tabular text-[#72eab8]">
            PRIVATE OFFLINE RUNTIME: $0.00 EGRESS
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-white/15 font-mono-tabular text-[10px] text-white/60">
                <th className="py-2.5 pr-4 font-medium">IGRIS SUBSYSTEM</th>
                <th className="py-2.5 px-4 font-medium">EXECUTION TARGET</th>
                <th className="py-2.5 px-4 font-medium">SPECIFICATION</th>
                <th className="py-2.5 pl-4 font-medium text-right">COST ALLOCATION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {costRows.map((row) => (
                <tr key={row.model} className="hover:bg-white/5 transition-colors">
                  <td className="py-3 pr-4 font-semibold text-white">{row.model}</td>
                  <td className="py-3 px-4 font-mono-tabular text-white/85">{row.target}</td>
                  <td className="py-3 px-4 font-mono-tabular text-white/85">{row.context}</td>
                  <td className="py-3 pl-4 font-mono-tabular text-right text-[#a9f1ff]">{row.compute}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    );
  }

  if (activePage === 'Evaluations') {
    return (
      <div className="space-y-4">
        <GlassCard rounded="2xl" className="p-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold text-white m-0">Trilingual Benchmark & Quality Gates</h2>
            <p className="text-xs text-white/70 mt-1 mb-0">
              Validated quality gates for Unicode 15.1, Candidate A BPE compression, and hardware memory budgets.
            </p>
          </div>
          <GlassButton
            variant="primary"
            onClick={() => onRunEvaluation(selectedModelId)}
          >
            <Play size={13} /> Run validation suite
          </GlassButton>
        </GlassCard>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {evaluations.map((ev) => (
            <GlassCard key={ev.id} rounded="2xl" className="p-4 space-y-3">
              <div className="flex items-center justify-between text-[10px] font-mono-tabular">
                <span className="text-white/65">{ev.modelId}</span>
                <span className="text-[#72eab8]">{ev.status.toUpperCase()}</span>
              </div>
              <h3 className="text-sm font-bold text-white m-0">{ev.suite}</h3>
              <div className="flex items-baseline justify-between pt-2 border-t border-white/12">
                <span className="text-2xl font-bold text-white tabular-nums">
                  {ev.score.toFixed(1)}%
                </span>
                <span className="font-mono-tabular text-[10px] text-white/60">
                  {ev.samples} samples · {ev.duration}
                </span>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    );
  }

  if (activePage === 'Settings') {
    return (
      <SettingsCard
        customEndpointUrl={customEndpointUrl}
        backendMode={backendMode}
        backendConnected={backendConnected}
        glassFrost={glassFrost}
        glassBlur={glassBlur}
        onUpdateEndpointUrl={onUpdateEndpointUrl}
        onUpdateBackendMode={onUpdateBackendMode}
        onTestBackendConnection={onTestBackendConnection}
        onUpdateGlassSettings={onUpdateGlassSettings}
      />
    );
  }

  // Documentation Workspace
  return (
    <GlassCard rounded="2xl" className="p-6 space-y-5">
      <div className="flex items-center justify-between pb-3 border-b border-white/15">
        <div>
          <h2 className="text-base font-bold text-white m-0">IGRIS System Architecture & Developer Guide</h2>
          <p className="text-xs text-white/75 mt-1 mb-0">
            Voice-First Autonomous Small Language Model (SLM) · Built from first principles.
          </p>
        </div>
        <span className="font-mono-tabular text-[11px] text-[#82ecff] px-3 py-1 rounded-full frosted-glass-bright">
          PHASE 3B.53 SPECIFICATION
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="frosted-well rounded-[18px] p-4 space-y-2">
          <div className="font-mono-tabular text-[10px] text-[#a9f1ff] uppercase">TRILINGUAL ENGINE</div>
          <h4 className="text-xs font-bold text-white m-0">Candidate A Tokenizer</h4>
          <p className="text-[11px] text-white/70 m-0 leading-relaxed">
            32,768 ByteLevel BPE vocabulary with 12 structural tokens and 256-byte fallback. Tuned specifically for English, Tamil Unicode (தமிழ்), and Tanglish.
          </p>
        </div>

        <div className="frosted-well rounded-[18px] p-4 space-y-2">
          <div className="font-mono-tabular text-[10px] text-[#a9f1ff] uppercase">MODEL CORE</div>
          <h4 className="text-xs font-bold text-white m-0">50M Parameter Baseline</h4>
          <p className="text-[11px] text-white/70 m-0 leading-relaxed">
            Decoder-only Transformer with Pre-LayerNorm RMSNorm, SwiGLU activation, RoPE embeddings, and GQA (8 query / 4 KV heads) tailored for RTX 3050.
          </p>
        </div>

        <div className="frosted-well rounded-[18px] p-4 space-y-2">
          <div className="font-mono-tabular text-[10px] text-[#a9f1ff] uppercase">SAFETY POLICY</div>
          <h4 className="text-xs font-bold text-white m-0">Three-Tier Automation Gate</h4>
          <p className="text-[11px] text-white/70 m-0 leading-relaxed">
            Strict human-in-the-loop authorization policy governing desktop commands and OS interactions. Destructive actions blocked by default.
          </p>
        </div>
      </div>

      <div className="pt-2 border-t border-white/10 font-mono-tabular text-[11px] text-white/60 flex flex-wrap gap-x-6 gap-y-2">
        <span>⌘K / Ctrl+K: Quick command palette</span>
        <span>↵: Send message</span>
        <span>Stop Button: Aborts generation stream</span>
      </div>
    </GlassCard>
  );
}
