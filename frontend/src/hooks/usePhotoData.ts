import { useCallback, useEffect, useState } from 'react';
import type { components } from '../types/api-schema';

type Photo = components['schemas']['Photo'];

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
 * Загружает данные фотографии из API и управляет состоянием загрузки и ошибок.
 */
const usePhotoData = (photoPk: number | string | null, apiUrl = '/api/gallery/photos/'): UsePhotoDataResult => {
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPhotoRequest = useCallback(async (): Promise<Photo> => {
    if (!photoPk) {
      throw new Error('Не указан идентификатор фотографии');
    }

    const response = await fetch(`${apiUrl}${photoPk}/`);

    if (!response.ok) {
      throw new Error(`Ошибка загрузки фото: ${response.status}`);
    }

    return response.json();
  }, [photoPk, apiUrl]);

  const loadPhoto = useCallback(async () => {
    if (!photoPk) {
      setPhoto(null);
      setLoading(true);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const photoData = await fetchPhotoRequest();
      setPhoto(photoData);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }, [photoPk, fetchPhotoRequest]);

  useEffect(() => {
    loadPhoto();
  }, [loadPhoto]);

  const safeRefetch = loadPhoto;

  return {
    photo,
    loading,
    error,
    refetch: safeRefetch,
  };
};

export default usePhotoData;
