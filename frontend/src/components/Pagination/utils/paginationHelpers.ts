/**
 * Формирует URL для указанной страницы.
 *
 * Добавляет параметр page к baseUrl, учитывая существующие параметры:
 * при наличии "?" параметр добавляется через "&", иначе через "?".
 *
 * @example
 * getPageUrl('/articles', 2) // '/articles?page=2'
 * getPageUrl('/articles?category=tech', 2) // '/articles?category=tech&page=2'
 */
export const getPageUrl = (baseUrl: string, pageNumber: number): string => {
  const separator = baseUrl.includes('?') ? '&' : '?';
  return `${baseUrl}${separator}page=${pageNumber}`;
};

/** Диапазон страниц основного окна пагинации. */
export interface PageRange {
  startPage: number;
  endPage: number;
}

/**
 * Вычисляет начальную и конечную страницы для отображения,
 * центрируя текущую страницу в видимом диапазоне.
 *
 * @example
 * calculatePageRange(5, 10) // {startPage: 3, endPage: 7}
 * calculatePageRange(1, 10) // {startPage: 1, endPage: 5}
 * calculatePageRange(10, 10) // {startPage: 6, endPage: 10}
 */
export const calculatePageRange = (currentPage: number, totalPages: number, maxVisiblePages = 5): PageRange => {
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

  if (endPage - startPage < maxVisiblePages - 1) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  return { startPage, endPage };
};
