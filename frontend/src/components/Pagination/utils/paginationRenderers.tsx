/**
 * Утилиты для рендеринга элементов пагинации.
 */

import React from 'react';
import { Pagination as BSPagination } from 'react-bootstrap';
import { getPageUrl } from '@components/Pagination/utils/paginationHelpers';
import {
  getButtonText,
  getButtonClassName,
  isButtonDisabled,
  getButtonHref,
  type NavigationButtonType,
} from '@components/Pagination/utils/buttonStates';

/** Тип элемента пагинации с номерами страниц. */
export type PageElementType = 'first-page' | 'ellipsis-start' | 'page' | 'ellipsis-end' | 'last-page';

/** Функция создания элемента пагинации в NumbersPagination. */
export type CreatePaginationElement = (elementType: PageElementType, page?: number) => React.ReactNode;

/**
 * Рендерит элемент пагинации с номерами страниц.
 */
export const renderPaginationItem = (
  elementType: PageElementType,
  page: number | undefined,
  currentPage: number,
  totalPages: number,
  baseUrl: string,
): React.ReactNode => {
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
      if (page === undefined) {
        return null;
      }
      return (
        <BSPagination.Item
          key={page}
          active={page === currentPage}
          href={page === currentPage ? undefined : getPageUrl(baseUrl, page)}
          aria-current={page === currentPage ? 'page' : undefined}
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
 * Рендерит навигационную кнопку.
 */
export const renderNavigationButton = (
  type: NavigationButtonType,
  currentPage: number,
  totalPages: number,
  baseUrl: string,
  onPageChange?: (page: number) => void,
): React.ReactNode => {
  const disabled = isButtonDisabled(type, currentPage, totalPages);
  const href = getButtonHref(type, currentPage, totalPages, baseUrl);
  const text = getButtonText(type);

  const finalClassName = getButtonClassName(type);

  // Если передан onPageChange, используем кнопку с обработчиком
  if (onPageChange) {
    const targetPage =
      type === 'first' ? 1 : type === 'prev' ? currentPage - 1 : type === 'next' ? currentPage + 1 : totalPages;
    return (
      <button className={finalClassName} onClick={() => onPageChange(targetPage)} disabled={disabled}>
        {text}
      </button>
    );
  }

  if (disabled) {
    return (
      <button className={finalClassName} disabled>
        {text}
      </button>
    );
  }

  return (
    <a className={finalClassName} href={href}>
      {text}
    </a>
  );
};

/**
 * Создает элемент первой страницы и многоточие в начале, если нужно.
 */
export const createFirstPageElements = (
  startPage: number,
  totalPages: number,
  createElement: CreatePaginationElement,
): React.ReactNode[] => {
  const items: React.ReactNode[] = [];

  if (startPage > 1) {
    items.push(createElement('first-page'));

    if (startPage > 2) {
      items.push(createElement('ellipsis-start'));
    }
  }

  return items;
};

/**
 * Создает элементы страниц в основном диапазоне.
 */
export const createMainPageElements = (
  startPage: number,
  endPage: number,
  currentPage: number,
  createElement: CreatePaginationElement,
): React.ReactNode[] => {
  const items: React.ReactNode[] = [];

  for (let i = startPage; i <= endPage; i++) {
    items.push(createElement('page', i));
  }

  return items;
};

/**
 * Создает многоточие и последнюю страницу в конце, если нужно.
 */
export const createLastPageElements = (
  endPage: number,
  totalPages: number,
  createElement: CreatePaginationElement,
): React.ReactNode[] => {
  const items: React.ReactNode[] = [];

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      items.push(createElement('ellipsis-end'));
    }
    items.push(createElement('last-page'));
  }

  return items;
};
