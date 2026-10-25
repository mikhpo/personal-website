import React, { useCallback } from 'react';
import { Button, Col, Row } from 'react-bootstrap';
import ArticleCard from '@components/Blog/Article/ArticleCard';
import AlbumCard from '@components/Gallery/Album/AlbumCard';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { blogService, galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import { useApiData } from '@hooks';
import type { components } from '@api-types/api-schema';

type Article = components['schemas']['Article'];
type AlbumList = components['schemas']['AlbumList'];

/** Результат поиска: топ выборки статей и альбомов. */
interface SearchData {
  articles: Article[];
  albums: AlbumList[];
}

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
  /** Загружает статьи и альбомы параллельно; пустой запрос возвращает пустые секции без сети. */
  const loadResults = useCallback(async (): Promise<SearchData> => {
    if (!search) {
      return { articles: [], albums: [] };
    }

    const [articlesData, albumsData] = await Promise.all([
      blogService.getArticles({ search, page_size: ARTICLES_PAGE_SIZE }),
      galleryService.getAlbums({ search, page_size: ALBUMS_PAGE_SIZE }),
    ]);
    return {
      articles: parseListResponse(articlesData).items,
      albums: parseListResponse(albumsData).items,
    };
  }, [search]);

  const { data, loading, error, refetch } = useApiData(loadResults);
  const articles = data?.articles ?? [];
  const albums = data?.albums ?? [];

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
              <Button variant="outline-primary" size="sm" onClick={refetch}>
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
