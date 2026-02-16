import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Navbar from '@components/Navbar/Navbar';
import BrandSection from './BrandSection';
import NavLink from './NavLink';
import OffcanvasTrigger from './OffcanvasTrigger';
import UserAuthSection from './UserAuthSection';

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
          { url: '#', text: 'Тэги', offcanvas: true },
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

  /**
   * Тест проверяет, что кнопка "Тэги" в выпадающем меню галереи
   * имеет атрибут offcanvas и открывает offcanvas панель
   *
   * @function
   * @name handles-tags-offcanvas-button-correctly
   */
  test('корректно обрабатывает кнопку offcanvas для тегов', () => {
    // Мокируем window.bootstrap
    const mockOffcanvasInstance = {
      show: jest.fn(),
    };

    const mockBootstrap = {
      Offcanvas: {
        getOrCreateInstance: jest.fn(() => mockOffcanvasInstance),
      },
    };

    Object.defineProperty(window, 'bootstrap', {
      value: mockBootstrap,
      writable: true,
    });

    // Мокируем document.getElementById
    const mockOffcanvasElement = document.createElement('div');
    mockOffcanvasElement.id = 'tagsOffcanvas';
    document.getElementById = jest.fn(() => mockOffcanvasElement);

    const props = {
      ...defaultProps,
      userAuthenticated: true,
      userName: 'testuser',
    };

    render(<Navbar {...props} />);

    // Сначала находим и кликаем на кнопку "Галерея", чтобы открыть dropdown
    const galleryDropdown = screen.getByText('Галерея');
    expect(galleryDropdown).toBeInTheDocument();

    // Имитируем hover или клик для открытия dropdown
    fireEvent.click(galleryDropdown);

    // Теперь кнопка "Тэги" должна стать видимой
    const tagsButton = screen.getByText('Тэги');
    expect(tagsButton).toBeInTheDocument();
    expect(tagsButton).toHaveAttribute('href', '#');

    // Симулируем клик по кнопке
    fireEvent.click(tagsButton);

    // Проверяем, что были вызваны соответствующие функции
    expect(document.getElementById).toHaveBeenCalledWith('tagsOffcanvas');
    expect(mockBootstrap.Offcanvas.getOrCreateInstance).toHaveBeenCalledWith(mockOffcanvasElement);
    expect(mockOffcanvasInstance.show).toHaveBeenCalled();
  });
});

// Тесты для BrandSection компонента
describe('BrandSection', () => {
  /**
   * Тест проверяет корректность отображения секции бренда
   *
   * Проверяет наличие:
   * - Ссылки с названием бренда
   * - Корректного URL для ссылки бренда
   *
   * @function
   * @name renders-brand-with-correct-properties
   */
  test('рендерит бренд с корректными свойствами', () => {
    const props = {
      brandName: 'Мой сайт',
      brandUrl: '/',
    };

    render(<BrandSection {...props} />);

    const brandLink = screen.getByText('Мой сайт');
    expect(brandLink).toBeInTheDocument();
    expect(brandLink).toHaveAttribute('href', '/');
  });
});

// Тесты для NavLink компонента
describe('NavLink', () => {
  /**
   * Тест проверяет корректность отображения обычной навигационной ссылки
   *
   * Проверяет наличие:
   * - Текста ссылки
   * - Корректного URL для ссылки
   * - Отсутствие класса active у неактивной ссылки
   *
   * @function
   * @name renders-regular-link
   */
  test('рендерит обычную ссылку', () => {
    const props = {
      link: {
        url: '/about',
        text: 'О нас',
        active: false,
      },
    };

    render(<NavLink {...props} />);

    const navLink = screen.getByText('О нас');
    expect(navLink).toBeInTheDocument();
    expect(navLink).toHaveAttribute('href', '/about');
    expect(navLink).not.toHaveClass('active');
  });

  /**
   * Тест проверяет корректность отображения активной навигационной ссылки
   *
   * Проверяет наличие:
   * - Текста ссылки
   * - Наличия класса active у активной ссылки
   *
   * @function
   * @name renders-active-link
   */
  test('рендерит активную ссылку', () => {
    const props = {
      link: {
        url: '/',
        text: 'Главная',
        active: true,
      },
    };

    render(<NavLink {...props} />);

    const navLink = screen.getByText('Главная');
    expect(navLink).toBeInTheDocument();
    expect(navLink).toHaveClass('active');
  });
});

