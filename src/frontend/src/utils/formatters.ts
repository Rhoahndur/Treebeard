/**
 * Utility functions for formatting data in the UI
 */

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatCurrencyDetailed = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatPercentage = (value: number, decimals = 0): string => {
  const fixed = value.toFixed(decimals);
  return fixed + '%';
};

export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('en-US').format(value);
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    year: 'numeric',
  }).format(date);
};

export const formatMonthYear = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    year: 'numeric',
  }).format(date);
};

export const getSavingsLevel = (savingsPercentage: number): 'high' | 'medium' | 'low' | 'none' => {
  if (savingsPercentage >= 15) return 'high';
  if (savingsPercentage >= 5) return 'medium';
  if (savingsPercentage > 0) return 'low';
  return 'none';
};

export const getSavingsBadgeVariant = (level: 'high' | 'medium' | 'low' | 'none') => {
  const variants = {
    high: 'success' as const,
    medium: 'info' as const,
    low: 'warning' as const,
    none: 'neutral' as const,
  };
  return variants[level];
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};
