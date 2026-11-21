import React from 'react';
import { InferenceConfig } from '../../utils/studioEngine';
import { GlassCard } from '../glass/GlassCard';
import { GlassSlider } from '../glass/GlassSlider';
import { GlassSwitch } from '../glass/GlassSwitch';

interface InferenceControlsCardProps {
  config: InferenceConfig;
  onChange: (next: InferenceConfig) => void;
}

export function InferenceControlsCard({
  config,
  onChange,
}: InferenceControlsCardProps) {
  return (
    <GlassCard rounded="2xl" className="p-4">
      <div className="flex items-center justify-between gap-2 mb-3.5">
        <h2 className="text-[13px] font-bold text-white m-0">Inference controls</h2>
        <span className="font-mono-tabular text-[10px] tracking-[0.08em] text-white/65">
          LIVE CONFIG
        </span>
      </div>

      <div className="space-y-3.5">
        <GlassSlider
          id="temperature-slider"
          label="Temperature"
          value={config.temperature}
          displayValue={config.temperature.toFixed(2)}
          min={0}
          max={2}
          step={0.05}
          onChange={(temperature) => onChange({ ...config, temperature })}
        />

        <GlassSlider
          id="tokens-slider"
          label="Max output tokens"
          value={config.maxTokens}
          displayValue={config.maxTokens.toLocaleString()}
          min={128}
          max={4096}
          step={128}
          onChange={(maxTokens) => onChange({ ...config, maxTokens })}
        />

        <GlassSlider
          id="top-p-slider"
          label="Top P"
          value={config.topP}
          displayValue={config.topP.toFixed(2)}
          min={0.1}
          max={1}
          step={0.05}
          onChange={(topP) => onChange({ ...config, topP })}
        />
      </div>

      <div className="mt-4 pt-3 border-t border-white/15 space-y-1.5">
        <GlassSwitch
          id="stream-toggle"
          label="Streaming response"
          checked={config.streaming}
          onToggle={() => onChange({ ...config, streaming: !config.streaming })}
        />
        <GlassSwitch
          id="usage-toggle"
          label="Return usage metadata"
          checked={config.returnUsage}
          onToggle={() => onChange({ ...config, returnUsage: !config.returnUsage })}
        />
      </div>
    </GlassCard>
  );
}
