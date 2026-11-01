/**
 * Тесты для компонента ArticleList.
 *
 * Проверяет корректность отображения списка статей с загрузкой из API,
 * включая обработку состояний загрузки, ошибок, пагинацию и пустого списка,
 * а также контракт превью: разметка статьи, обрезка длинных текстов,
 * фотографии и ссылка "Читать дальше".
 */

import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import ArticleList from './ArticleList';
import type { Paginated } from '@api-types/pagination';
import { makeArticle, paginate } from '@test-utils';
import { blogService } from '@services';

// Мок для blogService
jest.mock('@services');

// Автомок @services: обертка jest.mocked открывает mock-методы сервиса
const mockedBlogService = jest.mocked(blogService);

describe('ArticleList', () => {
  /**
   * Мок успешного ответа API с результатами
   */
  const mockApiResponse = paginate(
    [
      makeArticle({ id: 1, slug: 'article-1', title: 'Статья 1', content: 'Контент 1' }),
      makeArticle({ id: 2, slug: 'article-2', title: 'Статья 2', content: 'Контент 2' }),
    ],
    { count: 25, total_pages: 2, next: '/api/blog/articles/?page=2' },
  );

  /**
   * Мок успешного ответа API без results (плоский список)
   */
  // Плоский список вместо конверта нарушает тип сервиса сознательно:
  // компонент должен переживать устаревший формат ответа
  const mockFlatApiResponse = [
    makeArticle({ id: 1, slug: 'article-1', title: 'Статья 1', content: 'Контент 1' }),
  ] as unknown as Paginated<ReturnType<typeof makeArticle>>;

  /**
   * Мок пустого ответа API
   */
  const mockEmptyApiResponse = paginate([], { count: 0 });

  /** Длинный текст: заведомо больше порога в 200 слов. */
  const generateLongContent = () => Array(250).fill('слово').join(' ');

  /** Рендерит список с одной статьей из мока сервиса и дожидается вывода. */
  const renderWithArticle = async (article: ReturnType<typeof makeArticle>) => {
    mockedBlogService.getArticles.mockResolvedValue(paginate([article]));
    const view = render(<ArticleList />);
    await waitFor(() => {
      expect(screen.getByText(article.title)).toBeInTheDocument();
    });
    return view;
  };

  beforeEach(() => {
    mockedBlogService.getArticles.mockClear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  /**
   * Проверяет отображение индикатора загрузки при монтировании компонента.
   * Компонент должен показывать спиннер до получения данных от API.
   */
  test('отображает индикатор загрузки при монтировании', () => {
    mockedBlogService.getArticles.mockImplementation(() => new Promise(() => {}));
    render(<ArticleList />);
    expect(screen.getByText('Загрузка статей...', { selector: 'p' })).toBeInTheDocument();
  });

  /**
   * Проверяет отображение списка статей при успешной загрузке.
   * Заголовки статей становятся ссылками на страницы статей.
   */
  test('отображает список статей при успешной загрузке', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('Статья 1')).toBeInTheDocument();
    });

    expect(screen.getByText('Статья 2')).toBeInTheDocument();
  });

  /**
   * Проверяет отображение пагинации при наличии нескольких страниц.
   * Компонент должен показывать элементы управления страницами.
   */
  test('отображает пагинацию при наличии нескольких страниц', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByRole('navigation', { name: 'Навигация по страницам' })).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обработку ответа API без results (плоский список).
   * Компонент должен поддерживать оба формата ответов.
   */
  test('обрабатывает ответ API без results (плоский список)', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockFlatApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('Статья 1')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение ошибки при неудачной загрузке.
   * Компонент должен показывать сообщение об ошибке.
   */
  test('отображает ошибку при неудачной загрузке', async () => {
    mockedBlogService.getArticles.mockRejectedValue(new Error('Ошибка сети'));

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('Ошибка сети')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение кнопки "Повторить" при ошибке.
   * Пользователь должен иметь возможность повторить запрос.
   */
  test('отображает кнопку "Повторить" при ошибке', async () => {
    mockedBlogService.getArticles.mockRejectedValueOnce(new Error('Ошибка сети'));

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('retry-button')).toBeInTheDocument();
    });

    expect(screen.getByText('Повторить')).toBeInTheDocument();
  });

  /**
   * Проверяет повторную попытку загрузки при нажатии кнопки "Повторить".
   * Компонент должен повторять запрос при клике на кнопку.
   */
  test('повторная попытка загрузки при нажатии кнопки "Повторить"', async () => {
    mockedBlogService.getArticles
      .mockRejectedValueOnce(new Error('Ошибка сети'))
      .mockResolvedValueOnce(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByTestId('retry-button')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('retry-button'));

    await waitFor(() => {
      expect(screen.getByText('Статья 1')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет отображение сообщения при пустом списке статей.
   * Компонент должен информировать пользователя об отсутствии статей.
   */
  test('отображает сообщение при пустом списке статей', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('Статьи не найдены')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет переход на следующую страницу при клике.
   * Компонент должен загружать данные для следующей страницы.
   */
  test('переходит на следующую страницу', async () => {
    mockedBlogService.getArticles.mockResolvedValueOnce(mockApiResponse).mockResolvedValueOnce({
      ...mockApiResponse,
      previous: '/api/blog/articles/',
      next: null,
    });

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('следующая')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('следующая'));

    await waitFor(() => {
      expect(mockedBlogService.getArticles).toHaveBeenCalledTimes(2);
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

    mockedBlogService.getArticles
      .mockResolvedValueOnce(mockApiResponse)
      .mockResolvedValueOnce(responseWithPrevious)
      .mockResolvedValueOnce(mockApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('следующая')).toBeInTheDocument();
    });

    // Переход на вторую страницу, затем назад на первую
    fireEvent.click(screen.getByText('следующая'));

    await waitFor(() => {
      expect(mockedBlogService.getArticles).toHaveBeenCalledTimes(2);
    });

    fireEvent.click(screen.getByText('предыдущая'));

    await waitFor(() => {
      expect(mockedBlogService.getArticles).toHaveBeenCalledTimes(3);
    });
  });

  /**
   * Проверяет передачу слагов фильтрации в параметры запроса.
   * Слаги category/series/topic должны попадать в параметры mockedBlogService.getArticles.
   */
  test('передаёт слаги фильтрации в параметры запроса', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockApiResponse);

    render(<ArticleList categorySlug="react" seriesSlug="django" topicSlug="frontend" />);

    await waitFor(() => {
      expect(mockedBlogService.getArticles).toHaveBeenCalledWith(
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
   * Проп search должен попадать в параметры mockedBlogService.getArticles.
   */
  test('передаёт поисковый запрос в параметры запроса', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList search="react" />);

    await waitFor(() => {
      expect(mockedBlogService.getArticles).toHaveBeenCalledWith(expect.objectContaining({ search: 'react' }));
    });
  });

  /**
   * Проверяет сообщение о пустом результате при активном поиске.
   * Сообщение должно включать поисковый запрос пользователя.
   */
  test('отображает сообщение с запросом при пустом результате поиска', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList search="react" />);

    await waitFor(() => {
      expect(screen.getByText('По запросу "react" ничего не найдено')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет обычное сообщение при пустом списке без поискового запроса.
   * Прежнее поведение не должно измениться.
   */
  test('отображает обычное сообщение при пустом списке без поиска', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockEmptyApiResponse);

    render(<ArticleList />);

    await waitFor(() => {
      expect(screen.getByText('Статьи не найдены')).toBeInTheDocument();
    });
  });

  /**
   * Проверяет ссылку заголовка при отсутствии url статьи: срабатывает
   * fallback на страницу статьи по идентификатору.
   */
  test('ведет ссылку заголовка на страницу статьи при отсутствии url', async () => {
    await renderWithArticle(makeArticle({ id: 1, title: 'Тестовая статья', url: undefined }));

    expect(screen.getByText('Тестовая статья').closest('a')).toHaveAttribute('href', '/blog/1/');
  });

  /**
   * Проверяет, что фотография из начала статьи видна в превью длинной статьи.
   * Изображение находится до точки обрезки и попадает в карточку.
   */
  test('отображает фотографию в превью длинной статьи', async () => {
    await renderWithArticle(
      makeArticle({
        id: 7,
        title: 'Статья с фотографией',
        content: '<p><img src="/media/photo.jpg" alt="Фотография" /></p><p>' + generateLongContent() + '</p>',
      }),
    );

    const photo = screen.getByRole('img', { name: 'Фотография' });
    expect(photo).toHaveAttribute('src', '/media/photo.jpg');
  });

  /**
   * Проверяет, что HTML-форматирование короткой статьи сохраняется в превью:
   * контент рендерится как разметка, а не как текст.
   */
  test('отображает HTML-форматирование в превью короткой статьи', async () => {
    const { container } = await renderWithArticle(
      makeArticle({
        id: 8,
        title: 'Форматированная статья',
        content: '<p>Это <b>жирный</b> текст.</p>',
      }),
    );

    expect(container.querySelector('.card-text b')).toHaveTextContent('жирный');
  });

  /**
   * Проверяет, что длинная статья обрезается до 50 слов: начало текста в
   * превью есть, хвост - нет, разметка замкнута.
   */
  test('обрезает длинную статью до 50 слов с замкнутой разметкой', async () => {
    const numberedWords = Array.from({ length: 250 }, (_, index) => `слово${index + 1}`).join(' ');
    const { container } = await renderWithArticle(
      makeArticle({
        id: 9,
        title: 'Нумерованная статья',
        content: `<p>${numberedWords}</p>`,
      }),
    );

    const preview = container.querySelector('.card-text');
    expect(preview).toHaveTextContent('слово1');
    expect(preview).toHaveTextContent('слово50');
    expect(preview).not.toHaveTextContent('слово51');
    expect(preview?.innerHTML.endsWith('</p>')).toBe(true);
  });

  /**
   * Проверяет, что для длинной статьи отображается ссылка "Читать дальше"
   * со ссылкой на страницу статьи.
   */
  test('отображает ссылку "Читать дальше" для длинной статьи', async () => {
    await renderWithArticle(
      makeArticle({
        id: 3,
        title: 'Длинная статья',
        content: generateLongContent(),
        url: undefined,
      }),
    );

    expect(screen.getByText('Читать дальше')).toHaveAttribute('href', '/blog/3/');
  });

  /**
   * Проверяет, что для короткой статьи ссылка "Читать дальше" не отображается:
   * при количестве слов не более 200 усечение не применяется.
   */
  test('не отображает ссылку "Читать дальше" для короткой статьи', async () => {
    await renderWithArticle(
      makeArticle({
        id: 2,
        title: 'Короткая статья',
        content: '<p>Это короткий текст статьи.</p>',
      }),
    );

    expect(screen.queryByText('Читать дальше')).not.toBeInTheDocument();
  });
});
