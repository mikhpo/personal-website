import React, { useCallback, useEffect, useState } from 'react';
import { Container } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import AlbumCard from '@components/Gallery/Album/AlbumCard';
import usePagination from '@hooks/usePagination';
import useMasonry from '@hooks/useMasonry';
import Pagination from '@components/Pagination/Pagination';
import { buildApiUrl } from '@utils/apiUrl';
import type { components } from '../../../types/api-schema';
import type { Paginated } from '../../../types/pagination';

type AlbumList = components['schemas']['AlbumList'];

/** Свойства компонента списка альбомов. */
export interface AlbumListProps {
  /** Базовый URL endpoint альбомов. */
  apiUrl?: string;
  /** Слаг тега для фильтрации (tags__slug); URL фильтра строится во фронтенде. */
  tagSlug?: string;
  /** Поисковый запрос для фильтрации (search). */
  search?: string;
}

/**
 * Компонент списка альбомов с пагинацией.
 *
 * Загружает и отображает список альбомов из API, обрабатывая состояния
 * загрузки, ошибки и пустого списка. Отображает альбомы masonry-сеткой
 * карточек и поддерживает навигацию по страницам.
 *
 * @example
 * <AlbumList />
 *
 * @example
 * <AlbumList search="горы" />
 */
const AlbumList = ({ apiUrl = '/api/gallery/albums/', tagSlug, search }: AlbumListProps) => {
  const [albums, setAlbums] = useState<AlbumList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { currentPage, totalPages, hasNext, hasPrevious, nextPage, previousPage, goToPage, setTotalPages } =
    usePagination({ initialPage: 1 });

  /**
   * Выполняет HTTP-запрос к API для получения списка альбомов.
   *
   * useCallback с зависимостью [apiUrl, tagSlug, search] гарантирует, что
   * функция не пересоздается при каждом рендере, и ее безопасно использовать
   * в зависимостях других хуков без риска бесконечного цикла перерисовки.
   */
  const fetchAlbumsRequest = useCallback(
    async (page = 1): Promise<Paginated<AlbumList> | AlbumList[]> => {
      const url = buildApiUrl(apiUrl, { tags__slug: tagSlug, search, page });

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Ошибка загрузки: ${response.status}`);
      }

      return response.json();
    },
    [apiUrl, tagSlug, search],
  );

  /**
   * Загружает альбомы для указанной страницы и обновляет состояние компонента.
   *
   * Стабильность ссылки критична для корректной работы useEffect: функция
   * пересоздается только при изменении fetchAlbumsRequest или setTotalPages.
   */
  const loadAlbums = useCallback(
    async (page: number) => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchAlbumsRequest(page);
        // До нормализации (фаза 6) конверт читается как объединение: массив или конверт
        const raw = Array.isArray(data) ? data : data.results || data;
        const albumsList = Array.isArray(raw) ? raw : [];
        setAlbums(albumsList);

        if (!Array.isArray(data) && data.total_pages) {
          setTotalPages(data.total_pages);
        }

        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      }
    },
    [fetchAlbumsRequest, setTotalPages],
  );

  // Загружает альбомы при изменении текущей страницы; loadAlbums стабильна
  // благодаря useCallback, поэтому эффект срабатывает только при реальном
  // изменении currentPage
  useEffect(() => {
    loadAlbums(currentPage);
  }, [currentPage, loadAlbums]);

  const handlePageChange = (page: number) => {
    goToPage(page);
  };

  // Хук вызывается безусловно до ранних выходов; без отрисованной сетки он бездействует
  const { containerRef, markImageReady, revealedIds } = useMasonry(albums);

  if (loading) {
    return <Spinner message="Загрузка альбомов..." />;
  }

  if (error) {
    return <LoadingError message={error} onRetry={() => loadAlbums(currentPage)} />;
  }

  if (albums.length === 0) {
    const emptyMessage = search ? `По запросу "${search}" ничего не найдено` : 'Нет доступных альбомов';
    return <AlertList messages={[{ message: emptyMessage, level: 'info' }]} />;
  }

  return (
    <Container data-testid="album-list-container">
      <div ref={containerRef} className="masonry-grid">
        <div className="masonry-sizer" />
        {albums.map((album) => (
          <div key={album.id} className="masonry-item" data-id={album.id}>
            <AlbumCard album={album} revealed={revealedIds.has(album.id)} onImageLoad={markImageReady} />
          </div>
        ))}
      </div>
      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          hasNext={hasNext}
          hasPrevious={hasPrevious}
          onNext={nextPage}
          onPrevious={previousPage}
          onPageChange={handlePageChange}
          type="navigation"
        />
      )}
    </Container>
  );
};

export default AlbumList;
