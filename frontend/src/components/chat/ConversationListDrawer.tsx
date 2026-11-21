import React from 'react';
import { MessageSquare, Plus, Trash2, X } from 'lucide-react';
import { ConversationSession } from '../../context/ConversationContext';
import { GlassButton } from '../glass/GlassButton';

interface ConversationListDrawerProps {
  open: boolean;
  sessions: ConversationSession[];
  activeSessionId: string;
  onClose: () => void;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  onClearSession: () => void;
}

export function ConversationListDrawer({
  open,
  sessions,
  activeSessionId,
  onClose,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onClearSession,
}: ConversationListDrawerProps) {
  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-black/55 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Conversation history"
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm h-full frosted-glass border-l border-white/20 p-5 flex flex-col gap-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-white/15">
          <div className="flex items-center gap-2">
            <MessageSquare size={16} className="text-[#82ecff]" />
            <h3 className="text-sm font-bold text-white m-0 tracking-tight">Conversation History</h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-7 h-7 rounded-lg grid place-items-center hover:bg-white/10 text-white/70 hover:text-white transition-colors"
            aria-label="Close conversation history"
          >
            <X size={15} />
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <GlassButton
            variant="primary"
            size="sm"
            className="flex-1 justify-center"
            onClick={() => {
              onNewSession();
              onClose();
            }}
          >
            <Plus size={13} />
            <span>New Chat</span>
          </GlassButton>

          <GlassButton
            variant="glass"
            size="sm"
            onClick={() => {
              if (window.confirm('Clear all messages in the active conversation?')) {
                onClearSession();
                onClose();
              }
            }}
            title="Clear active conversation messages"
          >
            Clear Active
          </GlassButton>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {sessions.map((s) => {
            const isActive = s.id === activeSessionId;
            return (
              <div
                key={s.id}
                onClick={() => {
                  onSelectSession(s.id);
                  onClose();
                }}
                className={`group flex items-center justify-between p-3 rounded-2xl cursor-pointer transition-all border ${
                  isActive
                    ? 'frosted-glass-bright border-[#82ecff]/60 text-white shadow-[0_0_15px_rgba(130,236,255,0.15)]'
                    : 'hover:bg-white/10 border-white/10 text-white/75 hover:text-white'
                }`}
              >
                <div className="min-w-0 flex-1 pr-2">
                  <div className="text-xs font-semibold truncate leading-tight">{s.title}</div>
                  <div className="flex items-center gap-2 mt-1 font-mono-tabular text-[9.5px] text-white/50">
                    <span>{s.messages.length} msgs</span>
                    <span>·</span>
                    <span className="uppercase">{s.language || 'en'}</span>
                    <span>·</span>
                    <span>{new Date(s.updatedAt).toLocaleDateString([], { month: 'short', day: 'numeric' })}</span>
                  </div>
                </div>

                {sessions.length > 1 && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(s.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 text-white/40 hover:text-red-400 rounded-lg transition-all"
                    aria-label={`Delete conversation ${s.title}`}
                  >
                    <Trash2 size={13} />
                  </button>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer info */}
        <div className="pt-3 border-t border-white/10 text-center font-mono-tabular text-[10px] text-white/45">
          IGRIS TRILINGUAL CONVERSATION STORE
        </div>
      </div>
    </div>
  );
}
