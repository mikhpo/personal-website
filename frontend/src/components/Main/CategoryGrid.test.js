/**
 * Тесты для компонента CategoryGrid.
 *
 * Проверяет корректность отображения списка категорий с различными состояниями:
 * загрузка, ошибка, пустое состояние, успешное отображение списка.
 * Тесты используют моки для изоляции компонента от внешних зависимостей.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CategoryGrid from '@components/Main/CategoryGrid';

jest.mock('@services');

// Мокировать компонент CategoryCard для изоляции тестов
jest.mock('@components/Main/CategoryCard', () => ({
  __esModule: true,
  default: ({ category }) => <div data-testid={`category-card-${category.id}`}>{category.name}</div>,
}));

// Мокировать компоненты Spinner и AlertList
jest.mock('@components/Spinner/Spinner', () => ({
  __esModule: true,
  default: ({ message }) => <p>{message}</p>,
}));

jest.mock('@components/Alert/AlertList', () => ({
  __esModule: true,
  default: ({ messages }) => (
    <div>
      {messages.map((msg) => (
        <div key={`${msg.level}-${msg.message}`} data-testid={`alert-${msg.level}`}>
          {msg.message}
          {msg.actions}
        </div>
      ))}
    </div>
  ),
}));

describe('CategoryGrid', () => {
  // Тестовые данные категорий
  const mockCategories = [
    {
      id: 1,
      name: 'Разработка',
      slug: 'razrabotka',
      description: 'Статьи о разработке',
      image: '/media/blog/categories/dev.jpg',
    },
    {
      id: 2,
      name: 'Путешествия',
      slug: 'puteshestviya',
      description: 'Путешествия по миру',
      image: '/media/blog/categories/travel.jpg',
    },
    {
      id: 3,
      name: 'Категория без изображения',
      slug: 'no-image',
      description: 'Не должна отображаться',
    },
  ];

  const envelope = (results) => ({
    count: results.length,
    total_pages: 1,
    next: null,
    previous: null,
    results,
  });

  let blogService;

  beforeEach(() => {
    blogService = require('@services').blogService;
    blogService.getCategories.mockReset();
  });

  /**
   * Проверить отображение состояния загрузки.
   * Когда компонент загружает данные, должен отображаться компонент загрузки.
   */
  test('отображает состояние загрузки', () => {
    blogService.getCategories.mockImplementationOnce(() => new Promise(() => {}));

    render(<CategoryGrid />);
    // Проверяем видимый текст (не visually-hidden)
    const visibleText = screen.getByText('Загрузка категорий...', {
      selector: 'p',
    });
    expect(visibleText).toBeInTheDocument();
  });

  /**
   * Проверить отображение состояния ошибки.
   * Когда возникает ошибка загрузки, должен отображаться компонент ошибки.
   */
  test('отображает состояние ошибки', async () => {
    blogService.getCategories
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce(envelope(mockCategories));

    render(<CategoryGrid />);

    // Ждем завершения асинхронной операции
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });

    // Проверить, что кнопка повтора отображается и вызывает повторную загрузку
    const retryButton = screen.getByText('Повторить');
    expect(retryButton).toBeInTheDocument();

    userEvent.click(retryButton);

    // Ждем завершения повторной загрузки
    await waitFor(() => {
      expect(screen.getByTestId('category-grid-container')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение пустого состояния.
   * Когда API возвращает пустой список категорий без ошибок,
   * должен отображаться компонент пустого состояния.
   */
  test('отображает пустое состояние', async () => {
    blogService.getCategories.mockResolvedValueOnce(envelope([]));

    render(<CategoryGrid />);

    await waitFor(() => {
      expect(screen.getByText('Нет доступных категорий')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение списка категорий.
   * Когда API возвращает список категорий, должен отображаться список карточек.
   */
  test('отображает список категорий', async () => {
    blogService.getCategories.mockResolvedValueOnce(envelope(mockCategories));

    render(<CategoryGrid />);

    await waitFor(() => {
      expect(screen.getByTestId('category-grid-container')).toBeInTheDocument();
    });

    // Проверить, что только категории с изображениями отображаются
    expect(screen.getByTestId('category-card-1')).toBeInTheDocument();
    expect(screen.getByText('Разработка')).toBeInTheDocument();
    expect(screen.getByTestId('category-card-2')).toBeInTheDocument();
    expect(screen.getByText('Путешествия')).toBeInTheDocument();

    // Категория без изображения не должна отображаться
    expect(screen.queryByTestId('category-card-3')).not.toBeInTheDocument();
  });

  /**
   * Проверить отображение заголовка "Выберите категорию".
   */
  test('отображает заголовок "Выберите категорию"', async () => {
    blogService.getCategories.mockResolvedValueOnce(envelope(mockCategories.slice(0, 1)));

    render(<CategoryGrid />);

    await waitFor(() => {
      expect(screen.getByText('Выберите категорию')).toBeInTheDocument();
    });
  });
});
