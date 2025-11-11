# TreeBeard Frontend - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd /Users/aleksandrgaun/Downloads/TreeBeard/src/frontend

# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Storybook (Component Development)

```bash
# Start Storybook
npm run storybook
```

Open [http://localhost:6006](http://localhost:6006) to view component library.

### Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 📁 Project Structure

```
src/
├── components/          # React components
│   ├── design-system/  # Reusable UI components
│   ├── PlanCard/       # Plan recommendation card
│   └── CostBreakdown/  # Cost analysis component
├── pages/              # Page components
├── api/                # API client
├── types/              # TypeScript types
├── utils/              # Utility functions
└── styles/             # Global styles
```

---

## 🎨 Design System

### Components Available

- **Button** - 4 variants, 3 sizes, loading states
- **Card** - Flexible container with header, content, footer
- **Badge** - Status indicators
- **Input** - Form input with validation
- **Skeleton** - Loading placeholders

### Usage Example

```tsx
import { Button, Card, Badge } from '@/components/design-system';

function MyComponent() {
  return (
    <Card>
      <h2>Hello World</h2>
      <Badge variant="success">Active</Badge>
      <Button variant="primary">Click Me</Button>
    </Card>
  );
}
```

---

## 🔌 API Integration

### Setup Environment

Create `.env` file:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Usage Example

```tsx
import recommendationsApi from '@/api/recommendations';

const fetchRecommendations = async () => {
  const data = await recommendationsApi.generate({
    user_data: {
      zip_code: '78701',
      property_type: 'residential',
    },
    usage_data: [
      { month: '2024-01-01', kwh: 850 },
      // ... more months
    ],
    preferences: {
      cost_priority: 40,
      flexibility_priority: 30,
      renewable_priority: 20,
      rating_priority: 10,
    },
  });
  
  return data;
};
```

---

## 🧪 Testing Components

### Unit Test Example

```tsx
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

test('renders button', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button')).toBeInTheDocument();
});
```

---

## 📱 Responsive Design

All components are responsive:

- **Mobile**: 320px - 640px (1 column)
- **Tablet**: 640px - 1024px (2 columns)
- **Desktop**: 1024px+ (3 columns)

---

## ♿ Accessibility

All components are WCAG AA compliant:

- Keyboard navigation
- Screen reader support
- Color contrast >4.5:1
- ARIA labels
- Focus indicators

---

## 🎯 Key Features

### Plan Card Component

Display energy plan recommendations with:
- Savings badges
- Renewable energy indicators
- AI-generated explanations
- Key differentiators and trade-offs

### Cost Breakdown Component

Visualize costs with:
- 12-month cost projection chart
- Detailed breakdown table
- Break-even analysis
- Collapsible sections

### Results Page

Complete results display with:
- Top 3 plan recommendations
- User profile summary
- Loading states
- Error handling
- Empty states

---

## 🛠️ Development Tips

### Hot Reload

Vite provides instant hot module replacement (HMR). Changes appear immediately in the browser.

### TypeScript

All components are fully typed. Use the TypeScript Language Server in your editor for autocomplete and type checking.

### Linting

```bash
npm run lint
```

### Code Formatting

```bash
npm run format  # (if configured)
```

---

## 📦 Build & Deploy

### Production Build

```bash
npm run build
```

Output in `dist/` directory.

### Deploy to Vercel

```bash
npm install -g vercel
vercel --prod
```

### Deploy to Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- --port 3001
```

### Dependencies Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors

```bash
# Clear Vite cache
rm -rf .vite

# Rebuild
npm run build
```

---

## 📚 Additional Resources

- [Full Documentation](./FRONTEND-README.md)
- [API Contract](../../docs/contracts/epic-3-api-contract.md)
- [Component Stories](http://localhost:6006)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Docs](https://react.dev)

---

## 🤝 Need Help?

- Check the [README](./FRONTEND-README.md) for detailed documentation
- Review component stories in Storybook
- Check the API contract for backend integration
- Review the test files for usage examples

---

**Happy Coding! 🎉**
