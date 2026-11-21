import React from 'react';

interface GlassNavigationItemProps {
  label: string;
  icon: React.ReactNode;
  active: boolean;
  onClick: () => void;
}

export function GlassNavigationItem({
  label,
  icon,
  active,
  onClick,
}: GlassNavigationItemProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-current={active ? 'page' : undefined}
      className={`w-full flex items-center gap-3 px-3 py-2.5 min-h-[42px] rounded-[16px] text-left text-[13px] font-semibold transition-all duration-200 cursor-pointer select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 ${
        active
          ? 'frosted-glass-bright text-white'
          : 'text-white/75 border border-transparent hover:bg-white/10 hover:border-white/20 hover:text-white active:scale-[0.98]'
      }`}
    >
      <span
        className={`w-7 h-7 rounded-[10px] grid place-items-center shrink-0 transition-colors ${
          active
            ? 'bg-white/22 text-white border border-white/35 shadow-[inset_0_1px_0_rgba(255,255,255,0.45)]'
            : 'bg-white/8 text-white/75 border border-white/10'
        }`}
        aria-hidden="true"
      >
        {icon}
      </span>
      <span className="truncate">{label}</span>
    </button>
  );
}
