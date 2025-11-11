# Epic 9: Enhanced Visualizations - Technical Contract

**Stories:** 9.1 - 9.6
**Developer:** Frontend Dev #5
**Date:** 2025-11-10

## Overview

This contract documents the implementation of advanced data visualization components, comparison tools, scenario modeling, and export functionality for the TreeBeard Energy Plan Recommendation system.

## Implemented Components

### Story 9.1: Chart Library Integration & Setup

#### Chart Infrastructure Components

**ChartWrapper** (`/src/frontend/src/components/charts/ChartWrapper.tsx`)
- Consistent container for all charts with title, subtitle, legend support
- Responsive sizing with ResizeObserver
- Loading skeleton states
- Error handling with fallback UI
- Accessibility: ARIA labels, role="figure"

**ChartTheme** (`/src/frontend/src/components/charts/ChartTheme.ts`)
- Colorblind-friendly color palette:
  - Primary: `#3B82F6` (Blue)
  - Secondary: `#10B981` (Green)
  - Tertiary: `#F59E0B` (Orange)
  - Seasonal colors: Winter (blue), Spring (green), Summer (yellow), Fall (orange)
- Typography settings: Font family, sizes, weights
- Spacing and margin configurations
- Tooltip, grid, axis, and legend styling
- Gradient definitions for area charts
- Helper functions: `getSeasonalColor()`, `getSeriesColor()`

**ChartTooltip** (`/src/frontend/src/components/charts/ChartTooltip.tsx`)
- Custom accessible tooltip component
- Configurable formatters for values and labels
- Color-coded data points
- ARIA live region for screen readers

### Story 9.2: Usage Visualization Components

**MonthlyUsageChart** (`/src/frontend/src/components/charts/MonthlyUsageChart.tsx`)
- Bar chart showing kWh usage per month (last 12 months)
- Color-coded by season
- Average usage reference line
- Outlier detection (±2 standard deviations) with pattern fill
- Responsive with mobile optimization
- Data: Array of `UsageData` objects

**SeasonalPatternChart** (`/src/frontend/src/components/charts/SeasonalPatternChart.tsx`)
- Multi-line chart with 4 seasonal lines
- Shows typical usage pattern by season over 12 months
- Highlights current season with thicker line
- Current month marker
- X-axis: 12 months, Y-axis: kWh

**DailyUsageChart** (`/src/frontend/src/components/charts/DailyUsageChart.tsx`)
- Area chart showing hourly usage distribution (if available)
- Peak hours highlighted (4pm-8pm) with reference lines
- Gradient fill
- Fallback message if no time-of-use data available
- X-axis: 24 hours, Y-axis: kWh

**UsageProfileBadge** (`/src/frontend/src/components/charts/UsageProfileBadge.tsx`)
- Visual badge showing user's profile type
- Profile types supported: baseline, seasonal, high_user, variable, low_user
- Color-coded icons and backgrounds
- Shows annual usage and confidence score
- Responsive inline-flex layout

### Story 9.3: Cost Projection Charts

**CostComparisonChart** (`/src/frontend/src/components/charts/CostComparisonChart.tsx`)
- Composed chart with current vs recommended plan costs
- 12-month projection with month-by-month breakdown
- Shaded area showing monthly savings
- Dual-line visualization
- Total savings displayed in subtitle
- Input: `RankedPlan`, `UsageData[]`, optional current plan cost

**CumulativeSavingsChart** (`/src/frontend/src/components/charts/CumulativeSavingsChart.tsx`)
- Area chart showing cumulative savings over 12 months
- Break-even point marker (if ETF exists)
- 6-month and 12-month milestone annotations
- Green gradient fill
- Reference line at $0 for break-even visualization

**CostBreakdownChart** (`/src/frontend/src/components/charts/CostBreakdownChart.tsx`)
- Pie/donut chart with monthly cost components
- Slices: Base energy cost (~75%), Fees (~5%), Taxes (~10%), Renewable premium (variable)
- Percentage labels on significant slices (>5%)
- Center label showing total monthly cost
- Legend with dollar amounts

**RateStructureChart** (`/src/frontend/src/components/charts/RateStructureChart.tsx`)
- Adaptive visualization based on plan type:
  - **Fixed rate**: Simple badge with rate
  - **Time-of-use**: Bar chart with off-peak, shoulder, peak periods
  - **Tiered**: Bar chart with usage tier breakpoints
  - **Variable**: Range indicator
- Color-coded by rate level (green=low, blue=medium, red=high)

### Story 9.4: Side-by-Side Plan Comparison

**ComparisonView** (`/src/frontend/src/components/comparison/ComparisonView.tsx`)
- Container for comparison interface
- Sticky header with plan names
- Remove plan functionality
- Back navigation
- Empty state handling
- Synchronized layout for 2-3 plans

