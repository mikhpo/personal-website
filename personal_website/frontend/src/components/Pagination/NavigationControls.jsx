import React from 'react';
import PropTypes from 'prop-types';
import { renderNavigationButton } from './utils/paginationRenderers';

/**
 * Компонент для отображения кнопок навигации (Первая/Предыдущая/Следующая/Последняя)
 *
 * @param {Object} props - Свойства компонента
 * @param {number} props.currentPage - Текущая страница
 * @param {number} props.totalPages - Общее количество страниц
 * @param {string} props.baseUrl - Базовый URL для формирования ссылок
 * @param {string} props.type - Тип кнопки ('first', 'prev', 'next', 'last')
 *
 * @return {JSX.Element} Элемент управления навигацией
 */
const NavigationControls = ({ currentPage, totalPages, baseUrl, type }) => {
  return renderNavigationButton(type, currentPage, totalPages, baseUrl);
};

NavigationControls.propTypes = {
  currentPage: PropTypes.number.isRequired,
  totalPages: PropTypes.number.isRequired,
  baseUrl: PropTypes.string.isRequired,
  type: PropTypes.oneOf(['first', 'prev', 'next', 'last']).isRequired,
};

export default NavigationControls;
