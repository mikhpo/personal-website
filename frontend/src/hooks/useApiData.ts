import { useCallback, useEffect, useState } from 'react';

/** Опции хука useApiData. */
export interface UseApiDataOptions<T> {
  /** Выполнять ли загрузку сразу при монтировании. */
  immediate?: boolean;
  /** Начальное значение данных. */
  initialData?: T | null;
}

/** Результат хука useApiData. */
export interface UseApiDataResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  setData: React.Dispatch<React.SetStateAction<T | null>>;
}

const DEFAULT_ERROR_MESSAGE = 'Произошла ошибка при загрузке данных';

/**
 * Хук для загрузки данных из API с обработкой состояний загрузки, ошибки и повторной попытки.
 *
 * Упрощает работу с API, предоставляя унифицированный интерфейс для загрузки данных,
 * обработки ошибок и управления состоянием загрузки. Заменяет дублирующийся паттерн
 * загрузки данных в компонентах.
 *
 * @example
 * const { data, loading, error, refetch } = useApiData(
 *   () => blogService.getArticles({ page: 1 }),
 * );
 */
const useApiData = <T>(fetchFunction: () => Promise<T>, options: UseApiDataOptions<T> = {}): UseApiDataResult<T> => {
  const { immediate = true, initialData = null } = options;

  const [data, setData] = useState<T | null>(initialData);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await fetchFunction();
      setData(result);
    } catch (err) {
      setError(err instanceof Error && err.message ? err.message : DEFAULT_ERROR_MESSAGE);
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
