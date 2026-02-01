import React from 'react';
import PropTypes from 'prop-types';
import { Pagination as BSPagination } from 'react-bootstrap';
import PageNumbers from './PageNumbers';
import NavigationControls from './NavigationControls';

/**
 * Компонент пагинации
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 *
 * @return {JSX.Element|null} Компонент пагинации или null, если страниц меньше 2
 *
 * @description
 * Компонент отображает элементы пагинации с учетом текущей страницы и общего количества страниц.
 * Отображает ссылки на страницы, учитывая максимальное количество видимых страниц (5).
 * Всегда отображает первую и последнюю страницу, добавляя многоточия при необходимости.
 */
const Pagination = ({ currentPage, totalPages, baseUrl }) => {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <BSPagination className="justify-content-center">
      <NavigationControls
        currentPage={currentPage}
        totalPages={totalPages}
        baseUrl={baseUrl}
        type="prev"
      />
      <PageNumbers
        currentPage={currentPage}
        totalPages={totalPages}
        baseUrl={baseUrl}
      />
      <NavigationControls
        currentPage={currentPage}
        totalPages={totalPages}
        baseUrl={baseUrl}
        type="next"
      />
    </BSPagination>
  );
};

Pagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
};

export default Pagination;
