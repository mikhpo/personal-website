import { useState, useEffect, useCallback } from 'react';

/**
 * Хук для загрузки данных из API с обработкой состояний загрузки, ошибки и повторной попытки.
 *
 * Упрощает работу с API, предоставляя унифицированный интерфейс для загрузки данных,
 * обработки ошибок и управления состоянием загрузки. Заменяет дублирующийся паттерн
 * загрузки данных в компонентах.
 *
 * @param {Function} fetchFunction - Асинхронная функция для загрузки данных
 * @param {Array} [deps=[]] - Массив зависимостей для повторной загрузки при изменении
 * @param {Object} [options={}] - Дополнительные опции
 * @param {boolean} [options.immediate=true] - Выполнять ли загрузку сразу при монтировании
 * @param {any} [options.initialData=null] - Начальное значение данных
 * @return {Object} Объект с данными и функциями управления
 * @property {any} data - Загруженные данные
 * @property {boolean} loading - Состояние загрузки
 * @property {string|null} error - Сообщение об ошибке или null
 * @property {Function} refetch - Функция для повторной загрузки данных
 * @property {Function} setData - Функция для обновления данных
 *
 * @example
 * // Использование с сервисом API
 * const { data, loading, error, refetch } = useApiData(
 *   () => blogService.getArticles({ page: 1 }),
 *   { immediate: true }
 * );
 *
 * @example
 * // Использование с URL
 * const { data, loading, error } = useApiData(
 *   async () => await api.get('/api/photos/')
 * );
 */
const useApiData = (fetchFunction, options = {}) => {
  const { immediate = true, initialData = null } = options;

  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchFunction();
      setData(result);
    } catch (err) {
      setError(err.message || 'Произошла ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  }, [fetchFunction]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [immediate, fetchData]);

  return {
    data,
    loading,
    error,
    refetch,
    setData,
  };
};

export default useApiData;
