import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import TagsOffcanvas from './TagsOffcanvas';
import type { components } from '../../../types/api-schema';
import { galleryService as galleryServiceModule } from '@services';

type Tag = components['schemas']['Tag'];
type PaginatedTagList = components['schemas']['PaginatedTagList'];

jest.mock('@services');

/**
 * Тесты для компонента TagsOffcanvas.
 * Проверяют загрузку тегов через сервис API, отображение состояний
 * загрузки/ошибки/пустого состояния и взаимодействие пользователя.
 */

// Эмуляция window.matchMedia для корректной работы компонента Offcanvas из react-bootstrap.
// Библиотека jsdom не поддерживает matchMedia, поэтому создаётся мок-реализация
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
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

  const envelope = (results: Tag[]): PaginatedTagList => ({
    count: results.length,
    total_pages: 1,
    next: null,
    previous: null,
    results,
  });

  let galleryService: jest.Mocked<typeof galleryServiceModule>;

  beforeEach(() => {
    galleryService = jest.mocked(galleryServiceModule);
    galleryService.getTags.mockReset();
  });

  // Проверяет, что компонент не загружает данные при show=false
  test('не загружает данные если show=false', () => {
    render(<TagsOffcanvas show={false} onHide={jest.fn()} />);

    expect(galleryService.getTags).not.toHaveBeenCalled();
  });

  // Проверяет загрузку тегов при монтировании компонента с show=true
  test('загружает теги при монтировании если show=true', async () => {
    galleryService.getTags.mockResolvedValueOnce(envelope(mockTags));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(galleryService.getTags).toHaveBeenCalled();
    });
  });

  // Проверяет отображение индикатора загрузки во время выполнения запроса
  test('отображает индикатор загрузки', async () => {
    galleryService.getTags.mockImplementationOnce(() => new Promise(() => {}));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    // Используем getByText с точным матчером, чтобы избежать множественных совпадений
    expect(
      screen.getByText((content, element) => {
        return content === 'Загрузка тегов...' && element !== null && element.tagName.toLowerCase() === 'p';
      }),
    ).toBeInTheDocument();
  });

  // Проверяет отображение списка тегов после успешной загрузки данных
  test('отображает список тегов после загрузки', async () => {
    galleryService.getTags.mockResolvedValueOnce(envelope(mockTags));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Природа')).toBeInTheDocument();
      expect(screen.getByText('Пейзаж')).toBeInTheDocument();
      expect(screen.getByText('Портрет')).toBeInTheDocument();
    });
  });

  // Проверяет отображение сообщения об ошибке при ошибке сервиса
  test('обрабатывает ошибку загрузки', async () => {
    galleryService.getTags.mockRejectedValueOnce(new Error('Ошибка загрузки: 500'));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText(/Ошибка загрузки: 500/)).toBeInTheDocument();
    });
  });

  // Проверяет отображение сообщения об ошибке при ошибке сети
  test('обрабатывает network error', async () => {
    galleryService.getTags.mockRejectedValueOnce(new Error('Network error'));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  // Проверяет отображение пустого состояния при получении пустого списка
  test('отображает пустое состояние если нет тегов', async () => {
    galleryService.getTags.mockResolvedValueOnce(envelope([]));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Нет доступных тегов')).toBeInTheDocument();
    });
  });

  // Проверяет отображение заголовка "Тэги"
  test('отображает заголовок "Тэги"', async () => {
    galleryService.getTags.mockResolvedValueOnce(envelope([]));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />);
    });

    expect(screen.getByText('Тэги')).toBeInTheDocument();
  });

  // Проверяет отображение кнопки закрытия Offcanvas
  test('отображает кнопку закрытия', async () => {
    galleryService.getTags.mockResolvedValueOnce(envelope([]));

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

    galleryService.getTags.mockResolvedValueOnce(envelope([]));

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={handleHide} />);
    });

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
    galleryService.getTags
      .mockRejectedValueOnce(new Error('Ошибка загрузки: 500'))
      .mockResolvedValueOnce(envelope(mockTags));

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
    galleryService.getTags.mockResolvedValue(envelope(mockTags));

    let container: HTMLElement | undefined;
    await act(async () => {
      const result = render(<TagsOffcanvas show={false} onHide={jest.fn()} />);
      container = result.container;
    });

    expect(galleryService.getTags).not.toHaveBeenCalled();

    await act(async () => {
      render(<TagsOffcanvas show={true} onHide={jest.fn()} />, { container });
    });

    await waitFor(() => {
      expect(galleryService.getTags).toHaveBeenCalledTimes(1);
    });
  });
});
