import React, { useEffect } from 'react';
import { clsx } from 'clsx';
import { Button } from '@/components/design-system/Button';

/**
 * ConfirmDialog Component
 *
 * Modal dialog for confirming destructive or important actions.
 * Shows a title, message, and confirm/cancel buttons with appropriate styling
 * based on the variant (danger, warning, info).
 *
 * @example
 * <ConfirmDialog
 *   open={isOpen}
 *   title="Delete User"
 *   message="Are you sure you want to delete this user? This action cannot be undone."
 *   variant="danger"
 *   onConfirm={handleDelete}
 *   onCancel={() => setIsOpen(false)}
 * />
 */

export interface ConfirmDialogProps {
  /** Whether the dialog is open */
  open: boolean;
  /** Dialog title */
  title: string;
  /** Dialog message/description */
  message: string;
  /** Visual variant */
  variant?: 'danger' | 'warning' | 'info';
  /** Confirm button text */
  confirmText?: string;
  /** Cancel button text */
  cancelText?: string;
  /** Confirm button loading state */
  loading?: boolean;
  /** Confirm handler */
  onConfirm: () => void;
  /** Cancel handler */
  onCancel: () => void;
}

/**
 * ConfirmDialog Component
 */
export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  message,
  variant = 'danger',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  loading = false,
  onConfirm,
  onCancel,
}) => {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open && !loading) {
        onCancel();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [open, loading, onCancel]);

  // Prevent body scroll when dialog is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [open]);

  if (!open) return null;

  const variantStyles = {
    danger: {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      iconBg: 'bg-danger-light',
      iconColor: 'text-danger',
      confirmButton: 'bg-danger text-white hover:bg-danger-dark focus:ring-danger',
    },
    warning: {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      iconBg: 'bg-warning-light',
      iconColor: 'text-warning-dark',
      confirmButton: 'bg-warning-dark text-white hover:bg-warning focus:ring-warning',
    },
    info: {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      iconBg: 'bg-info-light',
      iconColor: 'text-info-dark',
      confirmButton: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
    },
  };

  const styles = variantStyles[variant];

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity z-40"
        onClick={!loading ? onCancel : undefined}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        className="fixed inset-0 z-50 overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
      >
        <div className="flex min-h-full items-center justify-center p-4">
          <div
            className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Icon */}
            <div className={clsx('mx-auto flex items-center justify-center h-12 w-12 rounded-full', styles.iconBg)}>
              <div className={styles.iconColor}>
                {styles.icon}
              </div>
            </div>

            {/* Title */}
            <h3
              id="confirm-dialog-title"
              className="mt-4 text-lg font-semibold text-gray-900 text-center"
            >
              {title}
            </h3>

            {/* Message */}
            <p className="mt-2 text-sm text-gray-600 text-center">
              {message}
            </p>

            {/* Actions */}
            <div className="mt-6 flex items-center justify-center space-x-3">
              <Button
                variant="outline"
                onClick={onCancel}
                disabled={loading}
                className="min-w-[100px]"
              >
                {cancelText}
              </Button>
              <button
                onClick={onConfirm}
                disabled={loading}
                className={clsx(
                  'min-w-[100px] px-4 py-2 rounded-lg font-medium transition-colors',
                  'focus:outline-none focus:ring-2 focus:ring-offset-2',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  styles.confirmButton
                )}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <svg
                      className="animate-spin h-4 w-4"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                  </div>
                ) : (
                  confirmText
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
