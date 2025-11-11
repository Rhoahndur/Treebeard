# TreeBeard Frontend - Epic 4 Implementation

## Overview

This is the frontend implementation for the TreeBeard Energy Plan Recommendation Agent, built as part of **Epic 4: Frontend Results Display (Stories 4.1-4.6)**.

The application displays energy plan recommendations with AI-generated explanations, cost breakdowns, and interactive visualizations.

## Tech Stack

- **React 18.3** - UI framework
- **TypeScript 5.3** - Type safety
- **Tailwind CSS 3.4** - Styling
- **Vite 5.0** - Build tool
- **Recharts 2.10** - Charts and visualizations
- **Axios 1.6** - HTTP client
- **Vitest** - Testing framework
- **Storybook 7.6** - Component development
- **React Router 6.21** - Routing

## Project Structure

```
src/frontend/
├── src/
│   ├── components/
│   │   ├── design-system/     # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   └── index.ts
│   │   ├── PlanCard/          # Plan recommendation card
│   │   │   ├── PlanCard.tsx
│   │   │   └── PlanCard.stories.tsx
│   │   ├── CostBreakdown/     # Cost analysis component
│   │   │   └── CostBreakdown.tsx
│   │   └── ResultsPage/
│   ├── pages/
│   │   └── ResultsPage.tsx    # Main results display page
│   ├── api/
│   │   ├── client.ts          # Axios API client
│   │   └── recommendations.ts # Recommendations API
│   ├── types/
│   │   └── recommendation.ts  # TypeScript types
│   ├── utils/
│   │   └── formatters.ts      # Utility functions
│   ├── styles/
│   │   └── index.css          # Global styles
│   ├── test/
│   │   └── setup.ts           # Test configuration
│   ├── App.tsx                # Root component
│   └── main.tsx               # Entry point
├── .storybook/                # Storybook config
├── index.html                 # HTML template
├── package.json               # Dependencies
├── vite.config.ts             # Vite configuration
├── tailwind.config.js         # Tailwind configuration
└── tsconfig.json              # TypeScript configuration
```

## Features Implemented

### Story 4.1: Design System & Component Library

- **Button**: Primary, secondary, outline, ghost variants with loading states
- **Card**: Flexible container with header, content, footer
- **Badge**: Status indicators with semantic colors
- **Input**: Form input with label, error, and helper text
- **Skeleton**: Loading placeholders
- **Responsive design foundation** with Tailwind CSS
- **Accessibility-first** approach with ARIA labels and keyboard navigation

### Story 4.2: Plan Card Component

- Displays plan details (name, supplier, rate, contract)
- Color-coded savings badges (high/medium/low)
- Renewable energy percentage indicator
- Expandable "Why this plan?" section with AI explanation
- Key differentiators and trade-offs
- Hover effects and interactions
- Mobile responsive (320px+)
- Full keyboard navigation
- WCAG AA compliant

### Story 4.3: Results Page Layout

- Header with total potential savings summary
- User profile summary (usage patterns, confidence score)
- Top 3 plan cards displayed
- Warning messages for important notices
- Empty state (no matches found)
- Error state handling
- Loading skeleton with animation
- Responsive grid layout

### Story 4.4: Cost Breakdown Component

- Annual cost vs. savings display
- 12-month cost projection chart (Recharts)
- Cost breakdown table (energy charges, fees, total)
- Break-even analysis
- Collapsible details section
- Tooltip explanations
- Accessible chart alternatives

### Story 4.5: Mobile Responsiveness

- Fully responsive from 320px to 4K displays
- Touch-friendly interactions (44px+ tap targets)
- Card stacking on mobile devices
- Collapsible sections for better mobile UX
- Tested responsive grid (1/2/3 columns)
- Font sizing scales appropriately

### Story 4.6: Accessibility Implementation

- ARIA labels for all interactive elements
- Full keyboard navigation support
- Focus indicators on all focusable elements
- Screen reader tested (semantic HTML)
- Color contrast WCAG AA (4.5:1 minimum)
- Alt text for icons (aria-hidden for decorative)
- Semantic HTML5 elements
- Focus trap in modals/dialogs

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd src/frontend
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Storybook

