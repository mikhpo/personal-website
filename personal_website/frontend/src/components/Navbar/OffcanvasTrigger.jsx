import React from 'react';
import PropTypes from 'prop-types';
import { NavDropdown } from 'react-bootstrap';
import useOffcanvasHandler from './hooks/useOffcanvasHandler';

/**
 * Компонент триггера для открытия offcanvas панели
 *
 * @param {Object} props - Свойства компонента
 * @param {Object} props.item - Объект элемента меню с offcanvas триггером
 * @param {string} props.item.text - Текст элемента меню
 *
 * @return {JSX.Element} Элемент меню для открытия offcanvas панели
 */
const OffcanvasTrigger = ({ item }) => {
  const { openOffcanvas } = useOffcanvasHandler();

  const handleOffcanvasClick = (e) => {
    e.preventDefault();
    openOffcanvas('tagsOffcanvas');
  };

  return (
    <NavDropdown.Item
      onClick={handleOffcanvasClick}
    >
      {item.text}
    </NavDropdown.Item>
  );
};

OffcanvasTrigger.propTypes = {
  item: PropTypes.shape({
    text: PropTypes.string.isRequired,
  }).isRequired,
};

export default OffcanvasTrigger;
