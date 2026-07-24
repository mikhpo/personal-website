/**
 * Утилиты для рендеринга элементов пагинации
 */

import React from 'react';
import { Pagination as BSPagination } from 'react-bootstrap';
import { getPageUrl } from '@components/Pagination/utils/paginationHelpers';
import { getButtonText, getButtonClassName, isButtonDisabled, getButtonHref } from '@components/Pagination/utils/buttonStates';

/**
 * Рендерит элемент пагинации с номерами страниц
 *
 * @param {string} elementType - Тип элемента ('first-page', 'ellipsis-start', 'page', 'ellipsis-end', 'last-page')
 * @param {number} page - Номер страницы (для элементов страниц)
 * @param {number} currentPage - Текущая страница
 * @param {number} totalPages - Общее количество страниц
 * @param {string} baseUrl - Базовый URL для формирования ссылок
 * @return {JSX.Element} Элемент пагинации
 */
export const renderPaginationItem = (elementType, page, currentPage, totalPages, baseUrl) => {
  switch (elementType) {
    case 'first-page':
      return (
        <BSPagination.Item key={1} href={getPageUrl(baseUrl, 1)}>
          1
        </BSPagination.Item>
      );

    case 'ellipsis-start':
      return <BSPagination.Ellipsis key="ellipsis-start" disabled />;

    case 'page':
      return (
        <BSPagination.Item
          key={page}
          active={page === currentPage}
          href={page === currentPage ? undefined : getPageUrl(baseUrl, page)}
        >
          {page}
        </BSPagination.Item>
      );

    case 'ellipsis-end':
      return <BSPagination.Ellipsis key="ellipsis-end" disabled />;

    case 'last-page':
      return (
        <BSPagination.Item key={totalPages} href={getPageUrl(baseUrl, totalPages)}>
          {totalPages}
        </BSPagination.Item>
      );

    default:
      return null;
  }
};

/**
 * Рендерит навигационную кнопку
 *
 * @param {string} type - Тип кнопки ('first', 'prev', 'next', 'last')
 * @param {number} currentPage - Текущая страница
 * @param {number} totalPages - Общее количество страниц
 * @param {string} baseUrl - Базовый URL для формирования ссылок
 * @param {function} [onPageChange] - Обработчик изменения страницы (опционально)
 * @return {JSX.Element} Навигационная кнопка
 */
export const renderNavigationButton = (type, currentPage, totalPages, baseUrl, onPageChange) => {
  const disabled = isButtonDisabled(type, currentPage, totalPages);
  const href = getButtonHref(type, currentPage, totalPages, baseUrl);
  const text = getButtonText(type);

  let finalClassName = getButtonClassName(type);
  if (disabled) {
    finalClassName = finalClassName + ' disabled';
  }

  // Если передан onPageChange, используем кнопку с обработчиком
  if (onPageChange) {
    const targetPage = type === 'first' ? 1 : type === 'prev' ? currentPage - 1 : type === 'next' ? currentPage + 1 : totalPages;
    return (
      <button
        className={finalClassName}
        onClick={() => onPageChange(targetPage)}
        disabled={disabled}
        style={{ marginLeft: '4px', marginRight: '4px' }}
      >
        {text}
      </button>
    );
  }

  if (disabled) {
    return (
      <a
        className={finalClassName}
        aria-disabled={true}
        tabIndex={-1}
      >
        {text}
      </a>
    );
  }

  return (
    <a
      className={finalClassName}
      href={href}
    >
      {text}
    </a>
  );
};

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
