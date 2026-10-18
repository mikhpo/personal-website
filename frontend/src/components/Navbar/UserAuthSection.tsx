import React from 'react';
import { Nav } from 'react-bootstrap';
import { getCsrfToken } from '@utils/cookies';

/** Свойства компонента секции аутентификации. */
export interface UserAuthSectionProps {
  userAuthenticated: boolean;
  userName?: string;
  userIsStaff?: boolean;
}

/**
 * Компонент секции аутентификации пользователя.
 */
const UserAuthSection = ({ userAuthenticated, userName = '', userIsStaff = false }: UserAuthSectionProps) => {
  return (
    <Nav>
      {userAuthenticated ? (
        <>
          <span className="navbar-text text-nowrap">
            <small>Вы вошли как {userName}</small>
          </span>
          {userIsStaff && (
            <a href="/admin/" className="navbar-text text-nowrap">
              Администрирование
            </a>
          )}
          {/* Выход в Django выполняется только запросом POST, поэтому оформлен формой с кнопкой.
              Отступ слева задает margin-right соседнего элемента с классом navbar-text (navbar.css) */}
          <form method="post" action="/accounts/logout/">
            <input type="hidden" name="csrfmiddlewaretoken" value={getCsrfToken() ?? ''} />
            <button type="submit" className="btn btn-outline-dark text-nowrap">
              Выйти
            </button>
          </form>
        </>
      ) : (
        <>
          <a href="/accounts/signup/" className="navbar-text text-nowrap">
            Регистрация
          </a>
          <a href="/accounts/login/" className="btn btn-outline-dark text-nowrap">
            Войти
          </a>
        </>
      )}
    </Nav>
  );
};

export default UserAuthSection;
