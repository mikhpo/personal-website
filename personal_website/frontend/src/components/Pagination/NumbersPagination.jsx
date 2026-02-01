import React from 'react';
import PropTypes from 'prop-types';
import PageNumbers from './PageNumbers';

/**
 * Компонент пагинации с номерами страниц
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 *
 * @return {JSX.Element} Элемент пагинации с номерами страниц
 */
const NumbersPagination = ({ currentPage, totalPages, baseUrl }) => {
  return (
    <PageNumbers
      currentPage={currentPage}
      totalPages={totalPages}
      baseUrl={baseUrl}
    />
  );
};

NumbersPagination.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
};

export default NumbersPagination;
