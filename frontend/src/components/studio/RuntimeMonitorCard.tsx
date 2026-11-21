import React from 'react';
import { GlassCard } from '../glass/GlassCard';

interface RuntimeMonitorCardProps {
  gpuUtilPct: number | null;
  vramAllocatedGb: number | null;
  totalMemoryGb?: number;
  queueDepth: number;
  isLive: boolean;
}

export function RuntimeMonitorCard({
  gpuUtilPct,
  vramAllocatedGb,
  totalMemoryGb = 6, // NVIDIA GeForce RTX 3050 target
  queueDepth,
  isLive,
}: RuntimeMonitorCardProps) {
  return (
    <GlassCard rounded="2xl" className="p-4">
      <div className="flex items-center justify-between gap-2 mb-3">
        <h2 className="text-[13px] font-bold text-white m-0">Hardware & Runtime Monitor</h2>
        <span
          className={`inline-flex items-center gap-1.5 font-mono-tabular text-[10px] tracking-[0.08em] ${
            isLive ? 'text-[#72eab8]' : 'text-[#f5c879]'
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isLive ? 'bg-[#72eab8] animate-ping' : 'bg-[#f5c879]'
            }`}
            aria-hidden="true"
          />
          {isLive ? 'LIVE TELEMETRY' : 'STANDBY'}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex items-center justify-between text-xs text-white/85">
            <span>GPU Utilisation</span>
            <b className="font-mono-tabular text-white">
              {isLive && gpuUtilPct !== null ? `${gpuUtilPct}%` : 'Standby (No active daemon)'}
            </b>
          </div>
          <div className="h-1.5 rounded-full bg-white/15 border border-white/15 mt-1.5 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#82ecff] to-[#b6a6ff] transition-all duration-300"
              style={{ width: `${isLive && gpuUtilPct !== null ? gpuUtilPct : 0}%` }}
            />
          </div>
        </div>

        <div className="pt-2 border-t border-white/12">
          <div className="flex items-center justify-between text-xs text-white/85">
            <span>Target Hardware Budget</span>
            <b className="font-mono-tabular text-[#a9f1ff]">RTX 3050 · {totalMemoryGb} GB VRAM</b>
          </div>
          <div className="flex items-center justify-between text-[11px] text-white/60 mt-1">
            <span>VRAM Allocation:</span>
            <span>
              {isLive && vramAllocatedGb !== null
                ? `${vramAllocatedGb.toFixed(1)} / ${totalMemoryGb} GB`
                : 'Budgeted: < 3.5 GB (Model ~100MB)'}
            </span>
          </div>
        </div>

        <div className="pt-2 border-t border-white/12 flex items-center justify-between text-xs text-white/85">
          <span>Active Queue Depth</span>
          <b className="font-mono-tabular text-white">
            {String(queueDepth).padStart(2, '0')}
          </b>
        </div>

        <div className="pt-2 border-t border-white/12 flex items-center justify-between text-xs text-white/85">
          <span>Execution Boundary</span>
          <b className="font-mono-tabular text-[#72eab8]">LOCAL ZERO-EGRESS</b>
        </div>
      </div>
    </GlassCard>
  );
}
