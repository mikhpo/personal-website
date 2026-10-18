import React, { useEffect, useState } from 'react';
import { Container, Button } from 'react-bootstrap';
import PhotoCard from '@components/Gallery/Photo/PhotoCard';
import SpinnerComponent from '@components/Spinner/Spinner';
import AlertList from '@components/Alert/AlertList';
import Pagination from '@components/Pagination/Pagination';
import useMasonry from '@hooks/useMasonry';
import { buildApiUrl } from '@utils/apiUrl';
import type { components } from '../../../types/api-schema';
import type { Paginated } from '../../../types/pagination';

type Photo = components['schemas']['Photo'];

/** Ответ endpoint альбома: список фотографий без конверта пагинации. */
type AlbumPhotosResponse = Pick<components['schemas']['AlbumDetail'], 'photos'>;

/** Списочный ответ зависит от apiUrl: конверт, массив или ответ endpoint альбома. */
type PhotosResponse = Paginated<Photo> | Photo[] | AlbumPhotosResponse;

/** Состояние данных пагинации списка фотографий. */
interface PaginationState {
  count: number;
  next: string | null;
  previous: string | null;
  currentPage: number;
  totalPages: number;
}

/**
 * Разбирает списочный ответ до фотографий и конверта пагинации.
 *
 * До нормализации (фаза 6) сохраняет действующую толерантность читателя:
 * ответ endpoint альбома (photos), конверт пагинации (results) и голый массив.
 */
const readPhotosResponse = (data: PhotosResponse): { photos: Photo[]; envelope: Paginated<Photo> | null } => {
  if (Array.isArray(data)) {
    return { photos: data, envelope: null };
  }
  if ('photos' in data) {
    return { photos: Array.isArray(data.photos) ? data.photos : [], envelope: null };
  }
  return { photos: Array.isArray(data.results) ? data.results : [], envelope: data };
};

/** Вычисляет номер страницы из параметра page ссылки пагинации. */
const currentPageFromUrl = (pageUrl: string): number => {
  const url = new URL(pageUrl);
  return parseInt(url.searchParams.get('page') || '1', 10);
};

/** Свойства компонента списка фотографий. */
export interface PhotoListProps {
  /** Базовый URL API; на странице альбома переопределяется endpoint альбома. */
  apiUrl?: string;
  /** Слаг тега для фильтрации (tags__slug); URL фильтра строится во фронтенде. */
  tagSlug?: string;
  /** Поисковый запрос для фильтрации (search). */
  search?: string;
}

/**
 * Компонент списка фотографий галереи.
 *
 * Загружает и отображает список фотографий из API галереи.
 * Обрабатывает состояния загрузки, ошибки и пустого списка.
 * Предоставляет возможность повторной попытки загрузки при ошибке.
 * Поддерживает пагинацию для навигации по большому количеству фотографий.
 *
 * @example
 * <PhotoList />
 *
 * @example
 * <PhotoList apiUrl="/api/gallery/album/1/photos/" />
 *
 * @example
 * <PhotoList search="закат" />
 */
const PhotoList = ({ apiUrl = '/api/gallery/photos/', tagSlug, search }: PhotoListProps) => {
  /** Состояние фотографий. */
  const [photos, setPhotos] = useState<Photo[]>([]);

  /** Состояние загрузки данных. */
  const [loading, setLoading] = useState(true);

  /** Состояние ошибки при загрузке данных. */
  const [error, setError] = useState<string | null>(null);

  /** Состояние данных пагинации. */
  const [pagination, setPagination] = useState<PaginationState>({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    totalPages: 0,
  });

  /** Загружает данные по указанному URL. */
  const fetchUrl = async (url: string): Promise<PhotosResponse> => {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Ошибка загрузки: ${response.status}`);
    }
    return await response.json();
  };

  // Эффект для загрузки фотографий при монтировании компонента или изменении apiUrl
  useEffect(() => {
    /** Загружает фотографии из API. */
    const loadPhotos = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(buildApiUrl(apiUrl, { tags__slug: tagSlug, search }));
        const { photos: photosList, envelope } = readPhotosResponse(data);
        setPhotos(photosList);

        // Обновить данные пагинации
        const totalPages = envelope && envelope.count ? Math.ceil(envelope.count / photosList.length) : 0;
        setPagination({
          count: envelope?.count || 0,
          next: envelope?.next ?? null,
          previous: envelope?.previous ?? null,
          currentPage: 1,
          totalPages: totalPages,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    loadPhotos();
  }, [apiUrl, tagSlug, search]);

  /** Обновляет состояние пагинации и список по ответу страницы. */
  const applyPageResponse = (data: PhotosResponse, currentPage: number, totalPages: number) => {
    const { photos: photosList, envelope } = readPhotosResponse(data);
    setPhotos(photosList);

    setPagination({
      count: envelope?.count || 0,
      next: envelope?.next ?? null,
      previous: envelope?.previous ?? null,
      currentPage,
      totalPages,
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
      // Построить URL с параметром страницы
      const url = buildApiUrl(apiUrl, { tags__slug: tagSlug, search, page });

      const data = await fetchUrl(url);
      applyPageResponse(data, page, pagination.totalPages);

      // Прокрутить страницу вверх
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
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(pagination.next);
        applyPageResponse(data, currentPageFromUrl(pagination.next), pagination.totalPages);

        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    }
  };

  /** Обработчик перехода на предыдущую страницу. */
  const handlePrevious = async () => {
    if (pagination.previous) {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(pagination.previous);
        applyPageResponse(data, currentPageFromUrl(pagination.previous), pagination.totalPages);

        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    }
  };

  /**
   * Повторная загрузка первой страницы: сбрасывает состояние ошибки
   * и повторно выполняет запрос к API.
   */
  const handleRetry = () => {
    /** Повторно загружает фотографии из API. */
    const retryLoadPhotos = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchUrl(buildApiUrl(apiUrl, { tags__slug: tagSlug, search }));
        const { photos: photosList, envelope } = readPhotosResponse(data);
        setPhotos(photosList);

        const totalPages = envelope && envelope.count ? Math.ceil(envelope.count / photosList.length) : 0;
        setPagination({
          count: envelope?.count || 0,
          next: envelope?.next ?? null,
          previous: envelope?.previous ?? null,
          currentPage: 1,
          totalPages: totalPages,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    retryLoadPhotos();
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
              <Button variant="outline-primary" size="sm" onClick={handleRetry}>
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

export default PhotoList;
