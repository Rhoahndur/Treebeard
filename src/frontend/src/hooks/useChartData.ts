import { useMemo } from 'react';
import type { UsageData, RankedPlan } from '@/types/recommendation';

export interface MonthlyDataPoint {
  month: string;
  monthLabel: string;
  kwh: number;
  cost?: number;
}

export interface UseChartDataReturn {
  monthlyData: MonthlyDataPoint[];
  totalUsage: number;
  averageUsage: number;
  peakMonth: MonthlyDataPoint | null;
  lowMonth: MonthlyDataPoint | null;
}

export const useChartData = (
  usageData: UsageData[],
  plan?: RankedPlan
): UseChartDataReturn => {
  return useMemo(() => {
    if (!usageData || usageData.length === 0) {
      return {
        monthlyData: [],
        totalUsage: 0,
        averageUsage: 0,
        peakMonth: null,
        lowMonth: null,
      };
    }

    // Transform usage data
    const monthlyData: MonthlyDataPoint[] = usageData.map((data) => {
      const date = new Date(data.month);
      const monthLabel = date.toLocaleDateString('en-US', {
        month: 'short',
        year: '2-digit',
      });

      const cost = plan
        ? (data.kwh * plan.average_rate_per_kwh) / 100 + (plan.monthly_fee || 0)
        : undefined;

      return {
        month: data.month,
        monthLabel,
        kwh: data.kwh,
        cost,
      };
    });

    // Calculate statistics
    const totalUsage = monthlyData.reduce((sum, d) => sum + d.kwh, 0);
    const averageUsage = totalUsage / monthlyData.length;

    // Find peak and low months
    const sortedByUsage = [...monthlyData].sort((a, b) => b.kwh - a.kwh);
    const peakMonth = sortedByUsage[0] || null;
    const lowMonth = sortedByUsage[sortedByUsage.length - 1] || null;

    return {
      monthlyData,
      totalUsage,
      averageUsage,
      peakMonth,
      lowMonth,
    };
  }, [usageData, plan]);
};
