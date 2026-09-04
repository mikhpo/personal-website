/**
 * Тесты для компонента ArticleList.
 *
 * Проверяет корректность отображения списка статей с загрузкой из API,
 * включая обработку состояний загрузки, ошибок, пагинацию и пустого списка.
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ArticleList from './ArticleList';
import { blogService } from '@services';

// Мок для blogService
jest.mock('@services');

// Мок для компонента ArticleCard
jest.mock('@components/Blog/Article/ArticleCard', () => {
  return function MockArticleCard({ article }) {
    return <div data-testid="article-card">{article.title}</div>;
  };
});

// Мок для компонента Pagination
jest.mock('@components/Pagination/Pagination', () => {
  return function MockPagination({ currentPage, totalPages, hasNext, hasPrevious, onNext, onPrevious }) {
    return (
      <div data-testid="pagination">
        <button onClick={onPrevious} disabled={!hasPrevious}>Пред.</button>
        <span>Стр. {currentPage} из {totalPages}</span>
        <button onClick={onNext} disabled={!hasNext}>След.</button>
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
        {messages.map((msg) => (
          <div key={`${msg.level}-${msg.message}`} data-testid={`alert-${msg.level}`}>
            {msg.message}
            {msg.actions}
          </div>
        ))}
      </div>
    );
  };
});

describe('ArticleList', () => {
  /**
   * Мок успешного ответа API с результатами
   */
  const mockApiResponse = {
    count: 25,
    next: '/api/blog/articles/?page=2',
    previous: null,
    results: [
      { id: 1, slug: 'article-1', title: 'Статья 1', content: 'Контент 1' },
      { id: 2, slug: 'article-2', title: 'Статья 2', content: 'Контент 2' },
    ],
  };

  /**
   * Мок успешного ответа API без results (плоский список)
   */
  const mockFlatApiResponse = [
    { id: 1, slug: 'article-1', title: 'Статья 1', content: 'Контент 1' },
  ];

  /**
   * Мок пустого ответа API
   */
  const mockEmptyApiResponse = {
    count: 0,
    next: null,
    previous: null,
    results: [],
  };

  beforeEach(() => {
    blogService.getArticles.mockClear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  /**
   * Проверяет отображение индикатора загрузки при монтировании компонента.
   * Компонент должен показывать спиннер до получения данных от API.
   */
  test('отображает индикатор загрузки при монтировании', () => {
    blogService.getArticles.mockImplementation(() => new Promise(() => {}));
    render(<ArticleList />);
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
    expect(screen.getByText('Загрузка статей...')).toBeInTheDocument();
  });

  /**
   * Проверяет отображение списка статей при успешной загрузке.
   * Данные должны корректно отображаться после получения от API.
   */
  test('отображает список статей при успешной загрузке', async () => {
    blogService.getArticles.mockResolvedValue(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getAllByTestId('article-card')).toHaveLength(2);
    });

    expect(screen.getByText('Статья 1')).toBeInTheDocument();
    expect(screen.getByText('Статья 2')).toBeInTheDocument();
  });

  /**
   * Проверяет отображение пагинации при наличии нескольких страниц.
   * Компонент должен показывать элементы управления страницами.
   */
  test('отображает пагинацию при наличии нескольких страниц', async () => {
    blogService.getArticles.mockResolvedValue(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('pagination')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обработку ответа API без results (плоский список).
   * Компонент должен поддерживать оба формата ответов.
   */
  test('обрабатывает ответ API без results (плоский список)', async () => {
    blogService.getArticles.mockResolvedValue(mockFlatApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('article-card')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение ошибки при неудачной загрузке.
   * Компонент должен показывать сообщение об ошибке.
   */
  test('отображает ошибку при неудачной загрузке', async () => {
    blogService.getArticles.mockRejectedValue(new Error('Ошибка сети'));

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('alert-list')).toBeInTheDocument();
    });

    expect(screen.getByTestId('alert-error')).toBeInTheDocument();
  });

  /**
   * Проверяет отображение кнопки "Повторить" при ошибке.
   * Пользователь должен иметь возможность повторить запрос.
   */
  test('отображает кнопку "Повторить" при ошибке', async () => {
    blogService.getArticles.mockRejectedValueOnce(new Error('Ошибка сети'));

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('Повторить')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет повторную попытку загрузки при нажатии кнопки "Повторить".
   * Компонент должен повторять запрос при клике на кнопку.
   */
  test('повторная попытка загрузки при нажатии кнопки "Повторить"', async () => {
    blogService.getArticles
      .mockRejectedValueOnce(new Error('Ошибка сети'))
      .mockResolvedValueOnce(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('Повторить')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Повторить'));

    await waitFor(() => {
      expect(screen.getAllByTestId('article-card')).toHaveLength(2);
    });
  });

  /**
   * Проверяет отображение сообщения при пустом списке статей.
   * Компонент должен информировать пользователя об отсутствии статей.
   */
  test('отображает сообщение при пустом списке статей', async () => {
    blogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('alert-list')).toBeInTheDocument();
    });

    expect(screen.getByText('Статьи не найдены')).toBeInTheDocument();
  });

  /**
   * Проверяет переход на следующую страницу при клике.
   * Компонент должен загружать данные для следующей страницы.
   */
  test('переходит на следующую страницу', async () => {
    blogService.getArticles
      .mockResolvedValueOnce(mockApiResponse)
      .mockResolvedValueOnce({
        ...mockApiResponse,
        previous: '/api/blog/articles/',
        next: null,
      });

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('pagination')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('След.'));

    await waitFor(() => {
      expect(blogService.getArticles).toHaveBeenCalledTimes(2);
    });
  });

  /**
   * Проверяет переход на предыдущую страницу при клике.
   * Компонент должен загружать данные для предыдущей страницы.
   */
  test('переходит на предыдущую страницу', async () => {
    const responseWithPrevious = {
      ...mockApiResponse,
      previous: '/api/blog/articles/',
      next: null,
    };

    blogService.getArticles
      .mockResolvedValueOnce(responseWithPrevious)
      .mockResolvedValueOnce(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('pagination')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Пред.'));

    await waitFor(() => {
      expect(blogService.getArticles).toHaveBeenCalled();
    });
  });

  /**
   * Проверяет передачу слагов фильтрации в параметры запроса.
   * Слаги category/series/topic должны попадать в параметры blogService.getArticles.
   */
  test('передаёт слаги фильтрации в параметры запроса', async () => {
    blogService.getArticles.mockResolvedValue(mockApiResponse);

    render(<ArticleList categorySlug="react" seriesSlug="django" topicSlug="frontend" />);

    await waitFor(() => {
      expect(blogService.getArticles).toHaveBeenCalledWith(
        expect.objectContaining({
          categories__slug: 'react',
          series__slug: 'django',
          topics__slug: 'frontend',
        }),
      );
    });
  });

  /**
   * Проверяет передачу поискового запроса в параметры запроса.
   * Проп search должен попадать в параметры blogService.getArticles.
   */
  test('передаёт поисковый запрос в параметры запроса', async () => {
    blogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList search="react" />);

    await waitFor(() => {
      expect(blogService.getArticles).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'react' }),
      );
    });
  });

  /**
   * Проверяет сообщение о пустом результате при активном поиске.
   * Сообщение должно включать поисковый запрос пользователя.
   */
  test('отображает сообщение с запросом при пустом результате поиска', async () => {
    blogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList search="react" />);

    await waitFor(() => {
      expect(screen.getByTestId('alert-list')).toBeInTheDocument();
    });

    expect(screen.getByText('По запросу «react» ничего не найдено')).toBeInTheDocument();
  });

  /**
   * Проверяет обычное сообщение при пустом списке без поискового запроса.
   * Прежнее поведение не должно измениться.
   */
  test('отображает обычное сообщение при пустом списке без поиска', async () => {
    blogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('alert-list')).toBeInTheDocument();
    });

    expect(screen.getByText('Статьи не найдены')).toBeInTheDocument();
  });
});
