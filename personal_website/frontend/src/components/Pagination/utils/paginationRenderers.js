/**
 * Утилиты для рендеринга элементов пагинации
 */

import React from 'react';
import { Pagination as BSPagination } from 'react-bootstrap';
import { getPageUrl } from './paginationHelpers';
import { getButtonText, getButtonClassName, isButtonDisabled, getButtonHref } from './buttonStates';

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
 * @return {JSX.Element} Навигационная кнопка
 */
export const renderNavigationButton = (type, currentPage, totalPages, baseUrl) => {
  const disabled = isButtonDisabled(type, currentPage, totalPages);
  const href = getButtonHref(type, currentPage, totalPages, baseUrl);
  const text = getButtonText(type);
  const className = getButtonClassName(type);

  return (
    <a
      className={className}
      href={href}
      {...(disabled ? { disabled: true } : {})}
    >
      {text}
    </a>
  );
};
