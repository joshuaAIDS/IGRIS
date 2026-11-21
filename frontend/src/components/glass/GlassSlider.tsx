import React from 'react';

interface GlassSliderProps {
  id: string;
  label: string;
  value: number;
  displayValue: string;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}

export function GlassSlider({
  id,
  label,
  value,
  displayValue,
  min,
  max,
  step,
  onChange,
}: GlassSliderProps) {
  const pct = Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100));

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2 text-xs">
        <label htmlFor={id} className="text-white/85 font-medium">
          {label}
        </label>
        <output
          htmlFor={id}
          className="font-mono-tabular text-xs font-medium text-[#a9f1ff]"
        >
          {displayValue}
        </output>
      </div>
      <div className="relative flex items-center py-1">
        <input
          id={id}
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          style={{
            background: `linear-gradient(90deg, rgba(168,238,255,0.75) 0%, rgba(190,175,255,0.8) ${pct}%, rgba(255,255,255,0.16) ${pct}%)`,
          }}
          className="glass-range focus-visible:ring-2 focus-visible:ring-white/60"
        />
      </div>
    </div>
  );
}
