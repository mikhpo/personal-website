/**
 * Тесты для компонента About.
 *
 * Проверяет состояния: загрузка, ошибка с повтором, пустой контент,
 * отображение HTML-контента из API.
 */

import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import About from '@components/About/AboutPage';
import type { SpinnerProps } from '@components/Spinner/Spinner';
import { aboutService } from '@services';

jest.mock('@services');

// Мокировать дочерние компоненты, чтобы проверить только About
jest.mock('@components/Spinner/Spinner', () => ({
  __esModule: true,
  default: ({ message }: SpinnerProps) => <p>{message}</p>,
}));

/**
 * Группа тестов компонента About.
 */
describe('About', () => {
  // Автомок @services: обертка jest.mocked открывает mock-методы сервиса
  const mockedAboutService = jest.mocked(aboutService);

  beforeEach(() => {
    mockedAboutService.getAbout.mockReset();
  });

  /**
   * Проверка показа сообщения о загрузке, пока ответ API не получен.
   */
  test('отображает состояние загрузки', () => {
    mockedAboutService.getAbout.mockImplementationOnce(() => new Promise(() => {}));
    render(<About />);
    expect(screen.getByText('Загрузка страницы...', { selector: 'p' })).toBeInTheDocument();
  });

  /**
   * Проверка вывода сообщения об ошибке и повторной загрузки по кнопке.
   */
  test('отображает ошибку и повторяет загрузку', async () => {
    mockedAboutService.getAbout
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ content: '<p>Контент</p>' });
    render(<About />);
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });

    const retryButton = screen.getByText('Повторить');
    await userEvent.click(retryButton);
    await waitFor(() => {
      expect(screen.getByText('Контент')).toBeInTheDocument();
    });
  });

  /**
   * Проверка, что при пустом контенте компонент ничего не выводит.
   */
  test('не выводит ничего при пустом контенте', async () => {
    mockedAboutService.getAbout.mockResolvedValueOnce({ content: '' });

    const { container } = render(<About />);
    await waitFor(() => {
      expect(mockedAboutService.getAbout).toHaveBeenCalledTimes(1);
      expect(container).toBeEmptyDOMElement();
    });
  });

  /**
   * Проверка отображения HTML-контента из API: текст и ссылка.
   */
  test('отображает HTML-контет из API', async () => {
    mockedAboutService.getAbout.mockResolvedValueOnce({ content: '<p>Привет!</p><a href="mailto:a@b.c">a@b.c</a>' });

    render(<About />);
    await waitFor(() => {
      expect(screen.getByText('Привет!')).toBeInTheDocument();
    });
    expect(screen.getByText('a@b.c')).toBeInTheDocument();
  });
});
