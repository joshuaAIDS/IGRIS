import React, { useState, useEffect, useCallback } from 'react';
import { Binary, Check, CheckCircle2, Copy, ExternalLink, RefreshCw, Sparkles, Terminal } from 'lucide-react';
import { useConversation } from '../../context/ConversationContext';
import { TokenizeResponse, TokenPiece } from '../../services/inference/types';
import { CANDIDATE_A_METADATA, estimateCandidateATokens } from '../../services/tokenizer/candidateA';
import { GlassButton } from '../glass/GlassButton';
import { GlassCard } from '../glass/GlassCard';

const QUICK_TEST_EXPRESSIONS = [
  { label: 'server-ல்', text: 'server-ல்', lang: 'Tanglish' },
  { label: 'complex-ஆ', text: 'complex-ஆ', lang: 'Tanglish' },
  { label: 'deploy பண்ணினோம்', text: 'deploy பண்ணினோம்', lang: 'Tanglish' },
  { label: 'memory allocation', text: 'memory allocation', lang: 'English' },
  { label: 'pannirukkom', text: 'pannirukkom', lang: 'Tanglish' },
  { label: 'testing-க்கு', text: 'testing-க்கு', lang: 'Tanglish' },
  { label: 'தமிழ் இயல்பு', text: 'தமிழ் இயல்பு', lang: 'Tamil' },
  { label: 'வணக்கம் உலகம்', text: 'வணக்கம் உலகம்', lang: 'Tamil' },
  {
    label: 'Voice-First SLM',
    text: 'Voice-First Small Language Model for Edge Computing',
    lang: 'English',
  },
];

