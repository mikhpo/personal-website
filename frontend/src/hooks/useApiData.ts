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
 * Ссылка на fetchFunction обязана быть стабильной между рендерами, поэтому функция
 * оборачивается в useCallback: смена ссылки запускает повторную загрузку, а
 * инлайн-стрелка в теле компонента устроила бы бесконечный цикл загрузки.
 *
 * Устаревшие ответы отбрасываются: если во время выполнения запроса сменился
 * fetchFunction или сработал refetch, ответ отмененного запроса не перезаписывает
 * свежие данные.
 *
 * @example
 * const loadArticles = useCallback(() => blogService.getArticles({ page }), [page]);
 * const { data, loading, error, refetch } = useApiData(loadArticles);
 */
const useApiData = <T>(fetchFunction: () => Promise<T>, options: UseApiDataOptions<T> = {}): UseApiDataResult<T> => {
  const { immediate = true, initialData = null } = options;

  const [data, setData] = useState<T | null>(initialData);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<string | null>(null);

  /** Счетчик вызовов refetch: смена значения перезапускает эффект загрузки. */
  const [fetchKey, setFetchKey] = useState(0);

  useEffect(() => {
    if (!immediate && fetchKey === 0) {
      return undefined;
    }

    // Флаг активности: после cleanup ответ устаревшего запроса не применяется
    let active = true;

    const load = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchFunction();
        if (active) {
          setData(result);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error && err.message ? err.message : DEFAULT_ERROR_MESSAGE);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      active = false;
    };
  }, [fetchFunction, immediate, fetchKey]);

  const refetch = useCallback(() => {
    setFetchKey((key) => key + 1);
  }, []);

  return {
    data,
    loading,
    error,
    refetch,
    setData,
  };
};

export default useApiData;
