/**
 * Utility functions for formatting data in the UI
 */

export const formatCurrency = (amount: number | string): string => {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(numAmount);
};

export const formatCurrencyDetailed = (amount: number | string): string => {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numAmount);
};

export const formatPercentage = (value: number | string, decimals = 0): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  const fixed = numValue.toFixed(decimals);
  return fixed + '%';
};

export const formatNumber = (value: number | string): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  return new Intl.NumberFormat('en-US').format(numValue);
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

export const getSavingsLevel = (savingsPercentage: number | string): 'high' | 'medium' | 'low' | 'none' => {
  const numPercentage = typeof savingsPercentage === 'string' ? parseFloat(savingsPercentage) : savingsPercentage;
  if (numPercentage >= 15) return 'high';
  if (numPercentage >= 5) return 'medium';
  if (numPercentage > 0) return 'low';
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
