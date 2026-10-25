import React, { useCallback, useEffect, useRef } from 'react';
import { Container } from 'react-bootstrap';
import PhotoCard from '@components/Gallery/Photo/PhotoCard';
import Spinner from '@components/Spinner/Spinner';
import LoadingError from '@components/Alert/LoadingError';
import AlertList from '@components/Alert/AlertList';
import Pagination from '@components/Pagination/Pagination';
import { galleryService } from '@services';
import { parseListResponse } from '@utils/pagination';
import { searchEmptyMessage } from '@utils/messages';
import { useApiData, useMasonry, usePagination } from '@hooks';

/** Свойства компонента списка фотографий. */
export interface PhotoListProps {
  /** ID альбома: включает режим страницы альбома без пагинации. */
  albumId?: number | null;
  /** Слаг тега для фильтрации (tags__slug); URL фильтра строится во фронтенде. */
  tagSlug?: string;
  /** Поисковый запрос для фильтрации (search). */
  search?: string;
}

/**
 * Компонент списка фотографий галереи.
 *
 * Загружает и отображает список фотографий через сервис галереи.
 * На странице альбома (проп albumId) фотографии берутся из детального
 * ответа альбома целиком, без пагинации; в остальных режимах список
 * построен по страницам.
 *
 * @example
 * <PhotoList />
 *
 * @example
 * <PhotoList albumId={1} />
 *
 * @example
 * <PhotoList search="закат" />
 */
const PhotoList = ({ albumId = null, tagSlug, search }: PhotoListProps) => {
  const { currentPage, totalPages, hasNext, hasPrevious, nextPage, previousPage, goToPage, setTotalPages } =
    usePagination({ initialPage: 1 });

  // Смена фильтров сбрасывает пагинацию на первую страницу; ссылка на goToPage
  // держится в ref: идентичность функции меняется при каждом переходе страницы
  const goToPageRef = useRef(goToPage);
  useEffect(() => {
    goToPageRef.current = goToPage;
  });

  useEffect(() => {
    goToPageRef.current(1);
  }, [tagSlug, search]);

  const loadPhotos = useCallback(async () => {
    if (albumId !== null) {
      const album = await galleryService.getAlbum(albumId);
      // Фотографии альбома приходят готовым массивом без пагинации
      return parseListResponse(album.photos).items;
    }
    const data = await galleryService.getPhotos({ tags__slug: tagSlug, search, page: currentPage });
    const parsed = parseListResponse(data);
    setTotalPages(parsed.totalPages);
    return parsed.items;
  }, [albumId, tagSlug, search, currentPage, setTotalPages]);

  const { data, loading, error, refetch } = useApiData(loadPhotos);
  const photos = data ?? [];

  // Прокрутка страницы вверх при смене страницы пагинации
  const previousPageRef = useRef<number | null>(null);
  useEffect(() => {
    if (previousPageRef.current !== null && previousPageRef.current !== currentPage) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    previousPageRef.current = currentPage;
  }, [currentPage]);

  // Хук вызывается безусловно до ранних выходов; без отрисованной сетки он бездействует
  const { containerRef, markImageReady, revealedIds } = useMasonry(photos);

  // Отображение индикатора загрузки
  if (loading) {
    return <Spinner message="Загрузка фотографий..." />;
  }

  // Отображение ошибки с кнопкой повтора
  if (error) {
    return <LoadingError message={error} onRetry={refetch} />;
  }

  // Отображение сообщения о пустом списке фотографий;
  // при активном поиске сообщение включает запрос пользователя
  if (photos.length === 0) {
    const emptyMessage = searchEmptyMessage(search, 'Нет доступных фотографий');
    return <AlertList messages={[{ message: emptyMessage, level: 'info' }]} />;
  }

  // Отображение списка фотографий; в режиме альбома пагинации нет
  return (
    <Container>
      <div ref={containerRef} className="masonry-grid">
        <div className="masonry-sizer" />
        {photos.map((photo) => (
          <div key={photo.id} className="masonry-item" data-id={photo.id}>
            <PhotoCard
              photo={photo}
              revealed={revealedIds.has(photo.id)}
              onImageLoad={() => markImageReady(photo.id)}
            />
          </div>
        ))}
      </div>
      {albumId === null && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          hasNext={hasNext}
          hasPrevious={hasPrevious}
          onPageChange={goToPage}
          onNext={nextPage}
          onPrevious={previousPage}
        />
      )}
    </Container>
  );
};

export default PhotoList;
