import React, { useEffect, useRef, useState } from 'react';
import { History, Sparkles, Trash2 } from 'lucide-react';
import { PROMPT_SUGGESTIONS, SupportedLanguage } from '../../config/languages';
import { useConversation } from '../../context/ConversationContext';
import { useTelemetry } from '../../context/TelemetryContext';
import { GlassButton } from '../glass/GlassButton';
import { GlassCard } from '../glass/GlassCard';
import { BackendStatusBadge } from '../chat/BackendStatusBadge';
import { ChatComposer } from '../chat/ChatComposer';
import { ChatMessageItem } from '../chat/ChatMessageItem';
import { ConversationListDrawer } from '../chat/ConversationListDrawer';

interface PlaygroundPanelProps {
  selectedModel: string;
  expanded?: boolean;
  onOpenSettings?: () => void;
}

export function PlaygroundPanel({
  selectedModel,
  expanded = false,
  onOpenSettings,
}: PlaygroundPanelProps) {
  const {
    sessions,
    activeSessionId,
    messages,
    isGenerating,
    error,
    activeLanguage,
    inferenceConfig,
    backendStatus,
    createNewSession,
    switchSession,
    deleteSession,
    clearCurrentSession,
    sendMessage,
    regenerateLastResponse,
    stopGeneration,
    setActiveLanguage,
    dismissError,
  } = useConversation();

  const { recordCompletion } = useTelemetry();

  const [prompt, setPrompt] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const userScrolledUpRef = useRef<boolean>(false);

  // Monitor user scroll to avoid hijacking view if they scroll up to read earlier text
  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 60;
    userScrolledUpRef.current = !isAtBottom;
  };

  // Auto-scroll when messages update or during streaming, unless user scrolled up
  useEffect(() => {
    if (scrollRef.current && !userScrolledUpRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isGenerating]);

  // Record telemetry on finished assistant messages
  useEffect(() => {
    if (!isGenerating && messages.length > 0) {
      const lastMsg = messages[messages.length - 1];
      if (lastMsg.role === 'assistant' && lastMsg.usage && !lastMsg.error) {
        recordCompletion(lastMsg.usage, !lastMsg.isDemo);
      }
    }
  }, [isGenerating, messages, recordCompletion]);

  const handleSendPrompt = (overridePrompt?: string, overrideLang?: SupportedLanguage) => {
    const textToSend = (overridePrompt ?? prompt).trim();
    if (!textToSend || isGenerating) return;

    userScrolledUpRef.current = false;
    sendMessage(textToSend, overrideLang || activeLanguage);
    if (!overridePrompt) {
      setPrompt('');
    }
  };

  return (
    <GlassCard
      rounded="3xl"
      className={`flex flex-col overflow-hidden ${
        expanded ? 'min-h-[660px]' : 'min-h-[560px]'
      }`}
    >
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 pt-4 pb-3 border-b border-white/15">
        <div className="flex items-center gap-2.5 min-w-0">
          <h2 className="text-[13px] font-bold tracking-tight text-white m-0">
            IGRIS Chat & Inference
          </h2>
          <span
            data-testid="active-model-pill"
            className="frosted-glass-bright rounded-full px-2.5 py-1 text-[10px] font-mono-tabular text-white/95 truncate max-w-[200px]"
          >
            {selectedModel}
          </span>
          <BackendStatusBadge
            status={backendStatus}
            isGenerating={isGenerating}
            onClickSettings={onOpenSettings}
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setHistoryOpen(true)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/15 text-white/75 hover:text-white font-mono-tabular text-[10px] transition-colors"
            title="Open conversation history"
          >
            <History size={12} />
            <span>History ({sessions.length})</span>
          </button>

          {messages.length > 0 && (
            <button
              type="button"
              onClick={clearCurrentSession}
              disabled={isGenerating}
              className="p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors"
              title="Clear current conversation"
              aria-label="Clear conversation"
            >
              <Trash2 size={13} />
            </button>
          )}

          <span className="font-mono-tabular text-[10px] tracking-[0.08em] text-white/65">
            SESSION #{activeSessionId}
          </span>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mx-4 mt-3 px-3.5 py-2.5 rounded-xl bg-red-950/40 border border-red-500/40 flex items-center justify-between gap-2 text-xs text-red-200">
          <span>{error}</span>
          <button
            type="button"
            onClick={dismissError}
            className="text-[10px] underline hover:text-white font-mono-tabular"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Conversation / Welcome Orb Area */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        data-testid="playground-conversation"
        className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-4"
      >
        {messages.length === 0 ? (
          <div className="my-auto py-6 px-3 text-center flex flex-col items-center">
            {/* Centered Luminous Model Visualization Orb inside a frosted-glass halo */}
            <div className="relative mb-5">
              <div
                className="frosted-glass-bright w-24 h-24 rounded-full grid place-items-center"
                aria-hidden="true"
              >
                <div
                  className="w-14 h-14 rounded-full relative"
                  style={{
                    background:
                      'radial-gradient(circle at 32% 28%, #ffffff 0%, #99ecff 24%, #8278e8 58%, #2e2458 84%)',
                    boxShadow:
                      '0 0 32px rgba(130, 236, 255, 0.36), inset 0 2px 6px rgba(255,255,255,0.7)',
                  }}
                >
                  <span
                    className="absolute -inset-2.5 rounded-full border border-white/35"
                    style={{ transform: 'rotateX(68deg)' }}
                  />
                </div>
              </div>
            </div>

            <h3 className="text-[17px] font-bold tracking-tight text-white m-0">
              What would you like to explore with IGRIS?
            </h3>
            <p className="text-xs text-white/72 mt-1.5 max-w-md leading-relaxed">
              Interact natively in English, தமிழ் (Tamil Unicode), or Tanglish. Observe Candidate A tokenization, test streaming decoding, or connect your local runtime daemon.
            </p>

            {/* Trilingual Quick Suggestions */}
            <div className="flex flex-wrap items-center justify-center gap-2 mt-5 max-w-xl">
              {PROMPT_SUGGESTIONS.map((suggestion) => (
                <GlassButton
                  key={suggestion.label}
                  variant="glass"
                  size="sm"
                  onClick={() => {
                    handleSendPrompt(suggestion.text, suggestion.language);
                  }}
                  title={suggestion.text}
                >
                  <Sparkles size={11} className="text-[#82ecff]" />
                  <span>{suggestion.label}</span>
                </GlassButton>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const isLatestAssistant =
              msg.role === 'assistant' &&
              idx === messages.length - 1 &&
              !isGenerating;

            return (
              <ChatMessageItem
                key={msg.id}
                message={msg}
                isLatestAssistantMessage={isLatestAssistant}
                onRegenerate={regenerateLastResponse}
                showUsage={inferenceConfig.returnUsage}
              />
            );
          })
        )}

        {isGenerating && (
          <div className="flex items-center gap-2 text-[11px] font-mono-tabular text-white/75 px-1 py-1">
            <span className="w-2 h-2 rounded-full bg-[#82ecff] animate-ping" aria-hidden="true" />
            <span>Streaming completion from {selectedModel}…</span>
          </div>
        )}
      </div>

      {/* Composer */}
      <ChatComposer
        prompt={prompt}
        isGenerating={isGenerating}
        activeLanguage={activeLanguage}
        onPromptChange={setPrompt}
        onSend={() => handleSendPrompt()}
        onStop={stopGeneration}
        onSelectLanguage={setActiveLanguage}
        streamingEnabled={inferenceConfig.streaming}
      />

      {/* Conversation History Drawer */}
      <ConversationListDrawer
        open={historyOpen}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onClose={() => setHistoryOpen(false)}
        onSelectSession={switchSession}
        onNewSession={() => createNewSession(selectedModel)}
        onDeleteSession={deleteSession}
        onClearSession={clearCurrentSession}
      />
    </GlassCard>
  );
}
