/**
 * Тесты для компонента SearchResults.
 *
 * Проверяют параллельную загрузку статей и альбомов с ограничением размера
 * выборки, рендер секций результатов со ссылками на полные списки разделов,
 * а также состояния подсказки при пустом запросе, загрузки и ошибки.
 * Сервисы API подменяются автомоком jest.mock('@services').
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import SearchResults from './SearchResults';
import { blogService, galleryService } from '@services';

// Мок для сервисов API
jest.mock('@services');

// Мок для компонента ArticleCard
jest.mock('@components/Blog/Article/ArticleCard', () => {
  return function MockArticleCard({ article }) {
    return <div data-testid="article-card">{article.title}</div>;
  };
});

// Мок для компонента AlbumCard
jest.mock('@components/Gallery/Album/AlbumCard', () => {
  return function MockAlbumCard({ album }) {
    return <div data-testid="album-card">{album.name}</div>;
  };
});

// Мок для компонента Spinner
jest.mock('@components/Spinner/Spinner', () => {
  return function MockSpinner({ message }) {
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

describe('SearchResults', () => {
  /**
   * Мок ответа API статей
   */
  const mockArticles = {
    count: 12,
    results: [
      { id: 1, title: 'Статья о Django', content: 'Контент' },
      { id: 2, title: 'Статья о React', content: 'Контент' },
    ],
  };

  /**
   * Мок ответа API альбомов
   */
  const mockAlbums = {
    count: 3,
    results: [
      { id: 1, name: 'Горы', description: 'Описание' },
      { id: 2, name: 'Море', description: 'Описание' },
    ],
  };

  afterEach(() => {
    jest.resetAllMocks();
  });

  /**
   * Пустой запрос показывает подсказку и не выполняет обращений к API.
   */
  test('пустой запрос показывает подсказку без обращения к API', () => {
    render(<SearchResults search="" />);

    expect(screen.getByText(/Введите поисковый запрос/)).toBeInTheDocument();
    expect(blogService.getArticles).not.toHaveBeenCalled();
    expect(galleryService.getAlbums).not.toHaveBeenCalled();
  });

  /**
   * При активном запросе оба сервиса вызываются параллельно с запросом
   * и ограничением размера выборки.
   */
  test('запрашивает статьи и альбомы с поисковым запросом и page_size', async () => {
    blogService.getArticles.mockResolvedValue(mockArticles);
    galleryService.getAlbums.mockResolvedValue(mockAlbums);

    render(<SearchResults search="react" />);

    await waitFor(() => {
      expect(screen.getAllByTestId('article-card')).toHaveLength(2);
    });

    expect(blogService.getArticles).toHaveBeenCalledWith({ search: 'react', page_size: 5 });
    expect(galleryService.getAlbums).toHaveBeenCalledWith({ search: 'react', page_size: 6 });
  });

  /**
   * Результаты отображаются в секциях "Статьи" и "Альбомы" со ссылками
   * на полные списки разделов.
   */
  test('отображает секции статей и альбомов со ссылками на полные результаты', async () => {
    blogService.getArticles.mockResolvedValue(mockArticles);
    galleryService.getAlbums.mockResolvedValue(mockAlbums);

    render(<SearchResults search="react" />);

    await waitFor(() => {
      expect(screen.getByText('Статьи (2)')).toBeInTheDocument();
    });

    expect(screen.getByText('Альбомы (2)')).toBeInTheDocument();
    expect(screen.getByText('Статья о Django')).toBeInTheDocument();
    expect(screen.getByText('Статья о React')).toBeInTheDocument();
    expect(screen.getByText('Горы')).toBeInTheDocument();
    expect(screen.getByText('Море')).toBeInTheDocument();

    const articlesLink = screen.getByText('Все статьи');
    expect(articlesLink).toHaveAttribute('href', '/blog/?search=react');

    const albumsLink = screen.getByText('Все альбомы');
    expect(albumsLink).toHaveAttribute('href', '/gallery/albums/?search=react');
  });

  /**
   * Пустая секция показывает сообщение "Ничего не найдено".
   */
  test('пустые секции показывают сообщение об отсутствии результатов', async () => {
    blogService.getArticles.mockResolvedValue({ count: 0, results: [] });
    galleryService.getAlbums.mockResolvedValue({ count: 0, results: [] });

    render(<SearchResults search="react" />);

    await waitFor(() => {
      expect(screen.getByText('Статьи (0)')).toBeInTheDocument();
    });

    expect(screen.getByText('Альбомы (0)')).toBeInTheDocument();
    expect(screen.getAllByText('Ничего не найдено')).toHaveLength(2);
  });

  /**
   * Во время загрузки отображается индикатор загрузки.
   */
  test('отображает индикатор загрузки', () => {
    blogService.getArticles.mockImplementation(() => new Promise(() => {}));
    galleryService.getAlbums.mockImplementation(() => new Promise(() => {}));

    render(<SearchResults search="react" />);

    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  /**
   * Ошибка загрузки отображается через AlertList с кнопкой повтора.
   */
  test('отображает ошибку с кнопкой повтора', async () => {
    blogService.getArticles.mockRejectedValue(new Error('Network error'));
    galleryService.getAlbums.mockResolvedValue(mockAlbums);

    render(<SearchResults search="react" />);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });

    expect(screen.getByText('Повторить')).toBeInTheDocument();
  });
});
