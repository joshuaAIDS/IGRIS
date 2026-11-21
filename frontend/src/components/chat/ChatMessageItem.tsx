import React, { useState } from 'react';
import { Check, Copy, RefreshCw, Sparkles, User } from 'lucide-react';
import { ChatMessage } from '../../services/inference/types';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ChatMessageItemProps {
  message: ChatMessage;
  isLatestAssistantMessage?: boolean;
  onRegenerate?: () => void;
  showUsage?: boolean;
}

export function ChatMessageItem({
  message,
  isLatestAssistantMessage = false,
  onRegenerate,
  showUsage = true,
}: ChatMessageItemProps) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`flex items-start gap-2.5 max-w-[92%] sm:max-w-[85%] ${
        isUser ? 'self-end flex-row-reverse' : 'self-start'
      }`}
    >
      {/* Avatar Badge */}
      <div
        className={`w-7 h-7 rounded-[10px] grid place-items-center text-[11px] font-bold shrink-0 border ${
          isUser
            ? 'frosted-glass-bright text-white border-white/40'
            : 'frosted-well text-[#82ecff] border-white/25'
        }`}
        aria-hidden="true"
      >
        {isUser ? <User size={13} /> : <Sparkles size={13} />}
      </div>

      {/* Bubble Container */}
      <div className="flex flex-col gap-1.5 min-w-0">
        <div
          className={`px-4 py-3 text-xs leading-relaxed text-white/95 ${
            isUser
              ? 'frosted-glass-bright rounded-[18px_6px_18px_18px]'
              : 'frosted-well rounded-[6px_18px_18px_18px] border border-white/20'
          } ${message.error ? 'border-[#ff8ea8]/60 bg-red-950/20' : ''}`}
        >
          {/* Header Metadata */}
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2 pb-1.5 border-b border-white/10 font-mono-tabular text-[10px]">
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-white/80">
                {isUser ? 'YOU' : message.modelId || 'IGRIS'}
              </span>
              {message.language && (
                <span className="px-1.5 py-0.2 rounded-full bg-white/10 text-white/70 text-[9px] uppercase">
                  {message.language}
                </span>
              )}
            </div>

            <div className="flex items-center gap-2">
              {!isUser && message.isDemo && (
                <span className="px-2 py-0.5 rounded-full bg-[#f5c879]/20 text-[#f5c879] border border-[#f5c879]/30 text-[9px] font-bold tracking-wider">
                  DEMO RESPONSE
                </span>
              )}
              <span className="text-white/50">{message.timestamp}</span>
            </div>
          </div>

          {/* Body Content */}
          {isUser ? (
            <div className="whitespace-pre-wrap">{message.content}</div>
          ) : (
            <MarkdownRenderer content={message.content} />
          )}

          {/* Usage Telemetry Footer */}
          {!isUser && showUsage && message.usage && (
            <div className="mt-3 pt-2 border-t border-white/10 font-mono-tabular text-[9.5px] text-white/60 flex flex-wrap items-center gap-x-3 gap-y-1">
              <span>prompt: {message.usage.promptTokens} tok</span>
              <span>completion: {message.usage.completionTokens} tok</span>
              <span>latency: {message.usage.latencyMs} ms</span>
              {message.usage.tokensPerSec && <span>rate: {message.usage.tokensPerSec} tok/s</span>}
            </div>
          )}
        </div>

        {/* Message Actions Toolbar */}
        {!isUser && (
          <div className="flex items-center gap-1 px-1 font-mono-tabular text-[10px] text-white/65">
            <button
              type="button"
              onClick={handleCopy}
              className="flex items-center gap-1 hover:text-white px-2 py-1 rounded-md hover:bg-white/10 cursor-pointer transition-colors"
              aria-label="Copy assistant response"
            >
              {copied ? <Check size={11} className="text-[#72eab8]" /> : <Copy size={11} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>

            {isLatestAssistantMessage && onRegenerate && (
              <button
                type="button"
                onClick={onRegenerate}
                className="flex items-center gap-1 hover:text-[#82ecff] px-2 py-1 rounded-md hover:bg-white/10 cursor-pointer transition-colors ml-1"
                aria-label="Regenerate response"
              >
                <RefreshCw size={11} />
                <span>Regenerate</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
