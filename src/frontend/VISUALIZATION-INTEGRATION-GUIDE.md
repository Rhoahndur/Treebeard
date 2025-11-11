# Visualization Components Integration Guide

Quick start guide for integrating the new visualization components into TreeBeard.

## Quick Start

### 1. Install Dependencies (Already Done)

```bash
npm install jspdf papaparse
npm install --save-dev @types/papaparse
```

### 2. Add Routes to Router

```tsx
// In your router configuration (App.tsx or Routes.tsx)
import { ComparisonPage } from './pages/ComparisonPage';
import { ScenarioPage } from './pages/ScenarioPage';

<Routes>
  {/* Existing routes */}
  <Route path="/comparison" element={<ComparisonPage />} />
  <Route path="/scenarios" element={<ScenarioPage />} />
</Routes>
```

### 3. Add Print Stylesheet

```html
<!-- In public/index.html -->
<link rel="stylesheet" href="/src/styles/print.css" media="print" />
```

Or import in your main CSS/App:

```tsx
// In App.tsx
import './styles/print.css';
```

## Using Individual Components

### Chart Components

```tsx
import {
  MonthlyUsageChart,
  SeasonalPatternChart,
  CostComparisonChart,
  UsageProfileBadge
} from '@/components/charts';

// In your component
<MonthlyUsageChart usageData={usageData} height={300} />
<SeasonalPatternChart usageData={usageData} />
<CostComparisonChart recommendedPlan={plan} usageData={usageData} />
<UsageProfileBadge profile={userProfile} />
```

### Export Components

```tsx
import { PdfExport, CsvExportUsage } from '@/components/export';

<PdfExport recommendation={recommendation} />
<CsvExportUsage usageData={usageData} profile={userProfile} />
```

### Comparison Hook

```tsx
import { useComparison } from '@/hooks/useComparison';

const MyComponent = () => {
  const { selectedPlans, addPlan, removePlan, isPlanSelected } = useComparison(3);

  return (
    <>
      {/* Plan selection */}
      <input
        type="checkbox"
        checked={isPlanSelected(plan.plan_id)}
        onChange={(e) => e.target.checked ? addPlan(plan) : removePlan(plan.plan_id)}
      />

      {/* Compare button */}
      {selectedPlans.length >= 2 && (
        <button onClick={() => navigate('/comparison', { state: { selectedPlans } })}>
          Compare Plans
        </button>
      )}
    </>
  );
};
```

### Scenario Hook

```tsx
import { useScenario } from '@/hooks/useScenario';

const MyComponent = () => {
  const {
    currentScenario,
    updateScenario,
    saveScenario,
    getShareUrl
  } = useScenario();

  return (
    <input
      type="range"
      value={currentScenario.usageAdjustment}
      onChange={(e) => updateScenario({ usageAdjustment: Number(e.target.value) })}
    />
  );
};
```

## Replacing ResultsPage

Option 1: Direct replacement

```tsx
// Rename current ResultsPage.tsx to ResultsPageOld.tsx
// Rename ResultsPageEnhanced.tsx to ResultsPage.tsx
```

Option 2: Gradual migration

```tsx
// Use both and feature flag
import { ResultsPage } from './pages/ResultsPage';
import { ResultsPageEnhanced } from './pages/ResultsPageEnhanced';

const Results = USE_NEW_VISUALIZATIONS ? ResultsPageEnhanced : ResultsPage;
```

## Component Props Reference

### MonthlyUsageChart

```tsx
interface MonthlyUsageChartProps {
  usageData: UsageData[];      // Required
  isLoading?: boolean;         // Optional
  error?: string | null;       // Optional
  height?: number;             // Optional, default 300
}
```

### CostComparisonChart

```tsx
interface CostComparisonChartProps {
  recommendedPlan: RankedPlan; // Required
  currentPlanCost?: number;    // Optional
  usageData: UsageData[];      // Required
  isLoading?: boolean;
  error?: string | null;
  height?: number;
}
```

### PdfExport

```tsx
interface PdfExportProps {
  recommendation: GenerateRecommendationResponse; // Required
  onExport?: () => void;                          // Optional callback
}
```

### useComparison

```tsx
const {
  selectedPlans,    // RankedPlan[]
  addPlan,          // (plan: RankedPlan) => boolean
  removePlan,       // (planId: string) => void
  clearAll,         // () => void
  isPlanSelected,   // (planId: string) => boolean
  canAddMore,       // boolean
  maxPlans,         // number (3)
} = useComparison(maxPlans?: number);
```

## Styling Classes

### Print-specific classes

```tsx
<div className="no-print">This won't print</div>
<div className="page-break-before">Start new page here</div>
<div className="page-break-after">Page break after this</div>
```