**ComparisonTable** (`/src/frontend/src/components/comparison/ComparisonTable.tsx`)
- Row-by-row feature comparison
- Attributes: Annual cost, Monthly avg, Rate, Contract, Renewable %, ETF, Savings
- Best value highlighting (green background, checkmark icon)
- Worst value highlighting (red/yellow background, warning icon)
- Responsive table with horizontal scrolling

**ComparisonCharts** (`/src/frontend/src/components/comparison/ComparisonCharts.tsx`)
- **12-Month Cost Projection**: Multi-line chart with all plans
- **Renewable Energy Comparison**: Bar chart showing renewable percentages
- **Contract Length Comparison**: Bar chart with contract months
- **Risk Score Radar**: 5-dimension radar chart (cost, flexibility, supplier, rate, ETF risks)
- All charts use series colors from theme

**TradeOffAnalyzer** (`/src/frontend/src/components/comparison/TradeOffAnalyzer.tsx`)
- Compares two plans and identifies gains vs trade-offs
- Factors analyzed:
  - Cost differences
  - Contract flexibility
  - Renewable energy percentage
  - Early termination fees
  - Rate stability (fixed vs variable)
  - Monthly fees
- Two-column layout: Gains (green) vs Trade-Offs (orange)
- Summary recommendation at bottom

### Story 9.5: Scenario Modeling Tool

**ScenarioBuilder** (`/src/frontend/src/components/scenarios/ScenarioBuilder.tsx`)
- 4 adjustable sliders:
  - Usage adjustment: -50% to +50%
  - Cost priority: 0-100%
  - Renewable priority: 0-100%
  - Flexibility priority: 0-100%
- Actions: Save scenario, Share (URL generation), Reset
- Save modal with scenario naming
- Share URL copied to clipboard

**ScenarioResults** (`/src/frontend/src/components/scenarios/ScenarioResults.tsx`)
- Shows updated recommendations based on scenario parameters
- Highlights if top plan changed
- Side-by-side comparison: Original vs Scenario top plans
- Lists top 3 plans in scenario with costs

**ScenarioComparison** (`/src/frontend/src/components/scenarios/ScenarioComparison.tsx`)
- Table of saved scenarios
- Columns: Name, Usage Adj., Cost Priority, Created Date, Actions
- Load and Delete actions
- localStorage persistence

**WhatIfCalculator** (`/src/frontend/src/components/scenarios/WhatIfCalculator.tsx`)
- Quick calculator for simple scenarios
- Inputs: Usage increase %, Rate increase %
- Shows impact on both current and recommended plans
- Real-time calculation and savings projection

### Story 9.6: Export Functionality

**PdfExport** (`/src/frontend/src/components/export/PdfExport.tsx`)
- Uses jsPDF library
- PDF contents:
  - Cover page with TreeBeard branding (primary blue header)
  - Generated date
  - Executive summary (top recommendation, savings)
  - User energy profile
  - Top 3 plans with full details and explanations
  - Footer with page numbers and branding
- Automatic page breaks
- Filename: `treebeard-recommendation-{date}.pdf`

**CsvExportUsage** (`/src/frontend/src/components/export/CsvExportUsage.tsx`)
- Uses papaparse library
- CSV columns: Month, Year, kWh, Estimated Cost, Season, Profile Type
- Estimates cost at ~12¢/kWh average
- Filename: `treebeard-usage-{userId}-{date}.csv`

**CsvExportComparison** (`/src/frontend/src/components/export/CsvExportComparison.tsx`)
- CSV with plan attributes as rows, plans as columns
- Rows: Plan Name, Supplier, Annual Cost, Monthly Cost, Rate, Contract, Renewable %, ETF, Savings, Plan Type
- Filename: `treebeard-comparison-{date}.csv`

**print.css** (`/src/frontend/src/styles/print.css`)
- Print media query stylesheet
- Hides: buttons, navigation, sticky elements (`.no-print` class)
- Page setup: 1cm margins, auto size
- Optimizes for black and white printing
- Shows chart placeholders with aria-labels
- Page break controls: `.page-break-before`, `.page-break-after`
- Footer with page numbers

### Custom Hooks

**useChartData** (`/src/frontend/src/hooks/useChartData.ts`)
- Transforms `UsageData[]` into chart-ready format
- Returns: `monthlyData`, `totalUsage`, `averageUsage`, `peakMonth`, `lowMonth`
- Optionally calculates costs if plan provided
- Memoized for performance

**useScenario** (`/src/frontend/src/hooks/useScenario.ts`)
- State management for scenario modeling
- Manages: `currentScenario`, `savedScenarios`
- Operations: `updateScenario`, `resetScenario`, `saveScenario`, `loadScenario`, `deleteScenario`
- URL sharing: `getShareUrl`, `loadFromUrl`
- localStorage persistence (key: `treebeard_scenarios`)

