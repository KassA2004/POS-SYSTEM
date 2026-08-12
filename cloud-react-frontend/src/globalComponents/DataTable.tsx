import type { ReactNode } from 'react';
import { ChevronsUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { Skeleton } from './Skeleton';

export interface Column<T> {
  key: string;
  header: string;
  align?: 'left' | 'right' | 'center';
  sortable?: boolean;
  render?: (row: T) => ReactNode;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
  onSort?: (key: string) => void;
  emptyText?: string;
}

export function DataTable<T extends object>({
  columns,
  data,
  loading,
  sortColumn,
  sortDirection,
  onSort,
  emptyText = 'No data records found',
}: DataTableProps<T>) {
  return (
    <div className="w-full rounded-lg border border-border-default overflow-hidden bg-surface">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left">
          <thead>
            <tr className="bg-surface-sunken border-b border-border-subtle h-9">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-5 text-caption font-medium text-ink-secondary ${
                    col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'
                  }`}
                >
                  {col.sortable ? (
                    <button
                      onClick={() => onSort?.(col.key)}
                      className="inline-flex items-center gap-1.5 hover:text-ink-primary cursor-pointer select-none"
                    >
                      {col.header}
                      {sortColumn === col.key ? (
                        sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />
                      ) : (
                        <ChevronsUpDown size={14} className="text-ink-tertiary" />
                      )}
                    </button>
                  ) : (
                    col.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle text-body text-ink-primary">
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="h-11">
                  {columns.map((col) => (
                    <td key={col.key} className="px-5 py-2">
                      <Skeleton className="h-4 w-full" />
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-5 py-12 text-center text-ink-tertiary">
                  {emptyText}
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr key={idx} className="h-11 hover:bg-surface-hover transition-colors">
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`px-5 py-2 ${
                        col.align === 'right' ? 'text-right tabular-nums' : col.align === 'center' ? 'text-center' : 'text-left'
                      }`}
                    >
                      {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? '')}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
