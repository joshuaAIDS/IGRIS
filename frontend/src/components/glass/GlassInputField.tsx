import React from 'react';

interface GlassInputFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  leadingIcon?: React.ReactNode;
  trailingAction?: React.ReactNode;
  containerClassName?: string;
}

export const GlassInputField = React.forwardRef<HTMLInputElement, GlassInputFieldProps>(
  function GlassInputField(
    { leadingIcon, trailingAction, containerClassName = '', className = '', ...rest },
    ref,
  ) {
    return (
      <div
        className={`frosted-well flex items-center gap-2.5 rounded-[20px] px-3.5 py-2 transition-all duration-150 focus-within:border-white/45 focus-within:bg-white/15 ${containerClassName}`}
      >
        {leadingIcon && (
          <span className="text-white/70 shrink-0 grid place-items-center" aria-hidden="true">
            {leadingIcon}
          </span>
        )}
        <input
          ref={ref}
          className={`flex-1 min-w-0 bg-transparent border-0 outline-none text-[13px] text-white placeholder:text-white/55 py-1.5 ${className}`}
          {...rest}
        />
        {trailingAction}
      </div>
    );
  },
);
