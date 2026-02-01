import React from 'react';
import PropTypes from 'prop-types';
import { Navbar as BSNavbar, Nav, NavDropdown, Container } from 'react-bootstrap';

/**
 * Компонент навигационной панели
 * Повторяет функциональность templates/navbar.html
 *
 * @param {Object} props - Свойства компонента
 * @param {string} props.brandName - Название бренда, отображаемое в левой части навигационной панели
 * @param {string} props.brandUrl - URL для ссылки на главную страницу сайта
 * @param {Array} props.links - Массив объектов ссылок навигации
 * @param {Object} props.links[].link - Объект ссылки навигации
 * @param {string} props.links[].link.url - URL ссылки
 * @param {string} props.links[].link.text - Текст ссылки
 * @param {boolean} props.links[].link.active - Признак активной ссылки
 * @param {Array} props.links[].link.dropdown - Массив элементов выпадающего меню (опционально)
 * @param {boolean} props.userAuthenticated - Признак аутентификации пользователя
 * @param {string} props.userName - Имя аутентифицированного пользователя
 * @param {boolean} props.userIsStaff - Признак принадлежности пользователя к группе staff
 *
 * @return {JSX.Element} Элемент навигационной панели Bootstrap
 *
 * @example
 * // Пример использования компонента с минимальными параметрами
 * <Navbar
 *   brandName="Мой сайт"
 *   brandUrl="/"
 *   links={[
 *     { url: "/", text: "Главная", active: true },
 *     { url: "/about", text: "О нас" }
 *   ]}
 *   userAuthenticated={false}
 * />
 *
 * @example
 * // Пример использования компонента с аутентифицированным пользователем
 * <Navbar
 *   brandName="Мой сайт"
 *   brandUrl="/"
 *   links={[
 *     { url: "/", text: "Главная" },
 *     {
 *       url: "/gallery",
 *       text: "Галерея",
 *       dropdown: [
 *         { url: "/gallery/photos", text: "Фотографии" },
 *         { url: "/gallery/albums", text: "Альбомы" }
 *       ]
 *     }
 *   ]}
 *   userAuthenticated={true}
 *   userName="Иван Иванов"
 *   userIsStaff={true}
 * />
 */
const Navbar = ({ brandName, brandUrl, links, userAuthenticated, userName, userIsStaff }) => {
  return (
    <BSNavbar bg="light" variant="light" expand="lg" className="shadow mb-5">
      <Container fluid>
        <BSNavbar.Brand href={brandUrl}>{brandName}</BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            {links.map((link) => {
              // Обработка элементов с выпадающим меню (галерея)
              if (link.dropdown) {
                // Всегда отображаем как dropdown для постоянного выравнивания
                return (
                  <NavDropdown
                    key={link.url}
                    title={link.text}
                    id={`nav-dropdown-${link.url}`}
                    active={link.active}
                  >
                    {link.dropdown.map((item) => {
                      // Обработка offcanvas кнопки для тегов
                      if (item.offcanvas) {
                        return (
                          <NavDropdown.Item
                            key={item.text}
                            onClick={(e) => {
                              e.preventDefault();
                              // Открыть offcanvas панель с тегами
                              const offcanvas = document.getElementById('tagsOffcanvas');
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
                            }}
                          >
                            {item.text}
                          </NavDropdown.Item>
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
              }

              // Обычные ссылки
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
          </Nav>
          <Nav>
            {userAuthenticated ? (
              <>
                <span className="navbar-text text-nowrap">
                  <small>Вы вошли как {userName}</small>
                </span>
                {userIsStaff && (
                  <a href="/admin/" className="navbar-text text-nowrap">Администрирование</a>
                )}
                <a href="/accounts/logout/" className="btn btn-outline-dark" role="button">Выйти</a>
              </>
            ) : (
              <>
                <a href="/accounts/signup/" className="navbar-text text-nowrap">Регистрация</a>
                <a href="/accounts/login/" className="btn btn-outline-dark" role="button">Войти</a>
              </>
            )}
          </Nav>
        </BSNavbar.Collapse>
      </Container>
    </BSNavbar>
  );
};

Navbar.propTypes = {
  brandName: PropTypes.string.isRequired,
  brandUrl: PropTypes.string.isRequired,
  links: PropTypes.arrayOf(
    PropTypes.shape({
      url: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      active: PropTypes.bool,
      dropdown: PropTypes.arrayOf(
        PropTypes.shape({
          url: PropTypes.string.isRequired,
          text: PropTypes.string.isRequired,
        })
      ),
    })
  ).isRequired,
  userAuthenticated: PropTypes.bool.isRequired,
  userName: PropTypes.string,
  userIsStaff: PropTypes.bool,
};

Navbar.defaultProps = {
  userName: '',
  userIsStaff: false,
};

export default Navbar;
