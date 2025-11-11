import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import clsx from 'clsx';
import type { CurrentPlan } from '@/types/onboarding';
import { currentPlanSchema, type CurrentPlanFormData } from '@/utils/validation';

interface Step2CurrentPlanProps {
  initialData?: Partial<CurrentPlan>;
  onSubmit: (data: CurrentPlan) => void;
  onBack: () => void;
}

const Tooltip: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [show, setShow] = useState(false);

  return (
    <div className="relative inline-block ml-1">
      <button
        type="button"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onFocus={() => setShow(true)}
        onBlur={() => setShow(false)}
        className="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-full"
        aria-label="More information"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </button>
      {show && (
        <div className="absolute z-10 w-64 p-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg bottom-full left-1/2 transform -translate-x-1/2 mb-2">
          <div className="relative">
            {children}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
          </div>
        </div>
      )}
    </div>
  );
};

export const Step2CurrentPlan: React.FC<Step2CurrentPlanProps> = ({
  initialData,
  onSubmit,
  onBack,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CurrentPlanFormData>({
    resolver: zodResolver(currentPlanSchema),
    defaultValues: initialData || {
      supplier_name: '',
      current_rate: 0,
      contract_end_date: '',
      early_termination_fee: 0,
      monthly_fee: 0,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your current energy plan</h2>
        <p className="text-gray-600">
          Help us understand your existing plan so we can show you potential savings.
        </p>
      </div>

      {/* Supplier Name */}
      <div>
        <label htmlFor="supplier_name" className="block text-sm font-medium text-gray-700 mb-1">
          Current Supplier <span className="text-red-500">*</span>
        </label>
        <input
          {...register('supplier_name')}
          type="text"
          id="supplier_name"
          className={clsx(
            'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            errors.supplier_name ? 'border-red-500' : 'border-gray-300'
          )}
          placeholder="e.g., TXU Energy"
          aria-invalid={errors.supplier_name ? 'true' : 'false'}
        />
        {errors.supplier_name && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {errors.supplier_name.message}
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Current Rate */}
        <div>
          <label htmlFor="current_rate" className="flex items-center text-sm font-medium text-gray-700 mb-1">
            Current Rate (cents/kWh) <span className="text-red-500">*</span>
            <Tooltip>
              The rate you currently pay per kilowatt-hour. You can find this on your electricity bill.
            </Tooltip>
          </label>
          <div className="relative">
            <input
              {...register('current_rate', { valueAsNumber: true })}
              type="number"
              step="0.01"
              id="current_rate"
              className={clsx(
                'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
                errors.current_rate ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="12.5"
              aria-invalid={errors.current_rate ? 'true' : 'false'}
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-500 sm:text-sm">¢/kWh</span>
            </div>
          </div>
          {errors.current_rate && (
            <p className="mt-1 text-sm text-red-600" role="alert">
              {errors.current_rate.message}
            </p>
          )}
        </div>

        {/* Contract End Date */}
        <div>
          <label htmlFor="contract_end_date" className="flex items-center text-sm font-medium text-gray-700 mb-1">
            Contract End Date <span className="text-red-500">*</span>
            <Tooltip>
              The date your current contract expires. Leave blank if you're month-to-month.
            </Tooltip>
          </label>
          <input
            {...register('contract_end_date')}
            type="date"
            id="contract_end_date"
            className={clsx(
              'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
              errors.contract_end_date ? 'border-red-500' : 'border-gray-300'
            )}
            aria-invalid={errors.contract_end_date ? 'true' : 'false'}
          />
          {errors.contract_end_date && (
            <p className="mt-1 text-sm text-red-600" role="alert">
              {errors.contract_end_date.message}
            </p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Early Termination Fee */}
        <div>
          <label htmlFor="early_termination_fee" className="flex items-center text-sm font-medium text-gray-700 mb-1">
            Early Termination Fee <span className="text-red-500">*</span>
            <Tooltip>
              The fee you would pay to cancel your current contract early. Enter 0 if month-to-month or no fee.
            </Tooltip>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              {...register('early_termination_fee', { valueAsNumber: true })}
              type="number"
              step="0.01"
              id="early_termination_fee"
              className={clsx(
                'w-full pl-7 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
                errors.early_termination_fee ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="150.00"
              aria-invalid={errors.early_termination_fee ? 'true' : 'false'}
            />
          </div>
          {errors.early_termination_fee && (
            <p className="mt-1 text-sm text-red-600" role="alert">
              {errors.early_termination_fee.message}
            </p>
          )}
        </div>

        {/* Monthly Fee */}
        <div>
          <label htmlFor="monthly_fee" className="flex items-center text-sm font-medium text-gray-700 mb-1">
            Monthly Base Fee <span className="text-red-500">*</span>
            <Tooltip>
              Any fixed monthly fee charged by your supplier (separate from usage charges). Enter 0 if none.
            </Tooltip>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              {...register('monthly_fee', { valueAsNumber: true })}
              type="number"
              step="0.01"
              id="monthly_fee"
              className={clsx(
                'w-full pl-7 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
                errors.monthly_fee ? 'border-red-500' : 'border-gray-300'
              )}
              placeholder="9.95"
              aria-invalid={errors.monthly_fee ? 'true' : 'false'}
            />
          </div>
          {errors.monthly_fee && (
            <p className="mt-1 text-sm text-red-600" role="alert">
              {errors.monthly_fee.message}
            </p>
          )}
        </div>
      </div>

      {/* Help text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Where to find this information</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                You can find these details on your most recent electricity bill, usually in the "Plan Details" or "Rate Information" section.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6">
        <button
          type="button"
          onClick={onBack}
          className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
        >
          Back
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? 'Saving...' : 'Next'}
        </button>
      </div>
    </form>
  );
};
