import { useCallback, useState } from 'react';

/** Опции хука usePagination. */
export interface UsePaginationOptions {
  /** Начальный номер страницы. */
  initialPage?: number;
  /** Общее количество страниц. */
  totalPages?: number;
  /** Callback при изменении страницы. */
  onPageChange?: (page: number) => void;
}

/** Результат хука usePagination. */
export interface UsePaginationResult {
  currentPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
  nextPage: () => void;
  previousPage: () => void;
  goToPage: (page: number) => void;
  setTotalPages: React.Dispatch<React.SetStateAction<number>>;
}

/**
 * Хук для управления состоянием пагинации.
 *
 * Упрощает работу с пагинацией, предоставляя унифицированный интерфейс
 * для управления текущей страницей, вычисления следующей/предыдущей страниц
 * и обработки переходов.
 *
 * @example
 * const {
 *   currentPage,
 *   nextPage,
 *   previousPage,
 *   hasPrevious,
 *   hasNext,
 *   setTotalPages,
 * } = usePagination({ initialPage: 1 });
 */
const usePagination = (options: UsePaginationOptions = {}): UsePaginationResult => {
  const { initialPage = 1, totalPages: initialTotalPages = 1, onPageChange } = options;

  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(initialTotalPages);

  const hasNext = currentPage < totalPages;
  const hasPrevious = currentPage > 1;

  const nextPage = useCallback(() => {
    if (hasNext) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      if (onPageChange) {
        onPageChange(newPage);
      }
    }
  }, [currentPage, hasNext, onPageChange]);

  const previousPage = useCallback(() => {
    if (hasPrevious) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      if (onPageChange) {
        onPageChange(newPage);
      }
    }
  }, [currentPage, hasPrevious, onPageChange]);

  const goToPage = useCallback(
    (page: number) => {
      if (page >= 1 && page <= totalPages && page !== currentPage) {
        setCurrentPage(page);
        if (onPageChange) {
          onPageChange(page);
        }
      }
    },
    [currentPage, totalPages, onPageChange],
  );

  return {
    currentPage,
    totalPages,
    hasNext,
    hasPrevious,
    nextPage,
    previousPage,
    goToPage,
    setTotalPages,
  };
};

export default usePagination;
