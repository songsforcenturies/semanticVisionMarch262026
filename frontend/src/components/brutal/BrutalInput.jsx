import React from 'react';
import { cn } from '@/lib/utils';

const BrutalInput = React.forwardRef(({ 
  className,
  label,
  error,
  variant = 'default',
  ...props 
}, ref) => {
  const baseStyles = 'w-full px-4 py-3 border-4 border-black font-medium focus:outline-none focus:ring-4 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    default: 'bg-white',
    pin: 'bg-yellow-100 text-center text-2xl font-bold tracking-widest'
  };
  
  return (
    <div className="w-full">
      {label && (
        <label className="block mb-2 font-bold uppercase text-sm">
          {label}
        </label>
      )}
      <input
        ref={ref}
        className={cn(
          baseStyles,
          variants[variant],
          error && 'border-rose-500 focus:ring-rose-500',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-rose-500 font-medium">{error}</p>
      )}
    </div>
  );
});

BrutalInput.displayName = 'BrutalInput';

export { BrutalInput };
