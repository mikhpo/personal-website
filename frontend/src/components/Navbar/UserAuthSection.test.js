import React from 'react';
import { render, screen } from '@testing-library/react';
import UserAuthSection from './UserAuthSection';

/**
 * Тесты для компонента UserAuthSection
 *
 * Данные тесты проверяют корректность отображения элементов
 * секции аутентификации пользователя в различных состояниях:
 * - Для аутентифицированного пользователя
 * - Для неаутентифицированного пользователя
 * - Для пользователя со статусом staff
 *
 * @module UserAuthSection.test
 * @description Тестирование компонента UserAuthSection
 */
describe('UserAuthSection', () => {
  /**
   * Базовые свойства для тестирования компонента для аутентифицированного пользователя
   *
   * @type {Object}
   * @property {boolean} userAuthenticated - Признак аутентификации пользователя
   * @property {string} userName - Имя аутентифицированного пользователя
   * @property {boolean} userIsStaff - Признак принадлежности пользователя к staff
   */
  const authenticatedUserProps = {
    userAuthenticated: true,
    userName: 'Тестовый Пользователь',
    userIsStaff: false,
  };

  /**
   * Базовые свойства для тестирования компонента для пользователя со статусом staff
   *
   * @type {Object}
   * @property {boolean} userAuthenticated - Признак аутентификации пользователя
   * @property {string} userName - Имя аутентифицированного пользователя
   * @property {boolean} userIsStaff - Признак принадлежности пользователя к staff
   */
  const staffUserProps = {
    userAuthenticated: true,
    userName: 'Админ Пользователь',
    userIsStaff: true,
  };

  /**
   * Базовые свойства для тестирования компонента для неаутентифицированного пользователя
   *
   * @type {Object}
   * @property {boolean} userAuthenticated - Признак аутентификации пользователя
   * @property {string} userName - Имя аутентифицированного пользователя
   * @property {boolean} userIsStaff - Признак принадлежности пользователя к staff
   */
  const unauthenticatedUserProps = {
    userAuthenticated: false,
    userName: '',
    userIsStaff: false,
  };

  /**
   * Тест проверяет корректность отображения элементов
   * для аутентифицированного пользователя
   *
   * Проверяет наличие:
   * - Текста с именем пользователя
   * - Формы с кнопкой для выхода
   * - Отсутствие ссылок для регистрации и входа
   */
  test('рендерит элементы для аутентифицированного пользователя', () => {
    render(<UserAuthSection {...authenticatedUserProps} />);

    // Проверяем отображение имени пользователя
    expect(screen.getByText('Вы вошли как Тестовый Пользователь')).toBeInTheDocument();

    // Проверяем форму выхода: выход в Django выполняется запросом POST
    const logoutButton = screen.getByText('Выйти');
    expect(logoutButton).toBeInTheDocument();
    expect(logoutButton.closest('form')).toHaveAttribute('action', '/accounts/logout/');
    expect(logoutButton.closest('form')).toHaveAttribute('method', 'post');
    expect(logoutButton).toHaveAttribute('type', 'submit');

    // Проверяем отсутствие ссылок для регистрации и входа
    expect(screen.queryByText('Регистрация')).not.toBeInTheDocument();
    expect(screen.queryByText('Войти')).not.toBeInTheDocument();
  });

  /**
   * Тест проверяет корректность отображения элементов
   * для неаутентифицированного пользователя
   *
   * Проверяет наличие:
   * - Ссылки для регистрации
   * - Ссылки для входа
   * - Отсутствие текста с именем пользователя
   * - Отсутствие ссылки для выхода
   */
  test('рендерит элементы для неаутентифицированного пользователя', () => {
    render(<UserAuthSection {...unauthenticatedUserProps} />);

    // Проверяем наличие ссылки для регистрации
    expect(screen.getByText('Регистрация')).toBeInTheDocument();
    expect(screen.getByText('Регистрация')).toHaveAttribute('href', '/accounts/signup/');

    // Проверяем наличие ссылки для входа
    expect(screen.getByText('Войти')).toBeInTheDocument();
    expect(screen.getByText('Войти')).toHaveAttribute('href', '/accounts/login/');

    // Проверяем отсутствие текста с именем пользователя
    expect(screen.queryByText(/Вы вошли как/)).not.toBeInTheDocument();

    // Проверяем отсутствие ссылки для выхода
    expect(screen.queryByText('Выйти')).not.toBeInTheDocument();
  });

  /**
   * Тест проверяет корректность отображения ссылки администрирования
   * для пользователя со статусом staff
   *
   * Проверяет наличие:
   * - Ссылки на административную панель
   */
  test('рендерит ссылку администрирования для staff пользователя', () => {
    render(<UserAuthSection {...staffUserProps} />);

    // Проверяем наличие ссылки на административную панель
    expect(screen.getByText('Администрирование')).toBeInTheDocument();
    expect(screen.getByText('Администрирование')).toHaveAttribute('href', '/admin/');
  });

  /**
   * Тест проверяет отсутствие ссылки администрирования
   * для обычного аутентифицированного пользователя
   *
   * Проверяет отсутствие:
   * - Ссылки на административную панель
   */
  test('не рендерит ссылку администрирования для обычного пользователя', () => {
    render(<UserAuthSection {...authenticatedUserProps} />);

    // Проверяем отсутствие ссылки на административную панель
    expect(screen.queryByText('Администрирование')).not.toBeInTheDocument();
  });

  /**
   * Тест проверяет корректность отображения имени пользователя
   *
   * Проверяет:
   * - Что имя пользователя отображается корректно
   * - Что при пустом имени пользователя отображается корректно
   */
  test('корректно отображает имя пользователя', () => {
    // Тест с именем пользователя
    const { rerender } = render(<UserAuthSection {...authenticatedUserProps} />);
    expect(screen.getByText('Вы вошли как Тестовый Пользователь')).toBeInTheDocument();

    // Тест с пустым именем пользователя
    rerender(<UserAuthSection {...authenticatedUserProps} userName="" />);
    expect(screen.getByText(/Вы вошли как/)).toBeInTheDocument();
  });
});
