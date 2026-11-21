import React from 'react';

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'glass' | 'liquid';
  size?: 'sm' | 'md';
  children: React.ReactNode;
}

export function GlassButton({
  variant = 'glass',
  size = 'md',
  className = '',
  type = 'button',
  children,
  ...rest
}: GlassButtonProps) {
  const sizeClass =
    size === 'sm'
      ? 'px-3.5 py-2 text-xs min-h-[36px]'
      : 'px-4 py-2.5 text-xs min-h-[40px]';

  const variantClass =
    variant === 'primary'
      ? 'frosted-cta font-bold hover:brightness-105'
      : variant === 'liquid'
        ? 'liquidglass text-white font-semibold hover:brightness-110'
        : 'frosted-well text-white/95 font-medium hover:bg-white/20 hover:border-white/35';

  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 rounded-full whitespace-nowrap shrink-0 cursor-pointer select-none transition-all duration-150 ease-out active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 disabled:opacity-45 disabled:cursor-not-allowed ${sizeClass} ${variantClass} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
