import React from 'react';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'frosted' | 'liquid' | 'bright';
  rounded?: 'xl' | '2xl' | '3xl';
  children: React.ReactNode;
}

const RADIUS_CLASS: Record<NonNullable<GlassCardProps['rounded']>, string> = {
  xl: 'rounded-[22px]',
  '2xl': 'rounded-[26px]',
  '3xl': 'rounded-[30px]',
};

export function GlassCard({
  variant = 'liquid',
  rounded = '2xl',
  className = '',
  children,
  ...rest
}: GlassCardProps) {
  const surfaceClass =
    variant === 'bright'
      ? 'liquidglass liquidglass-bright'
      : 'liquidglass';

  return (
    <div
      className={`relative ${surfaceClass} ${RADIUS_CLASS[rounded]} transition-[box-shadow,background-color,transform] duration-200 ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}
