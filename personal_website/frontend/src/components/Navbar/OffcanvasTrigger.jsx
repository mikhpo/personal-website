import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { NavDropdown } from 'react-bootstrap';

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
  const openOffcanvas = useCallback((offcanvasId) => {
    const offcanvas = document.getElementById(offcanvasId);
    if (offcanvas) {
      // Используем Bootstrap JS API для открытия offcanvas
      const bootstrap = window.bootstrap;
      if (bootstrap && bootstrap.Offcanvas) {
        const offcanvasInstance = bootstrap.Offcanvas.getOrCreateInstance(offcanvas);
        offcanvasInstance.show();
      } else {
        // Fallback если Bootstrap JS не доступен
        offcanvas.classList.add('show');
        offcanvas.style.visibility = 'visible';
        offcanvas.setAttribute('aria-modal', 'true');
        offcanvas.setAttribute('role', 'dialog');
        document.body.classList.add('offcanvas-open');
      }
    }
  }, []);

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
