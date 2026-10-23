import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import PhotoList from './PhotoList';
import type { PhotoCardProps } from './PhotoCard';
import { makePhoto, makeAlbumDetail, paginate } from '@test-utils';
import { galleryService as galleryServiceModule, api as apiModule } from '@services';

jest.mock('@services');

// Мокировать компонент PhotoCard для изоляции тестов
jest.mock('./PhotoCard', () => ({
  __esModule: true,
  default: ({ photo }: PhotoCardProps) => <div data-testid={`photo-card-${photo.id}`}>{photo.name}</div>,
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
    makePhoto({ id: 1, name: 'Фото 1', slug: 'photo-1', thumbnail_url: '/img1.jpg' }),
    makePhoto({ id: 2, name: 'Фото 2', slug: 'photo-2', thumbnail_url: '/img2.jpg' }),
    makePhoto({ id: 3, name: 'Фото 3', slug: 'photo-3', thumbnail_url: '/img3.jpg' }),
  ];

  let galleryService: jest.Mocked<typeof galleryServiceModule>;
  let api: jest.Mocked<typeof apiModule>;

  beforeEach(() => {
    galleryService = jest.mocked(galleryServiceModule);
    api = jest.mocked(apiModule);
    galleryService.getPhotos.mockReset();
    galleryService.getAlbum.mockReset();
    api.get.mockReset();
  });

  /**
   * Проверяет, что компонент запрашивает фотографии через сервис при монтировании
   */
  test('загружает данные при монтировании', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(paginate(mockPhotos));
    render(<PhotoList />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ page: 1 });
    });
  });

  /**
   * Проверяет передачу слага тега в параметры запроса
   */
  test('передаёт слаг тега в параметры запроса', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(paginate(mockPhotos));
    render(<PhotoList tagSlug="example-tag" />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ tags__slug: 'example-tag', page: 1 });
    });
  });

  /**
   * Проверяет передачу поискового запроса в параметры выборки
   */
  test('передаёт поисковый запрос в параметры выборки', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(paginate(mockPhotos));
    render(<PhotoList search="sunset" />);
    await waitFor(() => {
      expect(galleryService.getPhotos).toHaveBeenCalledWith({ search: 'sunset', page: 1 });
    });
  });

  /**
   * Проверяет сообщение о пустом результате при активном поиске
   */
  test('отображает сообщение с запросом при пустом результате поиска', async () => {
    galleryService.getPhotos.mockResolvedValueOnce(paginate([]));
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
    galleryService.getPhotos.mockResolvedValueOnce(paginate(mockPhotos));
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
    galleryService.getPhotos.mockResolvedValueOnce(paginate([]));
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
    galleryService.getAlbum.mockResolvedValueOnce(makeAlbumDetail({ id: 7, name: 'Альбом', photos: mockPhotos }));
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
      .mockResolvedValueOnce(paginate(mockPhotos));
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
    galleryService.getPhotos.mockResolvedValue(paginate(mockPhotos));
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
    const manyPhotos = Array.from({ length: 50 }, (_, i) =>
      makePhoto({ id: i + 1, name: `Фото ${i + 1}`, slug: `photo-${i + 1}` }),
    );
    galleryService.getPhotos.mockResolvedValueOnce(paginate(manyPhotos));
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
    const firstPage = paginate(mockPhotos.slice(0, 2), {
      count: 3,
      total_pages: 2,
      next: 'http://localhost/api/gallery/photos/?page=2',
    });
    const secondPage = paginate(mockPhotos.slice(2), {
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
    const photosWithoutThumbnails = mockPhotos.map((p) => makePhoto({ ...p, thumbnail_url: undefined }));
    galleryService.getPhotos.mockResolvedValueOnce(paginate(photosWithoutThumbnails));
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
    });
  });
});
