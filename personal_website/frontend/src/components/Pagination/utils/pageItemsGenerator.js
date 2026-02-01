/**
 * Утилиты для генерации элементов пагинации
 */

/**
 * Создает элемент первой страницы и многоточие в начале, если нужно
 *
 * @param {number} startPage - Начальная страница в основном диапазоне
 * @param {number} totalPages - Общее количество страниц
 * @param {string} baseUrl - Базовый URL для формирования ссылок
 * @param {Function} createElement - Функция для создания React-элементов
 * @return {Array} Массив элементов пагинации
 */
export const createFirstPageElements = (startPage, totalPages, baseUrl, createElement) => {
  const items = [];

  if (startPage > 1) {
    items.push(createElement('first-page'));

    if (startPage > 2) {
      items.push(createElement('ellipsis-start'));
    }
  }

  return items;
};

/**
 * Создает элементы страниц в основном диапазоне
 *
 * @param {number} startPage - Начальная страница в основном диапазоне
 * @param {number} endPage - Конечная страница в основном диапазоне
 * @param {number} currentPage - Текущая страница
 * @param {string} baseUrl - Базовый URL для формирования ссылок
 * @param {Function} createElement - Функция для создания React-элементов
 * @return {Array} Массив элементов пагинации
 */
export const createMainPageElements = (startPage, endPage, currentPage, baseUrl, createElement) => {
  const items = [];

  for (let i = startPage; i <= endPage; i++) {
    items.push(createElement('page', i));
  }

  return items;
};

/**
 * Создает многоточие и последнюю страницу в конце, если нужно
 *
 * @param {number} endPage - Конечная страница в основном диапазоне
 * @param {number} totalPages - Общее количество страниц
 * @param {string} baseUrl - Базовый URL для формирования ссылок
 * @param {Function} createElement - Функция для создания React-элементов
 * @return {Array} Массив элементов пагинации
 */
export const createLastPageElements = (endPage, totalPages, baseUrl, createElement) => {
  const items = [];

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      items.push(createElement('ellipsis-end'));
    }
    items.push(createElement('last-page'));
  }

  return items;
};
