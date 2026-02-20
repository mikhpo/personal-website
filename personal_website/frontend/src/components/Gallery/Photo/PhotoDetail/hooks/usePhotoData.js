import { useState, useEffect } from 'react';

/**
 * Хук для загрузки данных фотографии по slug.
 *
 * Загружает данные фотографии из API и управляет состоянием загрузки и ошибок.
 *
 * @param {string} photoSlug - Слаг фотографии для загрузки
 * @param {string} [apiUrl='/api/gallery/photos/'] - Базовый URL API
 * @return {Object} Объект с данными о фотографии и состоянии загрузки
 * @property {Object|null} photo - Данные фотографии или null
 * @property {boolean} loading - Состояние загрузки
 * @property {string|null} error - Сообщение об ошибке или null
 * @property {Function} refetch - Функция для повторной загрузки данных
 */
const usePhotoData = (photoSlug, apiUrl = '/api/gallery/photos/') => {
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPhoto = () => {
    // Если photoSlug пустой, не выполняем загрузку
    if (!photoSlug) {
      setPhoto(null);
      setLoading(true); // Оставляем loading=true как в тестах
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    fetch(`${apiUrl}${photoSlug}/`)
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
    // Если photoSlug пустой, не выполняем загрузку
    if (!photoSlug) {
      setPhoto(null);
      setLoading(true); // Оставляем loading=true как в тестах
      setError(null);
      return;
    }
    
    fetchPhoto();
  }, [photoSlug, apiUrl]);

  // Возвращаем безопасную функцию refetch, которая проверяет photoSlug перед вызовом
  const safeRefetch = () => {
    if (!photoSlug) {
      // Для пустого photoSlug просто обновляем состояние
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