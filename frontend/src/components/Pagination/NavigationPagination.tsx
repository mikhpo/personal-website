import React from 'react';
import PageInfo from '@components/Pagination/PageInfo';
import { renderNavigationButton } from '@components/Pagination/utils/paginationRenderers';

/** Общие свойства компонентов пагинации. */
export interface PaginationCoreProps {
  currentPage: number;
  totalPages: number;
  hasNext?: boolean;
  hasPrevious?: boolean;
  onPageChange?: (page: number) => void;
  onNext?: () => void;
  onPrevious?: () => void;
  baseUrl?: string;
}

/**
 * Компонент навигационной пагинации.
 */
const NavigationPagination = ({
  currentPage,
  totalPages,
  hasNext = false,
  hasPrevious = false,
  onPageChange,
  onNext,
  onPrevious,
  baseUrl = '',
}: PaginationCoreProps) => {
  return (
    <span className="step-links">
      <div>
        {(currentPage > 1 || hasPrevious) && (
          <>
            {renderNavigationButton('first', currentPage, totalPages, baseUrl, onPageChange)}
            {onPrevious ? (
              <button className="btn btn-outline-dark me-1" onClick={() => onPrevious()} disabled={!hasPrevious}>
                предыдущая
              </button>
            ) : (
              renderNavigationButton('prev', currentPage, totalPages, baseUrl, onPageChange)
            )}
          </>
        )}

        <PageInfo currentPage={currentPage} totalPages={totalPages} />

        {(currentPage < totalPages || hasNext) && (
          <>
            {onNext ? (
              <button className="btn btn-outline-dark ms-1" onClick={() => onNext()} disabled={!hasNext}>
                следующая
              </button>
            ) : (
              renderNavigationButton('next', currentPage, totalPages, baseUrl, onPageChange)
            )}
            {renderNavigationButton('last', currentPage, totalPages, baseUrl, onPageChange)}
          </>
        )}
      </div>
    </span>
  );
};

export default NavigationPagination;
