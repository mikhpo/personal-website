/**
 * Формирует URL для указанной страницы
 *
 * @param {string} baseUrl - Базовый URL для формирования ссылок
 * @param {number} pageNumber - Номер страницы
 * @return {string} URL страницы с параметром page
 *
 * @description
 * Добавляет параметр page к baseUrl.
 *
 * При добавлении параметра page функция учитывает наличие существующих
 * параметров в URL:
 * - Если URL уже содержит параметры (присутствует символ ?),
 *   то параметр page добавляется через символ &,
 * - Если параметров нет, то параметр page добавляется через символ ?.
 *
 * Примеры:
 * - '/articles' -> '/articles?page=2'
 * - '/articles?category=tech' -> '/articles?category=tech&page=2'
 */
export const getPageUrl = (baseUrl, pageNumber) => {
  const separator = baseUrl.includes('?') ? '&' : '?';
  return `${baseUrl}${separator}page=${pageNumber}`;
};

/**
 * Вычисляет начальную и конечную страницы для отображения
 *
 * @param {number} currentPage - Текущая страница
 * @param {number} totalPages - Общее количество страниц
 * @param {number} maxVisiblePages - Максимальное количество отображаемых страниц
 * @return {Object} Объект с startPage и endPage
 *
 * @description
 * Вычисляет диапазон страниц для отображения в пагинации, центрируя текущую страницу.
 *
 * Логика работы:
 * 1. Сначала вычисляется начальная страница, которая должна быть на середине
 *    видимого диапазона относительно текущей страницы
 * 2. Затем вычисляется конечная страница, учитывая ограничение maxVisiblePages
 *    и общее количество страниц
 * 3. Если диапазон страниц меньше maxVisiblePages (например, в конце списка),
 *    корректируется начальная страница, чтобы показать максимум элементов
 *
 * Примеры:
 * - currentPage=5, totalPages=10, maxVisiblePages=5 -> {startPage: 3, endPage: 7}
 * - currentPage=1, totalPages=10, maxVisiblePages=5 -> {startPage: 1, endPage: 5}
 * - currentPage=10, totalPages=10, maxVisiblePages=5 -> {startPage: 6, endPage: 10}
 */
export const calculatePageRange = (currentPage, totalPages, maxVisiblePages = 5) => {
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

  if (endPage - startPage < maxVisiblePages - 1) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  return { startPage, endPage };
};
