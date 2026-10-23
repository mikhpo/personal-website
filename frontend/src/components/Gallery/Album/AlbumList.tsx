import React, { useCallback, useEffect, useState } from 'react';
import { Container } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import AlbumCard from '@components/Gallery/Album/AlbumCard';
import usePagination from '@hooks/usePagination';
import useMasonry from '@hooks/useMasonry';
import Pagination from '@components/Pagination/Pagination';
import { galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../../types/api-schema';

type AlbumList = components['schemas']['AlbumList'];

/** Свойства компонента списка альбомов. */
export interface AlbumListProps {
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
const AlbumList = ({ tagSlug, search }: AlbumListProps) => {
  const [albums, setAlbums] = useState<AlbumList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { currentPage, totalPages, hasNext, hasPrevious, nextPage, previousPage, goToPage, setTotalPages } =
    usePagination({ initialPage: 1 });

  /**
   * Загружает альбомы для указанной страницы и обновляет состояние компонента.
   *
   * Стабильность ссылки критична для корректной работы useEffect: функция
   * пересоздается только при изменении tagSlug, search или setTotalPages.
   */
  const loadAlbums = useCallback(
    async (page: number) => {
      setLoading(true);
      setError(null);

      try {
        const data = await galleryService.getAlbums({
          ...(tagSlug ? { tags__slug: tagSlug } : {}),
          ...(search ? { search } : {}),
          page,
        });
        const { items, totalPages } = parseListResponse(data);
        setAlbums(items);
        setTotalPages(totalPages);

        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      }
    },
    [tagSlug, search, setTotalPages],
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
