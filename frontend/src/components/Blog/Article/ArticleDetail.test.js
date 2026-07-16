/**
 * Тесты для компонента ArticleDetail.
 *
 * Проверяет корректность отображения детального просмотра статьи с комментариями,
 * включая загрузку статьи, обработку ошибок, отображение комментариев и формы.
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ArticleDetail from './ArticleDetail';

// Мок для компонента CommentList
jest.mock('@components/Blog/Comment/CommentList', () => {
  return function MockCommentList({ comments }) {
    return (
      <div data-testid="comment-list">
        {comments && comments.map((c, i) => (
          <div key={i} data-testid="comment">{c.author_username}</div>
        ))}
      </div>
    );
  };
});

// Мок для компонента CommentForm
jest.mock('@components/Blog/Comment/CommentForm', () => {
  return function MockCommentForm({ articleId, isAuthenticated }) {
    return (
      <div data-testid="comment-form">
        <span>Form for article {articleId}</span>
        <span>Auth: {isAuthenticated ? 'yes' : 'no'}</span>
      </div>
    );
  };
});

// Мок для компонента SpinnerComponent
jest.mock('@components/Spinner/Spinner', () => {
  return function MockSpinnerComponent({ message }) {
    return <div data-testid="spinner">{message}</div>;
  };
});

// Мок для компонента AlertList
jest.mock('@components/Alert/AlertList', () => {
  return function MockAlertList({ messages }) {
    return (
      <div data-testid="alert-list">
        {messages.map((msg, i) => (
          <div key={i} data-testid={`alert-${msg.level}-${i}`}>
            {msg.message}
            {msg.actions}
          </div>
        ))}
      </div>
    );
  };
});

describe('ArticleDetail', () => {
  const mockProps = {
    articleId: 1,
    isAuthenticated: true,
    loginUrl: '/accounts/login/?next=/blog/1/',
  };

  const mockArticle = {
    id: 1,
    title: 'Тестовая статья',
    content: '<p>Полный текст статьи</p>',
    published_at: '01 янв. 2024 г.',
    modified_at: '02 янв. 2024 г.',
    comments: [
      { id: 1, author_username: 'user1', content: 'Отлично!', posted: '01 янв. 2024 г.' },
    ],
  };

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  /**
   * Проверяет отображение индикатора загрузки при монтировании компонента.
   * Компонент должен показывать спиннер до получения данных от API.
   */
  test('отображает индикатор загрузки при монтировании', () => {
    global.fetch.mockImplementation(() => new Promise(() => {}));
    render(<ArticleDetail {...mockProps} />);
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
    expect(screen.getByText('Загрузка статьи...')).toBeInTheDocument();
  });

  /**
   * Проверяет отображение заголовка статьи при успешной загрузке.
   * Заголовок должен корректно отображаться после получения данных.
   */
  test('отображает заголовок статьи', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Тестовая статья')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение контента статьи с HTML.
   * HTML-контент должен корректно рендериться через dangerouslySetInnerHTML.
   */
  test('отображает контент статьи с HTML', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Полный текст статьи')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение даты публикации.
   * Дата публикации должна отображаться в карточке статьи.
   */
  test('отображает дату публикации', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Опубликовано 01 янв. 2024 г.')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение даты обновления.
   * Дата обновления должна отображаться в карточке статьи.
   */
  test('отображает дату обновления', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Обновлено 02 янв. 2024 г.')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение формы комментариев.
   * Форма должна быть доступна для авторизованных пользователей.
   */
  test('отображает форму комментариев', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByTestId('comment-form')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет передачу articleId в компонент CommentForm.
   * ID статьи должен передаваться для создания комментария.
   */
  test('передает articleId в CommentForm', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Form for article 1')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет передачу isAuthenticated в компонент CommentForm.
   * Статус авторизации должен передаваться для отображения формы.
   */
  test('передает isAuthenticated в CommentForm', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Auth: yes')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение списка комментариев.
   * Комментарии должны отображаться после загрузки статьи.
   */
  test('отображает список комментариев', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByTestId('comment-list')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отсутствие CommentList при пустом списке комментариев.
   * Компонент не должен рендерить пустой список.
   */
  test('не отображает CommentList если комментариев нет', async () => {
    const articleWithoutComments = {
      ...mockArticle,
      comments: [],
    };

    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => articleWithoutComments,
    });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.queryByTestId('comment-list')).not.toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение ошибки при неудачной загрузке.
   * Компонент должен показывать сообщение об ошибке.
   */
  test('отображает ошибку при неудачной загрузке', async () => {
    global.fetch.mockRejectedValue(new Error('Статья не найдена'));

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByTestId('alert-list')).toBeInTheDocument();
    });

    expect(screen.getByTestId('alert-error-0')).toHaveTextContent('Статья не найдена');
  });

  /**
   * Проверяет отображение кнопки "Повторить" при ошибке.
   * Пользователь должен иметь возможность повторить запрос.
   */
  test('отображает кнопку "Повторить" при ошибке', async () => {
    global.fetch.mockRejectedValue(new Error('Статья не найдена'));

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Повторить')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет повторную попытку загрузки при нажатии кнопки "Повторить".
   * Компонент должен повторять запрос при клике на кнопку.
   */
  test('повторная попытка загрузки при нажатии кнопки "Повторить"', async () => {
    global.fetch
      .mockRejectedValueOnce(new Error('Статья не найдена'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockArticle,
      });

    render(<ArticleDetail {...mockProps} />);

    await waitFor(() => {
      expect(screen.getByText('Повторить')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Повторить'));

    await waitFor(() => {
      expect(screen.getByText('Тестовая статья')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет передачу isAuthenticated=false в CommentForm.
   * Для неавторизованных пользователей должна отображаться ссылка входа.
   */
  test('передает isAuthenticated=false в CommentForm', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail {...mockProps} isAuthenticated={false} loginUrl="/login/" />);

    await waitFor(() => {
      expect(screen.getByText('Auth: no')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет использование правильного URL для загрузки статьи.
   * Компонент должен использовать articleId для формирования URL API.
   */
  test('использует правильный URL для загрузки статьи', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockArticle,
    });

    render(<ArticleDetail articleId={5} isAuthenticated={true} loginUrl="/login/" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/blog/articles/5/');
    });
  });
});
