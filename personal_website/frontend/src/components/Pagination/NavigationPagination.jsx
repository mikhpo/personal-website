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
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 *
 * @return {JSX.Element} Элемент навигационной пагинации
 */
const NavigationPagination = ({ currentPage, totalPages, baseUrl }) => {
  return (
    <span className="step-links">
      <div>
        {currentPage > 1 && (
          <>
            {renderNavigationButton('first', currentPage, totalPages, baseUrl)}
            {renderNavigationButton('prev', currentPage, totalPages, baseUrl)}
          </>
        )}

        <PageInfo
          currentPage={currentPage}
          totalPages={totalPages}
        />

        {currentPage < totalPages && (
          <>
            {renderNavigationButton('next', currentPage, totalPages, baseUrl)}
            {renderNavigationButton('last', currentPage, totalPages, baseUrl)}
          </>
        )}
      </div>
    </span>
  );
};

NavigationPagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
};

export default NavigationPagination;
