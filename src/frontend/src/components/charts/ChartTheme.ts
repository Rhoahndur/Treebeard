/**
 * Chart Theme Configuration for TreeBeard
 * Provides consistent, colorblind-friendly colors and styling for all charts
 */

export const chartColors = {
  // Primary colors
  primary: '#3B82F6',      // Blue (recommended plan)
  secondary: '#10B981',    // Green (savings)
  tertiary: '#F59E0B',     // Orange (current plan)
  danger: '#EF4444',       // Red (risks, high costs)
  success: '#22C55E',      // Green (positive changes)
  neutral: '#6B7280',      // Gray (neutral data)

  // Seasonal colors (colorblind-friendly)
  winter: '#60A5FA',       // Light blue
  spring: '#34D399',       // Green
  summer: '#FBBF24',       // Yellow
  fall: '#F97316',         // Orange

  // Data series (for multi-line charts)
  series1: '#3B82F6',      // Blue
  series2: '#8B5CF6',      // Purple
  series3: '#EC4899',      // Pink
  series4: '#10B981',      // Green
  series5: '#F59E0B',      // Orange

  // Cost categories
  baseCost: '#3B82F6',     // Blue
  fees: '#F59E0B',         // Orange
  taxes: '#8B5CF6',        // Purple
  renewable: '#10B981',    // Green
};

export const chartTypography = {
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  fontSize: {
    xs: 10,
    sm: 12,
    base: 14,
    lg: 16,
    xl: 18,
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
};

export const chartSpacing = {
  margin: {
    top: 20,
    right: 30,
    bottom: 30,
    left: 40,
  },
  padding: {
    sm: 8,
    md: 16,
    lg: 24,
  },
};

export const chartSizing = {
  height: {
    mobile: 200,
    tablet: 250,
    desktop: 300,
    dashboard: 250,
  },
  width: '100%', // Responsive
};

export const chartTooltipStyle = {
  backgroundColor: 'rgba(255, 255, 255, 0.96)',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '12px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  fontSize: chartTypography.fontSize.sm,
  fontFamily: chartTypography.fontFamily,
};

export const chartGridStyle = {
  stroke: '#e5e7eb',
  strokeDasharray: '3 3',
  strokeWidth: 1,
};

export const chartAxisStyle = {
  stroke: '#9ca3af',
  fontSize: chartTypography.fontSize.sm,
  fontFamily: chartTypography.fontFamily,
};

export const chartLegendStyle = {
  fontSize: chartTypography.fontSize.sm,
  fontFamily: chartTypography.fontFamily,
  iconSize: 14,
  iconType: 'circle' as const,
};

// Gradient definitions for area charts
export const chartGradients = {
  savings: {
    start: '#22C55E',
    end: '#22C55E',
    opacity: { start: 0.8, end: 0.1 },
  },
  cost: {
    start: '#3B82F6',
    end: '#3B82F6',
    opacity: { start: 0.8, end: 0.1 },
  },
  usage: {
    start: '#F59E0B',
    end: '#F59E0B',
    opacity: { start: 0.8, end: 0.1 },
  },
};

// Accessibility labels
export const getAriaLabel = {
  lineChart: (title: string) => `Line chart showing ${title}`,
  barChart: (title: string) => `Bar chart showing ${title}`,
  areaChart: (title: string) => `Area chart showing ${title}`,
  pieChart: (title: string) => `Pie chart showing ${title}`,
  composedChart: (title: string) => `Combined chart showing ${title}`,
};

// Helper function to get seasonal color
export const getSeasonalColor = (month: number): string => {
  if (month >= 12 || month <= 2) return chartColors.winter;
  if (month >= 3 && month <= 5) return chartColors.spring;
  if (month >= 6 && month <= 8) return chartColors.summer;
  return chartColors.fall; // 9-11
};

// Helper function to get series color
export const getSeriesColor = (index: number): string => {
  const colors = [
    chartColors.series1,
    chartColors.series2,
    chartColors.series3,
    chartColors.series4,
    chartColors.series5,
  ];
  return colors[index % colors.length];
};
