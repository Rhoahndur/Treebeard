import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import clsx from 'clsx';
import type { UserInfo } from '@/types/onboarding';
import { userInfoSchema, type UserInfoFormData } from '@/utils/validation';

interface Step1UserInfoProps {
  initialData?: Partial<UserInfo>;
  onSubmit: (data: UserInfo) => void;
  onBack?: () => void;
}

export const Step1UserInfo: React.FC<Step1UserInfoProps> = ({
  initialData,
  onSubmit,
  onBack,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserInfoFormData>({
    resolver: zodResolver(userInfoSchema),
    defaultValues: initialData || {
      email: '',
      zip_code: '',
      property_type: 'residential',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Tell us about yourself</h2>
        <p className="text-gray-600">
          We'll use this information to find energy plans available in your area.
        </p>
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
          Email Address <span className="text-red-500">*</span>
        </label>
        <input
          {...register('email')}
          type="email"
          id="email"
          className={clsx(
            'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            errors.email ? 'border-red-500' : 'border-gray-300'
          )}
          placeholder="you@example.com"
          aria-invalid={errors.email ? 'true' : 'false'}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <p id="email-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.email.message}
          </p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          We'll send your recommendations to this email
        </p>
      </div>

      {/* ZIP Code */}
      <div>
        <label htmlFor="zip_code" className="block text-sm font-medium text-gray-700 mb-1">
          ZIP Code <span className="text-red-500">*</span>
        </label>
        <input
          {...register('zip_code')}
          type="text"
          id="zip_code"
          maxLength={10}
          className={clsx(
            'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors',
            errors.zip_code ? 'border-red-500' : 'border-gray-300'
          )}
          placeholder="78701"
          aria-invalid={errors.zip_code ? 'true' : 'false'}
          aria-describedby={errors.zip_code ? 'zip-error' : undefined}
        />
        {errors.zip_code && (
          <p id="zip-error" className="mt-1 text-sm text-red-600" role="alert">
            {errors.zip_code.message}
          </p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          Used to find plans available in your area
        </p>
      </div>

      {/* Property Type */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Property Type <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label
            className={clsx(
              'relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all hover:border-primary-300',
              'focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-primary-500'
            )}
          >
            <input
              {...register('property_type')}
              type="radio"
              value="residential"
              className="sr-only"
            />
            <div className="flex items-center w-full">
              <div className="flex-shrink-0">
                <svg
                  className="w-8 h-8 text-primary-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                  />
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <div className="text-sm font-medium text-gray-900">Residential</div>
                <div className="text-xs text-gray-500">Home or apartment</div>
              </div>
            </div>
          </label>

          <label
            className={clsx(
              'relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all hover:border-primary-300',
              'focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-primary-500'
            )}
          >
            <input
              {...register('property_type')}
              type="radio"
              value="commercial"
              className="sr-only"
            />
            <div className="flex items-center w-full">
              <div className="flex-shrink-0">
                <svg
                  className="w-8 h-8 text-primary-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <div className="text-sm font-medium text-gray-900">Commercial</div>
                <div className="text-xs text-gray-500">Business property</div>
              </div>
            </div>
          </label>
        </div>
        {errors.property_type && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {errors.property_type.message}
          </p>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6">
        {onBack ? (
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            Back
          </button>
        ) : (
          <div />
        )}
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
