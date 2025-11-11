import React, { useEffect, useState } from 'react';
import clsx from 'clsx';

interface LoadingScreenProps {
  className?: string;
}

const LOADING_MESSAGES = [
  { message: 'Analyzing your usage patterns...', duration: 2000 },
  { message: 'Finding available plans in your area...', duration: 2500 },
  { message: 'Calculating potential savings...', duration: 2000 },
  { message: 'Generating AI-powered explanations...', duration: 2500 },
  { message: 'Finalizing your recommendations...', duration: 2000 },
];

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ className }) => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Cycle through messages
    const messageInterval = setInterval(() => {
      setCurrentMessageIndex((prev) => {
        if (prev < LOADING_MESSAGES.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, LOADING_MESSAGES[currentMessageIndex]?.duration || 2000);

    return () => clearInterval(messageInterval);
  }, [currentMessageIndex]);

  useEffect(() => {
    // Smooth progress bar
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 95) {
          return prev + 1;
        }
        return prev;
      });
    }, 100);

    return () => clearInterval(progressInterval);
  }, []);

  return (
    <div className={clsx('flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6', className)}>
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        {/* Animated icon */}
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="w-20 h-20 border-4 border-primary-200 rounded-full animate-pulse" />
            <div className="absolute inset-0 w-20 h-20 border-4 border-primary-600 rounded-full border-t-transparent animate-spin" />
            <svg
              className="absolute inset-0 m-auto w-10 h-10 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          </div>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">
          Finding Your Perfect Plans
        </h2>

        {/* Message */}
        <p className="text-center text-gray-600 mb-6 h-12 flex items-center justify-center">
          <span className="animate-fade-in">
            {LOADING_MESSAGES[currentMessageIndex]?.message}
          </span>
        </p>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-sm text-gray-500">
            <span>Processing...</span>
            <span>{progress}%</span>
          </div>
        </div>

        {/* Fun facts or tips */}
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mt-6">
          <div className="flex items-start">
            <svg
              className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0"
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
            <div className="ml-3">
              <p className="text-sm text-blue-800">
                <span className="font-semibold">Did you know?</span> The average household can save
                $200-$400 per year by switching to a plan that better matches their usage patterns.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
