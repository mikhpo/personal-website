import React from 'react';
import PropTypes from 'prop-types';
import { Nav, NavDropdown } from 'react-bootstrap';

/**
 * Компонент списка навигационных ссылок
 * 
 * Отображает навигационные ссылки в виде обычных ссылок или выпадающих меню.
 * Поддерживает отображение специальных элементов для администраторов.
 * 
 * @component
 * @example
 * const links = [
 *   { url: '/', text: 'Главная', active: true },
 *   { 
 *     url: '/gallery', 
 *     text: 'Галерея', 
 *     dropdown: [
 *       { url: '/gallery/albums', text: 'Альбомы' },
 *       { url: '/gallery/tags', text: 'Теги', offcanvas: true }
 *     ]
 *   }
 * ];
 * const userIsStaff = true;
 * return <NavItems links={links} userIsStaff={userIsStaff} />;
 * 
 * @param {Array<Object>} links - Массив объектов ссылок для отображения
 * @param {string} links[].url - URL ссылки
 * @param {string} links[].text - Текст ссылки
 * @param {boolean} [links[].active=false] - Флаг активности ссылки
 * @param {Array<Object>} [links[].dropdown] - Массив элементов выпадающего меню
 * @param {string} links[].dropdown[].url - URL элемента меню
 * @param {string} links[].dropdown[].text - Текст элемента меню
 * @param {boolean} [links[].dropdown[].offcanvas=false] - Флаг открытия offcanvas панели
 * @param {boolean} [userIsStaff=false] - Флаг принадлежности пользователя к администраторам
 * 
 * @return {JSX.Element} Компонент навигационных ссылок
 */
const NavItems = ({ links, userIsStaff }) => (
  <>
    {links.map((link) => {
      // Ссылка с выпадающим меню
      if (link.dropdown) {
        return (
          <NavDropdown
            key={link.url}
            title={link.text}
            id={`nav-dropdown-${link.url}`}
            active={link.active}
          >
            {link.dropdown.map((item) => {
              // Элемент для открытия offcanvas панели
              if (item.offcanvas) {
                return (
                  <NavDropdown.Item
                    key={item.text}
                    onClick={(e) => {
                      e.preventDefault();
                      const offcanvas = document.getElementById('tagsOffcanvas');
                      if (offcanvas && window.bootstrap?.Offcanvas) {
                        window.bootstrap.Offcanvas.getOrCreateInstance(offcanvas).show();
                      }
                    }}
                  >
                    {item.text}
                  </NavDropdown.Item>
                );
              }

              // Обычный элемент выпадающего меню
              return (
                <NavDropdown.Item key={item.url} href={item.url}>
                  {item.text}
                </NavDropdown.Item>
              );
            })}

            {/* Дополнительные элементы для администраторов */}
            {userIsStaff && (
              <>
                <NavDropdown.Divider />
                <NavDropdown.Item href="/gallery/upload/">Загрузка</NavDropdown.Item>
              </>
            )}
          </NavDropdown>
        );
      }

      // Обычная навигационная ссылка
      return (
        <Nav.Link
          key={link.url}
          href={link.url}
          className={link.active ? 'active' : ''}
        >
          {link.text}
        </Nav.Link>
      );
    })}
  </>
);

NavItems.propTypes = {
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

NavItems.defaultProps = {
  userIsStaff: false,
};

export default NavItems;
