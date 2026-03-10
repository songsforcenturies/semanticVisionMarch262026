import React from 'react';
import { cn } from '@/lib/utils';

const BrutalBadge = React.forwardRef(({ 
  className, 
  variant = 'default',
  size = 'md',
  children,
  ...props 
}, ref) => {
  const baseStyles = 'inline-flex items-center font-bold uppercase rounded-md transition-all';
  
  const variants = {
    default: 'bg-[#f0ece4] text-[#5c564e] border border-black/10',
    indigo: 'bg-indigo-100/80 text-indigo-700 border border-indigo-200/60',
    emerald: 'bg-emerald-100/80 text-emerald-700 border border-emerald-200/60',
    rose: 'bg-rose-100/80 text-rose-700 border border-rose-200/60',
    amber: 'bg-amber-100/80 text-amber-700 border border-amber-200/60',
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base'
  };
  
  return (
    <span
      ref={ref}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </span>
  );
});

BrutalBadge.displayName = 'BrutalBadge';

export { BrutalBadge };
