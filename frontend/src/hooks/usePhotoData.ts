import { useCallback } from 'react';
import { galleryService } from '@services';
import { useApiData } from '@hooks';
import type { components } from '@api-types/api-schema';

type Photo = components['schemas']['PhotoDetail'];

/** Результат хука usePhotoData. */
export interface UsePhotoDataResult {
  photo: Photo | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Хук для загрузки данных фотографии по pk.
 *
 * Загружает данные фотографии через сервис галереи и управляет состоянием
 * загрузки и ошибок. Пустой pk возвращает photo без сетевого запроса.
 */
const usePhotoData = (photoPk: number | null): UsePhotoDataResult => {
  const fetchPhoto = useCallback(() => (photoPk ? galleryService.getPhoto(photoPk) : Promise.resolve(null)), [photoPk]);

  const { data: photo, loading, error, refetch } = useApiData<Photo | null>(fetchPhoto);

  return { photo, loading, error, refetch };
};

export default usePhotoData;
