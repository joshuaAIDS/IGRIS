import React from 'react';
import {
  Activity,
  BarChart3,
  Binary,
  BookOpen,
  Boxes,
  Compass,
  Rocket,
  Settings,
  Sparkles,
  Terminal,
  X,
} from 'lucide-react';
import { NavPageId } from '../../utils/studioEngine';
import { GlassCard } from '../glass/GlassCard';
import { GlassIconButton } from '../glass/GlassIconButton';
import { GlassNavigationItem } from '../glass/GlassNavigationItem';

interface SidebarProps {
  activePage: NavPageId;
  onSelectPage: (page: NavPageId) => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  runtimeLabel: string;
}

interface NavGroup {
  heading: string;
  items: { id: NavPageId; label: string; icon: React.ReactNode }[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    heading: 'IGRIS STUDIO',
    items: [
      { id: 'Chat', label: '1. Chat', icon: <Terminal size={15} /> },
      { id: 'Models', label: '2. Models', icon: <Boxes size={15} /> },
      { id: 'Tokenizer', label: '3. Tokenizer Lab', icon: <Binary size={15} /> },
      { id: 'Performance', label: '4. Performance', icon: <Activity size={15} /> },
      { id: 'Settings', label: '5. Settings', icon: <Settings size={15} /> },
    ],
  },
  {
    heading: 'WORKSPACE & OPS',
    items: [
      { id: 'Overview', label: 'Overview', icon: <Compass size={15} /> },
      { id: 'Deployments', label: 'Deployments', icon: <Rocket size={15} /> },
      { id: 'Evaluations', label: 'Evaluations', icon: <Sparkles size={15} /> },
      { id: 'Documentation', label: 'Documentation', icon: <BookOpen size={15} /> },
    ],
  },
];

function SidebarContent({
  activePage,
  onSelectPage,
  onCloseMobile,
  isMobileDrawer,
  runtimeLabel,
}: {
  activePage: NavPageId;
  onSelectPage: (page: NavPageId) => void;
  onCloseMobile?: () => void;
  isMobileDrawer?: boolean;
  runtimeLabel: string;
}) {
  return (
    <div className="flex flex-col h-full gap-6">
      {/* Brand Identity: IGRIS */}
      <div className="flex items-center justify-between gap-3 px-1">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-[12px] frosted-cta grid place-items-center font-extrabold text-sm tracking-tight shrink-0 shadow-[0_0_15px_rgba(130,236,255,0.4)]">
            இ
          </div>
          <div>
            <div className="text-[15px] font-extrabold tracking-[0.14em] text-white leading-none">
              IGRIS
            </div>
            <div className="text-[9px] font-mono-tabular tracking-[0.18em] text-[#82ecff] mt-1.5 uppercase">
              VOICE-FIRST SLM STUDIO
            </div>
          </div>
        </div>
        {isMobileDrawer && onCloseMobile && (
          <GlassIconButton
            variant="glass"
            size="sm"
            onClick={onCloseMobile}
            aria-label="Close navigation menu"
          >
            <X size={15} />
          </GlassIconButton>
        )}
      </div>

      <nav aria-label="Workspace navigation" className="flex-1 space-y-5">
        {NAV_GROUPS.map((group) => (
          <div key={group.heading}>
            <div className="font-mono-tabular text-[9.5px] tracking-[0.18em] text-white/50 px-2.5 mb-2 uppercase">
              {group.heading}
            </div>
            <div className="space-y-1">
              {group.items.map((item) => (
                <GlassNavigationItem
                  key={item.id}
                  id={item.id}
                  label={item.label}
                  icon={item.icon}
                  active={activePage === item.id}
                  onClick={() => {
                    onSelectPage(item.id);
                    if (onCloseMobile) onCloseMobile();
                  }}
                />
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Runtime Status Pill */}
      <div className="frosted-well rounded-[18px] p-3 border border-white/15">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#82ecff] animate-pulse" aria-hidden="true" />
          <span className="font-mono-tabular text-[9.5px] tracking-[0.12em] text-white/85 uppercase">
            {runtimeLabel}
          </span>
        </div>
        <div className="text-[11px] text-white/60 mt-1 font-mono-tabular">
          Target: RTX 3050 · 6GB VRAM
        </div>
      </div>
    </div>
  );
}

export function Sidebar({
  activePage,
  onSelectPage,
  mobileOpen,
  onCloseMobile,
  runtimeLabel,
}: SidebarProps) {
  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden lg:block w-64 shrink-0 p-5">
        <GlassCard rounded="3xl" className="h-[calc(100vh-2.5rem)] sticky top-5 p-4">
          <SidebarContent
            activePage={activePage}
            onSelectPage={onSelectPage}
            runtimeLabel={runtimeLabel}
          />
        </GlassCard>
      </aside>

      {/* Mobile Slide-Over Drawer */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-50 lg:hidden bg-black/60 backdrop-blur-md"
          role="dialog"
          aria-modal="true"
          aria-label="Mobile navigation"
          onClick={onCloseMobile}
        >
          <div
            className="w-72 max-w-[80vw] h-full frosted-glass border-r border-white/20 p-5 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <SidebarContent
              activePage={activePage}
              onSelectPage={onSelectPage}
              onCloseMobile={onCloseMobile}
              isMobileDrawer
              runtimeLabel={runtimeLabel}
            />
          </div>
        </div>
      )}
    </>
  );
}