### Chart wrapper classes

```tsx
<ChartWrapper
  title="My Chart"
  subtitle="Description"
  className="custom-class"
/>
```

## Common Patterns

### Full Results Page with Visualizations

```tsx
import { MonthlyUsageChart, SeasonalPatternChart, UsageProfileBadge } from '@/components/charts';
import { PdfExport, CsvExportUsage } from '@/components/export';
import { useComparison } from '@/hooks/useComparison';

const ResultsPage = ({ recommendation, usageData }) => {
  const { selectedPlans, addPlan } = useComparison(3);

  return (
    <div>
      {/* Export buttons */}
      <PdfExport recommendation={recommendation} />
      <CsvExportUsage usageData={usageData} profile={recommendation.user_profile} />

      {/* Profile badge */}
      <UsageProfileBadge profile={recommendation.user_profile} />

      {/* Charts */}
      <MonthlyUsageChart usageData={usageData} />
      <SeasonalPatternChart usageData={usageData} />

      {/* Plan cards with comparison checkboxes */}
      {/* ... */}
    </div>
  );
};
```

### Comparison Flow

```tsx
// 1. Results page - select plans
const { selectedPlans, addPlan } = useComparison(3);

// 2. Navigate to comparison
navigate('/comparison', { state: { selectedPlans } });

// 3. ComparisonPage receives plans and displays
// Already implemented in ComparisonPage.tsx
```

### Scenario Flow

```tsx
// 1. Click "Explore Scenarios" button
navigate('/scenarios', { state: { recommendation } });

// 2. ScenarioPage receives recommendation
// Already implemented in ScenarioPage.tsx
```

## Accessibility Checklist

- [ ] All charts have descriptive ARIA labels
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus indicators visible
- [ ] Screen reader announcements working
- [ ] Color contrast ratios meet WCAG AA
- [ ] Touch targets at least 44x44px

## Performance Tips

1. **Lazy load charts** for faster initial page load:

```tsx
const MonthlyUsageChart = React.lazy(() => import('@/components/charts/MonthlyUsageChart'));

<Suspense fallback={<Skeleton />}>
  <MonthlyUsageChart usageData={usageData} />
</Suspense>
```

2. **Debounce scenario updates** to avoid excessive re-renders:

```tsx
import { debounce } from 'lodash';

const debouncedUpdate = debounce(updateScenario, 500);
```

3. **Memoize chart data** when parent re-renders:

```tsx
const chartData = useMemo(() => transformData(usageData), [usageData]);
```

## Troubleshooting

### Charts not rendering

1. Check that `usageData` is an array with correct structure
2. Verify Recharts is installed: `npm list recharts`
3. Check browser console for errors

### PDF export not working

1. Check jsPDF is installed: `npm list jspdf`
2. Verify recommendation data is complete
3. Check browser console for errors

### Comparison not working

1. Verify react-router-dom is configured
2. Check that state is passed correctly: `{ state: { selectedPlans } }`
3. Ensure plans have valid `plan_id` fields

### Print layout broken

1. Verify print.css is loaded
2. Check media query: `@media print`
3. Test with print preview in browser

## Support

- **Documentation:** `/docs/contracts/story-9.1-9.6-contract.md`
- **Summary:** `/EPIC-9-SUMMARY.md`
- **Developer:** Frontend Dev #5

## Component Locations

```
/src/frontend/src/
├── components/
│   ├── charts/          - All chart components
│   ├── comparison/      - Comparison UI components
│   ├── scenarios/       - Scenario modeling components
│   └── export/          - Export functionality
├── hooks/
│   ├── useChartData.ts
│   ├── useComparison.ts
│   └── useScenario.ts
├── pages/
│   ├── ComparisonPage.tsx
│   ├── ScenarioPage.tsx
│   └── ResultsPageEnhanced.tsx
└── styles/
    └── print.css
```

## Quick Reference - Available Components

### Charts
- `ChartWrapper`, `ChartTooltip`, `chartColors`
- `MonthlyUsageChart`, `SeasonalPatternChart`, `DailyUsageChart`
- `UsageProfileBadge`
- `CostComparisonChart`, `CumulativeSavingsChart`
- `CostBreakdownChart`, `RateStructureChart`

### Comparison
- `ComparisonView`, `ComparisonTable`
- `ComparisonCharts`, `TradeOffAnalyzer`

### Scenarios
- `ScenarioBuilder`, `ScenarioResults`
- `ScenarioComparison`, `WhatIfCalculator`

### Export
- `PdfExport`, `CsvExportUsage`, `CsvExportComparison`

### Hooks
- `useChartData`, `useComparison`, `useScenario`

Happy coding!
