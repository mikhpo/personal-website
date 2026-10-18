/* eslint-disable react-x/set-state-in-effect -- синхронная установка состояния в effect - установленный паттерн загрузки этого хука; перестройка меняла бы рантайм и вне рамок миграции */
import { useEffect, useState } from 'react';
import type { components } from '../types/api-schema';

type Photo = components['schemas']['Photo'];

/** Результат хука useAlbumPhotos. */
export interface UseAlbumPhotosResult {
  photos: Photo[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Хук для загрузки фотографий альбома через эндпоинт детального просмотра альбома.
 *
 * Загружает данные альбома из API и возвращает список вложенных фотографий.
 */
const useAlbumPhotos = (albumId: number | string | null, apiUrl = '/api/gallery/albums/'): UseAlbumPhotosResult => {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAlbumPhotos = () => {
      if (albumId === null || albumId === undefined || albumId === '') {
        setPhotos([]);
        setLoading(false);
        setError(null);
        return;
      }

      setLoading(true);
      setError(null);

      fetch(`${apiUrl}${albumId}/`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Ошибка загрузки данных альбома: ${response.status}`);
          }
          return response.json();
        })
        .then((data: { photos?: Photo[] }) => {
          const photosList = data.photos || [];
          setPhotos(Array.isArray(photosList) ? photosList : []);
          setLoading(false);
        })
        .catch((err: Error) => {
          setError(err.message);
          setLoading(false);
        });
    };

    fetchAlbumPhotos();
  }, [albumId, apiUrl]);

  return {
    photos,
    loading,
    error,
    refetch: () => {
      const fetchAlbumPhotos = () => {
        if (albumId === null || albumId === undefined || albumId === '') {
          setPhotos([]);
          setLoading(false);
          setError(null);
          return;
        }

        setLoading(true);
        setError(null);

        fetch(`${apiUrl}${albumId}/`)
          .then((response) => {
            if (!response.ok) {
              throw new Error(`Ошибка загрузки данных альбома: ${response.status}`);
            }
            return response.json();
          })
          .then((data: { photos?: Photo[] }) => {
            const photosList = data.photos || [];
            setPhotos(Array.isArray(photosList) ? photosList : []);
            setLoading(false);
          })
          .catch((err: Error) => {
            setError(err.message);
            setLoading(false);
          });
      };

      fetchAlbumPhotos();
    },
  };
};

export default useAlbumPhotos;
