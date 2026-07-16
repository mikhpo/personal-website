import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import NavItems from './NavItems';

/**
 * Тесты для компонента NavItems
 *
 * Данные тесты проверяют корректность отображения навигационных ссылок
 * в различных конфигурациях:
 * - Обычные ссылки
 * - Выпадающие меню
 * - Элементы offcanvas
 * - Дополнительные элементы для администраторов
 *
 * @module NavItems.test
 * @description Тестирование компонента NavItems
 */
describe('NavItems', () => {
  /**
   * Базовые свойства для тестирования компонента
   *
   * Содержит минимально необходимый набор данных для рендера компонента:
   * - Массив навигационных ссылок с различными типами (обычные ссылки и dropdown)
   * - Состояние принадлежности пользователя к staff (по умолчанию false)
   *
   * @type {Object}
   * @property {Array} links - Массив навигационных ссылок
   * @property {string} links[].url - URL ссылки
   * @property {string} links[].text - Текст ссылки
   * @property {boolean} links[].active - Признак активной ссылки
   * @property {Array} links[].dropdown - Массив элементов выпадающего меню (для галереи)
   * @property {boolean} userIsStaff - Признак принадлежности пользователя к staff
   */
  const defaultProps = {
    links: [
      { url: '/', text: 'Главная', active: true },
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
    userIsStaff: false,
  };

  /**
   * Тест проверяет корректность отображения обычных навигационных ссылок
   *
   * Проверяет наличие:
   * - Обычных навигационных ссылок
   * - Активной ссылки с соответствующим классом
   * - Неактивной ссылки без класса active
   */
  test('рендерит обычные навигационные ссылки', () => {
    render(<NavItems {...defaultProps} />);
    expect(screen.getByText('Главная')).toBeInTheDocument();
    expect(screen.getByText('Главная')).toHaveClass('active');
    expect(screen.getByText('Блог')).toBeInTheDocument();
    expect(screen.getByText('Блог')).not.toHaveClass('active');
  });

  /**
   * Тест проверяет корректность отображения выпадающего меню
   *
   * Проверяет наличие:
   * - Ссылки с выпадающим меню
   * - Элементов выпадающего меню
   * - Отсутствие элементов выпадающего меню по умолчанию (до открытия)
   */
  test('рендерит выпадающее меню', () => {
    render(<NavItems {...defaultProps} />);
    expect(screen.getByText('Галерея')).toBeInTheDocument();
    expect(screen.queryByText('Альбомы')).not.toBeInTheDocument();
    expect(screen.queryByText('Фотографии')).not.toBeInTheDocument();
    expect(screen.queryByText('Тэги')).not.toBeInTheDocument();
  });

  /**
   * Тест проверяет корректность отображения элементов выпадающего меню
   * после открытия меню
   *
   * Проверяет наличие:
   * - Элементов выпадающего меню после открытия
   * - Обычных ссылок в выпадающем меню
   */
  test('рендерит элементы выпадающего меню', () => {
    render(<NavItems {...defaultProps} />);

    // Симулируем открытие выпадающего меню
    const galleryDropdown = screen.getByText('Галерея');
    fireEvent.click(galleryDropdown);

    // После открытия меню элементы должны отображаться
    expect(screen.getByText('Альбомы')).toBeInTheDocument();
    expect(screen.getByText('Фотографии')).toBeInTheDocument();
    expect(screen.getByText('Тэги')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что элемент offcanvas
   * в выпадающем меню открывает боковую панель
   */
  test('корректно обрабатывает кнопку offcanvas', () => {
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

    render(<NavItems {...defaultProps} />);

    // Сначала находим и кликаем на кнопку "Галерея", чтобы открыть dropdown
    const galleryDropdown = screen.getByText('Галерея');
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

  /**
   * Тест проверяет отображение дополнительных элементов
   * для пользователя с правами staff
   *
   * Проверяет наличие:
   * - Разделителя в выпадающем меню
   * - Ссылки на загрузку фотографий
   */
  test('рендерит дополнительные элементы для staff пользователя', () => {
    const props = {
      ...defaultProps,
      userIsStaff: true,
    };

    render(<NavItems {...props} />);

    // Сначала находим и кликаем на кнопку "Галерея", чтобы открыть dropdown
    const galleryDropdown = screen.getByText('Галерея');
    fireEvent.click(galleryDropdown);

    // Проверяем наличие дополнительных элементов для staff
    expect(screen.getByText('Загрузка')).toBeInTheDocument();
  });

  /**
   * Тест проверяет, что дополнительные элементы для staff
   * не отображаются для обычного пользователя
   *
   * Проверяет отсутствие:
   * - Ссылки на загрузку фотографий
   */
  test('не рендерит дополнительные элементы для обычного пользователя', () => {
    const props = {
      ...defaultProps,
      userIsStaff: false,
    };

    render(<NavItems {...props} />);

    // Сначала находим и кликаем на кнопку "Галерея", чтобы открыть dropdown
    const galleryDropdown = screen.getByText('Галерея');
    fireEvent.click(galleryDropdown);

    // Проверяем отсутствие дополнительных элементов для обычного пользователя
    expect(screen.queryByText('Загрузка')).not.toBeInTheDocument();
  });
});
