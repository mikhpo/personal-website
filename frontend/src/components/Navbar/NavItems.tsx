import React from 'react';
import { Nav, NavDropdown } from 'react-bootstrap';

/**
 * Элемент выпадающего меню навигации: обычная ссылка или кнопка
 * открытия offcanvas-панели.
 */
export type NavDropdownItem =
  { text: string; url: string; offcanvas?: undefined } | { text: string; offcanvas: true; url?: undefined };

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
  /** Обработчик открытия offcanvas-панели тегов. */
  onOpenOffcanvas?: () => void;
}

/**
 * Компонент списка навигационных ссылок.
 *
 * Отображает навигационные ссылки в виде обычных ссылок или выпадающих меню.
 * Поддерживает отображение специальных элементов для администраторов.
 */
const NavItems = ({ links, userIsStaff = false, onOpenOffcanvas }: NavItemsProps) => (
  <>
    {links.map((link) => {
      // Ссылка с выпадающим меню
      if (link.dropdown) {
        return (
          <NavDropdown key={link.url} title={link.text} id={`nav-dropdown-${link.url}`} active={link.active}>
            {link.dropdown.map((item) => {
              // Элемент для открытия offcanvas панели; закрытие меню
              // выполняет сам Dropdown по факту выбора пункта
              if (item.offcanvas) {
                return (
                  <NavDropdown.Item key={item.text} as="button" onClick={() => onOpenOffcanvas?.()}>
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
