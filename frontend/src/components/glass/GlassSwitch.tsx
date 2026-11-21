import React from 'react';

interface GlassSwitchProps {
  id: string;
  label: string;
  checked: boolean;
  onToggle: () => void;
}

export function GlassSwitch({ id, label, checked, onToggle }: GlassSwitchProps) {
  return (
    <div className="flex items-center justify-between gap-3 py-1">
      <label htmlFor={id} className="text-xs text-white/85 font-medium cursor-pointer">
        {label}
      </label>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={onToggle}
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border transition-all duration-200 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/75 ${
          checked
            ? 'bg-gradient-to-r from-[#80e8ff]/75 to-[#a896ff]/80 border-white/50 shadow-[0_0_14px_rgba(145,215,255,0.3)]'
            : 'bg-white/15 border-white/25'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 rounded-full bg-white shadow-[0_2px_6px_rgba(0,0,0,0.35)] transition-transform duration-200 ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );
}
