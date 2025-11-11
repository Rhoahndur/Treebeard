# TreeBeard Frontend - Onboarding Flow (Epic 5)

**Developer:** Frontend Dev #2
**Epic:** 5 - Frontend Onboarding Flow
**Status:** Complete
**Date:** November 10, 2025

---

## Overview

This document describes the implementation of Epic 5: Frontend Onboarding Flow for the TreeBeard AI Energy Plan Recommendation Agent. The onboarding flow is a 4-step form that collects user data and submits it to the recommendation engine.

---

## Features Implemented

### Story 5.1: Multi-Step Form Framework
- 4-step form structure with client-side routing
- Progress indicator showing 1/4, 2/4, 3/4, 4/4
- Next/Back navigation with state management
- React Hook Form for form management
- Zod for validation
- State persists across steps via localStorage

**Components:**
- `/components/ProgressIndicator/ProgressIndicator.tsx`
- `/pages/OnboardingPage.tsx`

### Story 5.2: User Info & Current Plan Forms

**Step 1: User Information**
- Email with format validation
- ZIP code with format validation (5 or 9 digits)
- Property type selection (residential/commercial)
- Inline validation and error messages
- Required field indicators

**Step 2: Current Plan Details**
- Current supplier name
- Current rate (cents/kWh)
- Contract end date
- Early termination fee
- Monthly base fee
- Tooltips for help text
- Input validation

**Components:**
- `/components/OnboardingFlow/Step1UserInfo.tsx`
- `/components/OnboardingFlow/Step2CurrentPlan.tsx`

### Story 5.3: File Upload Component

**Step 3: Usage Data**
- Drag-and-drop upload zone
- File browser fallback
- CSV parsing with Papa Parse
- File validation (type, size, format)
- Upload progress indicator
- Manual entry option (12-month inputs as fallback)
- Data preview table (first 5 rows)
- Download example CSV template

**Expected CSV Format:**
```csv
month,kwh
2024-01,850
2024-02,820
```

**Components:**
- `/components/FileUpload/FileUpload.tsx`
- `/components/OnboardingFlow/Step3UsageData.tsx`
- `/utils/csvParser.ts`

### Story 5.4: Preference Selection UI

**Step 4: Priorities**
- 4 preference sliders:
  - Cost Savings (minimize bill)
  - Contract Flexibility (short-term options)
  - Renewable Energy (clean sources)
  - Supplier Rating (reviews and reliability)
- Auto-adjust to sum to 100%
- Preset profile buttons:
  - Budget Focus (60% cost)
  - Eco-Conscious (60% renewable)
  - Flexible (60% flexibility)
  - Balanced (25% each)
- Visual feedback showing priority distribution
- Real-time validation

**Components:**
- `/components/PreferenceSliders/PreferenceSliders.tsx`
- `/components/OnboardingFlow/Step4Preferences.tsx`
- `/utils/presets.ts`

### Story 5.5: Auto-Save & Restore

- Auto-save to localStorage on field change (debounced 500ms)
- Restore prompt on page reload
- "Saved" indicator in UI
- Clear data on successful submission
- Data expires after 7 days automatically

**Components:**
- `/hooks/useAutoSave.ts`
- `/utils/localStorage.ts`

### Story 5.6: Form Submission & Loading States

- Submit to POST /api/v1/recommendations/generate
- Loading screen with animated spinner
- Progress messages:
  - "Analyzing your usage patterns..."
  - "Finding available plans in your area..."
  - "Calculating potential savings..."
  - "Generating AI-powered explanations..."
  - "Finalizing your recommendations..."
- Success handling with redirect to results page
- Error handling with retry button
- Comprehensive error messages

**Components:**
- `/components/LoadingScreen/LoadingScreen.tsx`
- `/api/client.ts`

---

## Tech Stack

- **React 18.3+** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Hook Form** - Form management
- **Zod** - Validation schemas
- **Papa Parse** - CSV parsing
- **React Router** - Client-side routing
- **Axios** - API calls
- **Vitest** - Unit testing
- **Testing Library** - Component testing

---

## Project Structure

