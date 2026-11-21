import React, { useEffect, useState } from 'react';
import { ArrowRight, Plus, Search, X } from 'lucide-react';
import { IGRIS_MODEL_CATALOG } from '../../config/models';
import { NavPageId } from '../../utils/studioEngine';
import { GlassCard } from '../glass/GlassCard';
import { GlassIconButton } from '../glass/GlassIconButton';
import { GlassInputField } from '../glass/GlassInputField';

interface CommandPaletteModalProps {
  open: boolean;
  onClose: () => void;
  onNavigate: (page: NavPageId) => void;
  onSelectModel: (modelId: string) => void;
  onNewSession: () => void;
}

const PAGES: NavPageId[] = [
  'Chat',
  'Models',
  'Tokenizer',
  'Performance',
  'Settings',
  'Overview',
  'Playground',
  'Deployments',
  'Monitoring',
  'Usage & costs',
  'Evaluations',
  'Documentation',
];

export function CommandPaletteModal({
  open,
  onClose,
  onNavigate,
  onSelectModel,
  onNewSession,
}: CommandPaletteModalProps) {
  const [query, setQuery] = useState('');

  useEffect(() => {
    if (!open) setQuery('');
  }, [open]);

  if (!open) return null;

  const q = query.trim().toLowerCase();
  const filteredPages = PAGES.filter((p) => p.toLowerCase().includes(q));
  const filteredModels = Object.values(IGRIS_MODEL_CATALOG).filter(
    (m) => m.name.toLowerCase().includes(q) || m.family.toLowerCase().includes(q),
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[12vh] px-4 bg-black/55 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Command palette"
      onClick={onClose}
    >
      <GlassCard
        variant="liquid"
        rounded="3xl"
        className="w-full max-w-lg p-4 space-y-3 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between gap-2">
          <span className="font-mono-tabular text-[10px] tracking-[0.14em] text-[#82ecff] uppercase">
            IGRIS Quick Workspace Commands
          </span>
          <GlassIconButton
            size="sm"
            onClick={onClose}
            aria-label="Close command palette"
          >
            <X size={14} />
          </GlassIconButton>
        </div>

        <GlassInputField
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Jump to view, switch IGRIS checkpoint, or start new chat…"
          aria-label="Search workspace commands"
          leadingIcon={<Search size={15} />}
        />

        <div className="max-h-72 overflow-y-auto space-y-3 pr-1">
          <div>
            <div className="font-mono-tabular text-[10px] text-white/55 px-2 mb-1.5 uppercase">
              ACTIONS
            </div>
            <button
              type="button"
              onClick={() => {
                onNewSession();
                onClose();
              }}
              className="w-full flex items-center justify-between px-3 py-2 rounded-[14px] text-xs font-medium text-white hover:bg-white/15 cursor-pointer transition-colors"
            >
              <span className="flex items-center gap-2">
                <Plus size={14} className="text-[#82ecff]" /> New IGRIS conversation session
              </span>
              <kbd className="font-mono-tabular text-[10px] text-white/50">↵</kbd>
            </button>
          </div>

          {filteredModels.length > 0 && (
            <div>
              <div className="font-mono-tabular text-[10px] text-white/55 px-2 mb-1.5 uppercase">
                IGRIS MODELS
              </div>
              <div className="space-y-1">
                {filteredModels.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => {
                      onSelectModel(m.id);
                      onClose();
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-[14px] text-xs font-medium text-white/90 hover:bg-white/15 hover:text-white cursor-pointer transition-colors"
                  >
                    <span>{m.name}</span>
                    <span className="font-mono-tabular text-[10px] text-[#82ecff]">
                      {m.family}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {filteredPages.length > 0 && (
            <div>
              <div className="font-mono-tabular text-[10px] text-white/55 px-2 mb-1.5 uppercase">
                NAVIGATE
              </div>
              <div className="space-y-1">
                {filteredPages.map((page) => (
                  <button
                    key={page}
                    type="button"
                    onClick={() => {
                      onNavigate(page);
                      onClose();
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-[14px] text-xs font-medium text-white/85 hover:bg-white/15 hover:text-white cursor-pointer transition-colors"
                  >
                    <span>{page}</span>
                    <ArrowRight size={13} className="text-white/40" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
