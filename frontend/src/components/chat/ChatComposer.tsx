import React, { useRef, useEffect } from 'react';
import { ArrowUp, Globe, Square } from 'lucide-react';
import { SupportedLanguage, SUPPORTED_LANGUAGES } from '../../config/languages';
import { estimateCandidateATokens } from '../../services/tokenizer/candidateA';
import { GlassIconButton } from '../glass/GlassIconButton';

interface ChatComposerProps {
  prompt: string;
  isGenerating: boolean;
  activeLanguage: SupportedLanguage;
  onPromptChange: (value: string) => void;
  onSend: () => void;
  onStop: () => void;
  onSelectLanguage: (lang: SupportedLanguage) => void;
  streamingEnabled?: boolean;
}

export function ChatComposer({
  prompt,
  isGenerating,
  activeLanguage,
  onPromptChange,
  onSend,
  onStop,
  onSelectLanguage,
  streamingEnabled = true,
}: ChatComposerProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (!isGenerating) {
      inputRef.current?.focus();
    }
  }, [isGenerating]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isGenerating) {
      onStop();
      return;
    }
    if (!prompt.trim()) return;
    onSend();
  };

  const estimatedTokens = estimateCandidateATokens(prompt, activeLanguage);

  return (
    <form onSubmit={handleSubmit} className="px-4 pb-4 pt-3 border-t border-white/15">
      {/* Input row container */}
      <div className="relative flex items-center gap-2">
        {/* Language selector toggle strictly for English, Tamil, Tanglish */}
        <div className="relative group">
          <div className="flex items-center gap-1 bg-white/10 hover:bg-white/15 border border-white/20 rounded-xl px-2 py-2 cursor-pointer transition-colors text-[11px] font-mono-tabular text-white/90">
            <Globe size={13} className="text-[#82ecff]" />
            <select
              value={activeLanguage}
              onChange={(e) => onSelectLanguage(e.target.value as SupportedLanguage)}
              className="bg-transparent text-white cursor-pointer focus:outline-none text-[11px] font-medium"
              aria-label="Select trilingual mode"
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.id} value={lang.id} className="bg-[#0b1022] text-white">
                  {lang.badge} ({lang.nativeName})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Text Input */}
        <div className="relative flex-1">
          <input
            ref={inputRef}
            id="igris-chat-input"
            type="text"
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            placeholder="Type in English, தமிழ், or Tanglish..."
            disabled={isGenerating}
            autoComplete="off"
            className="w-full px-4 py-2.5 rounded-2xl bg-white/10 hover:bg-white/12 focus:bg-white/15 border border-white/25 focus:border-[#82ecff]/70 text-white placeholder-white/45 text-xs transition-all focus:outline-none shadow-inner"
            aria-label="Message IGRIS"
          />
        </div>

        {/* Dynamic Send / Stop Generation Button */}
        {isGenerating ? (
          <button
            type="button"
            onClick={onStop}
            className="w-9 h-9 rounded-xl flex items-center justify-center bg-red-500/30 hover:bg-red-500/50 border border-red-400/50 text-white shadow-[0_0_12px_rgba(239,68,68,0.4)] cursor-pointer transition-all animate-pulse"
            aria-label="Stop generation"
            title="Stop generation"
          >
            <Square size={14} className="fill-white" />
          </button>
        ) : (
          <GlassIconButton
            type="submit"
            variant="cta"
            size="sm"
            disabled={!prompt.trim()}
            aria-label="Send message to IGRIS"
          >
            <ArrowUp size={15} />
          </GlassIconButton>
        )}
      </div>

      {/* Footer bar with token estimate and status info */}
      <div className="flex items-center justify-between gap-2 px-1 pt-2 font-mono-tabular text-[10px] text-white/55">
        <div className="flex items-center gap-3">
          <span>↵ Send · {streamingEnabled ? 'Streaming ON' : 'Batch mode'}</span>
          {prompt.trim().length > 0 && (
            <span className="text-[#a9f1ff]/80">
              ESTIMATED: ~{estimatedTokens} tok (ratio heuristic)
            </span>
          )}
        </div>
        <span className="tracking-wider">TRILINGUAL: EN · தமிழ் · TANGLISH</span>
      </div>
    </form>
  );
}
