import React, { useCallback, useState } from 'react';
import clsx from 'clsx';
import type { MonthlyUsage } from '@/types/onboarding';
import {
  parseUsageCSV,
  validateCSVFile,
  downloadExampleCSV,
  type CSVParseResult,
} from '@/utils/csvParser';

interface FileUploadProps {
  onDataParsed: (data: MonthlyUsage[]) => void;
  onError?: (errors: string[]) => void;
  className?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onDataParsed, onError, className }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [errors, setErrors] = useState<string[]>([]);

  const handleFile = useCallback(
    async (file: File) => {
      setIsProcessing(true);
      setErrors([]);

      // Validate file
      const validation = validateCSVFile(file);
      if (!validation.valid) {
        const errorList = [validation.error || 'Invalid file'];
        setErrors(errorList);
        if (onError) onError(errorList);
        setIsProcessing(false);
        return;
      }

      setFileName(file.name);

      // Parse CSV
      try {
        const result: CSVParseResult = await parseUsageCSV(file);

        if (result.success && result.data) {
          onDataParsed(result.data);
          setErrors([]);
        } else if (result.errors) {
          setErrors(result.errors);
          if (onError) onError(result.errors);
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Failed to parse CSV file';
        setErrors([errorMessage]);
        if (onError) onError([errorMessage]);
      } finally {
        setIsProcessing(false);
      }
    },
    [onDataParsed, onError]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        handleFile(files[0]);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        handleFile(files[0]);
      }
    },
    [handleFile]
  );

  return (
    <div className={className}>
      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={clsx(
          'relative border-2 border-dashed rounded-lg p-8 transition-all',
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400',
          isProcessing && 'opacity-50 pointer-events-none'
        )}
      >
        <div className="text-center">
          {/* Icon */}
          <div className="mx-auto w-16 h-16 flex items-center justify-center bg-gray-100 rounded-full mb-4">
            {isProcessing ? (
              <svg
                className="animate-spin h-8 w-8 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            ) : (
              <svg
                className="w-8 h-8 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            )}
          </div>

          {/* Text */}
          <div className="mb-4">
            <label
              htmlFor="file-upload"
              className="relative cursor-pointer text-primary-600 hover:text-primary-700 font-medium focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500 rounded"
            >
              <span>Upload a CSV file</span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                accept=".csv,text/csv"
                className="sr-only"
                onChange={handleFileInput}
                disabled={isProcessing}
                aria-label="Upload CSV file"
              />
            </label>
            <span className="text-gray-600"> or drag and drop</span>
          </div>

          <p className="text-xs text-gray-500">
            CSV file with month and kWh columns (max 5MB)
          </p>

          {fileName && !errors.length && (
            <div className="mt-4 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              <svg
                className="w-4 h-4 mr-1.5"
                fill="currentColor"
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              {fileName}
            </div>
          )}

          {isProcessing && (
            <p className="mt-4 text-sm text-gray-600">Processing your file...</p>
          )}
        </div>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4" role="alert">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                fill="currentColor"
                viewBox="0 0 20 20"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                There {errors.length === 1 ? 'was an error' : 'were errors'} with your file:
              </h3>
              <ul className="mt-2 text-sm text-red-700 list-disc list-inside space-y-1">
                {errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Example download */}
      <div className="mt-4 flex items-center justify-between text-sm">
        <div className="text-gray-600">
          Don't have a CSV file?{' '}
          <button
            type="button"
            onClick={downloadExampleCSV}
            className="text-primary-600 hover:text-primary-700 font-medium underline focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 rounded"
          >
            Download example template
          </button>
        </div>
      </div>

      {/* Format info */}
      <div className="mt-4 bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Expected CSV format:</h4>
        <pre className="text-xs text-gray-600 bg-white p-3 rounded border border-gray-200 overflow-x-auto">
          {`month,kwh
2024-01,850
2024-02,820
2024-03,780`}
        </pre>
        <p className="mt-2 text-xs text-gray-500">
          Include 3-24 months of data. Month should be in YYYY-MM-DD format (first day of month).
        </p>
      </div>
    </div>
  );
};
