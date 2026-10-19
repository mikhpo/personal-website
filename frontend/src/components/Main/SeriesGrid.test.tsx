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
import type { AlertMessage } from '@components/Alert/AlertList';
import type { components } from '../../types/api-schema';

type Series = components['schemas']['Series'];

import { blogService as realBlogService } from '@services';

jest.mock('@services');

// Мокировать компонент SeriesCard для изоляции тестов
jest.mock('@components/Main/SeriesCard', () => ({
  __esModule: true,
  default: ({ series }: { series: Series }) => <div data-testid={`series-card-${series.id}`}>{series.name}</div>,
}));

// Мокировать компоненты Spinner и AlertList
jest.mock('@components/Spinner/Spinner', () => ({
  __esModule: true,
  default: ({ message }: { message?: string }) => <p>{message}</p>,
}));

jest.mock('@components/Alert/AlertList', () => ({
  __esModule: true,
  default: ({ messages }: { messages?: AlertMessage[] }) => (
    <div>
      {(messages ?? []).map((msg: AlertMessage) => (
        <div key={`${msg.level}-${msg.message}`} data-testid={`alert-${msg.level}`}>
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

  const envelope = (results: Series[]) => ({
    count: results.length,
    total_pages: 1,
    next: null,
    previous: null,
    results,
  });

  const blogService = jest.mocked(realBlogService);

  beforeEach(() => {
    blogService.getSeries.mockReset();
  });

  /**
   * Проверить отображение состояния загрузки.
   * Когда компонент загружает данные, должен отображаться компонент загрузки.
   */
  test('отображает состояние загрузки', () => {
    blogService.getSeries.mockImplementationOnce(() => new Promise(() => {}));

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
    blogService.getSeries.mockRejectedValueOnce(new Error('Network error')).mockResolvedValueOnce(envelope(mockSeries));

    render(<SeriesGrid />);

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
      expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение списка серий.
   * Когда API возвращает список серий, должен отображаться список карточек.
   */
  test('отображает список серий', async () => {
    blogService.getSeries.mockResolvedValueOnce(envelope(mockSeries));

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
    blogService.getSeries.mockResolvedValueOnce(envelope(mockSeries.slice(0, 2)));

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
   * Проверить обработку ошибок сервиса.
   */
  test('обрабатывает ошибку сервиса', async () => {
    blogService.getSeries.mockRejectedValueOnce(new Error('Ошибка загрузки: 500'));

    render(<SeriesGrid />);

    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки: 500')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение заголовка "Или серию".
   */
  test('отображает заголовок "Или серию"', async () => {
    blogService.getSeries.mockResolvedValueOnce(envelope(mockSeries.slice(0, 1)));

    render(<SeriesGrid />);

    // Ждем завершения загрузки
    await waitFor(() => {
      expect(screen.getByText('Или серию')).toBeInTheDocument();
    });
  });
});
