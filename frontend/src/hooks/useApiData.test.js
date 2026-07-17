/**
 * Тесты для хука useApiData.
 *
 * Проверяют загрузку данных из API, обработку ошибок,
 * управление состоянием загрузки и повторной загрузки.
 */

import { renderHook, waitFor } from '@testing-library/react';
import { act } from 'react';
import useApiData from './useApiData';

describe('useApiData', () => {
  const mockFetchFunction = jest.fn();
  const mockData = { results: [{ id: 1, name: 'Test' }] };

  beforeEach(() => {
    mockFetchFunction.mockClear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Проверяет начальное состояние при монтировании с immediate=true.
   */
  describe('с немедленной загрузкой (immediate=true)', () => {
    test('устанавливает loading=true при монтировании', () => {
      mockFetchFunction.mockImplementation(() => new Promise(() => {}));

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true })
      );

      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBe(null);
      expect(result.current.data).toBe(null);
    });

    test('загружает данные при монтировании', async () => {
      mockFetchFunction.mockResolvedValue(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true })
      );

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockFetchFunction).toHaveBeenCalledTimes(1);
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBe(null);
    });

    test('обрабатывает ошибки при загрузке', async () => {
      const errorMessage = 'Network error';
      mockFetchFunction.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toBe(null);
      expect(result.current.error).toBe(errorMessage);
    });
  });

  /**
   * Проверяет поведение без немедленной загрузки (immediate=false).
   */
  describe('без немедленной загрузки (immediate=false)', () => {
    test('не загружает данные при монтировании', async () => {
      mockFetchFunction.mockResolvedValue(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: false })
      );

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBe(null);
      expect(result.current.error).toBe(null);

      // Проверяем, что fetch не был вызван
      expect(mockFetchFunction).not.toHaveBeenCalled();
    });

    test('позволяет загрузить данные через refetch', async () => {
      mockFetchFunction.mockResolvedValue(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: false })
      );

      // Загружаем данные вручную
      act(() => {
        result.current.refetch();
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockData);
      expect(mockFetchFunction).toHaveBeenCalledTimes(1);
    });
  });

  /**
   * Проверяет функцию refetch для повторной загрузки данных.
   */
  describe('refetch', () => {
    test('перезагружает данные при вызове refetch', async () => {
      mockFetchFunction.mockResolvedValue(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Вызываем refetch
      act(() => {
        result.current.refetch();
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockFetchFunction).toHaveBeenCalledTimes(2);
    });

    test('очищает предыдущую ошибку при refetch', async () => {
      const errorMessage = 'First error';
      mockFetchFunction
        .mockRejectedValueOnce(new Error(errorMessage))
        .mockResolvedValueOnce(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true })
      );

      await waitFor(() => {
        expect(result.current.error).toBe(errorMessage);
      });

      // Вызываем refetch для повторной попытки
      act(() => {
        result.current.refetch();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe(null);
      expect(result.current.data).toEqual(mockData);
    });
  });

  /**
   * Проверяет обновление зависимостей.
   */
  describe('зависимости', () => {
    test('перезагружает данные при изменении зависимостей', async () => {
      mockFetchFunction.mockResolvedValue(mockData);

      const { result, rerender } = renderHook(
        ({ dep }) => useApiData(mockFetchFunction, [dep], { immediate: true }),
        { initialProps: { dep: 'value1' } }
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(mockFetchFunction).toHaveBeenCalledTimes(1);

      // Изменяем зависимость
      rerender({ dep: 'value2' });

      // Ожидаем повторную загрузку
      await waitFor(() => {
        expect(mockFetchFunction).toHaveBeenCalledTimes(2);
      });
    });
  });

  /**
   * Проверяет функцию setData для обновления данных.
   */
  describe('setData', () => {
    test('позволяет обновить данные вручную', async () => {
      mockFetchFunction.mockResolvedValue(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Обновляем данные вручную
      const newData = { results: [{ id: 2, name: 'Updated' }] };
      act(() => {
        result.current.setData(newData);
      });

      expect(result.current.data).toEqual(newData);
      expect(result.current.loading).toBe(false);
    });
  });

  /**
   * Проверяет работу с начальными данными.
   */
  describe('initialData', () => {
    test('использует initialData как начальное значение', () => {
      const initialData = { results: [{ id: 0, name: 'Initial' }] };
      mockFetchFunction.mockResolvedValue(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true, initialData })
      );

      // Начальные данные должны быть доступны сразу
      expect(result.current.data).toEqual(initialData);
      expect(result.current.loading).toBe(true);
    });

    test('заменяет initialData на загруженные данные', async () => {
      const initialData = { results: [{ id: 0, name: 'Initial' }] };
      mockFetchFunction.mockResolvedValue(mockData);

      const { result } = renderHook(() =>
        useApiData(mockFetchFunction, [], { immediate: true, initialData })
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Данные должны быть заменены на загруженные
      expect(result.current.data).toEqual(mockData);
      expect(result.current.data).not.toEqual(initialData);
    });
  });
});
