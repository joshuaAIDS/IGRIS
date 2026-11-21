import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { TokenUsage } from '../services/inference/types';

export interface TelemetryPoint {
  label: string;
  tokensPerSec: number;
  requests: number;
}

export interface TelemetryState {
  sessionRequests: number;
  sessionTokens: number;
  lastLatencyMs: number;
  throughputHistory: TelemetryPoint[];
  gpuUtilPct: number | null; // null indicates waiting for live runtime telemetry
  vramAllocatedGb: number | null;
  targetVramGb: number;
  queueDepth: number;
  isLive: boolean;
}

export interface TelemetryContextType extends TelemetryState {
  recordCompletion: (usage?: TokenUsage, isLiveBackend?: boolean) => void;
  resetSessionTelemetry: () => void;
  updateLiveMetrics: (gpu: number, vram: number, queue: number) => void;
}

const INITIAL_SERIES: TelemetryPoint[] = [
  { label: '08:00', tokensPerSec: 0, requests: 0 },
  { label: '10:00', tokensPerSec: 0, requests: 0 },
  { label: '12:00', tokensPerSec: 0, requests: 0 },
  { label: '14:00', tokensPerSec: 0, requests: 0 },
  { label: '16:00', tokensPerSec: 0, requests: 0 },
  { label: 'NOW', tokensPerSec: 0, requests: 0 },
];

const TelemetryContext = createContext<TelemetryContextType | null>(null);

export const TelemetryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sessionRequests, setSessionRequests] = useState<number>(0);
  const [sessionTokens, setSessionTokens] = useState<number>(0);
  const [lastLatencyMs, setLastLatencyMs] = useState<number>(0);
  const [throughputHistory, setThroughputHistory] = useState<TelemetryPoint[]>(INITIAL_SERIES);
  const [gpuUtilPct, setGpuUtilPct] = useState<number | null>(null);
  const [vramAllocatedGb, setVramAllocatedGb] = useState<number | null>(null);
  const [queueDepth, setQueueDepth] = useState<number>(0);
  const [isLive, setIsLive] = useState<boolean>(false);

  const recordCompletion = useCallback((usage?: TokenUsage, isLiveBackend = false) => {
    setIsLive(isLiveBackend);
    setSessionRequests((prev) => prev + 1);

    if (usage) {
      setSessionTokens((prev) => prev + usage.totalTokens);
      setLastLatencyMs(usage.latencyMs);

      const tps = usage.tokensPerSec || (usage.latencyMs > 0 ? Math.round((usage.completionTokens / usage.latencyMs) * 1000) : 0);

      setThroughputHistory((prev) => {
        const next = prev.slice(1).map((pt) => ({ ...pt }));
        if (next.length > 0 && next[next.length - 1].label === 'NOW') {
          const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          next[next.length - 1].label = nowStr;
        }
        next.push({
          label: 'NOW',
          tokensPerSec: Math.min(250, tps),
          requests: next.length > 0 ? next[next.length - 1].requests + 1 : 1,
        });
        return next;
      });
    }
  }, []);

  const resetSessionTelemetry = useCallback(() => {
    setSessionRequests(0);
    setSessionTokens(0);
    setLastLatencyMs(0);
    setThroughputHistory(INITIAL_SERIES);
  }, []);

  const updateLiveMetrics = useCallback((gpu: number, vram: number, queue: number) => {
    setGpuUtilPct(gpu);
    setVramAllocatedGb(vram);
    setQueueDepth(queue);
    setIsLive(true);
  }, []);

  const value = useMemo(
    () => ({
      sessionRequests,
      sessionTokens,
      lastLatencyMs,
      throughputHistory,
      gpuUtilPct,
      vramAllocatedGb,
      targetVramGb: 6.0, // Calibrated target for NVIDIA RTX 3050 (6GB VRAM)
      queueDepth,
      isLive,
      recordCompletion,
      resetSessionTelemetry,
      updateLiveMetrics,
    }),
    [
      sessionRequests,
      sessionTokens,
      lastLatencyMs,
      throughputHistory,
      gpuUtilPct,
      vramAllocatedGb,
      queueDepth,
      isLive,
      recordCompletion,
      resetSessionTelemetry,
      updateLiveMetrics,
    ],
  );

  return <TelemetryContext.Provider value={value}>{children}</TelemetryContext.Provider>;
};

export function useTelemetry(): TelemetryContextType {
  const ctx = useContext(TelemetryContext);
  if (!ctx) {
    throw new Error('useTelemetry must be used within TelemetryProvider');
  }
  return ctx;
}