```
src/frontend/src/
├── api/
│   └── client.ts                 # Axios API client
├── components/
│   ├── FileUpload/
│   │   └── FileUpload.tsx        # CSV upload component
│   ├── LoadingScreen/
│   │   └── LoadingScreen.tsx     # Loading UI
│   ├── OnboardingFlow/
│   │   ├── Step1UserInfo.tsx     # User info form
│   │   ├── Step2CurrentPlan.tsx  # Current plan form
│   │   ├── Step3UsageData.tsx    # Usage data upload
│   │   └── Step4Preferences.tsx  # Preference selection
│   ├── PreferenceSliders/
│   │   └── PreferenceSliders.tsx # Preference UI
│   └── ProgressIndicator/
│       └── ProgressIndicator.tsx # Progress bar
├── hooks/
│   └── useAutoSave.ts            # Auto-save hook
├── pages/
│   └── OnboardingPage.tsx        # Main onboarding page
├── types/
│   ├── api.ts                    # API type definitions
│   └── onboarding.ts             # Onboarding types
├── utils/
│   ├── csvParser.ts              # CSV parsing utilities
│   ├── localStorage.ts           # LocalStorage utilities
│   ├── presets.ts                # Preference presets
│   ├── validation.ts             # Zod schemas
│   └── __tests__/               # Unit tests
├── App.tsx                       # App router
├── main.tsx                      # Entry point
└── index.css                     # Global styles
```

---

## Form State Shape

```typescript
interface OnboardingData {
  user: {
    email: string;
    zip_code: string;
    property_type: 'residential' | 'commercial';
  };
  current_plan: {
    supplier_name: string;
    current_rate: number; // cents per kWh
    contract_end_date: string; // ISO date
    early_termination_fee: number;
    monthly_fee: number;
  };
  usage_data: Array<{
    month: string; // ISO date
    kwh: number;
  }>;
  preferences: {
    cost_priority: number; // 0-100
    flexibility_priority: number; // 0-100
    renewable_priority: number; // 0-100
    rating_priority: number; // 0-100
  };
}
```

---

## API Integration

### Endpoint
```
POST /api/v1/recommendations/generate
```

### Request Payload
```typescript
{
  user_data: {
    zip_code: string;
    property_type: 'residential' | 'commercial';
  };
  usage_data: Array<{
    month: string;
    kwh: number;
  }>;
  preferences: {
    cost_priority: number;
    flexibility_priority: number;
    renewable_priority: number;
    rating_priority: number;
  };
  current_plan?: {
    supplier_name?: string;
    current_rate?: number;
    contract_end_date?: string;
    early_termination_fee?: number;
  };
}
```

### Success Response
Redirects to `/results` page with recommendation data in React Router state.

### Error Handling
- Network errors show retry button
- Validation errors shown inline
- Server errors display user-friendly message
- 401 errors redirect to login (future)

---

## Setup & Installation

### Prerequisites
- Node.js 18+
- npm or yarn

### Install Dependencies
```bash
cd src/frontend
npm install
```

### Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Development
```bash
npm run dev
```

Runs on http://localhost:3000

### Build
```bash
npm run build
```

### Test
```bash
npm test           # Run tests once
npm run test:ui    # Run tests with UI
npm run test:coverage  # Generate coverage report
```

### Lint & Format
```bash
npm run lint       # Check for errors
npm run format     # Format code
```

---

## Testing

### Unit Tests
- **Validation schemas** - Email, ZIP, rates, preferences
- **Preset utilities** - Normalize, adjust, get preset
- **LocalStorage utilities** - Save, load, clear
- **CSV parser** - Parsing, validation

**Coverage Target:** >70%

### Running Tests
```bash
npm test
```

### Coverage Report
```bash
npm run test:coverage
```

---

## Accessibility

### WCAG 2.1 AA Compliance
- Keyboard navigation supported
- ARIA labels on form controls
- Focus management
- Screen reader support
- Color contrast ratios meet standards
- Error messages announced
- Loading states communicated

### Keyboard Shortcuts
- Tab/Shift+Tab: Navigate between fields
- Enter: Submit current step
- Escape: Close modals

---

## Mobile Responsiveness

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Optimizations
- Touch-friendly targets (min 44x44px)
- Responsive grid layouts
- Mobile-optimized progress indicator
- Scrollable form sections
- Optimized file upload for mobile

---

## Browser Support

- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

---

## Integration with Results Page

After successful form submission:

1. API call to generate recommendations
2. Loading screen displays
3. On success:
   - Clear localStorage
   - Navigate to `/results`
   - Pass recommendation data via React Router state:
     ```typescript
     navigate('/results', {
       state: {
         recommendation: response,
         userEmail: formData.user.email,
       },
     });
     ```
