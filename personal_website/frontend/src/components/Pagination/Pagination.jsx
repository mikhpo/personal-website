import React from 'react';
import PropTypes from 'prop-types';
import NavigationPagination from '@components/Pagination/NavigationPagination';
import NumbersPagination from '@components/Pagination/NumbersPagination';

/**
 * Основной компонент пагинации
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 * @param {string} props.type - Тип пагинации ('navigation' или 'numbers')
 *
 * @return {JSX.Element|null} Компонент пагинации или null, если страниц меньше 2
 */
const Pagination = ({ currentPage, totalPages, baseUrl, type = 'navigation' }) => {
  if (totalPages <= 1) {
    return null;
  }

  const PaginationComponent = type === 'numbers' ? NumbersPagination : NavigationPagination;

  return (
    <div className="container">
      <div className="pagination">
        <PaginationComponent
          currentPage={currentPage}
          totalPages={totalPages}
          baseUrl={baseUrl}
        />
      </div>
      <br />
    </div>
  );
};

Pagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
  type: PropTypes.oneOf(['navigation', 'numbers']),
};

export default Pagination;
