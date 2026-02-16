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
  // Не отображаем пагинацию, если страниц мало
  if (totalPages <= 1) {
    return null;
  }

  // Выбираем тип пагинации
  if (type === 'numbers') {
    return (
      <div className="container">
        <div className="pagination">
          <NumbersPagination
            currentPage={currentPage}
            totalPages={totalPages}
            baseUrl={baseUrl}
          />
        </div>
        <br />
      </div>
    );
  }

  // По умолчанию используем навигационную пагинацию
  return (
    <div className="container">
      <div className="pagination">
        <NavigationPagination
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
