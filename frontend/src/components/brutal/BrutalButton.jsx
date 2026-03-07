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
  const baseStyles = 'font-bold uppercase transition-all brutal-active disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    default: 'bg-white text-black border-4 border-black brutal-shadow-md hover:brutal-shadow-lg',
    indigo: 'bg-indigo-500 text-white border-4 border-black brutal-shadow-md hover:brutal-shadow-indigo',
    emerald: 'bg-emerald-500 text-white border-4 border-black brutal-shadow-md hover:brutal-shadow-emerald',
    rose: 'bg-rose-400 text-white border-4 border-black brutal-shadow-md hover:brutal-shadow-rose',
    amber: 'bg-amber-400 text-black border-4 border-black brutal-shadow-md hover:brutal-shadow-amber',
    dark: 'bg-black text-white border-4 border-black brutal-shadow-md hover:brutal-shadow-lg',
    ghost: 'bg-transparent border-4 border-black text-black hover:bg-gray-100'
  };
  
  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
    xl: 'px-10 py-5 text-xl'
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
