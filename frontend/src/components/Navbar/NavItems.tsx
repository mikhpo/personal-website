import React from 'react';
import { Nav, NavDropdown } from 'react-bootstrap';

/** Элемент выпадающего меню навигации. */
export interface NavDropdownItem {
  /** URL элемента меню; отсутствует у элементов, открывающих offcanvas-панель. */
  url?: string;
  text: string;
  /** Открывает offcanvas-панель вместо перехода по ссылке. */
  offcanvas?: boolean;
}

/** Ссылка навигационной панели: обычная или с выпадающим меню. */
export interface NavLink {
  url: string;
  text: string;
  active?: boolean;
  dropdown?: NavDropdownItem[];
}

/** Свойства компонента списка навигационных ссылок. */
export interface NavItemsProps {
  links: NavLink[];
  userIsStaff?: boolean;
}

/**
 * Компонент списка навигационных ссылок.
 *
 * Отображает навигационные ссылки в виде обычных ссылок или выпадающих меню.
 * Поддерживает отображение специальных элементов для администраторов.
 */
const NavItems = ({ links, userIsStaff = false }: NavItemsProps) => (
  <>
    {links.map((link) => {
      // Ссылка с выпадающим меню
      if (link.dropdown) {
        return (
          <NavDropdown key={link.url} title={link.text} id={`nav-dropdown-${link.url}`} active={link.active}>
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
        <Nav.Link key={link.url} href={link.url} className={link.active ? 'active' : ''}>
          {link.text}
        </Nav.Link>
      );
    })}
  </>
);

export default NavItems;
