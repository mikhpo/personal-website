import React from 'react';
import PropTypes from 'prop-types';
import { Nav } from 'react-bootstrap';

/**
 * Компонент секции аутентификации пользователя
 *
 * @param {Object} props - Свойства компонента
 * @param {boolean} props.userAuthenticated - Признак аутентификации пользователя
 * @param {string} props.userName - Имя аутентифицированного пользователя
 * @param {boolean} props.userIsStaff - Признак принадлежности пользователя к staff
 *
 * @return {JSX.Element} Элемент секции аутентификации пользователя
 */
const UserAuthSection = ({ userAuthenticated, userName, userIsStaff }) => {
  return (
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
  );
};

UserAuthSection.propTypes = {
  userAuthenticated: PropTypes.bool.isRequired,
  userName: PropTypes.string,
  userIsStaff: PropTypes.bool,
};

UserAuthSection.defaultProps = {
  userName: '',
  userIsStaff: false,
};

export default UserAuthSection;
