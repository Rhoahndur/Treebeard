import Papa from 'papaparse';
import type { MonthlyUsage } from '@/types/onboarding';

export interface CSVParseResult {
  success: boolean;
  data?: MonthlyUsage[];
  errors?: string[];
}

export interface CSVValidationError {
  row: number;
  field: string;
  message: string;
}

/**
 * Parse and validate CSV file for usage data
 * Expected format: month,kwh
 * Example: 2024-01,850
 */
export function parseUsageCSV(file: File): Promise<CSVParseResult> {
  return new Promise((resolve) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const errors: string[] = [];
        const usageData: MonthlyUsage[] = [];

        // Validate headers
        const headers = results.meta.fields || [];
        if (!headers.includes('month') || !headers.includes('kwh')) {
          errors.push('CSV must have "month" and "kwh" columns');
          resolve({ success: false, errors });
          return;
        }

        // Validate and transform data
        results.data.forEach((row: any, index: number) => {
          const rowNum = index + 2; // +2 for header and 0-index

          // Validate month format
          if (!row.month || typeof row.month !== 'string') {
            errors.push(`Row ${rowNum}: Missing or invalid month`);
            return;
          }

          // Parse and validate month (ISO date format)
          const monthDate = new Date(row.month);
          if (isNaN(monthDate.getTime())) {
            errors.push(`Row ${rowNum}: Invalid date format for month "${row.month}". Use YYYY-MM-DD format.`);
            return;
          }

          // Validate kWh value
          const kwh = parseFloat(row.kwh);
          if (isNaN(kwh)) {
            errors.push(`Row ${rowNum}: Invalid kWh value "${row.kwh}". Must be a number.`);
            return;
          }

          if (kwh < 0) {
            errors.push(`Row ${rowNum}: kWh value cannot be negative`);
            return;
          }

          if (kwh > 100000) {
            errors.push(`Row ${rowNum}: kWh value seems unrealistically high (${kwh})`);
            return;
          }

          // Add to usage data
          usageData.push({
            month: formatToFirstDayOfMonth(monthDate),
            kwh: Math.round(kwh), // Round to nearest integer
          });
        });

        // Check minimum data requirements
        if (usageData.length < 3) {
          errors.push('At least 3 months of usage data required');
        }

        if (usageData.length > 24) {
          errors.push('Maximum 24 months of usage data allowed');
        }

        // Check for duplicate months
        const months = usageData.map((d) => d.month);
        const duplicates = months.filter((month, index) => months.indexOf(month) !== index);
        if (duplicates.length > 0) {
          errors.push(`Duplicate months found: ${duplicates.join(', ')}`);
        }

        if (errors.length > 0) {
          resolve({ success: false, errors });
        } else {
          // Sort by month ascending
          usageData.sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime());
          resolve({ success: true, data: usageData });
        }
      },
      error: (error) => {
        resolve({
          success: false,
          errors: [`Failed to parse CSV: ${error.message}`],
        });
      },
    });
  });
}

/**
 * Format date to first day of month in ISO format
 */
function formatToFirstDayOfMonth(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}-01`;
}

/**
 * Generate example CSV content
 */
export function generateExampleCSV(): string {
  const months: MonthlyUsage[] = [];
  const now = new Date();

  for (let i = 11; i >= 0; i--) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const month = formatToFirstDayOfMonth(date);
    const kwh = Math.round(600 + Math.random() * 400); // Random between 600-1000 kWh

    months.push({ month, kwh });
  }

  const header = 'month,kwh\n';
  const rows = months.map((m) => `${m.month},${m.kwh}`).join('\n');

  return header + rows;
}

/**
 * Download example CSV file
 */
export function downloadExampleCSV(): void {
  const csvContent = generateExampleCSV();
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', 'example_usage_data.csv');
  link.style.visibility = 'hidden';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/**
 * Validate file before parsing
 */
export function validateCSVFile(file: File): { valid: boolean; error?: string } {
  // Check file type
  if (!file.name.endsWith('.csv') && file.type !== 'text/csv') {
    return { valid: false, error: 'File must be a CSV file' };
  }

  // Check file size (max 5MB)
  const maxSize = 5 * 1024 * 1024; // 5MB
  if (file.size > maxSize) {
    return { valid: false, error: 'File size must be less than 5MB' };
  }

  return { valid: true };
}
