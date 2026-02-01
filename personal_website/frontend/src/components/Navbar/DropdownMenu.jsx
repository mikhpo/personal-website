import React from 'react';
import PropTypes from 'prop-types';
import { NavDropdown } from 'react-bootstrap';
import OffcanvasTrigger from './OffcanvasTrigger';

/**
 * Компонент выпадающего меню
 *
 * @param {Object} props - Свойства компонента
 * @param {Object} props.link - Объект ссылки с dropdown элементами
 * @param {string} props.link.url - URL ссылки
 * @param {string} props.link.text - Текст ссылки
 * @param {boolean} props.link.active - Признак активной ссылки
 * @param {Array} props.link.dropdown - Массив элементов выпадающего меню
 * @param {boolean} props.userIsStaff - Признак принадлежности пользователя к staff
 *
 * @return {JSX.Element} Элемент выпадающего меню
 */
const DropdownMenu = ({ link, userIsStaff }) => {
  return (
    <NavDropdown
      title={link.text}
      id={`nav-dropdown-${link.url}`}
      active={link.active}
    >
      {link.dropdown.map((item) => {
        // Обработка offcanvas кнопки для тегов
        if (item.offcanvas) {
          return (
            <OffcanvasTrigger
              key={item.text}
              item={item}
            />
          );
        }

        // Обычные ссылки
        return (
          <NavDropdown.Item key={item.url} href={item.url}>
            {item.text}
          </NavDropdown.Item>
        );
      })}
      {userIsStaff && (
        <>
          <NavDropdown.Divider />
          <NavDropdown.Item href="/gallery/upload/">Загрузка</NavDropdown.Item>
        </>
      )}
    </NavDropdown>
  );
};

DropdownMenu.propTypes = {
  link: PropTypes.shape({
    url: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    active: PropTypes.bool,
    dropdown: PropTypes.arrayOf(
      PropTypes.shape({
        url: PropTypes.string,
        text: PropTypes.string.isRequired,
        offcanvas: PropTypes.bool,
      })
    ).isRequired,
  }).isRequired,
  userIsStaff: PropTypes.bool,
};

DropdownMenu.defaultProps = {
  userIsStaff: false,
};

export default DropdownMenu;
