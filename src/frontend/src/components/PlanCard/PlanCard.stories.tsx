import type { Meta, StoryObj } from '@storybook/react';
import { PlanCard } from './PlanCard';
import type { RankedPlan } from '@/types/recommendation';

const samplePlan: RankedPlan = {
  rank: 1,
  plan_id: '123e4567-e89b-12d3-a456-426614174000',
  plan_name: 'EcoSaver Plus',
  supplier_name: 'Green Energy Co.',
  plan_type: 'Fixed Rate',
  scores: {
    cost_score: 85,
    flexibility_score: 70,
    renewable_score: 95,
    rating_score: 88,
    composite_score: 87,
  },
  projected_annual_cost: 1450,
  projected_monthly_cost: 120.83,
  average_rate_per_kwh: 8.5,
  savings: {
    annual_savings: 250,
    savings_percentage: 14.7,
    monthly_savings: 20.83,
    break_even_months: 0,
  },
  contract_length_months: 12,
  early_termination_fee: 150,
  renewable_percentage: 100,
  monthly_fee: 9.99,
  explanation: 'This plan offers excellent savings with 100% renewable energy. The fixed rate protects you from price fluctuations, making it ideal for budget-conscious customers who care about sustainability.',
  key_differentiators: [
    '100% renewable energy from wind and solar',
    'Fixed rate protects against price increases',
    'High customer satisfaction rating (4.5/5)',
  ],
  trade_offs: [
    '12-month contract with early termination fee',
    'Small monthly service fee of $9.99',
  ],
};

const meta = {
  title: 'Components/PlanCard',
  component: PlanCard,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof PlanCard>;

export default meta;
type Story = StoryObj<typeof meta>;

export const TopRanked: Story = {
  args: {
    plan: samplePlan,
    showRank: true,
  },
};

export const SecondRanked: Story = {
  args: {
    plan: {
      ...samplePlan,
      rank: 2,
      plan_name: 'Value Saver',
      savings: {
        annual_savings: 180,
        savings_percentage: 10.5,
        monthly_savings: 15,
      },
    },
    showRank: true,
  },
};

export const NoSavings: Story = {
  args: {
    plan: {
      ...samplePlan,
      savings: undefined,
    },
    showRank: true,
  },
};

export const MonthToMonth: Story = {
  args: {
    plan: {
      ...samplePlan,
      contract_length_months: 0,
      early_termination_fee: 0,
    },
    showRank: true,
  },
};

export const Selected: Story = {
  args: {
    plan: samplePlan,
    isSelected: true,
    showRank: true,
  },
};

export const WithoutRank: Story = {
  args: {
    plan: samplePlan,
    showRank: false,
  },
};
