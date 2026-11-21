import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Boxes,
  Check,
  Cpu,
  Layers,
  Lock,
  Search,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { IGRIS_MODEL_CATALOG, ModelSpec } from '../../config/models';
import { useConversation } from '../../context/ConversationContext';
import { CANDIDATE_A_METADATA } from '../../services/tokenizer/candidateA';
import { GlassButton } from '../glass/GlassButton';
import { GlassCard } from '../glass/GlassCard';
import { GlassInputField } from '../glass/GlassInputField';

interface ModelsRegistryCardProps {
  selectedModelId: string;
  onSelectModelAndOpenPlayground: (modelId: string) => void;
}

export function ModelsRegistryCard({
  selectedModelId,
  onSelectModelAndOpenPlayground,
}: ModelsRegistryCardProps) {
  const { backendStatus, fetchModels } = useConversation();
  const [modelSearch, setModelSearch] = useState('');
  const [liveModels, setLiveModels] = useState<any[]>([]);

  useEffect(() => {
    if (backendStatus.isConnected) {
      fetchModels()
        .then((data) => {
          if (Array.isArray(data) && data.length > 0) {
            setLiveModels(data);
          }
        })
        .catch(() => {
          // Keep local catalog
        });
    }
  }, [backendStatus.isConnected, fetchModels]);

  const allModels = Object.values(IGRIS_MODEL_CATALOG);
  const q = modelSearch.trim().toLowerCase();
  const models = q
    ? allModels.filter(
        (m) =>
          m.name.toLowerCase().includes(q) ||
          m.family.toLowerCase().includes(q) ||
          m.desc.toLowerCase().includes(q),
      )
    : allModels;

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <GlassCard rounded="2xl" className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="font-mono-tabular text-[10px] text-[#a9f1ff] uppercase tracking-[0.15em]">
              CHECKPOINT REGISTRY / SPECIFICATIONS
            </span>
            <span
              className={`font-mono-tabular text-[10px] px-2 py-0.5 rounded-full ${
                backendStatus.modelState === 'MODEL LOADED'
                  ? 'bg-emerald-500/20 text-[#72eab8] border border-emerald-500/30'
                  : 'bg-amber-500/20 text-[#f5c879] border border-amber-500/30'
              }`}
            >
              {backendStatus.modelState ?? 'MODEL NOT TRAINED'}
            </span>
          </div>
          <h2 className="text-lg font-bold text-white m-0">IGRIS Architecture & Model Inventory</h2>
          <p className="text-xs text-white/75 mt-1 mb-0 max-w-2xl leading-relaxed">
            Inspect authoritative 16-layer production architecture, 12-layer baseline configuration, verified Candidate A
            tokenizer, and honest checkpoint status.
          </p>
        </div>

        <div className="w-full md:w-72">
          <GlassInputField
            value={modelSearch}
            onChange={(e) => setModelSearch(e.target.value)}
            placeholder="Search models, families, or parameters..."
            aria-label="Filter model registry"
            leadingIcon={<Search size={14} />}
          />
        </div>
      </GlassCard>

      {/* Honest Checkpoint Status Banner */}
      <GlassCard rounded="2xl" className="p-4 bg-amber-950/20 border-amber-500/30 flex items-start gap-3">
        <div className="w-7 h-7 rounded-xl bg-amber-500/20 border border-amber-400/40 grid place-items-center text-[#f5c879] shrink-0 mt-0.5">
          <Lock size={14} />
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-bold text-[#f5c879] uppercase tracking-wider m-0">
              Governance Gate: Pretraining Locked
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-amber-400/10 text-amber-300 font-mono-tabular text-[9px] uppercase">
              MODEL NOT TRAINED
            </span>
          </div>
          <p className="text-xs text-white/80 m-0 leading-relaxed">
            The IGRIS model architecture (16 layers, GQA 8:4, SwiGLU, RMSNorm) and Candidate A BPE tokenizer are fully
            specified and verified invariant on disk. No trained checkpoint exists on disk. In strict accordance with
            project governance, random untrained weights are prevented from generating fabricated inference.
          </p>
        </div>
      </GlassCard>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {models.map((model) => {
          const isActive = model.id === selectedModelId;
          const isProduction = model.id === 'IGRIS-PROD-16L';
          const isBaseline = model.id === 'IGRIS-50M-BASELINE';
          const isTokenizer = model.id === 'IGRIS-CANDIDATE-A';

          return (
            <GlassCard
              key={model.id}
              variant={isActive ? 'bright' : 'frosted'}
              rounded="2xl"
              className="p-5 flex flex-col justify-between gap-4"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-mono-tabular text-[10px] text-[#a9f1ff] uppercase tracking-[0.12em]">
                      {model.family} · {model.params}
                    </div>
                    <h3 className="text-base font-bold text-white mt-1 mb-0">{model.name}</h3>
                  </div>

                  <span
                    className={`font-mono-tabular text-[10px] px-2.5 py-1 rounded-full ${
                      isTokenizer
                        ? 'bg-emerald-500/20 text-[#72eab8] border border-emerald-500/30'
                        : isProduction
                        ? 'bg-amber-500/20 text-[#f5c879] border border-amber-500/30'
                        : 'bg-white/10 text-white/70 border border-white/20'
                    }`}
                  >
                    {isTokenizer
                      ? 'VERIFIED INVARIANT'
                      : isProduction
                      ? 'MODEL NOT TRAINED'
                      : model.status.toUpperCase()}
                  </span>
                </div>

                <p className="text-xs text-white/75 leading-relaxed mt-2.5 mb-0">
                  {model.desc}
                </p>

                {/* Architecture Specifications Grid */}
                <div className="mt-4 p-3 rounded-xl bg-black/30 border border-white/10 space-y-2 text-xs font-mono-tabular">
                  <div className="text-[10px] font-bold text-[#a9f1ff] uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <Layers size={12} />
                    <span>Architectural Parameters</span>
                  </div>

                  {isProduction && (
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px]">
                      <div className="flex justify-between text-white/70">
                        <span>Layers:</span> <b className="text-white">16 decoder blocks</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Hidden Size:</span> <b className="text-white">512 dims</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Intermediate:</span> <b className="text-white">2048 dims (4x)</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Attention GQA:</span> <b className="text-white">8 Query : 4 KV</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Activation:</span> <b className="text-[#82ecff]">SwiGLU</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Norm:</span> <b className="text-white">RMSNorm (1e-5)</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Positional:</span> <b className="text-white">RoPE (θ=10000.0)</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Embeddings:</span> <b className="text-[#72eab8]">Tied (79.7M)</b>
                      </div>
                    </div>
                  )}

                  {isBaseline && (
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px]">
                      <div className="flex justify-between text-white/70">
                        <span>Layers:</span> <b className="text-white">12 decoder blocks</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Hidden Size:</span> <b className="text-white">512 dims</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Intermediate:</span> <b className="text-white">1376 dims</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Attention GQA:</span> <b className="text-white">8 Query : 4 KV</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Activation:</span> <b className="text-[#82ecff]">SwiGLU</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Embeddings:</span> <b className="text-[#72eab8]">Tied (51.6M)</b>
                      </div>
                    </div>
                  )}

                  {isTokenizer && (
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px]">
                      <div className="flex justify-between text-white/70">
                        <span>Vocab Size:</span> <b className="text-[#82ecff]">32,768</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Structural:</span> <b className="text-white">12 special tokens</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Byte Fallback:</span> <b className="text-[#72eab8]">256 native bytes</b>
                      </div>
                      <div className="flex justify-between text-white/70">
                        <span>Target Script:</span> <b className="text-white">EN · தமிழ் · Tanglish</b>
                      </div>
                      <div className="col-span-2 pt-1 border-t border-white/10 flex justify-between text-[10px] text-white/60">
                        <span>SHA-256:</span>
                        <code className="text-[#a9f1ff] font-mono">ac7e18b13973450b43bfff18609a833e4ef0e642b8dc5803e39ab1e81ba4c561</code>
                      </div>
                    </div>
                  )}

                  {!isProduction && !isBaseline && !isTokenizer && (
                    <div className="text-[11px] text-white/70">
                      Standard local inference gateway protocol on http://127.0.0.1:8000 with SSE streaming.
                    </div>
                  )}
                </div>
              </div>

              {/* Checkpoint Availability & Action */}
              <div className="space-y-3 pt-2 border-t border-white/10">
                <div className="flex items-center justify-between text-xs font-mono-tabular">
                  <span className="text-white/60">CHECKPOINT AVAILABILITY:</span>
                  <span className={isTokenizer ? 'text-[#72eab8] font-bold' : 'text-amber-300 font-bold'}>
                    {isTokenizer
                      ? 'INVARIANT ON DISK'
                      : backendStatus.checkpointPath
                      ? backendStatus.checkpointPath
                      : 'NO CHECKPOINT LOADED'}
                  </span>
                </div>

                <GlassButton
                  variant={isActive ? 'primary' : 'glass'}
                  className="w-full justify-center"
                  onClick={() => onSelectModelAndOpenPlayground(model.id)}
                >
                  {isActive ? (
                    <>
                      <Check size={14} /> Selected for Chat & Playground
                    </>
                  ) : (
                    'Load into Chat'
                  )}
                </GlassButton>
              </div>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
}