/**
 * Тесты для компонента SearchResults.
 *
 * Проверяют параллельную загрузку статей и альбомов с ограничением размера
 * выборки, рендер секций результатов со ссылками на полные списки разделов,
 * а также состояния подсказки при пустом запросе, загрузки и ошибки.
 * Сервисы API подменяются автомоком jest.mock('@services').
 */

import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import SearchResults from './SearchResults';
import type { ArticleCardProps } from '@components/Blog/Article/ArticleCard';
import type { AlbumCardProps } from '@components/Gallery/Album/AlbumCard';
import type { SpinnerProps } from '@components/Spinner/Spinner';
import type { AlertListProps } from '@components/Alert/AlertList';
import { makeAlbum, makeArticle, paginate } from '@test-utils';
import { blogService, galleryService } from '@services';

// Мок для сервисов API
jest.mock('@services');

// Автомоки @services: обертка jest.mocked открывает mock-методы сервисов
const mockedBlogService = jest.mocked(blogService);
const mockedGalleryService = jest.mocked(galleryService);

// Мок для компонента ArticleCard
jest.mock('@components/Blog/Article/ArticleCard', () => {
  return function MockArticleCard({ article }: ArticleCardProps) {
    return <div data-testid="article-card">{article.title}</div>;
  };
});

// Мок для компонента AlbumCard
jest.mock('@components/Gallery/Album/AlbumCard', () => {
  return function MockAlbumCard({ album }: AlbumCardProps) {
    return <div data-testid="album-card">{album.name}</div>;
  };
});

// Мок для компонента Spinner
jest.mock('@components/Spinner/Spinner', () => {
  return function MockSpinner({ message }: SpinnerProps) {
    return <div data-testid="spinner">{message}</div>;
  };
});

// Мок для компонента AlertList
jest.mock('@components/Alert/AlertList', () => {
  return function MockAlertList({ messages = [] }: AlertListProps) {
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
  const mockArticles = paginate(
    [
      makeArticle({ id: 1, title: 'Статья о Django', content: 'Контент' }),
      makeArticle({ id: 2, title: 'Статья о React', content: 'Контент' }),
    ],
    { count: 12 },
  );

  /**
   * Мок ответа API альбомов
   */
  const mockAlbums = paginate(
    [
      makeAlbum({ id: 1, name: 'Горы', description: 'Описание' }),
      makeAlbum({ id: 2, name: 'Море', description: 'Описание' }),
    ],
    { count: 3 },
  );

  afterEach(() => {
    jest.resetAllMocks();
  });

  /**
   * Пустой запрос показывает подсказку и не выполняет обращений к API.
   */
  test('пустой запрос показывает подсказку без обращения к API', () => {
    render(<SearchResults search="" />);

    expect(screen.getByText(/Введите поисковый запрос/)).toBeInTheDocument();
    expect(mockedBlogService.getArticles).not.toHaveBeenCalled();
    expect(mockedGalleryService.getAlbums).not.toHaveBeenCalled();
  });

  /**
   * При активном запросе оба сервиса вызываются параллельно с запросом
   * и ограничением размера выборки.
   */
  test('запрашивает статьи и альбомы с поисковым запросом и page_size', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockArticles);
    mockedGalleryService.getAlbums.mockResolvedValue(mockAlbums);

    render(<SearchResults search="react" />);

    await waitFor(() => {
      expect(screen.getAllByTestId('article-card')).toHaveLength(2);
    });

    expect(mockedBlogService.getArticles).toHaveBeenCalledWith({ search: 'react', page_size: 5 });
    expect(mockedGalleryService.getAlbums).toHaveBeenCalledWith({ search: 'react', page_size: 6 });
  });

  /**
   * Результаты отображаются в секциях "Статьи" и "Альбомы" со ссылками
   * на полные списки разделов.
   */
  test('отображает секции статей и альбомов со ссылками на полные результаты', async () => {
    mockedBlogService.getArticles.mockResolvedValue(mockArticles);
    mockedGalleryService.getAlbums.mockResolvedValue(mockAlbums);

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
    mockedBlogService.getArticles.mockResolvedValue(paginate([], { count: 0 }));
    mockedGalleryService.getAlbums.mockResolvedValue(paginate([], { count: 0 }));

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
    mockedBlogService.getArticles.mockImplementation(() => new Promise(() => {}));
    mockedGalleryService.getAlbums.mockImplementation(() => new Promise(() => {}));

    render(<SearchResults search="react" />);

    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  /**
   * Ошибка загрузки отображается через AlertList с кнопкой повтора.
   */
  test('отображает ошибку с кнопкой повтора', async () => {
    mockedBlogService.getArticles.mockRejectedValue(new Error('Network error'));
    mockedGalleryService.getAlbums.mockResolvedValue(mockAlbums);

    render(<SearchResults search="react" />);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });

    expect(screen.getByText('Повторить')).toBeInTheDocument();
  });
});