**useComparison** (`/src/frontend/src/hooks/useComparison.ts`)
- State management for plan comparison (max 3 plans)
- Operations: `addPlan`, `removePlan`, `clearAll`, `isPlanSelected`
- Returns: `selectedPlans`, `canAddMore`, `maxPlans`
- Validation: prevents duplicates, enforces max plans

### New Pages

**ComparisonPage** (`/src/frontend/src/pages/ComparisonPage.tsx`)
- Full-page comparison interface
- Uses `ComparisonView`, `ComparisonTable`, `ComparisonCharts`, `TradeOffAnalyzer`
- CSV export button
- Multiple trade-off comparisons for 3 plans
- Print-friendly with page breaks
- Route: `/comparison` (requires state with `selectedPlans`)

**ScenarioPage** (`/src/frontend/src/pages/ScenarioPage.tsx`)
- Scenario modeling interface
- Layout: ScenarioBuilder + ScenarioResults (side-by-side on desktop)
- WhatIfCalculator below
- SavedScenarios comparison table
- Back to Results navigation
- Route: `/scenarios` (requires state with `recommendation`)

**ResultsPageEnhanced** (`/src/frontend/src/pages/ResultsPageEnhanced.tsx`)
- Enhanced version of original ResultsPage
- New features:
  - Action buttons: PDF export, CSV export, Compare, Scenarios
  - UsageProfileBadge integration
  - Usage charts: MonthlyUsageChart, SeasonalPatternChart
  - CostComparisonChart for selected plan
  - Plan selection checkboxes (max 3 for comparison)
  - Comparison button appears when 2+ plans selected
- Maintains existing: Feedback widget, CostBreakdown, warnings, CTA

## Data Flow

### Chart Data Format

```typescript
// Usage Data
interface UsageData {
  month: string;  // ISO date (YYYY-MM-DD)
  kwh: number;
}

// Monthly Data Point (transformed)
interface MonthlyDataPoint {
  month: string;
  monthLabel: string;  // "Jan '24"
  kwh: number;
  cost?: number;       // Calculated if plan provided
}
```

### Scenario Parameters

```typescript
interface ScenarioParams {
  usageAdjustment: number;     // -50 to 50
  costPriority: number;        // 0-100
  renewablePriority: number;   // 0-100
  flexibilityPriority: number; // 0-100
}

interface SavedScenario {
  id: string;
  name: string;
  params: ScenarioParams;
  createdAt: string;
}
```

### Comparison State

```typescript
interface UseComparisonReturn {
  selectedPlans: RankedPlan[];
  addPlan: (plan: RankedPlan) => boolean;
  removePlan: (planId: string) => void;
  clearAll: () => void;
  isPlanSelected: (planId: string) => boolean;
  canAddMore: boolean;
  maxPlans: number;  // 3
}
```

## Performance Optimizations

1. **Lazy Loading**: All chart components can be lazy loaded with React.lazy()
2. **Memoization**: useChartData hook uses useMemo for expensive calculations
3. **Debouncing**: Scenario updates should be debounced (500ms recommended)
4. **ResizeObserver**: Charts auto-resize efficiently without window listeners
5. **Virtualization**: Not currently implemented but recommended for large scenario lists

## Accessibility Features

- All charts have ARIA labels describing content
- Keyboard navigation supported for interactive elements
- Screen reader announcements via aria-live regions
- High contrast colorblind-friendly palette
- Semantic HTML: proper headings, labels, roles
- Focus management in modals and expandable sections
- Minimum touch target size: 44x44px

## Responsive Design

### Breakpoints
- Mobile (< 640px): Single column, reduced chart height (200px)
- Tablet (640px - 1024px): Two columns for charts
- Desktop (> 1024px): Three columns for plan cards, full-size charts (300px)

### Mobile Optimizations
- Stacked chart layout
- Reduced chart heights
- Simplified tooltips
- Horizontal scrolling for comparison table
- Collapsed navigation

### Print Layout
- Hides interactive elements
- Black and white optimization
- Page break controls
- Chart placeholders with descriptions
- Page numbers in footer

## Error Handling

All chart components include:
- Loading states with skeleton UI
- Error states with user-friendly messages
- Empty state handling ("No data available")
- Fallback UI for unsupported browsers
- Try-catch around localStorage operations

## Browser Compatibility

- Modern browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Recharts compatibility: IE11 not supported
- jsPDF: All modern browsers
- papaparse: All browsers with ES5 support
- ResizeObserver: Polyfill may be needed for older browsers

## Dependencies

