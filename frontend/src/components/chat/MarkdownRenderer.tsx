import React, { useState } from 'react';
import { Check, Copy } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  // Parse content into blocks: code blocks vs text blocks
  const parts: React.ReactNode[] = [];
  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;

  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    const textBefore = content.slice(lastIndex, match.index);
    if (textBefore) {
      parts.push(
        <div key={`text-${lastIndex}`} className="space-y-2">
          {renderTextMarkdown(textBefore)}
        </div>,
      );
    }

    const lang = match[1] || 'code';
    const code = match[2];
    parts.push(<CodeBlock key={`code-${match.index}`} language={lang} code={code} />);

    lastIndex = match.index + match[0].length;
  }

  const remainingText = content.slice(lastIndex);
  if (remainingText) {
    parts.push(
      <div key={`text-${lastIndex}`} className="space-y-2">
        {renderTextMarkdown(remainingText)}
      </div>,
    );
  }

  return <div className="markdown-body space-y-2.5 text-xs leading-relaxed">{parts}</div>;
}

function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-2 rounded-[14px] overflow-hidden border border-white/20 bg-black/45 backdrop-blur-md">
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-white/10 bg-white/5 font-mono-tabular text-[10px] text-white/70">
        <span className="uppercase tracking-wider">{language}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-white cursor-pointer px-1.5 py-0.5 rounded hover:bg-white/10 transition-colors"
          aria-label="Copy code to clipboard"
        >
          {copied ? <Check size={11} className="text-[#72eab8]" /> : <Copy size={11} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <pre className="p-3 overflow-x-auto font-mono text-[11px] text-[#e8f2ff] leading-relaxed m-0 selection:bg-white/20">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function renderTextMarkdown(raw: string): React.ReactNode[] {
  const paragraphs = raw.split(/\n\s*\n/);

  return paragraphs.map((para, pIdx) => {
    const trimmed = para.trim();
    if (!trimmed) return null;

    // Blockquote
    if (trimmed.startsWith('>')) {
      const quoteText = trimmed.replace(/^>\s*/gm, '');
      return (
        <blockquote
          key={`blockquote-${pIdx}`}
          className="border-l-2 border-[#82ecff] pl-3 py-1 my-1.5 italic text-white/80 bg-white/5 rounded-r-[8px]"
        >
          {renderInlineFormatting(quoteText)}
        </blockquote>
      );
    }

    // Headings
    if (trimmed.startsWith('### ')) {
      return (
        <h4 key={`h4-${pIdx}`} className="text-xs font-bold text-white mt-2 mb-1 tracking-wide">
          {renderInlineFormatting(trimmed.slice(4))}
        </h4>
      );
    }
    if (trimmed.startsWith('## ')) {
      return (
        <h3 key={`h3-${pIdx}`} className="text-sm font-bold text-[#a9f1ff] mt-2 mb-1 tracking-tight">
          {renderInlineFormatting(trimmed.slice(3))}
        </h3>
      );
    }
    if (trimmed.startsWith('# ')) {
      return (
        <h2 key={`h2-${pIdx}`} className="text-base font-extrabold text-white mt-3 mb-1.5 tracking-tight">
          {renderInlineFormatting(trimmed.slice(2))}
        </h2>
      );
    }

    // Unordered List
    if (trimmed.split('\n').every((line) => line.trim().startsWith('- ') || line.trim().startsWith('* '))) {
      const items = trimmed.split('\n').map((l) => l.trim().replace(/^[-*]\s+/, ''));
      return (
        <ul key={`ul-${pIdx}`} className="list-disc list-inside space-y-1 my-1 text-white/90">
          {items.map((item, idx) => (
            <li key={idx}>{renderInlineFormatting(item)}</li>
          ))}
        </ul>
      );
    }

    // Numbered List
    if (trimmed.split('\n').every((line) => /^\d+\.\s+/.test(line.trim()))) {
      const items = trimmed.split('\n').map((l) => l.trim().replace(/^\d+\.\s+/, ''));
      return (
        <ol key={`ol-${pIdx}`} className="list-decimal list-inside space-y-1 my-1 text-white/90">
          {items.map((item, idx) => (
            <li key={idx}>{renderInlineFormatting(item)}</li>
          ))}
        </ol>
      );
    }

    // Standard paragraph with line breaks preserved
    const lines = trimmed.split('\n');
    return (
      <p key={`p-${pIdx}`} className="m-0 leading-relaxed text-white/95">
        {lines.map((line, lIdx) => (
          <React.Fragment key={lIdx}>
            {renderInlineFormatting(line)}
            {lIdx < lines.length - 1 && <br />}
          </React.Fragment>
        ))}
      </p>
    );
  });
}

function renderInlineFormatting(text: string): React.ReactNode {
  // Regex to split on inline code `...`, bold **...**, and italics *...*
  const tokenRegex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
  const parts = text.split(tokenRegex);

  return parts.map((part, idx) => {
    if (part.startsWith('`') && part.endsWith('`') && part.length > 1) {
      return (
        <code
          key={idx}
          className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-black/40 border border-white/15 text-[#a8f1ff]"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith('**') && part.endsWith('**') && part.length > 3) {
      return <strong key={idx} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
      return <em key={idx} className="italic text-white/85">{part.slice(1, -1)}</em>;
    }
    return part;
  });
}
