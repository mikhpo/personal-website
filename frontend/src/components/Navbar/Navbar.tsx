import React, { useState } from 'react';
import { Navbar as BSNavbar, Nav, Container } from 'react-bootstrap';
import NavItems, { type NavLink } from '@components/Navbar/NavItems';
import UserAuthSection from '@components/Navbar/UserAuthSection';
import ThemeToggle from '@components/Navbar/ThemeToggle';
import TagsOffcanvas from '@components/Gallery/Tags/TagsOffcanvas';
import SearchForm from '@components/Search/SearchForm';

/** Свойства компонента навигационной панели. */
export interface NavbarProps {
  /** Название бренда в левой части панели. */
  brandName: string;
  /** URL ссылки на главную страницу сайта. */
  brandUrl: string;
  /** Массив ссылок навигации. */
  links: NavLink[];
  /** Признак аутентификации пользователя. */
  userAuthenticated: boolean;
  /** Имя аутентифицированного пользователя. */
  userName?: string;
  /** Признак принадлежности пользователя к группе staff. */
  userIsStaff?: boolean;
}

/**
 * Компонент навигационной панели.
 *
 * Между ссылками навигации и секцией авторизации содержит форму общего
 * поиска, ведущую на /main/search/.
 */
const Navbar = ({ brandName, brandUrl, links, userAuthenticated, userName = '', userIsStaff = false }: NavbarProps) => {
  // Панель тегов открывается из выпадающего меню галереи и принадлежит Navbar:
  // offcanvas рендерится в portal, поэтому находится в конце дерева
  const [tagsOpen, setTagsOpen] = useState(false);

  return (
    // Без variant: цвета ссылок и фона задаются CSS-переменными Bootstrap
    // и автоматически адаптируются к активной теме (data-bs-theme на <html>)
    <BSNavbar bg="body-tertiary" expand="lg" className="shadow mb-5">
      <Container fluid>
        <BSNavbar.Brand href={brandUrl}>{brandName}</BSNavbar.Brand>
        <BSNavbar.Toggle aria-controls="basic-navbar-nav" />
        <BSNavbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <NavItems links={links} userIsStaff={userIsStaff} onOpenOffcanvas={() => setTagsOpen(true)} />
          </Nav>
          {/* Класс navbar-search задает отступ до секции авторизации, равный зазору внутри нее (navbar.css) */}
          <div className="navbar-search my-2 my-lg-0">
            <SearchForm targetUrl="/main/search/" placeholder="Поиск по сайту..." />
          </div>
          <ThemeToggle />
          <UserAuthSection userAuthenticated={userAuthenticated} userName={userName} userIsStaff={userIsStaff} />
        </BSNavbar.Collapse>
      </Container>
      <TagsOffcanvas show={tagsOpen} onHide={() => setTagsOpen(false)} />
    </BSNavbar>
  );
};

export default Navbar;
