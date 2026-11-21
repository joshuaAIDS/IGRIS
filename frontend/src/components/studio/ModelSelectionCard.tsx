import React from 'react';
import { DEFAULT_MODEL_ID, IGRIS_MODEL_CATALOG, ModelSpec } from '../../config/models';
import { GlassCard } from '../glass/GlassCard';
import { GlassDropdown } from '../glass/GlassDropdown';

interface ModelSelectionCardProps {
  selectedModelId: string;
  onSelectModel: (modelId: string) => void;
}

export function ModelSelectionCard({
  selectedModelId,
  onSelectModel,
}: ModelSelectionCardProps) {
  const activeSpec: ModelSpec =
    IGRIS_MODEL_CATALOG[selectedModelId] ?? IGRIS_MODEL_CATALOG[DEFAULT_MODEL_ID];

  const options = Object.values(IGRIS_MODEL_CATALOG).map((m) => ({
    value: m.id,
    label: m.name,
  }));

  return (
    <GlassCard rounded="2xl" className="p-4">
      <div className="flex items-center justify-between gap-2 mb-3">
        <h2 className="text-[13px] font-bold text-white m-0">IGRIS Model Checkpoint</h2>
        <span className="font-mono-tabular text-[10px] tracking-[0.08em] text-[#82ecff]">
          {activeSpec.family}
        </span>
      </div>

      <GlassDropdown
        id="model-selector"
        label="Select active model"
        value={selectedModelId}
        options={options}
        onChange={onSelectModel}
      />

      <p
        data-testid="model-description"
        className="text-[11px] text-white/75 leading-relaxed mt-3 mb-3.5"
      >
        {activeSpec.desc}
      </p>

      <div className="grid grid-cols-2 gap-2.5">
        <div className="frosted-well rounded-[16px] p-3">
          <span className="block font-mono-tabular text-[9px] tracking-[0.12em] text-white/65">
            FORMAT / PRECISION
          </span>
          <b
            data-testid="model-quantization"
            className="block text-sm font-bold text-white mt-1 tabular-nums"
          >
            {activeSpec.quantization}
          </b>
        </div>
        <div className="frosted-well rounded-[16px] p-3">
          <span className="block font-mono-tabular text-[9px] tracking-[0.12em] text-white/65">
            CONTEXT TOKENS
          </span>
          <b
            data-testid="model-context"
            className="block text-sm font-bold text-white mt-1 tabular-nums"
          >
            {activeSpec.contextWindow}
          </b>
        </div>
      </div>

      {activeSpec.targetHardware && (
        <div className="mt-2.5 px-3 py-2 rounded-xl bg-white/5 border border-white/10 font-mono-tabular text-[10px] text-white/60 flex items-center justify-between">
          <span>TARGET PLATFORM:</span>
          <span className="text-[#a9f1ff]">{activeSpec.targetHardware}</span>
        </div>
      )}
    </GlassCard>
  );
}
