import React, { useState } from 'react';
import { clsx } from 'clsx';
import { Button } from '@/components/design-system/Button';
import type { ColumnDef, SortDirection } from '@/types/admin';

/**
 * DataTable Component
 *
 * Generic, reusable table component with sorting, pagination, and filtering.
 * Used throughout the admin dashboard for displaying data in tabular format.
 *
 * @example
 * <DataTable
 *   columns={columns}
 *   data={users}
 *   currentPage={1}
 *   totalPages={10}
 *   onPageChange={setPage}
 *   onSort={(key, direction) => handleSort(key, direction)}
 * />
 */

export interface DataTableProps<T> {
  /** Column definitions */
  columns: ColumnDef<T>[];
  /** Data rows */
  data: T[];
  /** Loading state */
  loading?: boolean;
  /** Empty state message */
  emptyMessage?: string;
  /** Current page number */
  currentPage?: number;
  /** Total pages */
  totalPages?: number;
  /** Total items count */
  totalItems?: number;
  /** Items per page */
  itemsPerPage?: number;
  /** Page change handler */
  onPageChange?: (page: number) => void;
  /** Sort handler */
  onSort?: (key: string, direction: SortDirection) => void;
  /** Current sort key */
  sortKey?: string;
  /** Current sort direction */
  sortDirection?: SortDirection;
  /** Row key extractor */
  getRowKey: (row: T) => string;
  /** Row click handler */
  onRowClick?: (row: T) => void;
}

/**
 * DataTable Component
 */
export const DataTable = <T,>({
  columns,
  data,
  loading = false,
  emptyMessage = 'No data available',
  currentPage = 1,
  totalPages = 1,
  totalItems,
  itemsPerPage,
  onPageChange,
  onSort,
  sortKey,
  sortDirection,
  getRowKey,
  onRowClick,
}: DataTableProps<T>) => {
  const [localSortKey, setLocalSortKey] = useState<string | undefined>(sortKey);
  const [localSortDirection, setLocalSortDirection] = useState<SortDirection>('asc');

  const handleSort = (key: string) => {
    const newDirection: SortDirection =
      localSortKey === key && localSortDirection === 'asc' ? 'desc' : 'asc';

    setLocalSortKey(key);
    setLocalSortDirection(newDirection);

    if (onSort) {
      onSort(key, newDirection);
    }
  };

  const renderSortIcon = (columnKey: string) => {
    if (localSortKey !== columnKey) {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
        </svg>
      );
    }

    return localSortDirection === 'asc' ? (
      <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
      </svg>
    ) : (
      <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    );
  };

  const startItem = totalItems ? (currentPage - 1) * (itemsPerPage || 0) + 1 : 0;
  const endItem = totalItems ? Math.min(currentPage * (itemsPerPage || 0), totalItems) : 0;

  return (
    <div className="bg-white rounded-lg shadow-card overflow-hidden">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={clsx(
                    'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                    column.sortable && 'cursor-pointer hover:bg-gray-100 select-none'
                  )}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.label}</span>
                    {column.sortable && renderSortIcon(column.key)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 5 }).map((_, idx) => (
                <tr key={idx}>
                  {columns.map((column) => (
                    <td key={column.key} className="px-6 py-4">
                      <div className="h-4 bg-gray-200 rounded animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length === 0 ? (
              // Empty state
              <tr>
                <td colSpan={columns.length} className="px-6 py-12 text-center">
                  <div className="flex flex-col items-center justify-center text-gray-500">
                    <svg className="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p className="text-sm font-medium">{emptyMessage}</p>
                  </div>
                </td>
              </tr>
            ) : (
              // Data rows
              data.map((row) => (
                <tr
                  key={getRowKey(row)}
                  className={clsx(
                    'hover:bg-gray-50 transition-colors',
                    onRowClick && 'cursor-pointer'
                  )}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((column) => {
                    const value = (row as any)[column.key];
                    return (
                      <td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm">
                        {column.render ? column.render(value, row) : value}
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {onPageChange && totalPages > 1 && (
        <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div className="flex items-center justify-between">
            {/* Pagination info */}
            <div className="text-sm text-gray-700">
              {totalItems && (
                <span>
                  Showing <span className="font-medium">{startItem}</span> to{' '}
                  <span className="font-medium">{endItem}</span> of{' '}
                  <span className="font-medium">{totalItems}</span> results
                </span>
              )}
            </div>

            {/* Pagination controls */}
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Previous
              </Button>

              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum: number;

                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => onPageChange(pageNum)}
                      className={clsx(
                        'px-3 py-1 text-sm font-medium rounded',
                        pageNum === currentPage
                          ? 'bg-primary-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      )}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
