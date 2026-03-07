import React from 'react';
import { cn } from '@/lib/utils';

const BrutalBadge = React.forwardRef(({ 
  className, 
  variant = 'default',
  size = 'md',
  children,
  ...props 
}, ref) => {
  const baseStyles = 'inline-block font-bold uppercase border-2 border-black';
  
  const variants = {
    default: 'bg-white text-black',
    indigo: 'bg-indigo-500 text-white',
    emerald: 'bg-emerald-500 text-white',
    rose: 'bg-rose-400 text-white',
    amber: 'bg-amber-400 text-black',
    baseline: 'bg-blue-400 text-white',
    target: 'bg-purple-500 text-white',
    stretch: 'bg-orange-500 text-white'
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base'
  };
  
  return (
    <span
      ref={ref}
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
});

BrutalBadge.displayName = 'BrutalBadge';

export { BrutalBadge };
