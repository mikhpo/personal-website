import { useState, useEffect } from 'react';

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

  const fetchPhoto = () => {
    // Если photoPk пустой, не выполняем загрузку
    if (!photoPk) {
      setPhoto(null);
      setLoading(true);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

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
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    // Если photoPk пустой, не выполняем загрузку
    if (!photoPk) {
      setPhoto(null);
      setLoading(true);
      setError(null);
      return;
    }

    fetchPhoto();
  }, [photoPk, apiUrl]);

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
