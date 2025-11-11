import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot,
} from 'recharts';
import { ChartWrapper } from './ChartWrapper';
import { ChartTooltip } from './ChartTooltip';
import { chartColors, chartGridStyle, chartAxisStyle } from './ChartTheme';
import type { UsageData } from '@/types/recommendation';
import { formatNumber } from '@/utils/formatters';

export interface SeasonalPatternChartProps {
  usageData: UsageData[];
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}

interface SeasonalData {
  month: string;
  monthLabel: string;
  winter: number | null;
  spring: number | null;
  summer: number | null;
  fall: number | null;
}

export const SeasonalPatternChart: React.FC<SeasonalPatternChartProps> = ({
  usageData,
  isLoading = false,
  error = null,
  height = 300,
}) => {
  const { chartData, currentSeason, currentMonthIndex } = useMemo(() => {
    if (!usageData || usageData.length === 0) {
      return { chartData: [], currentSeason: '', currentMonthIndex: -1 };
    }

    // Group data by season and month
    const seasonalMap = new Map<string, { winter: number[]; spring: number[]; summer: number[]; fall: number[] }>();

    usageData.forEach((data) => {
      const date = new Date(data.month);
      const monthNum = date.getMonth(); // 0-11
      const monthKey = monthNum.toString();

      let season: 'winter' | 'spring' | 'summer' | 'fall' = 'winter';
      if (monthNum >= 3 && monthNum <= 5) season = 'spring';
      else if (monthNum >= 6 && monthNum <= 8) season = 'summer';
      else if (monthNum >= 9 && monthNum <= 11) season = 'fall';

      if (!seasonalMap.has(monthKey)) {
        seasonalMap.set(monthKey, { winter: [], spring: [], summer: [], fall: [] });
      }

      seasonalMap.get(monthKey)![season].push(data.kwh);
    });

    // Create chart data with average for each season per month
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];

    const data: SeasonalData[] = months.map((monthLabel, index) => {
      const monthData = seasonalMap.get(index.toString());

      const avgWinter = monthData?.winter.length
        ? monthData.winter.reduce((a, b) => a + b, 0) / monthData.winter.length
        : null;
      const avgSpring = monthData?.spring.length
        ? monthData.spring.reduce((a, b) => a + b, 0) / monthData.spring.length
        : null;
      const avgSummer = monthData?.summer.length
        ? monthData.summer.reduce((a, b) => a + b, 0) / monthData.summer.length
        : null;
      const avgFall = monthData?.fall.length
        ? monthData.fall.reduce((a, b) => a + b, 0) / monthData.fall.length
        : null;

      return {
        month: index.toString(),
        monthLabel,
        winter: avgWinter,
        spring: avgSpring,
        summer: avgSummer,
        fall: avgFall,
      };
    });

    // Determine current season
    const now = new Date();
    const nowMonth = now.getMonth();
    let currentSeason = 'Winter';
    if (nowMonth >= 3 && nowMonth <= 5) currentSeason = 'Spring';
    else if (nowMonth >= 6 && nowMonth <= 8) currentSeason = 'Summer';
    else if (nowMonth >= 9 && nowMonth <= 11) currentSeason = 'Fall';

    return { chartData: data, currentSeason, currentMonthIndex: nowMonth };
  }, [usageData]);

  if (chartData.length === 0 && !isLoading && !error) {
    return (
      <ChartWrapper
        title="Seasonal Usage Patterns"
        subtitle="Typical usage patterns by season"
        error="No seasonal data available"
        height={height}
      />
    );
  }

  return (
    <ChartWrapper
      title="Seasonal Usage Patterns"
      subtitle={`Typical usage patterns by season • Current: ${currentSeason}`}
      isLoading={isLoading}
      error={error}
      height={height}
      ariaLabel="Line chart showing seasonal energy usage patterns throughout the year"
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid {...chartGridStyle} />
          <XAxis
            dataKey="monthLabel"
            {...chartAxisStyle}
          />
          <YAxis
            {...chartAxisStyle}
            label={{
              value: 'kWh',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12 },
            }}
          />
          <Tooltip
            content={
              <ChartTooltip
                formatter={(value, name) => `${formatNumber(Number(value))} kWh`}
              />
            }
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          <Line
            type="monotone"
            dataKey="winter"
            name="Winter"
            stroke={chartColors.winter}
            strokeWidth={currentSeason === 'Winter' ? 3 : 2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="spring"
            name="Spring"
            stroke={chartColors.spring}
            strokeWidth={currentSeason === 'Spring' ? 3 : 2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="summer"
            name="Summer"
            stroke={chartColors.summer}
            strokeWidth={currentSeason === 'Summer' ? 3 : 2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="fall"
            name="Fall"
            stroke={chartColors.fall}
            strokeWidth={currentSeason === 'Fall' ? 3 : 2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            connectNulls
          />
          {/* Highlight current month */}
          {currentMonthIndex >= 0 && (
            <ReferenceDot
              x={chartData[currentMonthIndex]?.monthLabel}
              y={0}
              r={0}
              label={{
                value: 'Current',
                position: 'top',
                fill: chartColors.neutral,
                fontSize: 10,
              }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </ChartWrapper>
  );
};

SeasonalPatternChart.displayName = 'SeasonalPatternChart';
