import React from 'react';
import PropTypes from 'prop-types';
import PreviousButtons from './PreviousButtons';
import NextButtons from './NextButtons';
import PageInfo from './PageInfo';

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
        <PreviousButtons
          currentPage={currentPage}
          totalPages={totalPages}
          baseUrl={baseUrl}
        />

        <PageInfo
          currentPage={currentPage}
          totalPages={totalPages}
        />

        <NextButtons
          currentPage={currentPage}
          totalPages={totalPages}
          baseUrl={baseUrl}
        />
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
