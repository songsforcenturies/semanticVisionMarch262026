import React from 'react';
import { cn } from '@/lib/utils';

const BrutalButton = React.forwardRef(({ 
  className, 
  variant = 'default', 
  size = 'md',
  fullWidth = false,
  children, 
  ...props 
}, ref) => {
  const baseStyles = 'font-bold uppercase transition-all rounded-lg disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.97]';
  
  const variants = {
    default: 'bg-[#f8f6f1] text-[#2d2a26] border-2 border-black/15 shadow-sm hover:shadow-md',
    indigo: 'bg-indigo-500/90 text-white border-2 border-indigo-600/30 shadow-sm hover:shadow-md hover:bg-indigo-500',
    emerald: 'bg-emerald-500/90 text-white border-2 border-emerald-600/30 shadow-sm hover:shadow-md hover:bg-emerald-500',
    rose: 'bg-rose-400/90 text-white border-2 border-rose-500/30 shadow-sm hover:shadow-md hover:bg-rose-400',
    amber: 'bg-amber-400/90 text-[#3e3018] border-2 border-amber-500/30 shadow-sm hover:shadow-md hover:bg-amber-400',
    dark: 'bg-[#1e1e2e] text-white border-2 border-white/10 shadow-sm hover:shadow-md',
    ghost: 'bg-transparent border-2 border-black/15 text-[#2d2a26] hover:bg-black/5'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-5 py-2.5 text-sm',
    lg: 'px-7 py-3.5 text-base',
    xl: 'px-9 py-4.5 text-lg'
  };
  
  return (
    <button
      ref={ref}
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
});

BrutalButton.displayName = 'BrutalButton';

export { BrutalButton };
