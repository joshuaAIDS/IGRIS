import React from 'react';

interface GlassIconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'glass' | 'cta' | 'liquid';
  size?: 'sm' | 'md';
  children: React.ReactNode;
}

export function GlassIconButton({
  variant = 'glass',
  size = 'md',
  className = '',
  type = 'button',
  children,
  ...rest
}: GlassIconButtonProps) {
  const sizeClass = size === 'sm' ? 'w-9 h-9' : 'w-10 h-10';
  const variantClass =
    variant === 'cta'
      ? 'frosted-cta'
      : variant === 'liquid'
        ? 'liquidglass text-white hover:brightness-110'
        : 'frosted-well text-white/95 hover:bg-white/20 hover:border-white/40';

  return (
    <button
      type={type}
      className={`inline-grid place-items-center rounded-full shrink-0 cursor-pointer select-none transition-all duration-150 ease-out active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 disabled:opacity-45 disabled:cursor-not-allowed ${sizeClass} ${variantClass} ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
