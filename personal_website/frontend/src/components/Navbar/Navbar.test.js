import React from 'react';
import { render, screen } from '@testing-library/react';
import Navbar from './Navbar';

/**
 * Тесты для компонента навигационной панели
 *
 * Данные тесты проверяют корректность отображения навигационной панели
 * в различных состояниях пользователя:
 * - Для неавторизованного пользователя
 * - Для авторизованного пользователя
 * - Для пользователя с правами staff
 *
 * @module Navbar.test
 * @description Тестирование компонента Navbar
 */
describe('Navbar', () => {
  /**
   * Базовые свойства для тестирования компонента
   *
   * Содержит минимально необходимый набор данных для рендера компонента:
   * - Название бренда и URL главной страницы
   * - Массив навигационных ссылок с различными типами (обычные ссылки и dropdown)
   * - Состояние аутентификации пользователя (по умолчанию false)
   * - Признак принадлежности к staff (по умолчанию false)
   *
   * @type {Object}
   * @property {string} brandName - Название бренда сайта
   * @property {string} brandUrl - URL главной страницы сайта
   * @property {Array} links - Массив навигационных ссылок
   * @property {string} links[].url - URL ссылки
   * @property {string} links[].text - Текст ссылки
   * @property {boolean} links[].active - Признак активной ссылки
   * @property {Array} links[].dropdown - Массив элементов выпадающего меню (для галереи)
   * @property {boolean} userAuthenticated - Признак аутентификации пользователя
   * @property {boolean} userIsStaff - Признак принадлежности пользователя к staff
   */
  const defaultProps = {
    brandName: 'Мой сайт',
    brandUrl: '/',
    links: [
      { url: '/', text: 'Главная', active: false },
      { url: '/blog/', text: 'Блог', active: false },
      {
        url: '/gallery/',
        text: 'Галерея',
        active: false,
        dropdown: [
          { url: '/gallery/albums/', text: 'Альбомы' },
          { url: '/gallery/photos/', text: 'Фотографии' },
          { url: '/gallery/tags/', text: 'Тэги' },
        ]
      },
    ],
    userAuthenticated: false,
    userIsStaff: false,
  };

  /**
   * Тест проверяет корректность отображения навигационной панели
   * для неавторизованного пользователя
   *
   * Проверяет наличие:
   * - Названия бренда
   * - Основных навигационных ссылок (Главная, Блог, Галерея)
   * - Ссылок для аутентификации (Войти, Регистрация)
   * - Отсутствие элементов dropdown по умолчанию
   *
   * @function
   * @name renders-navigation-for-unauthenticated-user
   */
  test('рендерит навигацию для неавторизованного пользователя', () => {
    render(<Navbar {...defaultProps} />);

    expect(screen.getByText('Мой сайт')).toBeInTheDocument();
    expect(screen.getByText('Главная')).toBeInTheDocument();
    expect(screen.getByText('Блог')).toBeInTheDocument();
    expect(screen.getByText('Галерея')).toBeInTheDocument();
    expect(screen.getByText('Войти')).toBeInTheDocument();
    expect(screen.getByText('Регистрация')).toBeInTheDocument();

    // Проверяем, что dropdown элементы не отображаются по умолчанию
    expect(screen.queryByText('Альбомы')).not.toBeInTheDocument();
  });

  /**
   * Тест проверяет корректность отображения навигационной панели
   * для авторизованного пользователя
   *
   * Проверяет наличие:
   * - Информации о текущем пользователе
   * - Ссылки для выхода из аккаунта
   * - Отсутствие ссылок для аутентификации
   *
   * @function
   * @name renders-navigation-for-authenticated-user
   */
  test('рендерит навигацию для авторизованного пользователя', () => {
    const props = {
      ...defaultProps,
      userAuthenticated: true,
      userName: 'testuser',
    };

    render(<Navbar {...props} />);

    expect(screen.getByText(/Вы вошли как testuser/)).toBeInTheDocument();
    expect(screen.getByText('Выйти')).toBeInTheDocument();
    expect(screen.queryByText('Войти')).not.toBeInTheDocument();
  });

  /**
   * Тест проверяет отображение дополнительных элементов
   * для пользователя с правами staff
   *
   * Проверяет наличие ссылки на административную панель
   *
   * @function
   * @name renders-additional-elements-for-staff-user
   */
  test('рендерит дополнительные элементы для staff пользователя', () => {
    const props = {
      ...defaultProps,
      userAuthenticated: true,
      userIsStaff: true,
      userName: 'staffuser',
    };

    render(<Navbar {...props} />);

    expect(screen.getByText('Администрирование')).toBeInTheDocument();
  });
});
