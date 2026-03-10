import React from 'react';
import { cn } from '@/lib/utils';

const variantStyles = {
  default: { backgroundColor: '#f8f6f1', color: '#2d2a26' },
  indigo: { backgroundColor: '#e8e4f0', color: '#2d2a3e' },
  emerald: { backgroundColor: '#e4f0e8', color: '#1a3324' },
  rose: { backgroundColor: '#f0e4e6', color: '#3e1a22' },
  amber: { backgroundColor: '#f0ece4', color: '#3e3018' },
  dark: { backgroundColor: '#1e1e2e', color: '#e8e4f0' },
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
  const baseStyles = 'border-4 border-black/20 rounded-lg p-6 transition-all';
  
  const shadows = {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl'
  };
  
  return (
    <div
      ref={ref}
      className={cn(
        baseStyles,
        shadows[shadow],
        hover && 'hover:translate-y-[-2px] hover:shadow-xl cursor-pointer',
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
