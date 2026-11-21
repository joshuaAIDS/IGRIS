import React from 'react';
import { ArrowUpRight, Rocket, Settings2, Sparkles, Terminal } from 'lucide-react';
import { ActivityEntry } from '../../utils/studioEngine';
import { GlassCard } from '../glass/GlassCard';

interface RecentActivityCardProps {
  activities: ActivityEntry[];
  onViewAll: () => void;
}

const ICON_MAP: Record<ActivityEntry['icon'], React.ReactNode> = {
  deploy: <Rocket size={13} />,
  prompt: <Terminal size={13} />,
  eval: <Sparkles size={13} />,
  config: <Settings2 size={13} />,
};

export function RecentActivityCard({
  activities,
  onViewAll,
}: RecentActivityCardProps) {
  return (
    <GlassCard rounded="2xl" className="p-4 flex flex-col">
      <div className="flex items-center justify-between gap-2 mb-3">
        <h2 className="text-[13px] font-bold text-white m-0">Recent activity</h2>
        <button
          type="button"
          onClick={onViewAll}
          className="inline-flex items-center gap-1 font-mono-tabular text-[10px] tracking-[0.06em] text-white/75 hover:text-white cursor-pointer transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 rounded px-1.5 py-0.5"
        >
          <span>VIEW ALL</span>
          <ArrowUpRight size={12} aria-hidden="true" />
        </button>
      </div>

      <div className="divide-y divide-white/10">
        {activities.slice(0, 4).map((item) => (
          <div
            key={item.id}
            className="flex items-center gap-3 py-2.5 first:pt-1 last:pb-1"
          >
            <div
              className="frosted-well w-8 h-8 rounded-[11px] grid place-items-center text-[#a9f1ff] shrink-0"
              aria-hidden="true"
            >
              {ICON_MAP[item.icon]}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-xs font-medium text-white/95 truncate">
                {item.title}
              </div>
              <div className="font-mono-tabular text-[10px] text-white/60 mt-0.5 truncate">
                {item.subtitle}
              </div>
            </div>
            <time className="font-mono-tabular text-[10px] text-white/55 shrink-0">
              {item.time}
            </time>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
