import React from 'react';
import PropTypes from 'prop-types';
import NavLink from './NavLink';
import DropdownMenu from './DropdownMenu';

/**
 * Компонент для отображения списка навигационных ссылок
 *
 * @param {Object} props - Свойства компонента
 * @param {Array} props.links - Массив объектов ссылок навигации
 * @param {boolean} props.userIsStaff - Признак принадлежности пользователя к staff
 *
 * @return {JSX.Element} Элемент списка навигационных ссылок
 */
const NavLinksMapper = ({ links, userIsStaff }) => {
  return (
    <>
      {links.map((link) => {
        // Обработка элементов с выпадающим меню
        if (link.dropdown) {
          return (
            <DropdownMenu
              key={link.url}
              link={link}
              userIsStaff={userIsStaff}
            />
          );
        }

        // Обычные ссылки
        return (
          <NavLink
            key={link.url}
            link={link}
          />
        );
      })}
    </>
  );
};

NavLinksMapper.propTypes = {
  links: PropTypes.arrayOf(
    PropTypes.shape({
      url: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      active: PropTypes.bool,
      dropdown: PropTypes.arrayOf(
        PropTypes.shape({
          url: PropTypes.string,
          text: PropTypes.string.isRequired,
          offcanvas: PropTypes.bool,
        })
      ),
    })
  ).isRequired,
  userIsStaff: PropTypes.bool,
};

NavLinksMapper.defaultProps = {
  userIsStaff: false,
};

export default NavLinksMapper;
