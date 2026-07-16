import React from 'react';
import PropTypes from 'prop-types';
import { Pagination as BSPagination } from 'react-bootstrap';
import { calculatePageRange } from '@components/Pagination/utils/paginationHelpers';
import {
  createFirstPageElements,
  createMainPageElements,
  createLastPageElements,
  renderPaginationItem
} from '@components/Pagination/utils/paginationRenderers';

/**
 * Компонент пагинации с номерами страниц
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 *
 * @return {JSX.Element} Элемент пагинации с номерами страниц
 *
 * @description
 * Создает элемент пагинации с номерами страниц, включая:
 * - Номера страниц вокруг текущей (не более 5)
 * - Первая и последняя страница
 * - Многоточия при необходимости
 * - Активный элемент для текущей страницы
 */
const NumbersPagination = ({ currentPage, totalPages, baseUrl }) => {
  const { startPage, endPage } = calculatePageRange(currentPage, totalPages);

  const createElement = (elementType, page) =>
    renderPaginationItem(elementType, page, currentPage, totalPages, baseUrl);

  const firstPageElements = createFirstPageElements(startPage, totalPages, baseUrl, createElement);
  const mainPageElements = createMainPageElements(startPage, endPage, currentPage, baseUrl, createElement);
  const lastPageElements = createLastPageElements(endPage, totalPages, baseUrl, createElement);

  const items = [...firstPageElements, ...mainPageElements, ...lastPageElements];

  return (
    <BSPagination className="justify-content-center">
      {items}
    </BSPagination>
  );
};

NumbersPagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
};

export default NumbersPagination;
