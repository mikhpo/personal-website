import React from 'react';
import NavigationPagination from '@components/Pagination/NavigationPagination';
import NumbersPagination from '@components/Pagination/NumbersPagination';
import type { PaginationCoreProps } from '@components/Pagination/NavigationPagination';

/** Свойства основного компонента пагинации. */
export interface PaginationProps extends PaginationCoreProps {
  /** Тип пагинации. */
  type?: 'navigation' | 'numbers';
}

/**
 * Основной компонент пагинации.
 *
 * @return Компонент пагинации или null, если страниц меньше двух
 */
const Pagination = ({
  currentPage,
  totalPages,
  hasNext = false,
  hasPrevious = false,
  onPageChange,
  onNext,
  onPrevious,
  baseUrl = '',
  type = 'navigation',
}: PaginationProps) => {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <nav className="container mt-4" aria-label="Навигация по страницам">
      <div className="pagination">
        {type === 'numbers' ? (
          <NumbersPagination currentPage={currentPage} totalPages={totalPages} baseUrl={baseUrl} />
        ) : (
          <NavigationPagination
            currentPage={currentPage}
            totalPages={totalPages}
            hasNext={hasNext}
            hasPrevious={hasPrevious}
            onPageChange={onPageChange}
            onNext={onNext}
            onPrevious={onPrevious}
            baseUrl={baseUrl}
          />
        )}
      </div>
    </nav>
  );
};

export default Pagination;
