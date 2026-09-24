/**
 * Тесты для компонента About.
 *
 * Проверяет состояния: загрузка, ошибка с повтором, пустой контент,
 * отображение HTML-контента из API.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import About from '@components/About/AboutPage';

// Мокировать дочерние компоненты, чтобы проверить только About
jest.mock('@components/Spinner/Spinner', () => ({
  __esModule: true,
  default: ({ message }) => <p>{message}</p>,
}));

/**
 * Группа тестов компонента About.
 */
describe('About', () => {
  /**
   * Установить свежий мок глобального fetch перед каждым тестом.
   */
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  /**
   * Восстановить исходные моки после каждого теста.
   */
  afterEach(() => {
    jest.restoreAllMocks();
  });

  /**
   * Проверка показа сообщения о загрузке, пока ответ API не получен.
   */
  test('отображает состояние загрузки', () => {
    global.fetch.mockImplementation(() => new Promise(() => {}));
    render(<About />);
    expect(screen.getByText('Загрузка страницы...', { selector: 'p' })).toBeInTheDocument();
  });

  /**
   * Проверка вывода сообщения об ошибке и повторной загрузки по кнопке.
   */
  test('отображает ошибку и повторяет загрузку', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));
    render(<About />);
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });

    const retryButton = screen.getByText('Повторить');
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ content: '<p>Контент</p>' }),
    });
    await userEvent.click(retryButton);
    await waitFor(() => {
      expect(screen.getByText('Контент')).toBeInTheDocument();
    });
  });

  /**
   * Проверка, что при пустом контенте компонент ничего не выводит.
   */
  test('не выводит ничего при пустом контенте', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ content: '' }),
    });

    const { container } = render(<About />);
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(container).toBeEmptyDOMElement();
    });
  });

  /**
   * Проверка отображения HTML-контента из API: текст и ссылка.
   */
  test('отображает HTML-контет из API', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ content: '<p>Привет!</p><a href="mailto:a@b.c">a@b.c</a>' }),
    });

    render(<About />);
    await waitFor(() => {
      expect(screen.getByText('Привет!')).toBeInTheDocument();
    });
    expect(screen.getByText('a@b.c')).toBeInTheDocument();
  });
});
