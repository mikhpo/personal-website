/**
 * Тесты для хука useTheme.
 *
 * Проверяют приоритет темы (явный выбор, системная, светлая по умолчанию),
 * синхронизацию атрибута data-bs-theme и реакцию на смену системной темы.
 */

import { renderHook, act } from '@testing-library/react';
import useTheme from './useTheme';

/**
 * Создает управляемый стаб window.matchMedia с возможностью
 * эмулировать смену системной темы событием change.
 * @param {boolean} initialMatches - Начальное совпадение запроса (prefers-color-scheme: dark)
 * @return {Object} Стаб с функцией query и функцией triggerChange
 */
const createMatchMediaStub = (initialMatches) => {
  const listeners = new Set();
  const mediaQuery = {
    matches: initialMatches,
    addEventListener: jest.fn((event, listener) => listeners.add(listener)),
    removeEventListener: jest.fn((event, listener) => listeners.delete(listener)),
  };
  return {
    query: jest.fn(() => mediaQuery),
    triggerChange: (matches) => {
      mediaQuery.matches = matches;
      listeners.forEach((listener) => listener({ matches }));
    },
  };
};

describe('useTheme', () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute('data-bs-theme');
  });

  /**
   * Проверяет определение темы по умолчанию.
   */
  describe('тема по умолчанию', () => {
    test('использует системную светлую тему без явного выбора', () => {
      window.matchMedia = createMatchMediaStub(false).query;

      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe('light');
      expect(result.current.systemTheme).toBe('light');
      expect(result.current.storedTheme).toBeNull();
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'light');
    });

    test('использует системную темную тему без явного выбора', () => {
      window.matchMedia = createMatchMediaStub(true).query;

      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe('dark');
      expect(result.current.systemTheme).toBe('dark');
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'dark');
    });

    test('использует светлую тему, если matchMedia недоступен', () => {
      const originalMatchMedia = window.matchMedia;
      delete window.matchMedia;

      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe('light');
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'light');

      window.matchMedia = originalMatchMedia;
    });
  });

  /**
   * Проверяет приоритет явного выбора над системной темой.
   */
  describe('явный выбор пользователя', () => {
    test.each([
      ['dark', 'light'],
      ['light', 'dark'],
    ])('сохраненный выбор "%s" перекрывает системную тему "%s"', (stored, system) => {
      window.matchMedia = createMatchMediaStub(system === 'dark').query;
      window.localStorage.setItem('theme', JSON.stringify(stored));

      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe(stored);
      expect(document.documentElement).toHaveAttribute('data-bs-theme', stored);
    });

    test('поврежденное значение в localStorage игнорируется', () => {
      window.matchMedia = createMatchMediaStub(true).query;
      window.localStorage.setItem('theme', JSON.stringify('blue'));

      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe('dark');
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'dark');
    });
  });

  /**
   * Проверяет реакцию на смену системной темы.
   */
  describe('смена системной темы', () => {
    test('меняет действующую тему, пока нет явного выбора', () => {
      const stub = createMatchMediaStub(false);
      window.matchMedia = stub.query;

      const { result } = renderHook(() => useTheme());

      expect(result.current.theme).toBe('light');

      act(() => stub.triggerChange(true));

      expect(result.current.theme).toBe('dark');
      expect(result.current.systemTheme).toBe('dark');
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'dark');
    });

    test('не меняет действующую тему при явном выборе', () => {
      const stub = createMatchMediaStub(false);
      window.matchMedia = stub.query;
      window.localStorage.setItem('theme', JSON.stringify('light'));

      const { result } = renderHook(() => useTheme());

      act(() => stub.triggerChange(true));

      expect(result.current.theme).toBe('light');
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'light');
    });
  });

  /**
   * Проверяет функции управления темой.
   */
  describe('setTheme и toggleTheme', () => {
    test('setTheme записывает явный выбор в localStorage', () => {
      window.matchMedia = createMatchMediaStub(false).query;

      const { result } = renderHook(() => useTheme());

      act(() => result.current.setTheme('dark'));

      expect(result.current.theme).toBe('dark');
      expect(result.current.storedTheme).toBe('dark');
      expect(window.localStorage.getItem('theme')).toBe(JSON.stringify('dark'));
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'dark');
    });

    test('setTheme(null) возвращает режим следования системной теме', () => {
      window.matchMedia = createMatchMediaStub(true).query;

      const { result } = renderHook(() => useTheme());

      act(() => result.current.setTheme('light'));
      expect(result.current.theme).toBe('light');

      act(() => result.current.setTheme(null));

      expect(result.current.theme).toBe('dark');
      expect(result.current.storedTheme).toBeNull();
      expect(window.localStorage.getItem('theme')).toBeNull();
      expect(document.documentElement).toHaveAttribute('data-bs-theme', 'dark');
    });

    test('setTheme с недопустимым значением возвращает системный режим', () => {
      window.matchMedia = createMatchMediaStub(false).query;

      const { result } = renderHook(() => useTheme());

      act(() => result.current.setTheme('blue'));

      expect(result.current.theme).toBe('light');
      expect(result.current.storedTheme).toBeNull();
      expect(window.localStorage.getItem('theme')).toBeNull();
    });

    test('toggleTheme переключает светлую тему на темную с записью выбора', () => {
      window.matchMedia = createMatchMediaStub(false).query;

      const { result } = renderHook(() => useTheme());

      act(() => result.current.toggleTheme());

      expect(result.current.theme).toBe('dark');
      expect(result.current.storedTheme).toBe('dark');
    });

    test('toggleTheme переключает темную тему на светлую с записью выбора', () => {
      window.matchMedia = createMatchMediaStub(true).query;

      const { result } = renderHook(() => useTheme());

      act(() => result.current.toggleTheme());

      expect(result.current.theme).toBe('light');
      expect(result.current.storedTheme).toBe('light');
    });
  });
});
