/**
 * Утилиты для определения состояний кнопок навигации
 */

/**
 * Проверяет, должна ли кнопка быть отключена
 *
 * @param {string} type - Тип кнопки ('first', 'prev', 'next', 'last')
 * @param {number} currentPage - Текущая страница
 * @param {number} totalPages - Общее количество страниц
 * @return {boolean} true, если кнопка должна быть отключена
 */
export const isButtonDisabled = (type, currentPage, totalPages) => {
  switch (type) {
    case 'first':
    case 'prev':
      return currentPage === 1;
    case 'next':
    case 'last':
      return currentPage === totalPages;
    default:
      return false;
  }
};

/**
 * Получает URL для кнопки навигации
 *
 * @param {string} type - Тип кнопки ('first', 'prev', 'next', 'last')
 * @param {number} currentPage - Текущая страница
 * @param {number} totalPages - Общее количество страниц
 * @param {string} baseUrl - Базовый URL для формирования ссылок
 * @return {string|undefined} URL для кнопки или undefined, если кнопка должна быть отключена
 */
export const getButtonHref = (type, currentPage, totalPages, baseUrl) => {
  if (isButtonDisabled(type, currentPage, totalPages)) {
    return undefined;
  }

  switch (type) {
    case 'first':
      return baseUrl + (baseUrl.includes('?') ? '&' : '?') + 'page=1';
    case 'prev':
      return baseUrl + (baseUrl.includes('?') ? '&' : '?') + 'page=' + (currentPage - 1);
    case 'next':
      return baseUrl + (baseUrl.includes('?') ? '&' : '?') + 'page=' + (currentPage + 1);
    case 'last':
      return baseUrl + (baseUrl.includes('?') ? '&' : '?') + 'page=' + totalPages;
    default:
      return undefined;
  }
};

/**
 * Получает текст для кнопки навигации
 *
 * @param {string} type - Тип кнопки ('first', 'prev', 'next', 'last')
 * @return {string} Текст для кнопки
 */
export const getButtonText = (type) => {
  switch (type) {
    case 'first':
      return 'первая';
    case 'prev':
      return 'предыдущая';
    case 'next':
      return 'следующая';
    case 'last':
      return 'последняя';
    default:
      return '';
  }
};

/**
 * Получает CSS-классы для кнопки навигации
 *
 * @param {string} type - Тип кнопки ('first', 'prev', 'next', 'last')
 * @return {string} CSS-классы для кнопки
 */
export const getButtonClassName = (type) => {
  const baseClasses = 'btn btn-outline-dark';

  switch (type) {
    case 'first':
    case 'prev':
      return `${baseClasses} me-1`;
    case 'next':
    case 'last':
      return `${baseClasses} ms-1`;
    default:
      return baseClasses;
  }
};
