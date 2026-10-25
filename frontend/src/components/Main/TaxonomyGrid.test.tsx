/**
 * Тесты для компонента TaxonomyGrid.
 *
 * Проверяют отображение сеток справочников блога (категорий и серий)
 * во всех состояниях: загрузка, ошибка с повтором, пустое состояние,
 * фильтрация элементов без изображений и структура сетки Bootstrap.
 * Сервисы API подменяются автомоком jest.mock('@services').
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaxonomyGrid from '@components/Main/TaxonomyGrid';
import type { AlertMessage } from '@components/Alert/AlertList';
import type { components } from '@api-types/api-schema';

type Category = components['schemas']['Category'];
type Series = components['schemas']['Series'];

import { blogService as realBlogService } from '@services';

jest.mock('@services');

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

/** Свойства сетки категорий без функций. */
const categoryGridProps = {
  testId: 'category-grid-container',
  title: 'Выберите категорию',
  loadingMessage: 'Загрузка категорий...',
  emptyMessage: 'Нет доступных категорий',
};

/** Свойства сетки серий без функций. */
const seriesGridProps = {
  testId: 'series-grid-container',
  title: 'Или серию',
  loadingMessage: 'Загрузка серий...',
  emptyMessage: 'Нет доступных серий',
};

describe('TaxonomyGrid', () => {
  // Тестовые данные: третий элемент без изображения не должен отображаться
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
    { id: 3, name: 'Категория без изображения', slug: 'no-image', description: 'Не должна отображаться' },
  ] as Category[];

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
    { id: 3, name: 'Серия без изображения', slug: 'no-image', description: 'Не должна отображаться' },
  ] as Series[];

  const envelope = <T,>(results: T[]) => ({
    count: results.length,
    total_pages: 1,
    next: null,
    previous: null,
    results,
  });

  const blogService = jest.mocked(realBlogService);

  describe('сетка категорий', () => {
    // Стабильная ссылка функции загрузки: контракт хука useApiData
    const fetchCategories = jest.fn(async () => {
      const data = await blogService.getCategories();
      return data.results.filter((category) => category.image);
    });

    /** Полные свойства сетки категорий. */
    const props = {
      ...categoryGridProps,
      fetchFunction: fetchCategories,
      renderItem: (category: Category) => <div data-testid={`category-card-${category.id}`}>{category.name}</div>,
    };

    beforeEach(() => {
      fetchCategories.mockClear();
      blogService.getCategories.mockReset();
    });

    test('отображает состояние загрузки', () => {
      blogService.getCategories.mockImplementation(() => new Promise(() => {}));

      render(<TaxonomyGrid<Category> {...props} />);

      const visibleText = screen.getByText('Загрузка категорий...', { selector: 'p' });
      expect(visibleText).toBeInTheDocument();
    });

    test('отображает состояние ошибки и повторяет загрузку', async () => {
      blogService.getCategories
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(envelope(mockCategories));

      render(<TaxonomyGrid<Category> {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });

      const retryButton = screen.getByText('Повторить');
      expect(retryButton).toBeInTheDocument();

      await userEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByTestId('category-grid-container')).toBeInTheDocument();
      });
    });

    test('отображает пустое состояние', async () => {
      blogService.getCategories.mockResolvedValue(envelope([]));

      render(<TaxonomyGrid<Category> {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Нет доступных категорий')).toBeInTheDocument();
      });
    });

    test('отображает список категорий без элементов без изображений', async () => {
      blogService.getCategories.mockResolvedValue(envelope(mockCategories));

      render(<TaxonomyGrid<Category> {...props} />);

      await waitFor(() => {
        expect(screen.getByTestId('category-grid-container')).toBeInTheDocument();
      });

      expect(screen.getByTestId('category-card-1')).toBeInTheDocument();
      expect(screen.getByText('Разработка')).toBeInTheDocument();
      expect(screen.getByTestId('category-card-2')).toBeInTheDocument();
      expect(screen.getByText('Путешествия')).toBeInTheDocument();

      expect(screen.queryByTestId('category-card-3')).not.toBeInTheDocument();
    });

    test('отображает заголовок сетки', async () => {
      blogService.getCategories.mockResolvedValue(envelope(mockCategories.slice(0, 1)));

      render(<TaxonomyGrid<Category> {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Выберите категорию')).toBeInTheDocument();
      });
    });

    test('использует правильную структуру сетки Bootstrap', async () => {
      blogService.getCategories.mockResolvedValue(envelope(mockCategories.slice(0, 2)));

      const renderResult = render(<TaxonomyGrid<Category> {...props} />);

      await waitFor(() => {
        expect(screen.getByTestId('category-grid-container')).toBeInTheDocument();
      });

      const container = renderResult.container.querySelector('.container');
      expect(container).toBeInTheDocument();
      expect(container).toHaveAttribute('data-testid', 'category-grid-container');

      const row = renderResult.container.querySelector('.row');
      expect(row).toBeInTheDocument();
      expect(row).toHaveClass('g-4', 'justify-content-center');

      const cols = renderResult.container.querySelectorAll('.col');
      expect(cols.length).toBe(2);
    });
  });

  describe('сетка серий', () => {
    // Стабильная ссылка функции загрузки: контракт хука useApiData
    const fetchSeries = jest.fn(async () => {
      const data = await blogService.getSeries();
      return data.results.filter((series) => series.image);
    });

    /** Полные свойства сетки серий. */
    const props = {
      ...seriesGridProps,
      fetchFunction: fetchSeries,
      renderItem: (series: Series) => <div data-testid={`series-card-${series.id}`}>{series.name}</div>,
    };

    beforeEach(() => {
      fetchSeries.mockClear();
      blogService.getSeries.mockReset();
    });

    test('отображает состояние загрузки', () => {
      blogService.getSeries.mockImplementation(() => new Promise(() => {}));

      render(<TaxonomyGrid<Series> {...props} />);

      const visibleText = screen.getByText('Загрузка серий...', { selector: 'p' });
      expect(visibleText).toBeInTheDocument();
    });

    test('отображает состояние ошибки и повторяет загрузку', async () => {
      blogService.getSeries
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(envelope(mockSeries));

      render(<TaxonomyGrid<Series> {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });

      const retryButton = screen.getByText('Повторить');
      expect(retryButton).toBeInTheDocument();

      await userEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
      });
    });

    test('отображает список серий без элементов без изображений', async () => {
      blogService.getSeries.mockResolvedValue(envelope(mockSeries));

      render(<TaxonomyGrid<Series> {...props} />);

      await waitFor(() => {
        expect(screen.getByTestId('series-grid-container')).toBeInTheDocument();
      });

      expect(screen.getByTestId('series-card-1')).toBeInTheDocument();
      expect(screen.getByText('Лангтанг-трек')).toBeInTheDocument();
      expect(screen.getByTestId('series-card-2')).toBeInTheDocument();
      expect(screen.getByText('Аннапурна')).toBeInTheDocument();

      expect(screen.queryByTestId('series-card-3')).not.toBeInTheDocument();
    });

    test('отображает заголовок сетки', async () => {
      blogService.getSeries.mockResolvedValue(envelope(mockSeries.slice(0, 1)));

      render(<TaxonomyGrid<Series> {...props} />);

      await waitFor(() => {
        expect(screen.getByText('Или серию')).toBeInTheDocument();
      });
    });
  });
});
