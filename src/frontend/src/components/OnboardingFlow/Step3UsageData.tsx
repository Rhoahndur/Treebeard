import React, { useState } from 'react';
import clsx from 'clsx';
import type { MonthlyUsage } from '@/types/onboarding';
import { FileUpload } from '../FileUpload/FileUpload';

interface Step3UsageDataProps {
  initialData?: MonthlyUsage[];
  onSubmit: (data: MonthlyUsage[]) => void;
  onBack: () => void;
}

export const Step3UsageData: React.FC<Step3UsageDataProps> = ({
  initialData,
  onSubmit,
  onBack,
}) => {
  const [usageData, setUsageData] = useState<MonthlyUsage[]>(initialData || []);
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [manualData, setManualData] = useState<MonthlyUsage[]>(
    initialData || generateEmptyMonths(12)
  );

  const handleFileDataParsed = (data: MonthlyUsage[]) => {
    setUsageData(data);
    setShowManualEntry(false);
  };

  const handleManualChange = (index: number, field: 'month' | 'kwh', value: string) => {
    const newData = [...manualData];
    if (field === 'month') {
      newData[index].month = value;
    } else {
      newData[index].kwh = parseFloat(value) || 0;
    }
    setManualData(newData);
  };

  const handleAddMonth = () => {
    setManualData([...manualData, { month: '', kwh: 0 }]);
  };

  const handleRemoveMonth = (index: number) => {
    const newData = manualData.filter((_, i) => i !== index);
    setManualData(newData);
  };

  const handleManualSubmit = () => {
    // Filter out empty rows
    const validData = manualData.filter((item) => item.month && item.kwh > 0);
    if (validData.length >= 3) {
      setUsageData(validData);
      setShowManualEntry(false);
    }
  };

  const handleNext = () => {
    if (showManualEntry) {
      const validData = manualData.filter((item) => item.month && item.kwh > 0);
      if (validData.length >= 3) {
        onSubmit(validData);
      }
    } else {
      onSubmit(usageData);
    }
  };

  const isValid = showManualEntry
    ? manualData.filter((item) => item.month && item.kwh > 0).length >= 3
    : usageData.length >= 3;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your energy usage</h2>
        <p className="text-gray-600">
          Upload your usage data or enter it manually. We need at least 3 months of data to generate accurate recommendations.
        </p>
      </div>

      {/* Tab switcher */}
      <div className="flex border-b border-gray-200">
        <button
          type="button"
          onClick={() => setShowManualEntry(false)}
          className={clsx(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
            !showManualEntry
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          )}
        >
          Upload CSV
        </button>
        <button
          type="button"
          onClick={() => setShowManualEntry(true)}
          className={clsx(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
            showManualEntry
              ? 'border-primary-600 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          )}
        >
          Manual Entry
        </button>
      </div>

      {/* CSV Upload */}
      {!showManualEntry && (
        <div>
          <FileUpload onDataParsed={handleFileDataParsed} />

          {/* Data preview */}
          {usageData.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                Data Preview ({usageData.length} months)
              </h3>
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Month
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          Usage (kWh)
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {usageData.slice(0, 5).map((item, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(item.month).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                            })}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.kwh.toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {usageData.length > 5 && (
                  <div className="bg-gray-50 px-6 py-3 text-sm text-gray-500">
                    + {usageData.length - 5} more months
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Manual Entry */}
      {showManualEntry && (
        <div>
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
            {manualData.map((item, index) => (
              <div key={index} className="flex gap-3 items-start">
                <div className="flex-1">
                  <label htmlFor={`month-${index}`} className="sr-only">
                    Month
                  </label>
                  <input
                    type="date"
                    id={`month-${index}`}
                    value={item.month}
                    onChange={(e) => handleManualChange(index, 'month', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Select month"
                  />
                </div>
                <div className="flex-1">
                  <label htmlFor={`kwh-${index}`} className="sr-only">
                    kWh
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      id={`kwh-${index}`}
                      value={item.kwh || ''}
                      onChange={(e) => handleManualChange(index, 'kwh', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="kWh"
                      min="0"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <span className="text-gray-500 text-sm">kWh</span>
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveMonth(index)}
                  className="p-2 text-red-600 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                  aria-label="Remove month"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={handleAddMonth}
            className="mt-4 w-full px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 border border-primary-200 rounded-lg hover:bg-primary-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
          >
            + Add Month
          </button>

          {manualData.filter((item) => item.month && item.kwh > 0).length < 3 && (
            <p className="mt-2 text-sm text-amber-600">
              At least 3 months of data required (currently{' '}
              {manualData.filter((item) => item.month && item.kwh > 0).length})
            </p>
          )}
        </div>
      )}

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
          type="button"
          onClick={handleNext}
          disabled={!isValid}
          className="px-6 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
};

function generateEmptyMonths(count: number): MonthlyUsage[] {
  const months: MonthlyUsage[] = [];
  const now = new Date();

  for (let i = count - 1; i >= 0; i--) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');

    months.push({
      month: `${year}-${month}-01`,
      kwh: 0,
    });
  }

  return months;
}
