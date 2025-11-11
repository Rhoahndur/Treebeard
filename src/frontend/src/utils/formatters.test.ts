import { describe, it, expect } from 'vitest';
import { 
  formatCurrency, 
  formatPercentage, 
  formatNumber,
  getSavingsLevel,
  getSavingsBadgeVariant 
} from './formatters';

describe('formatters', () => {
  describe('formatCurrency', () => {
    it('formats positive numbers as currency', () => {
      expect(formatCurrency(1234)).toBe('$1,234');
      expect(formatCurrency(1234.56)).toBe('$1,235');
    });

    it('formats negative numbers as currency', () => {
      expect(formatCurrency(-1234)).toBe('-$1,234');
    });

    it('formats zero', () => {
      expect(formatCurrency(0)).toBe('$0');
    });
  });

  describe('formatPercentage', () => {
    it('formats percentages with default decimals', () => {
      expect(formatPercentage(14.7)).toBe('15%');
      expect(formatPercentage(14.7, 1)).toBe('14.7%');
      expect(formatPercentage(14.7, 2)).toBe('14.70%');
    });
  });

  describe('formatNumber', () => {
    it('formats numbers with thousands separator', () => {
      expect(formatNumber(1234)).toBe('1,234');
      expect(formatNumber(1234567)).toBe('1,234,567');
    });
  });

  describe('getSavingsLevel', () => {
    it('returns correct savings level', () => {
      expect(getSavingsLevel(20)).toBe('high');
      expect(getSavingsLevel(15)).toBe('high');
      expect(getSavingsLevel(10)).toBe('medium');
      expect(getSavingsLevel(5)).toBe('medium');
      expect(getSavingsLevel(3)).toBe('low');
      expect(getSavingsLevel(0)).toBe('none');
      expect(getSavingsLevel(-5)).toBe('none');
    });
  });

  describe('getSavingsBadgeVariant', () => {
    it('returns correct badge variant', () => {
      expect(getSavingsBadgeVariant('high')).toBe('success');
      expect(getSavingsBadgeVariant('medium')).toBe('info');
      expect(getSavingsBadgeVariant('low')).toBe('warning');
      expect(getSavingsBadgeVariant('none')).toBe('neutral');
    });
  });
});
