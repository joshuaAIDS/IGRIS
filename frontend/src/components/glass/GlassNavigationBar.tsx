import React from 'react';
import { Command, Menu } from 'lucide-react';
import { GlassButton } from './GlassButton';
import { GlassIconButton } from './GlassIconButton';

interface GlassNavigationBarProps {
  activePage: string;
  environment: 'Development' | 'Production';
  onToggleEnvironment: () => void;
  onOpenCommandPalette: () => void;
  onOpenProfile: () => void;
  onOpenMobileNav: () => void;
}

export function GlassNavigationBar({
  activePage,
  environment,
  onToggleEnvironment,
  onOpenCommandPalette,
  onOpenProfile,
  onOpenMobileNav,
}: GlassNavigationBarProps) {
  return (
    <header className="flex items-center justify-between gap-4 mb-6">
      <div className="flex items-center gap-3 min-w-0">
        <GlassIconButton
          variant="glass"
          size="sm"
          onClick={onOpenMobileNav}
          aria-label="Open navigation menu"
          className="lg:hidden"
        >
          <Menu size={16} />
        </GlassIconButton>

        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-[11px] font-mono-tabular tracking-[0.12em] text-white/65 truncate">
          <span>WORKSPACE</span>
          <span aria-hidden="true">/</span>
          <span className="text-white font-medium truncate">
            {activePage.toUpperCase()}
          </span>
        </nav>
      </div>

      <div className="flex items-center gap-2.5 shrink-0">
        <button
          type="button"
          onClick={onToggleEnvironment}
          aria-label={`Switch environment, currently ${environment}`}
          className="liquidglass hidden sm:inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 min-h-[36px] text-[11px] font-mono-tabular tracking-[0.06em] text-white/95 cursor-pointer transition-all duration-150 hover:brightness-110 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/75 whitespace-nowrap shrink-0"
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              environment === 'Production' ? 'bg-[#72eab8]' : 'bg-[#82ecff]'
            }`}
            aria-hidden="true"
          />
          <span>{environment.toUpperCase()} ENVIRONMENT</span>
        </button>

        <GlassButton
          variant="liquid"
          size="sm"
          onClick={onOpenCommandPalette}
          aria-label="Open command palette"
          className="font-mono-tabular text-[11px]"
        >
          <Command size={13} aria-hidden="true" />
          <span>K</span>
        </GlassButton>

        <GlassIconButton
          variant="liquid"
          size="sm"
          onClick={onOpenProfile}
          aria-label="Workspace profile and runtime info"
          className="text-xs font-bold tracking-tight"
        >
          U
        </GlassIconButton>
      </div>
    </header>
  );
}
