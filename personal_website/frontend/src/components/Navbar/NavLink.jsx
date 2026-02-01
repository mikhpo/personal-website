import React from 'react';
import PropTypes from 'prop-types';
import { Nav } from 'react-bootstrap';

/**
 * Компонент отдельной навигационной ссылки
 *
 * @param {Object} props - Свойства компонента
 * @param {Object} props.link - Объект ссылки
 * @param {string} props.link.url - URL ссылки
 * @param {string} props.link.text - Текст ссылки
 * @param {boolean} props.link.active - Признак активной ссылки
 *
 * @return {JSX.Element} Элемент навигационной ссылки
 */
const NavLink = ({ link }) => {
  return (
    <Nav.Link
      href={link.url}
      className={link.active ? 'active' : ''}
    >
      {link.text}
    </Nav.Link>
  );
};

NavLink.propTypes = {
  link: PropTypes.shape({
    url: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    active: PropTypes.bool,
  }).isRequired,
};

NavLink.defaultProps = {
  link: {
    active: false,
  },
};

export default NavLink;
