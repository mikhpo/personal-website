import React from 'react';
import { Pagination as BSPagination } from 'react-bootstrap';
import { calculatePageRange } from '@components/Pagination/utils/paginationHelpers';
import {
  createFirstPageElements,
  createMainPageElements,
  createLastPageElements,
  renderPaginationItem,
  type PageElementType,
} from '@components/Pagination/utils/paginationRenderers';

/** Свойства компонента пагинации с номерами страниц. */
export interface NumbersPaginationProps {
  currentPage: number;
  totalPages: number;
  baseUrl: string;
}

/**
 * Компонент пагинации с номерами страниц.
 *
 * Создает элемент пагинации с номерами страниц, включая номера вокруг текущей
 * (не более 5), первую и последнюю страницу, многоточия при необходимости
 * и активный элемент для текущей страницы.
 */
const NumbersPagination = ({ currentPage, totalPages, baseUrl }: NumbersPaginationProps) => {
  const { startPage, endPage } = calculatePageRange(currentPage, totalPages);

  const createElement = (elementType: PageElementType, page?: number): React.ReactNode =>
    renderPaginationItem(elementType, page, currentPage, totalPages, baseUrl);

  const firstPageElements = createFirstPageElements(startPage, totalPages, baseUrl, createElement);
  const mainPageElements = createMainPageElements(startPage, endPage, currentPage, baseUrl, createElement);
  const lastPageElements = createLastPageElements(endPage, totalPages, baseUrl, createElement);

  const items = [...firstPageElements, ...mainPageElements, ...lastPageElements];

  return <BSPagination className="justify-content-center">{items}</BSPagination>;
};

export default NumbersPagination;
