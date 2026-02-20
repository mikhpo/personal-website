import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TagsOffcanvas from './TagsOffcanvas';

/**
 * Тесты для компонента TagsOffcanvas.
 * Проверяют загрузку тегов, отображение состояний загрузки/ошибки/пустого состояния,
 * обработку различных форматов ответа API и взаимодействие пользователя.
 */

// Эмуляция window.matchMedia для корректной работы компонента Offcanvas из react-bootstrap.
// Библиотека jsdom не поддерживает matchMedia, поэтому создаётся мок-реализация
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('TagsOffcanvas', () => {
  // Мок-данные тегов для тестирования
  const mockTags = [
    { id: 1, name: 'Природа', slug: 'nature' },
    { id: 2, name: 'Пейзаж', slug: 'landscape' },
    { id: 3, name: 'Портрет', slug: 'portrait' },
  ];

  // Настройка mock fetch перед каждым тестом
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  // Восстановление всех моков после каждого теста
  afterEach(() => {
    jest.restoreAllMocks();
  });

  // Проверяет, что компонент не загружает данные при show=false
  test('не загружает данные если show=false', () => {
    render(<TagsOffcanvas show={false} onHide={jest.fn()} />);

    expect(global.fetch).not.toHaveBeenCalled();
  });

  // Проверяет загрузку тегов при монтировании компонента с show=true
  test('загружает теги при монтировании если show=true', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockTags }),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/gallery/tags/');
    });
  });

  // Проверяет отображение индикатора загрузки во время выполнения fetch запроса
  test('отображает индикатор загрузки', async () => {
    global.fetch.mockImplementationOnce(() => new Promise(() => {}));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    // Используем getByText с точным матчером, чтобы избежать множественных совпадений
    expect(screen.getByText((content, element) => {
      return content === 'Загрузка тегов...' && element.tagName.toLowerCase() === 'p';
    })).toBeInTheDocument();
  });

  // Проверяет отображение списка тегов после успешной загрузки данных
  test('отображает список тегов после загрузки', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockTags }),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Природа')).toBeInTheDocument();
      expect(screen.getByText('Пейзаж')).toBeInTheDocument();
      expect(screen.getByText('Портрет')).toBeInTheDocument();
    });
  });

  // Проверяет отображение сообщения об ошибке при HTTP ошибке
  test('обрабатывает ошибку загрузки', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 500/)).toBeInTheDocument();
    });
  });

  // Проверяет отображение сообщения об ошибке при ошибке сети
  test('обрабатывает network error', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  // Проверяет отображение пустого состояния при получении пустого массива от API
  test('отображает пустое состояние если нет тегов', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Нет доступных тегов')).toBeInTheDocument();
    });
  });

  // Проверяет корректную обработку ответа API в виде прямого массива без обёртки results
  test('обрабатывает прямой массив без results', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTags,
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Природа')).toBeInTheDocument();
    });
  });

  // Проверяет отображение пустого состояния при получении пустого объекта от API
  test('обрабатывает пустой объект ответа', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Нет доступных тегов')).toBeInTheDocument();
    });
  });

  // Проверяет отображение пустого состояния, если results не является массивом
  test('обрабатывает не-массив в results', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: 'not an array' }),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Нет доступных тегов')).toBeInTheDocument();
    });
  });

  // Проверяет использование кастомного URL при передаче props tagsApiUrl
  test('использует кастомный tagsApiUrl', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: mockTags }),
    });

    await act(async () => {
      render(
        <TagsOffcanvas
          show={true}
          onHide={jest.fn()}
          tagsApiUrl="/custom/api/tags/"
        />
      );
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/custom/api/tags/');
    });
  });

  // Проверяет отображение заголовка "Тэги"
  test('отображает заголовок "Тэги"', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    expect(screen.getByText('Тэги')).toBeInTheDocument();
  });

  // Проверяет отображение кнопки закрытия Offcanvas
  test('отображает кнопку закрытия', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    const closeButton = screen.getByLabelText('Close');
    expect(closeButton).toBeInTheDocument();
  });

  // Проверяет вызов колбэка onHide при клике на кнопку закрытия
  test('вызывает onHide при клике на кнопку закрытия', async () => {
    const user = userEvent.setup();
    const handleHide = jest.fn();

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={handleHide} />);
    });

    // Ожидаем рендер компонента и появление кнопки закрытия
    await waitFor(() => {
      const closeButton = screen.getByLabelText('Close');
      expect(closeButton).toBeInTheDocument();
    });

    const closeButton = screen.getByLabelText('Close');
    await user.click(closeButton);

    expect(handleHide).toHaveBeenCalledTimes(1);
  });

  // Проверяет возможность повторной загрузки данных после отображения ошибки
  test('повторная загрузка работает после ошибки', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: mockTags }),
      });

    const user = userEvent.setup();
    
    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 500/)).toBeInTheDocument();
    });

    const retryButton = screen.getByText('Повторить');
    await user.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('Природа')).toBeInTheDocument();
    });
  });

  // Проверяет загрузку данных при изменении show с false на true
  test('загружает данные при изменении show с false на true', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ results: mockTags }),
    });

    let container;
    await act(async () => {
      const result = render(<TagsOffcanvas show={false} onHide={jest.fn()} />);
      container = result.container;
    });

    expect(global.fetch).not.toHaveBeenCalled();

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />, { container });
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  // Проверяет перезагрузку данных при изменении props tagsApiUrl
  test('перезагружает данные при изменении tagsApiUrl', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ results: mockTags }),
    });

    let container;
    await act(async () => {
      const result = render(
        <TagsOffcanvas show={true} onHide={jest.fn()} tagsApiUrl="/api/tags1/" />
      );
      container = result.container;
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/tags1/');
    });

    await act(async () => {
      render(
        <TagsOffcanvas show={true} onHide={jest.fn()} tagsApiUrl="/api/tags2/" />
      , { container });
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/tags2/');
    });
  });

});