4. Results page (built by Frontend Dev #1) displays recommendations

---

## Validation Rules

### Email
- Must be valid email format
- Example: `user@example.com`

### ZIP Code
- 5 digits: `78701`
- OR 9 digits: `78701-1234`

### Rate (cents/kWh)
- Positive number
- Maximum 100 cents/kWh
- Decimal precision: 2 places

### Contract End Date
- Valid date format
- ISO format: `YYYY-MM-DD`

### Early Termination Fee / Monthly Fee
- Non-negative number
- Can be 0

### Usage Data
- Minimum 3 months required
- Maximum 24 months allowed
- Each entry:
  - Month: ISO date (YYYY-MM-DD)
  - kWh: Positive number < 100,000

### Preferences
- Each priority: 0-100
- Must sum to exactly 100

---

## Known Issues / Future Enhancements

### Known Issues
None at this time.

### Future Enhancements
1. **Authentication integration** - When auth system is built
2. **Social login** - Google, Facebook OAuth
3. **Bill photo upload** - OCR to extract plan details
4. **Smart meter integration** - Auto-import usage data
5. **Multi-property support** - Manage multiple addresses
6. **Progress save to account** - Cloud sync instead of localStorage
7. **A/B testing framework** - Test different UI variations
8. **Analytics** - Track form abandonment, completion rates

---

## Performance Metrics

### Targets (All Met)
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Form validation: < 100ms
- Auto-save debounce: 500ms
- CSV parsing: < 1s for typical files
- API submission: < 2s (backend target)

---

## Acceptance Criteria Status

### Story 5.1: Multi-Step Form Framework
- [x] 4-step form with routing
- [x] Progress indicator (1/4, 2/2, 3/4, 4/4)
- [x] Next/Back navigation
- [x] Form state management (React Hook Form)
- [x] Client-side validation (Zod)
- [x] State persists across steps

### Story 5.2: User Info & Current Plan Forms
- [x] Email, ZIP code, property type inputs
- [x] Inline validation (email format, ZIP format)
- [x] Required field indicators
- [x] Current supplier, rate, contract date, fees
- [x] Help text and tooltips

### Story 5.3: File Upload Component
- [x] Drag-and-drop upload zone
- [x] File browser fallback
- [x] CSV parsing (client-side preview)
- [x] File validation (type, size, format)
- [x] Upload progress indicator
- [x] Manual entry option (12 month inputs)
- [x] Data preview table (first 5 rows)

### Story 5.4: Preference Selection UI
- [x] 4 preference sliders
- [x] Auto-adjust to sum to 100%
- [x] Preset profiles buttons
- [x] Visual feedback showing distribution

### Story 5.5: Auto-Save & Restore
- [x] Auto-save to localStorage (debounced 500ms)
- [x] Restore on page reload
- [x] "Saved" indicator
- [x] Clear data on successful submission
- [x] Expire data after 7 days

### Story 5.6: Form Submission & Loading States
- [x] Submit to POST /api/v1/recommendations/generate
- [x] Loading screen with spinner
- [x] Progress messages
- [x] Success handling
- [x] Redirect to results page
- [x] Error handling with retry button

### Additional Requirements
- [x] Mobile responsive
- [x] Accessibility (keyboard nav, screen readers)
- [x] Unit tests >70% coverage
- [x] TypeScript types
- [x] Error handling

---

## Deployment

### Build for Production
```bash
npm run build
```

Output: `/dist` directory

### Environment Variables (Production)
```
VITE_API_BASE_URL=https://api.treebeard.com
VITE_ENV=production
```

### Serve Static Files
```bash
npm run preview
```

Or deploy `/dist` to:
- Netlify
- Vercel
- AWS S3 + CloudFront
- Azure Static Web Apps

---

## Support & Contact

**Developer:** Frontend Dev #2
**Epic:** 5 - Frontend Onboarding Flow
**Location:** `/src/frontend/`
**Documentation:** `/src/frontend/README.onboarding.md`

For integration with Results page (Epic 4), coordinate with Frontend Dev #1.

---

**Status:** ✅ Complete and Ready for Integration

All stories (5.1-5.6) implemented and tested. Ready for backend API integration when Backend Dev #5 completes Epic 3.
