import React from 'react';
import PropTypes from 'prop-types';

/**
 * Компонент для отображения информации о текущей странице
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 *
 * @return {JSX.Element|null} Элемент с информацией о странице или null, если страниц мало
 */
const PageInfo = ({ currentPage, totalPages }) => {
  if (totalPages <= 1) {
    return null;
  }

  return (
    <span className="current mx-2">
      страница {currentPage} из {totalPages}
    </span>
  );
};

PageInfo.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
};

export default PageInfo;
