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

  const fetchPhoto = useCallback(() => {
    if (!photoPk) {
      const updateInitialState = () => {
        // eslint-disable-next-line react-x/set-state-in-effect
        setPhoto(null);
        // eslint-disable-next-line react-x/set-state-in-effect
        setLoading(true);
        // eslint-disable-next-line react-x/set-state-in-effect
        setError(null);
      };
      updateInitialState();
      return;
    }

    const updateLoadingState = () => {
      // eslint-disable-next-line react-x/set-state-in-effect
      setLoading(true);
      // eslint-disable-next-line react-x/set-state-in-effect
      setError(null);
    };
    updateLoadingState();

    fetch(`${apiUrl}${photoPk}/`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Ошибка загрузки фото: ${response.status}`);
        }
        return response.json();
      })
      .then(photoData => {
        setPhoto(photoData);
        setLoading(false);
      })
      .catch(err => {
        // eslint-disable-next-line react-x/set-state-in-effect
        setError(err.message);
        // eslint-disable-next-line react-x/set-state-in-effect
        setLoading(false);
      });
  }, [photoPk, apiUrl]);

  useEffect(() => {
    if (!photoPk) {
      const updateInitialState = () => {
        // eslint-disable-next-line react-x/set-state-in-effect
        setPhoto(null);
        // eslint-disable-next-line react-x/set-state-in-effect
        setLoading(true);
        // eslint-disable-next-line react-x/set-state-in-effect
        setError(null);
      };
      updateInitialState();
      return;
    }

    fetchPhoto();
  }, [photoPk, fetchPhoto]);

  // Возвращаем безопасную функцию refetch, которая проверяет photoPk перед вызовом
  const safeRefetch = () => {
    if (!photoPk) {
      // Для пустого photoPk просто обновляем состояние
      setPhoto(null);
      setLoading(true);
      setError(null);
      return;
    }
    fetchPhoto();
  };

  return {
    photo,
    loading,
    error,
    refetch: safeRefetch
  };
};

export default usePhotoData;
