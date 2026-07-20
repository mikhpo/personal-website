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

  useEffect(() => {
    const fetchAlbumPhotos = () => {
      if (albumId === null || albumId === undefined || albumId === '') {
        const updateInitialState = () => {
          setPhotos([]);
          setLoading(false);
          setError(null);
        };
        updateInitialState();
        return;
      }

      const updateLoadingState = () => {
        setLoading(true);
        setError(null);
      };
      updateLoadingState();

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

    fetchAlbumPhotos();
  }, [albumId, apiUrl]);

  return {
    photos,
    loading,
    error,
    refetch: () => {
      const fetchAlbumPhotos = () => {
        if (albumId === null || albumId === undefined || albumId === '') {
          const updateInitialState = () => {
            setPhotos([]);
            setLoading(false);
            setError(null);
          };
          updateInitialState();
          return;
        }

        const updateLoadingState = () => {
          setLoading(true);
          setError(null);
        };
        updateLoadingState();

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

      fetchAlbumPhotos();
    }
  };
};

export default useAlbumPhotos;
