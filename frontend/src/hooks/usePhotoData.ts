import { useCallback, useEffect, useState } from 'react';
import { galleryService } from '@services';
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
 * Загружает данные фотографии через сервис галереи и управляет состоянием
 * загрузки и ошибок.
 */
const usePhotoData = (photoPk: number | string | null): UsePhotoDataResult => {
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      const photoData = await galleryService.getPhoto(photoPk);
      setPhoto(photoData);
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setLoading(false);
    }
  }, [photoPk]);

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
