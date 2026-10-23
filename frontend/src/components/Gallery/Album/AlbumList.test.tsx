/**
 * Тесты для компонента AlbumList.
 *
 * Проверяет корректность отображения списка альбомов через сервис API
 * с различными состояниями: загрузка, ошибка, пустое состояние, фильтры
 * и структура masonry-сетки.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import AlbumList from './AlbumList';
import { galleryService as realGalleryService } from '@services';
import type { AlbumCardProps } from './AlbumCard';
import type { SpinnerProps } from '@components/Spinner/Spinner';
import type { AlertListProps } from '@components/Alert/AlertList';
import { makeAlbum, paginate } from '@test-utils';

jest.mock('@services');

// Мокировать компонент AlbumCard для изоляции тестов
jest.mock('./AlbumCard', () => ({
  __esModule: true,
  default: ({ album }: AlbumCardProps) => <div data-testid={`album-card-${album.id}`}>{album.name}</div>,
}));

// Мокировать компоненты Spinner и AlertList
jest.mock('@components/Spinner/Spinner', () => ({
  __esModule: true,
  default: ({ message }: SpinnerProps) => <p>{message}</p>,
}));

jest.mock('@components/Alert/AlertList', () => ({
  __esModule: true,
  default: ({ messages = [] }: AlertListProps) => (
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

// Объект мока создается один раз: стабильный setTotalPages не перезапускает
// эффект загрузки на каждой перерисовке (как и реальный хук usePagination)
const mockPaginationState = {
  currentPage: 1,
  totalPages: 1,
  hasNext: false,
  hasPrevious: false,
  nextPage: jest.fn(),
  previousPage: jest.fn(),
  goToPage: jest.fn(),
  setTotalPages: jest.fn(),
};

jest.mock('@hooks/usePagination', () => ({
  __esModule: true,
  default: () => mockPaginationState,
}));

jest.mock('@components/Pagination/Pagination', () => ({
  __esModule: true,
  default: () => null,
}));

describe('AlbumList', () => {
  // Тестовые данные альбомов
  const mockAlbums = [
    makeAlbum({
      id: 1,
      name: 'Альбом 1',
      slug: 'album-1',
      description: 'Описание альбома 1',
      cover_thumbnail_url: '/media/album1.jpg',
    }),
    makeAlbum({
      id: 2,
      name: 'Альбом 2',
      slug: 'album-2',
      description: 'Описание альбома 2',
      cover_thumbnail_url: '/media/album2.jpg',
    }),
    makeAlbum({
      id: 3,
      name: 'Альбом 3',
      slug: 'album-3',
    }),
  ];

  const galleryService = jest.mocked(realGalleryService);

  beforeEach(() => {
    galleryService.getAlbums.mockReset();
  });

  /**
   * Проверить отображение состояния загрузки.
   */
  test('отображает состояние загрузки', () => {
    galleryService.getAlbums.mockImplementationOnce(() => new Promise(() => {}));

    render(<AlbumList />);
    // Проверяем видимый текст (не visually-hidden)
    const visibleText = screen.getByText('Загрузка альбомов...', {
      selector: 'p',
    });
    expect(visibleText).toBeInTheDocument();
  });

  /**
   * Проверить отображение состояния ошибки.
   */
  test('отображает состояние ошибки', async () => {
    galleryService.getAlbums
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce(paginate(mockAlbums));

    render(<AlbumList />);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });

    // Проверить, что кнопка повтора отображается и вызывает повторную загрузку
    const retryButton = screen.getByText('Повторить');
    expect(retryButton).toBeInTheDocument();

    await userEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByTestId('album-list-container')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение пустого состояния.
   */
  test('отображает пустое состояние', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate([]));

    render(<AlbumList />);

    await waitFor(() => {
      expect(screen.getByText('Нет доступных альбомов')).toBeInTheDocument();
    });
  });

  /**
   * Проверить отображение списка альбомов.
   */
  test('отображает список альбомов', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate(mockAlbums));

    render(<AlbumList />);

    await waitFor(() => {
      expect(screen.getByTestId('album-list-container')).toBeInTheDocument();
    });

    mockAlbums.forEach((album) => {
      expect(screen.getByTestId(`album-card-${album.id}`)).toBeInTheDocument();
      expect(screen.getByText(album.name)).toBeInTheDocument();
    });
  });

  /**
   * Проверить запрос первой страницы без фильтров.
   */
  test('запрашивает первую страницу без фильтров', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate([]));

    render(<AlbumList />);

    await waitFor(() => {
      expect(galleryService.getAlbums).toHaveBeenCalledWith({ page: 1 });
    });
  });

  /**
   * Проверить передачу слага тега в параметры запроса.
   */
  test('передаёт слаг тега в параметры запроса', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate([]));

    render(<AlbumList tagSlug="example-tag" />);

    await waitFor(() => {
      expect(galleryService.getAlbums).toHaveBeenCalledWith({ tags__slug: 'example-tag', page: 1 });
    });
  });

  /**
   * Проверить передачу поискового запроса в параметры выборки.
   */
  test('передаёт поисковый запрос в параметры выборки', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate([]));

    render(<AlbumList search="sunset" />);

    await waitFor(() => {
      expect(galleryService.getAlbums).toHaveBeenCalledWith({ search: 'sunset', page: 1 });
    });
  });

  /**
   * Проверить сообщение о пустом результате при активном поиске.
   */
  test('отображает сообщение с запросом при пустом результате поиска', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate([]));

    render(<AlbumList search="sunset" />);

    await waitFor(() => {
      expect(screen.getByText('По запросу "sunset" ничего не найдено')).toBeInTheDocument();
    });
  });

  /**
   * Проверить правильную структуру masonry-сетки.
   */
  test('использует правильную структуру masonry-сетки', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate(mockAlbums));

    const renderResult = render(<AlbumList />);

    await waitFor(() => {
      expect(screen.getByTestId('album-list-container')).toBeInTheDocument();
    });

    const container = renderResult.container.querySelector('.container');
    expect(container).toBeInTheDocument();
    expect(container).toHaveAttribute('data-testid', 'album-list-container');

    const grid = renderResult.container.querySelector('.masonry-grid');
    expect(grid).not.toBeNull();
    expect(grid!.querySelector('.masonry-sizer')).toBeInTheDocument();

    const items = renderResult.container.querySelectorAll('.masonry-item');
    expect(items).toHaveLength(mockAlbums.length);
  });

  /**
   * Проверить обработку ошибок сервиса.
   */
  test('обрабатывает ошибку сервиса', async () => {
    galleryService.getAlbums.mockRejectedValueOnce(new Error('Ошибка загрузки: 500'));

    render(<AlbumList />);

    await waitFor(() => {
      expect(screen.getByText('Ошибка загрузки: 500')).toBeInTheDocument();
    });
  });

  /**
   * Проверить использование total_pages из ответа API.
   */
  test('использует total_pages из ответа API', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate(mockAlbums, { count: 100, total_pages: 5 }));

    render(<AlbumList />);

    await waitFor(() => {
      expect(screen.getByTestId('album-list-container')).toBeInTheDocument();
    });

    mockAlbums.forEach((album) => {
      expect(screen.getByTestId(`album-card-${album.id}`)).toBeInTheDocument();
    });
  });

  /**
   * Проверить работу с одной страницей.
   */
  test('корректно работает с разным количеством страниц', async () => {
    galleryService.getAlbums.mockResolvedValueOnce(paginate(mockAlbums.slice(0, 1), { count: 5, total_pages: 1 }));

    render(<AlbumList />);

    await waitFor(() => {
      expect(screen.getByTestId('album-list-container')).toBeInTheDocument();
    });

    // При одной странице пагинация не отображается
    const pagination = screen.queryByText('Pagination');
    expect(pagination).not.toBeInTheDocument();
  });
});
