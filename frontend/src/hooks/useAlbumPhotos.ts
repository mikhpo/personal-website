/* eslint-disable react-x/set-state-in-effect -- синхронная установка состояния в effect - установленный паттерн загрузки этого хука */
import { useEffect, useState } from 'react';
import { galleryService } from '@services';
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
 * Загружает данные альбома через сервис галереи и возвращает список вложенных
 * фотографий целиком: навигация между фото работает без оглядки на пагинацию.
 */
const useAlbumPhotos = (albumId: number | string | null): UseAlbumPhotosResult => {
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

      galleryService
        .getAlbum(albumId)
        .then((album) => {
          setPhotos(album.photos);
          setLoading(false);
        })
        .catch((err: Error) => {
          setError(err.message);
          setLoading(false);
        });
    };

    fetchAlbumPhotos();
  }, [albumId]);

  const refetch = () => {
    if (albumId === null || albumId === undefined || albumId === '') {
      setPhotos([]);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    galleryService
      .getAlbum(albumId)
      .then((album) => {
        setPhotos(album.photos);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  };

  return {
    photos,
    loading,
    error,
    refetch,
  };
};

export default useAlbumPhotos;
