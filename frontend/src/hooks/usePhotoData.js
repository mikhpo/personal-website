import { useState, useEffect, useCallback } from 'react';

/**
 * Хук для загрузки данных фотографии по pk.
 *
 * Загружает данные фотографии из API и управляет состоянием загрузки и ошибок.
 *
 * @param {number|string} photoPk - Первичный ключ фотографии для загрузки
 * @param {string} [apiUrl='/api/gallery/photos/'] - Базовый URL API
 * @return {Object} Объект с данными о фотографии и состоянии загрузки
 * @property {Object|null} photo - Данные фотографии или null
 * @property {boolean} loading - Состояние загрузки
 * @property {string|null} error - Сообщение об ошибке или null
 * @property {Function} refetch - Функция для повторной загрузки данных
 */
const usePhotoData = (photoPk, apiUrl = '/api/gallery/photos/') => {
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPhotoRequest = useCallback(async () => {
    if (!photoPk) {
      throw new Error('Не указан идентификатор фотографии');
    }

    const response = await fetch(`${apiUrl}${photoPk}/`);

    if (!response.ok) {
      throw new Error(`Ошибка загрузки фото: ${response.status}`);
    }

    return response.json();
  }, [photoPk, apiUrl]);

  useEffect(() => {
    if (!photoPk) {
      // При отсутствии photoPk не выполняем запрос, состояние уже корректное
      return;
    }

    const loadPhoto = async () => {
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
    };

    loadPhoto();
  }, [photoPk, fetchPhotoRequest]);

  const safeRefetch = () => {
    if (!photoPk) {
      // При отсутствии photoPk только сбрасываем состояние
      setPhoto(null);
      setLoading(true);
      setError(null);
      return;
    }

    const reloadPhoto = async () => {
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
    };

    reloadPhoto();
  };

  return {
    photo,
    loading,
    error,
    refetch: safeRefetch
  };
};

export default usePhotoData;
