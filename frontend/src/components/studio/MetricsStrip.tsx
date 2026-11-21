import React from 'react';
import { GlassCard } from '../glass/GlassCard';

interface MetricsStripProps {
  sessionRequests: number;
  sessionTokens: number;
  lastLatencyMs: number;
  backendConnected: boolean;
  isDemo: boolean;
  activeModelName: string;
}

export function MetricsStrip({
  sessionRequests,
  sessionTokens,
  lastLatencyMs,
  backendConnected,
  isDemo,
  activeModelName,
}: MetricsStripProps) {
  const cards = [
    {
      label: 'Session Prompts',
      value: String(sessionRequests),
      unit: '',
      delta: sessionRequests > 0 ? `+${sessionRequests}` : '0 active',
      deltaColor: sessionRequests > 0 ? 'text-[#72eab8]' : 'text-white/40',
      foot: 'Prompts evaluated this session',
    },
    {
      label: 'Inference Latency',
      value: lastLatencyMs > 0 && !isDemo ? String(lastLatencyMs) : 'UNAVAILABLE',
      unit: lastLatencyMs > 0 && !isDemo ? 'ms' : '',
      delta: lastLatencyMs > 0 && !isDemo ? 'Measured' : 'UNAVAILABLE',
      deltaColor: lastLatencyMs > 0 && !isDemo ? 'text-[#82ecff]' : 'text-white/40',
      foot: lastLatencyMs > 0 && !isDemo ? 'Generation turn duration' : 'Awaiting genuine model inference',
    },
    {
      label: 'Candidate A Tokens',
      value: sessionTokens > 0 ? sessionTokens.toLocaleString() : '0',
      unit: 'tok',
      delta: sessionTokens > 0 ? (isDemo ? 'ESTIMATED (DEMO)' : 'Measured') : 'Standby',
      deltaColor: sessionTokens > 0 ? (isDemo ? 'text-[#f5c879]' : 'text-[#72eab8]') : 'text-white/40',
      foot: isDemo ? 'Simulated demo tokens' : 'Trilingual BPE 32K token budget',
    },
    {
      label: 'Runtime Status',
      value: backendConnected ? 'ONLINE' : isDemo ? 'DEMO' : 'OFFLINE',
      unit: '',
      delta: backendConnected ? '● Connected' : '● Standby',
      deltaColor: backendConnected ? 'text-[#72eab8]' : 'text-[#f5c879]',
      foot: activeModelName,
    },
  ];

  return (
    <section
      aria-label="Workspace key metrics"
      className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3.5 mb-5"
    >
      {cards.map((card) => (
        <GlassCard
          key={card.label}
          rounded="xl"
          className="px-4 py-4 overflow-hidden group hover:border-white/40"
        >
          <div className="flex items-center justify-between gap-2">
            <span className="font-mono-tabular text-[10px] tracking-[0.14em] uppercase text-white/70">
              {card.label}
            </span>
          </div>
          <div className="flex items-baseline gap-2.5 mt-2.5">
            <div className="text-[26px] font-bold tracking-[-0.04em] text-white tabular-nums leading-none">
              {card.value}
              {card.unit && (
                <span className="text-[13px] font-semibold text-white/70 ml-1">
                  {card.unit}
                </span>
              )}
            </div>
            <span className={`font-mono-tabular text-[11px] ${card.deltaColor}`}>
              {card.delta}
            </span>
          </div>
          <div className="text-[11px] text-white/65 mt-1.5">{card.foot}</div>
        </GlassCard>
      ))}
    </section>
  );
}
