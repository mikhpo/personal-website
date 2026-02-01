import React from 'react';
import PropTypes from 'prop-types';
import { Navbar as BSNavbar, Nav, NavDropdown, Container } from 'react-bootstrap';

/**
 * Компонент навигационной панели
 * Повторяет функциональность templates/navbar.html
 *
 * @param {Object} props - Свойства компонента
 * @param {string} props.brandName - Название бренда
 * @param {string} props.brandUrl - URL бренда
 * @param {Array} props.links - Ссылки навигации
 * @param {boolean} props.userAuthenticated - Признак аутентификации пользователя
 * @param {string} props.username - Имя пользователя
 * @param {boolean} props.userIsStaff - Признак staff пользователя
 * @return {JSX.Element} Элемент навигационной панели
 */
const Navbar = ({ brandName, brandUrl, links, userAuthenticated, username, userIsStaff }) => {
  return (
    <BSNavbar bg="dark" variant="dark" expand="lg">
      <Container>
        <BSNavbar.Brand href={brandUrl}>{brandName}</BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            {links.map((link) => {
              // Обработка dropdown для галереи
              if (link.dropdown) {
                return (
                  <NavDropdown
                    key={link.url}
                    title={link.text}
                    active={link.active}
                    href={link.url}
                  >
                    {link.dropdown.map((item) => (
                      <NavDropdown.Item key={item.url} href={item.url}>
                        {item.text}
                      </NavDropdown.Item>
                    ))}
                    {userIsStaff && (
                      <>
                        <NavDropdown.Divider />
                        <NavDropdown.Item href="/gallery/upload/">Загрузка</NavDropdown.Item>
                      </>
                    )}
                  </NavDropdown>
                );
              }

              // Обычная ссылка
              return (
                <Nav.Link key={link.url} href={link.url} active={link.active}>
                  {link.text}
                </Nav.Link>
              );
            })}
          </Nav>
          <Nav>
            {userAuthenticated ? (
              <>
                <Nav.Link disabled className="text-nowrap">
                  Вы вошли как {username}
                </Nav.Link>
                {userIsStaff && (
                  <Nav.Link href="/admin/" className="text-nowrap">
                    Администрирование
                  </Nav.Link>
                )}
                <Nav.Link href="/accounts/logout/">Выйти</Nav.Link>
              </>
            ) : (
              <>
                <Nav.Link href="/accounts/signup/" className="text-nowrap">
                  Регистрация
                </Nav.Link>
                <Nav.Link href="/accounts/login/">Войти</Nav.Link>
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
  username: PropTypes.string,
  userIsStaff: PropTypes.bool,
};

Navbar.defaultProps = {
  username: '',
  userIsStaff: false,
};

export default Navbar;
