import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Plus } from 'lucide-react';
import { DeepSpaceBackground } from './components/background/DeepSpaceBackground';
import { GlassButton } from './components/glass/GlassButton';
import { GlassNavigationBar } from './components/glass/GlassNavigationBar';
import { LiquidGlassFilter } from './components/glass/LiquidGlassFilter';
import { CommandPaletteModal } from './components/studio/CommandPaletteModal';
import { InferenceControlsCard } from './components/studio/InferenceControlsCard';
import { MetricsStrip } from './components/studio/MetricsStrip';
import { ModelSelectionCard } from './components/studio/ModelSelectionCard';
import { PlaygroundPanel } from './components/studio/PlaygroundPanel';
import { RecentActivityCard } from './components/studio/RecentActivityCard';
import { RuntimeMonitorCard } from './components/studio/RuntimeMonitorCard';
import { Sidebar } from './components/studio/Sidebar';
import { ThroughputChartCard } from './components/studio/ThroughputChartCard';
import {
  DeploymentItem,
  EvaluationRun,
  WorkspaceViews,
} from './components/studio/WorkspaceViews';
import { DEFAULT_MODEL_ID, IGRIS_MODEL_CATALOG } from './config/models';
import { ConversationProvider, useConversation } from './context/ConversationContext';
import { TelemetryProvider, useTelemetry } from './context/TelemetryContext';
import { useLiquidGlassProximity } from './hooks/useLiquidGlassProximity';
import { ActivityEntry, NavPageId } from './utils/studioEngine';

const PAGE_HEADINGS: Record<NavPageId, { eyebrow: string; title: string; subtitle: string }> = {
  Overview: {
    eyebrow: 'IGRIS WORKSPACE / 01',
    title: 'Trilingual Model Workspace',
    subtitle: 'Interact with IGRIS across English, தமிழ் (Tamil), and Tanglish with zero-egress privacy.',
  },
  Chat: {
    eyebrow: 'INTERACTIVE INFERENCE / 02',
    title: 'IGRIS Studio Chat',
    subtitle: 'Full-duplex trilingual chat, streaming inference, and conversation history.',
  },
  Playground: {
    eyebrow: 'INTERACTIVE INFERENCE / 02',
    title: 'Playground & Chat Interface',
    subtitle: 'Test trilingual prompts, Candidate A tokenization, decoding parameters, and streaming responses.',
  },
  Models: {
    eyebrow: 'CHECKPOINT REGISTRY / 03',
    title: 'IGRIS Architecture Registry',
    subtitle: 'Inspect model inventory, architectural configurations, checkpoint availability, and honest model state.',
  },
  Tokenizer: {
    eyebrow: 'TOKENIZER LAB / 04',
    title: 'Candidate A Tokenizer Lab',
    subtitle: 'Inspect verified 32,768 ByteLevel BPE tokenization, token IDs, pieces, decoded text, and exact ratios.',
  },
  Performance: {
    eyebrow: 'SYSTEM OBSERVABILITY / 05',
    title: 'Hardware & Inference Performance',
    subtitle: 'Actual measured GPU VRAM, system RAM, generation throughput, and end-to-end request latency.',
  },
  Deployments: {
    eyebrow: 'RUNTIME TARGETS / 04',
    title: 'Deployments & Node Targets',
    subtitle: 'Manage local inference daemon targets, GPU memory budgets, and worker status.',
  },
  Monitoring: {
    eyebrow: 'SYSTEM OBSERVABILITY / 05',
    title: 'Monitoring & Live Telemetry',
    subtitle: 'Observe prompt completion rate, Candidate A token usage, and local execution status.',
  },
  'Usage & costs': {
    eyebrow: 'RESOURCE LEDGER / 06',
    title: 'Compute & Token Allocation',
    subtitle: 'Track zero-egress offline execution and private GPU compute savings.',
  },
  Evaluations: {
    eyebrow: 'QUALITY BENCHMARKS / 07',
    title: 'Evaluations & Quality Gates',
    subtitle: 'Verify Unicode 15.1 conformance, Candidate A tokenization ratios, and hardware constraints.',
  },
  Settings: {
    eyebrow: 'STUDIO PREFERENCES / 08',
    title: 'Settings & Backend Connection',
    subtitle: 'Configure local IGRIS inference runtime endpoint and calibrate liquid-glass optical properties.',
  },
  Documentation: {
    eyebrow: 'SYSTEM ARCHITECTURE / 09',
    title: 'IGRIS System Architecture & Guide',
    subtitle: 'Voice-First SLM specifications, trilingual Candidate A tokenizer design, and safety policies.',
  },
};

