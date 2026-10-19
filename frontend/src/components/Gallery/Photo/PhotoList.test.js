import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PhotoList from './PhotoList';

jest.mock('@services');

// Мокировать компонент PhotoCard для изоляции тестов
jest.mock('./PhotoCard', () => ({
  __esModule: true,
  default: ({ photo }) => <div data-testid={`photo-card-${photo.id}`}>{photo.name}</div>,
}));

/**
 * Тесты для компонента PhotoList
 *
 * Проверяет корректность отображения списка фотографий через сервисы API,
 * обработку различных состояний (загрузка, ошибка, пустой список),
 * режим страницы альбома и функциональность пагинации.
 */
describe('PhotoList', () => {
  const mockPhotos = [
    { id: 1, name: 'Фото 1', slug: 'photo-1', thumbnail_url: '/img1.jpg' },
    { id: 2, name: 'Фото 2', slug: 'photo-2', thumbnail_url: '/img2.jpg' },
    { id: 3, name: 'Фото 3', slug: 'photo-3', thumbnail_url: '/img3.jpg' },
  ];

  const envelope = (results, extra = {}) => ({
    count: results.length,
    total_pages: 1,
    next: null,
    previous: null,
    results,
    ...extra,
  });

  let galleryService;
  let api;

  beforeEach(() => {
    const services = require('@services');
    galleryService = services.galleryService;
    api = services.api;
    galleryService.getPhotos.mockReset();
    galleryService.getAlbum.mockReset();
    api.get.mockReset();
  });

  /**
   * Проверяет, что компонент запрашивает фотографии через сервис при монтировании
   */
  test('загружает данные при монтировании', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(envelope(mockPhotos));
    render(<PhotoList />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ page: 1 });
    });
  });

  /**
   * Проверяет передачу слага тега в параметры запроса
   */
  test('передаёт слаг тега в параметры запроса', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(envelope(mockPhotos));
    render(<PhotoList tagSlug="example-tag" />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ tags__slug: 'example-tag', page: 1 });
    });
  });

  /**
   * Проверяет передачу поискового запроса в параметры выборки
   */
  test('передаёт поисковый запрос в параметры выборки', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(envelope(mockPhotos));
    render(<PhotoList search="sunset" />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ search: 'sunset', page: 1 });
    });
  });

  /**
   * Проверяет сообщение о пустом результате при активном поиске
   */
  test('отображает сообщение с запросом при пустом результате поиска', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(envelope([]));
    render(<PhotoList search="sunset" />);
    await waitFor(() => {
      expect(screen.getByText('По запросу "sunset" ничего не найдено')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение индикатора загрузки
   */
  test('отображает индикатор загрузки', () => {
    galleryService.getPhotos.mockImplementationOnce(() => new Promise(() => {}));
    render(<PhotoList />);
    expect(screen.getAllByText('Загрузка фотографий...')).toHaveLength(2);
  });

  /**
   * Проверяет отображение списка фотографий после успешной загрузки
   */
  test('отображает список фотографий после загрузки', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(envelope(mockPhotos));
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
      expect(screen.getByText('Фото 2')).toBeInTheDocument();
      expect(screen.getByText('Фото 3')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обработку ошибок сервиса
   */
  test('обрабатывает ошибку загрузки', async () => {
    galleryService.getPhotos.mockRejectedValueOnce(new Error('Ошибка загрузки: 500'));
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 500/)).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение сообщения при отсутствии фотографий
   */
  test('отображает пустое состояние если нет фотографий', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(envelope([]));
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Нет доступных фотографий')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет режим страницы альбома: фотографии берутся из детального
   * ответа альбома, пагинация не запрашивается
   */
  test('загружает фотографии альбома через детальный эндпоинт', async () => {
    galleryService.getAlbum.mockResolvedValueOnce({
      id: 7,
      name: 'Альбом',
      photos: mockPhotos,
    });
    render(<PhotoList albumId={7} />);
    await waitFor(() => {
      expect(galleryService.getAlbum).toHaveBeenCalledWith(7);
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
      expect(screen.getByText('Фото 3')).toBeInTheDocument();
    });
    expect(galleryService.getPhotos).not.toHaveBeenCalled();
  });

  /**
   * Проверяет функциональность повторной загрузки после ошибки
   */
  test('повторная загрузка работает после ошибки', async () => {
    const user = userEvent.setup();
    galleryService.getPhotos
      .mockRejectedValueOnce(new Error('Ошибка загрузки: 500'))
      .mockResolvedValueOnce(envelope(mockPhotos));
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 500/)).toBeInTheDocument();
    });

    const retryButton = screen.getByText('Повторить');
    await user.click(retryButton);

    await waitFor(
      () => {
        expect(screen.getByText('Фото 1')).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });

  /**
   * Проверяет перезагрузку данных при изменении фильтра
   */
  test('перезагружает данные при изменении фильтра', async () => {
    galleryService.getPhotos.mockResolvedValue(envelope(mockPhotos));
    const { rerender } = render(<PhotoList tagSlug="first-tag" />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ tags__slug: 'first-tag', page: 1 });
    });
    rerender(<PhotoList tagSlug="second-tag" />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ tags__slug: 'second-tag', page: 1 });
    });
  });

  /**
   * Проверяет работу с большим количеством фотографий
   */
  test('рендерит большое количество фотографий', async () => {
    const manyPhotos = Array.from({ length: 50 }, (_, i) => ({
      id: i + 1,
      name: `Фото ${i + 1}`,
      slug: `photo-${i + 1}`,
    }));
    galleryService.getPhotos.mockResolvedValueOnce(envelope(manyPhotos));
    const { container } = render(<PhotoList />);
    await waitFor(() => {
      const items = container.querySelectorAll('.masonry-item');
      expect(items).toHaveLength(50);
    });
  });

  /**
   * Проверяет переход по ссылке следующей страницы пагинации
   */
  test('переходит на следующую страницу по ссылке пагинации', async () => {
    const user = userEvent.setup();
    const firstPage = envelope(mockPhotos.slice(0, 2), {
      count: 3,
      total_pages: 2,
      next: 'http://localhost/api/gallery/photos/?page=2',
    });
    const secondPage = envelope(mockPhotos.slice(2), {
      count: 3,
      total_pages: 2,
      previous: 'http://localhost/api/gallery/photos/?page=1',
    });
    galleryService.getPhotos.mockResolvedValueOnce(firstPage);
    api.get.mockResolvedValueOnce(secondPage);
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
    });

    await user.click(screen.getByText('следующая'));

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('http://localhost/api/gallery/photos/?page=2');
      expect(screen.getByText('Фото 3')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обработку ошибки 404
   */
  test('обрабатывает ошибку 404', async () => {
    galleryService.getPhotos.mockRejectedValueOnce(new Error('Ошибка загрузки: 404'));
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 404/)).toBeInTheDocument();
    });
  });

  /**
   * Проверяет работу с фотографиями без thumbnail_url
   */
  test('работает с фотографиями без thumbnail_url', async () => {
    const photosWithoutThumbnails = mockPhotos.map((p) => ({ ...p, thumbnail_url: undefined }));
    galleryService.getPhotos.mockResolvedValueOnce(envelope(photosWithoutThumbnails));
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
    });
  });
});
