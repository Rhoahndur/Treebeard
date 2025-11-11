import React from 'react';
import { clsx } from 'clsx';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number;
  height?: string | number;
  circle?: boolean;
  count?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({ 
  width,
  height,
  circle = false,
  count = 1,
  className,
  style,
  ...props
}) => {
  const skeletons = Array.from({ length: count }, (_, i) => (
    <div
      key={i}
      className={clsx(
        'animate-pulse-soft bg-gray-200',
        circle ? 'rounded-full' : 'rounded',
        className
      )}
      style={{
        width: width || (circle ? '40px' : '100%'),
        height: height || (circle ? '40px' : '20px'),
        ...style,
      }}
      aria-hidden="true"
      {...props}
    />
  ));

  return count > 1 ? <div className="space-y-2">{skeletons}</div> : skeletons[0];
};

Skeleton.displayName = 'Skeleton';

export const SkeletonCard: React.FC = () => (
  <div className="bg-white rounded-card shadow-card p-6" aria-hidden="true">
    <div className="flex items-center space-x-4 mb-4">
      <Skeleton circle width={48} height={48} />
      <div className="flex-1">
        <Skeleton height={24} width="60%" className="mb-2" />
        <Skeleton height={16} width="40%" />
      </div>
    </div>
    <Skeleton count={3} className="mb-2" />
    <div className="flex gap-2 mt-4">
      <Skeleton width={100} height={32} />
      <Skeleton width={100} height={32} />
    </div>
  </div>
);

SkeletonCard.displayName = 'SkeletonCard';