// Тесты для UserAuthSection компонента
describe('UserAuthSection', () => {
  /**
   * Тест проверяет корректность отображения элементов
   * для неавторизованного пользователя
   *
   * Проверяет наличие:
   * - Ссылки для регистрации
   * - Кнопки для входа
   *
   * @function
   * @name renders-elements-for-unauthenticated-user
   */
  test('рендерит элементы для неавторизованного пользователя', () => {
    const props = {
      userAuthenticated: false,
    };

    render(<UserAuthSection {...props} />);

    expect(screen.getByText('Войти')).toBeInTheDocument();
    expect(screen.getByText('Регистрация')).toBeInTheDocument();
  });

  /**
   * Тест проверяет корректность отображения элементов
   * для авторизованного пользователя
   *
   * Проверяет наличие:
   * - Информации о текущем пользователе
   * - Кнопки для выхода
   * - Отсутствие ссылок для аутентификации
   *
   * @function
   * @name renders-elements-for-authenticated-user
   */
  test('рендерит элементы для авторизованного пользователя', () => {
    const props = {
      userAuthenticated: true,
      userName: 'testuser',
    };

    render(<UserAuthSection {...props} />);

    expect(screen.getByText(/Вы вошли как testuser/)).toBeInTheDocument();
    expect(screen.getByText('Выйти')).toBeInTheDocument();
  });

  /**
   * Тест проверяет отображение ссылки администрирования
   * для пользователя с правами staff
   *
   * Проверяет наличие:
   * - Ссылки на административную панель
   *
   * @function
   * @name renders-admin-link-for-staff-user
   */
  test('рендерит ссылку администрирования для staff пользователя', () => {
    const props = {
      userAuthenticated: true,
      userName: 'staffuser',
      userIsStaff: true,
    };

    render(<UserAuthSection {...props} />);

    expect(screen.getByText('Администрирование')).toBeInTheDocument();
  });
});

// Тесты для OffcanvasTrigger компонента
describe('OffcanvasTrigger', () => {
  /**
   * Тест проверяет корректность отображения элемента меню
   * с offcanvas триггером
   *
   * Проверяет:
   * - Наличие элемента меню с текстом
   * - Корректность открытия offcanvas панели при клике
   *
   * @function
   * @name renders-offcanvas-trigger-menu-item
   */
  test('рендерит элемент меню с offcanvas триггером', () => {
    // Мокируем window.bootstrap
    const mockOffcanvasInstance = {
      show: jest.fn(),
    };

    const mockBootstrap = {
      Offcanvas: {
        getOrCreateInstance: jest.fn(() => mockOffcanvasInstance),
      },
    };

    Object.defineProperty(window, 'bootstrap', {
      value: mockBootstrap,
      writable: true,
    });

    // Мокируем document.getElementById
    const mockOffcanvasElement = document.createElement('div');
    mockOffcanvasElement.id = 'tagsOffcanvas';
    document.getElementById = jest.fn(() => mockOffcanvasElement);

    const props = {
      item: {
        text: 'Тэги',
      },
    };

    render(<OffcanvasTrigger {...props} />);

    const offcanvasTrigger = screen.getByText('Тэги');
    expect(offcanvasTrigger).toBeInTheDocument();

    // Симулируем клик по кнопке
    fireEvent.click(offcanvasTrigger);

    // Проверяем, что были вызваны соответствующие функции
    expect(document.getElementById).toHaveBeenCalledWith('tagsOffcanvas');
    expect(mockBootstrap.Offcanvas.getOrCreateInstance).toHaveBeenCalledWith(mockOffcanvasElement);
    expect(mockOffcanvasInstance.show).toHaveBeenCalled();
  });
});
