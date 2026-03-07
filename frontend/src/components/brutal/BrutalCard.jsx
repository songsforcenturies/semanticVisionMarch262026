import React from 'react';
import { cn } from '@/lib/utils';

const BrutalCard = React.forwardRef(({ 
  className, 
  variant = 'default',
  shadow = 'lg',
  hover = false,
  children,
  ...props 
}, ref) => {
  const baseStyles = 'border-6 border-black p-6 transition-all';
  
  const variants = {
    default: 'bg-white',
    indigo: 'bg-indigo-100',
    emerald: 'bg-emerald-100',
    rose: 'bg-rose-100',
    amber: 'bg-amber-100',
    dark: 'bg-gray-900 text-white'
  };
  
  const shadows = {
    sm: 'brutal-shadow-sm',
    md: 'brutal-shadow-md',
    lg: 'brutal-shadow-lg',
    xl: 'brutal-shadow-xl'
  };
  
  return (
    <div
      ref={ref}
      className={cn(
        baseStyles,
        variants[variant],
        shadows[shadow],
        hover && 'hover:translate-x-1 hover:translate-y-1 hover:shadow-xl cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
});

BrutalCard.displayName = 'BrutalCard';

export { BrutalCard };
