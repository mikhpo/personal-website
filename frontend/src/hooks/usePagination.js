import { useState, useCallback } from 'react';

/**
 * Хук для управления состоянием пагинации.
 *
 * Упрощает работу с пагинацией, предоставляя унифицированный интерфейс
 * для управления текущей страницей, вычисления следующей/предыдущей страниц
 * и обработки переходов.
 *
 * @param {Object} [options={}] - Дополнительные опции
 * @param {number} [options.initialPage=1] - Начальный номер страницы
 * @param {number} [options.totalPages=1] - Общее количество страниц
 * @param {Function} [options onPageChange] - Callback при изменении страницы
 * @return {Object} Объект с состоянием пагинации и функциями управления
 * @property {number} currentPage - Текущая страница
 * @property {number} totalPages - Общее количество страниц
 * @property {boolean} hasNext - Есть ли следующая страница
 * @property {boolean} hasPrevious - Есть ли предыдущая страница
 * @property {Function} nextPage - Функция для перехода к следующей странице
 * @property {Function} previousPage - Функция для перехода к предыдущей странице
 * @property {Function} goToPage - Функция для перехода к указанной странице
 * @property {Function} setTotalPages - Функция для обновления общего количества страниц
 *
 * @example
 * // Базовое использование
 * const {
 *   currentPage,
 *   nextPage,
 *   previousPage,
 *   hasPrevious,
 *   hasNext,
 *   setTotalPages
 * } = usePagination({ initialPage: 1 });
 *
 * @example
 * // Использование с callback
 * const pagination = usePagination({
 *   initialPage: 1,
 *   onPageChange: (page) => console.log('Страница изменена:', page)
 * });
 */
const usePagination = (options = {}) => {
  const {
    initialPage = 1,
    totalPages: initialTotalPages = 1,
    onPageChange,
  } = options;

  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(initialTotalPages);

  /**
   * Вычисляет наличие следующей страницы.
   * @return {boolean}
   */
  const hasNext = currentPage < totalPages;

  /**
   * Вычисляет наличие предыдущей страницы.
   * @return {boolean}
   */
  const hasPrevious = currentPage > 1;

  /**
   * Переход к следующей странице.
   * @function
   * @return {void}
   */
  const nextPage = useCallback(() => {
    if (hasNext) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      if (onPageChange) {
        onPageChange(newPage);
      }
    }
  }, [currentPage, hasNext, onPageChange]);

  /**
   * Переход к предыдущей странице.
   * @function
   * @return {void}
   */
  const previousPage = useCallback(() => {
    if (hasPrevious) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      if (onPageChange) {
        onPageChange(newPage);
      }
    }
  }, [currentPage, hasPrevious, onPageChange]);

  /**
   * Переход к указанной странице.
   * @function
   * @param {number} page - Номер страницы для перехода
   * @return {void}
   */
  const goToPage = useCallback((page) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      setCurrentPage(page);
      if (onPageChange) {
        onPageChange(page);
      }
    }
  }, [currentPage, totalPages, onPageChange]);

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
