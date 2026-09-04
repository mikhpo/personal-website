import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PhotoList from './PhotoList';

// Мокировать компонент PhotoCard для изоляции тестов
jest.mock('./PhotoCard', () => ({
  __esModule: true,
  default: ({ photo }) => (
    <div data-testid={`photo-card-${photo.id}`}>{photo.name}</div>
  ),
}));

/**
 * Тесты для компонента PhotoList
 *
 * Проверяет корректность отображения списка фотографий,
 * обработку различных состояний (загрузка, ошибка, пустой список)
 * и функциональность повторной загрузки данных
 */
describe('PhotoList', () => {
  const mockPhotos = [
    { id: 1, name: 'Фото 1', slug: 'photo-1', thumbnail_url: '/img1.jpg', datetime_taken: '2024-01-01T10:00:00Z' },
    { id: 2, name: 'Фото 2', slug: 'photo-2', thumbnail_url: '/img2.jpg', datetime_taken: '2024-01-02T10:00:00Z' },
    { id: 3, name: 'Фото 3', slug: 'photo-3', thumbnail_url: '/img3.jpg', datetime_taken: '2024-01-03T10:00:00Z' },
  ];

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  /**
   * Проверяет, что компонент выполняет запрос к API при монтировании
   */
  test('загружает данные при монтировании', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/gallery/photos/');
    });
  });

  /**
   * Проверяет передачу слага тега в URL фильтрации
   */
  test('передаёт слаг тега в URL фильтрации', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });
    render(<PhotoList tagSlug="example-tag" />);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('tags__slug=example-tag'),
      );
    });
  });

  /**
   * Проверяет передачу поискового запроса в URL выборки
   */
  test('передаёт поисковый запрос в URL выборки', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });
    render(<PhotoList search="sunset" />);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('search=sunset'),
      );
    });
  });

  /**
   * Проверяет сообщение о пустом результате при активном поиске
   */
  test('отображает сообщение с запросом при пустом результате поиска', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });
    render(<PhotoList search="sunset" />);
    await waitFor(() => {
      expect(screen.getByText('По запросу «sunset» ничего не найдено')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение индикатора загрузки
   */
  test('отображает индикатор загрузки', () => {
    global.fetch.mockImplementationOnce(() => new Promise(() => {}));
    render(<PhotoList />);
    expect(screen.getAllByText('Загрузка фотографий...')).toHaveLength(2);
  });

  /**
   * Проверяет отображение списка фотографий после успешной загрузки
   */
  test('отображает список фотографий после загрузки', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
      expect(screen.getByText('Фото 2')).toBeInTheDocument();
      expect(screen.getByText('Фото 3')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обработку ошибок HTTP
   */
  test('обрабатывает ошибку загрузки', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 500/)).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение сообщения при отсутствии фотографий
   */
  test('отображает пустое состояние если нет фотографий', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Нет доступных фотографий')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обработку данных в формате массива напрямую (без поля results)
   * Хотя стандартный API возвращает данные с пагинацией (в поле results),
   * компонент должен корректно обрабатывать и случай, когда API возвращает
   * массив фотографий напрямую (например, при кастомной настройке пагинации
   * или при тестировании с упрощенными данными)
   */
  test('обрабатывает прямой массив без results', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockPhotos,
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обработку пустого объекта ответа
   */
  test('обрабатывает пустой объект ответа', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Нет доступных фотографий')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет функциональность повторной загрузки после ошибки
   */
  test('повторная загрузка работает после ошибки', async () => {
    const user = userEvent.setup();
    global.fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockPhotos }),
      });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 500/)).toBeInTheDocument();
    });

    // Найти кнопку повтора
    const retryButton = screen.getByText('Повторить');
    await user.click(retryButton);

    // Дождаться появления фотографий
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  /**
   * Проверяет перезагрузку данных при изменении apiUrl
   */
  test('перезагружает данные при изменении apiUrl', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ results: mockPhotos }),
    });
    const { rerender } = render(<PhotoList apiUrl="/api/photos1/" />);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/photos1/');
    });
    rerender(<PhotoList apiUrl="/api/photos2/" />);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/photos2/');
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
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: manyPhotos }),
    });
    const { container } = render(<PhotoList />);
    await waitFor(() => {
      const cols = container.querySelectorAll('.col');
      expect(cols).toHaveLength(50);
    });
  });

  /**
   * Проверяет обработку ошибки 404
   */
  test('обрабатывает ошибку 404', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 404/)).toBeInTheDocument();
    });
  });

  /**
   * Проверяет работу с фотографиями без thumbnail_url
   */
  test('работает с фотографиями без thumbnail_url', async () => {
    const photosWithoutThumbnails = mockPhotos.map(p => ({ ...p, thumbnail_url: undefined }));
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: photosWithoutThumbnails }),
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет работу с фотографиями без datetime_taken
   */
  test('работает с фотографиями без datetime_taken', async () => {
    const photosWithoutDates = mockPhotos.map(p => ({ ...p, datetime_taken: undefined }));
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: photosWithoutDates }),
    });
    render(<PhotoList />);
    await waitFor(() => {
      expect(screen.getByText('Фото 1')).toBeInTheDocument();
    });
  });
});
