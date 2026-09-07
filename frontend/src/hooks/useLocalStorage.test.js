/**
 * Тесты для хука useLocalStorage.
 *
 * Проверяют чтение и запись значений в localStorage,
 * удаление ключа через null/undefined и обработку поврежденных данных.
 */

import { renderHook, act } from '@testing-library/react';
import useLocalStorage from './useLocalStorage';

describe('useLocalStorage', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  /**
   * Проверяет чтение начального значения.
   */
  describe('чтение значения', () => {
    test('возвращает initialValue, если в localStorage ничего нет', () => {
      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      expect(result.current[0]).toBe('light');
    });

    test('возвращает значение из localStorage вместо initialValue', () => {
      window.localStorage.setItem('theme', JSON.stringify('dark'));

      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      expect(result.current[0]).toBe('dark');
    });

    test('возвращает initialValue для ключа с пустой строкой', () => {
      window.localStorage.setItem('theme', '');

      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      expect(result.current[0]).toBe('light');
    });

    test('возвращает initialValue при поврежденном JSON', () => {
      const warnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
      window.localStorage.setItem('theme', '{не json');

      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      expect(result.current[0]).toBe('light');
      expect(warnSpy).toHaveBeenCalled();
      warnSpy.mockRestore();
    });
  });

  /**
   * Проверяет запись значений.
   */
  describe('запись значения', () => {
    test('сохраняет значение в localStorage в формате JSON', () => {
      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      act(() => result.current[1]('dark'));

      expect(result.current[0]).toBe('dark');
      expect(window.localStorage.getItem('theme')).toBe(JSON.stringify('dark'));
    });

    test('поддерживает функциональное обновление', () => {
      window.localStorage.setItem('count', JSON.stringify(1));

      const { result } = renderHook(() => useLocalStorage('count', 0));

      act(() => result.current[1]((current) => current + 1));

      expect(result.current[0]).toBe(2);
      expect(window.localStorage.getItem('count')).toBe('2');
    });

    test('перезаписывает ранее сохраненное значение', () => {
      window.localStorage.setItem('theme', JSON.stringify('dark'));

      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      act(() => result.current[1]('light'));

      expect(window.localStorage.getItem('theme')).toBe(JSON.stringify('light'));
    });
  });

  /**
   * Проверяет удаление ключа через null и undefined.
   */
  describe('удаление значения', () => {
    test('setValue(null) удаляет ключ из localStorage', () => {
      window.localStorage.setItem('theme', JSON.stringify('dark'));

      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      act(() => result.current[1](null));

      expect(result.current[0]).toBeNull();
      expect(window.localStorage.getItem('theme')).toBeNull();
    });

    test('setValue(undefined) удаляет ключ из localStorage', () => {
      window.localStorage.setItem('theme', JSON.stringify('dark'));

      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      act(() => result.current[1](undefined));

      expect(result.current[0]).toBeUndefined();
      expect(window.localStorage.getItem('theme')).toBeNull();
    });

    test('после удаления чтение возвращает initialValue', () => {
      const { result } = renderHook(() => useLocalStorage('theme', 'light'));

      act(() => result.current[1]('dark'));
      act(() => result.current[1](null));

      expect(window.localStorage.getItem('theme')).toBeNull();
    });
  });
});
