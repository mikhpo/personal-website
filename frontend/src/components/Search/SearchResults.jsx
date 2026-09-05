import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Button, Col, Row } from 'react-bootstrap';
import ArticleCard from '@components/Blog/Article/ArticleCard';
import AlbumCard from '@components/Gallery/Album/AlbumCard';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import { blogService, galleryService } from '@services';

/**
 * Количество статей в секции результатов общего поиска
 * @type {number}
 */
const ARTICLES_PAGE_SIZE = 5;

/**
 * Количество альбомов в секции результатов общего поиска
 * @type {number}
 */
const ALBUMS_PAGE_SIZE = 6;

/**
 * Компонент результатов общего поиска по сайту.
 *
 * Запрашивает статьи и альбомы параллельно с ограничением размера выборки
 * и отображает их в отдельных секциях со ссылками на полные результаты
 * разделов. Пагинация на странице не используется: полный список открывается
 * по ссылке в соответствующем разделе.
 *
 * @component
 * @param {Object} props - Свойства компонента
 * @param {string} [props.search] - Поисковый запрос; пустое значение показывает подсказку
 * @return {JSX.Element} Компонент результатов поиска
 *
 * @example
 * // Результаты поиска по запросу из URL страницы /search/
 * <SearchResults search="django" />
 */
const SearchResults = ({ search }) => {
  /**
   * Найденные статьи (топ выборки)
   * @type {[Array, function]}
   */
  const [articles, setArticles] = useState([]);

  /**
   * Найденные альбомы (топ выборки)
   * @type {[Array, function]}
   */
  const [albums, setAlbums] = useState([]);

  /**
   * Состояние загрузки данных
   * @type {[boolean, function]}
   */
  const [loading, setLoading] = useState(Boolean(search));

  /**
   * Состояние ошибки при загрузке данных
   * @type {[string|null, function]}
   */
  const [error, setError] = useState(null);

  /**
   * Счётчик повторных попыток загрузки
   * @type {[number, function]}
   */
  const [retryCount, setRetryCount] = useState(0);

  /**
   * Загружает статьи и альбомы параллельно с одинаковым поисковым запросом.
   *
   * @function loadResults
   * @return {Promise<void>}
   */
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
      setArticles(articlesData.results || articlesData);
      setAlbums(albumsData.results || albumsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search]);

  /**
   * Эффект загрузки результатов при изменении запроса или повторной попытке
   */
  useEffect(() => {
    loadResults();
  }, [loadResults, retryCount]);

  // Пустой запрос: подсказка без обращения к API
  if (!search) {
    return (
      <p className="text-muted">Введите поисковый запрос, чтобы найти статьи и альбомы.</p>
    );
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
              <Button
                variant="outline-primary"
                size="sm"
                onClick={() => setRetryCount((count) => count + 1)}
              >
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

SearchResults.propTypes = {
  search: PropTypes.string,
};

SearchResults.defaultProps = {
  search: '',
};

export default SearchResults;
