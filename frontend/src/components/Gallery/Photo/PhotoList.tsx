import React, { useCallback, useEffect, useState } from 'react';
import { Container, Button } from 'react-bootstrap';
import PhotoCard from '@components/Gallery/Photo/PhotoCard';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import Pagination from '@components/Pagination/Pagination';
import useMasonry from '@hooks/useMasonry';
import { galleryService, api } from '@services';
import { parseListResponse } from '@utils/pagination';
import type { components } from '../../../types/api-schema';
import type { Paginated } from '../../../types/pagination';

type Photo = components['schemas']['Photo'];

/** Состояние данных пагинации списка фотографий. */
interface PaginationState {
  count: number;
  next: string | null;
  previous: string | null;
  currentPage: number;
  totalPages: number;
}

/** Свойства компонента списка фотографий. */
export interface PhotoListProps {
  /** ID альбома: включает режим страницы альбома без пагинации. */
  albumId?: number | null;
  /** Слаг тега для фильтрации (tags__slug); URL фильтра строится во фронтенде. */
  tagSlug?: string;
  /** Поисковый запрос для фильтрации (search). */
  search?: string;
}

const EMPTY_PAGINATION: PaginationState = {
  count: 0,
  next: null,
  previous: null,
  currentPage: 1,
  totalPages: 0,
};

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
  /** Состояние фотографий. */
  const [photos, setPhotos] = useState<Photo[]>([]);

  /** Состояние загрузки данных. */
  const [loading, setLoading] = useState(true);

  /** Состояние ошибки при загрузке данных. */
  const [error, setError] = useState<string | null>(null);

  /** Состояние данных пагинации. */
  const [pagination, setPagination] = useState<PaginationState>(EMPTY_PAGINATION);

  /**
   * Загружает первую страницу списка или полный список альбома.
   */
  const loadPhotos = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (albumId !== null) {
        const album = await galleryService.getAlbum(albumId);
        // Фотографии альбома приходят готовым массивом без пагинации
        const parsed = parseListResponse(album.photos);
        setPhotos(parsed.items);
        setPagination({ ...EMPTY_PAGINATION, count: parsed.count });
      } else {
        const data = await galleryService.getPhotos({
          ...(tagSlug ? { tags__slug: tagSlug } : {}),
          ...(search ? { search } : {}),
          page: 1,
        });
        const parsed = parseListResponse(data);
        setPhotos(parsed.items);
        setPagination({
          count: parsed.count,
          next: parsed.next,
          previous: parsed.previous,
          currentPage: 1,
          totalPages: parsed.totalPages,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, [albumId, tagSlug, search]);

  // Эффект для загрузки фотографий при монтировании и изменении источника данных
  useEffect(() => {
    loadPhotos();
  }, [loadPhotos]);

  /** Применяет ответ страницы к состоянию компонента. */
  const applyPage = (data: Paginated<Photo>, currentPage: number) => {
    const parsed = parseListResponse(data);
    setPhotos(parsed.items);
    setPagination({
      count: parsed.count,
      next: parsed.next,
      previous: parsed.previous,
      currentPage,
      totalPages: parsed.totalPages,
    });
  };

  /** Обработчик изменения страницы пагинации. */
  const handlePageChange = async (page: number) => {
    if (page < 1 || !pagination.totalPages || page > pagination.totalPages) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await galleryService.getPhotos({
        ...(tagSlug ? { tags__slug: tagSlug } : {}),
        ...(search ? { search } : {}),
        page,
      });
      applyPage(data, page);

      // Прокрутить страницу вверх
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  /** Загружает страницу по ссылке пагинации (next или previous). */
  const loadByLink = async (pageUrl: string) => {
    setLoading(true);
    setError(null);

    try {
      const data = await api.get<Paginated<Photo>>(pageUrl);
      const page = currentPageFromUrl(pageUrl);
      applyPage(data, page);

      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  /** Обработчик перехода на следующую страницу. */
  const handleNext = async () => {
    if (pagination.next) {
      await loadByLink(pagination.next);
    }
  };

  /** Обработчик перехода на предыдущую страницу. */
  const handlePrevious = async () => {
    if (pagination.previous) {
      await loadByLink(pagination.previous);
    }
  };

  // Хук вызывается безусловно до ранних выходов; без отрисованной сетки он бездействует
  const { containerRef, markImageReady, revealedIds } = useMasonry(photos);

  // Отображение индикатора загрузки
  if (loading) {
    return <SpinnerComponent message="Загрузка фотографий..." />;
  }

  // Отображение сообщения об ошибке с кнопкой повтора
  if (error) {
    return (
      <AlertList
        messages={[
          {
            message: error,
            level: 'error',
            actions: (
              <Button variant="outline-primary" size="sm" onClick={() => loadPhotos()}>
                Повторить
              </Button>
            ),
          },
        ]}
      />
    );
  }

  // Отображение сообщения о пустом списке фотографий;
  // при активном поиске сообщение включает запрос пользователя
  if (photos.length === 0) {
    const emptyMessage = search ? `По запросу "${search}" ничего не найдено` : 'Нет доступных фотографий';
    return <AlertList messages={[{ message: emptyMessage, level: 'info' }]} />;
  }

  // Отображение списка фотографий с пагинацией
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
      <Pagination
        currentPage={pagination.currentPage}
        totalPages={pagination.totalPages}
        hasNext={!!pagination.next}
        hasPrevious={!!pagination.previous}
        onPageChange={handlePageChange}
        onNext={handleNext}
        onPrevious={handlePrevious}
      />
    </Container>
  );
};

/** Вычисляет номер страницы из параметра page ссылки пагинации. */
const currentPageFromUrl = (pageUrl: string): number => {
  const url = new URL(pageUrl);
  return parseInt(url.searchParams.get('page') || '1', 10);
};

export default PhotoList;
