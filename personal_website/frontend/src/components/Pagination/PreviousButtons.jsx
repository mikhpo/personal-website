import React from 'react';
import PropTypes from 'prop-types';
import NavigationControls from '@components/Pagination/NavigationControls';

/**
 * Компонент для отображения кнопок "первая" и "предыдущая"
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 *
 * @return {JSX.Element|null} Элементы кнопок или null, если кнопки не нужны
 */
const PreviousButtons = ({ currentPage, totalPages, baseUrl }) => {
  if (currentPage <= 1) {
    return null;
  }

  return (
    <>
      <NavigationControls
        currentPage={currentPage}
        totalPages={totalPages}
        baseUrl={baseUrl}
        type="first"
      />
      <NavigationControls
        currentPage={currentPage}
        totalPages={totalPages}
        baseUrl={baseUrl}
        type="prev"
      />
    </>
  );
};

PreviousButtons.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
};

export default PreviousButtons;