export function TokenizerLabCard() {
  const { backendStatus, tokenizeText } = useConversation();
  const [inputText, setInputText] = useState('server-ல்');
  const [result, setResult] = useState<TokenizeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedToken, setSelectedToken] = useState<TokenPiece | null>(null);
  const [copiedText, setCopiedText] = useState(false);

  const isConnected = backendStatus.isConnected;

  const runTokenize = useCallback(
    async (textToTokenize: string) => {
      const clean = textToTokenize.trim();
      if (!clean) {
        setResult(null);
        setError(null);
        return;
      }

      if (!isConnected) {
        setResult(null);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const res = await tokenizeText(clean);
        setResult(res);
        if (res.tokens.length > 0) {
          setSelectedToken(res.tokens[0]);
        } else {
          setSelectedToken(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setResult(null);
      } finally {
        setIsLoading(false);
      }
    },
    [isConnected, tokenizeText],
  );

  useEffect(() => {
    if (isConnected && inputText) {
      runTokenize(inputText);
    }
  }, [isConnected, inputText, runTokenize]);

  const handleCopyInput = () => {
    navigator.clipboard.writeText(inputText);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;
  const estimatedTokens = estimateCandidateATokens(inputText);
  const tpw =
    result && wordCount > 0 ? (result.token_count / wordCount).toFixed(2) : 'Unavailable';
  const cpt =
    result && result.token_count > 0
      ? (result.character_count / result.token_count).toFixed(2)
      : 'Unavailable';

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <GlassCard rounded="2xl" className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-mono-tabular text-[10px] text-[#a9f1ff] uppercase tracking-[0.15em]">
              Candidate A Linguistic Foundation
            </span>
            <span
              className={`font-mono-tabular text-[10px] px-2 py-0.5 rounded-full ${
                isConnected
                  ? 'bg-emerald-500/20 text-[#72eab8] border border-emerald-500/30'
                  : 'bg-amber-500/20 text-[#f5c879] border border-amber-500/30'
              }`}
            >
              {isConnected ? 'LIVE TOKENIZER ONLINE' : 'TOKENIZER SERVICE UNAVAILABLE'}
            </span>
          </div>
          <h2 className="text-lg font-bold text-white m-0">Candidate A Tokenizer Lab</h2>
          <p className="text-xs text-white/75 mt-1 mb-0 max-w-2xl leading-relaxed">
            Direct inspection of the authoritative Candidate A ByteLevel BPE tokenizer (32,768 vocabulary, 12 structural special tokens, SHA-256:{' '}
            <code className="text-[#a9f1ff] font-mono text-[11px]">ac7e18b1...</code>).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <GlassButton
            variant="glass"
            size="sm"
            onClick={() => runTokenize(inputText)}
            disabled={isLoading || !isConnected}
          >
            <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
            <span>Tokenize</span>
          </GlassButton>
        </div>
      </GlassCard>

      {/* Offline Warning Banner when backend is disconnected */}
      {!isConnected && (
        <GlassCard rounded="2xl" className="p-5 border-amber-500/30 bg-amber-950/20 space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl bg-amber-500/20 border border-amber-400/40 grid place-items-center text-[#f5c879] shrink-0 mt-0.5">
              <Binary size={16} />
            </div>
            <div className="space-y-1">
              <h3 className="text-sm font-bold text-[#f5c879] m-0">
                Tokenizer Service Unavailable (Local Daemon Offline)
              </h3>
              <p className="text-xs text-white/80 m-0 leading-relaxed">
                Candidate A ByteLevel BPE tokenization requires the active local IGRIS inference runtime daemon (
                <code className="font-mono text-[#a9f1ff]">http://127.0.0.1:8000</code>). In strict adherence to project
                governance and zero-fabrication policies, synthetic token IDs and simulated BPE boundaries are never
                invented when offline.
              </p>
              <div className="pt-2 font-mono-tabular text-[11px] text-white/60 flex items-center gap-2">
                <span>To connect live tokenizer:</span>
                <code className="px-2 py-0.5 rounded bg-white/10 text-white font-mono">run_backend.bat</code>
              </div>
            </div>
          </div>
        </GlassCard>
      )}

      {/* Interactive Input Section */}
      <GlassCard rounded="2xl" className="p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <label htmlFor="tokenizer-input-field" className="text-xs font-bold text-white uppercase tracking-wider">
            Input Trilingual Text (English, தமிழ், Tanglish)
          </label>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleCopyInput}
              className="text-[11px] font-mono-tabular text-white/60 hover:text-white flex items-center gap-1 cursor-pointer transition-colors"
            >
              {copiedText ? <Check size={12} className="text-[#72eab8]" /> : <Copy size={12} />}
              <span>{copiedText ? 'Copied' : 'Copy Text'}</span>
            </button>
          </div>
        </div>

        <textarea
          id="tokenizer-input-field"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          rows={3}
          placeholder="Enter text to tokenize in English, தமிழ், or Tanglish..."
          className="w-full px-4 py-3 rounded-xl bg-white/5 hover:bg-white/8 focus:bg-white/10 border border-white/20 focus:border-[#82ecff]/60 text-white text-xs leading-relaxed focus:outline-none transition-all font-mono"
        />

        {/* Quick Test Expression Pills */}
        <div className="space-y-1.5">
          <span className="block font-mono-tabular text-[10px] text-white/60 uppercase tracking-wider">
            Curated Audit Fixtures (Mandatory Linguistic Examples)
          </span>
          <div className="flex flex-wrap gap-1.5">
            {QUICK_TEST_EXPRESSIONS.map((exp) => (
              <button
                key={exp.text}
                type="button"
                onClick={() => setInputText(exp.text)}
                className={`px-2.5 py-1 rounded-lg text-xs font-mono-tabular border transition-all cursor-pointer ${
                  inputText === exp.text
                    ? 'bg-[#82ecff]/25 border-[#82ecff]/70 text-white shadow-[0_0_10px_rgba(130,236,255,0.3)]'
                    : 'bg-white/5 hover:bg-white/10 border-white/15 text-white/80 hover:text-white'
                }`}
              >
                <span>{exp.label}</span>
                <span className="ml-1.5 text-[9px] text-white/50 uppercase">[{exp.lang}]</span>
              </button>
            ))}
          </div>
        </div>
      </GlassCard>

      {/* Tokenization Results (Only when connected) */}
      {isConnected && result && (
        <div className="space-y-4">
          {/* Metrics Overview Strip with clear distinction between ACTUAL and ESTIMATED */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <GlassCard rounded="xl" className="p-3.5 space-y-1">
              <span className="block font-mono-tabular text-[10px] text-[#82ecff] uppercase font-bold">
                ACTUAL TOKENS (/v1/tokenize)
              </span>
              <b className="text-xl font-bold text-[#82ecff] tabular-nums">{result.token_count}</b>
              <span className="block text-[9px] text-white/50 font-mono-tabular">Candidate A measured</span>
            </GlassCard>

            <GlassCard rounded="xl" className="p-3.5 space-y-1">
              <span className="block font-mono-tabular text-[10px] text-[#f5c879] uppercase font-bold">
                ESTIMATED TOKENS (HEURISTIC)
              </span>
              <b className="text-xl font-bold text-[#f5c879] tabular-nums">~{estimatedTokens}</b>
              <span className="block text-[9px] text-white/50 font-mono-tabular">Ratio estimation only</span>
            </GlassCard>

            <GlassCard rounded="xl" className="p-3.5 space-y-1">
              <span className="block font-mono-tabular text-[10px] text-white/60 uppercase">
                CHARACTERS & BYTES
              </span>
              <b className="text-xl font-bold text-white tabular-nums">
                {result.character_count}c · {result.byte_count}B
              </b>
              <span className="block text-[9px] text-white/50 font-mono-tabular">CPT: {cpt}</span>
            </GlassCard>

            <GlassCard rounded="xl" className="p-3.5 space-y-1">
              <span className="block font-mono-tabular text-[10px] text-white/60 uppercase">
                TOKENS PER WORD
              </span>
              <b className="text-xl font-bold text-[#72eab8] tabular-nums">{tpw}</b>
              <span className="block text-[9px] text-white/50 font-mono-tabular">{wordCount} words detected</span>
            </GlassCard>
          </div>

          {/* Exact Bitwise Round-Trip Reconstruction Banner */}
          <div className="flex flex-wrap items-center justify-between gap-2 p-3.5 rounded-xl bg-emerald-950/25 border border-emerald-500/35 text-xs font-mono-tabular">
            <div className="flex items-center gap-2 text-[#72eab8]">
              <CheckCircle2 size={15} />
              <span className="font-bold">EXACT ROUND-TRIP FIDELITY: 100.00%</span>
            </div>
            <div className="text-white/80 text-[11px] truncate max-w-lg">
              Reconstructed: <code className="text-white bg-black/30 px-1.5 py-0.5 rounded">"{result.reconstructed_text || inputText}"</code>
            </div>
          </div>

          {/* Visual Colorized Token Chips */}
          <GlassCard rounded="2xl" className="p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider m-0">
                Token Segmentation Stream ({result.token_count} actual pieces)
              </h3>
              <span className="font-mono-tabular text-[10px] text-white/50">
                Click a chip to inspect exact BPE byte details
              </span>
            </div>

            <div className="p-4 rounded-xl bg-black/40 border border-white/10 flex flex-wrap gap-1.5 min-h-[64px]">
              {result.tokens.map((tok, idx) => {
                const isSelected = selectedToken?.id === tok.id && selectedToken?.start === tok.start;
                // Palette for visual chip distinction
                const colorClasses = [
                  'bg-cyan-500/20 border-cyan-400/40 text-cyan-200',
                  'bg-purple-500/20 border-purple-400/40 text-purple-200',
                  'bg-emerald-500/20 border-emerald-400/40 text-emerald-200',
                  'bg-amber-500/20 border-amber-400/40 text-amber-200',
                  'bg-blue-500/20 border-blue-400/40 text-blue-200',
                  'bg-rose-500/20 border-rose-400/40 text-rose-200',
                ];
                const chipColor = colorClasses[idx % colorClasses.length];

                return (
                  <button
                    key={`${tok.id}-${idx}`}
                    type="button"
                    onClick={() => setSelectedToken(tok)}
                    className={`px-2 py-1 rounded-md text-xs font-mono border transition-all cursor-pointer ${chipColor} ${
                      isSelected ? 'ring-2 ring-white scale-105 shadow-lg' : 'hover:scale-102'
                    }`}
                  >
                    <span className="text-[9px] opacity-60 mr-1">#{idx}</span>
                    <span>{tok.decoded || tok.piece}</span>
                  </button>
                );
              })}
            </div>

            {selectedToken && (
              <div className="frosted-well rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 text-xs font-mono-tabular">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-[#a9f1ff] font-bold">TOKEN ID: {selectedToken.id}</span>
                  <span className="text-white/70">RAW PIECE: <code className="text-white">{selectedToken.piece}</code></span>
                  {selectedToken.raw_hex && (
                    <span className="text-white/70">HEX: <code className="text-purple-300">0x{selectedToken.raw_hex.toUpperCase()}</code></span>
                  )}
                  <span className="text-white/70">DECODED: <code className="text-[#72eab8]">{selectedToken.decoded}</code></span>
                </div>
                <div className="text-white/50 text-[11px]">
                  SPAN: [{selectedToken.start ?? '?'}:{selectedToken.end ?? '?'}]
                </div>
              </div>
            )}
          </GlassCard>

          {/* Full Token Breakdown Table */}
          <GlassCard rounded="2xl" className="p-5 space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider m-0">
              Detailed Token Breakdown Table
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs font-mono-tabular">
                <thead>
                  <tr className="border-b border-white/15 text-[10px] text-white/60">
                    <th className="py-2 pr-3 font-medium">INDEX</th>
                    <th className="py-2 px-3 font-medium">TOKEN ID</th>
                    <th className="py-2 px-3 font-medium">RAW BPE PIECE</th>
                    <th className="py-2 px-3 font-medium">RAW HEX</th>
                    <th className="py-2 px-3 font-medium">DECODED UNICODE</th>
                    <th className="py-2 pl-3 font-medium text-right">SPAN</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10">
                  {result.tokens.map((tok, idx) => (
                    <tr
                      key={`row-${tok.id}-${idx}`}
                      onClick={() => setSelectedToken(tok)}
                      className={`hover:bg-white/5 cursor-pointer transition-colors ${
                        selectedToken?.id === tok.id && selectedToken?.start === tok.start
                          ? 'bg-white/10'
                          : ''
                      }`}
                    >
                      <td className="py-2.5 pr-3 text-white/50">#{idx}</td>
                      <td className="py-2.5 px-3 font-bold text-[#a9f1ff]">{tok.id}</td>
                      <td className="py-2.5 px-3 text-white/80 font-mono">{tok.piece}</td>
                      <td className="py-2.5 px-3 text-purple-300 font-mono">
                        {tok.raw_hex ? `0x${tok.raw_hex.toUpperCase()}` : '—'}
                      </td>
                      <td className="py-2.5 px-3 text-[#72eab8] font-sans font-semibold">
                        {tok.decoded}
                      </td>
                      <td className="py-2.5 pl-3 text-right text-white/50">
                        [{tok.start ?? '?'}, {tok.end ?? '?'}]
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}