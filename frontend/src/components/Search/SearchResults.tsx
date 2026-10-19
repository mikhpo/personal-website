import React, { useCallback, useEffect, useState } from 'react';
import { Button, Col, Row } from 'react-bootstrap';
import ArticleCard from '@components/Blog/Article/ArticleCard';
import AlbumCard from '@components/Gallery/Album/AlbumCard';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { blogService, galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../types/api-schema';

type Article = components['schemas']['Article'];
type AlbumList = components['schemas']['AlbumList'];

/** Количество статей в секции результатов общего поиска. */
const ARTICLES_PAGE_SIZE = 5;

/** Количество альбомов в секции результатов общего поиска. */
const ALBUMS_PAGE_SIZE = 6;

/** Свойства компонента результатов общего поиска. */
export interface SearchResultsProps {
  /** Поисковый запрос; пустое значение показывает подсказку. */
  search?: string;
}

/**
 * Компонент результатов общего поиска по сайту.
 *
 * Запрашивает статьи и альбомы параллельно с ограничением размера выборки
 * и отображает их в отдельных секциях со ссылками на полные результаты
 * разделов. Пагинация на странице не используется: полный список открывается
 * по ссылке в соответствующем разделе.
 *
 * @example
 * <SearchResults search="django" />
 */
const SearchResults = ({ search = '' }: SearchResultsProps) => {
  /** Найденные статьи (топ выборки). */
  const [articles, setArticles] = useState<Article[]>([]);

  /** Найденные альбомы (топ выборки). */
  const [albums, setAlbums] = useState<AlbumList[]>([]);

  /** Состояние загрузки данных. */
  const [loading, setLoading] = useState(Boolean(search));

  /** Состояние ошибки при загрузке данных. */
  const [error, setError] = useState<string | null>(null);

  /** Счётчик повторных попыток загрузки. */
  const [retryCount, setRetryCount] = useState(0);

  /** Загружает статьи и альбомы параллельно с одинаковым поисковым запросом. */
  const loadResults = useCallback(async () => {
    if (!search) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [articlesData, albumsData] = await Promise.all([
        blogService.getArticles({ search, page_size: ARTICLES_PAGE_SIZE }),
        galleryService.getAlbums({ search, page_size: ALBUMS_PAGE_SIZE }),
      ]);
      setArticles(parseListResponse(articlesData).items);
      setAlbums(parseListResponse(albumsData).items);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [search]);

  // Эффект загрузки результатов при изменении запроса или повторной попытке
  useEffect(() => {
    loadResults();
  }, [loadResults, retryCount]);

  // Пустой запрос: подсказка без обращения к API
  if (!search) {
    return <p className="text-muted">Введите поисковый запрос, чтобы найти статьи и альбомы.</p>;
  }

  if (loading) {
    return <Spinner message="Загрузка результатов..." />;
  }

  if (error) {
    return (
      <AlertList
        messages={[
          {
            message: error,
            level: 'error',
            actions: (
              <Button variant="outline-primary" size="sm" onClick={() => setRetryCount((count) => count + 1)}>
                Повторить
              </Button>
            ),
          },
        ]}
      />
    );
  }

  return (
    <div>
      <section className="mb-4">
        <h2>Статьи ({articles.length})</h2>
        {articles.length > 0 ? (
          articles.map((article) => <ArticleCard key={article.id} article={article} />)
        ) : (
          <p className="text-muted">Ничего не найдено</p>
        )}
        <a href={`/blog/?search=${encodeURIComponent(search)}`}>Все статьи</a>
      </section>
      <section className="mb-4">
        <h2>Альбомы ({albums.length})</h2>
        {albums.length > 0 ? (
          <Row xs={1} md={4} className="g-4 justify-content-center mb-3">
            {albums.map((album) => (
              <Col key={album.id}>
                <AlbumCard album={album} />
              </Col>
            ))}
          </Row>
        ) : (
          <p className="text-muted">Ничего не найдено</p>
        )}
        <a href={`/gallery/albums/?search=${encodeURIComponent(search)}`}>Все альбомы</a>
      </section>
    </div>
  );
};

export default SearchResults;
