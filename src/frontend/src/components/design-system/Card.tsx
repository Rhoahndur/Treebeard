import React from 'react';
import { clsx } from 'clsx';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
  clickable?: boolean;
  children: React.ReactNode;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ 
    variant = 'default',
    padding = 'md',
    hoverable = false,
    clickable = false,
    className,
    children,
    ...props
  }, ref) => {
    const baseStyles = 'bg-white rounded-card transition-all duration-200';
    
    const variantStyles = {
      default: 'shadow-card',
      bordered: 'border border-gray-200',
      elevated: 'shadow-card-hover',
    };
    
    const paddingStyles = {
      none: '',
      sm: 'p-4',
      md: 'p-6',
      lg: 'p-8',
    };
    
    const interactiveStyles = hoverable 
      ? 'hover:shadow-card-hover hover:-translate-y-0.5'
      : '';
    
    const clickableStyles = clickable
      ? 'cursor-pointer active:shadow-card'
      : '';
    
    return (
      <div
        ref={ref}
        className={clsx(
          baseStyles,
          variantStyles[variant],
          paddingStyles[padding],
          interactiveStyles,
          clickableStyles,
          className
        )}
        role={clickable ? 'button' : undefined}
        tabIndex={clickable ? 0 : undefined}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ 
  className, 
  children, 
  ...props 
}) => (
  <div className={clsx('mb-4', className)} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ 
  className, 
  children, 
  ...props 
}) => (
  <h3 className={clsx('text-xl font-semibold text-gray-900', className)} {...props}>
    {children}
  </h3>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ 
  className, 
  children, 
  ...props 
}) => (
  <div className={clsx('text-gray-700', className)} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ 
  className, 
  children, 
  ...props 
}) => (
  <div className={clsx('mt-4 pt-4 border-t border-gray-200', className)} {...props}>
    {children}
  </div>
);
