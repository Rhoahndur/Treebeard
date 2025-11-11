import React from 'react';
import { clsx } from 'clsx';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'renewable';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ 
  variant = 'neutral',
  size = 'md',
  className,
  children,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center font-medium rounded-full';
  
  const variantStyles = {
    success: 'bg-success-light text-success-dark',
    warning: 'bg-warning-light text-warning-dark',
    danger: 'bg-danger-light text-danger-dark',
    info: 'bg-info-light text-info-dark',
    neutral: 'bg-gray-100 text-gray-700',
    renewable: 'bg-renewable-100 text-renewable-700',
  };
  
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };
  
  return (
    <span
      className={clsx(
        baseStyles,
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

Badge.displayName = 'Badge';