Run Storybook for component development:

```bash
npm run storybook
```

Storybook will be available at `http://localhost:6006`

### Testing

Run tests:

```bash
npm test
```

Run tests with UI:

```bash
npm run test:ui
```

Generate coverage report:

```bash
npm run test:coverage
```

### Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## API Integration

The frontend integrates with the backend API at `/api/v1/recommendations/generate`.

### Environment Variables

Create a `.env` file:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### API Client

The API client (`src/api/client.ts`) handles:
- Authentication with JWT tokens
- Request/response interceptors
- Error handling
- Token management

### Usage Example

```typescript
import recommendationsApi from '@/api/recommendations';

const recommendation = await recommendationsApi.generate({
  user_data: {
    zip_code: '78701',
    property_type: 'residential',
  },
  usage_data: [...],
  preferences: {
    cost_priority: 40,
    flexibility_priority: 30,
    renewable_priority: 20,
    rating_priority: 10,
  },
});
```

## Design System

### Color Palette

- **Primary**: Green (#22c55e) - Main brand color
- **Success**: Green (#10b981) - Positive actions/savings
- **Warning**: Amber (#f59e0b) - Cautions/warnings
- **Danger**: Red (#ef4444) - Errors/negative
- **Info**: Blue (#3b82f6) - Informational
- **Renewable**: Emerald (#10b981) - Renewable energy

### Typography

- **Font Family**: Inter (body), Lexend (headings)
- **Sizes**: xs (12px) to 4xl (36px)
- **Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Spacing

Tailwind's default spacing scale (4px base) with custom additions:
- 18 (4.5rem), 88 (22rem), 112 (28rem), 128 (32rem)

### Breakpoints

- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

## Accessibility

### WCAG AA Compliance

All components meet WCAG 2.1 AA standards:

- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Focus Indicators**: Visible focus rings on all focusable elements
- **Screen Readers**: Semantic HTML and ARIA labels
- **Touch Targets**: Minimum 44x44px for touch targets

### Testing

Accessibility tested with:
- Storybook a11y addon
- Keyboard navigation testing
- Screen reader testing (VoiceOver)
- Color contrast checker

## Performance

### Optimization Strategies

- **Code Splitting**: React.lazy for route-based splitting
- **Tree Shaking**: Vite automatically removes unused code
- **Image Optimization**: Responsive images with srcset
- **Caching**: API responses cached in localStorage
- **Lazy Loading**: Charts loaded on-demand

### Performance Targets

- First Contentful Paint (FCP): < 1.5s
- Time to Interactive (TTI): < 3.5s
- Lighthouse Score: > 90

## Testing Strategy

### Unit Tests

- Component behavior testing
- Utility function testing
- 70%+ code coverage target

### Integration Tests

- User flow testing
- API integration testing
- Error handling testing

### E2E Tests (Future)

- Critical user journeys
- Cross-browser testing

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Deployment

### Build

```bash
npm run build
```

Output: `dist/` directory

### Deploy to Vercel/Netlify

```bash
# Vercel
vercel --prod

# Netlify
netlify deploy --prod
```

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Known Issues & Future Enhancements

### Current Limitations

- Mock data used for monthly breakdown charts
- No authentication flow implemented yet
- Limited error recovery options

### Planned Enhancements (v2.0)

- Real-time plan comparisons
- Saved plan favorites
- Share recommendations
- Print-friendly view
- Dark mode support
- Offline support (PWA)

## Contributing

### Code Style

- Use TypeScript for type safety
- Follow ESLint rules
- Use Prettier for formatting
- Write tests for new components
- Document complex logic

### Component Guidelines

1. Use functional components with hooks
2. Implement accessibility from the start
3. Create Storybook stories for all components
4. Write unit tests with >70% coverage
5. Follow the design system

## Support

For issues or questions:
- GitHub Issues: [Link to repo]
- Documentation: `/docs`
- API Contract: `/docs/contracts/epic-3-api-contract.md`

## License

[Your License]

---

**Built with by Frontend Dev #1 for TreeBeard Project**
**Epic 4 - Frontend Results Display - Stories 4.1-4.6**
