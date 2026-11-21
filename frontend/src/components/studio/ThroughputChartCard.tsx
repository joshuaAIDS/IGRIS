import React, { useState } from 'react';
import { ThroughputPoint } from '../../utils/studioEngine';
import { GlassCard } from '../glass/GlassCard';

interface ThroughputChartCardProps {
  series: ThroughputPoint[];
  tall?: boolean;
}

export function ThroughputChartCard({
  series,
  tall = false,
}: ThroughputChartCardProps) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const activePoint =
    hoveredIdx !== null ? series[hoveredIdx] : series[series.length - 1];

  return (
    <GlassCard rounded="2xl" className="p-4 flex flex-col">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div>
          <h2 className="text-[13px] font-bold text-white m-0">
            Inference throughput
          </h2>
          {activePoint && (
            <p className="font-mono-tabular text-[10px] text-[#a9f1ff] mt-1 mb-0">
              {activePoint.label} · {activePoint.tokensPerSec} tok/s ·{' '}
              {activePoint.requests.toLocaleString()} req
            </p>
          )}
        </div>
        <span className="font-mono-tabular text-[10px] tracking-[0.06em] text-white/65">
          LAST 12 HOURS · TOKENS / SEC
        </span>
      </div>

      <div
        className={`relative flex items-end gap-1.5 sm:gap-2 px-2 pt-3 border-b border-white/20 ${
          tall ? 'h-48' : 'h-32'
        }`}
        style={{
          backgroundImage:
            'repeating-linear-gradient(to bottom, transparent 0, transparent 29px, rgba(255,255,255,0.08) 30px)',
        }}
        role="img"
        aria-label="Inference throughput bar chart over the last 12 hours"
      >
        {series.map((pt, idx) => {
          const isHovered = hoveredIdx === idx;
          return (
            <button
              key={`${pt.label}-${idx}`}
              type="button"
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
              onFocus={() => setHoveredIdx(idx)}
              onBlur={() => setHoveredIdx(null)}
              aria-label={`${pt.label}: ${pt.tokensPerSec} tokens per second`}
              className="flex-1 h-full flex items-end cursor-pointer focus-visible:outline-none group"
            >
              <span
                className={`w-full rounded-t-[6px] border-t border-x transition-all duration-150 ${
                  isHovered
                    ? 'border-white/80 bg-gradient-to-t from-white/35 via-[#a6efff]/75 to-white/95 shadow-[0_0_16px_rgba(166,239,255,0.45)]'
                    : 'border-white/30 bg-gradient-to-t from-white/18 via-[#82ecff]/45 to-[#d4f7ff]/80 group-hover:brightness-110'
                }`}
                style={{ height: `${Math.max(12, pt.tokensPerSec)}%` }}
              />
            </button>
          );
        })}
      </div>

      <div className="flex justify-between pt-2.5 px-1 font-mono-tabular text-[10px] text-white/60">
        <span>08:00</span>
        <span>10:00</span>
        <span>12:00</span>
        <span>14:00</span>
        <span>16:00</span>
        <span>NOW</span>
      </div>
    </GlassCard>
  );
}
