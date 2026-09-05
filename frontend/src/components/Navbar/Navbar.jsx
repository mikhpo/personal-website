import React from 'react';
import PropTypes from 'prop-types';
import { Navbar as BSNavbar, Nav, Container } from 'react-bootstrap';
import NavItems from '@components/Navbar/NavItems';
import UserAuthSection from '@components/Navbar/UserAuthSection';
import SearchForm from '@components/Search/SearchForm';

/**
 * Компонент навигационной панели
 * Повторяет функциональность templates/navbar.html
 * Между ссылками навигации и секцией авторизации содержит
 * форму общего поиска, ведущую на /main/search/
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
            <NavItems links={links} userIsStaff={userIsStaff} />
          </Nav>
          {/* Отступ me-lg-3 отделяет кнопку поиска от секции авторизации, my-2/my-lg-0 - интервалы в гамбургер-меню */}
          <div className="me-lg-3 my-2 my-lg-0">
            <SearchForm targetUrl="/main/search/" placeholder="Поиск по сайту..." />
          </div>
          <UserAuthSection
            userAuthenticated={userAuthenticated}
            userName={userName}
            userIsStaff={userIsStaff}
          />
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
