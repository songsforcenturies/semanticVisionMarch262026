import React from 'react';
import { cn } from '@/lib/utils';

const BrutalProgress = React.forwardRef(({ 
  className,
  value = 0,
  max = 100,
  variant = 'default',
  size = 'md',
  showLabel = false,
  ...props 
}, ref) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const variants = {
    default: 'bg-gray-200',
    indigo: 'bg-indigo-100',
    emerald: 'bg-emerald-100',
    amber: 'bg-amber-100',
    rose: 'bg-rose-100'
  };
  
  const fillVariants = {
    default: 'bg-black',
    indigo: 'bg-indigo-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-400',
    rose: 'bg-rose-400'
  };
  
  const sizes = {
    sm: 'h-4',
    md: 'h-6',
    lg: 'h-8'
  };
  
  return (
    <div ref={ref} className={cn('w-full', className)} {...props}>
      <div className={cn(
        'w-full border-4 border-black overflow-hidden',
        variants[variant],
        sizes[size]
      )}>
        <div
          className={cn(
            'h-full transition-all duration-500 ease-out',
            fillVariants[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <p className="mt-1 text-sm font-bold text-right">
          {value} / {max} ({Math.round(percentage)}%)
        </p>
      )}
    </div>
  );
});

BrutalProgress.displayName = 'BrutalProgress';

export { BrutalProgress };