const INITIAL_DEPLOYMENTS: DeploymentItem[] = [
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

const INITIAL_EVALUATIONS: EvaluationRun[] = [
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

const INITIAL_ACTIVITIES: ActivityEntry[] = [
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

function StudioInner() {
  const [activePage, setActivePage] = useState<NavPageId>('Overview');
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [environment, setEnvironment] = useState<'Development' | 'Production'>('Development');

  const [selectedModelId, setSelectedModelId] = useState<string>(DEFAULT_MODEL_ID);
  const [deployments, setDeployments] = useState<DeploymentItem[]>(INITIAL_DEPLOYMENTS);
  const [evaluations, setEvaluations] = useState<EvaluationRun[]>(INITIAL_EVALUATIONS);
  const [activities, setActivities] = useState<ActivityEntry[]>(INITIAL_ACTIVITIES);

  const [glassFrost, setGlassFrost] = useState<number>(0.1);
  const [glassBlur, setGlassBlur] = useState<number>(26);

  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const toastTimerRef = useRef<number | null>(null);

  const {
    activeSessionId,
    createNewSession,
    inferenceConfig,
    setInferenceConfig,
    backendStatus,
    customEndpointUrl,
    setCustomEndpointUrl,
    setBackendMode,
    checkBackendHealth,
  } = useConversation();

  const {
    sessionRequests,
    sessionTokens,
    lastLatencyMs,
    throughputHistory,
    gpuUtilPct,
    vramAllocatedGb,
    queueDepth,
  } = useTelemetry();

  const showToast = useCallback((text: string) => {
    setToastMessage(text);
    if (toastTimerRef.current) {
      window.clearTimeout(toastTimerRef.current);
    }
    toastTimerRef.current = window.setTimeout(() => {
      setToastMessage(null);
    }, 2400);
  }, []);

  useEffect(() => {
    document.documentElement.style.setProperty('--glass-frost', String(glassFrost));
    document.documentElement.style.setProperty('--glass-blur', `${glassBlur}px`);
  }, [glassFrost, glassBlur]);

  useLiquidGlassProximity(glassFrost);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setCommandPaletteOpen((open) => !open);
      } else if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
        setMobileNavOpen(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => {
      window.removeEventListener('keydown', onKeyDown);
      if (toastTimerRef.current) window.clearTimeout(toastTimerRef.current);
    };
  }, []);

  const pushActivity = useCallback(
    (entry: Omit<ActivityEntry, 'id' | 'time'>) => {
      setActivities((prev) => [
        {
          ...entry,
          id: `act-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
          time: 'Just now',
        },
        ...prev,
      ]);
    },
    [],
  );

  const handleSelectModel = useCallback(
    (modelId: string) => {
      setSelectedModelId(modelId);
      const spec = IGRIS_MODEL_CATALOG[modelId] ?? IGRIS_MODEL_CATALOG[DEFAULT_MODEL_ID];
      showToast(`Selected ${spec.name}`);
      pushActivity({
        icon: 'config',
        title: 'Model checkpoint selected',
        subtitle: `${spec.name} · ${spec.params}`,
      });
    },
    [pushActivity, showToast],
  );

  const handleNewSession = useCallback(() => {
    const newId = createNewSession(selectedModelId);
    if (activePage !== 'Overview' && activePage !== 'Playground') {
      setActivePage('Playground');
    }
    pushActivity({
      icon: 'prompt',
      title: 'New conversation session',
      subtitle: `${selectedModelId} · #${newId}`,
    });
    showToast(`New session #${newId} ready`);
  }, [activePage, createNewSession, pushActivity, selectedModelId, showToast]);

  const handleToggleDeploymentHealth = (id: string) => {
    setDeployments((prev) =>
      prev.map((d) => (d.id === id ? { ...d, healthy: !d.healthy } : d)),
    );
    showToast('Deployment state updated');
  };

  const handleScaleDeployment = (id: string, delta: number) => {
    setDeployments((prev) =>
      prev.map((d) => {
        if (d.id !== id) return d;
        const nextReplicas = Math.max(1, Math.min(4, d.replicas + delta));
        return { ...d, replicas: nextReplicas, targetReplicas: nextReplicas };
      }),
    );
    showToast('Target replicas updated');
  };

  const handleRunEvaluation = (modelId: string) => {
    const newEval: EvaluationRun = {
      id: `eval-${Date.now()}`,
      suite: 'Candidate A Tokenizer Compression Regression Check',
      modelId,
      score: 100.0,
      samples: 500,
      status: 'Passed',
      duration: '42ms',
    };
    setEvaluations((prev) => [newEval, ...prev]);
    pushActivity({
      icon: 'eval',
      title: 'Validation suite passed',
      subtitle: `${modelId} · 100.0%`,
    });
    showToast(`Validation passed for ${modelId}`);
  };

  const activeHeading = PAGE_HEADINGS[activePage];
  const activeSpec = IGRIS_MODEL_CATALOG[selectedModelId] ?? IGRIS_MODEL_CATALOG[DEFAULT_MODEL_ID];

  return (
    <div className="relative min-h-screen text-white">
      {/* SVG Liquid Glass Chromatic Displacement Filter */}
      <LiquidGlassFilter blurStdDev={Number(((glassBlur / 26) * 1.05).toFixed(2))} />

      {/* Preserved Deep Space Cosmic Animated Three.js Background */}
      <DeepSpaceBackground />

      <div className="relative z-10 flex min-h-screen max-w-[1680px] mx-auto">
        <Sidebar
          activePage={activePage}
          onSelectPage={setActivePage}
          mobileOpen={mobileNavOpen}
          onCloseMobile={() => setMobileNavOpen(false)}
          runtimeLabel={
            backendStatus.isConnected
              ? 'LOCAL RUNTIME · CONNECTED'
              : backendStatus.isDemo
                ? 'DEMO SIMULATION · STANDBY'
                : 'DISCONNECTED · STANDBY'
          }
        />

        <main className="flex-1 min-w-0 px-4 py-5 sm:px-6 lg:px-8 lg:py-6">
          <GlassNavigationBar
            activePage={activePage}
            environment={environment}
            onToggleEnvironment={() => {
              const next = environment === 'Development' ? 'Production' : 'Development';
              setEnvironment(next);
              showToast(`Switched to ${next} environment mode`);
            }}
            onOpenCommandPalette={() => setCommandPaletteOpen(true)}
            onOpenProfile={() => {
              setActivePage('Settings');
              showToast('Opened IGRIS settings');
            }}
            onOpenMobileNav={() => setMobileNavOpen(true)}
          />

          {/* Workspace Heading */}
          <section className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
            <div>
              <div className="font-mono-tabular text-[10px] tracking-[0.2em] text-[#a9f1ff] mb-2">
                {activeHeading.eyebrow}
              </div>
              <h1 className="text-2xl sm:text-[28px] font-bold tracking-[-0.03em] text-white m-0 leading-tight">
                {activeHeading.title}
              </h1>
              <p className="text-xs text-white/75 mt-1.5 mb-0">
                {activeHeading.subtitle}
              </p>
            </div>
            <GlassButton variant="primary" onClick={handleNewSession}>
              <Plus size={14} aria-hidden="true" />
              <span>New conversation</span>
            </GlassButton>
          </section>

          {activePage === 'Overview' && (
            <>
              <MetricsStrip
                sessionRequests={sessionRequests}
                sessionTokens={sessionTokens}
                lastLatencyMs={lastLatencyMs}
                backendConnected={backendStatus.isConnected}
                isDemo={backendStatus.isDemo}
                activeModelName={activeSpec.name}
              />

              <section className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.55fr)_minmax(310px,0.85fr)] gap-4">
                <PlaygroundPanel
                  selectedModel={activeSpec.name}
                  onOpenSettings={() => setActivePage('Settings')}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-1 gap-4 content-start">
                  <ModelSelectionCard
                    selectedModelId={selectedModelId}
                    onSelectModel={handleSelectModel}
                  />
                  <InferenceControlsCard
                    config={inferenceConfig}
                    onChange={setInferenceConfig}
                  />
                  <div className="md:col-span-2 xl:col-span-1">
                    <RuntimeMonitorCard
                      gpuUtilPct={gpuUtilPct}
                      vramAllocatedGb={vramAllocatedGb}
                      totalMemoryGb={6}
                      queueDepth={queueDepth}
                      isLive={backendStatus.isConnected}
                    />
                  </div>
                </div>
              </section>

              <section className="grid grid-cols-1 lg:grid-cols-[1.2fr_1fr] gap-4 mt-4">
                <ThroughputChartCard series={throughputHistory} />
                <RecentActivityCard
                  activities={activities}
                  onViewAll={() => setActivePage('Monitoring')}
                />
              </section>
            </>
          )}

          {(activePage === 'Playground' || activePage === 'Chat') && (
            <section className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.65fr)_minmax(310px,0.8fr)] gap-4">
              <PlaygroundPanel
                selectedModel={activeSpec.name}
                expanded
                onOpenSettings={() => setActivePage('Settings')}
              />
              <div className="space-y-4">
                <ModelSelectionCard
                  selectedModelId={selectedModelId}
                  onSelectModel={handleSelectModel}
                />
                <InferenceControlsCard
                  config={inferenceConfig}
                  onChange={setInferenceConfig}
                />
              </div>
            </section>
          )}

          {activePage !== 'Overview' && activePage !== 'Playground' && activePage !== 'Chat' && (
            <WorkspaceViews
              activePage={activePage}
              selectedModelId={selectedModelId}
              deployments={deployments}
              evaluations={evaluations}
              throughputSeries={throughputHistory}
              gpuUtil={gpuUtilPct}
              memoryGb={vramAllocatedGb}
              queueDepth={queueDepth}
              customEndpointUrl={customEndpointUrl}
              backendMode={backendStatus.isDemo ? 'demo' : 'http'}
              backendConnected={backendStatus.isConnected}
              glassFrost={glassFrost}
              glassBlur={glassBlur}
              onSelectModelAndOpenPlayground={(modelId) => {
                handleSelectModel(modelId);
                setActivePage('Playground');
              }}
              onToggleDeploymentHealth={handleToggleDeploymentHealth}
              onScaleDeployment={handleScaleDeployment}
              onRunEvaluation={handleRunEvaluation}
              onUpdateEndpointUrl={(url) => {
                setCustomEndpointUrl(url);
                showToast('Endpoint URL updated');
              }}
              onUpdateBackendMode={(mode) => {
                setBackendMode(mode);
                showToast(`Switched inference mode to ${mode === 'demo' ? 'Demo Simulation' : 'Local Runtime'}`);
              }}
              onTestBackendConnection={async () => {
                const res = await checkBackendHealth();
                showToast(res.statusText);
              }}
              onUpdateGlassSettings={(frost, blur) => {
                setGlassFrost(frost);
                setGlassBlur(blur);
              }}
            />
          )}
        </main>
      </div>

      <CommandPaletteModal
        open={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onNavigate={setActivePage}
        onSelectModel={handleSelectModel}
        onNewSession={handleNewSession}
      />

      {/* Frosted Glass Toast */}
      {toastMessage && (
        <div
          role="status"
          aria-live="polite"
          className="frosted-glass-bright backdrop-blur-xl fixed right-5 bottom-5 z-50 rounded-[18px] px-4 py-2.5 text-xs font-medium text-white shadow-2xl"
        >
          {toastMessage}
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <TelemetryProvider>
      <ConversationProvider>
        <StudioInner />
      </ConversationProvider>
    </TelemetryProvider>
  );
}
