import React from 'react';
import PropTypes from 'prop-types';
import PageInfo from '@components/Pagination/PageInfo';
import { renderNavigationButton } from '@components/Pagination/utils/paginationRenderers';

/**
 * Компонент навигационной пагинации
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
 *
 * @return {JSX.Element} Элемент навигационной пагинации
 */
const NavigationPagination = ({
  currentPage,
  totalPages,
  hasNext,
  hasPrevious,
  onPageChange,
  onNext,
  onPrevious,
  baseUrl,
}) => {
  return (
    <span className="step-links">
      <div>
        {(currentPage > 1 || hasPrevious) && (
          <>
            {renderNavigationButton('first', currentPage, totalPages, baseUrl, onPageChange)}
            {onPrevious ? (
              <button
                className="btn btn-outline-dark me-1"
                onClick={() => onPrevious()}
                disabled={!hasPrevious}
              >
                предыдущая
              </button>
            ) : (
              renderNavigationButton('prev', currentPage, totalPages, baseUrl, onPageChange)
            )}
          </>
        )}

        <PageInfo
          currentPage={currentPage}
          totalPages={totalPages}
        />

        {(currentPage < totalPages || hasNext) && (
          <>
            {onNext ? (
              <button
                className="btn btn-outline-dark ms-1"
                onClick={() => onNext()}
                disabled={!hasNext}
              >
                следующая
              </button>
            ) : (
              renderNavigationButton('next', currentPage, totalPages, baseUrl, onPageChange)
            )}
            {renderNavigationButton('last', currentPage, totalPages, baseUrl, onPageChange)}
          </>
        )}
      </div>
    </span>
  );
};

NavigationPagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  hasNext: PropTypes.bool,
  hasPrevious: PropTypes.bool,
  onPageChange: PropTypes.func,
  onNext: PropTypes.func,
  onPrevious: PropTypes.func,
  baseUrl: PropTypes.string,
};

NavigationPagination.defaultProps = {
  hasNext: false,
  hasPrevious: false,
  onPageChange: undefined,
  onNext: undefined,
  onPrevious: undefined,
  baseUrl: '',
};

export default NavigationPagination;
