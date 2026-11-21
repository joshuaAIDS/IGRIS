import React from 'react';
import { ChevronDown } from 'lucide-react';

export interface GlassDropdownOption {
  value: string;
  label: string;
}

interface GlassDropdownProps {
  id: string;
  label: string;
  value: string;
  options: GlassDropdownOption[];
  onChange: (value: string) => void;
}

export function GlassDropdown({
  id,
  label,
  value,
  options,
  onChange,
}: GlassDropdownProps) {
  return (
    <div className="relative">
      <label htmlFor={id} className="sr-only">
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="frosted-well w-full appearance-none rounded-[16px] px-3.5 py-2.5 pr-10 text-xs font-semibold text-white outline-none cursor-pointer transition-colors hover:bg-white/15 focus-visible:ring-2 focus-visible:ring-white/70"
      >
        {options.map((opt) => (
          <option
            key={opt.value}
            value={opt.value}
            className="bg-[#0e152c] text-white"
          >
            {opt.label}
          </option>
        ))}
      </select>
      <ChevronDown
        size={15}
        className="pointer-events-none absolute right-3.5 top-1/2 -translate-y-1/2 text-white/80"
        aria-hidden="true"
      />
    </div>
  );
}
