import React from 'react';
import { cn } from '@/lib/utils';

const variantStyles = {
  default: { backgroundColor: '#ffffff', color: '#111827' },
  indigo: { backgroundColor: '#e0e7ff', color: '#111827' },
  emerald: { backgroundColor: '#d1fae5', color: '#111827' },
  rose: { backgroundColor: '#ffe4e6', color: '#111827' },
  amber: { backgroundColor: '#fef3c7', color: '#111827' },
  dark: { backgroundColor: '#111827', color: '#ffffff' },
};

const BrutalCard = React.forwardRef(({ 
  className, 
  variant = 'default',
  shadow = 'lg',
  hover = false,
  style: userStyle,
  children,
  ...props 
}, ref) => {
  const baseStyles = 'border-4 border-black p-6 transition-all';
  
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
        shadows[shadow],
        hover && 'hover:translate-x-1 hover:translate-y-1 hover:shadow-xl cursor-pointer',
        className
      )}
      style={{ ...variantStyles[variant], ...userStyle }}
      {...props}
    >
      {children}
    </div>
  );
});

BrutalCard.displayName = 'BrutalCard';

export { BrutalCard };
