import React, { useRef, useEffect, useState } from 'react';
import { Skeleton } from '@/components/design-system';
import { AlertCircle } from 'lucide-react';

export interface ChartWrapperProps {
  title?: string;
  subtitle?: string;
  children?: React.ReactNode;
  isLoading?: boolean;
  error?: string | null;
  height?: number;
  className?: string;
  ariaLabel?: string;
  showLegend?: boolean;
}

export const ChartWrapper: React.FC<ChartWrapperProps> = ({
  title,
  subtitle,
  children,
  isLoading = false,
  error = null,
  height = 300,
  className = '',
  ariaLabel,
  showLegend = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState<number>(0);

  // Responsive sizing - observe container width
  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setContainerWidth(entry.contentRect.width);
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // Adjust height for mobile
  const responsiveHeight =
    containerWidth < 640 ? Math.min(height, 200) : height;

  if (isLoading) {
    return (
      <div
        className={`bg-white rounded-lg shadow-card p-6 ${className}`}
        ref={containerRef}
      >
        {title && (
          <div className="mb-4">
            <Skeleton className="h-6 w-48 mb-2" />
            {subtitle && <Skeleton className="h-4 w-64" />}
          </div>
        )}
        <Skeleton className="w-full" style={{ height: responsiveHeight }} />
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={`bg-white rounded-lg shadow-card p-6 ${className}`}
        ref={containerRef}
        role="alert"
      >
        {title && (
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
          </div>
        )}
        <div
          className="flex flex-col items-center justify-center text-center py-12"
          style={{ height: responsiveHeight }}
        >
          <AlertCircle className="w-12 h-12 text-danger mb-3" aria-hidden="true" />
          <p className="text-gray-900 font-medium mb-1">Unable to Load Chart</p>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg shadow-card p-6 ${className}`}
      ref={containerRef}
      role="figure"
      aria-label={ariaLabel || title}
    >
      {(title || subtitle) && (
        <div className="mb-4">
          {title && (
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>
      )}
      <div
        className="chart-container"
        style={{ width: '100%', height: responsiveHeight }}
      >
        {children}
      </div>
    </div>
  );
};

ChartWrapper.displayName = 'ChartWrapper';
