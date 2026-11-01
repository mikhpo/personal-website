import React, { useCallback } from 'react';
import { Container } from 'react-bootstrap';
import Spinner from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import LoadingError from '@components/Alert/LoadingError';
import AlbumCard from '@components/Gallery/Album/AlbumCard';
import Pagination from '@components/Pagination/Pagination';
import { galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import { searchEmptyMessage } from '@utils/messages';
import { useApiData, useMasonry, usePagination } from '@hooks';

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
  const { currentPage, totalPages, hasNext, hasPrevious, nextPage, previousPage, goToPage, setTotalPages } =
    usePagination({ initialPage: 1 });

  /**
   * Загружает альбомы для текущей страницы.
   *
   * Смена ссылки функции (фильтры, номер страницы) запускает загрузку хуком.
   */
  const loadAlbums = useCallback(async () => {
    const data = await galleryService.getAlbums({ tags__slug: tagSlug, search, page: currentPage });
    const parsed = parseListResponse(data);
    setTotalPages(parsed.totalPages);
    return parsed.items;
  }, [tagSlug, search, currentPage, setTotalPages]);

  const { data, loading, error, refetch } = useApiData(loadAlbums);
  const albums = data ?? [];

  const handlePageChange = (page: number) => {
    goToPage(page);
  };

  // Хук вызывается безусловно до ранних выходов; без отрисованной сетки он бездействует
  const { containerRef, markImageReady, revealedIds } = useMasonry(albums);

  if (loading) {
    return <Spinner message="Загрузка альбомов..." />;
  }

  if (error) {
    return <LoadingError message={error} onRetry={refetch} />;
  }

  if (albums.length === 0) {
    const emptyMessage = searchEmptyMessage(search, 'Нет доступных альбомов');
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