```json
{
  "recharts": "^2.10.3",
  "jspdf": "^2.5.2",
  "papaparse": "^5.4.1",
  "@types/papaparse": "^5.3.14"
}
```

## Testing Recommendations

### Unit Tests
- Test chart data transformations (useChartData hook)
- Test scenario state management (useScenario hook)
- Test comparison state management (useComparison hook)
- Test export file generation

### Integration Tests
- Test chart rendering with sample data
- Test comparison workflow (select → compare → export)
- Test scenario workflow (adjust → save → load)
- Test responsive behavior at different breakpoints

### Accessibility Tests
- Keyboard navigation through all interactive elements
- Screen reader compatibility (NVDA, JAWS, VoiceOver)
- Color contrast ratios (WCAG AA compliance)
- Focus management

### Visual Regression Tests
- Chart appearance across browsers
- Print layout rendering
- PDF export output

## Usage Examples

### Basic Chart Usage

```tsx
import { MonthlyUsageChart } from '@/components/charts';

<MonthlyUsageChart
  usageData={usageData}
  isLoading={false}
  height={300}
/>
```

### Comparison Workflow

```tsx
import { useComparison } from '@/hooks/useComparison';

const { selectedPlans, addPlan, isPlanSelected } = useComparison(3);

// In plan card
<input
  type="checkbox"
  checked={isPlanSelected(plan.plan_id)}
  onChange={(e) => e.target.checked ? addPlan(plan) : removePlan(plan.plan_id)}
/>

// Navigate to comparison
<Button onClick={() => navigate('/comparison', { state: { selectedPlans } })}>
  Compare Plans
</Button>
```

### Scenario Modeling

```tsx
import { useScenario } from '@/hooks/useScenario';

const {
  currentScenario,
  updateScenario,
  saveScenario,
  getShareUrl
} = useScenario();

<input
  type="range"
  value={currentScenario.usageAdjustment}
  onChange={(e) => updateScenario({ usageAdjustment: Number(e.target.value) })}
/>
```

### Export PDF

```tsx
import { PdfExport } from '@/components/export';

<PdfExport
  recommendation={recommendation}
  onExport={() => console.log('PDF exported')}
/>
```

## Future Enhancements

1. **Interactive Charts**: Click to drill down, zoom, pan
2. **Animated Transitions**: Smooth data updates
3. **Chart Annotations**: User notes on charts
4. **Custom Date Ranges**: User-selected time periods
5. **Chart Templates**: Save custom chart configurations
6. **Dashboard**: Customizable chart dashboard
7. **Real-time Data**: Live usage updates
8. **Mobile App**: Native mobile chart components
9. **Advanced Analytics**: ML-powered insights
10. **Social Sharing**: Share charts to social media

## Known Limitations

1. Charts don't render in email clients (use PDF export instead)
2. Large datasets (>500 points) may cause performance issues
3. Print layout doesn't capture interactive chart states
4. PDF export doesn't include actual chart images (text-based)
5. CSV export doesn't preserve formatting
6. Scenario URL sharing limited to query parameter size (~2000 chars)
7. localStorage limited to ~5MB (may affect many saved scenarios)

## File Inventory

### Components (25 files)
- `/src/frontend/src/components/charts/` (11 files)
- `/src/frontend/src/components/comparison/` (4 files)
- `/src/frontend/src/components/scenarios/` (4 files)
- `/src/frontend/src/components/export/` (3 files)
- Index files (4 files)

### Hooks (3 files)
- `/src/frontend/src/hooks/useChartData.ts`
- `/src/frontend/src/hooks/useScenario.ts`
- `/src/frontend/src/hooks/useComparison.ts`

### Pages (2 files)
- `/src/frontend/src/pages/ComparisonPage.tsx`
- `/src/frontend/src/pages/ScenarioPage.tsx`
- `/src/frontend/src/pages/ResultsPageEnhanced.tsx` (enhanced version)

### Styles (1 file)
- `/src/frontend/src/styles/print.css`

### Documentation (1 file)
- `/docs/contracts/story-9.1-9.6-contract.md` (this file)

**Total: 32 implementation files + 1 documentation file**

## Success Metrics

All acceptance criteria met:
- ✅ 11 chart types implemented
- ✅ All charts responsive and accessible
- ✅ Colorblind-friendly palette applied
- ✅ Side-by-side comparison for 2-3 plans
- ✅ Scenario modeling with adjustable parameters
- ✅ PDF export with professional layout
- ✅ CSV export for usage and comparison data
- ✅ Print stylesheet implemented
- ✅ 3 custom hooks created
- ✅ 2 new pages created
- ✅ Existing components enhanced

---

**Contract Status:** COMPLETE
**Reviewed By:** Frontend Dev #5
**Date:** 2025-11-10
