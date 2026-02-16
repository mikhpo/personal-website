import { useState, useEffect } from 'react';

/**
 * Хук для загрузки фотографий альбома.
 *
 * Загружает список фотографий альбома из API и управляет состоянием загрузки и ошибок.
 *
 * @param {number|null} albumId - ID альбома для загрузки фотографий (может быть null)
 * @param {string} [apiUrl='/api/gallery/photos/'] - Базовый URL API
 * @return {Object} Объект с данными о фотографиях альбома и состоянии загрузки
 * @property {Array} photos - Массив фотографий альбома
 * @property {boolean} loading - Состояние загрузки
 * @property {string|null} error - Сообщение об ошибке или null
 * @property {Function} refetch - Функция для повторной загрузки данных
 */
const useAlbumPhotos = (albumId, apiUrl = '/api/gallery/photos/') => {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlbumPhotos = () => {
    // Если albumId null или undefined, не загружаем фотографии
    if (albumId === null || albumId === undefined) {
      setPhotos([]);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    fetch(`${apiUrl}?album=${albumId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Ошибка загрузки фотографий альбома: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        const photosList = data.results || data;
        setPhotos(Array.isArray(photosList) ? photosList : []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAlbumPhotos();
  }, [albumId, apiUrl]);

  return {
    photos,
    loading,
    error,
    refetch: fetchAlbumPhotos
  };
};

export default useAlbumPhotos;