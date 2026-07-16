import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PhotoUploadForm from './PhotoUploadForm';

/**
 * Тесты для компонента PhotoUploadForm.
 * Проверяют загрузку альбомов, выбор файлов, процесс загрузки фотографий,
 * обработку ошибок и отображение прогресса загрузки.
 */

// Мок для document.cookie для эмуляции CSRF токена
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: 'csrftoken=test-csrf-token',
});

describe('PhotoUploadForm', () => {
  // Мок-данные альбомов для тестирования
  const mockAlbums = [
    { id: 1, name: 'Альбом 1' },
    { id: 2, name: 'Альбом 2' },
  ];

  // Настройка mock fetch перед каждым тестом
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  // Восстановление всех моков после каждого теста
  afterEach(() => {
    jest.restoreAllMocks();
  });

  // Проверяет автоматическую загрузку списка альбомов при монтировании компонента
  test('загружает список альбомов при монтировании', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/gallery/albums/');
    });
  });

  // Проверяет отображение индикатора загрузки во время получения списка альбомов
  test('отображает индикатор загрузки альбомов', () => {
    global.fetch.mockImplementationOnce(() => new Promise(() => {}));

    render(<PhotoUploadForm />);

    const loadingElements = screen.getAllByText('Загрузка альбомов...');
    expect(loadingElements.length).toBeGreaterThan(0);
  });

  // Проверяет отображение формы после успешной загрузки альбомов
  test('отображает форму после загрузки альбомов', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
      expect(screen.getByText('Выберите альбом')).toBeInTheDocument();
    });
  });

  // Проверяет отображение сообщения об ошибке при неудачной загрузке альбомов
  test('отображает ошибку загрузки альбомов', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки альбомов: 500/)).toBeInTheDocument();
    });
  });

  // Проверяет возможность повторной загрузки альбомов после ошибки
  test('повторная загрузка альбомов работает после ошибки', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки альбомов/)).toBeInTheDocument();
    });

    const retryButton = screen.getByText('Повторить');
    await user.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });
  });

  // Проверяет блокировку кнопки загрузки при отсутствии выбранного альбома
  test('кнопка загрузки отключена без выбранного альбома', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      const uploadButton = screen.getByText('Загрузить');
      expect(uploadButton).toBeDisabled();
    });
  });

  // Проверяет блокировку кнопки загрузки при наличии альбома, но отсутствии файлов
  test('кнопка загрузки отключена без файлов', async () => {
    const user = userEvent.setup();

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const uploadButton = screen.getByText('Загрузить');
    expect(uploadButton).toBeDisabled();
  });

  // Проверяет блокировку кнопки загрузки при наличии файлов, но отсутствии выбранного альбома
  test('кнопка disabled если альбом не выбран', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    expect(uploadButton).toBeDisabled();
  });

  // Проверяет успешную загрузку файлов на сервер
  test('успешная загрузка файлов', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [{ success: true }] }),
      });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    await user.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('Фотографии успешно загружены!')).toBeInTheDocument();
    });
  });

  // Проверяет отображение прогресса во время загрузки файлов
  test('отображает прогресс загрузки', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      })
      .mockImplementationOnce(() =>
        new Promise(resolve =>
          setTimeout(
            () =>
              resolve({
                ok: true,
                json: async () => ({ results: [{ success: true }] }),
              }),
            100
          )
        )
      );

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    await user.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('Прогресс загрузки:')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Фотографии успешно загружены!')).toBeInTheDocument();
    });
  });

  // Проверяет обработку ошибки при загрузке файла
  test('обрабатывает ошибку загрузки файла', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    await user.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('Ошибки загрузки')).toBeInTheDocument();
    });
  });

  // Проверяет блокировку кнопки во время процесса загрузки
  test('кнопка отключена во время загрузки', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      })
      .mockImplementationOnce(() => new Promise(() => {}));

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    await user.click(uploadButton);

    expect(screen.getByText('Загрузка...')).toBeInTheDocument();
    expect(uploadButton).toBeDisabled();
  });

  // Проверяет использование кастомного URL для API загрузки
  test('использует кастомный apiUrl', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [{ success: true }] }),
      });

    render(<PhotoUploadForm apiUrl="/custom/api/" />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    await user.click(uploadButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/custom/api/upload/',
        expect.any(Object)
      );
    });
  });

  // Проверяет использование кастомного URL для API альбомов
  test('использует кастомный albumsApiUrl', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<PhotoUploadForm albumsApiUrl="/custom/albums/" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/custom/albums/');
    });
  });

  // Проверяет сброс формы после успешной загрузки всех файлов
  test('сбрасывает форму после успешной загрузки', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [{ success: true }] }),
      });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    await user.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('Фотографии успешно загружены!')).toBeInTheDocument();
      expect(screen.queryByText('test.jpg')).not.toBeInTheDocument();
    });
  });

  // Проверяет передачу CSRF токена в заголовках запроса
  test('отправляет CSRF токен в заголовках', async () => {
    const user = userEvent.setup();

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockAlbums }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [{ success: true }] }),
      });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    const uploadButton = screen.getByText('Загрузить');
    await user.click(uploadButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-CSRFToken': 'test-csrf-token',
          }),
        })
      );
    });
  });

  // Проверяет корректную обработку ответа API в виде прямого массива без обёртки results
  test('обрабатывает прямой массив альбомов без results', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAlbums,
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Альбом 1')).toBeInTheDocument();
    });
  });

  // Проверяет обработку сетевой ошибки при загрузке альбомов
  test('обрабатывает network error при загрузке альбомов', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  // Проверяет очистку сообщений об ошибках и успехе при выборе новых файлов
  test('очищает ошибки и успех при выборе новых файлов', async () => {
    const user = userEvent.setup();

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockAlbums }),
    });

    render(<PhotoUploadForm />);

    await waitFor(() => {
      expect(screen.getByText('Загрузка фотографий')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    await user.selectOptions(select, '1');

    const file1 = new File(['content'], 'test1.jpg', { type: 'image/jpeg' });
    const input = document.querySelector('input[type="file"]');
    fireEvent.change(input, { target: { files: [file1] } });

    await waitFor(() => {
      expect(screen.getByText('test1.jpg')).toBeInTheDocument();
    });

    const file2 = new File(['content'], 'test2.jpg', { type: 'image/jpeg' });
    fireEvent.change(input, { target: { files: [file2] } });

    await waitFor(() => {
      expect(screen.getByText('test2.jpg')).toBeInTheDocument();
      expect(screen.queryByText('test1.jpg')).not.toBeInTheDocument();
    });
  });
});
