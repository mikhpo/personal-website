import React from 'react';
import PropTypes from 'prop-types';
import { Pagination as BSPagination } from 'react-bootstrap';
import { getPageUrl, calculatePageRange } from './paginationUtils';

/**
 * Компонент для отображения номеров страниц в пагинации
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 *
 * @return {Array<JSX.Element>} Массив элементов пагинации
 *
 * @description
 * Создает массив элементов пагинации, включая:
 * - Номера страниц вокруг текущей (не более 5)
 * - Первая и последняя страница
 * - Многоточия при необходимости
 * - Активный элемент для текущей страницы
 */
const PageNumbers = ({ currentPage, totalPages, baseUrl }) => {
  const { startPage, endPage } = calculatePageRange(currentPage, totalPages);
  const pages = [];

  // Добавляем первую страницу и многоточие в начале, если нужно
  const addFirstPageWithEllipsis = () => {
    if (startPage > 1) {
      pages.push(
        <BSPagination.Item key={1} href={getPageUrl(baseUrl, 1)}>
          1
        </BSPagination.Item>
      );
      if (startPage > 2) {
        pages.push(<BSPagination.Ellipsis key="ellipsis-start" disabled />);
      }
    }
  };

  // Добавляем номера страниц в основном диапазоне
  const addMainPageNumbers = () => {
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <BSPagination.Item
          key={i}
          active={i === currentPage}
          href={i === currentPage ? undefined : getPageUrl(baseUrl, i)}
        >
          {i}
        </BSPagination.Item>
      );
    }
  };

  // Добавляем многоточие и последнюю страницу в конце, если нужно
  const addLastPageWithEllipsis = () => {
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push(<BSPagination.Ellipsis key="ellipsis-end" disabled />);
      }
      pages.push(
        <BSPagination.Item key={totalPages} href={getPageUrl(baseUrl, totalPages)}>
          {totalPages}
        </BSPagination.Item>
      );
    }
  };

  // Формируем структуру пагинации
  addFirstPageWithEllipsis();
  addMainPageNumbers();
  addLastPageWithEllipsis();

  return pages;
};

PageNumbers.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
};

export default PageNumbers;
