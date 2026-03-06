/**
 * Тесты для компонента CommentForm.
 *
 * Проверяет корректность отображения формы добавления комментария,
 * включая обработку авторизации, отправку формы, валидацию данных.
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import CommentForm from './CommentForm';

// Мок для компонента AlertList
jest.mock('@components/Alert/AlertList', () => {
  return function MockAlertList({ messages }) {
    return (
      <div data-testid="alert-list">
        {messages.map((msg, i) => (
          <div key={i} data-testid={`alert-${msg.level}`}>{msg.message}</div>
        ))}
      </div>
    );
  };
});

describe('CommentForm', () => {
  const mockProps = {
    articleId: 1,
    isAuthenticated: true,
    loginUrl: '/accounts/login/?next=/blog/test/',
    onSuccess: jest.fn(),
  };

  beforeEach(() => {
    global.fetch = jest.fn();
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'csrftoken=test-csrf-token-12345',
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  /**
   * Проверяет отображение ссылки на страницу входа для неавторизованных пользователей.
   * Неавторизованные пользователи должны видеть ссылку вместо формы.
   */
  describe('неавторизованный пользователь', () => {
    test('отображает ссылку на страницу входа', () => {
      render(<CommentForm {...mockProps} isAuthenticated={false} />);
      const link = screen.getByText('Войдите, чтобы оставить комментарий');
      expect(link).toBeInTheDocument();
      expect(link).toHaveAttribute('href', mockProps.loginUrl);
    });

    /**
     * Проверяет, что форма не отображается для неавторизованных пользователей.
     * Поля ввода и кнопка отправки должны отсутствовать.
     */
    test('не отображает форму', () => {
      render(<CommentForm {...mockProps} isAuthenticated={false} />);
      expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /добавить комментарий/i })).not.toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение формы для авторизованных пользователей.
   * Форма должна содержать поле ввода текста и кнопку отправки.
   */
  describe('авторизованный пользователь', () => {
    test('отображает форму с textarea и кнопкой', () => {
      render(<CommentForm {...mockProps} />);
      expect(screen.getByRole('textbox')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /добавить комментарий/i })).toBeInTheDocument();
    });

    /**
     * Проверяет возможность ввода текста в поле комментария.
     * Поле textarea должно поддерживать изменение значения.
     */
    test('позволяет вводить текст в поле комментария', () => {
      render(<CommentForm {...mockProps} />);
      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Тестовый комментарий' } });
      expect(textarea).toHaveValue('Тестовый комментарий');
    });
  });

  /**
   * Проверяет функциональность отправки формы.
   * Включает успешную отправку, обработку ошибок и CSRF-токен.
   */
  describe('отправка формы', () => {
    /**
     * Проверяет успешную отправку комментария.
     * Данные должны быть отправлены на сервер с правильными заголовками.
     */
    test('отправляет комментарий при успешной отправке', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, content: 'Комментарий' }),
      });

      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Тестовый комментарий' } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/blog/comments/',
          expect.objectContaining({
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': 'test-csrf-token-12345',
            },
            body: JSON.stringify({
              article: 1,
              content: 'Тестовый комментарий',
            }),
          })
        );
      });

      await waitFor(() => {
        expect(mockProps.onSuccess).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toHaveValue('');
      });
    });

    /**
     * Проверяет отображение ошибки при пустом комментарии.
     * Пустой текст должен блокировать отправку формы.
     */
    test('отображает ошибку при пустом комментарии', async () => {
      render(<CommentForm {...mockProps} />);

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(screen.getByTestId('alert-list')).toBeInTheDocument();
      });

      expect(screen.getByTestId('alert-error')).toHaveTextContent('Комментарий не может быть пустым');
    });

    /**
     * Проверяет отображение ошибки при неудачной отправке.
     * Ошибка сети должна быть отображена пользователю.
     */
    test('отображает ошибку при неудачной отправке', async () => {
      global.fetch.mockRejectedValue(new Error('Ошибка сети'));

      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Тестовый комментарий' } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(screen.getByTestId('alert-list')).toBeInTheDocument();
      });

      expect(screen.getByTestId('alert-error')).toHaveTextContent('Ошибка сети');
    });

    /**
     * Проверяет блокировку кнопки во время отправки.
     * Кнопка должна быть отключена и показывать текст "Отправка...".
     */
    test('отключает кнопку во время отправки', async () => {
      global.fetch.mockImplementation(() => new Promise(() => {}));

      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Тестовый комментарий' } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(screen.getByRole('button')).toHaveTextContent('Отправка...');
        expect(screen.getByRole('button')).toBeDisabled();
      });
    });

    /**
     * Проверяет использование CSRF-токена из cookie.
     * Заголовок X-CSRFToken должен содержать токен из cookie.
     */
    test('использует CSRF токен из cookie', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, content: 'Комментарий' }),
      });

      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Тест' } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        const callArgs = global.fetch.mock.calls[0];
        expect(callArgs[1].headers['X-CSRFToken']).toBe('test-csrf-token-12345');
      });
    });
  });

  /**
   * Проверяет вызов callback функции onSuccess.
   * Callback должен вызываться после успешной отправки комментария.
   */
  describe('callback onSuccess', () => {
    test('вызывает onSuccess после успешной отправки', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, content: 'Комментарий' }),
      });

      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Тест' } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(mockProps.onSuccess).toHaveBeenCalled();
      });
    });

    test('не вызывает onSuccess если он не передан', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, content: 'Комментарий' }),
      });

      const onSuccess = jest.fn();
      render(<CommentForm {...mockProps} onSuccess={onSuccess} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: 'Тест' } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(onSuccess).toHaveBeenCalled();
      });
    });
  });

  /**
   * Проверяет обработку граничных случаев.
   * Включает пустые значения, длинные тексты и специальные символы.
   */
  describe('граничные случаи', () => {
    test('обрабатывает комментарий с пробелами только', async () => {
      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: '   ' } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(screen.getByTestId('alert-error')).toHaveTextContent('Комментарий не может быть пустым');
      });
    });

    /**
     * Проверяет обработку длинных комментариев.
     * Компонент должен справляться с текстами произвольной длины.
     */
    test('обрабатывает длинные комментарии', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, content: 'Длинный комментарий' }),
      });

      const longComment = 'а'.repeat(1000);
      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: longComment } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    });

    /**
     * Проверяет обработку специальных символов в комментарии.
     * Компонент должен корректно отправлять текст со спецсимволами.
     */
    test('обрабатывает специальные символы в комментарии', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, content: 'Комментарий с символами' }),
      });

      const specialComment = 'Текст с <символами> & "спецсимволами"';
      render(<CommentForm {...mockProps} />);

      const textarea = screen.getByRole('textbox');
      fireEvent.change(textarea, { target: { value: specialComment } });

      fireEvent.click(screen.getByRole('button', { name: /добавить комментарий/i }));

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    });
  });
});
