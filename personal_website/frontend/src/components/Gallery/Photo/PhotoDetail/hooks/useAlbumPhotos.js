import { useState, useEffect } from 'react';

/**
 * Хук для загрузки фотографий альбома через эндпоинт детального просмотра альбома.
 *
 * Загружает данные альбома из API и возвращает список вложенных фотографий.
 *
 * @param {number|null} albumId - ID альбома для загрузки фотографий (может быть null)
 * @param {string} [apiUrl='/api/gallery/albums/'] - Базовый URL API альбомов
 * @return {Object} Объект с данными о фотографиях альбома и состоянии загрузки
 * @property {Array} photos - Массив фотографий альбома
 * @property {boolean} loading - Состояние загрузки
 * @property {string|null} error - Сообщение об ошибке или null
 * @property {Function} refetch - Функция для повторной загрузки данных
 */
const useAlbumPhotos = (albumId, apiUrl = '/api/gallery/albums/') => {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAlbumPhotos = () => {
    // Проверяем, что albumId существует и это число
    if (albumId === null || albumId === undefined || albumId === '') {
      setPhotos([]);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    fetch(`${apiUrl}${albumId}/`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Ошибка загрузки данных альбома: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        const photosList = data.photos || [];
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
