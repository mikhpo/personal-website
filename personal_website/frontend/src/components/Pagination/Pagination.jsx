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
 * @param {boolean} props.hasNext - Есть ли следующая страница
 * @param {boolean} props.hasPrevious - Есть ли предыдущая страница
 * @param {function} props.onPageChange - Обработчик изменения страницы
 * @param {function} props.onNext - Обработчик перехода на следующую страницу
 * @param {function} props.onPrevious - Обработчик перехода на предыдущую страницу
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 * @param {string} props.type - Тип пагинации ('navigation' или 'numbers')
 *
 * @return {JSX.Element|null} Компонент пагинации или null, если страниц меньше 2
 */
const Pagination = ({
  currentPage,
  totalPages,
  hasNext,
  hasPrevious,
  onPageChange,
  onNext,
  onPrevious,
  baseUrl,
  type = 'navigation',
}) => {
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
          hasNext={hasNext}
          hasPrevious={hasPrevious}
          onPageChange={onPageChange}
          onNext={onNext}
          onPrevious={onPrevious}
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
  hasNext: PropTypes.bool,
  hasPrevious: PropTypes.bool,
  onPageChange: PropTypes.func,
  onNext: PropTypes.func,
  onPrevious: PropTypes.func,
  baseUrl: PropTypes.string,
  type: PropTypes.oneOf(['navigation', 'numbers']),
};

Pagination.defaultProps = {
  hasNext: false,
  hasPrevious: false,
  onPageChange: undefined,
  onNext: undefined,
  onPrevious: undefined,
  baseUrl: '',
};

export default Pagination;