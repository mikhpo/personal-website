/**
 * Тесты для компонента SeriesGrid.
 *
 * Проверяет корректность отображения списка серий с различными состояниями:
 * загрузка, ошибка, пустое состояние, успешное отображение списка.
 * Тесты используют моки для изоляции компонента от внешних зависимостей.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SeriesGrid from '@components/Main/SeriesGrid';

// Мокировать компонент SeriesCard для изоляции тестов
jest.mock('@components/Main/SeriesCard', () => ({
  __esModule: true,
  default: ({ series }) => (
    <div data-testid={`series-card-${series.id}`}>{series.name}</div>
  ),
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
      {messages.map((msg, index) => (
        <div key={index} data-testid={`alert-${msg.level}`}>
          {msg.message}
          {msg.actions}
        </div>
      ))}
    </div>
  ),
}));

describe('SeriesGrid', () => {
  // Тестовые данные серий
  const mockSeries = [
    {
      id: 1,
      name: 'Лангтанг-трек',
      slug: 'langtang-trek',
      description: 'Поход в Непале',
      image: '/media/blog/series/langtang.jpg',
    },
    {
      id: 2,
      name: 'Аннапурна',
      slug: 'annapurna',
      description: 'Поход вокруг Аннапурны',
      image: '/media/blog/series/annapurna.jpg',
    },
    {
      id: 3,
      name: 'Серия без изображения',
      slug: 'no-image',
      description: 'Не должна отображаться',
    },
  ];

  // Настройка мока fetch перед каждым тестом
  beforeEach(() => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ results: [] }),
      }),
    );
  });

  // Восстановление оригинального fetch после каждого теста
  afterEach(() => {
    jest.restoreAllMocks();
  });

  // Очистить моки перед каждым тестом
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Проверить отображение состояния загрузки.
   * Когда компонент загружает данные, должен отображаться компонент загрузки.
   */
  test('отображает состояние загрузки', () => {
    // Мокаем fetch чтобы он не завершался сразу
    global.fetch.mockImplementation(() => new Promise(() => {}));

    render(<SeriesGrid />);
    // Проверяем видимый текст (не visually-hidden)
    const visibleText = screen.getByText('Загрузка серий...', {
      selector: 'p',
    });
    expect(visibleText).toBeInTheDocument();
  });

  /**
   * Проверить отображение состояния ошибки.
   * Когда возникает ошибка загрузки, должен отображаться компонент ошибки.
   */
  test('отображает состояние ошибки', async () => {
    // Мокаем сетевую ошибку
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<SeriesGrid />);

    // Ждем завершения асинхронной операции
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });

    // Проверить, что кнопка повтора отображается
    const retryButton = screen.getByText('Повторить');
    expect(retryButton).toBeInTheDocument();

    // Проверить, что кнопка повтора вызывает повторную загрузку
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockSeries }),
    });

    userEvent.click(retryButton);

    // Ждем завершения повторной загрузки
    await waitFor(() => {
      expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение списка серий.
   * Когда API возвращает массив серий, должен отображаться список карточек.
   */
  test('отображает список серий', async () => {
    // Настроить мок API для возврата списка серий
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockSeries }),
    });

    render(<SeriesGrid />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
    });

    // Проверить, что только серии с изображениями отображаются
    expect(screen.getByTestId('series-card-1')).toBeInTheDocument();
    expect(screen.getByText('Лангтанг-трек')).toBeInTheDocument();
    expect(screen.getByTestId('series-card-2')).toBeInTheDocument();
    expect(screen.getByText('Аннапурна')).toBeInTheDocument();

    // Серия без изображения не должна отображаться
    expect(screen.queryByTestId('series-card-3')).not.toBeInTheDocument();
  });

  /**
   * Проверить правильную структуру сетки.
   * Компонент должен использовать правильные CSS классы для сетки Bootstrap.
   */
  test('использует правильную структуру сетки Bootstrap', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockSeries.slice(0, 2) }),
    });

    const renderResult = render(<SeriesGrid />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
    });

    // Проверить наличие контейнера
    const container = renderResult.container.querySelector('.container');
    expect(container).toBeInTheDocument();
    expect(container).toHaveAttribute('data-testid', 'series-grid-container');

    // Проверить наличие строки
    const row = renderResult.container.querySelector('.row');
    expect(row).toBeInTheDocument();
    expect(row).toHaveClass('g-4', 'justify-content-center');

    // Проверить колонки
    const cols = renderResult.container.querySelectorAll('.col');
    // Должны быть только серии с изображениями (2 штуки)
    expect(cols.length).toBe(2);
  });

  /**
   * Проверить обработку ответа без поля results.
   * Компонент должен корректно обрабатывать прямой массив серий.
   */
  test('обрабатывает результат без results', async () => {
    // Мокаем ответ без поля results
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSeries,
    });

    render(<SeriesGrid />);

    // Ждем завершения асинхронной операции
    await waitFor(() => {
      expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
    });

    // Проверить, что серии с изображениями отображаются
    expect(screen.getByTestId('series-card-1')).toBeInTheDocument();
    expect(screen.queryByTestId('series-card-3')).not.toBeInTheDocument();
  });

  /**
   * Проверить обработку HTTP ошибок.
   * При получении ошибочного HTTP статуса должна устанавливаться ошибка.
   */
  test('обрабатывает HTTP ошибку', async () => {
    // Мокаем HTTP ошибку
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    render(<SeriesGrid />);

    // Ждем завершения асинхронной операции
    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки: 500')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение заголовка "Или серию".
   */
  test('отображает заголовок "Или серию"', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockSeries.slice(0, 1) }),
    });

    render(<SeriesGrid />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(screen.getByText('Или серию')).toBeInTheDocument();
    });
  });
});
