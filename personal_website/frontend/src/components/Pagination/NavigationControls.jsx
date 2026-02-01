import React from 'react';
import PropTypes from 'prop-types';
import { Pagination as BSPagination } from 'react-bootstrap';
import { getPageUrl } from './paginationUtils';

/**
 * Компонент для отображения кнопок навигации (Предыдущая/Следующая)
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 * @param {string} props.type - Тип кнопки ('prev' или 'next')
 *
 * @return {JSX.Element} Элемент управления навигацией
 */
const NavigationControls = ({ currentPage, totalPages, baseUrl, type }) => {
  if (type === 'prev') {
    return (
      <BSPagination.Prev
        disabled={currentPage === 1}
        href={currentPage > 1 ? getPageUrl(baseUrl, currentPage - 1) : undefined}
      />
    );
  }

  return (
    <BSPagination.Next
      disabled={currentPage === totalPages}
      href={currentPage < totalPages ? getPageUrl(baseUrl, currentPage + 1) : undefined}
    />
  );
};

NavigationControls.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
  type: PropTypes.oneOf(['prev', 'next']).isRequired,
};

export default NavigationControls;
