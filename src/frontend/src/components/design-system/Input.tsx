import React from 'react';
import { clsx } from 'clsx';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ 
    label,
    error,
    helperText,
    fullWidth = false,
    className,
    id,
    ...props 
  }, ref) => {
    const inputId = id || 'input-' + Date.now();
    
    return (
      <div className={clsx(fullWidth && 'w-full')}>
        {label && (
          <label 
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={clsx(
            'block w-full rounded-lg border px-3 py-2 text-base',
            'transition-colors duration-200',
            'focus:outline-none focus:ring-2 focus:ring-offset-2',
            'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
            error 
              ? 'border-danger text-danger-dark focus:border-danger focus:ring-danger' 
              : 'border-gray-300 text-gray-900 focus:border-primary-600 focus:ring-primary-500',
            className
          )}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={
            error ? inputId + '-error' : helperText ? inputId + '-helper' : undefined
          }
          {...props}
        />
        {error && (
          <p id={inputId + '-error'} className="mt-1 text-sm text-danger" role="alert">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={inputId + '-helper'} className="mt-1 text-sm text-gray-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
