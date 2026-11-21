import React, { useState } from 'react';
import {
  Activity,
  AlertCircle,
  Cpu,
  Gauge,
  HardDrive,
  RefreshCw,
  Server,
  Zap,
} from 'lucide-react';
import { useConversation } from '../../context/ConversationContext';
import { useTelemetry } from '../../context/TelemetryContext';
import { GlassButton } from '../glass/GlassButton';
import { GlassCard } from '../glass/GlassCard';
import { ThroughputChartCard } from './ThroughputChartCard';

export function PerformanceTelemetryCard() {
  const { backendStatus, checkBackendHealth } = useConversation();
  const {
    sessionRequests,
    sessionTokens,
    lastLatencyMs,
    throughputHistory,
  } = useTelemetry();

  const [isRefreshing, setIsRefreshing] = useState(false);

  const hw = backendStatus.hardware;
  const isConnected = backendStatus.isConnected;

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await checkBackendHealth();
    } finally {
      setIsRefreshing(false);
    }
  };

  // GPU Memory Calculations
  const hasCuda = isConnected && Boolean(hw?.cuda_available) && (hw?.total_vram_gb ?? 0) > 0;
  const gpuTotal = hasCuda ? `${hw?.total_vram_gb?.toFixed(2)} GB` : 'Unavailable';
  const gpuFree = hasCuda ? `${hw?.free_vram_gb?.toFixed(2)} GB` : 'Unavailable';
  const gpuAllocated =
    hasCuda && hw?.total_vram_gb && hw?.free_vram_gb
      ? `${(hw.total_vram_gb - hw.free_vram_gb).toFixed(2)} GB`
      : 'Unavailable';
  const gpuUtilPercent =
    hasCuda && hw?.total_vram_gb && hw?.free_vram_gb
      ? Math.round(((hw.total_vram_gb - hw.free_vram_gb) / hw.total_vram_gb) * 100)
      : null;

  // System RAM Calculations
  const hasRam = isConnected && typeof hw?.system_ram_total_gb === 'number';
  const ramTotal = hasRam ? `${hw?.system_ram_total_gb?.toFixed(2)} GB` : 'Unavailable';
  const ramAvail = hasRam ? `${hw?.system_ram_available_gb?.toFixed(2)} GB` : 'Unavailable';
  const ramUsed = hasRam ? `${hw?.system_ram_used_gb?.toFixed(2)} GB` : 'Unavailable';
  const ramPercent = hasRam ? `${hw?.system_ram_util_pct}%` : 'Unavailable';

  // Generation Speed & Latency Calculations
  // Strictly UNAVAILABLE until genuine trained model inference occurs
  const isGenuineInference = Boolean(isConnected && backendStatus.isTrained && lastLatencyMs > 0);
  const latestThroughput =
    throughputHistory.length > 0 ? throughputHistory[throughputHistory.length - 1].tokensPerSec : 0;
  const generationSpeed =
    isGenuineInference && latestThroughput > 0 ? `${latestThroughput} tok/s` : 'UNAVAILABLE';
  const latency = isGenuineInference ? `${lastLatencyMs} ms` : 'UNAVAILABLE';

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <GlassCard rounded="2xl" className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-mono-tabular text-[10px] text-[#a9f1ff] uppercase tracking-[0.15em]">
              Hardware & Inference Telemetry
            </span>
            <span
              className={`font-mono-tabular text-[10px] px-2 py-0.5 rounded-full ${
                isConnected
                  ? 'bg-emerald-500/20 text-[#72eab8] border border-emerald-500/30'
                  : 'bg-amber-500/20 text-[#f5c879] border border-amber-500/30'
              }`}
            >
              {isConnected ? 'LIVE TELEMETRY STREAM' : 'TELEMETRY UNAVAILABLE (STANDBY)'}
            </span>
          </div>
          <h2 className="text-lg font-bold text-white m-0">Live Performance & Resource Observability</h2>
          <p className="text-xs text-white/75 mt-1 mb-0 max-w-2xl leading-relaxed">
            Actual measured hardware metrics directly queried via PyTorch CUDA device properties, psutil system
            virtual memory sensors, and request timers. Inactive or unmeasured metrics are reported as{' '}
            <code className="text-[#a9f1ff] font-mono text-[11px]">Unavailable</code> without fabrication.
          </p>
        </div>

        <GlassButton
          variant="glass"
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          <RefreshCw size={13} className={isRefreshing ? 'animate-spin' : ''} />
          <span>Refresh Sensor Telemetry</span>
        </GlassButton>
      </GlassCard>

      {/* 4 Core Quantitative Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* GPU Memory Card */}
        <GlassCard rounded="2xl" className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono-tabular text-[10px] text-white/60 uppercase">SYSTEM CUDA MEMORY TELEMETRY</span>
            <div className="w-6 h-6 rounded-lg bg-cyan-500/20 border border-cyan-400/40 grid place-items-center text-[#82ecff]">
              <Cpu size={13} />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white tabular-nums tracking-tight">
              {gpuAllocated !== 'Unavailable' ? gpuAllocated : 'Unavailable'}
            </div>
            <div className="text-[11px] font-mono-tabular text-white/60 mt-1">
              Total: {gpuTotal} · Free: {gpuFree}
            </div>
          </div>
          {gpuUtilPercent !== null ? (
            <div className="space-y-1 pt-1">
              <div className="w-full h-1.5 rounded-full bg-white/10 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#82ecff] to-[#72eab8] rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, gpuUtilPercent)}%` }}
                />
              </div>
              <span className="font-mono-tabular text-[9.5px] text-white/50 block">
                PyTorch/system allocation (untrained model weights unallocated)
              </span>
            </div>
          ) : (
            <div className="text-[10px] font-mono-tabular text-amber-300/80">
              {isConnected ? 'CUDA not active (safe CPU execution)' : 'Daemon offline'}
            </div>
          )}
        </GlassCard>

        {/* System RAM Card */}
        <GlassCard rounded="2xl" className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono-tabular text-[10px] text-white/60 uppercase">SYSTEM RAM</span>
            <div className="w-6 h-6 rounded-lg bg-purple-500/20 border border-purple-400/40 grid place-items-center text-purple-300">
              <HardDrive size={13} />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-white tabular-nums tracking-tight">
              {ramUsed !== 'Unavailable' ? ramUsed : 'Unavailable'}
            </div>
            <div className="text-[11px] font-mono-tabular text-white/60 mt-1">
              Total: {ramTotal} · Available: {ramAvail}
            </div>
          </div>
          <div className="text-[10px] font-mono-tabular text-white/50 pt-1">
            Utilization: {ramPercent}
          </div>
        </GlassCard>

        {/* Generation Speed Card */}
        <GlassCard rounded="2xl" className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono-tabular text-[10px] text-white/60 uppercase">GENERATION SPEED</span>
            <div className="w-6 h-6 rounded-lg bg-emerald-500/20 border border-emerald-400/40 grid place-items-center text-[#72eab8]">
              <Zap size={13} />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-[#72eab8] tabular-nums tracking-tight">
              {generationSpeed}
            </div>
            <div className="text-[11px] font-mono-tabular text-white/60 mt-1">
              Cumulative: {sessionTokens} tokens generated
            </div>
          </div>
          <div className="text-[10px] font-mono-tabular text-white/50 pt-1">
            {generationSpeed === 'UNAVAILABLE' ? 'Awaiting genuine model inference (MODEL_NOT_TRAINED)' : 'Live measured rate'}
          </div>
        </GlassCard>

        {/* Latency Card */}
        <GlassCard rounded="2xl" className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono-tabular text-[10px] text-white/60 uppercase">REQUEST LATENCY</span>
            <div className="w-6 h-6 rounded-lg bg-amber-500/20 border border-amber-400/40 grid place-items-center text-[#f5c879]">
              <Gauge size={13} />
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-[#f5c879] tabular-nums tracking-tight">
              {latency}
            </div>
            <div className="text-[11px] font-mono-tabular text-white/60 mt-1">
              Total requests: {sessionRequests}
            </div>
          </div>
          <div className="text-[10px] font-mono-tabular text-white/50 pt-1">
            {latency === 'UNAVAILABLE' ? 'Awaiting genuine model inference (MODEL_NOT_TRAINED)' : 'End-to-end round trip'}
          </div>
        </GlassCard>
      </div>

      {/* Live Chart & System Profile Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-4">
        {/* Throughput Series */}
        <ThroughputChartCard series={throughputHistory} tall />

        {/* Detailed Hardware Platform Profile */}
        <GlassCard rounded="2xl" className="p-5 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-white/10">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider m-0">
                Hardware Node Specification
              </h3>
              <Server size={14} className="text-white/60" />
            </div>

            <div className="space-y-2.5 text-xs font-mono-tabular">
              <div className="flex items-center justify-between">
                <span className="text-white/60">Execution Device:</span>
                <span className="font-bold text-[#a9f1ff]">
                  {hw?.device ?? (isConnected ? 'cpu' : 'Unavailable')}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/60">Device Name:</span>
                <span className="text-white font-medium text-right truncate max-w-[190px]">
                  {hw?.device_name ?? 'Unavailable'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/60">CUDA Available:</span>
                <span className={hw?.cuda_available ? 'text-[#72eab8] font-bold' : 'text-white/60'}>
                  {isConnected ? (hw?.cuda_available ? 'YES' : 'NO') : 'Unavailable'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/60">Safe for GPU:</span>
                <span className={hw?.safe_for_gpu ? 'text-[#72eab8]' : 'text-amber-300'}>
                  {isConnected ? (hw?.safe_for_gpu ? 'YES' : 'NO') : 'Unavailable'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/60">CPU Architecture:</span>
                <span className="text-white text-right truncate max-w-[180px]">
                  {hw?.cpu_architecture ?? 'Unavailable'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/60">Logical CPU Cores:</span>
                <span className="text-white">{hw?.cpu_threads ?? 'Unavailable'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white/60">Host Platform:</span>
                <span className="text-white text-right truncate max-w-[180px]">
                  {hw?.system_platform ?? 'Unavailable'}
                </span>
              </div>
              {hw?.fallback_reason && (
                <div className="pt-2 border-t border-white/10 text-[10px] text-amber-300">
                  Fallback: {hw.fallback_reason}
                </div>
              )}
            </div>
          </div>

          <div className="frosted-well rounded-xl p-3 text-[10.5px] text-white/65 flex items-start gap-2">
            <AlertCircle size={14} className="text-[#a9f1ff] shrink-0 mt-0.5" />
            <span>
              All sensor telemetry reflects genuine system calls. No random or mock metrics are generated.
            </span>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}